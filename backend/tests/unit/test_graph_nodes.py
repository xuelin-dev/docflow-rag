"""Unit tests for LangGraph node functions."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.graph.nodes import (
    classify_query,
    retrieve_documents,
    rerank_results,
    generate_answer,
    QueryClassification,
)
from src.graph.state import GraphState


@pytest.fixture
def base_state() -> GraphState:
    """Create a base graph state for testing."""
    return GraphState(
        query="What is semantic chunking?",
        namespace="default",
        classification=None,
        retrieved_chunks=[],
        reranked_chunks=[],
        answer="",
        sources=[],
        metadata={},
    )


class TestClassifyQuery:
    """Tests for the query classification node."""

    @pytest.mark.asyncio
    async def test_classifies_factual_query(self, base_state: GraphState) -> None:
        base_state.query = "What is the capital of France?"
        with patch("src.graph.nodes._call_llm") as mock_llm:
            mock_llm.return_value = '{"type": "factual", "complexity": "simple"}'
            result = await classify_query(base_state)
            assert result.classification is not None
            assert result.classification.type == "factual"

    @pytest.mark.asyncio
    async def test_classifies_analytical_query(self, base_state: GraphState) -> None:
        base_state.query = "Compare semantic chunking vs fixed-size chunking"
        with patch("src.graph.nodes._call_llm") as mock_llm:
            mock_llm.return_value = '{"type": "analytical", "complexity": "complex"}'
            result = await classify_query(base_state)
            assert result.classification.type == "analytical"

    @pytest.mark.asyncio
    async def test_classification_fallback_on_error(
        self, base_state: GraphState
    ) -> None:
        with patch("src.graph.nodes._call_llm", side_effect=Exception("LLM error")):
            result = await classify_query(base_state)
            # Should fall back to default classification
            assert result.classification is not None
            assert result.classification.type == "general"


class TestRetrieveDocuments:
    """Tests for the document retrieval node."""

    @pytest.mark.asyncio
    async def test_retrieves_chunks(self, base_state: GraphState) -> None:
        mock_chunks = [
            {"content": "Chunk 1 about chunking", "score": 0.95},
            {"content": "Chunk 2 about splitting", "score": 0.87},
        ]
        with patch("src.graph.nodes._vector_search", return_value=mock_chunks):
            result = await retrieve_documents(base_state)
            assert len(result.retrieved_chunks) == 2

    @pytest.mark.asyncio
    async def test_empty_retrieval(self, base_state: GraphState) -> None:
        with patch("src.graph.nodes._vector_search", return_value=[]):
            result = await retrieve_documents(base_state)
            assert result.retrieved_chunks == []


class TestRerankResults:
    """Tests for the reranking node."""

    @pytest.mark.asyncio
    async def test_reranks_chunks(self, base_state: GraphState) -> None:
        base_state.retrieved_chunks = [
            {"content": "Less relevant chunk", "score": 0.7},
            {"content": "More relevant chunk about semantic chunking", "score": 0.6},
        ]
        with patch("src.graph.nodes._cross_encoder_rerank") as mock_rerank:
            mock_rerank.return_value = [
                {"content": "More relevant chunk about semantic chunking", "score": 0.95},
                {"content": "Less relevant chunk", "score": 0.3},
            ]
            result = await rerank_results(base_state)
            assert len(result.reranked_chunks) == 2
            assert result.reranked_chunks[0]["score"] > result.reranked_chunks[1]["score"]

    @pytest.mark.asyncio
    async def test_rerank_passthrough_when_disabled(
        self, base_state: GraphState
    ) -> None:
        base_state.retrieved_chunks = [{"content": "A chunk", "score": 0.8}]
        base_state.metadata["rerank_enabled"] = False
        result = await rerank_results(base_state)
        assert result.reranked_chunks == base_state.retrieved_chunks


class TestGenerateAnswer:
    """Tests for the answer generation node."""

    @pytest.mark.asyncio
    async def test_generates_answer(self, base_state: GraphState) -> None:
        base_state.reranked_chunks = [
            {"content": "Semantic chunking splits text at meaning boundaries.", "score": 0.95},
        ]
        with patch("src.graph.nodes._call_llm") as mock_llm:
            mock_llm.return_value = "Semantic chunking splits text at natural meaning boundaries."
            result = await generate_answer(base_state)
            assert result.answer
            assert "semantic" in result.answer.lower()

    @pytest.mark.asyncio
    async def test_no_answer_without_context(self, base_state: GraphState) -> None:
        base_state.reranked_chunks = []
        with patch("src.graph.nodes._call_llm") as mock_llm:
            mock_llm.return_value = "I don't have enough context to answer this question."
            result = await generate_answer(base_state)
            assert "don't have enough" in result.answer.lower() or result.answer != ""
