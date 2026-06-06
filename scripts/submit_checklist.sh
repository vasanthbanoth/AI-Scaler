#!/usr/bin/env bash
# Pre-submit verification
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
API="${API_BASE_URL:-http://localhost:8000}"

# shellcheck disable=SC1091
[[ -f .env ]] && set -a && source .env && set +a

echo "═══ Scaler AI Engineer — Submit Checklist ═══"
echo ""

pass=0
fail=0

check() {
  if eval "$2" >/dev/null 2>&1; then
    echo "  ✓ $1"
    pass=$((pass + 1))
  else
    echo "  ✗ $1"
    fail=$((fail + 1))
  fi
}

check "data/resume.md exists" "test -f data/resume.md"
check "data/chunks.json exists" "test -f data/chunks.json"
check "voice/vapi-assistant.json" "test -f voice/vapi-assistant.json"
check "voice/TEST_SCRIPTS.md" "test -f voice/TEST_SCRIPTS.md"
check "evals/golden_qa.json" "test -f evals/golden_qa.json"
check "evals/run_chat_eval.py" "test -f evals/run_chat_eval.py"
check "evals/generate_report.py" "test -f evals/generate_report.py"
check "render.yaml" "test -f render.yaml"
check "Dockerfile" "test -f Dockerfile"
check "docs/ARCHITECTURE.md" "test -f docs/ARCHITECTURE.md"

if curl -sf "$API/health" >/dev/null 2>&1; then
  H=$(curl -s "$API/health")
  echo "  ✓ API health ($API)"
  pass=$((pass + 1))
  echo "$H" | python3 -c "
import json,sys
d=json.load(sys.stdin)
print(f\"     chunks={d.get('chunks_loaded')} corpus_ready={d.get('corpus_ready')} cal={d.get('calendar_configured')}\")
" 2>/dev/null || true
else
  echo "  ✗ API not reachable at $API"
  fail=$((fail + 1))
fi

check "eval PDF exists" "test -f evals/output/eval_report.pdf"
check "chat eval run (optional)" "test -f evals/runs/chat_eval.json"

echo ""
echo "Keys in .env:"
[[ -n "${OPENAI_API_KEY:-}${GROQ_API_KEY:-}" ]] && echo "  ✓ LLM key set" || echo "  ✗ Set OPENAI_API_KEY or GROQ_API_KEY"
[[ -n "${CALCOM_API_KEY:-}" ]] && echo "  ✓ CALCOM_API_KEY set" || echo "  ⚠ CALCOM_API_KEY empty (booking won't confirm)"
[[ -n "${CALCOM_EVENT_TYPE_ID:-}" ]] && echo "  ✓ CALCOM_EVENT_TYPE_ID set" || echo "  ⚠ CALCOM_EVENT_TYPE_ID empty"
[[ -n "${VAPI_API_KEY:-}" ]] && echo "  ✓ VAPI_API_KEY set" || echo "  ⚠ VAPI_API_KEY empty"
[[ -n "${NEXT_PUBLIC_VOICE_PHONE:-}" ]] && echo "  ✓ NEXT_PUBLIC_VOICE_PHONE set" || echo "  ⚠ Phone number not set for landing page"

echo ""
echo "Passed: $pass | Failed/Warnings: $fail+"
echo "Deploy chat URL + phone on form: https://forms.gle/MrZMGCKikHaFkA3J9"
