"""
Service Performance Analysis Module for Penske Logistics
Analyzes KPIs across all logistics services
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Container for performance metrics"""
    on_time_delivery_rate: float
    fleet_utilization: float
    warehouse_efficiency: float
    cost_per_shipment: float
    customer_satisfaction: float
    revenue_per_mile: float
    maintenance_compliance: float
    capacity_utilization: float


class ServicePerformanceAnalyzer:
    """Analyze performance across all Penske services"""
    
    def __init__(self, datasets: Dict[str, pd.DataFrame]):
        """
        Initialize with loaded datasets
        
        Args:
            datasets: Dictionary of dataframes from DataLoader
        """
        self.datasets = datasets
        self.metrics_cache = {}
        
    def calculate_overall_kpis(self) -> Dict[str, float]:
        """Calculate company-wide KPIs"""
        
        kpis = {}
        
        if 'delivery_performance' in self.datasets:
            df = self.datasets['delivery_performance']
            kpis['on_time_delivery_rate'] = df['on_time'].mean() * 100
            kpis['avg_delay_minutes'] = df[df['delay_minutes'] > 0]['delay_minutes'].mean()
            kpis['total_deliveries'] = len(df)
            kpis['total_revenue'] = df['revenue'].sum()
            kpis['avg_profit_margin'] = df['profit_margin'].mean() * 100
        
        if 'fleet_operations' in self.datasets:
            df = self.datasets['fleet_operations']
            kpis['fleet_utilization'] = df['load_capacity_used'].mean()
            kpis['avg_fuel_efficiency'] = df['miles_driven'].sum() / df['fuel_consumed'].sum()
            kpis['fleet_on_time_rate'] = df['on_time_rate'].mean() * 100
        
        if 'warehouse_metrics' in self.datasets:
            df = self.datasets['warehouse_metrics']
            kpis['warehouse_throughput_avg'] = df['throughput_units'].mean()
            kpis['inventory_accuracy'] = df['inventory_accuracy'].mean()
            kpis['order_fill_rate'] = df['order_fill_rate'].mean()
            kpis['dock_utilization'] = df['dock_utilization'].mean()
        
        if 'customer_data' in self.datasets:
            df = self.datasets['customer_data']
            kpis['customer_satisfaction_avg'] = df['satisfaction_score'].mean()
            kpis['customer_retention_rate'] = df['is_active'].mean() * 100
            kpis['avg_contract_value'] = df['contract_value'].mean()
        
        if 'maintenance_records' in self.datasets:
            df = self.datasets['maintenance_records']
            kpis['avg_maintenance_cost'] = df['cost'].mean()
            kpis['preventive_maintenance_rate'] = (df['maintenance_type'] == 'Preventive').mean() * 100
            kpis['avg_downtime_hours'] = df['downtime_hours'].mean()
        
        return kpis
    
    def analyze_by_region(self) -> pd.DataFrame:
        """Analyze performance metrics by region"""
        
        regional_metrics = []
        
        if 'delivery_performance' in self.datasets:
            df = self.datasets['delivery_performance']
            delivery_by_region = df.groupby('destination_region').agg({
                'on_time': 'mean',
                'revenue': 'sum',
                'profit_margin': 'mean',
                'delay_minutes': 'mean',
                'delivery_id': 'count'
            }).rename(columns={
                'on_time': 'on_time_rate',
                'delivery_id': 'total_deliveries'
            })
            regional_metrics.append(delivery_by_region)
        
        if 'warehouse_metrics' in self.datasets:
            df = self.datasets['warehouse_metrics']
            warehouse_by_region = df.groupby('region').agg({
                'throughput_units': 'mean',
                'order_fill_rate': 'mean',
                'inventory_accuracy': 'mean'
            })
            regional_metrics.append(warehouse_by_region)
        
        if 'fleet_operations' in self.datasets:
            df = self.datasets['fleet_operations']
            fleet_by_region = df.groupby('region').agg({
                'load_capacity_used': 'mean',
                'on_time_rate': 'mean',
                'miles_driven': 'sum'
            }).rename(columns={
                'load_capacity_used': 'fleet_utilization',
                'on_time_rate': 'fleet_on_time_rate'
            })
            regional_metrics.append(fleet_by_region)
        
        if regional_metrics:
            result = pd.concat(regional_metrics, axis=1)
            result = result.fillna(0)
            return result
        
        return pd.DataFrame()
    
    def analyze_by_service_type(self) -> pd.DataFrame:
        """Analyze performance by service type"""
        
        service_metrics = []
        
        if 'delivery_performance' in self.datasets:
            df = self.datasets['delivery_performance']
            delivery_by_service = df.groupby('service_type').agg({
                'on_time': 'mean',
                'revenue': ['sum', 'mean'],
                'profit_margin': 'mean',
                'weight_lbs': 'mean',
                'distance_miles': 'mean',
                'delivery_id': 'count'
            })
            delivery_by_service.columns = ['_'.join(col).strip() for col in delivery_by_service.columns]
            service_metrics.append(delivery_by_service)
        
        if 'fleet_operations' in self.datasets:
            df = self.datasets['fleet_operations']
            fleet_by_service = df.groupby('service_type').agg({
                'miles_driven': 'mean',
                'load_capacity_used': 'mean',
                'on_time_rate': 'mean',
                'fuel_consumed': 'mean'
            }).add_prefix('fleet_')
            service_metrics.append(fleet_by_service)
        
        if service_metrics:
            result = pd.concat(service_metrics, axis=1)
            return result
        
        return pd.DataFrame()
    
    def calculate_trend_analysis(self, metric: str, period: str = 'M') -> pd.DataFrame:
        """
        Calculate trends over time for a specific metric
        
        Args:
            metric: Metric to analyze
            period: Time period ('D', 'W', 'M', 'Q')
        """
        
        trend_data = []
        
        if metric in ['on_time_rate', 'revenue', 'profit_margin'] and 'delivery_performance' in self.datasets:
            df = self.datasets['delivery_performance'].copy()
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            
            if metric == 'on_time_rate':
                trend = df['on_time'].resample(period).mean() * 100
            else:
                trend = df[metric].resample(period).sum() if metric == 'revenue' else df[metric].resample(period).mean()
            
            trend_data = trend.reset_index()
            trend_data.columns = ['date', metric]
        
        elif metric in ['throughput', 'fill_rate'] and 'warehouse_metrics' in self.datasets:
            df = self.datasets['warehouse_metrics'].copy()
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            
            col_map = {'throughput': 'throughput_units', 'fill_rate': 'order_fill_rate'}
            trend = df[col_map[metric]].resample(period).mean()
            trend_data = trend.reset_index()
            trend_data.columns = ['date', metric]
        
        return pd.DataFrame(trend_data) if isinstance(trend_data, list) else trend_data
    
    def identify_underperforming_areas(self, threshold_pct: float = 20) -> Dict[str, List[str]]:
        """
        Identify areas performing below threshold compared to average
        
        Args:
            threshold_pct: Percentage below average to flag as underperforming
        """
        
        underperforming = {}
        
        regional = self.analyze_by_region()
        if not regional.empty:
            for col in regional.columns:
                avg = regional[col].mean()
                threshold = avg * (1 - threshold_pct / 100)
                below_avg = regional[regional[col] < threshold].index.tolist()
                if below_avg:
                    underperforming[f'region_{col}'] = below_avg
        
        if 'delivery_performance' in self.datasets:
            df = self.datasets['delivery_performance']
            driver_perf = df.groupby('driver_id').agg({
                'on_time': 'mean',
                'profit_margin': 'mean'
            })
            
            avg_on_time = driver_perf['on_time'].mean()
            low_performers = driver_perf[driver_perf['on_time'] < avg_on_time * 0.8].index.tolist()
            if low_performers:
                underperforming['low_performing_drivers'] = low_performers[:20]
        
        if 'warehouse_metrics' in self.datasets:
            df = self.datasets['warehouse_metrics']
            wh_perf = df.groupby('warehouse_id').agg({
                'order_fill_rate': 'mean',
                'throughput_units': 'mean'
            })
            
            avg_fill = wh_perf['order_fill_rate'].mean()
            low_wh = wh_perf[wh_perf['order_fill_rate'] < avg_fill * 0.85].index.tolist()
            if low_wh:
                underperforming['low_performing_warehouses'] = low_wh
        
        return underperforming
    
    def generate_performance_scorecard(self) -> pd.DataFrame:
        """Generate a comprehensive performance scorecard"""
        
        scorecard = []
        
        kpi_targets = {
            'on_time_delivery_rate': {'target': 95, 'weight': 0.20},
            'fleet_utilization': {'target': 85, 'weight': 0.15},
            'inventory_accuracy': {'target': 99, 'weight': 0.10},
            'order_fill_rate': {'target': 98, 'weight': 0.15},
            'customer_satisfaction_avg': {'target': 8.5, 'weight': 0.15},
            'customer_retention_rate': {'target': 90, 'weight': 0.10},
            'avg_profit_margin': {'target': 15, 'weight': 0.10},
            'preventive_maintenance_rate': {'target': 60, 'weight': 0.05}
        }
        
        actual_kpis = self.calculate_overall_kpis()
        
        for kpi, config in kpi_targets.items():
            actual = actual_kpis.get(kpi, 0)
            target = config['target']
            weight = config['weight']
            
            achievement = min(100, (actual / target) * 100) if target > 0 else 0
            weighted_score = achievement * weight
            
            if achievement >= 100:
                status = 'Exceeds'
            elif achievement >= 90:
                status = 'Meets'
            elif achievement >= 75:
                status = 'Below'
            else:
                status = 'Critical'
            
            scorecard.append({
                'KPI': kpi.replace('_', ' ').title(),
                'Target': target,
                'Actual': round(actual, 2),
                'Achievement %': round(achievement, 1),
                'Weight': weight,
                'Weighted Score': round(weighted_score, 2),
                'Status': status
            })
        
        df = pd.DataFrame(scorecard)
        df['Overall Score'] = df['Weighted Score'].sum()
        
        return df
    
    def get_executive_summary(self) -> Dict:
        """Generate executive summary of performance"""
        
        kpis = self.calculate_overall_kpis()
        scorecard = self.generate_performance_scorecard()
        underperforming = self.identify_underperforming_areas()
        
        overall_score = scorecard['Weighted Score'].sum()
        
        if overall_score >= 90:
            health_status = 'Excellent'
        elif overall_score >= 80:
            health_status = 'Good'
        elif overall_score >= 70:
            health_status = 'Fair'
        else:
            health_status = 'Needs Improvement'
        
        critical_kpis = scorecard[scorecard['Status'] == 'Critical']['KPI'].tolist()
        exceeding_kpis = scorecard[scorecard['Status'] == 'Exceeds']['KPI'].tolist()
        
        summary = {
            'overall_score': round(overall_score, 1),
            'health_status': health_status,
            'critical_areas': critical_kpis,
            'exceeding_areas': exceeding_kpis,
            'underperforming_count': sum(len(v) for v in underperforming.values()),
            'key_metrics': {
                'on_time_delivery': round(kpis.get('on_time_delivery_rate', 0), 1),
                'customer_satisfaction': round(kpis.get('customer_satisfaction_avg', 0), 1),
                'fleet_utilization': round(kpis.get('fleet_utilization', 0), 1),
                'profit_margin': round(kpis.get('avg_profit_margin', 0), 1)
            },
            'recommendations': self._generate_recommendations(scorecard, underperforming)
        }
        
        return summary
    
    def _generate_recommendations(self, scorecard: pd.DataFrame, underperforming: Dict) -> List[str]:
        """Generate actionable recommendations based on analysis"""
        
        recommendations = []
        
        critical = scorecard[scorecard['Status'] == 'Critical']
        for _, row in critical.iterrows():
            kpi = row['KPI']
            gap = row['Target'] - row['Actual']
            recommendations.append(f"PRIORITY: Improve {kpi} by {gap:.1f} to meet target")
        
        if 'low_performing_drivers' in underperforming:
            count = len(underperforming['low_performing_drivers'])
            recommendations.append(f"Review training needs for {count} underperforming drivers")
        
        if 'low_performing_warehouses' in underperforming:
            whs = underperforming['low_performing_warehouses']
            recommendations.append(f"Conduct operational review at warehouses: {', '.join(whs[:3])}")
        
        for key, regions in underperforming.items():
            if 'region' in key and regions:
                recommendations.append(f"Investigate performance issues in regions: {', '.join(regions[:3])}")
        
        return recommendations[:10]


if __name__ == '__main__':
    from src.data_prep import DataLoader
    
    loader = DataLoader(use_dummy=True)
    datasets = loader.load_all()
    
    analyzer = ServicePerformanceAnalyzer(datasets)
    
    print("\n=== Overall KPIs ===")
    kpis = analyzer.calculate_overall_kpis()
    for k, v in kpis.items():
        print(f"  {k}: {v:.2f}")
    
    print("\n=== Executive Summary ===")
    summary = analyzer.get_executive_summary()
    print(f"  Overall Score: {summary['overall_score']}")
    print(f"  Health Status: {summary['health_status']}")
    print(f"  Critical Areas: {summary['critical_areas']}")
    print(f"\n  Recommendations:")
    for rec in summary['recommendations']:
        print(f"    - {rec}")
