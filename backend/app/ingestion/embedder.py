"""Embedding generation using BGE-M3."""

from app.config import settings


class EmbeddingService:
    """Generate dense and sparse embeddings using BGE-M3.

    BGE-M3 produces:
    - Dense: 1024-dimensional vectors for semantic similarity
    - Sparse: Lexical weight vectors for BM25-style matching
    """

    def __init__(
        self,
        model_name: str = settings.embedding_model,
        device: str = settings.embedding_device,
    ) -> None:
        self.model_name = model_name
        self.device = device
        self._model = None

    @property
    def model(self):
        """Lazy-load the embedding model."""
        if self._model is None:
            from FlagEmbedding import BGEM3FlagModel
            self._model = BGEM3FlagModel(self.model_name, use_fp16=(self.device != "cpu"))
        return self._model

    def embed(self, texts: list[str]) -> dict:
        """Generate both dense and sparse embeddings.

        Args:
            texts: List of text strings to embed.

        Returns:
            {
                "dense": list[list[float]],       # shape: (N, 1024)
                "sparse": list[dict[int, float]]   # token_id -> weight
            }
        """
        output = self.model.encode(
            texts,
            return_dense=True,
            return_sparse=True,
            return_colbert_vecs=False,
        )
        return {
            "dense": output["dense_vecs"].tolist(),
            "sparse": output["lexical_weights"],
        }

    def embed_query(self, query: str) -> dict:
        """Embed a single query string.

        Convenience method that returns embeddings for a single text.
        """
        result = self.embed([query])
        return {
            "dense": result["dense"][0],
            "sparse": result["sparse"][0],
        }
