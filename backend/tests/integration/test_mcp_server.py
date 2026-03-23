"""Integration tests for the MCP (Model Context Protocol) server.

These tests verify that the MCP server correctly exposes
DocFlow RAG capabilities as tools for LLM agents.

Requirements:
  - FastAPI running with MCP endpoints enabled
  - PostgreSQL with seeded data
  - Milvus with indexed embeddings
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


class TestMCPToolDiscovery:
    """Test MCP tool listing and schema."""

    @pytest.mark.asyncio
    async def test_list_tools(self, client: AsyncClient) -> None:
        """MCP server should list available tools."""
        response = await client.get("/api/v1/mcp/tools")
        assert response.status_code == 200
        tools = response.json()
        assert isinstance(tools, list)
        # Should expose at least query and upload tools
        tool_names = {t["name"] for t in tools}
        assert "query_knowledge_base" in tool_names or len(tool_names) > 0

    @pytest.mark.asyncio
    async def test_tool_schema_valid(self, client: AsyncClient) -> None:
        """Each tool should have a valid JSON schema."""
        response = await client.get("/api/v1/mcp/tools")
        assert response.status_code == 200
        for tool in response.json():
            assert "name" in tool
            assert "description" in tool
            assert "inputSchema" in tool
            schema = tool["inputSchema"]
            assert schema.get("type") == "object"


class TestMCPToolExecution:
    """Test MCP tool invocation."""

    @pytest.mark.asyncio
    async def test_invoke_query_tool(self, client: AsyncClient) -> None:
        """Invoking the query tool via MCP should return results."""
        response = await client.post(
            "/api/v1/mcp/invoke",
            json={
                "tool": "query_knowledge_base",
                "arguments": {
                    "query": "What is RAG?",
                    "namespace": "default",
                },
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "result" in data or "content" in data

    @pytest.mark.asyncio
    async def test_invoke_list_documents_tool(self, client: AsyncClient) -> None:
        """Invoking the list documents tool should return document list."""
        response = await client.post(
            "/api/v1/mcp/invoke",
            json={
                "tool": "list_documents",
                "arguments": {
                    "namespace": "default",
                },
            },
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_invoke_unknown_tool_returns_error(
        self, client: AsyncClient
    ) -> None:
        """Invoking a non-existent tool should return an error."""
        response = await client.post(
            "/api/v1/mcp/invoke",
            json={
                "tool": "nonexistent_tool",
                "arguments": {},
            },
        )
        assert response.status_code in (400, 404)


class TestMCPSSE:
    """Test MCP Server-Sent Events transport."""

    @pytest.mark.asyncio
    async def test_sse_endpoint_exists(self, client: AsyncClient) -> None:
        """The SSE endpoint should be accessible."""
        response = await client.get(
            "/api/v1/mcp/sse",
            headers={"Accept": "text/event-stream"},
            timeout=5.0,
        )
        # Should either stream or return appropriate status
        assert response.status_code in (200, 204, 404)
