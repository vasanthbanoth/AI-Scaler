#!/usr/bin/env bash
# Push to public GitHub repo (requires: gh auth login)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

REPO_NAME="${1:-scaler-ai-persona}"

if ! gh auth status &>/dev/null; then
  echo "Run once:  gh auth login"
  exit 1
fi

if [[ ! -d .git ]]; then
  git init
  git branch -M main
fi

# ensure secrets not staged
git add -A
git status
if git diff --cached --name-only | grep -E '^\.env$'; then
  echo "ABORT: .env is staged — never commit secrets"
  exit 1
fi

read -r -p "Commit message [initial: Scaler AI persona]?: " MSG
MSG="${MSG:-initial: Scaler AI persona RAG + voice + chat}"

git commit -m "$MSG" 2>/dev/null || echo "(nothing new to commit)"

if ! gh repo view "vasanthbanoth/$REPO_NAME" &>/dev/null; then
  gh repo create "$REPO_NAME" --public --source=. --remote=origin --push
else
  git remote add origin "https://github.com/vasanthbanoth/$REPO_NAME.git" 2>/dev/null || true
  git push -u origin main
fi

echo "Done: https://github.com/vasanthbanoth/$REPO_NAME"
