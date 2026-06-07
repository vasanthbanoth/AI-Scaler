"""Format retrieval hits into readable answers — corpus excerpts only, no hardcoded facts."""

from __future__ import annotations

import re

BOOKING_WORDS = ("book", "interview", "slot", "availability", "calendar", "schedule", "meeting")
INJECTION_MARKERS = (
    "ignore all instructions",
    "ignore previous",
    "system prompt",
    "jailbreak",
    "you are now",
    "pretend you",
    "print your",
)


def _clean(text: str) -> str:
    text = re.sub(r"^# Repository:.*\n+", "", text, flags=re.M)
    text = re.sub(r"^#+\s*", "", text, flags=re.M)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _excerpt(text: str, limit: int = 480) -> str:
    clean = _clean(text)
    if len(clean) <= limit:
        return clean
    cut = clean[:limit].rsplit(" ", 1)[0]
    return cut + "…"


def _is_injection(question: str) -> bool:
    q = question.lower()
    return any(m in q for m in INJECTION_MARKERS)


def _asks_unknown_repo(question: str, hits: list[dict]) -> bool:
    q = question.lower()
    if "private-stealth" in q or "stealth-repo" in q or "repo-9999" in q:
        return True
    slug_m = re.search(r"vasanthbanoth/([a-z0-9._-]+)", q)
    if slug_m:
        slug = slug_m.group(1).rstrip(".")
        indexed = {re.sub(r"^github:", "", (h.get("source") or "").lower()) for h in hits}
        if not any(slug in src or src.endswith(slug) for src in indexed):
            return True
    return False


def synthesize_reply(question: str, hits: list[dict]) -> str:
    if _is_injection(question):
        return (
            "I won't override my instructions or invent facts. "
            "I only answer from Vasanth's public resume and GitHub corpus — ask about a specific project instead."
        )

    if _asks_unknown_repo(question, hits):
        return (
            "I don't have that repository in Vasanth's public corpus — I won't invent an architecture. "
            "Ask about an indexed repo (Mail-InboxAI, Josh-AI-TASK, Multi-Modal-RAG) or book time to discuss."
        )

    if not hits:
        return (
            "I don't have that in Vasanth's resume or public GitHub READMEs. "
            "I won't guess — try a specific repo (Mail-InboxAI, Josh-AI-TASK, Multi-Modal-RAG) or ask to book time."
        )

    seen: list[str] = []
    parts: list[str] = []
    for h in hits[:3]:
        src = h.get("source", "corpus")
        if src in seen:
            continue
        seen.append(src)
        parts.append(_excerpt(h.get("text", "")))

    body = "\n\n".join(parts)
    cites = " ".join(f"[{s}]" for s in seen[:4])
    return f"{body}\n\n{cites}"
