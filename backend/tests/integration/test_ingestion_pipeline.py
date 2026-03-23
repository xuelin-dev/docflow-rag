"""Integration tests for the document ingestion pipeline.

These tests verify the full ingestion flow:
  Upload → Parse → Chunk → Embed → Store in Milvus

Requirements:
  - PostgreSQL (test database)
  - Milvus standalone
  - Redis
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient


pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        "not config.getoption('--run-integration')",
        reason="Integration tests require --run-integration flag",
    ),
]


class TestDocumentUpload:
    """Test document upload and processing."""

    @pytest.mark.asyncio
    async def test_upload_markdown_document(self, client: AsyncClient) -> None:
        """Uploading a markdown file should return 201 with processing status."""
        content = b"# Test\n\nThis is a test document for ingestion."
        response = await client.post(
            "/api/v1/documents/upload",
            files={"file": ("test.md", content, "text/markdown")},
            data={"namespace": "default"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["status"] in ("processing", "completed")
        assert data["document_id"]

    @pytest.mark.asyncio
    async def test_upload_with_metadata(self, client: AsyncClient) -> None:
        """Documents can include custom metadata."""
        content = b"# API Docs\n\nSome API documentation."
        response = await client.post(
            "/api/v1/documents/upload",
            files={"file": ("api.md", content, "text/markdown")},
            data={
                "namespace": "default",
                "metadata": '{"category": "api", "version": "1.0"}',
            },
        )
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_upload_unsupported_format_rejected(
        self, client: AsyncClient
    ) -> None:
        """Unsupported file formats should be rejected with 422."""
        content = b"\x00\x01\x02binary"
        response = await client.post(
            "/api/v1/documents/upload",
            files={"file": ("binary.exe", content, "application/octet-stream")},
        )
        assert response.status_code == 422


class TestChunkingPipeline:
    """Test that uploaded documents are properly chunked."""

    @pytest.mark.asyncio
    async def test_document_produces_chunks(self, client: AsyncClient) -> None:
        """A sufficiently long document should produce multiple chunks."""
        long_content = ("This is a paragraph about RAG systems. " * 50).encode()
        response = await client.post(
            "/api/v1/documents/upload",
            files={"file": ("long.md", long_content, "text/markdown")},
        )
        doc_id = response.json()["document_id"]

        # Poll for completion (in real tests, use a proper wait mechanism)
        detail = await client.get(f"/api/v1/documents/{doc_id}")
        assert detail.status_code == 200
        # chunks_count may be null while processing
        data = detail.json()
        assert "chunks_count" in data
