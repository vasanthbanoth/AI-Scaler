#!/usr/bin/env bash
# One-time local setup — run from repo root
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=== Vasanth AI Persona — setup ==="

if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "Created .env from .env.example"
  echo ""
  echo "Edit .env now and add at minimum:"
  echo "  OPENAI_API_KEY=sk-..."
  echo "  CALCOM_API_KEY=..."
  echo "  CALCOM_EVENT_TYPE_ID=..."
  echo ""
  read -r -p "Press Enter after you've saved .env (or Ctrl+C to exit)…"
fi

# shellcheck disable=SC1091
set -a && source .env && set +a

PY="${PY:-}"
if [[ -z "$PY" ]]; then
  for c in python3.12 python3.11 python3.10 python3; do
    if command -v "$c" &>/dev/null; then PY=$c; break; fi
  done
fi
[[ -n "$PY" ]] || { echo "Python 3.10+ required"; exit 1; }

if [[ ! -d .venv ]]; then
  "$PY" -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -q -U pip
pip install -q -r services/api/requirements.txt httpx tiktoken python-dotenv

if [[ -z "${OPENAI_API_KEY:-}" ]]; then
  echo "ERROR: OPENAI_API_KEY missing in .env"
  exit 1
fi

export REPO_ROOT="$ROOT"
python scripts/ingest.py

echo ""
echo "=== Setup complete ==="
echo "Start server:  ./scripts/start.sh"
echo "Chat URL:      http://localhost:8000/chat"
echo "API docs:      http://localhost:8000/docs"
