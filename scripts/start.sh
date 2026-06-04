#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ ! -f data/chunks.json ]]; then
  echo "No corpus — run ./scripts/setup.sh first"
  exit 1
fi

# shellcheck disable=SC1091
[[ -f .env ]] && set -a && source .env && set +a
source .venv/bin/activate
export REPO_ROOT="$ROOT"
export PYTHONPATH="$ROOT/services/api"
cd "$ROOT/services/api"
echo "Chat → http://localhost:8000/chat"
exec uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
