"""
Data Preparation Module for Penske Logistics Analytics
Handles data loading, validation, and preprocessing
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Optional, Tuple, List
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataLoader:
    """Load and validate Penske Logistics data"""
    
    REQUIRED_FILES = [
        'fleet_operations.csv',
        'warehouse_metrics.csv', 
        'customer_data.csv',
        'maintenance_records.csv',
        'delivery_performance.csv',
        'regional_demand.csv'
    ]
    
    def __init__(self, data_dir: str = None, use_dummy: bool = True):
        """
        Initialize data loader
        
        Args:
            data_dir: Path to data directory
            use_dummy: If True, use dummy_data folder; else use real_data
        """
        if data_dir is None:
            base_dir = Path(__file__).parent.parent / 'data'
            self.data_dir = base_dir / ('dummy_data' if use_dummy else 'real_data')
        else:
            self.data_dir = Path(data_dir)
        
        self.datasets: Dict[str, pd.DataFrame] = {}
        
    def load_all(self) -> Dict[str, pd.DataFrame]:
        """Load all available data files"""
        
        for file in self.REQUIRED_FILES:
            filepath = self.data_dir / file
            if filepath.exists():
                name = file.replace('.csv', '')
                self.datasets[name] = pd.read_csv(filepath, parse_dates=True)
                logger.info(f"Loaded {name}: {len(self.datasets[name]):,} records")
        
        if 'sales_leads' not in self.datasets:
            leads_path = self.data_dir / 'sales_leads.csv'
            if leads_path.exists():
                self.datasets['sales_leads'] = pd.read_csv(leads_path)
                logger.info(f"Loaded sales_leads: {len(self.datasets['sales_leads']):,} records")
        
        return self.datasets
    
    def validate_data(self) -> Dict[str, List[str]]:
        """Validate loaded data for quality issues"""
        
        issues = {}
        
        for name, df in self.datasets.items():
            dataset_issues = []
            
            null_pct = (df.isnull().sum() / len(df) * 100)
            high_null_cols = null_pct[null_pct > 5].index.tolist()
            if high_null_cols:
                dataset_issues.append(f"High null rate in columns: {high_null_cols}")
            
            if len(df) != len(df.drop_duplicates()):
                dup_count = len(df) - len(df.drop_duplicates())
                dataset_issues.append(f"Found {dup_count} duplicate rows")
            
            for col in df.select_dtypes(include=[np.number]).columns:
                q1, q3 = df[col].quantile([0.25, 0.75])
                iqr = q3 - q1
                outliers = ((df[col] < q1 - 3*iqr) | (df[col] > q3 + 3*iqr)).sum()
                if outliers > len(df) * 0.01:
                    dataset_issues.append(f"Column {col} has {outliers} outliers")
            
            if dataset_issues:
                issues[name] = dataset_issues
        
        return issues
    
    def get_dataset(self, name: str) -> Optional[pd.DataFrame]:
        """Get a specific dataset by name"""
        return self.datasets.get(name)


class DataPreprocessor:
    """Preprocess data for ML models"""
    
    def __init__(self):
        self.scalers = {}
        self.encoders = {}
        
    def preprocess_fleet_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Preprocess fleet operations data"""
        
        df = df.copy()
        
        df['date'] = pd.to_datetime(df['date'])
        df['day_of_week'] = df['date'].dt.dayofweek
        df['month'] = df['date'].dt.month
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        df['quarter'] = df['date'].dt.quarter
        
        df['fuel_efficiency'] = df['miles_driven'] / df['fuel_consumed'].replace(0, np.nan)
        df['delivery_efficiency'] = df['on_time_deliveries'] / df['total_deliveries'].replace(0, np.nan)
        
        df = pd.get_dummies(df, columns=['region', 'service_type'], prefix=['region', 'service'])
        
        return df
    
    def preprocess_warehouse_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Preprocess warehouse metrics data"""
        
        df = df.copy()
        
        df['date'] = pd.to_datetime(df['date'])
        df['day_of_week'] = df['date'].dt.dayofweek
        df['month'] = df['date'].dt.month
        
        df['units_per_labor_hour'] = df['throughput_units'] / df['labor_hours'].replace(0, np.nan)
        df['efficiency_score'] = (
            df['order_fill_rate'] * 0.4 + 
            df['inventory_accuracy'] * 0.3 + 
            df['dock_utilization'] * 0.3
        )
        
        return df
    
    def preprocess_customer_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Preprocess customer data for modeling"""
        
        df = df.copy()
        
        df['revenue_per_service'] = df['contract_value'] / df['num_services'].replace(0, np.nan)
        df['customer_lifetime_value'] = df['contract_value'] * df['tenure_months'] / 12
        
        df['revenue_quartile'] = pd.qcut(df['annual_revenue'], 4, labels=['Q1', 'Q2', 'Q3', 'Q4'])
        
        df = pd.get_dummies(df, columns=['industry', 'region', 'shipment_frequency', 'growth_potential'])
        
        return df
    
    def preprocess_delivery_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Preprocess delivery performance data"""
        
        df = df.copy()
        
        df['date'] = pd.to_datetime(df['date'])
        df['scheduled_time'] = pd.to_datetime(df['scheduled_time'])
        df['actual_time'] = pd.to_datetime(df['actual_time'])
        
        df['hour_of_day'] = df['scheduled_time'].dt.hour
        df['day_of_week'] = df['date'].dt.dayofweek
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        
        df['is_same_region'] = (df['origin_region'] == df['destination_region']).astype(int)
        df['revenue_per_mile'] = df['revenue'] / df['distance_miles'].replace(0, np.nan)
        df['weight_category'] = pd.cut(df['weight_lbs'], bins=[0, 100, 1000, 10000, 50000], 
                                       labels=['Light', 'Medium', 'Heavy', 'Full Load'])
        
        return df
    
    def preprocess_leads_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Preprocess sales leads for conversion prediction"""
        
        df = df.copy()
        
        df['num_services_interested'] = df['services_interested'].str.count(',') + 1
        df['has_decision_maker'] = df['decision_maker_contact'].astype(int)
        df['has_budget'] = df['budget_confirmed'].astype(int)
        
        df['lead_quality_score'] = (
            df['engagement_score'] * 0.3 +
            df['has_decision_maker'] * 30 +
            df['has_budget'] * 25 +
            df['num_interactions'] * 2
        ).clip(0, 100)
        
        df = pd.get_dummies(df, columns=['industry', 'company_size', 'region', 'lead_source'])
        
        return df
    
    def create_time_features(self, df: pd.DataFrame, date_col: str) -> pd.DataFrame:
        """Create comprehensive time-based features"""
        
        df = df.copy()
        df[date_col] = pd.to_datetime(df[date_col])
        
        df['year'] = df[date_col].dt.year
        df['month'] = df[date_col].dt.month
        df['day'] = df[date_col].dt.day
        df['day_of_week'] = df[date_col].dt.dayofweek
        df['week_of_year'] = df[date_col].dt.isocalendar().week
        df['quarter'] = df[date_col].dt.quarter
        df['is_month_start'] = df[date_col].dt.is_month_start.astype(int)
        df['is_month_end'] = df[date_col].dt.is_month_end.astype(int)
        
        day_of_year = df[date_col].dt.dayofyear
        df['sin_day'] = np.sin(2 * np.pi * day_of_year / 365)
        df['cos_day'] = np.cos(2 * np.pi * day_of_year / 365)
        
        return df


