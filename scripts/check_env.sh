#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENV="$ROOT/.env"
[[ -f "$ENV" ]] || { echo "✗ No .env file"; exit 1; }

check() {
  local key=$1
  local val
  val=$(grep "^${key}=" "$ENV" | cut -d= -f2- | tr -d '"' | tr -d "'" | xargs)
  if [[ -z "$val" ]]; then
    echo "✗ $key is EMPTY — paste your real key"
    return 1
  fi
  echo "✓ $key set (${#val} chars)"
  return 0
}

echo "Checking .env …"
FAIL=0
check OPENAI_API_KEY || FAIL=1
check CALCOM_API_KEY || FAIL=1
check CALCOM_EVENT_TYPE_ID || FAIL=1
if [[ $FAIL -eq 1 ]]; then
  echo ""
  echo "Open .env and paste real keys (not placeholders):"
  echo "  open -e \"$ENV\""
  exit 1
fi
./scripts/sync_env.sh
echo "All required keys present."
