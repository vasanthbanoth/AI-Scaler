# Architecture

```mermaid
flowchart TB
  subgraph evaluators [Scaler evaluators]
    Phone[Phone call]
    Web[Browser chat]
  end

  subgraph edge [Vercel — Next.js 15]
    Landing[Landing /]
    ChatUI[Chat /chat]
    ChatAPI[API /api/chat]
  end

  subgraph compute [Render — FastAPI]
    RAG[Hybrid RAG<br/>BM25 + BGE vectors]
    Cal[Cal.com v2]
    BookFlow[booking_flow.py]
    VapiHook[/voice/vapi]
  end

  subgraph voice [Vapi cloud]
    Vapi[Vapi orchestrator]
    STT[Deepgram nova-2]
    TTS[ElevenLabs]
    Twilio[Twilio number]
  end

  subgraph corpus [Offline ingest]
    Resume[data/resume.md]
    GH[GitHub API<br/>README + commits]
    Chunks[data/chunks.json]
  end

  Web --> Landing
  Web --> ChatUI
  ChatUI --> ChatAPI
  ChatAPI -->|POST /chat| RAG
  ChatAPI -->|booking intent| BookFlow
  BookFlow --> Cal
  Phone --> Twilio --> Vapi
  Vapi --> STT
  Vapi --> TTS
  Vapi --> VapiHook
  VapiHook --> RAG
  VapiHook --> Cal
  ingest[scripts/ingest.py] --> Resume
  ingest --> GH
  ingest --> Chunks
  RAG --> Chunks
```

## Security model

| Secret | Where it lives | Never in |
|--------|----------------|----------|
| `OPENAI_API_KEY` / `GROQ_API_KEY` | Vercel + Render env | Client bundle, git |
| `CALCOM_API_KEY` | Render env | Client |
| `VAPI_*` | Vapi dashboard + Render | Client |
| `GITHUB_TOKEN` | Render / local ingest | Client |

`NEXT_PUBLIC_*` only for `NEXT_PUBLIC_VOICE_PHONE` and `NEXT_PUBLIC_API_BASE_URL`.

## Latency budget

| Path | Target | How |
|------|--------|-----|
| Chat response | &lt;2s | FastAPI RAG + LLM or corpus synthesize fallback |
| Voice first audio | &lt;2s | Vapi + gpt-4o-mini + short tool payloads |
| RAG retrieval | &lt;200ms | In-memory hybrid index |

## Cost (estimate)

| Unit | Cost |
|------|------|
| Voice call ~5 min | $0.08–0.15 |
| Chat session ~10 turns | $0.03–0.06 |
| One-time ingest (local BGE) | $0 |
