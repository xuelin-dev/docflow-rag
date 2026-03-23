"""Redis client wrapper for cache and queue operations."""

import logging

import redis.asyncio as aioredis

from app.config import settings

logger = logging.getLogger(__name__)


class RedisService:
    """Redis client wrapper with connection management.

    Used for semantic cache, rate limiting, session state,
    and Redis Streams-based ingestion queue.
    """

    def __init__(self) -> None:
        self.client: aioredis.Redis | None = None

    async def connect(self) -> None:
        """Establish connection to Redis."""
        try:
            self.client = aioredis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=False,  # Keep bytes for embedding storage
            )
            await self.client.ping()
            logger.info("Connected to Redis at %s:%s", settings.redis_host, settings.redis_port)
        except Exception:
            logger.warning("Failed to connect to Redis — cache and queue will be unavailable")
            self.client = None

    async def disconnect(self) -> None:
        """Close Redis connection."""
        if self.client:
            await self.client.close()
            self.client = None
            logger.info("Disconnected from Redis")

    async def ping(self) -> bool:
        """Check if Redis is reachable."""
        if self.client is None:
            return False
        try:
            return await self.client.ping()
        except Exception:
            return False

    async def enqueue_ingestion(
        self,
        doc_id: str,
        namespace: str,
        file_path: str,
        doc_type: str,
    ) -> str:
        """Add a document to the ingestion queue via Redis Streams.

        Returns:
            Stream message ID.
        """
        if self.client is None:
            raise ConnectionError("Redis is not connected")

        msg_id = await self.client.xadd(
            "ingestion_queue",
            {
                "doc_id": doc_id,
                "namespace": namespace,
                "file_path": file_path,
                "doc_type": doc_type,
            },
        )
        return msg_id


redis_service = RedisService()
