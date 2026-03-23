"""Cross-encoder reranking node using BGE-reranker-v2-m3."""

from app.config import settings
from app.retrieval.state import RAGState


async def rerank_node(state: RAGState) -> dict:
    """Rerank retrieved documents using cross-encoder for fine-grained relevance.

    Cross-encoder sees (query, document) pairs jointly, capturing
    relevance that bi-encoder embedding similarity misses.
    Latency: ~15ms per pair on GPU, ~100ms per pair on CPU.
    """
    if not settings.reranker_enabled or not state.get("retrieved_docs"):
        return {
            "reranked_docs": state.get("retrieved_docs", []),
            "latency_ms": {**state.get("latency_ms", {}), "rerank": 0},
        }

    # TODO: Initialize reranker and score pairs
    # from FlagEmbedding import FlagReranker
    # reranker = FlagReranker(settings.reranker_model, use_fp16=True)

    return {
        "reranked_docs": state.get("retrieved_docs", [])[:settings.reranker_top_k],
        "latency_ms": {**state.get("latency_ms", {}), "rerank": 0},
    }
