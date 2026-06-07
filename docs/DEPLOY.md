# Deploy guide — Unified Deployment

Your app uses a **single unified deployment**. The Next.js frontend is built statically and served by the FastAPI backend on the same port, meaning you only need to deploy the `Dockerfile` to a single host.

| What | Platform | URL you get |
|------|----------|-------------|
| **Chat UI & API** | **Render** | `https://vasanth-persona-api.onrender.com/chat` |
| **Voice** (Part A) | **Vapi** | Phone number from Vapi dashboard |

---

## Step 1 — Push to GitHub (required first)

```bash
cd "/Users/vasanthbanoth/Downloads/AI Scaler"
gh auth login
git add -A
git commit -m "Scaler AI persona — unified voice, RAG chat, evals"
git remote add origin https://github.com/vasanthbanoth/scaler-ai-persona.git
git push -u origin main
```

Create the repo on GitHub first if it doesn't exist: https://github.com/new

---

## Step 2 — Deploy Unified App on Render

1. Go to https://dashboard.render.com → **New +** → **Blueprint**
2. Connect your GitHub repo `scaler-ai-persona`
3. Render reads `render.yaml` automatically
4. In Render dashboard → **Environment**, add:

| Key | Value |
|-----|-------|
| `GROQ_API_KEY` | From https://console.groq.com (free) |
| `OPENAI_API_KEY` | Optional if using Groq |
| `CALCOM_API_KEY` | From Cal.com → Settings → API Keys |
| `CALCOM_EVENT_TYPE_ID` | Cal.com event type ID (number) |
| `VAPI_SERVER_SECRET` | Copy from Render (auto-generated) or your `.env` |
| `NEXT_PUBLIC_VOICE_PHONE` | `+1...` after Vapi setup (Step 3) |

5. Wait for deploy (~5–10 min first time; ingest and frontend build runs on boot via Dockerfile)
6. Verify: `https://YOUR-RENDER-URL.onrender.com/health`  
   → `corpus_ready: true`, `chunks_loaded` > 0

**Copy your Render URL** — e.g. `https://vasanth-persona-api.onrender.com`

---

## Step 3 — Vapi voice (Part A)

After Render is live:

```bash
# In .env set API_BASE_URL to your Render URL, then:
./scripts/configure_vapi.sh
```

1. Vapi dashboard → Assistants → Import `voice/vapi-assistant.ready.json`
2. Server URL: `https://YOUR-RENDER-URL.onrender.com/voice/vapi`
3. Header: `x-vapi-secret: <VAPI_SERVER_SECRET from Render>`
4. Phone Numbers → buy/attach number → copy E.164 (e.g. `+14155551234`)
5. Add to Render env: `NEXT_PUBLIC_VOICE_PHONE=+14155551234` → redeploy

Test with `voice/TEST_SCRIPTS.md` (5 calls).

---

## Step 4 — Cal.com (real booking)

1. https://cal.com → create account / event type (30 min interview)
2. Settings → Developer → **API Key**
3. Event Type ID: from event URL or API
4. Add both to **Render** env.

---

## Step 5 — Submit

| Form field | Your value |
|------------|------------|
| Chat URL | `https://YOUR-RENDER-APP.onrender.com/chat` |
| Phone | Vapi number |
| GitHub | `https://github.com/vasanthbanoth/scaler-ai-persona` |
| PDF | `evals/output/eval_report.pdf` |
| Loom | ≤4 min unified architecture walkthrough |

Form: https://forms.gle/MrZMGCKikHaFkA3J9
