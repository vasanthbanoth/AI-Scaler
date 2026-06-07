from __future__ import annotations

import logging
import os
import subprocess
import sys
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import PlainTextResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.booking_flow import handle_booking, is_booking_intent, try_complete_booking
from app.calendar.calcom import CalcomClient
from app.config import ROOT, get_settings
from app.rag.demo import keyword_search, load_demo_store
from app.rag.hybrid import HybridRetriever
from app.rag.store import ChunkStore
from app.rag.synthesize import synthesize_reply

log = logging.getLogger("persona")
store = ChunkStore(get_settings().chunks_path)
retriever: HybridRetriever | None = None
demo_mode = False


def _maybe_run_ingest():
    settings = get_settings()
    if store.load():
        return True
    embed_local = os.getenv("EMBEDDING_PROVIDER", "auto") == "local"
    if not settings.openai_api_key and not embed_local:
        log.warning("No chunks.json — set OPENAI_API_KEY or EMBEDDING_PROVIDER=local for ingest")
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
    global retriever, demo_mode
    if _maybe_run_ingest() or store.load():
        retriever = HybridRetriever(store)
    elif (ROOT / "data" / "resume.md").exists():
        demo_store = load_demo_store(ROOT / "data" / "resume.md")
        store.chunks = demo_store.chunks
        demo_mode = True
        log.warning("Resume-only demo mode — run ingest.py for full GitHub RAG")
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
    s = get_settings()
    cal = CalcomClient()
    return {
        "ok": True,
        "chunks_loaded": len(store.chunks),
        "corpus_ready": len(store.chunks) > 0 and not demo_mode,
        "demo_mode": demo_mode,
        "openai_configured": bool(s.openai_api_key and s.openai_api_key.startswith("sk-")),
        "groq_configured": bool(s.groq_api_key),
        "calendar_configured": cal.configured,
        "retrieval": "hybrid" if retriever else ("demo" if demo_mode else "none"),
    }


@app.post("/rag/search")
async def rag_search(body: SearchRequest):
    if not retriever and not demo_mode:
        raise HTTPException(503, "Corpus not ingested. Run: python scripts/ingest.py")
    return {"results": _retrieve(body.query, k=body.k)}


def _retrieve(message: str, k: int = 8) -> list[dict]:
    if retriever:
        return retriever.query(message, k=k)
    if demo_mode:
        hits = keyword_search(store, message, k=k)
        return [
            {
                "text": c.text,
                "source": c.source + " (demo)",
                "score": round(score, 4),
                "meta": c.meta,
            }
            for c, score in hits
        ]
    return []


@app.post("/chat", response_model=ChatResponse)
async def chat(body: ChatRequest):
    if not retriever and not demo_mode:
        raise HTTPException(503, "Corpus not ingested. Run: python scripts/ingest.py")

    t0 = time.perf_counter()
    settings = get_settings()

    booking_done = await try_complete_booking(body.message, body.session_id)
    if booking_done:
        latency = int((time.perf_counter() - t0) * 1000)
        return ChatResponse(reply=booking_done, sources=[], latency_ms=latency)

    if is_booking_intent(body.message):
        reply = await handle_booking(body.message, body.session_id)
        latency = int((time.perf_counter() - t0) * 1000)
        return ChatResponse(reply=reply, sources=[], latency_ms=latency)

    hits = _retrieve(body.message, k=8)
    context = "\n\n---\n\n".join(
        f"[{h['source']}] (score={h['score']})\n{h['text']}" for h in hits
    )

    def _grounded_reply() -> str:
        return synthesize_reply(body.message, hits)

    from app.rag.synthesize import _asks_unknown_repo, _is_injection

    if _is_injection(body.message) or _asks_unknown_repo(body.message, hits):
        latency = int((time.perf_counter() - t0) * 1000)
        return ChatResponse(reply=_grounded_reply(), sources=hits[:2], latency_ms=latency)

    if demo_mode and not settings.openai_api_key and not settings.groq_api_key:
        latency = int((time.perf_counter() - t0) * 1000)
        return ChatResponse(reply=_grounded_reply(), sources=hits, latency_ms=latency)

    try:
        from app.llm import chat_completion

        reply = chat_completion(context, body.message)
    except Exception as e:
        log.warning("LLM fallback: %s", e)
        reply = _grounded_reply()

    latency = int((time.perf_counter() - t0) * 1000)
    return ChatResponse(reply=reply, sources=hits, latency_ms=latency)


@app.post("/api/chat")
async def api_chat_frontend(request: Request):
    data = await request.json()
    messages = data.get("messages", [])
    session_id = data.get("session_id") or data.get("id") or "web-default"
    
    last_user = next((m for m in reversed(messages) if m.get("role") == "user"), None)
    if not last_user or not last_user.get("content"):
        raise HTTPException(400, "No message provided")
    
    chat_req = ChatRequest(message=last_user.get("content"), session_id=session_id)
    chat_res = await chat(chat_req)
    
    text = chat_res.reply or "No reply generated."
    sources = chat_res.sources or []
    if sources:
        chips = " ".join(f"[{s.get('source', '')}]" for s in sources[:5])
        text += f"\n\n---\n*Sources: {chips}*"
        
    return PlainTextResponse(text)


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
            hits = _retrieve(q, k=5)
            out = (
                "\n".join(f"{h['source']}: {h['text'][:400]}" for h in hits)
                if hits
                else "No matching context in corpus."
            )
        elif name == "get_availability":
            from datetime import datetime, timedelta

            cal = CalcomClient()
            slots = await cal.get_slots(datetime.now(), datetime.now() + timedelta(days=7))
            out = (
                ", ".join(s["start"] for s in slots[:8])
                if slots
                else "No slots — Cal.com may need CALCOM_API_KEY and CALCOM_EVENT_TYPE_ID."
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


@app.get("/{full_path:path}", include_in_schema=False)
async def catch_all(full_path: str):
    out_dir = ROOT / "frontend" / "out"
    path = out_dir / full_path
    if path.is_file():
        return FileResponse(path)
    
    html_path = out_dir / f"{full_path}.html"
    if html_path.is_file():
        return FileResponse(html_path)
        
    if full_path == "" and (out_dir / "index.html").is_file():
        return FileResponse(out_dir / "index.html")
        
    if (out_dir / "404.html").is_file():
        return FileResponse(out_dir / "404.html", status_code=404)
        
    raise HTTPException(status_code=404, detail="Not Found")
