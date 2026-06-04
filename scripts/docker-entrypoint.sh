#!/bin/sh
set -e
export REPO_ROOT=/app
export PYTHONPATH=/app

if [ "${RUN_INGEST_ON_START:-0}" = "1" ] && [ ! -f /app/data/chunks.json ]; then
  echo "[entrypoint] Building RAG corpus…"
  python /app/scripts/ingest.py || echo "[entrypoint] Ingest failed — check OPENAI_API_KEY"
fi

exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
