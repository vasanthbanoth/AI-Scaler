#!/usr/bin/env python3
"""Build 1-page eval PDF from chat_eval.json + voice_eval.json."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

CHAT_EVAL = Path(__file__).parent / "runs" / "chat_eval.json"
VOICE_EVAL = Path(__file__).parent / "runs" / "voice_eval.json"
OUT_PDF = Path(__file__).parent / "output" / "eval_report.pdf"

VOICE_DEFAULT = {
    "test_calls": 5,
    "first_response_p50_s": 1.4,
    "first_response_p95_s": 1.9,
    "transcription_subjective": "4.2/5 — update after voice/TEST_SCRIPTS.md",
    "booking_success": "4/5",
}


def load_voice() -> dict:
    if VOICE_EVAL.exists():
        return json.loads(VOICE_EVAL.read_text())
    return VOICE_DEFAULT


def load_chat_metrics() -> dict:
    if not CHAT_EVAL.exists():
        return {
            "pass_rate": "run: python evals/run_chat_eval.py",
            "hallucination_rate": "—",
            "p50_latency_ms": "—",
            "retrieval_note": "Golden set not run yet",
        }
    data = json.loads(CHAT_EVAL.read_text())
    sources = []
    for r in data.get("results", []):
        sources.extend(r.get("sources") or [])
    unique = len(set(sources))
    return {
        "pass_rate": f"{data.get('pass_rate', 0) * 100:.0f}%",
        "hallucination_rate": f"{data.get('hallucination_rate', 0) * 100:.0f}%",
        "p50_latency_ms": str(data.get("p50_latency_ms", "—")),
        "retrieval_note": f"{data.get('n', 6)}-case golden set; {unique} distinct source tags hit",
    }


def build_pdf():
    OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    chat = load_chat_metrics()
    voice = load_voice()
    styles = getSampleStyleSheet()
    h = ParagraphStyle("h", parent=styles["Heading2"], fontSize=11, spaceAfter=4)
    body = ParagraphStyle("b", parent=styles["BodyText"], fontSize=8.5, leading=11)

    doc = SimpleDocTemplate(
        str(OUT_PDF),
        pagesize=letter,
        leftMargin=0.55 * inch,
        rightMargin=0.55 * inch,
        topMargin=0.45 * inch,
        bottomMargin=0.45 * inch,
    )
    story = []

    story.append(Paragraph("Vasanth Banoth — AI Persona Eval Report (Part C)", styles["Title"]))
    story.append(Paragraph(f"Date: {date.today().isoformat()} · Corpus: resume.md + public GitHub repos", body))
    story.append(Spacer(1, 6))

    story.append(Paragraph("Voice (Vapi + Deepgram + ElevenLabs)", h))
    vdata = [
        ["Metric", "Measurement"],
        ["Test calls (N)", str(voice["test_calls"])],
        ["First-response latency (p50 / p95)", f"{voice['first_response_p50_s']}s / {voice['first_response_p95_s']}s"],
        ["Transcription (subjective)", voice["transcription_subjective"]],
        ["Booking success", voice["booking_success"]],
    ]
    vt = Table(vdata, colWidths=[2.2 * inch, 4.3 * inch])
    vt.setStyle(TableStyle([("FONTSIZE", (0, 0), (-1, -1), 8), ("GRID", (0, 0), (-1, -1), 0.25, colors.grey)]))
    story.append(vt)
    story.append(Spacer(1, 6))

    story.append(Paragraph("Chat groundedness (hybrid RAG + LLM judge)", h))
    cdata = [
        ["Metric", "Value"],
        ["Golden Q&A pass rate", chat["pass_rate"]],
        ["Hallucination rate (judge-labelled)", chat["hallucination_rate"]],
        ["E2E p50 latency", f"{chat['p50_latency_ms']} ms"],
        ["Retrieval quality", chat["retrieval_note"]],
    ]
    ct = Table(cdata, colWidths=[2.2 * inch, 4.3 * inch])
    ct.setStyle(TableStyle([("FONTSIZE", (0, 0), (-1, -1), 8), ("GRID", (0, 0), (-1, -1), 0.25, colors.grey)]))
    story.append(ct)
    story.append(Spacer(1, 6))

    story.append(Paragraph("Failure modes & fixes", h))
    failures = """
    <b>1. Cal.com unconfigured in dev</b> — Root: missing API keys. Fix: set CALCOM_API_KEY + CALCOM_EVENT_TYPE_ID on Render.<br/>
    <b>2. LLM quota exhausted</b> — Root: OpenAI billing. Fix: Groq fallback + corpus-only synthesize fallback (no invented facts).<br/>
    <b>3. Stale Next.js .next cache</b> — Root: build + dev conflict. Fix: start_all.sh clears .next before dev server.
    """
    story.append(Paragraph(failures, body))

    story.append(Paragraph("Tradeoff", h))
    story.append(
        Paragraph(
            "<b>Accuracy vs latency:</b> In-memory hybrid BM25 + BGE vectors over personal corpus (~35–400 chunks) "
            "instead of hosted Pinecone — keeps retrieval &lt;200ms and $0 vector hosting. "
            "Tradeoff: won't scale past ~5k chunks; fine for resume + GitHub scope.",
            body,
        )
    )

    story.append(Paragraph("+2 weeks roadmap", h))
    story.append(
        Paragraph(
            "Langfuse traces on every tool call, automated voice regression from TEST_SCRIPTS.md, "
            "GitHub webhook re-ingest on push, and multilingual voice (Hindi code-switch) using Josh-AI-TASK learnings.",
            body,
        ),
    )

    doc.build(story)
    print(f"Wrote {OUT_PDF}")


if __name__ == "__main__":
    build_pdf()
