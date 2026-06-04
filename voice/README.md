# Voice agent (Vapi + Twilio)

## Stack

| Layer | Choice | Why |
|-------|--------|-----|
| Orchestration | [Vapi](https://vapi.ai) | Sub-2s latency target, barge-in, tool calls |
| STT | Deepgram `nova-2` | Accurate interruptions |
| TTS | ElevenLabs | Natural phone voice |
| Telephony | Twilio (via Vapi dashboard) | US/IN numbers |
| Knowledge + calendar | Your FastAPI `API_BASE_URL` | Same RAG + Cal.com as chat |

## Setup (≈30 min)

1. Create account at https://dashboard.vapi.ai
2. Import `vapi-assistant.json` (replace `{{API_BASE_URL}}` and `{{VAPI_SERVER_SECRET}}`)
3. Add server tools URL: `https://<your-api>/voice/vapi` with header `x-vapi-secret: <VAPI_SERVER_SECRET>`
4. Buy/import a phone number in Vapi → attach assistant
5. Set env on API: `VAPI_SERVER_SECRET`, `CALCOM_*`, `OPENAI_API_KEY`

## Latency tips

- Use `gpt-4o-mini` (not full 4o) on voice model
- Keep `search_knowledge` queries short; corpus is small
- `responseDelaySeconds: 0.4` — tune down once stable
- Run API in `us-east` or `ap-south-1` close to Vapi region

## Test script

Run 5 calls and log:

- time from user stop-speaking → first audio (target &lt;2s)
- booking success rate (3/5 minimum before submit)

Record metrics in `evals/generate_report.py`.
