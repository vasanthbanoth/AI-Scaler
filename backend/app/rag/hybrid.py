"""Hybrid retrieval: dense embeddings + BM25 via reciprocal rank fusion."""

from __future__ import annotations

import re

from rank_bm25 import BM25Okapi

from app.rag.retrieve import Retriever
from app.rag.store import Chunk, ChunkStore


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]{2,}", text.lower())


class HybridRetriever(Retriever):
    def __init__(self, store: ChunkStore):
        super().__init__(store)
        corpus = [_tokenize(c.text) for c in store.chunks]
        self._bm25 = BM25Okapi(corpus) if corpus else None

    def query(self, question: str, k: int = 8) -> list[dict]:
        if not self.store.chunks:
            return []

        vec = self.embed(question)
        dense_hits = self.store.search(vec, k=k * 2)
        dense_rank = {c.id: i + 1 for i, (c, _) in enumerate(dense_hits)}

        sparse_rank: dict[str, int] = {}
        if self._bm25:
            scores = self._bm25.get_scores(_tokenize(question))
            top_idx = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[: k * 2]
            sparse_rank = {self.store.chunks[i].id: r + 1 for r, i in enumerate(top_idx) if scores[i] > 0}

        rrf: dict[str, float] = {}
        for chunk_id in set(dense_rank) | set(sparse_rank):
            s = 0.0
            if chunk_id in dense_rank:
                s += 1 / (60 + dense_rank[chunk_id])
            if chunk_id in sparse_rank:
                s += 1 / (60 + sparse_rank[chunk_id])
            rrf[chunk_id] = s

        by_id = {c.id: c for c in self.store.chunks}
        fused = sorted(rrf.items(), key=lambda x: x[1], reverse=True)[:k]

        return [
            {
                "text": by_id[cid].text,
                "source": by_id[cid].source,
                "score": round(score, 4),
                "meta": by_id[cid].meta,
            }
            for cid, score in fused
            if cid in by_id
        ]
