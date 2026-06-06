#!/usr/bin/env bash
# Automates everything that does NOT require your API keys.
# Keys: paste once into .env, re-run this script.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

export PATH="$ROOT/.tools/bin:$PATH"

echo "╔══════════════════════════════════════════╗"
echo "║  Vasanth AI Persona — auto setup         ║"
echo "╚══════════════════════════════════════════╝"

# ── 1. Portable Node (no system install needed) ──
if [[ ! -x "$ROOT/.tools/bin/node" ]]; then
  echo "→ Installing Node.js to .tools/ …"
  ARCH=$(uname -m)
  VER="v22.14.0"
  [[ "$ARCH" == "arm64" ]] && PKG="node-${VER}-darwin-arm64" || PKG="node-${VER}-darwin-x64"
  curl -fsSL "https://nodejs.org/dist/${VER}/${PKG}.tar.gz" -o /tmp/node.tar.gz
  mkdir -p "$ROOT/.tools"
  tar -xzf /tmp/node.tar.gz -C "$ROOT/.tools" --strip-components=1
  rm /tmp/node.tar.gz
fi
echo "✓ Node $(node -v) · npm $(npm -v)"

# ── 2. Python venv + deps ──
PY="${PY:-}"
for c in python3.12 python3.11 python3.10 python3; do
  command -v "$c" &>/dev/null && PY=$c && break
done
[[ -n "$PY" ]] || { echo "✗ Python 3.10+ required"; exit 1; }

if [[ ! -d .venv ]]; then
  "$PY" -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -q -U pip
pip install -q -r services/api/requirements.txt httpx tiktoken python-dotenv
echo "✓ Python deps installed"

# ── 3. .env bootstrap ──
if [[ ! -f .env ]]; then
  cp .env.example .env
  # generate webhook secret automatically
  SECRET=$(openssl rand -hex 24 2>/dev/null || python3 -c "import secrets; print(secrets.token_hex(24))")
  if [[ "$(uname)" == "Darwin" ]]; then
    sed -i '' "s/VAPI_SERVER_SECRET=/VAPI_SERVER_SECRET=${SECRET}/" .env
  else
    sed -i "s/VAPI_SERVER_SECRET=/VAPI_SERVER_SECRET=${SECRET}/" .env
  fi
  echo "✓ Created .env — YOU MUST add OPENAI_API_KEY + CALCOM_* (see below)"
fi
# shellcheck disable=SC1091
set -a && source .env && set +a
chmod +x scripts/sync_env.sh
./scripts/sync_env.sh 2>/dev/null || true

# ── 4. Check required secrets ──
MISSING=()
CAL_MISSING=()
[[ -z "${OPENAI_API_KEY:-}" || "${OPENAI_API_KEY}" == "sk-..." ]] && MISSING+=("OPENAI_API_KEY")
[[ -z "${CALCOM_API_KEY:-}" ]] && CAL_MISSING+=("CALCOM_API_KEY")
[[ -z "${CALCOM_EVENT_TYPE_ID:-}" ]] && CAL_MISSING+=("CALCOM_EVENT_TYPE_ID")

if [[ ${#MISSING[@]} -gt 0 ]]; then
  echo ""
  echo "⚠  Cannot run ingest without:"
  for m in "${MISSING[@]}"; do echo "   • $m"; done
  echo "   OPENAI → https://platform.openai.com/api-keys"
  INGEST_SKIP=1
else
  INGEST_SKIP=0
fi

if [[ ${#CAL_MISSING[@]} -gt 0 ]]; then
  echo ""
  echo "ℹ  Cal.com keys missing (booking won't work until added):"
  for m in "${CAL_MISSING[@]}"; do echo "   • $m"; done
  echo "   CALCOM → https://cal.com → Developer → API keys + Event Type ID"
fi

# ── 5. RAG ingest ──
if [[ "$INGEST_SKIP" == "0" ]]; then
  if [[ ! -f data/chunks.json ]]; then
    echo "→ Running corpus ingest (resume + GitHub) …"
    export REPO_ROOT="$ROOT"
    python scripts/ingest.py
    echo "✓ Corpus built: $(python -c "import json; print(len(json.load(open('data/chunks.json'))))") chunks"
  else
    echo "✓ Corpus already exists (data/chunks.json)"
  fi
fi

# ── 6. Next.js deps ──
echo "→ npm install (apps/web) …"
cd "$ROOT/apps/web"
npm install --silent
echo "✓ Next.js deps installed"

# ── 7. Vapi config file (needs API_BASE_URL) ──
cd "$ROOT"
if [[ -n "${API_BASE_URL:-}" && "$API_BASE_URL" != "http://localhost:8000" ]]; then
  ./scripts/configure_vapi.sh 2>/dev/null && echo "✓ Vapi JSON ready" || true
fi

# ── 8. Summary ──
echo ""
echo "════════════════════════════════════════════"
if [[ "$INGEST_SKIP" == "0" ]]; then
  echo "READY TO RUN:"
  echo "  ./scripts/start_all.sh"
  echo "  Chat → http://localhost:3000/chat"
  echo "  API  → http://localhost:8000/health"
else
  echo "PARTIAL — add keys to .env, re-run this script."
  echo "Then: ./scripts/start_all.sh"
fi
echo "════════════════════════════════════════════"
