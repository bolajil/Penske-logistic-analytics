"""
Unit tests for Penske Logistics Analytics models
"""

import pytest
import pandas as pd
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_generator import (
    generate_fleet_operations,
    generate_warehouse_metrics,
    generate_customer_data,
    generate_delivery_performance,
    generate_regional_demand,
    generate_leads_data
)
from src.data_prep import DataLoader, DataPreprocessor
from src.service_performance import ServicePerformanceAnalyzer
from src.resource_prediction import DemandForecaster
from src.customer_acquisition import LeadScorer, ChurnPredictor, CustomerSegmenter


class TestDataGeneration:
    """Test data generation functions"""
    
    def test_fleet_operations_generation(self):
        df = generate_fleet_operations(100)
        assert len(df) == 100
        assert 'vehicle_id' in df.columns
        assert 'miles_driven' in df.columns
        assert df['miles_driven'].min() >= 0
    
    def test_warehouse_metrics_generation(self):
        df = generate_warehouse_metrics(100)
        assert len(df) == 100
        assert 'warehouse_id' in df.columns
        assert 'throughput_units' in df.columns
    
    def test_customer_data_generation(self):
        df = generate_customer_data(50)
        assert len(df) == 50
        assert 'customer_id' in df.columns
        assert 'contract_value' in df.columns
    
    def test_delivery_performance_generation(self):
        df = generate_delivery_performance(100)
        assert len(df) == 100
        assert 'on_time' in df.columns
        assert df['on_time'].dtype == bool
    
    def test_regional_demand_generation(self):
        df = generate_regional_demand(100)
        assert len(df) == 100
        assert 'shipment_volume' in df.columns
    
    def test_leads_data_generation(self):
        df = generate_leads_data(100)
        assert len(df) == 100
        assert 'converted' in df.columns


class TestDataPreprocessor:
    """Test data preprocessing functions"""
    
    @pytest.fixture
    def preprocessor(self):
        return DataPreprocessor()
    
    @pytest.fixture
    def sample_fleet_data(self):
        return generate_fleet_operations(100)
    
    def test_fleet_preprocessing(self, preprocessor, sample_fleet_data):
        processed = preprocessor.preprocess_fleet_data(sample_fleet_data)
        assert 'day_of_week' in processed.columns
        assert 'month' in processed.columns
        assert 'fuel_efficiency' in processed.columns
    
    def test_time_features_creation(self, preprocessor):
        df = pd.DataFrame({
            'date': pd.date_range('2024-01-01', periods=10),
            'value': range(10)
        })
        processed = preprocessor.create_time_features(df, 'date')
        assert 'year' in processed.columns
        assert 'month' in processed.columns
        assert 'sin_day' in processed.columns


class TestServicePerformance:
    """Test service performance analyzer"""
    
    @pytest.fixture
    def datasets(self):
        return {
            'fleet_operations': generate_fleet_operations(500),
            'warehouse_metrics': generate_warehouse_metrics(200),
            'customer_data': generate_customer_data(100),
            'delivery_performance': generate_delivery_performance(500),
            'maintenance_records': pd.DataFrame({
                'maintenance_id': range(100),
                'vehicle_id': [f'VH-{i}' for i in range(100)],
                'cost': np.random.normal(500, 100, 100),
                'downtime_hours': np.random.exponential(5, 100),
                'maintenance_type': np.random.choice(['Preventive', 'Corrective'], 100)
            })
        }
    
    @pytest.fixture
    def analyzer(self, datasets):
        return ServicePerformanceAnalyzer(datasets)
    
    def test_calculate_kpis(self, analyzer):
        kpis = analyzer.calculate_overall_kpis()
        assert isinstance(kpis, dict)
        assert 'on_time_delivery_rate' in kpis
    
    def test_regional_analysis(self, analyzer):
        regional = analyzer.analyze_by_region()
        assert isinstance(regional, pd.DataFrame)
    
    def test_executive_summary(self, analyzer):
        summary = analyzer.get_executive_summary()
        assert 'overall_score' in summary
        assert 'health_status' in summary
        assert 'recommendations' in summary


class TestDemandForecaster:
    """Test demand forecasting model"""
    
    @pytest.fixture
    def forecaster(self):
        return DemandForecaster()
    
    @pytest.fixture
    def demand_data(self):
        return generate_regional_demand(500)
    
    def test_feature_preparation(self, forecaster, demand_data):
        prepared = forecaster.prepare_features(demand_data)
        assert 'day_of_week' in prepared.columns
        assert 'sin_day' in prepared.columns
    
    def test_model_training(self, forecaster, demand_data):
        results = forecaster.train_demand_model(demand_data, 'shipment_volume')
        assert 'metrics' in results
        assert 'mae' in results['metrics']
        assert results['metrics']['mape'] > 0


class TestLeadScorer:
    """Test lead scoring model"""
    
    @pytest.fixture
    def scorer(self):
        return LeadScorer()
    
    @pytest.fixture
    def leads_data(self):
        return generate_leads_data(200)
    
    def test_model_training(self, scorer, leads_data):
        results = scorer.train(leads_data)
        assert 'metrics' in results
        assert 'auc_roc' in results['metrics']
        assert results['metrics']['auc_roc'] > 0.5
    
    def test_lead_scoring(self, scorer, leads_data):
        scorer.train(leads_data)
        scored = scorer.score_leads(leads_data.head(10))
        assert 'lead_score' in scored.columns
        assert 'priority' in scored.columns
        assert scored['lead_score'].max() <= 100


class TestChurnPredictor:
    """Test churn prediction model"""
    
    @pytest.fixture
    def predictor(self):
        return ChurnPredictor()
    
    @pytest.fixture
    def customer_data(self):
        return generate_customer_data(200)
    
    def test_model_training(self, predictor, customer_data):
        results = predictor.train(customer_data)
        assert 'metrics' in results
        assert results['metrics']['auc_roc'] > 0.5
    
    def test_churn_prediction(self, predictor, customer_data):
        predictor.train(customer_data)
        risks = predictor.predict_churn_risk(customer_data.head(10))
        assert 'churn_risk_score' in risks.columns
        assert 'risk_level' in risks.columns


class TestCustomerSegmenter:
    """Test customer segmentation"""
    
    @pytest.fixture
    def segmenter(self):
        return CustomerSegmenter(n_segments=3)
    
    @pytest.fixture
    def customer_data(self):
        return generate_customer_data(100)
    
    def test_segmentation(self, segmenter, customer_data):
        results = segmenter.fit_segments(customer_data)
        assert results['n_segments'] == 3
        assert len(results['segment_profiles']) == 3
    
    def test_segment_assignment(self, segmenter, customer_data):
        segmenter.fit_segments(customer_data)
        assigned = segmenter.assign_segments(customer_data)
        assert 'segment_id' in assigned.columns
        assert assigned['segment_id'].nunique() <= 3


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
