# Deploy guide — Vercel + Render

Your app uses **two free platforms** (this is the intended setup):

| What | Platform | URL you get |
|------|----------|-------------|
| **Chat UI** (Part B) | **Vercel** | `https://your-app.vercel.app/chat` |
| **API + RAG + Cal.com + Vapi** | **Render** | `https://vasanth-persona-api.onrender.com` |
| **Voice** (Part A) | **Vapi** (not Vercel) | Phone number from Vapi dashboard |

You do **not** deploy everything on Vercel alone — the Python FastAPI backend must run on Render (or Railway/Fly.io). Vercel only hosts the Next.js frontend.

---

## Step 1 — Push to GitHub (required first)

```bash
cd "/Users/vasanthbanoth/Downloads/AI Scaler"
gh auth login
git add -A
git commit -m "Scaler AI persona — voice, RAG chat, evals"
git remote add origin https://github.com/vasanthbanoth/scaler-ai-persona.git
git push -u origin main
```

Create the repo on GitHub first if it doesn't exist: https://github.com/new

---

## Step 2 — Deploy API on Render (backend)

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

5. Wait for deploy (~5–10 min first time; ingest runs on boot)
6. Verify: `https://YOUR-RENDER-URL.onrender.com/health`  
   → `corpus_ready: true`, `chunks_loaded` > 0

**Copy your Render URL** — e.g. `https://vasanth-persona-api.onrender.com`

---

## Step 3 — Deploy chat on Vercel (frontend)

1. Go to https://vercel.com/new
2. Import the same GitHub repo
3. **Important:** set **Root Directory** → `apps/web`
4. Framework: Next.js (auto-detected)
5. **Environment variables:**

| Key | Value |
|-----|-------|
| `API_BASE_URL` | `https://YOUR-RENDER-URL.onrender.com` |
| `NEXT_PUBLIC_API_BASE_URL` | Same Render URL |
| `OPENAI_API_KEY` | Same as Render (or leave empty if using Groq on API only) |
| `NEXT_PUBLIC_VOICE_PHONE` | `+1...` after Vapi setup (Step 4) |

6. Deploy
7. Your public chat URL: **`https://YOUR-VERCEL-APP.vercel.app/chat`**

---

## Step 4 — Vapi voice (Part A)

After Render is live:

```bash
# In .env set API_BASE_URL to your Render URL, then:
./scripts/configure_vapi.sh
```

1. Vapi dashboard → Assistants → Import `voice/vapi-assistant.ready.json`
2. Server URL: `https://YOUR-RENDER-URL.onrender.com/voice/vapi`
3. Header: `x-vapi-secret: <VAPI_SERVER_SECRET from Render>`
4. Phone Numbers → buy/attach number → copy E.164 (e.g. `+14155551234`)
5. Add to Vercel env: `NEXT_PUBLIC_VOICE_PHONE=+14155551234` → redeploy

Test with `voice/TEST_SCRIPTS.md` (5 calls).

---

## Step 5 — Cal.com (real booking)

1. https://cal.com → create account / event type (30 min interview)
2. Settings → Developer → **API Key**
3. Event Type ID: from event URL or API
4. Add both to **Render** env (not Vercel — booking runs on API)

---

## Step 6 — Submit

| Form field | Your value |
|------------|------------|
| Chat URL | `https://YOUR-VERCEL-APP.vercel.app/chat` |
| Phone | Vapi number |
| GitHub | `https://github.com/vasanthbanoth/scaler-ai-persona` |
| PDF | `evals/output/eval_report.pdf` |
| Loom | ≤4 min architecture walkthrough |

Form: https://forms.gle/MrZMGCKikHaFkA3J9

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Chat says "Cannot reach API" | `API_BASE_URL` on Vercel must be Render URL (no trailing slash) |
| `corpus_ready: false` on Render | Wait for ingest; check Render logs; set `EMBEDDING_PROVIDER=local` |
| Render cold start slow | Free tier sleeps after 15 min — first request wakes it (~30s) |
| Booking fails | `CALCOM_API_KEY` + `CALCOM_EVENT_TYPE_ID` on Render only |

```bash
./scripts/submit_checklist.sh   # verify locally before form
```
