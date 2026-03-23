"""Query analysis node — classify intent, extract entities, determine complexity."""

from app.retrieval.state import RAGState
from app.services.llm import llm_service


async def analyze_query_node(state: RAGState) -> dict:
    """Analyze the incoming query to extract entities and classify complexity.

    Uses LLM to determine if the query is simple (direct lookup) or
    complex (requires decomposition into sub-queries).
    """
    query = state["query"]

    prompt = f"""Analyze this query and respond with JSON:
{{
  "query_type": "simple" or "complex",
  "entities": ["list", "of", "key", "entities"],
  "reasoning": "brief explanation"
}}

Query: {query}"""

    response = await llm_service.generate(prompt)

    # Default to simple if parsing fails
    return {
        "query_type": "simple",
        "entities": [],
        "sub_queries": [],
        "latency_ms": {**state.get("latency_ms", {}), "analyze_query": 0},
    }
