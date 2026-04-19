"""
RAG Tools — @tool wrappers for RAGEngine
==========================================
Thin wrappers that make document retrieval callable by LangGraph agents.
"""

import json
import logging
from typing import Dict, Any

from langchain_core.tools import tool

logger = logging.getLogger(__name__)

# Module-level reference — set by orchestrator at startup
_rag_engine = None


def set_rag_engine(engine):
    """Inject the RAGEngine instance."""
    global _rag_engine
    _rag_engine = engine


@tool
def search_documents(query: str, top_k: int = 5) -> str:
    """Search logistics knowledge base for relevant documents, SOPs, and policies.
    Use this when the user asks about company policies, procedures, best practices,
    or when you need additional context to answer a question.
    Args:
        query: Natural language search query
        top_k: Number of results to return (default 5)"""
    if _rag_engine is None:
        return json.dumps({"error": "RAG engine not initialized"})
    try:
        if hasattr(_rag_engine, 'query'):
            results = _rag_engine.query(query, top_k=top_k)
        elif hasattr(_rag_engine, 'search'):
            results = _rag_engine.search(query, top_k=top_k)
        elif hasattr(_rag_engine, 'similarity_search'):
            results = _rag_engine.similarity_search(query, k=top_k)
        else:
            return json.dumps({"error": "RAG engine has no query/search method"})
        if isinstance(results, list):
            return json.dumps([
                {
                    "content": getattr(r, "page_content", r.get("text", str(r))) if hasattr(r, "page_content") else r.get("text", str(r)),
                    "metadata": getattr(r, "metadata", r.get("metadata", {})) if hasattr(r, "metadata") else r.get("metadata", {}),
                }
                for r in results
            ], default=str)
        return json.dumps(results, default=str)
    except Exception as e:
        logger.error(f"search_documents failed: {e}")
        return json.dumps({"error": str(e)})


@tool
def get_document_context(query: str) -> str:
    """Retrieve and concatenate relevant document context for a query.
    Returns a single text block of the most relevant content.
    Use this to enrich agent responses with supporting documentation.
    Args:
        query: Natural language search query"""
    if _rag_engine is None:
        return "No RAG engine available — responding without document context."
    try:
        if hasattr(_rag_engine, 'get_context'):
            return _rag_engine.get_context(query)
        if hasattr(_rag_engine, 'query'):
            results = _rag_engine.query(query, top_k=3)
            if isinstance(results, list):
                chunks = []
                for r in results:
                    if hasattr(r, "page_content"):
                        chunks.append(r.page_content)
                    elif isinstance(r, dict) and "text" in r:
                        chunks.append(r["text"])
                    else:
                        chunks.append(str(r))
                return "\n\n---\n\n".join(chunks) if chunks else "No relevant documents found."
            return str(results)
        return "RAG engine has no query method."
    except Exception as e:
        logger.error(f"get_document_context failed: {e}")
        return f"Error retrieving context: {e}"


# Convenience: list of all RAG tools for agent binding
ALL_RAG_TOOLS = [
    search_documents,
    get_document_context,
]
