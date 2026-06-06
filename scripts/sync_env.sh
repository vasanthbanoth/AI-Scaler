#!/usr/bin/env bash
# Copy root .env → apps/web/.env.local (Next.js only reads env from its own directory)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
if [[ ! -f "$ROOT/.env" ]]; then
  echo "Missing $ROOT/.env — run ./scripts/auto_everything.sh first"
  exit 1
fi
cp "$ROOT/.env" "$ROOT/apps/web/.env.local"
# Browser-safe public vars (Next.js only exposes NEXT_PUBLIC_* to client)
API_URL="${API_BASE_URL:-http://localhost:8000}"
if grep -q '^NEXT_PUBLIC_API_BASE_URL=' "$ROOT/apps/web/.env.local" 2>/dev/null; then
  sed -i '' "s|^NEXT_PUBLIC_API_BASE_URL=.*|NEXT_PUBLIC_API_BASE_URL=$API_URL|" "$ROOT/apps/web/.env.local"
else
  echo "NEXT_PUBLIC_API_BASE_URL=$API_URL" >> "$ROOT/apps/web/.env.local"
fi
echo "✓ Synced .env → apps/web/.env.local"
