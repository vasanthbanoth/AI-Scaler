# Submission checklist (48h)

## Before you submit the form

- [ ] `data/resume.md` matches your real resume (dates, Xelron, IIIT Kota)
- [ ] `python scripts/ingest.py` succeeded → `/health` shows `chunks_loaded > 0`
- [ ] Cal.com event type live (15–30 min slots, IST timezone)
- [ ] Chat URL public (Vercel) — test golden questions from `evals/golden_qa.json`
- [ ] Voice number answers + books (5 test calls logged)
- [ ] `evals/output/eval_report.pdf` generated with real voice numbers
- [ ] GitHub repo public — this repo, clean README
- [ ] Loom ≤4 min uploaded (unlisted or public link)
- [ ] Form: https://forms.gle/MrZMGCKikHaFkA3J9
- [ ] Checkbox: links stay live **7 days**

## Env vars you must set (never in git)

| Variable | Where |
|----------|-------|
| `OPENAI_API_KEY` | Render + Vapi |
| `CALCOM_API_KEY`, `CALCOM_EVENT_TYPE_ID` | Render |
| `VAPI_API_KEY`, phone number | Vapi dashboard |
| `VAPI_SERVER_SECRET` | Render + Vapi server URL secret |
| `API_BASE_URL` | Vercel + replace in `voice/vapi-assistant.json` |

## What I need from you (if stuck)

1. OpenAI API key (billing on)
2. Cal.com account + event type ID
3. Vapi account (free trial often includes credits)
4. Confirm resume PDF content — paste updates into `data/resume.md`
5. Optional: `GITHUB_TOKEN` for faster ingest
