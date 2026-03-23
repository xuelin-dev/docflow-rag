"""Query rewrite node for self-correction loop."""

from app.retrieval.state import RAGState
from app.services.llm import llm_service


async def rewrite_query_node(state: RAGState) -> dict:
    """Rewrite the query to improve retrieval in the next attempt.

    Uses LLM to generate an alternative query that might retrieve
    more relevant documents based on what was (and wasn't) found.
    """
    query = state["query"]
    docs = state.get("reranked_docs", [])
    doc_summaries = "\n".join(d.get("text", "")[:200] for d in docs[:3])

    prompt = f"""The original query did not retrieve relevant documents.

Original query: {query}
Retrieved documents (not relevant enough):
{doc_summaries}

Generate a better search query that would find the right information.
Focus on key terms and specificity. Return only the rewritten query."""

    rewritten = await llm_service.generate(prompt)
    rewritten = rewritten.strip() if rewritten else query

    return {
        "rewritten_query": rewritten,
        "query": rewritten,
        "rewrite_count": state.get("rewrite_count", 0) + 1,
        "latency_ms": {**state.get("latency_ms", {}), "rewrite_query": 0},
    }
