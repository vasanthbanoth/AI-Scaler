# Submission checklist — Vasanth Banoth

Form: https://forms.gle/MrZMGCKikHaFkA3J9

## Before you submit

```bash
# 1. Corpus
EMBEDDING_PROVIDER=local python scripts/ingest.py

# 2. Deploy API (Render) + Web (Vercel apps/web)
# 3. Cal.com + Vapi keys in Render .env
./scripts/configure_vapi.sh   # after Render URL is live

# 4. Voice — 5 test calls (voice/TEST_SCRIPTS.md)
python evals/run_voice_eval.py

# 5. Chat eval
python evals/run_chat_eval.py
python evals/generate_report.py

# 6. Verify
./scripts/submit_checklist.sh
```

## Form fields

| Field | Value |
|-------|-------|
| Name | Vasanth Banoth |
| Email | thevasanthbanoth@gmail.com |
| Hours | _(your honest estimate)_ |
| Voice phone | `+1...` from Vapi dashboard → set `NEXT_PUBLIC_VOICE_PHONE` on Vercel |
| **Public chat URL** | `https://<your-vercel-app>.vercel.app/chat` |
| GitHub | `https://github.com/vasanthbanoth/scaler-ai-persona` |
| Eval PDF | `evals/output/eval_report.pdf` |
| Loom | ≤4 min — architecture + one hard problem (RAG fallback / booking flow) |

## Deploy order

**Full guide:** [docs/DEPLOY.md](docs/DEPLOY.md)

1. Push public GitHub repo
2. **Render** (API backend) — Blueprint from `render.yaml` → copy `https://xxx.onrender.com`
3. **Vercel** (chat UI only) — root directory **`apps/web`** → `API_BASE_URL` = Render URL
4. **Vapi** — `./scripts/configure_vapi.sh` → attach phone → `NEXT_PUBLIC_VOICE_PHONE` on Vercel
5. **Cal.com** — keys on Render
6. Keep live **7 days** after submit

## Hard requirements status

| Requirement | Where |
|-------------|-------|
| Live voice | Vapi phone + `POST /voice/vapi` tools |
| Live chat | Vercel `/chat` → FastAPI `/chat` |
| Real booking | Cal.com v2 + chat `booking_flow.py` + voice `book_interview` |
| RAG grounded | `scripts/ingest.py` → hybrid retrieval, no hardcoded answers |
| Eval PDF | `evals/generate_report.py` |
| Public repo | README + ARCHITECTURE.md + this file |
