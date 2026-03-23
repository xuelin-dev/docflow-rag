"""Redis-backed semantic cache for RAG responses."""

from datetime import datetime, timezone

import numpy as np

from app.config import settings
from app.ingestion.embedder import EmbeddingService
from app.services.redis import RedisService


def cosine_similarity(a: list[float] | np.ndarray, b: np.ndarray) -> float:
    """Compute cosine similarity between two vectors."""
    a_arr = np.array(a, dtype=np.float32)
    norm_a = np.linalg.norm(a_arr)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a_arr, b) / (norm_a * norm_b))


class SemanticCache:
    """Redis-backed semantic cache for RAG responses.

    Caches LLM responses keyed by query embedding similarity.
    Avoids redundant LLM API calls for semantically similar queries.
    """

    def __init__(self, redis: RedisService, embedder: EmbeddingService) -> None:
        self.redis = redis
        self.embedder = embedder
        self.similarity_threshold = settings.cache_similarity_threshold
        self.default_ttl = settings.cache_ttl

    async def get(self, query: str, namespace: str) -> dict | None:
        """Check cache for a semantically similar query.

        Embeds the incoming query and scans cached entries in the namespace
        for cosine similarity above threshold.
        """
        client = self.redis.client
        if client is None:
            return None

        query_embedding = self.embedder.embed_query(query)["dense"]

        pattern = f"rag_cache:{namespace}:*"
        async for key in client.scan_iter(pattern, count=100):
            cached = await client.hgetall(key)
            if not cached:
                continue

            emb_key = b"embedding" if b"embedding" in cached else "embedding"
            if emb_key not in cached:
                continue

            cached_embedding = np.frombuffer(cached[emb_key], dtype=np.float32)
            similarity = cosine_similarity(query_embedding, cached_embedding)

            if similarity >= self.similarity_threshold:
                import json
                result_key = b"result" if b"result" in cached else "result"
                return json.loads(cached[result_key])

        return None

    async def put(
        self,
        query: str,
        namespace: str,
        result: dict,
        ttl: int | None = None,
    ) -> None:
        """Cache a RAG result with its query embedding."""
        client = self.redis.client
        if client is None:
            return

        import json

        query_embedding = self.embedder.embed_query(query)["dense"]
        key = f"rag_cache:{namespace}:{hash(query)}"

        await client.hset(key, mapping={
            "embedding": np.array(query_embedding, dtype=np.float32).tobytes(),
            "result": json.dumps(result),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        await client.expire(key, ttl or self.default_ttl)

    async def invalidate_namespace(self, namespace: str) -> int:
        """Invalidate all cache entries for a namespace."""
        client = self.redis.client
        if client is None:
            return 0

        count = 0
        pattern = f"rag_cache:{namespace}:*"
        async for key in client.scan_iter(pattern, count=100):
            await client.delete(key)
            count += 1
        return count
