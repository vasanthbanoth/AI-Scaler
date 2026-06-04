#!/usr/bin/env bash
# Patch vapi-assistant.json and print dashboard checklist
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

# shellcheck disable=SC1091
[[ -f .env ]] && set -a && source .env && set +a

API_BASE_URL="${API_BASE_URL:?Set API_BASE_URL in .env (your Render URL)}"
SECRET="${VAPI_SERVER_SECRET:-dev-secret}"

OUT="$ROOT/voice/vapi-assistant.ready.json"
sed -e "s|{{API_BASE_URL}}|$API_BASE_URL|g" -e "s|{{VAPI_SERVER_SECRET}}|$SECRET|g" \
  "$ROOT/voice/vapi-assistant.json" > "$OUT"

echo "Wrote $OUT"
echo ""
echo "Vapi dashboard steps:"
echo " 1. Assistants → Import JSON ($OUT)"
echo " 2. Server URL: $API_BASE_URL/voice/vapi"
echo " 3. Server secret header: x-vapi-secret: $SECRET"
echo " 4. Phone Numbers → attach assistant → copy E.164 number for form"
echo ""
if [[ -n "${VAPI_API_KEY:-}" ]]; then
  echo "Optional: create via API — see https://docs.vapi.ai"
fi
