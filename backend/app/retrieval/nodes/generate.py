"""Answer generation node with source citations."""

from app.retrieval.state import RAGState
from app.services.llm import llm_service


async def generate_node(state: RAGState) -> dict:
    """Generate an answer with source citations from graded documents.

    Constructs a prompt with the relevant documents and instructs
    the LLM to cite sources using [1], [2], etc. notation.
    """
    query = state["query"]
    docs = state.get("reranked_docs", [])

    # Build context from retrieved documents
    context_parts = []
    sources = []
    for i, doc in enumerate(docs):
        context_parts.append(f"[{i + 1}] {doc.get('text', '')}")
        sources.append({
            "doc_title": doc.get("doc_title", "Unknown"),
            "chunk_text": doc.get("text", "")[:500],
            "source_url": doc.get("source_url"),
            "relevance_score": doc.get("rerank_score", doc.get("rrf_score", 0.0)),
            "page_number": doc.get("page_number"),
        })

    context = "\n\n".join(context_parts) if context_parts else "No relevant documents found."

    prompt = f"""Answer the question based on the provided context. Cite sources using [1], [2], etc.
If the context doesn't contain enough information, say so honestly.

Context:
{context}

Question: {query}

Answer:"""

    answer = await llm_service.generate(prompt)

    return {
        "answer": answer or "I couldn't generate an answer based on the available documents.",
        "sources": sources,
        "latency_ms": {**state.get("latency_ms", {}), "generate": 0},
    }
