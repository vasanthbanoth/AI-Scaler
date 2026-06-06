from app.rag.embeddings import embed_query
from app.rag.store import ChunkStore


class Retriever:
    def __init__(self, store: ChunkStore):
        self.store = store

    def embed(self, text: str) -> list[float]:
        return embed_query(text)

    def query(self, question: str, k: int = 6) -> list[dict]:
        vec = self.embed(question)
        hits = self.store.search(vec, k=k)
        return [
            {
                "text": c.text,
                "source": c.source,
                "score": round(score, 4),
                "meta": c.meta,
            }
            for c, score in hits
        ]
