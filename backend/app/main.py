"""FastAPI application factory with lifespan management."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import v1_router
from app.config import settings
from app.services.milvus import milvus_service
from app.services.redis import redis_service


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Manage application startup and shutdown."""
    # Startup
    await redis_service.connect()
    await milvus_service.connect()
    yield
    # Shutdown
    await redis_service.disconnect()
    await milvus_service.disconnect()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Production-grade Agentic RAG engine that turns private documents into a conversational, traceable knowledge base.",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # CORS
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers
    application.include_router(v1_router, prefix=settings.api_prefix)

    @application.get("/health")
    async def health_check():
        """Basic health check."""
        return {"status": "healthy", "version": settings.app_version}

    @application.get("/health/ready")
    async def readiness_check():
        """Check all dependencies are available."""
        checks = {
            "redis": await redis_service.ping(),
            "milvus": await milvus_service.ping(),
        }
        all_ready = all(checks.values())
        return {"status": "ready" if all_ready else "degraded", "checks": checks}

    return application


app = create_app()
