"""
Performance Tools — @tool wrappers for ServicePerformanceAnalyzer
=================================================================
Thin wrappers that make existing analytics functions callable by LangGraph agents.
"""

import json
import logging
from typing import Dict, Any, Optional

from langchain_core.tools import tool

logger = logging.getLogger(__name__)

# Module-level reference — set by orchestrator at startup
_analyzer = None


def set_analyzer(analyzer):
    """Inject the ServicePerformanceAnalyzer instance."""
    global _analyzer
    _analyzer = analyzer


@tool
def calculate_kpis() -> str:
    """Calculate company-wide KPIs including on-time delivery rate, fleet utilization,
    warehouse efficiency, customer satisfaction, maintenance costs, and profit margins.
    Use this when the user asks about overall performance or KPI metrics."""
    if _analyzer is None:
        return json.dumps({"error": "Performance analyzer not initialized"})
    try:
        kpis = _analyzer.calculate_overall_kpis()
        return json.dumps({k: round(v, 2) if isinstance(v, float) else v for k, v in kpis.items()})
    except Exception as e:
        logger.error(f"calculate_kpis failed: {e}")
        return json.dumps({"error": str(e)})


@tool
def analyze_by_region() -> str:
    """Analyze performance metrics broken down by geographic region.
    Use this when the user asks about regional performance, area comparisons,
    or which regions are doing best/worst."""
    if _analyzer is None:
        return json.dumps({"error": "Performance analyzer not initialized"})
    try:
        df = _analyzer.analyze_by_region()
        if df.empty:
            return json.dumps({"message": "No regional data available"})
        return df.round(2).to_json(orient="index")
    except Exception as e:
        logger.error(f"analyze_by_region failed: {e}")
        return json.dumps({"error": str(e)})


@tool
def analyze_by_service_type() -> str:
    """Analyze performance broken down by service type (e.g., FTL, LTL, Dedicated, etc.).
    Use this when the user asks about service-level performance or service comparisons."""
    if _analyzer is None:
        return json.dumps({"error": "Performance analyzer not initialized"})
    try:
        df = _analyzer.analyze_by_service_type()
        if df.empty:
            return json.dumps({"message": "No service type data available"})
        return df.round(2).to_json(orient="index")
    except Exception as e:
        logger.error(f"analyze_by_service_type failed: {e}")
        return json.dumps({"error": str(e)})


@tool
def identify_underperformers(threshold_pct: float = 20.0) -> str:
    """Find regions, drivers, and warehouses performing below average.
    Use this when the user asks about underperforming areas, problems, or what needs attention.
    Args:
        threshold_pct: Percentage below average to flag (default 20%)."""
    if _analyzer is None:
        return json.dumps({"error": "Performance analyzer not initialized"})
    try:
        result = _analyzer.identify_underperforming_areas(threshold_pct)
        return json.dumps(result, default=str)
    except Exception as e:
        logger.error(f"identify_underperformers failed: {e}")
        return json.dumps({"error": str(e)})


@tool
def get_executive_summary() -> str:
    """Generate a comprehensive executive summary with overall score, health status,
    critical areas, and actionable recommendations. Use this for high-level overview requests."""
    if _analyzer is None:
        return json.dumps({"error": "Performance analyzer not initialized"})
    try:
        summary = _analyzer.get_executive_summary()
        return json.dumps(summary, default=str)
    except Exception as e:
        logger.error(f"get_executive_summary failed: {e}")
        return json.dumps({"error": str(e)})


@tool
def get_performance_scorecard() -> str:
    """Generate a detailed KPI scorecard with targets, actuals, achievement percentages,
    and weighted scores. Use this when the user asks for a scorecard or target tracking."""
    if _analyzer is None:
        return json.dumps({"error": "Performance analyzer not initialized"})
    try:
        df = _analyzer.generate_performance_scorecard()
        return df.to_json(orient="records")
    except Exception as e:
        logger.error(f"get_performance_scorecard failed: {e}")
        return json.dumps({"error": str(e)})


@tool
def analyze_trend(metric: str = "on_time_rate", period: str = "M") -> str:
    """Analyze trends over time for a specific metric.
    Use this when the user asks about trends, changes over time, or historical patterns.
    Args:
        metric: One of 'on_time_rate', 'revenue', 'profit_margin', 'throughput', 'fill_rate'
        period: Time grouping — 'D' (daily), 'W' (weekly), 'M' (monthly), 'Q' (quarterly)"""
    if _analyzer is None:
        return json.dumps({"error": "Performance analyzer not initialized"})
    try:
        df = _analyzer.calculate_trend_analysis(metric, period)
        if isinstance(df, list) or df.empty:
            return json.dumps({"message": f"No trend data for {metric}"})
        df_out = df.copy()
        if "date" in df_out.columns:
            df_out["date"] = df_out["date"].astype(str)
        return df_out.to_json(orient="records")
    except Exception as e:
        logger.error(f"analyze_trend failed: {e}")
        return json.dumps({"error": str(e)})


# Convenience: list of all performance tools for agent binding
ALL_PERFORMANCE_TOOLS = [
    calculate_kpis,
    analyze_by_region,
    analyze_by_service_type,
    identify_underperformers,
    get_executive_summary,
    get_performance_scorecard,
    analyze_trend,
]
