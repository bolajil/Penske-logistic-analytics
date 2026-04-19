"""
Customer Tools — @tool wrappers for LeadScorer, ChurnPredictor, CustomerSegmenter
==================================================================================
Thin wrappers that make existing customer analytics callable by LangGraph agents.
"""

import json
import logging
from typing import Dict, Any

from langchain_core.tools import tool

logger = logging.getLogger(__name__)

# Module-level references — set by orchestrator at startup
_lead_scorer = None
_churn_predictor = None
_segmenter = None


def set_lead_scorer(scorer):
    global _lead_scorer
    _lead_scorer = scorer


def set_churn_predictor(predictor):
    global _churn_predictor
    _churn_predictor = predictor


def set_segmenter(segmenter):
    global _segmenter
    _segmenter = segmenter


@tool
def score_leads(top_n: int = 10) -> str:
    """Score and rank sales leads for customer acquisition.
    Use this when the user asks about lead prioritization, sales pipeline, or prospect ranking.
    Args:
        top_n: Number of top leads to return (default 10)"""
    if _lead_scorer is None:
        return json.dumps({"error": "Lead scorer not initialized"})
    try:
        if hasattr(_lead_scorer, 'score_leads'):
            result = _lead_scorer.score_leads()
        elif hasattr(_lead_scorer, 'predict'):
            result = _lead_scorer.predict()
        else:
            return json.dumps({"error": "Lead scorer has no scoring method"})
        if hasattr(result, 'head'):
            return result.head(top_n).to_json(orient="records")
        return json.dumps(result, default=str)
    except Exception as e:
        logger.error(f"score_leads failed: {e}")
        return json.dumps({"error": str(e)})


@tool
def predict_churn(threshold: float = 0.5) -> str:
    """Predict which customers are at risk of churning.
    Use this when the user asks about customer retention, churn risk, or at-risk accounts.
    Args:
        threshold: Probability threshold to flag as at-risk (default 0.5)"""
    if _churn_predictor is None:
        return json.dumps({"error": "Churn predictor not initialized"})
    try:
        if hasattr(_churn_predictor, 'predict_churn'):
            result = _churn_predictor.predict_churn(threshold=threshold)
        elif hasattr(_churn_predictor, 'predict'):
            result = _churn_predictor.predict(threshold=threshold)
        else:
            return json.dumps({"error": "Churn predictor has no predict method"})
        if hasattr(result, 'to_json'):
            return result.to_json(orient="records")
        return json.dumps(result, default=str)
    except Exception as e:
        logger.error(f"predict_churn failed: {e}")
        return json.dumps({"error": str(e)})


@tool
def segment_customers(n_segments: int = 4) -> str:
    """Segment customers into groups based on behavior, value, and engagement.
    Use this when the user asks about customer segments, groups, or clustering.
    Args:
        n_segments: Number of customer segments to create (default 4)"""
    if _segmenter is None:
        return json.dumps({"error": "Customer segmenter not initialized"})
    try:
        if hasattr(_segmenter, 'segment'):
            result = _segmenter.segment(n_clusters=n_segments)
        elif hasattr(_segmenter, 'fit_predict'):
            result = _segmenter.fit_predict(n_clusters=n_segments)
        else:
            return json.dumps({"error": "Segmenter has no segment method"})
        if hasattr(result, 'to_json'):
            return result.to_json(orient="records")
        return json.dumps(result, default=str)
    except Exception as e:
        logger.error(f"segment_customers failed: {e}")
        return json.dumps({"error": str(e)})


@tool
def get_customer_overview() -> str:
    """Get an overview of the customer base — total customers, retention rate,
    average contract value, satisfaction score. Use for quick customer health checks."""
    results = {}
    if _lead_scorer and hasattr(_lead_scorer, 'get_pipeline_summary'):
        try:
            results["pipeline"] = _lead_scorer.get_pipeline_summary()
        except Exception:
            pass
    if _churn_predictor and hasattr(_churn_predictor, 'get_summary'):
        try:
            results["churn"] = _churn_predictor.get_summary()
        except Exception:
            pass
    if not results:
        results["message"] = "Customer modules not fully initialized"
    return json.dumps(results, default=str)


# Convenience: list of all customer tools for agent binding
ALL_CUSTOMER_TOOLS = [
    score_leads,
    predict_churn,
    segment_customers,
    get_customer_overview,
]
