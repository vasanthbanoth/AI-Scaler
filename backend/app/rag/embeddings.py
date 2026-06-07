"""Query-time embeddings — matches scripts/embed_local.py / ingest provider."""

from __future__ import annotations

import json
import os
import re
from collections import Counter
from pathlib import Path

from openai import OpenAI

from app.config import ROOT, get_settings

_META_PATH = ROOT / "data" / "embedding_meta.json"


def _load_meta() -> dict:
    if _META_PATH.exists():
        return json.loads(_META_PATH.read_text())
    provider = os.getenv("EMBEDDING_PROVIDER", "auto")
    if provider == "local":
        return {"provider": "local", "model": "bge-small-en-v1.5"}
    return {"provider": "openai", "model": get_settings().embedding_model}


def _fastembed(texts: list[str]) -> list[list[float]]:
    from fastembed import TextEmbedding

    model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
    return [vec.tolist() for vec in model.embed(texts)]


def _tfidf_embed(texts: list[str], vocab: dict[str, int] | None = None) -> tuple[list[list[float]], dict[str, int]]:
    if vocab is None:
        vocab = {}
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


def embed_query(text: str) -> list[float]:
    meta = _load_meta()
    if meta.get("provider") == "local":
        try:
            return _fastembed([text])[0]
        except ImportError:
            vocab = meta.get("vocab")
            if vocab:
                return _tfidf_embed([text], vocab)[0][0]
            return _tfidf_embed([text])[0][0]

    settings = get_settings()
    client = OpenAI(api_key=settings.openai_api_key or None)
    resp = client.embeddings.create(model=meta.get("model", settings.embedding_model), input=text)
    return resp.data[0].embedding
