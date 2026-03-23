"""LangGraph state machine for Agentic RAG."""

from langgraph.graph import END, StateGraph

from app.retrieval.nodes.analyze import analyze_query_node
from app.retrieval.nodes.generate import generate_node
from app.retrieval.nodes.grade import grade_documents_node
from app.retrieval.nodes.rerank import rerank_node
from app.retrieval.nodes.retrieve import hybrid_retrieve_node
from app.retrieval.nodes.rewrite import rewrite_query_node
from app.retrieval.nodes.route import decompose_query_node, route_node
from app.retrieval.state import RAGState


def route_after_grading(state: RAGState) -> str:
    """Decide next step after document grading.

    Returns:
        "relevant" — proceed to generation.
        "rewrite" — rewrite query and retry retrieval.
        "fallback" — max retries exceeded, generate with best-effort docs.
    """
    if state.get("is_relevant"):
        return "relevant"
    if state.get("rewrite_count", 0) >= 2:
        return "fallback"
    return "rewrite"


def build_rag_graph() -> StateGraph:
    """Build and compile the Agentic RAG state machine.

    Graph flow:
        analyze_query → route → [simple: hybrid_retrieve, complex: decompose → hybrid_retrieve]
        → rerank → grade_documents → [relevant: generate, not relevant: rewrite → retry]
        → END

    Max self-correction loops: 2 (configurable).
    """
    graph = StateGraph(RAGState)

    # Add nodes
    graph.add_node("analyze_query", analyze_query_node)
    graph.add_node("route", route_node)
    graph.add_node("decompose_query", decompose_query_node)
    graph.add_node("hybrid_retrieve", hybrid_retrieve_node)
    graph.add_node("rerank", rerank_node)
    graph.add_node("grade_documents", grade_documents_node)
    graph.add_node("rewrite_query", rewrite_query_node)
    graph.add_node("generate", generate_node)

    # Set entry point
    graph.set_entry_point("analyze_query")
    graph.add_edge("analyze_query", "route")

    # Conditional routing based on query complexity
    graph.add_conditional_edges(
        "route",
        lambda state: state.get("query_type", "simple"),
        {
            "simple": "hybrid_retrieve",
            "complex": "decompose_query",
        },
    )
    graph.add_edge("decompose_query", "hybrid_retrieve")
    graph.add_edge("hybrid_retrieve", "rerank")
    graph.add_edge("rerank", "grade_documents")

    # Grading → generate or rewrite
    graph.add_conditional_edges(
        "grade_documents",
        route_after_grading,
        {
            "relevant": "generate",
            "rewrite": "rewrite_query",
            "fallback": "generate",
        },
    )
    graph.add_edge("rewrite_query", "hybrid_retrieve")
    graph.add_edge("generate", END)

    return graph.compile()
