"""
API endpoint tests for Penske Logistics Analytics
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.api_server import app


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


class TestHealthEndpoints:
    """Test health check endpoints"""
    
    def test_root_endpoint(self, client):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data


class TestPerformanceEndpoints:
    """Test performance API endpoints"""
    
    def test_performance_summary(self, client):
        response = client.get("/api/v1/performance/summary")
        assert response.status_code == 200
        data = response.json()
        assert "kpis" in data
        assert "summary" in data
    
    def test_regional_performance(self, client):
        response = client.get("/api/v1/performance/regional")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
    
    def test_scorecard(self, client):
        response = client.get("/api/v1/performance/scorecard")
        assert response.status_code == 200
        data = response.json()
        assert "scorecard" in data


class TestPredictionEndpoints:
    """Test prediction API endpoints"""
    
    def test_resource_prediction(self, client):
        response = client.post(
            "/api/v1/predict/resources",
            json={"forecast_days": 30}
        )
        assert response.status_code == 200
        data = response.json()
        assert "plan" in data
    
    def test_customer_prediction(self, client):
        response = client.post("/api/v1/predict/customers")
        assert response.status_code == 200
        data = response.json()
        assert "total_customers" in data


class TestInsightEndpoints:
    """Test insight generation endpoints"""
    
    def test_performance_insight(self, client):
        response = client.post(
            "/api/v1/insights/generate",
            json={"insight_type": "performance"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "content" in data
    
    def test_invalid_insight_type(self, client):
        response = client.post(
            "/api/v1/insights/generate",
            json={"insight_type": "invalid"}
        )
        assert response.status_code == 400


class TestAlertEndpoints:
    """Test alert endpoints"""
    
    def test_get_alerts(self, client):
        response = client.get("/api/v1/alerts")
        assert response.status_code == 200
        data = response.json()
        assert "alerts" in data
        assert "total_alerts" in data


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
