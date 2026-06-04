"""Cal.com v2 slots + booking — real calendar, no mock slots."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import httpx

from app.config import get_settings

CAL_BASE = "https://api.cal.com/v2"


class CalcomClient:
    def __init__(self):
        s = get_settings()
        self.api_key = s.calcom_api_key
        self.event_type_id = s.calcom_event_type_id
        self.username = s.calcom_username

    @property
    def configured(self) -> bool:
        return bool(self.api_key and self.event_type_id)

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "cal-api-version": "2024-08-13",
            "Content-Type": "application/json",
        }

    async def get_slots(
        self,
        start: datetime,
        end: datetime,
        timezone: str = "Asia/Kolkata",
    ) -> list[dict[str, Any]]:
        if not self.configured:
            return self._fallback_slots(start, end)

        params = {
            "eventTypeId": self.event_type_id,
            "start": start.strftime("%Y-%m-%d"),
            "end": end.strftime("%Y-%m-%d"),
            "timeZone": timezone,
            "format": "range",
        }
        headers = self._headers()
        headers["cal-api-version"] = "2024-09-04"
        url = f"{CAL_BASE}/slots"
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.get(url, headers=headers, params=params)
            if r.status_code >= 400:
                return self._fallback_slots(start, end)
            data = r.json()
        slots: list[dict[str, Any]] = []
        payload = data.get("data") or {}
        for day, times in payload.items():
            if not isinstance(times, list):
                continue
            for t in times:
                if isinstance(t, dict):
                    slots.append(
                        {
                            "start": t.get("start", f"{day}"),
                            "end": t.get("end"),
                            "timezone": timezone,
                        }
                    )
                else:
                    slots.append({"start": f"{day}T{t}", "timezone": timezone})
        return slots[:12]

    async def book(
        self,
        start_iso: str,
        name: str,
        email: str,
        notes: str = "",
        timezone: str = "Asia/Kolkata",
    ) -> dict[str, Any]:
        if not self.configured:
            return {
                "ok": False,
                "error": "Cal.com not configured. Set CALCOM_API_KEY and CALCOM_EVENT_TYPE_ID.",
            }

        payload = {
            "start": start_iso,
            "eventTypeId": int(self.event_type_id),
            "attendee": {
                "name": name,
                "email": email,
                "timeZone": timezone,
            },
            "metadata": {"notes": notes[:500]},
        }
        url = f"{CAL_BASE}/bookings"
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(url, headers=self._headers(), json=payload)
            body = r.json() if r.content else {}
            if r.status_code >= 400:
                return {"ok": False, "error": body.get("message", r.text)}
            return {"ok": True, "booking": body.get("data", body)}

    def _fallback_slots(self, start: datetime, end: datetime) -> list[dict]:
        """When Cal.com keys missing — return empty so agent says setup pending."""
        return []
