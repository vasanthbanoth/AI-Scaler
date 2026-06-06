"""Free local embeddings — no OpenAI billing required."""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path


def _fastembed(texts: list[str]) -> list[list[float]]:
    from fastembed import TextEmbedding

    model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
    return [vec.tolist() for vec in model.embed(texts)]


def _tfidf_embed_all(texts: list[str]) -> tuple[list[list[float]], dict[str, int]]:
    vocab: dict[str, int] = {}
    for t in texts:
        for tok in set(re.findall(r"[a-z0-9]{3,}", t.lower())):
            vocab.setdefault(tok, len(vocab))

    dim = max(len(vocab), 1)
    out = []
    for t in texts:
        tokens = re.findall(r"[a-z0-9]{3,}", t.lower())
        vec = [0.0] * dim
        counts = Counter(tokens)
        for tok, c in counts.items():
            if tok in vocab:
                vec[vocab[tok]] = float(c)
        norm = sum(x * x for x in vec) ** 0.5 or 1.0
        out.append([x / norm for x in vec])
    return out, vocab


def embed_corpus(texts: list[str], out_meta: Path) -> list[list[float]]:
    try:
        vectors = _fastembed(texts)
        out_meta.write_text(
            json.dumps({"provider": "local", "model": "BAAI/bge-small-en-v1.5"}, indent=2)
        )
        return vectors
    except ImportError:
        vectors, vocab = _tfidf_embed_all(texts)
        out_meta.write_text(
            json.dumps({"provider": "local", "model": "tfidf", "vocab": vocab}, indent=2)
        )
        return vectors


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a batch (used when fastembed is available)."""
    try:
        return _fastembed(texts)
    except ImportError:
        return _tfidf_embed_all(texts)[0]
