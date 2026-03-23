"""Redis Streams consumer for async document ingestion."""

import asyncio
import logging

from app.config import settings
from app.ingestion.chunker import HierarchicalChunker
from app.ingestion.embedder import EmbeddingService
from app.ingestion.indexer import MilvusIndexer
from app.ingestion.parser import DocumentParser
from app.services.redis import redis_service

logger = logging.getLogger(__name__)

STREAM_NAME = "ingestion_queue"
GROUP_NAME = "ingestion_workers"
CONSUMER_NAME = "worker-1"


class IngestionWorker:
    """Background worker that consumes document ingestion tasks from Redis Streams.

    Pipeline: Parse → Chunk → Embed → Index
    """

    def __init__(self) -> None:
        self.parser = DocumentParser()
        self.chunker = HierarchicalChunker()
        self.embedder = EmbeddingService()
        self.indexer = MilvusIndexer()

    async def start(self) -> None:
        """Start consuming from the ingestion queue.

        Creates the consumer group if it doesn't exist, then loops
        reading messages and processing them.
        """
        client = redis_service.client
        if client is None:
            logger.error("Redis not connected, cannot start worker")
            return

        # Create consumer group (ignore if exists)
        try:
            await client.xgroup_create(STREAM_NAME, GROUP_NAME, id="0", mkstream=True)
        except Exception:
            pass  # Group already exists

        logger.info("Ingestion worker started, listening on %s", STREAM_NAME)

        while True:
            try:
                messages = await client.xreadgroup(
                    GROUP_NAME, CONSUMER_NAME,
                    {STREAM_NAME: ">"},
                    count=1, block=5000,
                )

                for stream, entries in messages:
                    for msg_id, data in entries:
                        await self._process_message(data)
                        await client.xack(STREAM_NAME, GROUP_NAME, msg_id)

            except asyncio.CancelledError:
                logger.info("Ingestion worker shutting down")
                break
            except Exception:
                logger.exception("Error processing ingestion message")
                await asyncio.sleep(1)

    async def _process_message(self, data: dict) -> None:
        """Process a single ingestion message.

        Expected data: {doc_id, namespace, file_path, doc_type}
        """
        from pathlib import Path

        doc_id = data.get(b"doc_id", data.get("doc_id", "")).decode() if isinstance(data.get(b"doc_id"), bytes) else data.get("doc_id", "")
        file_path = data.get(b"file_path", data.get("file_path", "")).decode() if isinstance(data.get(b"file_path"), bytes) else data.get("file_path", "")
        namespace = data.get(b"namespace", data.get("namespace", "default")).decode() if isinstance(data.get(b"namespace"), bytes) else data.get("namespace", "default")

        logger.info("Processing document %s from %s", doc_id, file_path)

        # Parse
        parsed = await self.parser.parse(Path(file_path), doc_id)

        # Chunk
        chunks = self.chunker.chunk(parsed)

        # Embed child chunks
        child_chunks = [c for c in chunks if c.level == "child"]
        if child_chunks:
            texts = [c.text for c in child_chunks]
            embeddings = self.embedder.embed(texts)
            for chunk, emb in zip(child_chunks, embeddings["dense"]):
                chunk.embedding = emb

        # Index
        indexed = await self.indexer.index_chunks(chunks, namespace)
        logger.info("Indexed %d chunks for document %s", indexed, doc_id)
