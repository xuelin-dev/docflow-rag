"""Milvus indexing operations for document chunks."""

from app.config import settings
from app.ingestion.chunker import Chunk
from app.services.milvus import milvus_service


class MilvusIndexer:
    """Write chunk embeddings to Milvus for vector search.

    Manages the docflow_child_chunks collection with HNSW index
    for dense vectors and sparse inverted index for BM25.
    """

    def __init__(self, collection_name: str = settings.milvus_collection) -> None:
        self.collection_name = collection_name

    async def index_chunks(self, chunks: list[Chunk], namespace: str) -> int:
        """Index a batch of child chunks into Milvus.

        Args:
            chunks: List of chunks with embeddings populated.
            namespace: Document namespace for partition filtering.

        Returns:
            Number of chunks successfully indexed.
        """
        child_chunks = [c for c in chunks if c.level == "child" and c.embedding is not None]

        if not child_chunks:
            return 0

        entities = [
            {
                "chunk_id": chunk.chunk_id,
                "doc_id": chunk.doc_id,
                "parent_chunk_id": chunk.parent_chunk_id or "",
                "namespace": namespace,
                "dense_embedding": chunk.embedding,
            }
            for chunk in child_chunks
        ]

        client = milvus_service.client
        if client is None:
            raise ConnectionError("Milvus is not connected")

        # TODO: Insert via pymilvus when collection is created
        return len(entities)

    async def delete_by_doc_id(self, doc_id: str) -> int:
        """Delete all chunks for a document from Milvus.

        Args:
            doc_id: Document ID whose chunks should be removed.

        Returns:
            Number of chunks deleted.
        """
        client = milvus_service.client
        if client is None:
            raise ConnectionError("Milvus is not connected")

        # TODO: Delete via pymilvus expression filter
        return 0
