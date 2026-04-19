"""
Planner Node — Intent Classification & Agent Routing
=====================================================
Uses LLM to classify the user's query and determine which agents to invoke.
Falls back to keyword-based classification if LLM is unavailable.
"""

import os
import json
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

try:
    from langchain_openai import ChatOpenAI
    HAS_LANGCHAIN_OPENAI = True
except ImportError:
    HAS_LANGCHAIN_OPENAI = False

# Agent categories the planner can route to
VALID_AGENTS = ["performance", "forecast", "customer", "rag"]

# Keyword-based fallback classification
KEYWORD_MAP = {
    "performance": [
        "kpi", "metric", "on-time", "delivery rate", "fleet utilization",
        "warehouse", "scorecard", "underperform", "trend", "anomaly",
        "region", "service type", "executive summary", "performance",
        "how are we doing", "status", "health", "efficiency",
    ],
    "forecast": [
        "forecast", "predict", "demand", "capacity", "fleet size",
        "staffing", "resource", "plan", "next month", "next quarter",
        "growth", "scaling", "optimize", "allocation", "future",
    ],
    "customer": [
        "customer", "lead", "churn", "retention", "acquisition",
        "segment", "sales", "pipeline", "prospect", "at-risk",
        "satisfaction", "contract", "revenue per customer",
    ],
    "rag": [
        "policy", "procedure", "sop", "document", "guide",
        "how to", "what is the process", "regulation", "compliance",
        "best practice", "standard", "manual",
    ],
}

PLANNER_SYSTEM_PROMPT = """You are a logistics analytics planner for Penske Logistics.
Your job is to classify the user's question and decide which specialist agents to invoke.

Available agents:
- performance: KPIs, delivery rates, fleet utilization, warehouse metrics, trends, anomalies, regional analysis
- forecast: Demand prediction, fleet sizing, capacity planning, resource allocation, staffing needs
- customer: Lead scoring, churn prediction, customer segmentation, retention analysis, sales pipeline
- rag: Document search, company policies, SOPs, procedures, best practices

Rules:
1. Return a JSON array of agent names to invoke, in order of priority.
2. Most questions need 1-2 agents. Complex questions may need 3.
3. Always include "rag" if the question references policies, procedures, or needs supporting context.
4. If the question is ambiguous, include "performance" as the default.
5. Return ONLY the JSON array, no other text.

Examples:
- "What's our on-time delivery rate?" → ["performance"]
- "How many trucks do we need next quarter?" → ["forecast"]
- "Which customers are at risk of leaving?" → ["customer"]
- "What's our SOP for handling damaged goods?" → ["rag"]
- "Why is the Northeast region underperforming and what should we do about it?" → ["performance", "rag"]
- "Give me a full executive briefing" → ["performance", "forecast", "customer"]
"""


def classify_with_llm(query: str) -> List[str]:
    """Use LLM to classify query intent and return agent list."""
    if not HAS_LANGCHAIN_OPENAI:
        return []

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return []

    try:
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            api_key=api_key,
            max_tokens=100,
        )
        response = llm.invoke([
            {"role": "system", "content": PLANNER_SYSTEM_PROMPT},
            {"role": "user", "content": query},
        ])
        content = response.content.strip()
        # Parse JSON array from response
        if content.startswith("["):
            agents = json.loads(content)
            return [a for a in agents if a in VALID_AGENTS]
        return []
    except Exception as e:
        logger.warning(f"LLM classification failed, falling back to keywords: {e}")
        return []


def classify_with_keywords(query: str) -> List[str]:
    """Fallback: keyword-based intent classification."""
    query_lower = query.lower()
    scores = {}
    for agent, keywords in KEYWORD_MAP.items():
        score = sum(1 for kw in keywords if kw in query_lower)
        if score > 0:
            scores[agent] = score

    if not scores:
        return ["performance"]  # default agent

    # Sort by score descending, return top agents
    sorted_agents = sorted(scores.keys(), key=lambda a: scores[a], reverse=True)
    return sorted_agents[:3]


def plan_agents(query: str) -> List[str]:
    """
    Main planner function: classify user query and return ordered list of agents.
    Tries LLM first, falls back to keyword classification.
    """
    # Try LLM classification first
    agents = classify_with_llm(query)
    if agents:
        logger.info(f"Planner (LLM): {agents}")
        return agents

    # Fallback to keywords
    agents = classify_with_keywords(query)
    logger.info(f"Planner (keywords): {agents}")
    return agents


def planner_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """LangGraph node: classify query and set the plan."""
    query = state.get("query", "")
    agents = plan_agents(query)
    return {
        "plan": agents,
        "current_agent_index": 0,
        "agent_outputs": {},
        "needs_review": False,
        "error": None,
        "retry_count": 0,
    }
