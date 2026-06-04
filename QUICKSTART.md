# Quickstart — do this now (15 min)

## Step 1 — API keys in `.env`

```bash
cd "/Users/vasanthbanoth/Downloads/AI Scaler"
cp .env.example .env
open -e .env   # macOS TextEdit
```

Paste:

```env
OPENAI_API_KEY=sk-...your-key...
CALCOM_API_KEY=cal_live_...
CALCOM_EVENT_TYPE_ID=1234567
API_BASE_URL=http://localhost:8000
VAPI_SERVER_SECRET=pick-a-long-random-string
RUN_INGEST_ON_START=1
```

Get Cal.com: https://cal.com → Event Types → your interview event → Settings → **Event Type ID** + Developer → **API key**.

## Step 2 — One command setup

```bash
chmod +x scripts/*.sh
./scripts/setup.sh
./scripts/start.sh
```

Open: http://localhost:8000/chat

## Step 3 — GitHub (terminal)

```bash
gh auth login
./scripts/publish_github.sh scaler-ai-persona
```

## Step 4 — Render (browser)

1. https://dashboard.render.com → **New** → **Blueprint**
2. Connect `vasanthbanoth/scaler-ai-persona`
3. Add env vars: `OPENAI_API_KEY`, `CALCOM_API_KEY`, `CALCOM_EVENT_TYPE_ID`
4. Deploy → wait ~5 min → visit `https://YOUR_APP.onrender.com/chat`

Update `.env`: `API_BASE_URL=https://YOUR_APP.onrender.com`

## Step 5 — Voice

```bash
./scripts/configure_vapi.sh
```

Import `voice/vapi-assistant.ready.json` in Vapi → attach phone number.

## Step 6 — Submit

- Eval: `python evals/run_chat_eval.py` then `python evals/generate_report.py`
- Form: see `SUBMIT.md`
- Loom: 4 min architecture walkthrough

**I cannot complete steps 1, 3–5 without your API keys and `gh auth login` on your machine.**
