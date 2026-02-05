"""
Penske Logistics Analytics API Server
FastAPI REST endpoints for programmatic access
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_prep import DataLoader
from src.service_performance import ServicePerformanceAnalyzer
from src.resource_prediction import DemandForecaster, ResourceOptimizer
from src.customer_acquisition import LeadScorer, ChurnPredictor
from src.genai_insights import InsightGenerator

app = FastAPI(
    title="Penske Logistics Analytics API",
    description="REST API for logistics performance analysis and predictions",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

loader = DataLoader(use_dummy=True)
datasets = loader.load_all()
analyzer = ServicePerformanceAnalyzer(datasets)
insight_generator = InsightGenerator()


class PredictionRequest(BaseModel):
    region: Optional[str] = None
    service_type: Optional[str] = None
    forecast_days: int = 30


class LeadScoreRequest(BaseModel):
    lead_ids: List[str]


class InsightRequest(BaseModel):
    insight_type: str
    context: Optional[Dict] = None


@app.get("/")
async def root():
    """API health check"""
    return {
        "status": "healthy",
        "service": "Penske Logistics Analytics API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/v1/performance/summary")
async def get_performance_summary():
    """Get overall performance KPIs"""
    try:
        kpis = analyzer.calculate_overall_kpis()
        summary = analyzer.get_executive_summary()
        return {
            "kpis": kpis,
            "summary": summary,
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/performance/regional")
async def get_regional_performance():
    """Get performance metrics by region"""
    try:
        regional = analyzer.analyze_by_region()
        return {
            "data": regional.to_dict(),
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/performance/service/{service_type}")
async def get_service_performance(service_type: str):
    """Get performance for a specific service type"""
    try:
        service_data = analyzer.analyze_by_service_type()
        if service_type in service_data.index:
            return {
                "service_type": service_type,
                "metrics": service_data.loc[service_type].to_dict(),
                "generated_at": datetime.now().isoformat()
            }
        raise HTTPException(status_code=404, detail=f"Service type '{service_type}' not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/performance/scorecard")
async def get_scorecard():
    """Get performance scorecard"""
    try:
        scorecard = analyzer.generate_performance_scorecard()
        return {
            "scorecard": scorecard.to_dict(orient='records'),
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/predict/resources")
async def predict_resources(request: PredictionRequest):
    """Predict resource requirements"""
    try:
        forecaster = DemandForecaster()
        optimizer = ResourceOptimizer(forecaster)
        
        plan = optimizer.generate_resource_plan(
            datasets.get('regional_demand'),
            datasets.get('fleet_operations'),
            datasets.get('warehouse_metrics')
        )
        
        if request.region and request.region in plan['regions']:
            return {
                "region": request.region,
                "plan": plan['regions'][request.region],
                "generated_at": datetime.now().isoformat()
            }
        
        return {
            "plan": plan,
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/predict/customers")
async def predict_customer_metrics():
    """Get customer churn predictions and lead scores"""
    try:
        if 'customer_data' not in datasets:
            raise HTTPException(status_code=404, detail="Customer data not available")
        
        churn_predictor = ChurnPredictor()
        churn_predictor.train(datasets['customer_data'])
        churn_risks = churn_predictor.predict_churn_risk(datasets['customer_data'])
        
        high_risk = churn_risks[churn_risks['risk_level'].isin(['High', 'Critical'])]
        
        return {
            "total_customers": len(datasets['customer_data']),
            "high_risk_count": len(high_risk),
            "total_revenue_at_risk": float(high_risk['revenue_at_risk'].sum()),
            "high_risk_customers": high_risk[['customer_id', 'company_name', 'churn_risk_score', 'risk_level']].head(20).to_dict(orient='records'),
            "generated_at": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/insights/generate")
async def generate_insights(request: InsightRequest):
    """Generate AI-powered insights"""
    try:
        if request.insight_type == "performance":
            kpis = analyzer.calculate_overall_kpis()
            insight = insight_generator.generate_performance_insight(kpis)
        elif request.insight_type == "resources":
            optimizer = ResourceOptimizer()
            plan = optimizer.generate_resource_plan(
                datasets.get('regional_demand'),
                datasets.get('fleet_operations'),
                datasets.get('warehouse_metrics')
            )
            insight = insight_generator.generate_resource_recommendation(plan)
        elif request.insight_type == "customers":
            customer_summary = {
                "total_customers": len(datasets.get('customer_data', [])),
                "avg_satisfaction": datasets['customer_data']['satisfaction_score'].mean() if 'customer_data' in datasets else 0
            }
            insight = insight_generator.generate_customer_insight(customer_summary)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown insight type: {request.insight_type}")
        
        return {
            "insight_type": request.insight_type,
            "content": insight,
            "generated_at": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/alerts")
async def get_alerts():
    """Get current operational alerts"""
    try:
        underperforming = analyzer.identify_underperforming_areas()
        
        alerts = []
        for area, items in underperforming.items():
            severity = "high" if len(items) > 5 else "medium"
            alerts.append({
                "type": area,
                "severity": severity,
                "affected_items": items[:10],
                "count": len(items)
            })
        
        return {
            "alerts": alerts,
            "total_alerts": len(alerts),
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
