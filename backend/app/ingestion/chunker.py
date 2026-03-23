"""Hierarchical chunking strategy for document elements."""

import uuid
from dataclasses import dataclass, field

from app.config import settings
from app.ingestion.parser import ParsedDocument


@dataclass
class Chunk:
    """A document chunk with hierarchy information."""
    chunk_id: str
    doc_id: str
    text: str
    parent_chunk_id: str | None  # None if this IS a parent chunk
    level: str  # "child" or "parent"
    chunk_index: int
    token_count: int
    metadata: dict = field(default_factory=dict)
    embedding: list[float] | None = None


class HierarchicalChunker:
    """Two-level hierarchical chunking strategy.

    Small chunks (child, ~256 tokens) for precise retrieval.
    Large chunks (parent, ~1024 tokens) for rich generation context.
    Retrieval returns child chunks → system looks up parent chunks → passes parents to LLM.
    """

    def __init__(
        self,
        child_chunk_size: int = settings.child_chunk_size,
        child_overlap: int = settings.child_chunk_overlap,
        parent_chunk_size: int = settings.parent_chunk_size,
        parent_overlap: int = settings.parent_chunk_overlap,
    ) -> None:
        self.child_chunk_size = child_chunk_size
        self.child_overlap = child_overlap
        self.parent_chunk_size = parent_chunk_size
        self.parent_overlap = parent_overlap

    def chunk(self, document: ParsedDocument) -> list[Chunk]:
        """Split a parsed document into hierarchical chunks.

        Returns both parent and child chunks. Child chunks reference
        their parent via parent_chunk_id.
        """
        full_text = "\n\n".join(el.text for el in document.elements)
        words = full_text.split()

        if not words:
            return []

        # Create parent chunks first
        parent_chunks = self._create_chunks(
            words=words,
            doc_id=document.doc_id,
            chunk_size=self.parent_chunk_size,
            overlap=self.parent_overlap,
            level="parent",
        )

        # Create child chunks within each parent
        all_chunks: list[Chunk] = []
        for parent in parent_chunks:
            all_chunks.append(parent)
            parent_words = parent.text.split()
            children = self._create_chunks(
                words=parent_words,
                doc_id=document.doc_id,
                chunk_size=self.child_chunk_size,
                overlap=self.child_overlap,
                level="child",
                parent_chunk_id=parent.chunk_id,
            )
            all_chunks.extend(children)

        return all_chunks

    def _create_chunks(
        self,
        words: list[str],
        doc_id: str,
        chunk_size: int,
        overlap: int,
        level: str,
        parent_chunk_id: str | None = None,
    ) -> list[Chunk]:
        """Create fixed-size word-level chunks with overlap."""
        chunks: list[Chunk] = []
        step = max(chunk_size - overlap, 1)
        idx = 0

        for start in range(0, len(words), step):
            chunk_words = words[start : start + chunk_size]
            text = " ".join(chunk_words)
            chunks.append(Chunk(
                chunk_id=str(uuid.uuid4()),
                doc_id=doc_id,
                text=text,
                parent_chunk_id=parent_chunk_id,
                level=level,
                chunk_index=idx,
                token_count=len(chunk_words),
                metadata={"start_word": start},
            ))
            idx += 1

            if start + chunk_size >= len(words):
                break

        return chunks
