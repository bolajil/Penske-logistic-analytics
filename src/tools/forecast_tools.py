"""
Forecast Tools — @tool wrappers for DemandForecaster & FleetOptimizer
======================================================================
Thin wrappers that make existing prediction functions callable by LangGraph agents.
"""

import json
import logging
from typing import Dict, Any

from langchain_core.tools import tool

logger = logging.getLogger(__name__)

# Module-level references — set by orchestrator at startup
_forecaster = None
_fleet_optimizer = None
_capacity_planner = None


def set_forecaster(forecaster):
    """Inject the DemandForecaster instance."""
    global _forecaster
    _forecaster = forecaster


def set_fleet_optimizer(optimizer):
    """Inject the FleetOptimizer instance."""
    global _fleet_optimizer
    _fleet_optimizer = optimizer


def set_capacity_planner(planner):
    """Inject the CapacityPlanner instance."""
    global _capacity_planner
    _capacity_planner = planner


@tool
def forecast_demand(region: str = "all", horizon_days: int = 30) -> str:
    """Forecast demand for logistics resources across regions.
    Use this when the user asks about future demand, expected volumes, or planning ahead.
    Args:
        region: Region to forecast for, or 'all' for company-wide
        horizon_days: Number of days to forecast ahead (default 30)"""
    if _forecaster is None:
        return json.dumps({"error": "Forecaster not initialized"})
    try:
        if hasattr(_forecaster, 'predict'):
            result = _forecaster.predict(region=region, horizon_days=horizon_days)
            if hasattr(result, 'to_json'):
                return result.to_json(orient="records")
            return json.dumps(result, default=str)
        elif hasattr(_forecaster, 'forecast'):
            result = _forecaster.forecast(region=region, horizon_days=horizon_days)
            return json.dumps(result, default=str)
        return json.dumps({"error": "Forecaster has no predict/forecast method"})
    except Exception as e:
        logger.error(f"forecast_demand failed: {e}")
        return json.dumps({"error": str(e)})


@tool
def optimize_fleet(region: str = "all") -> str:
    """Optimize fleet allocation and recommend vehicle distribution.
    Use this when the user asks about fleet sizing, vehicle allocation, or fleet efficiency.
    Args:
        region: Region to optimize for, or 'all' for company-wide"""
    if _fleet_optimizer is None:
        return json.dumps({"error": "Fleet optimizer not initialized"})
    try:
        if hasattr(_fleet_optimizer, 'optimize'):
            result = _fleet_optimizer.optimize(region=region)
        elif hasattr(_fleet_optimizer, 'recommend_fleet_size'):
            result = _fleet_optimizer.recommend_fleet_size(region=region)
        else:
            return json.dumps({"error": "Fleet optimizer has no optimize method"})
        return json.dumps(result, default=str)
    except Exception as e:
        logger.error(f"optimize_fleet failed: {e}")
        return json.dumps({"error": str(e)})


@tool
def plan_capacity(scenario: str = "baseline") -> str:
    """Run capacity planning analysis for warehouse and fleet resources.
    Use this when the user asks about capacity, warehousing needs, or scaling.
    Args:
        scenario: Planning scenario — 'baseline', 'growth_10', 'growth_20', 'peak_season'"""
    if _capacity_planner is None:
        return json.dumps({"error": "Capacity planner not initialized"})
    try:
        if hasattr(_capacity_planner, 'plan'):
            result = _capacity_planner.plan(scenario=scenario)
        elif hasattr(_capacity_planner, 'run_scenario'):
            result = _capacity_planner.run_scenario(scenario=scenario)
        else:
            return json.dumps({"error": "Capacity planner has no plan method"})
        return json.dumps(result, default=str)
    except Exception as e:
        logger.error(f"plan_capacity failed: {e}")
        return json.dumps({"error": str(e)})


@tool
def get_resource_summary() -> str:
    """Get a summary of current resource allocation and utilization.
    Use this for a quick overview of fleet, warehouse, and staffing status."""
    results = {}
    if _forecaster and hasattr(_forecaster, 'get_summary'):
        try:
            results["demand"] = _forecaster.get_summary()
        except Exception as e:
            results["demand"] = {"error": str(e)}
    if _fleet_optimizer and hasattr(_fleet_optimizer, 'get_summary'):
        try:
            results["fleet"] = _fleet_optimizer.get_summary()
        except Exception as e:
            results["fleet"] = {"error": str(e)}
    if not results:
        results["message"] = "Resource modules not fully initialized"
    return json.dumps(results, default=str)


# Convenience: list of all forecast tools for agent binding
ALL_FORECAST_TOOLS = [
    forecast_demand,
    optimize_fleet,
    plan_capacity,
    get_resource_summary,
]
