"""Reciprocal Rank Fusion for combining dense and sparse retrieval results."""

from dataclasses import dataclass

from app.config import settings


@dataclass
class HybridSearchConfig:
    """Configuration for hybrid retrieval."""
    dense_weight: float = settings.dense_weight
    sparse_weight: float = settings.sparse_weight
    top_k_per_source: int = 20
    final_top_k: int = settings.retrieval_top_k
    rrf_k: int = settings.rrf_k


def reciprocal_rank_fusion(
    dense_results: list[dict],
    sparse_results: list[dict],
    k: int = 60,
) -> list[dict]:
    """Fuse dense and sparse retrieval results using Reciprocal Rank Fusion.

    RRF score = sum(1 / (k + rank_i)) for each ranking list.
    Simple, parameter-free (except k), consistently outperforms
    linear combination in practice.

    Args:
        dense_results: Documents ranked by vector similarity.
        sparse_results: Documents ranked by BM25/sparse score.
        k: RRF constant (default 60, standard value).

    Returns:
        Fused and sorted list of documents with rrf_score.
    """
    scores: dict[str, float] = {}
    doc_map: dict[str, dict] = {}

    for rank, doc in enumerate(dense_results):
        chunk_id = doc["chunk_id"]
        scores[chunk_id] = scores.get(chunk_id, 0) + 1 / (k + rank + 1)
        doc_map[chunk_id] = doc

    for rank, doc in enumerate(sparse_results):
        chunk_id = doc["chunk_id"]
        scores[chunk_id] = scores.get(chunk_id, 0) + 1 / (k + rank + 1)
        doc_map[chunk_id] = doc

    sorted_ids = sorted(scores, key=lambda cid: scores[cid], reverse=True)
    return [
        {**doc_map[cid], "rrf_score": scores[cid]}
        for cid in sorted_ids
    ]
