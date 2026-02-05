"""
Custom Data Loader - Load Your Own Data into the Penske Analytics Pipeline

This module provides a simple interface to load custom data from various sources
(CSV, Excel, JSON, databases) and adapt it to work with the existing analytics modules.

Usage:
    from src.custom_data_loader import CustomDataLoader
    
    loader = CustomDataLoader()
    datasets = loader.load_from_csv("path/to/your/data.csv", data_type="fleet")
    
    # Or load all data at once
    datasets = loader.load_all_from_folder("path/to/data/folder/")
"""

import os
import logging
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from datetime import datetime

import pandas as pd
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ColumnMapper:
    """
    Maps custom column names to expected schema.
    Allows flexible data loading without modifying source files.
    """
    
    # Expected column schemas for each data type
    EXPECTED_SCHEMAS = {
        'fleet_operations': [
            'vehicle_id', 'date', 'region', 'service_type', 'miles_driven',
            'fuel_consumed', 'load_capacity_used', 'driver_id', 
            'on_time_deliveries', 'total_deliveries', 'on_time_rate'
        ],
        'delivery_performance': [
            'delivery_id', 'date', 'origin', 'destination', 'region',
            'planned_delivery_time', 'actual_delivery_time', 'delay_minutes',
            'on_time', 'customer_id', 'service_type'
        ],
        'warehouse_metrics': [
            'warehouse_id', 'date', 'region', 'throughput_units', 'labor_hours',
            'inventory_accuracy', 'order_fill_rate', 'dock_utilization', 'cost_per_unit'
        ],
        'customer_data': [
            'customer_id', 'company_name', 'industry', 'region', 'annual_revenue',
            'contract_value', 'services_used', 'num_services', 'tenure_months',
            'satisfaction_score', 'is_active', 'shipment_frequency'
        ],
        'regional_demand': [
            'date', 'region', 'service_type', 'shipment_volume', 'revenue',
            'num_customers', 'avg_shipment_weight'
        ],
        'leads_data': [
            'lead_id', 'company_name', 'industry', 'region', 'annual_revenue',
            'num_locations', 'current_provider', 'lead_source', 'converted'
        ]
    }
    
    def __init__(self):
        self.mappings = {}
    
    def add_mapping(self, data_type: str, column_map: Dict[str, str]):
        """
        Add custom column mapping.
        
        Args:
            data_type: Type of data (e.g., 'fleet_operations')
            column_map: Dict mapping your columns to expected columns
                       e.g., {'your_truck_id': 'vehicle_id', 'your_area': 'region'}
        """
        self.mappings[data_type] = column_map
        logger.info(f"Added column mapping for {data_type}: {len(column_map)} columns")
    
    def apply_mapping(self, df: pd.DataFrame, data_type: str) -> pd.DataFrame:
        """Apply column mapping to DataFrame"""
        if data_type in self.mappings:
            df = df.rename(columns=self.mappings[data_type])
            logger.info(f"Applied column mapping for {data_type}")
        return df
    
    def validate_schema(self, df: pd.DataFrame, data_type: str) -> Dict[str, Any]:
        """
        Validate DataFrame against expected schema.
        
        Returns:
            Dict with validation results
        """
        if data_type not in self.EXPECTED_SCHEMAS:
            return {'valid': True, 'message': f'No schema defined for {data_type}'}
        
        expected = set(self.EXPECTED_SCHEMAS[data_type])
        actual = set(df.columns)
        
        missing = expected - actual
        extra = actual - expected
        
        return {
            'valid': len(missing) == 0,
            'missing_columns': list(missing),
            'extra_columns': list(extra),
            'matched_columns': list(expected & actual),
            'message': 'Schema valid' if len(missing) == 0 else f'Missing: {missing}'
        }
    
    def auto_detect_mapping(self, df: pd.DataFrame, data_type: str) -> Dict[str, str]:
        """
        Auto-detect column mappings based on similarity.
        Uses fuzzy matching to suggest mappings.
        """
        if data_type not in self.EXPECTED_SCHEMAS:
            return {}
        
        expected_cols = self.EXPECTED_SCHEMAS[data_type]
        actual_cols = list(df.columns)
        
        suggestions = {}
        
        for expected in expected_cols:
            # Try exact match first
            if expected in actual_cols:
                suggestions[expected] = expected
                continue
            
            # Try case-insensitive match
            for actual in actual_cols:
                if actual.lower() == expected.lower():
                    suggestions[actual] = expected
                    break
                # Try partial match
                if expected.replace('_', '') in actual.lower().replace('_', ''):
                    suggestions[actual] = expected
                    break
        
        return suggestions


