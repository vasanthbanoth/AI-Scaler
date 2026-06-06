"""Multi-turn Cal.com booking for chat (mirrors voice book_interview tool)."""

from __future__ import annotations

import re
from datetime import datetime, timedelta
from typing import Any

from app.calendar.calcom import CalcomClient

_sessions: dict[str, dict[str, Any]] = {}

BOOKING_WORDS = ("book", "interview", "slot", "availability", "calendar", "schedule", "meeting")
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
ISO_RE = re.compile(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(?::\d{2})?(?:[+-]\d{2}:\d{2}|Z)?")


def is_booking_intent(text: str) -> bool:
    q = text.lower()
    return any(w in q for w in BOOKING_WORDS)


def _sid(session_id: str | None) -> str:
    return session_id or "default"


def _extract_name(text: str, email: str) -> str:
    for pat in (
        r"(?:name[:\s]+)([A-Za-z][A-Za-z .'-]{1,40})",
        r"(?:i(?:'m| am)\s+)([A-Za-z][A-Za-z .'-]{1,40})",
    ):
        m = re.search(pat, text, re.I)
        if m:
            return m.group(1).strip()
    before = text.split(email)[0].strip()
    parts = [p.strip() for p in re.split(r"[,;]", before) if p.strip()]
    for p in reversed(parts):
        if not ISO_RE.search(p) and len(p.split()) <= 4 and re.match(r"^[A-Za-z]", p):
            return p
    return "Guest"


async def try_complete_booking(message: str, session_id: str | None) -> str | None:
    """If message has email + slot, attempt Cal.com book."""
    email_m = EMAIL_RE.search(message)
    iso_m = ISO_RE.search(message)
    if not email_m or not iso_m:
        return None

    email = email_m.group()
    name = _extract_name(message, email)
    start_iso = iso_m.group().replace(" ", "T")
    if "T" in start_iso and not start_iso.endswith("Z") and "+" not in start_iso[10:]:
        start_iso += "+05:30"

    cal = CalcomClient()
    if not cal.configured:
        return (
            f"Got it — **{name}** ({email}) for `{start_iso}`. "
            "Cal.com isn't wired yet; Vasanth will confirm at **thevasanthbanoth@gmail.com**."
        )

    result = await cal.book(
        start_iso=start_iso,
        name=name,
        email=email,
        notes="Booked via chat",
    )
    _sessions.pop(_sid(session_id), None)
    if result.get("ok"):
        return (
            f"**Interview confirmed** for {name} ({email}) at `{start_iso}` (IST). "
            "You should receive a Cal.com confirmation email shortly."
        )
    return f"Booking failed: {result.get('error', 'unknown error')}. Try another slot or email thevasanthbanoth@gmail.com."


async def handle_booking(message: str, session_id: str | None) -> str:
    sid = _sid(session_id)
    completed = await try_complete_booking(message, session_id)
    if completed:
        return completed

    cal = CalcomClient()
    start = datetime.now()
    end = start + timedelta(days=7)
    slots = await cal.get_slots(start, end)

    if cal.configured and slots:
        _sessions[sid] = {"slots": slots[:8]}
        lines = "\n".join(f"• `{s['start']}`" for s in slots[:8])
        return (
            "Available interview slots (next 7 days, IST):\n\n"
            f"{lines}\n\n"
            "To confirm, reply with: **slot ISO time**, your **name**, and **email**.\n"
            "Example: `2026-06-10T14:00:00+05:30`, Priya Sharma, priya@company.com"
        )

    _sessions[sid] = {"awaiting": "details"}
    return (
        "Vasanth is available **Mon–Sat, 10:00–20:00 IST**.\n\n"
        "Cal.com live slots need API keys configured. For now, send your **preferred time**, "
        "**name**, and **email** — e.g. `2026-06-10T14:00:00+05:30`, Your Name, you@email.com — "
        "or email **thevasanthbanoth@gmail.com**."
    )
