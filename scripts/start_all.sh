#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export PATH="$ROOT/.tools/node/bin:$ROOT/.tools/bin:$PATH"
cd "$ROOT"

# shellcheck disable=SC1091
[[ -f .env ]] && set -a && source .env && set +a
./scripts/sync_env.sh

# Free ports from stale processes
for port in 8000 3000; do
  pids=$(lsof -ti :"$port" 2>/dev/null || true)
  if [[ -n "$pids" ]]; then
    echo "Stopping process on :$port …"
    kill $pids 2>/dev/null || true
    sleep 1
  fi
done

source .venv/bin/activate
export REPO_ROOT="$ROOT"
export PYTHONPATH="$ROOT/services/api"

echo "Starting API on :8000 …"
cd "$ROOT/services/api"
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
API_PID=$!

sleep 2
if ! curl -sf http://localhost:8000/health >/dev/null; then
  echo "ERROR: API failed to start. Check logs above."
  kill $API_PID 2>/dev/null || true
  exit 1
fi

echo "Starting Next.js on :3000 …"
cd "$ROOT/apps/web"
# Avoid stale .next chunks after `npm run build` breaks dev mode
rm -rf .next
npm run dev &
WEB_PID=$!

sleep 3
trap 'kill $API_PID $WEB_PID 2>/dev/null' EXIT
echo ""
echo "  ✓ Landing  → http://localhost:3000"
echo "  ✓ Chat     → http://localhost:3000/chat"
echo "  ✓ API      → http://localhost:8000/health"
echo ""
wait
