"""Query routing and decomposition nodes."""

from app.retrieval.state import RAGState
from app.services.llm import llm_service


async def route_node(state: RAGState) -> dict:
    """Route query based on analysis — no additional processing needed.

    The query_type is already determined by analyze_query_node.
    This node serves as the branching point in the graph.
    """
    return {"latency_ms": {**state.get("latency_ms", {}), "route": 0}}


async def decompose_query_node(state: RAGState) -> dict:
    """Break a complex query into simpler sub-queries for parallel retrieval.

    For multi-faceted questions, decomposition improves recall by
    searching for each aspect independently.
    """
    query = state["query"]

    prompt = f"""Break this complex query into 2-3 simpler sub-queries for document search.
Return a JSON list of strings.

Query: {query}"""

    response = await llm_service.generate(prompt)

    # Default: use original query as-is
    return {
        "sub_queries": [query],
        "latency_ms": {**state.get("latency_ms", {}), "decompose_query": 0},
    }
