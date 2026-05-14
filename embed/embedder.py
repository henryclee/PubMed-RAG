import time

from sentence_transformers import SentenceTransformer

from core.settings import settings


class Embedder:
    def __init__(self):
        start = time.time()
        self.model = SentenceTransformer(settings.embedding_model_uri)
        print(
            f"Loaded embedding model from {settings.embedding_model_uri} in {time.time() - start:.2f} seconds."
        )

    def embed(self, text: str) -> list[float]:
        return self.model.encode(text, normalize_embeddings=True).tolist()  # type: ignore

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return self.model.encode(  # type: ignore
            texts, normalize_embeddings=True, batch_size=settings.batch_size
        ).tolist()


embedder = Embedder()