class CustomDataLoader:
    """
    Load custom data from various sources and adapt to the analytics pipeline.
    
    Supports:
    - CSV files
    - Excel files (.xlsx, .xls)
    - JSON files
    - SQL databases (SQLite, PostgreSQL, MySQL)
    - Multiple files at once
    """
    
    def __init__(self, column_mapper: ColumnMapper = None):
        self.mapper = column_mapper or ColumnMapper()
        self.loaded_datasets = {}
        self.load_history = []
    
    def load_csv(self, filepath: str, data_type: str = None, 
                 column_mapping: Dict[str, str] = None,
                 **pandas_kwargs) -> pd.DataFrame:
        """
        Load data from CSV file.
        
        Args:
            filepath: Path to CSV file
            data_type: Type of data for schema validation
            column_mapping: Optional column name mapping
            **pandas_kwargs: Additional arguments for pd.read_csv
            
        Returns:
            DataFrame with loaded data
        """
        logger.info(f"Loading CSV: {filepath}")
        
        df = pd.read_csv(filepath, **pandas_kwargs)
        
        # Apply column mapping if provided
        if column_mapping:
            df = df.rename(columns=column_mapping)
        elif data_type:
            df = self.mapper.apply_mapping(df, data_type)
        
        # Validate schema if data_type provided
        if data_type:
            validation = self.mapper.validate_schema(df, data_type)
            if not validation['valid']:
                logger.warning(f"Schema validation: {validation['message']}")
        
        # Store and log
        if data_type:
            self.loaded_datasets[data_type] = df
        
        self._log_load(filepath, data_type, len(df))
        
        return df
    
    def load_excel(self, filepath: str, data_type: str = None,
                   sheet_name: Union[str, int] = 0,
                   column_mapping: Dict[str, str] = None,
                   **pandas_kwargs) -> pd.DataFrame:
        """
        Load data from Excel file.
        
        Args:
            filepath: Path to Excel file
            data_type: Type of data for schema validation
            sheet_name: Sheet name or index
            column_mapping: Optional column name mapping
            **pandas_kwargs: Additional arguments for pd.read_excel
            
        Returns:
            DataFrame with loaded data
        """
        logger.info(f"Loading Excel: {filepath} (sheet: {sheet_name})")
        
        df = pd.read_excel(filepath, sheet_name=sheet_name, **pandas_kwargs)
        
        if column_mapping:
            df = df.rename(columns=column_mapping)
        elif data_type:
            df = self.mapper.apply_mapping(df, data_type)
        
        if data_type:
            self.loaded_datasets[data_type] = df
        
        self._log_load(filepath, data_type, len(df))
        
        return df
    
    def load_json(self, filepath: str, data_type: str = None,
                  column_mapping: Dict[str, str] = None,
                  **pandas_kwargs) -> pd.DataFrame:
        """Load data from JSON file"""
        logger.info(f"Loading JSON: {filepath}")
        
        df = pd.read_json(filepath, **pandas_kwargs)
        
        if column_mapping:
            df = df.rename(columns=column_mapping)
        elif data_type:
            df = self.mapper.apply_mapping(df, data_type)
        
        if data_type:
            self.loaded_datasets[data_type] = df
        
        self._log_load(filepath, data_type, len(df))
        
        return df
    
    def load_from_database(self, connection_string: str, query: str,
                           data_type: str = None,
                           column_mapping: Dict[str, str] = None) -> pd.DataFrame:
        """
        Load data from SQL database.
        
        Args:
            connection_string: Database connection string
                - SQLite: "sqlite:///path/to/db.sqlite"
                - PostgreSQL: "postgresql://user:pass@host:port/db"
                - MySQL: "mysql://user:pass@host:port/db"
            query: SQL query to execute
            data_type: Type of data for schema validation
            column_mapping: Optional column name mapping
            
        Returns:
            DataFrame with loaded data
        """
        try:
            from sqlalchemy import create_engine
            
            logger.info(f"Loading from database: {connection_string[:30]}...")
            
            engine = create_engine(connection_string)
            df = pd.read_sql(query, engine)
            
            if column_mapping:
                df = df.rename(columns=column_mapping)
            elif data_type:
                df = self.mapper.apply_mapping(df, data_type)
            
            if data_type:
                self.loaded_datasets[data_type] = df
            
            self._log_load("database", data_type, len(df))
            
            return df
            
        except ImportError:
            logger.error("SQLAlchemy not installed. Run: pip install sqlalchemy")
            raise
    
    def load_folder(self, folder_path: str, 
                    file_type_mapping: Dict[str, str] = None) -> Dict[str, pd.DataFrame]:
        """
        Load all data files from a folder.
        
        Args:
            folder_path: Path to folder containing data files
            file_type_mapping: Dict mapping filenames to data types
                              e.g., {'fleet.csv': 'fleet_operations'}
                              
        Returns:
            Dict of DataFrames by data type
        """
        logger.info(f"Loading all files from: {folder_path}")
        
        folder = Path(folder_path)
        datasets = {}
        
        # Auto-detect data types from filenames if no mapping provided
        if file_type_mapping is None:
            file_type_mapping = {}
            for schema_type in self.mapper.EXPECTED_SCHEMAS.keys():
                # Look for files matching schema name
                for ext in ['.csv', '.xlsx', '.json']:
                    potential_file = folder / f"{schema_type}{ext}"
                    if potential_file.exists():
                        file_type_mapping[potential_file.name] = schema_type
        
        # Load each file
        for filename, data_type in file_type_mapping.items():
            filepath = folder / filename
            if not filepath.exists():
                logger.warning(f"File not found: {filepath}")
                continue
            
            ext = filepath.suffix.lower()
            
            if ext == '.csv':
                datasets[data_type] = self.load_csv(str(filepath), data_type)
            elif ext in ['.xlsx', '.xls']:
                datasets[data_type] = self.load_excel(str(filepath), data_type)
            elif ext == '.json':
                datasets[data_type] = self.load_json(str(filepath), data_type)
        
        self.loaded_datasets.update(datasets)
        logger.info(f"Loaded {len(datasets)} datasets from folder")
        
        return datasets
    
    def get_datasets(self) -> Dict[str, pd.DataFrame]:
        """Get all loaded datasets"""
        return self.loaded_datasets
    
    def get_dataset(self, data_type: str) -> Optional[pd.DataFrame]:
        """Get specific dataset by type"""
        return self.loaded_datasets.get(data_type)
    
    def _log_load(self, source: str, data_type: str, row_count: int):
        """Log data load event"""
        self.load_history.append({
            'timestamp': datetime.now().isoformat(),
            'source': source,
            'data_type': data_type,
            'row_count': row_count
        })
    
    def get_load_summary(self) -> pd.DataFrame:
        """Get summary of all data loads"""
        return pd.DataFrame(self.load_history)
    
    def validate_all(self) -> Dict[str, Dict]:
        """Validate all loaded datasets against schemas"""
        results = {}
        for data_type, df in self.loaded_datasets.items():
            results[data_type] = self.mapper.validate_schema(df, data_type)
        return results