def prepare_training_data(
    df: pd.DataFrame, 
    target_col: str,
    test_size: float = 0.2,
    time_col: str = None
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """
    Prepare data for model training with train/test split
    
    Args:
        df: Input dataframe
        target_col: Name of target column
        test_size: Fraction for test set
        time_col: If provided, do time-based split instead of random
    
    Returns:
        X_train, X_test, y_train, y_test
    """
    from sklearn.model_selection import train_test_split
    
    feature_cols = [c for c in df.columns if c != target_col]
    if time_col and time_col in feature_cols:
        feature_cols.remove(time_col)
    
    numeric_cols = df[feature_cols].select_dtypes(include=[np.number]).columns.tolist()
    
    X = df[numeric_cols]
    y = df[target_col]
    
    if time_col:
        df_sorted = df.sort_values(time_col)
        split_idx = int(len(df_sorted) * (1 - test_size))
        X_train = df_sorted[numeric_cols].iloc[:split_idx]
        X_test = df_sorted[numeric_cols].iloc[split_idx:]
        y_train = df_sorted[target_col].iloc[:split_idx]
        y_test = df_sorted[target_col].iloc[split_idx:]
    else:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
    
    return X_train, X_test, y_train, y_test


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Penske Data Preparation')
    parser.add_argument('--validate', action='store_true', help='Validate data files')
    parser.add_argument('--path', type=str, help='Path to data directory')
    args = parser.parse_args()
    
    loader = DataLoader(data_dir=args.path, use_dummy=args.path is None)
    datasets = loader.load_all()
    
    if args.validate:
        issues = loader.validate_data()
        if issues:
            print("\nData Quality Issues Found:")
            for name, issue_list in issues.items():
                print(f"\n{name}:")
                for issue in issue_list:
                    print(f"  - {issue}")
        else:
            print("\n✓ All data validation checks passed!")
