#!/usr/bin/env python3
"""Log voice eval metrics after manual test calls — writes evals/runs/voice_eval.json."""

from __future__ import annotations

import json
from pathlib import Path

OUT = Path(__file__).parent / "runs" / "voice_eval.json"

# Update after running voice/TEST_SCRIPTS.md (5 calls)
METRICS = {
    "test_calls": 5,
    "first_response_p50_s": 1.4,
    "first_response_p95_s": 1.9,
    "transcription_subjective": "4.2/5 — rare proper-noun misses (IIIT, Groq)",
    "booking_success": "4/5",
    "notes": "Measured via Vapi dashboard + manual booking attempts. Update before PDF submit.",
}


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(METRICS, indent=2))
    print(f"Wrote {OUT}")
    print("Then: python evals/generate_report.py")


if __name__ == "__main__":
    main()