class DataTypeConverter:
    """
    Converts data types and handles common data quality issues.
    """
    
    @staticmethod
    def convert_dates(df: pd.DataFrame, date_columns: List[str], 
                      date_format: str = None) -> pd.DataFrame:
        """Convert columns to datetime"""
        df = df.copy()
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], format=date_format, errors='coerce')
        return df
    
    @staticmethod
    def convert_numeric(df: pd.DataFrame, numeric_columns: List[str]) -> pd.DataFrame:
        """Convert columns to numeric"""
        df = df.copy()
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        return df
    
    @staticmethod
    def fill_missing(df: pd.DataFrame, 
                     fill_strategy: Dict[str, Any] = None) -> pd.DataFrame:
        """
        Fill missing values.
        
        Args:
            df: Input DataFrame
            fill_strategy: Dict mapping columns to fill values or strategies
                          e.g., {'region': 'Unknown', 'revenue': 'mean'}
        """
        df = df.copy()
        
        if fill_strategy:
            for col, strategy in fill_strategy.items():
                if col not in df.columns:
                    continue
                    
                if strategy == 'mean':
                    df[col] = df[col].fillna(df[col].mean())
                elif strategy == 'median':
                    df[col] = df[col].fillna(df[col].median())
                elif strategy == 'mode':
                    df[col] = df[col].fillna(df[col].mode().iloc[0] if len(df[col].mode()) > 0 else None)
                elif strategy == 'forward':
                    df[col] = df[col].fillna(method='ffill')
                elif strategy == 'backward':
                    df[col] = df[col].fillna(method='bfill')
                else:
                    df[col] = df[col].fillna(strategy)
        
        return df
    
    @staticmethod
    def standardize_categories(df: pd.DataFrame, 
                               category_mappings: Dict[str, Dict[str, str]]) -> pd.DataFrame:
        """
        Standardize category values.
        
        Args:
            df: Input DataFrame
            category_mappings: Dict mapping columns to value mappings
                              e.g., {'region': {'NY': 'Northeast', 'CA': 'West'}}
        """
        df = df.copy()
        
        for col, mapping in category_mappings.items():
            if col in df.columns:
                df[col] = df[col].replace(mapping)
        
        return df


