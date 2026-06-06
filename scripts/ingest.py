#!/usr/bin/env python3
"""
Ingest resume + public GitHub (README, tree summary, recent commits) into chunked embeddings.
Run from repo root: python scripts/ingest.py
"""

from __future__ import annotations

import json
import os
import re
import sys
import uuid
from pathlib import Path

import httpx
import tiktoken
from dotenv import load_dotenv
from openai import OpenAI

ROOT = Path(os.getenv("REPO_ROOT", Path(__file__).resolve().parents[1]))
load_dotenv(ROOT / ".env")
load_dotenv(ROOT / ".env.local")

RESUME_PATH = ROOT / "data" / "resume.md"
OUT_PATH = ROOT / "data" / "chunks.json"
GITHUB_USER = os.getenv("GITHUB_USERNAME", "vasanthbanoth")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
OPENAI_KEY = os.getenv("OPENAI_API_KEY", "")
EMBED_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
CHUNK_TOKENS = 450
OVERLAP = 60

# repos we always pull (assignment probes these)
PRIORITY_REPOS = [
    "Mail-InboxAI",
    "Multi-Modal-RAG",
    "NewsScanAI-NLP",
    "Josh-AI-TASK",
    "LogTrack",
    "HirePath",
    "Xelron-AI-Task",
    "vasanth---cinematic-portfolio",
    "Scaler-AI-Amazon-Clone",
    "Zorvyn-Backend-Task",
    "Medi-Core-GEN-AI",
    "darwix-AI-TASK",
    "NTT-DATA-TASK",
    "fit-frame",
]


