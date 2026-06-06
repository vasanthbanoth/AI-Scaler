#!/usr/bin/env bash
# Opens .env and validates keys after you save
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENV="$ROOT/.env"

if [[ ! -f "$ENV" ]]; then
  cp "$ROOT/.env.example" "$ENV"
fi

echo "Opening .env — paste your keys after the = sign:"
echo "  OPENAI_API_KEY=sk-proj-...     (from platform.openai.com)"
echo "  CALCOM_API_KEY=cal_live_...    (from cal.com → Developer)"
echo "  CALCOM_EVENT_TYPE_ID=1234567"
echo ""
open -e "$ENV" 2>/dev/null || nano "$ENV" || vi "$ENV"

read -r -p "Press Enter after you've saved .env…"

"$ROOT/scripts/check_env.sh" && "$ROOT/scripts/sync_env.sh"
echo ""
echo "Now restart:  ./scripts/start_all.sh"
