"""In-memory vector store — fine for ~1k chunks from one resume + GitHub corpus."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np


@dataclass
class Chunk:
    id: str
    text: str
    source: str
    meta: dict[str, Any]
    embedding: list[float]


class ChunkStore:
    def __init__(self, path: Path):
        self.path = path
        self.chunks: list[Chunk] = []
        self._matrix: np.ndarray | None = None

    def load(self) -> bool:
        if not self.path.exists():
            return False
        raw = json.loads(self.path.read_text())
        self.chunks = [
            Chunk(
                id=item["id"],
                text=item["text"],
                source=item["source"],
                meta=item.get("meta", {}),
                embedding=item["embedding"],
            )
            for item in raw
        ]
        if self.chunks:
            self._matrix = np.array([c.embedding for c in self.chunks], dtype=np.float32)
            norms = np.linalg.norm(self._matrix, axis=1, keepdims=True)
            self._matrix = self._matrix / np.clip(norms, 1e-9, None)
        return True

    def search(self, query_vec: list[float], k: int = 6) -> list[tuple[Chunk, float]]:
        if not self.chunks or self._matrix is None:
            return []
        q = np.array(query_vec, dtype=np.float32)
        q = q / max(np.linalg.norm(q), 1e-9)
        scores = self._matrix @ q
        idx = np.argsort(scores)[::-1][:k]
        return [(self.chunks[i], float(scores[i])) for i in idx]


def cosine_sim(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)
