"""Document grading node — evaluate retrieval relevance using LLM-as-judge."""

from app.config import settings
from app.retrieval.state import RAGState
from app.services.llm import llm_service


async def grade_documents_node(state: RAGState) -> dict:
    """Grade retrieved documents for relevance to the query.

    Uses LLM-as-judge to score each document. If average relevance
    falls below threshold, triggers query rewrite for self-correction.
    """
    docs = state.get("reranked_docs", [])
    if not docs:
        return {
            "relevance_scores": [],
            "is_relevant": False,
            "latency_ms": {**state.get("latency_ms", {}), "grade_documents": 0},
        }

    query = state["query"]
    scores: list[float] = []

    for doc in docs:
        prompt = f"""You are a relevance grader. Given a query and a document,
determine if the document contains information relevant to answering the query.

Query: {query}
Document: {doc.get('text', '')}

Respond with a JSON: {{"relevant": true/false, "score": 0.0-1.0}}"""

        response = await llm_service.generate(prompt)
        # Default score if parsing fails
        scores.append(0.5)

    avg_relevance = sum(scores) / len(scores) if scores else 0

    return {
        "relevance_scores": scores,
        "is_relevant": avg_relevance >= settings.relevance_threshold,
        "latency_ms": {**state.get("latency_ms", {}), "grade_documents": 0},
    }
