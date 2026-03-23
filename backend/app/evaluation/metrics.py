"""Custom evaluation metrics for RAG pipeline assessment."""

from dataclasses import dataclass
from typing import Literal


@dataclass
class EvalSample:
    """A single evaluation sample."""
    query: str
    expected_answer: str
    relevant_doc_ids: list[str]
    difficulty: Literal["simple", "complex", "multi-hop"]
    domain: str  # "api-docs", "design-docs", etc.


@dataclass
class EvalResult:
    """Result of evaluating a single sample."""
    query: str
    expected: str
    actual: str
    faithfulness: float  # 0-1: is answer grounded in sources?
    relevance: float     # 0-1: are retrieved docs relevant?
    answer_quality: float  # 0-1: is answer helpful and complete?
    retrieval_recall: float  # 0-1: did retrieval find correct docs?
    latency_ms: int


def compute_faithfulness(answer: str, source_texts: list[str]) -> float:
    """Compute faithfulness score — is the answer grounded in sources?

    Uses overlap-based heuristic as baseline.
    V1: Replace with LLM-as-judge evaluation.
    """
    if not answer or not source_texts:
        return 0.0

    answer_words = set(answer.lower().split())
    source_words = set()
    for text in source_texts:
        source_words.update(text.lower().split())

    if not answer_words:
        return 0.0

    overlap = len(answer_words & source_words)
    return min(overlap / len(answer_words), 1.0)


def compute_retrieval_recall(
    retrieved_doc_ids: list[str],
    relevant_doc_ids: list[str],
) -> float:
    """Compute recall@k — fraction of relevant docs that were retrieved."""
    if not relevant_doc_ids:
        return 1.0
    retrieved_set = set(retrieved_doc_ids)
    relevant_set = set(relevant_doc_ids)
    return len(retrieved_set & relevant_set) / len(relevant_set)


def compute_precision_at_k(
    retrieved_doc_ids: list[str],
    relevant_doc_ids: list[str],
    k: int = 5,
) -> float:
    """Compute precision@k — fraction of top-k retrieved docs that are relevant."""
    top_k = retrieved_doc_ids[:k]
    if not top_k:
        return 0.0
    relevant_set = set(relevant_doc_ids)
    relevant_in_top_k = sum(1 for doc_id in top_k if doc_id in relevant_set)
    return relevant_in_top_k / len(top_k)
