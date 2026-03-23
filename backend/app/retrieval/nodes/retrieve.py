"""Hybrid retrieval node — vector + BM25 + RRF fusion."""

from app.retrieval.state import RAGState
from app.retrieval.strategies.hybrid import reciprocal_rank_fusion
from app.services.milvus import milvus_service


async def hybrid_retrieve_node(state: RAGState) -> dict:
    """Perform hybrid retrieval combining dense vector and sparse BM25 search.

    Uses BGE-M3's dual embeddings with Milvus for both dense and sparse
    retrieval, then fuses results using Reciprocal Rank Fusion (RRF).
    """
    query = state.get("rewritten_query") or state["query"]
    namespace = state["namespace"]

    # TODO: Embed query, search Milvus (dense + sparse), apply RRF
    retrieved_docs: list[dict] = []

    return {
        "retrieved_docs": retrieved_docs,
        "latency_ms": {**state.get("latency_ms", {}), "hybrid_retrieve": 0},
    }