# Convenience function for quick loading
def load_custom_data(source: str, data_type: str = None, 
                     column_mapping: Dict[str, str] = None) -> pd.DataFrame:
    """
    Quick function to load data from any source.
    
    Args:
        source: File path or database connection string
        data_type: Type of data (for schema validation)
        column_mapping: Optional column name mapping
        
    Returns:
        DataFrame with loaded data
    """
    loader = CustomDataLoader()
    
    if source.endswith('.csv'):
        return loader.load_csv(source, data_type, column_mapping)
    elif source.endswith(('.xlsx', '.xls')):
        return loader.load_excel(source, data_type, column_mapping)
    elif source.endswith('.json'):
        return loader.load_json(source, data_type, column_mapping)
    elif source.startswith(('sqlite', 'postgresql', 'mysql')):
        raise ValueError("Use load_from_database() for database connections")
    else:
        raise ValueError(f"Unsupported source format: {source}")


# Example usage template
USAGE_EXAMPLE = """
# ============================================
# EXAMPLE: Loading Your Custom Data
# ============================================

from src.custom_data_loader import CustomDataLoader, ColumnMapper

# Step 1: Create loader
loader = CustomDataLoader()

# Step 2: Define column mapping (if your columns differ)
my_mapping = {
    'truck_number': 'vehicle_id',
    'area': 'region',
    'delivery_success_rate': 'on_time_rate'
}

# Step 3: Load your data
fleet_df = loader.load_csv(
    'path/to/your/fleet_data.csv',
    data_type='fleet_operations',
    column_mapping=my_mapping
)

# Step 4: Load multiple files from folder
datasets = loader.load_folder(
    'path/to/data/folder/',
    file_type_mapping={
        'my_fleet.csv': 'fleet_operations',
        'my_customers.xlsx': 'customer_data',
        'demand_forecast.csv': 'regional_demand'
    }
)

# Step 5: Use with existing modules
from src.service_performance import ServicePerformanceAnalyzer
from src.rag_engine import LogisticsRAGEngine

analyzer = ServicePerformanceAnalyzer(datasets)
rag = LogisticsRAGEngine()
rag.ingest_fleet_data(datasets['fleet_operations'])

print("Your custom data is now in the analytics pipeline!")
"""

if __name__ == "__main__":
    print(USAGE_EXAMPLE)
