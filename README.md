# Vasanth Banoth — AI Hiring Persona

End-to-end AI representative for the **Scaler AI Engineer Intern** screening: voice agent, RAG-grounded chat, and real Cal.com booking.

[![Architecture](docs/ARCHITECTURE.md)](docs/ARCHITECTURE.md) · [Submit guide](SUBMIT.md)

## What evaluators get

| Part | Deliverable |
|------|-------------|
| **A — Voice (35%)** | Vapi phone number · `search_knowledge` · `get_availability` · `book_interview` |
| **B — Chat (35%)** | Public `/chat` URL · hybrid RAG · booking from chat · injection-safe |
| **C — Evals (30%)** | `evals/output/eval_report.pdf` · golden Q&A · voice test scripts |

## Stack

| Layer | Tech |
|-------|------|
| Chat UI | Next.js 15, Tailwind, Vercel AI SDK |
| API | FastAPI, hybrid BM25 + BGE vectors, Groq/OpenAI LLM |
| Corpus | `resume.md` + GitHub READMEs/commits → `chunks.json` |
| Voice | Vapi · Deepgram nova-2 · ElevenLabs · Twilio |
| Calendar | Cal.com API v2 |
| Deploy | Vercel (web) + Render (API) |

## Quick start

```bash
cp .env.example .env
# Fill keys (see SUBMIT.md). Minimum for local RAG: EMBEDDING_PROVIDER=local

./scripts/auto_everything.sh   # ingest + deps
./scripts/start_all.sh         # API :8000 + UI :3000
```

- Landing: http://localhost:3000  
- Chat: http://localhost:3000/chat  
- API: http://localhost:8000/health  

## Voice setup

```bash
# After Render API is live:
./scripts/configure_vapi.sh
# Import voice/vapi-assistant.ready.json in Vapi dashboard
# Run 5 test calls: voice/TEST_SCRIPTS.md
```

## Evals (Part C)

```bash
python evals/run_chat_eval.py      # needs live API + OPENAI_API_KEY (judge)
python evals/run_voice_eval.py     # update metrics after voice tests
python evals/generate_report.py    # → evals/output/eval_report.pdf
```

## Deploy

**Vercel** = chat UI · **Render** = API/RAG/voice webhooks · **Vapi** = phone

See **[docs/DEPLOY.md](docs/DEPLOY.md)** for step-by-step instructions.

## Cost

| Item | ~USD |
|------|------|
| Voice call 5 min | 0.08–0.15 |
| Chat session | 0.03–0.06 |
| Ingest (local BGE) | 0 |

## Security

- `.env` gitignored — keys only in Vercel/Render dashboards
- Chat proxies to FastAPI server-side; browser never sees API keys

## Author

**Vasanth Banoth** — [GitHub](https://github.com/vasanthbanoth) · thevasanthbanoth@gmail.com
