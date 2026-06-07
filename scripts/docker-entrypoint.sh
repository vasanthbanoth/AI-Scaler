#!/bin/sh
set -e
export REPO_ROOT=/app
export PYTHONPATH=/app

echo "[entrypoint] Starting FastAPI Unified Server…"
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
