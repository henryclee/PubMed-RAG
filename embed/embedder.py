from sentence_transformers import SentenceTransformer


class Embedder:
    def __init__(self):
        self.model = SentenceTransformer(
            "/Volumes/Data/embedding_models/bge-large-en-v1.5"
        )

    def embed(self, text: str) -> list[float]:
        return self.model.encode(text, normalize_embeddings=True).tolist()  # type: ignore

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return self.model.encode(  # type: ignore
            texts, normalize_embeddings=True, batch_size=32
        ).tolist()


embedder = Embedder()
