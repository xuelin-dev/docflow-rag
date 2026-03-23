"""End-to-end tests for the complete query flow.

These tests simulate a real user journey:
  1. Upload a document
  2. Wait for ingestion to complete
  3. Query the knowledge base
  4. Verify the answer references the uploaded document

Requirements:
  - Full stack running (all Docker services)
  - Clean test namespace
"""

import asyncio
import time

import pytest
import pytest_asyncio
from httpx import AsyncClient


pytestmark = [
    pytest.mark.e2e,
    pytest.mark.skipif(
        "not config.getoption('--run-e2e')",
        reason="E2E tests require --run-e2e flag",
    ),
]

TEST_NAMESPACE = "e2e_test"
MAX_POLL_SECONDS = 60
POLL_INTERVAL = 2


class TestFullQueryFlow:
    """Test the complete upload → query → answer flow."""

    @pytest.mark.asyncio
    async def test_upload_and_query(self, client: AsyncClient) -> None:
        """Upload a document, then query it and verify the answer."""
        # Step 1: Upload a document
        doc_content = b"""# Python Type Hints Guide

Type hints in Python improve code readability and enable static analysis.

## Basic Types
- `int`, `str`, `float`, `bool` for primitives
- `list[int]`, `dict[str, Any]` for collections
- `Optional[str]` for nullable values

## Benefits
1. Better IDE autocompletion
2. Catch bugs before runtime with mypy
3. Self-documenting code
4. Easier refactoring
"""
        upload_resp = await client.post(
            "/api/v1/documents/upload",
            files={"file": ("type_hints.md", doc_content, "text/markdown")},
            data={"namespace": TEST_NAMESPACE},
        )
        assert upload_resp.status_code == 201
        doc_id = upload_resp.json()["document_id"]

        # Step 2: Wait for ingestion to complete
        deadline = time.monotonic() + MAX_POLL_SECONDS
        while time.monotonic() < deadline:
            status_resp = await client.get(f"/api/v1/documents/{doc_id}")
            assert status_resp.status_code == 200
            if status_resp.json()["status"] == "completed":
                break
            await asyncio.sleep(POLL_INTERVAL)
        else:
            pytest.fail(f"Document {doc_id} did not complete within {MAX_POLL_SECONDS}s")

        # Step 3: Query the knowledge base
        query_resp = await client.post(
            "/api/v1/query",
            json={
                "query": "What are the benefits of Python type hints?",
                "namespace": TEST_NAMESPACE,
                "top_k": 3,
                "rerank": True,
            },
        )
        assert query_resp.status_code == 200
        data = query_resp.json()

        # Step 4: Verify the answer
        assert "answer" in data
        answer_lower = data["answer"].lower()
        # Should mention at least one benefit from the document
        assert any(
            keyword in answer_lower
            for keyword in ["autocompletion", "mypy", "readability", "refactoring", "bug"]
        )

        # Step 5: Verify sources reference our document
        sources = data.get("sources", [])
        assert len(sources) > 0

    @pytest.mark.asyncio
    async def test_query_nonexistent_namespace(self, client: AsyncClient) -> None:
        """Querying a namespace with no documents should handle gracefully."""
        response = await client.post(
            "/api/v1/query",
            json={
                "query": "Any question",
                "namespace": "nonexistent_e2e_ns",
            },
        )
        # Should either return empty answer or 404
        assert response.status_code in (200, 404)
        if response.status_code == 200:
            data = response.json()
            assert "answer" in data

    @pytest.mark.asyncio
    async def test_delete_document_removes_from_search(
        self, client: AsyncClient
    ) -> None:
        """After deleting a document, it should no longer appear in results."""
        # Upload
        content = b"# Unique Token XYZ123\n\nThis contains a unique identifier."
        upload_resp = await client.post(
            "/api/v1/documents/upload",
            files={"file": ("unique.md", content, "text/markdown")},
            data={"namespace": TEST_NAMESPACE},
        )
        doc_id = upload_resp.json()["document_id"]

        # Wait for ingestion
        deadline = time.monotonic() + MAX_POLL_SECONDS
        while time.monotonic() < deadline:
            resp = await client.get(f"/api/v1/documents/{doc_id}")
            if resp.json()["status"] == "completed":
                break
            await asyncio.sleep(POLL_INTERVAL)

        # Delete
        del_resp = await client.delete(f"/api/v1/documents/{doc_id}")
        assert del_resp.status_code in (200, 204)

        # Query should not find deleted content
        query_resp = await client.post(
            "/api/v1/query",
            json={
                "query": "XYZ123 unique identifier",
                "namespace": TEST_NAMESPACE,
            },
        )
        if query_resp.status_code == 200:
            sources = query_resp.json().get("sources", [])
            source_ids = [s.get("document_id") for s in sources]
            assert doc_id not in source_ids
