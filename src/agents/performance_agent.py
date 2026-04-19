"""
Performance Agent — Analyzes KPIs, trends, anomalies, and regional performance
================================================================================
Wraps ServicePerformanceAnalyzer tools and uses LLM to interpret results.
"""

import os
import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

try:
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import SystemMessage, HumanMessage
    HAS_LANGCHAIN = True
except ImportError:
    HAS_LANGCHAIN = False

from src.tools.performance_tools import ALL_PERFORMANCE_TOOLS

SYSTEM_PROMPT = """You are the Performance Analysis Agent for Penske Logistics.
You have access to tools that calculate KPIs, analyze regions, detect underperformers,
generate scorecards, and analyze trends.

When answering:
1. Always call at least one tool to get real data — never fabricate numbers.
2. Present key findings with specific metrics and percentages.
3. Highlight areas of concern (below target) and areas of strength (exceeding target).
4. If asked about a specific metric or region, use the most targeted tool.
5. For broad questions, use get_executive_summary or calculate_kpis.
6. Return your analysis as structured JSON with keys: "summary", "key_metrics", "concerns", "recommendations".
"""


def _run_with_llm(query: str, context: str = "") -> Dict[str, Any]:
    """Run the performance agent with LLM tool-calling."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or not HAS_LANGCHAIN:
        return _run_without_llm(query)

    try:
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            api_key=api_key,
        ).bind_tools(ALL_PERFORMANCE_TOOLS)

        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=f"User question: {query}\n\nAdditional context: {context}" if context else f"User question: {query}"),
        ]

        # First call — LLM decides which tools to use
        response = llm.invoke(messages)

        # Execute tool calls
        tool_results = {}
        if response.tool_calls:
            tool_map = {t.name: t for t in ALL_PERFORMANCE_TOOLS}
            for tc in response.tool_calls:
                tool_name = tc["name"]
                tool_args = tc["args"]
                if tool_name in tool_map:
                    result = tool_map[tool_name].invoke(tool_args)
                    tool_results[tool_name] = result

        # Second call — LLM synthesizes tool results into analysis
        messages.append(response)
        for tool_name, result in tool_results.items():
            messages.append(HumanMessage(content=f"Tool '{tool_name}' returned:\n{result}"))

        messages.append(HumanMessage(content="Now synthesize these results into a clear analysis. Return JSON with keys: summary, key_metrics, concerns, recommendations."))

        final_response = ChatOpenAI(
            model="gpt-4o-mini", temperature=0.3, api_key=api_key,
        ).invoke(messages)

        try:
            content = final_response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            return json.loads(content)
        except (json.JSONDecodeError, IndexError):
            return {
                "summary": final_response.content,
                "key_metrics": tool_results,
                "concerns": [],
                "recommendations": [],
            }

    except Exception as e:
        logger.error(f"Performance agent LLM failed: {e}")
        return _run_without_llm(query)


def _run_without_llm(query: str) -> Dict[str, Any]:
    """Fallback: run performance tools directly without LLM interpretation."""
    query_lower = query.lower()

    results = {}

    if any(kw in query_lower for kw in ["executive", "summary", "overview", "briefing", "how are we"]):
        results["executive_summary"] = json.loads(
            ALL_PERFORMANCE_TOOLS[4].invoke({})  # get_executive_summary
        )
    elif any(kw in query_lower for kw in ["region", "area", "geographic", "northeast", "southeast", "midwest", "west"]):
        results["regional_analysis"] = json.loads(
            ALL_PERFORMANCE_TOOLS[1].invoke({})  # analyze_by_region
        )
    elif any(kw in query_lower for kw in ["underperform", "problem", "issue", "concern", "attention"]):
        results["underperformers"] = json.loads(
            ALL_PERFORMANCE_TOOLS[3].invoke({"threshold_pct": 20.0})  # identify_underperformers
        )
    elif any(kw in query_lower for kw in ["trend", "over time", "historical", "change"]):
        metric = "on_time_rate"
        if "revenue" in query_lower:
            metric = "revenue"
        elif "profit" in query_lower:
            metric = "profit_margin"
        results["trend"] = json.loads(
            ALL_PERFORMANCE_TOOLS[6].invoke({"metric": metric, "period": "M"})  # analyze_trend
        )
    elif any(kw in query_lower for kw in ["scorecard", "target", "achievement"]):
        results["scorecard"] = json.loads(
            ALL_PERFORMANCE_TOOLS[5].invoke({})  # get_performance_scorecard
        )
    else:
        results["kpis"] = json.loads(
            ALL_PERFORMANCE_TOOLS[0].invoke({})  # calculate_kpis
        )

    return {
        "summary": "Performance analysis completed (no LLM — raw tool output).",
        "key_metrics": results,
        "concerns": [],
        "recommendations": [],
    }


def performance_agent_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """LangGraph node: run performance analysis and store results."""
    query = state.get("query", "")
    rag_context = state.get("rag_context", "")

    try:
        result = _run_with_llm(query, rag_context)
        outputs = state.get("agent_outputs", {})
        outputs["performance"] = result
        return {"agent_outputs": outputs}
    except Exception as e:
        logger.error(f"Performance agent node failed: {e}")
        return {"error": f"Performance agent failed: {e}"}
