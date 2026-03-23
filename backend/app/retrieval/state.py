"""RAG state schema for the LangGraph state machine."""

from typing import Annotated, Literal, TypedDict

from langgraph.graph.message import add_messages


class RAGState(TypedDict):
    """State schema for the Agentic RAG graph.

    Tracks the full lifecycle of a query through analysis, retrieval,
    grading, potential rewriting, and generation.
    """

    # Input
    query: str
    namespace: str
    conversation_id: str | None

    # Query Analysis
    query_type: Literal["simple", "complex"] | None
    sub_queries: list[str]
    entities: list[str]

    # Retrieval
    retrieved_docs: list[dict]  # [{chunk_id, text, score, source}]
    reranked_docs: list[dict]   # post cross-encoder

    # Grading
    relevance_scores: list[float]
    is_relevant: bool | None

    # Self-Correction
    rewrite_count: int  # track retry attempts
    rewritten_query: str | None

    # Generation
    answer: str | None
    sources: list[dict]  # [{doc_title, chunk_text, url, score}]
    cached: bool

    # Metadata
    messages: Annotated[list, add_messages]  # conversation history
    latency_ms: dict  # per-node latency tracking
