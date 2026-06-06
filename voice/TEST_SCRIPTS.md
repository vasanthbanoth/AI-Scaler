# Voice test scripts (Part A — run 5 calls before submit)

Log each call: first-response latency (Vapi dashboard), booking outcome, transcription notes.

## Call 1 — Intro + role fit
1. Wait for AI intro.
2. Ask: *"Why is Vasanth a good fit for an AI engineer intern role?"*
3. Expect: RAG-backed answer citing Mail-InboxAI / Multi-Modal-RAG.
4. Interrupt mid-answer: *"Wait — what about voice latency?"*
5. Expect: brief recovery, no crash.

## Call 2 — Deep repo probe
1. Ask: *"Walk me through Mail-InboxAI — stack and RAG tradeoffs."*
2. Follow-up: *"What would you change in the architecture?"*
3. Expect: specifics from README (Elysia, Elasticsearch, Groq), honest tradeoff.

## Call 3 — Unknown / refusal
1. Ask: *"Describe vasanthbanoth/private-stealth-repo-9999."*
2. Expect: refuses — not in corpus.

## Call 4 — Availability
1. Ask: *"I'd like to schedule an interview next week."*
2. Expect: `get_availability` tool → real slots (if Cal.com configured) or honest setup message.

## Call 5 — Full booking
1. Ask for slots.
2. Pick a slot: *"Book Tuesday at 2pm IST."*
3. Provide name + email when asked.
4. Expect: `book_interview` → Cal.com confirmation.
5. Record: booking success Y/N.

## Metrics to fill in `evals/generate_report.py` → `VOICE` dict

| Metric | How to measure |
|--------|----------------|
| First-response p50/p95 | Vapi call logs / stopwatch from ring to first speech |
| Transcription | Subjective 1–5 on proper nouns (IIIT, Groq, Elysia) |
| Booking success | N successful / 5 attempts |
