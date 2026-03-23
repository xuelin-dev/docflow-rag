"""Unit tests for the document chunker module."""

import pytest

from app.ingestion.chunker import (
    Chunk,
    ChunkingStrategy,
    chunk_document,
    split_by_tokens,
)


class TestSplitByTokens:
    """Tests for fixed-size token splitting."""

    def test_empty_text_returns_empty(self) -> None:
        result = split_by_tokens("", chunk_size=100, overlap=20)
        assert result == []

    def test_short_text_single_chunk(self) -> None:
        text = "Hello world, this is a short text."
        result = split_by_tokens(text, chunk_size=100, overlap=20)
        assert len(result) == 1
        assert result[0] == text

    def test_text_splits_with_overlap(self) -> None:
        # Create text long enough to require multiple chunks
        words = [f"word{i}" for i in range(200)]
        text = " ".join(words)
        result = split_by_tokens(text, chunk_size=50, overlap=10)
        assert len(result) > 1
        # Verify all original content is covered
        combined = " ".join(result)
        for word in words:
            assert word in combined

    def test_overlap_must_be_less_than_chunk_size(self) -> None:
        with pytest.raises(ValueError, match="overlap"):
            split_by_tokens("some text", chunk_size=10, overlap=15)


class TestChunkDocument:
    """Tests for the main chunk_document function."""

    def test_returns_list_of_chunks(self) -> None:
        text = "A short document about AI."
        result = chunk_document(
            text,
            strategy=ChunkingStrategy.FIXED,
            chunk_size=512,
            overlap=64,
        )
        assert isinstance(result, list)
        assert all(isinstance(c, Chunk) for c in result)

    def test_chunk_has_content_and_metadata(self) -> None:
        text = "Retrieval-Augmented Generation is a technique for grounded LLM responses."
        result = chunk_document(
            text,
            strategy=ChunkingStrategy.FIXED,
            chunk_size=512,
            overlap=64,
        )
        assert len(result) >= 1
        chunk = result[0]
        assert chunk.content
        assert chunk.index == 0
        assert chunk.token_count > 0

    def test_fixed_strategy_produces_deterministic_output(self) -> None:
        text = "Deterministic chunking should produce the same result every time."
        r1 = chunk_document(text, strategy=ChunkingStrategy.FIXED)
        r2 = chunk_document(text, strategy=ChunkingStrategy.FIXED)
        assert [c.content for c in r1] == [c.content for c in r2]

    def test_invalid_strategy_raises(self) -> None:
        with pytest.raises((ValueError, KeyError)):
            chunk_document("text", strategy="nonexistent")  # type: ignore[arg-type]
