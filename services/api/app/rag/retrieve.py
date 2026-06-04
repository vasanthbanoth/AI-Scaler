from openai import OpenAI

from app.config import get_settings
from app.rag.store import ChunkStore


class Retriever:
    def __init__(self, store: ChunkStore):
        self.store = store
        settings = get_settings()
        self.client = OpenAI(api_key=settings.openai_api_key or None)
        self.model = settings.embedding_model

    def embed(self, text: str) -> list[float]:
        resp = self.client.embeddings.create(model=self.model, input=text)
        return resp.data[0].embedding

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
