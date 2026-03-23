"""Unit tests for the semantic cache module."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.services.semantic_cache import SemanticCache, CacheEntry


@pytest.fixture
def mock_redis() -> AsyncMock:
    """Create a mock Redis client."""
    redis = AsyncMock()
    redis.get = AsyncMock(return_value=None)
    redis.set = AsyncMock(return_value=True)
    redis.delete = AsyncMock(return_value=1)
    redis.keys = AsyncMock(return_value=[])
    return redis


@pytest.fixture
def mock_embedder() -> MagicMock:
    """Create a mock embedding function."""
    embedder = MagicMock()
    embedder.embed = AsyncMock(return_value=[0.1] * 1536)
    return embedder


@pytest.fixture
def cache(mock_redis: AsyncMock, mock_embedder: MagicMock) -> SemanticCache:
    """Create a SemanticCache instance with mocked dependencies."""
    return SemanticCache(
        redis_client=mock_redis,
        embedder=mock_embedder,
        similarity_threshold=0.92,
        ttl_seconds=3600,
    )


class TestSemanticCache:
    """Tests for SemanticCache."""

    @pytest.mark.asyncio
    async def test_cache_miss_returns_none(self, cache: SemanticCache) -> None:
        result = await cache.get("What is RAG?")
        assert result is None

    @pytest.mark.asyncio
    async def test_cache_set_stores_entry(
        self, cache: SemanticCache, mock_redis: AsyncMock
    ) -> None:
        entry = CacheEntry(
            query="What is RAG?",
            answer="RAG stands for Retrieval-Augmented Generation.",
            sources=["doc1.md"],
            embedding=[0.1] * 1536,
        )
        await cache.set("What is RAG?", entry)
        mock_redis.set.assert_called_once()

    @pytest.mark.asyncio
    async def test_cache_hit_with_similar_query(
        self, cache: SemanticCache, mock_redis: AsyncMock
    ) -> None:
        # Simulate a stored cache entry
        stored_entry = CacheEntry(
            query="What is RAG?",
            answer="Retrieval-Augmented Generation.",
            sources=["doc1.md"],
            embedding=[0.1] * 1536,
        )
        mock_redis.keys.return_value = [b"cache:abc123"]
        mock_redis.get.return_value = stored_entry.model_dump_json().encode()

        # Patch cosine similarity to return high value
        with patch.object(cache, "_cosine_similarity", return_value=0.98):
            result = await cache.get("What does RAG mean?")
            assert result is not None
            assert result.answer == "Retrieval-Augmented Generation."

    @pytest.mark.asyncio
    async def test_cache_miss_with_dissimilar_query(
        self, cache: SemanticCache, mock_redis: AsyncMock
    ) -> None:
        stored_entry = CacheEntry(
            query="What is RAG?",
            answer="Retrieval-Augmented Generation.",
            sources=["doc1.md"],
            embedding=[0.1] * 1536,
        )
        mock_redis.keys.return_value = [b"cache:abc123"]
        mock_redis.get.return_value = stored_entry.model_dump_json().encode()

        with patch.object(cache, "_cosine_similarity", return_value=0.5):
            result = await cache.get("How to deploy Docker?")
            assert result is None

    def test_cosine_similarity_identical_vectors(self, cache: SemanticCache) -> None:
        vec = [1.0, 0.0, 0.0]
        assert cache._cosine_similarity(vec, vec) == pytest.approx(1.0)

    def test_cosine_similarity_orthogonal_vectors(self, cache: SemanticCache) -> None:
        vec_a = [1.0, 0.0, 0.0]
        vec_b = [0.0, 1.0, 0.0]
        assert cache._cosine_similarity(vec_a, vec_b) == pytest.approx(0.0)

    @pytest.mark.asyncio
    async def test_invalidate_clears_cache(
        self, cache: SemanticCache, mock_redis: AsyncMock
    ) -> None:
        mock_redis.keys.return_value = [b"cache:a", b"cache:b"]
        await cache.invalidate()
        assert mock_redis.delete.called
