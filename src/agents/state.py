"""
Penske Logistics Analytics — Shared State Schema
==================================================
Defines the TypedDict state that flows through the LangGraph StateGraph.
Every node reads from and writes to this shared state.
"""

from typing import TypedDict, List, Dict, Any, Optional, Annotated
from operator import add


class PenskeState(TypedDict):
    """Shared state for the Penske LangGraph orchestrator."""

    # ── Input ──────────────────────────────────────────────────────────
    query: str                                    # Original user question
    datasets: Dict[str, Any]                      # Loaded DataFrames (injected at startup)

    # ── Planning ───────────────────────────────────────────────────────
    plan: List[str]                               # Agent names to invoke (set by planner)
    current_agent_index: int                      # Tracks which agent is executing next

    # ── Agent Outputs ──────────────────────────────────────────────────
    agent_outputs: Dict[str, Any]                 # key = agent name, value = result dict
    rag_context: str                              # Retrieved document context from RAG

    # ── Control Flow ───────────────────────────────────────────────────
    needs_review: bool                            # Flag for human-in-the-loop gating
    review_approved: bool                         # Set by human review node

    # ── Error Handling ─────────────────────────────────────────────────
    error: Optional[str]                          # Error message if any node fails
    retry_count: int                              # Current retry attempt (max 3)

    # ── Output ─────────────────────────────────────────────────────────
    final_answer: str                             # Synthesized response to the user
