"""
Dummy Data Generator for Penske Logistics Analytics
Generates realistic synthetic data for testing and development
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
from pathlib import Path

np.random.seed(42)

REGIONS = ['Northeast', 'Southeast', 'Midwest', 'Southwest', 'West', 'Northwest']
SERVICE_TYPES = [
    'Dedicated Contract Carriage',
    'Distribution Center Management', 
    'Transportation Management',
    'Supply Chain Solutions',
    'Fleet Maintenance',
    'Freight Management'
]
INDUSTRIES = [
    'Retail', 'Manufacturing', 'Food & Beverage', 'Healthcare',
    'Automotive', 'E-commerce', 'Consumer Goods', 'Technology'
]
MAINTENANCE_TYPES = ['Preventive', 'Corrective', 'Emergency', 'Scheduled']


def generate_fleet_operations(num_records: int = 10000) -> pd.DataFrame:
    """Generate fleet operations data"""
    
    start_date = datetime(2023, 1, 1)
    dates = [start_date + timedelta(days=np.random.randint(0, 730)) for _ in range(num_records)]
    
    data = {
        'vehicle_id': [f'VH-{np.random.randint(1000, 9999)}' for _ in range(num_records)],
        'date': dates,
        'region': np.random.choice(REGIONS, num_records),
        'service_type': np.random.choice(SERVICE_TYPES, num_records),
        'miles_driven': np.random.normal(450, 120, num_records).clip(50, 800),
        'fuel_consumed': None,
        'load_capacity_used': np.random.beta(5, 2, num_records) * 100,
        'driver_id': [f'DRV-{np.random.randint(100, 999)}' for _ in range(num_records)],
        'on_time_deliveries': None,
        'total_deliveries': np.random.poisson(8, num_records).clip(1, 20)
    }
    
    df = pd.DataFrame(data)
    df['fuel_consumed'] = df['miles_driven'] / np.random.uniform(6, 9, num_records)
    df['on_time_deliveries'] = (df['total_deliveries'] * np.random.beta(8, 2, num_records)).astype(int)
    df['on_time_rate'] = df['on_time_deliveries'] / df['total_deliveries']
    
    return df


def generate_warehouse_metrics(num_records: int = 5000) -> pd.DataFrame:
    """Generate warehouse performance metrics"""
    
    warehouses = [f'WH-{region[:2].upper()}-{i}' for region in REGIONS for i in range(1, 6)]
    start_date = datetime(2023, 1, 1)
    
    records = []
    for _ in range(num_records):
        wh = np.random.choice(warehouses)
        region = [r for r in REGIONS if r[:2].upper() in wh][0]
        date = start_date + timedelta(days=np.random.randint(0, 730))
        
        base_throughput = np.random.normal(5000, 1500)
        seasonality = 1 + 0.3 * np.sin(2 * np.pi * date.timetuple().tm_yday / 365)
        
        records.append({
            'warehouse_id': wh,
            'date': date,
            'region': region,
            'throughput_units': int(max(500, base_throughput * seasonality)),
            'labor_hours': np.random.normal(200, 50),
            'inventory_accuracy': np.random.beta(20, 1) * 100,
            'order_fill_rate': np.random.beta(15, 2) * 100,
            'dock_utilization': np.random.beta(6, 3) * 100,
            'cost_per_unit': np.random.uniform(1.5, 4.5)
        })
    
    return pd.DataFrame(records)


def generate_customer_data(num_customers: int = 500) -> pd.DataFrame:
    """Generate customer database with features for acquisition modeling"""
    
    records = []
    for i in range(num_customers):
        is_active = np.random.random() > 0.15
        tenure = np.random.exponential(24) if is_active else np.random.exponential(12)
        
        annual_revenue = np.random.lognormal(18, 1.5)
        contract_value = annual_revenue * np.random.uniform(0.001, 0.02)
        
        num_services = np.random.choice([1, 2, 3, 4], p=[0.4, 0.35, 0.2, 0.05])
        services = np.random.choice(SERVICE_TYPES, num_services, replace=False)
        
        records.append({
            'customer_id': f'CUST-{10000 + i}',
            'company_name': f'Company_{i}',
            'industry': np.random.choice(INDUSTRIES),
            'region': np.random.choice(REGIONS),
            'annual_revenue': annual_revenue,
            'contract_value': contract_value,
            'services_used': ','.join(services),
            'num_services': num_services,
            'tenure_months': int(tenure),
            'satisfaction_score': min(10, max(1, np.random.normal(7.5, 1.5))),
            'is_active': is_active,
            'shipment_frequency': np.random.choice(['Daily', 'Weekly', 'Monthly'], p=[0.3, 0.5, 0.2]),
            'avg_shipment_value': np.random.lognormal(8, 1),
            'payment_reliability': np.random.beta(10, 2) * 100,
            'growth_potential': np.random.choice(['High', 'Medium', 'Low'], p=[0.2, 0.5, 0.3])
        })
    
    return pd.DataFrame(records)


def generate_maintenance_records(num_records: int = 8000) -> pd.DataFrame:
    """Generate vehicle maintenance records"""
    
    vehicles = [f'VH-{np.random.randint(1000, 9999)}' for _ in range(200)]
    start_date = datetime(2023, 1, 1)
    
    records = []
    for _ in range(num_records):
        maint_type = np.random.choice(MAINTENANCE_TYPES, p=[0.5, 0.3, 0.1, 0.1])
        
        if maint_type == 'Preventive':
            cost = np.random.normal(500, 150)
            downtime = np.random.exponential(4)
        elif maint_type == 'Corrective':
            cost = np.random.normal(1200, 400)
            downtime = np.random.exponential(12)
        elif maint_type == 'Emergency':
            cost = np.random.normal(2500, 800)
            downtime = np.random.exponential(24)
        else:
            cost = np.random.normal(350, 100)
            downtime = np.random.exponential(2)
        
        parts = np.random.choice(
            ['Tires', 'Brakes', 'Oil Change', 'Transmission', 'Engine', 'Electrical', 'HVAC', 'Suspension'],
            size=np.random.randint(1, 4),
            replace=False
        )
        
        records.append({
            'maintenance_id': f'MNT-{100000 + _}',
            'vehicle_id': np.random.choice(vehicles),
            'date': start_date + timedelta(days=np.random.randint(0, 730)),
            'maintenance_type': maint_type,
            'cost': max(50, cost),
            'downtime_hours': max(1, downtime),
            'parts_replaced': ','.join(parts),
            'mileage_at_service': np.random.randint(10000, 500000),
            'technician_id': f'TECH-{np.random.randint(100, 200)}',
            'warranty_covered': np.random.random() > 0.7
        })
    
    return pd.DataFrame(records)


def generate_delivery_performance(num_records: int = 15000) -> pd.DataFrame:
    """Generate delivery performance records"""
    
    start_date = datetime(2023, 1, 1)
    
    records = []
    for i in range(num_records):
        date = start_date + timedelta(days=np.random.randint(0, 730))
        scheduled = date.replace(hour=np.random.randint(6, 20))
        
        delay_factor = np.random.exponential(0.5)
        if np.random.random() > 0.88:
            delay_minutes = int(delay_factor * 120)
        else:
            delay_minutes = int(np.random.normal(0, 15))
        
        actual = scheduled + timedelta(minutes=delay_minutes)
        
        service = np.random.choice(['LTL', 'FTL', 'Expedited', 'White Glove'], p=[0.4, 0.35, 0.15, 0.1])
        
        if service == 'LTL':
            weight = np.random.lognormal(6, 1)
        elif service == 'FTL':
            weight = np.random.normal(35000, 8000)
        else:
            weight = np.random.lognormal(5, 1.5)
        
        records.append({
            'delivery_id': f'DEL-{1000000 + i}',
            'date': date,
            'origin_region': np.random.choice(REGIONS),
            'destination_region': np.random.choice(REGIONS),
            'service_type': service,
            'scheduled_time': scheduled,
            'actual_time': actual,
            'delay_minutes': delay_minutes,
            'weight_lbs': max(10, weight),
            'customer_id': f'CUST-{np.random.randint(10000, 10500)}',
            'driver_id': f'DRV-{np.random.randint(100, 999)}',
            'distance_miles': np.random.lognormal(5, 1),
            'revenue': np.random.lognormal(6, 1),
            'cost': None,
            'on_time': delay_minutes <= 15
        })
    
    df = pd.DataFrame(records)
    df['cost'] = df['revenue'] * np.random.uniform(0.65, 0.85, len(df))
    df['profit_margin'] = (df['revenue'] - df['cost']) / df['revenue']
    
    return df


def generate_regional_demand(num_records: int = 4000) -> pd.DataFrame:
    """Generate regional demand forecasting data"""
    
    start_date = datetime(2023, 1, 1)
    
    records = []
    for _ in range(num_records):
        date = start_date + timedelta(days=np.random.randint(0, 730))
        region = np.random.choice(REGIONS)
        service = np.random.choice(SERVICE_TYPES)
        
        day_of_year = date.timetuple().tm_yday
        seasonality = 1 + 0.25 * np.sin(2 * np.pi * day_of_year / 365)
        
        if date.weekday() < 5:
            weekday_factor = 1.2
        else:
            weekday_factor = 0.6
        
        base_volume = np.random.normal(150, 40)
        volume = int(max(10, base_volume * seasonality * weekday_factor))
        
        records.append({
            'date': date,
            'region': region,
            'service_type': service,
            'shipment_volume': volume,
            'total_weight': volume * np.random.normal(2000, 500),
            'total_revenue': volume * np.random.lognormal(6, 0.5),
            'fleet_vehicles_available': np.random.randint(20, 100),
            'warehouse_capacity_used': np.random.beta(5, 3) * 100,
            'labor_available': np.random.randint(50, 200),
            'weather_impact': np.random.choice(['None', 'Minor', 'Moderate', 'Severe'], p=[0.7, 0.15, 0.1, 0.05]),
            'competitor_activity': np.random.choice(['Low', 'Normal', 'High'], p=[0.2, 0.6, 0.2])
        })
    
    return pd.DataFrame(records)


def generate_leads_data(num_leads: int = 1000) -> pd.DataFrame:
    """Generate sales leads for customer acquisition modeling"""
    
    records = []
    for i in range(num_leads):
        company_size = np.random.choice(['Small', 'Medium', 'Large', 'Enterprise'], p=[0.3, 0.4, 0.2, 0.1])
        
        if company_size == 'Enterprise':
            conversion_prob = 0.35
            revenue = np.random.lognormal(20, 0.5)
        elif company_size == 'Large':
            conversion_prob = 0.25
            revenue = np.random.lognormal(18, 0.8)
        elif company_size == 'Medium':
            conversion_prob = 0.18
            revenue = np.random.lognormal(16, 1)
        else:
            conversion_prob = 0.12
            revenue = np.random.lognormal(14, 1.2)
        
        engagement_score = np.random.beta(3, 5) * 100
        conversion_prob *= (0.5 + engagement_score / 100)
        converted = np.random.random() < conversion_prob
        
        records.append({
            'lead_id': f'LEAD-{20000 + i}',
            'company_name': f'Prospect_{i}',
            'industry': np.random.choice(INDUSTRIES),
            'company_size': company_size,
            'region': np.random.choice(REGIONS),
            'estimated_annual_revenue': revenue,
            'current_logistics_provider': np.random.choice(['Competitor A', 'Competitor B', 'In-house', 'Multiple', 'None']),
            'services_interested': ','.join(np.random.choice(SERVICE_TYPES, np.random.randint(1, 4), replace=False)),
            'lead_source': np.random.choice(['Website', 'Referral', 'Trade Show', 'Cold Call', 'Marketing Campaign']),
            'engagement_score': engagement_score,
            'days_in_pipeline': np.random.exponential(45),
            'num_interactions': np.random.poisson(5),
            'decision_maker_contact': np.random.random() > 0.4,
            'budget_confirmed': np.random.random() > 0.6,
            'converted': converted,
            'contract_value_if_converted': revenue * np.random.uniform(0.005, 0.015) if converted else 0
        })
    
    return pd.DataFrame(records)


def save_all_data(output_dir: str = None):
    """Generate and save all dummy data files"""
    
    if output_dir is None:
        output_dir = Path(__file__).parent.parent / 'data' / 'dummy_data'
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("Generating Penske Logistics dummy data...")
    
    datasets = {
        'fleet_operations.csv': generate_fleet_operations(),
        'warehouse_metrics.csv': generate_warehouse_metrics(),
        'customer_data.csv': generate_customer_data(),
        'maintenance_records.csv': generate_maintenance_records(),
        'delivery_performance.csv': generate_delivery_performance(),
        'regional_demand.csv': generate_regional_demand(),
        'sales_leads.csv': generate_leads_data()
    }
    
    for filename, df in datasets.items():
        filepath = output_dir / filename
        df.to_csv(filepath, index=False)
        print(f"  [OK] Generated {filename}: {len(df):,} records")
    
    print(f"\nAll data saved to: {output_dir}")
    return datasets


if __name__ == '__main__':
    save_all_data()
