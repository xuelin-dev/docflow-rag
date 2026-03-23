"""Shared pytest fixtures for DocFlow RAG backend tests."""

import asyncio
from collections.abc import AsyncGenerator, Generator
from typing import Any

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.config import settings
from app.db.session import Base, get_db_session
from app.main import app

# Use an in-memory SQLite for unit tests (fast, no external deps).
# Integration tests should use a real PostgreSQL via TEST_DATABASE_URL.
TEST_DATABASE_URL = getattr(settings, "TEST_DATABASE_URL", None) or "sqlite+aiosqlite:///"


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create a single event loop for the entire test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def engine():
    """Create a test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=StaticPool if "sqlite" in TEST_DATABASE_URL else None,
        echo=False,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(engine) -> AsyncGenerator[AsyncSession, None]:
    """Provide a transactional database session that rolls back after each test."""
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as session:
        async with session.begin():
            yield session
            await session.rollback()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Provide an async HTTP test client with dependency overrides."""

    async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db_session] = _override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def sample_document() -> dict[str, Any]:
    """Return a sample document dict for testing."""
    return {
        "title": "Test Document",
        "content": "This is a test document about retrieval-augmented generation. "
        "RAG combines retrieval with generation for better accuracy.",
        "source": "test/sample.md",
        "doc_type": "markdown",
        "namespace": "default",
    }


@pytest.fixture
def sample_chunks() -> list[dict[str, Any]]:
    """Return sample chunk dicts for testing."""
    return [
        {
            "content": "Retrieval-Augmented Generation combines retrieval with generation.",
            "metadata": {"source": "test/sample.md", "chunk_index": 0},
            "token_count": 8,
        },
        {
            "content": "RAG pipelines typically use vector databases for similarity search.",
            "metadata": {"source": "test/sample.md", "chunk_index": 1},
            "token_count": 10,
        },
        {
            "content": "Semantic chunking preserves meaning boundaries in text splitting.",
            "metadata": {"source": "test/sample.md", "chunk_index": 2},
            "token_count": 9,
        },
    ]
