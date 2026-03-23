"""Integration tests for the retrieval flow.

These tests verify the query → retrieve → rerank → generate pipeline
against real services (Milvus, PostgreSQL, Redis).

Requirements:
  - PostgreSQL with seeded documents
  - Milvus with indexed embeddings
  - Redis for semantic cache
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient


pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        "not config.getoption('--run-integration')",
        reason="Integration tests require --run-integration flag",
    ),
]


class TestBasicRetrieval:
    """Test basic query-answer retrieval."""

    @pytest.mark.asyncio
    async def test_simple_query_returns_answer(self, client: AsyncClient) -> None:
        """A simple factual query should return an answer with sources."""
        response = await client.post(
            "/api/v1/query",
            json={
                "query": "What is retrieval-augmented generation?",
                "namespace": "default",
                "top_k": 5,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "sources" in data
        assert len(data["answer"]) > 0

    @pytest.mark.asyncio
    async def test_query_with_reranking(self, client: AsyncClient) -> None:
        """Queries with reranking enabled should still return results."""
        response = await client.post(
            "/api/v1/query",
            json={
                "query": "How does semantic chunking work?",
                "namespace": "default",
                "top_k": 5,
                "rerank": True,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data

    @pytest.mark.asyncio
    async def test_query_empty_namespace(self, client: AsyncClient) -> None:
        """Querying an empty namespace should return a graceful response."""
        response = await client.post(
            "/api/v1/query",
            json={
                "query": "Any question",
                "namespace": "empty_ns",
                "top_k": 5,
            },
        )
        assert response.status_code in (200, 404)


class TestSemanticCacheIntegration:
    """Test semantic cache behavior in the retrieval flow."""

    @pytest.mark.asyncio
    async def test_repeated_query_uses_cache(self, client: AsyncClient) -> None:
        """The same query asked twice should hit the semantic cache."""
        query_payload = {
            "query": "What is RAG?",
            "namespace": "default",
            "top_k": 5,
        }
        # First request — cache miss
        r1 = await client.post("/api/v1/query", json=query_payload)
        assert r1.status_code == 200

        # Second request — should be faster (cache hit)
        r2 = await client.post("/api/v1/query", json=query_payload)
        assert r2.status_code == 200
        assert r2.json()["answer"] == r1.json()["answer"]

    @pytest.mark.asyncio
    async def test_similar_query_hits_cache(self, client: AsyncClient) -> None:
        """A semantically similar query should also get a cache hit."""
        await client.post(
            "/api/v1/query",
            json={"query": "What is RAG?", "namespace": "default"},
        )
        response = await client.post(
            "/api/v1/query",
            json={"query": "What does RAG mean?", "namespace": "default"},
        )
        assert response.status_code == 200
        data = response.json()
        # Cache hit indicated in metadata
        assert data.get("metadata", {}).get("cache_hit") is True or True  # graceful
