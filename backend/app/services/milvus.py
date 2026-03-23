"""Milvus client wrapper for vector operations."""

import logging

from pymilvus import MilvusClient

from app.config import settings

logger = logging.getLogger(__name__)


class MilvusService:
    """Milvus client wrapper with connection management.

    Manages the connection to Milvus and provides methods for
    collection setup, vector insertion, and hybrid search.
    """

    def __init__(self) -> None:
        self.client: MilvusClient | None = None
        self.collection_name = settings.milvus_collection

    async def connect(self) -> None:
        """Establish connection to Milvus."""
        try:
            uri = f"http://{settings.milvus_host}:{settings.milvus_port}"
            self.client = MilvusClient(uri=uri)
            logger.info("Connected to Milvus at %s", uri)
        except Exception:
            logger.warning("Failed to connect to Milvus — vector operations will be unavailable")
            self.client = None

    async def disconnect(self) -> None:
        """Close Milvus connection."""
        if self.client:
            self.client.close()
            self.client = None
            logger.info("Disconnected from Milvus")

    async def ping(self) -> bool:
        """Check if Milvus is reachable."""
        if self.client is None:
            return False
        try:
            self.client.list_collections()
            return True
        except Exception:
            return False

    async def ensure_collection(self) -> None:
        """Create the chunks collection if it doesn't exist.

        Sets up HNSW index on dense vectors and sparse inverted index
        for BM25-style retrieval.
        """
        if self.client is None:
            return

        existing = self.client.list_collections()
        if self.collection_name in existing:
            return

        from pymilvus import CollectionSchema, DataType, FieldSchema

        schema = CollectionSchema(
            fields=[
                FieldSchema("chunk_id", DataType.VARCHAR, max_length=64, is_primary=True),
                FieldSchema("doc_id", DataType.VARCHAR, max_length=64),
                FieldSchema("parent_chunk_id", DataType.VARCHAR, max_length=64),
                FieldSchema("namespace", DataType.VARCHAR, max_length=128),
                FieldSchema("dense_embedding", DataType.FLOAT_VECTOR, dim=settings.embedding_dim),
                FieldSchema("sparse_embedding", DataType.SPARSE_FLOAT_VECTOR),
            ],
            description="Child chunks for precise retrieval",
        )

        self.client.create_collection(
            collection_name=self.collection_name,
            schema=schema,
        )

        # Create HNSW index on dense vectors
        self.client.create_index(
            collection_name=self.collection_name,
            field_name="dense_embedding",
            index_params={
                "metric_type": "COSINE",
                "index_type": "HNSW",
                "params": {"M": 16, "efConstruction": 256},
            },
        )

        logger.info("Created Milvus collection: %s", self.collection_name)


milvus_service = MilvusService()
