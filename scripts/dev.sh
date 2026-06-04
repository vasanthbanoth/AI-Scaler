#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ ! -f .env ]]; then
  echo "Copy .env.example → .env and add OPENAI_API_KEY"
  exit 1
fi

if [[ ! -f data/chunks.json ]]; then
  echo "Running ingest…"
  source .venv/bin/activate 2>/dev/null || python3 -m venv .venv && source .venv/bin/activate
  pip install -q -r services/api/requirements.txt httpx tiktoken python-dotenv
  python scripts/ingest.py
fi

export PYTHONPATH="$ROOT/services/api"
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000 --app-dir "$ROOT/services/api" &
API_PID=$!
sleep 2

cd apps/web
npm install --silent
API_BASE_URL=http://localhost:8000 npm run dev &
WEB_PID=$!

trap "kill $API_PID $WEB_PID 2>/dev/null" EXIT
echo "API http://localhost:8000/docs · Chat http://localhost:3000"
wait
