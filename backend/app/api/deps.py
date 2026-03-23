"""Dependency injection for API endpoints."""

from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, HTTPException, Security
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.session import async_session_factory
from app.services.milvus import MilvusService, milvus_service
from app.services.redis import RedisService, redis_service

api_key_header = APIKeyHeader(name=settings.api_key_header, auto_error=False)


async def get_db() -> AsyncIterator[AsyncSession]:
    """Yield an async database session."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_redis() -> RedisService:
    """Get Redis service instance."""
    return redis_service


async def get_milvus() -> MilvusService:
    """Get Milvus service instance."""
    return milvus_service


async def verify_api_key(api_key: str | None = Security(api_key_header)) -> str:
    """Validate API key and return user identifier."""
    if api_key is None:
        raise HTTPException(status_code=401, detail="Missing API key")
    # TODO: Validate against database in production
    if settings.debug:
        return "dev-user"
    raise HTTPException(status_code=401, detail="Invalid API key")


# Type aliases for dependency injection
DbSession = Annotated[AsyncSession, Depends(get_db)]
Redis = Annotated[RedisService, Depends(get_redis)]
Milvus = Annotated[MilvusService, Depends(get_milvus)]
CurrentUser = Annotated[str, Depends(verify_api_key)]
