"""Seed the database with sample data for development.

Usage:
    python -m scripts.seed_data
"""

import asyncio
import logging
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.config import settings
from src.models.document import Document, Namespace

logger = logging.getLogger(__name__)

SAMPLE_DOCUMENTS = [
    {
        "title": "Getting Started with RAG",
        "content": """# Getting Started with RAG

Retrieval-Augmented Generation (RAG) combines the power of large language models
with external knowledge retrieval to produce more accurate and up-to-date responses.

## Key Concepts

- **Retrieval**: Finding relevant documents from a knowledge base
- **Augmentation**: Injecting retrieved context into the LLM prompt
- **Generation**: Producing a response grounded in the retrieved information

## Architecture Overview

A typical RAG pipeline consists of:

1. **Document Ingestion** — Parse, chunk, and embed documents
2. **Vector Store** — Store embeddings for similarity search
3. **Query Pipeline** — Retrieve relevant chunks and generate answers

## Best Practices

- Use semantic chunking over fixed-size splitting
- Implement hybrid search (dense + sparse retrieval)
- Add a reranking step for improved precision
- Cache frequent queries to reduce latency
""",
        "source": "docs/getting-started.md",
        "doc_type": "markdown",
    },
    {
        "title": "DocFlow API Reference",
        "content": """# DocFlow API Reference

## Endpoints

### POST /api/v1/documents/upload
Upload a document for ingestion into the knowledge base.

**Request Body:** `multipart/form-data`
- `file` (required): The document file (PDF, MD, TXT, DOCX)
- `namespace` (optional): Target namespace (default: "default")
- `metadata` (optional): JSON metadata object

**Response:** `201 Created`
```json
{
  "document_id": "uuid",
  "status": "processing",
  "chunks_count": null
}
```

### POST /api/v1/query
Query the knowledge base with natural language.

**Request Body:**
```json
{
  "query": "How does semantic chunking work?",
  "namespace": "default",
  "top_k": 5,
  "rerank": true
}
```

### GET /api/v1/documents
List all documents in a namespace.

### DELETE /api/v1/documents/{document_id}
Remove a document and its associated chunks/embeddings.
""",
        "source": "docs/api-reference.md",
        "doc_type": "markdown",
    },
    {
        "title": "Deployment Guide",
        "content": """# Deployment Guide

## Prerequisites

- Docker & Docker Compose v2+
- At least 8 GB RAM (Milvus requires ~4 GB)
- OpenAI API key or compatible embedding provider

## Quick Start

```bash
# Clone the repository
git clone https://github.com/your-org/docflow-rag.git
cd docflow-rag

# Copy environment variables
cp .env.example .env
# Edit .env with your API keys

# Start all services
make dev

# Run database migrations
make migrate

# Seed sample data
make seed
```

## Production Deployment

```bash
# Build production images
make build

# Start with production overrides
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Monitoring

- FastAPI health: http://localhost:8000/health
- Milvus health: http://localhost:9091/healthz
- MinIO console: http://localhost:9001
""",
        "source": "docs/deployment.md",
        "doc_type": "markdown",
    },
]


async def seed_data() -> None:
    """Create default namespace and seed sample documents."""
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        async with session.begin():
            # Create default namespace
            namespace = Namespace(
                name="default",
                description="Default document namespace",
                created_at=datetime.now(timezone.utc),
            )
            session.add(namespace)
            await session.flush()

            logger.info("Created default namespace (id=%s)", namespace.id)

            # Add sample documents
            for doc_data in SAMPLE_DOCUMENTS:
                doc = Document(
                    namespace_id=namespace.id,
                    title=doc_data["title"],
                    content=doc_data["content"],
                    source=doc_data["source"],
                    doc_type=doc_data["doc_type"],
                    status="pending",
                    created_at=datetime.now(timezone.utc),
                )
                session.add(doc)
                logger.info("Added document: %s", doc_data["title"])

        await session.commit()
        logger.info("Seed data committed successfully.")

    await engine.dispose()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    asyncio.run(seed_data())