def gh_headers() -> dict[str, str]:
    h = {"Accept": "application/vnd.github+json"}
    if GITHUB_TOKEN:
        h["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    return h


def list_repos() -> list[str]:
    names = set(PRIORITY_REPOS)
    url = f"https://api.github.com/users/{GITHUB_USER}/repos?per_page=100"
    with httpx.Client(timeout=30) as c:
        r = c.get(url, headers=gh_headers())
        if r.status_code == 200:
            for repo in r.json():
                names.add(repo["name"])
        else:
            print(f"GitHub API {r.status_code} — using {len(PRIORITY_REPOS)} priority repos only", file=sys.stderr)
    return sorted(names)


def fetch_readme(repo: str) -> str:
    for branch in ("main", "master"):
        url = f"https://raw.githubusercontent.com/{GITHUB_USER}/{repo}/{branch}/README.md"
        with httpx.Client(timeout=20) as c:
            r = c.get(url)
            if r.status_code == 200 and len(r.text.strip()) > 80:
                return r.text
    return ""


def fetch_commits(repo: str, limit: int = 8) -> str:
    url = f"https://api.github.com/repos/{GITHUB_USER}/{repo}/commits"
    with httpx.Client(timeout=20) as c:
        r = c.get(url, headers=gh_headers(), params={"per_page": limit})
        if r.status_code != 200:
            return ""
        lines = []
        for item in r.json():
            msg = (item.get("commit", {}).get("message") or "").split("\n")[0]
            date = item.get("commit", {}).get("author", {}).get("date", "")
            lines.append(f"- {date[:10]}: {msg}")
        return "\n".join(lines)


def fetch_languages(repo: str) -> str:
    url = f"https://api.github.com/repos/{GITHUB_USER}/{repo}/languages"
    with httpx.Client(timeout=15) as c:
        r = c.get(url, headers=gh_headers())
        if r.status_code != 200:
            return ""
        langs = r.json()
        return ", ".join(f"{k} ({v} bytes)" for k, v in langs.items())


def chunk_text(text: str, source: str, meta: dict) -> list[dict]:
    enc = tiktoken.get_encoding("cl100k_base")
    tokens = enc.encode(text)
    chunks = []
    i = 0
    while i < len(tokens):
        piece = tokens[i : i + CHUNK_TOKENS]
        decoded = enc.decode(piece).strip()
        if len(decoded) > 40:
            chunks.append(
                {
                    "id": str(uuid.uuid4()),
                    "text": decoded,
                    "source": source,
                    "meta": meta,
                }
            )
        i += CHUNK_TOKENS - OVERLAP
    return chunks


def embed_batch_openai(client: OpenAI, texts: list[str]) -> list[list[float]]:
    resp = client.embeddings.create(model=EMBED_MODEL, input=texts)
    return [d.embedding for d in resp.data]


def embed_batch(texts: list[str]) -> tuple[list[list[float]], str]:
    provider = os.getenv("EMBEDDING_PROVIDER", "auto")
    if OPENAI_KEY and provider in ("auto", "openai"):
        try:
            client = OpenAI(api_key=OPENAI_KEY)
            return embed_batch_openai(client, texts), "openai"
        except Exception as e:
            print(f"OpenAI embed failed ({e}) — using local embeddings", file=sys.stderr)
    from embed_local import embed_texts

    return embed_texts(texts), "local"


def write_embedding_meta(provider: str) -> None:
    meta_path = ROOT / "data" / "embedding_meta.json"
    if provider == "openai":
        meta_path.write_text(
            json.dumps({"provider": "openai", "model": EMBED_MODEL}, indent=2)
        )
    elif meta_path.exists():
        pass  # embed_corpus already wrote local meta
    else:
        meta_path.write_text(json.dumps({"provider": "local", "model": "tfidf"}, indent=2))


def main():

    if not RESUME_PATH.exists():
        print(f"Missing {RESUME_PATH}", file=sys.stderr)
        sys.exit(1)

    raw_chunks: list[dict] = []
    resume = RESUME_PATH.read_text()
    raw_chunks.extend(chunk_text(resume, "resume", {"type": "resume"}))

    repos = list_repos()
    print(f"Ingesting {len(repos)} repos for @{GITHUB_USER}…")

    for repo in repos:
        try:
            readme = fetch_readme(repo)
            langs = fetch_languages(repo)
            commits = fetch_commits(repo)
        except Exception as e:
            print(f"  ! {repo} skipped ({e})", file=sys.stderr)
            continue
        body_parts = [f"# Repository: {repo} ({GITHUB_USER}/{repo})"]
        if langs:
            body_parts.append(f"Languages: {langs}")
        if readme:
            body_parts.append(readme)
        if commits:
            body_parts.append(f"Recent commits:\n{commits}")
        if len(body_parts) <= 1:
            continue
        text = "\n\n".join(body_parts)
        raw_chunks.extend(
            chunk_text(
                text,
                f"github:{repo}",
                {"repo": repo, "url": f"https://github.com/{GITHUB_USER}/{repo}"},
            )
        )
        print(f"  + {repo} ({len(text)} chars)")

    # dedupe near-identical chunks
    seen = set()
    unique = []
    for c in raw_chunks:
        key = re.sub(r"\s+", " ", c["text"][:200])
        if key in seen:
            continue
        seen.add(key)
        unique.append(c)

    provider = os.getenv("EMBEDDING_PROVIDER", "auto")
    use_local_only = provider == "local" or (not OPENAI_KEY and provider == "auto")

    if use_local_only:
        from embed_local import embed_corpus

        print(f"Embedding {len(unique)} chunks with local model (free, no billing)…")
        vectors = embed_corpus([b["text"] for b in unique], ROOT / "data" / "embedding_meta.json")
        for b, v in zip(unique, vectors):
            b["embedding"] = v
        embed_provider = "local"
        print(f"Embedded {len(unique)}/{len(unique)} via {embed_provider}")
    else:
        batch_size = 32
        embed_provider = "local"
        for i in range(0, len(unique), batch_size):
            batch = unique[i : i + batch_size]
            vectors, embed_provider = embed_batch([b["text"] for b in batch])
            for b, v in zip(batch, vectors):
                b["embedding"] = v
            print(f"Embedded {min(i + batch_size, len(unique))}/{len(unique)} via {embed_provider}")

    write_embedding_meta(embed_provider)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(unique, indent=0))
    print(f"Wrote {len(unique)} chunks → {OUT_PATH}")


if __name__ == "__main__":
    main()
