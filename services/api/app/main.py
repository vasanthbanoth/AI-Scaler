from __future__ import annotations

import logging
import os
import subprocess
import sys
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from openai import OpenAI
from pydantic import BaseModel, Field

from app.calendar.calcom import CalcomClient
from app.config import ROOT, get_settings
from app.prompts import SYSTEM_PROMPT
from app.rag.retrieve import Retriever
from app.rag.store import ChunkStore

log = logging.getLogger("persona")
store = ChunkStore(get_settings().chunks_path)
retriever: Retriever | None = None

STATIC_DIR = Path(__file__).parent / "static"


def _maybe_run_ingest():
    settings = get_settings()
    if store.load():
        return True
    if not settings.openai_api_key:
        log.warning("No chunks.json and OPENAI_API_KEY unset — skipping auto-ingest")
        return False
    run = os.getenv("RUN_INGEST_ON_START", "").lower() in ("1", "true", "yes")
    if not run and not settings.run_ingest_on_start:
        return False
    script = ROOT / "scripts" / "ingest.py"
    if not script.exists():
        return False
    log.info("Running ingest.py (first boot)…")
    subprocess.run(
        [sys.executable, str(script)],
        cwd=str(ROOT),
        env={**os.environ, "REPO_ROOT": str(ROOT)},
        check=False,
    )
    return store.load()


@asynccontextmanager
async def lifespan(app: FastAPI):
    global retriever
    if _maybe_run_ingest() or store.load():
        retriever = Retriever(store)
    else:
        log.warning("Corpus not loaded — POST /chat will return 503")
    yield


app = FastAPI(title="Vasanth AI Persona API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    reply: str
    sources: list[dict[str, Any]]
    latency_ms: int


class SearchRequest(BaseModel):
    query: str
    k: int = 6


class BookRequest(BaseModel):
    start_iso: str
    name: str
    email: str
    notes: str = ""


@app.get("/health")
async def health():
    return {
        "ok": True,
        "chunks_loaded": len(store.chunks),
        "corpus_ready": len(store.chunks) > 0,
    }


@app.post("/rag/search")
async def rag_search(body: SearchRequest):
    if not retriever:
        raise HTTPException(503, "Corpus not ingested. Run: python scripts/ingest.py")
    return {"results": retriever.query(body.query, k=body.k)}


@app.post("/chat", response_model=ChatResponse)
async def chat(body: ChatRequest):
    if not retriever:
        raise HTTPException(503, "Corpus not ingested. Run: python scripts/ingest.py")

    t0 = time.perf_counter()
    hits = retriever.query(body.message, k=8)
    context = "\n\n---\n\n".join(
        f"[{h['source']}] (score={h['score']})\n{h['text']}" for h in hits
    )

    settings = get_settings()
    client = OpenAI(api_key=settings.openai_api_key)
    completion = client.chat.completions.create(
        model=settings.chat_model,
        temperature=0.2,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"CONTEXT:\n{context}\n\nUSER:\n{body.message}",
            },
        ],
    )
    reply = completion.choices[0].message.content or ""
    latency = int((time.perf_counter() - t0) * 1000)
    return ChatResponse(reply=reply, sources=hits, latency_ms=latency)


@app.get("/calendar/slots")
async def calendar_slots(days: int = 7, timezone: str = "Asia/Kolkata"):
    from datetime import datetime, timedelta

    cal = CalcomClient()
    start = datetime.now()
    end = start + timedelta(days=days)
    slots = await cal.get_slots(start, end, timezone=timezone)
    return {"slots": slots, "configured": cal.configured}


@app.post("/calendar/book")
async def calendar_book(body: BookRequest):
    cal = CalcomClient()
    result = await cal.book(
        start_iso=body.start_iso,
        name=body.name,
        email=body.email,
        notes=body.notes,
    )
    if not result.get("ok"):
        raise HTTPException(400, result.get("error", "booking failed"))
    return result


# ─── Vapi tool webhook (function calls from voice agent) ───

class VapiToolCall(BaseModel):
    message: dict[str, Any] = Field(default_factory=dict)


def _verify_vapi(secret: str | None, header: str | None):
    expected = get_settings().vapi_server_secret
    if expected and expected != "dev-secret" and header != expected:
        raise HTTPException(401, "invalid vapi secret")


@app.post("/voice/vapi")
async def vapi_webhook(
    payload: dict[str, Any],
    x_vapi_secret: str | None = Header(default=None),
):
    _verify_vapi(get_settings().vapi_server_secret, x_vapi_secret)

    message = payload.get("message") or {}
    if message.get("type") != "tool-calls":
        return {"ok": True}

    results = []
    for tc in message.get("toolCallList", []):
        fn = tc.get("function", {})
        name = fn.get("name")
        args = fn.get("arguments") or {}
        if isinstance(args, str):
            import json

            args = json.loads(args) if args else {}

        tool_call_id = tc.get("id")
        if name == "search_knowledge":
            q = args.get("query", "")
            if not retriever:
                out = "Corpus not loaded."
            else:
                hits = retriever.query(q, k=5)
                out = "\n".join(f"{h['source']}: {h['text'][:400]}" for h in hits)
        elif name == "get_availability":
            from datetime import datetime, timedelta

            cal = CalcomClient()
            slots = await cal.get_slots(
                datetime.now(), datetime.now() + timedelta(days=7)
            )
            out = (
                ", ".join(s["start"] for s in slots[:8])
                if slots
                else "No slots returned — calendar API may need configuration."
            )
        elif name == "book_interview":
            cal = CalcomClient()
            res = await cal.book(
                start_iso=args.get("start_iso", ""),
                name=args.get("name", "Guest"),
                email=args.get("email", "guest@example.com"),
                notes=args.get("notes", "Phone interview via AI persona"),
            )
            out = str(res)
        else:
            out = f"Unknown tool {name}"

        results.append({"toolCallId": tool_call_id, "result": out})

    return {"results": results}


if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
async def root():
    if (STATIC_DIR / "chat.html").exists():
        return RedirectResponse("/chat")
    return {
        "service": "vasanth-ai-persona",
        "docs": "/docs",
        "chat": "/chat",
        "resume": str(ROOT / "data" / "resume.md"),
    }


@app.get("/chat")
async def chat_ui():
    path = STATIC_DIR / "chat.html"
    if not path.exists():
        raise HTTPException(404, "chat UI missing")
    return FileResponse(path, media_type="text/html")
