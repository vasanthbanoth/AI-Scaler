"""Keyword fallback for local demo when chunks.json / OpenAI are unavailable."""

from __future__ import annotations

import re
from pathlib import Path

from app.rag.store import Chunk, ChunkStore


def load_demo_store(resume_path: Path) -> ChunkStore:
    store = ChunkStore(resume_path.parent / "_demo_unused.json")
    text = resume_path.read_text()
    parts = re.split(r"(?=^## )", text, flags=re.MULTILINE)
    store.chunks = []
    for i, part in enumerate(parts):
        part = part.strip()
        if len(part) < 40:
            continue
        store.chunks.append(
            Chunk(
                id=f"demo-{i}",
                text=part,
                source="resume",
                meta={"demo": True},
                embedding=[0.0],
            )
        )
    store._matrix = None
    return store


def keyword_search(store: ChunkStore, query: str, k: int = 6) -> list[tuple[Chunk, float]]:
    words = {w.lower() for w in re.findall(r"[a-z0-9]{3,}", query)}
    if not words:
        return []
    scored = []
    for c in store.chunks:
        blob = c.text.lower()
        hits = sum(1 for w in words if w in blob)
        if hits:
            scored.append((c, hits / len(words)))
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:k]
