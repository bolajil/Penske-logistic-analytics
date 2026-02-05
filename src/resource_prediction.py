"""
Resource Allocation Prediction Module for Penske Logistics
Predicts fleet, staffing, and capacity needs using ML models
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, mean_absolute_percentage_error
try:
    import xgboost as xgb
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False
    xgb = None
import joblib
from pathlib import Path
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class DemandForecaster:
    """Forecast demand for resources across regions and services"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.feature_importance = {}
        
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for demand forecasting"""
        
        df = df.copy()
        df['date'] = pd.to_datetime(df['date'])
        
        df['day_of_week'] = df['date'].dt.dayofweek
        df['month'] = df['date'].dt.month
        df['quarter'] = df['date'].dt.quarter
        df['week_of_year'] = df['date'].dt.isocalendar().week
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        df['is_month_end'] = df['date'].dt.is_month_end.astype(int)
        df['is_month_start'] = df['date'].dt.is_month_start.astype(int)
        
        day_of_year = df['date'].dt.dayofyear
        df['sin_day'] = np.sin(2 * np.pi * day_of_year / 365)
        df['cos_day'] = np.cos(2 * np.pi * day_of_year / 365)
        df['sin_week'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
        df['cos_week'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
        
        df = pd.get_dummies(df, columns=['region', 'service_type'], drop_first=True)
        
        weather_map = {'None': 0, 'Minor': 1, 'Moderate': 2, 'Severe': 3}
        if 'weather_impact' in df.columns:
            df['weather_impact_num'] = df['weather_impact'].map(weather_map)
        
        competitor_map = {'Low': 0, 'Normal': 1, 'High': 2}
        if 'competitor_activity' in df.columns:
            df['competitor_num'] = df['competitor_activity'].map(competitor_map)
        
        return df
    
    def create_lag_features(self, df: pd.DataFrame, target_col: str, lags: List[int] = [1, 7, 14, 30]) -> pd.DataFrame:
        """Create lag features for time series"""
        
        df = df.copy()
        df = df.sort_values('date')
        
        for lag in lags:
            df[f'{target_col}_lag_{lag}'] = df[target_col].shift(lag)
        
        for window in [7, 14, 30]:
            df[f'{target_col}_rolling_mean_{window}'] = df[target_col].rolling(window).mean()
            df[f'{target_col}_rolling_std_{window}'] = df[target_col].rolling(window).std()
        
        df = df.dropna()
        
        return df
    
    def train_demand_model(
        self, 
        df: pd.DataFrame, 
        target_col: str = 'shipment_volume',
        model_type: str = 'xgboost'
    ) -> Dict:
        """
        Train demand forecasting model
        
        Args:
            df: Prepared dataframe with features
            target_col: Column to predict
            model_type: 'xgboost', 'random_forest', or 'gradient_boosting'
        """
        
        df_prepared = self.prepare_features(df)
        df_prepared = self.create_lag_features(df_prepared, target_col)
        
        exclude_cols = ['date', target_col, 'weather_impact', 'competitor_activity']
        feature_cols = [c for c in df_prepared.columns if c not in exclude_cols]
        numeric_cols = df_prepared[feature_cols].select_dtypes(include=[np.number]).columns.tolist()
        
        X = df_prepared[numeric_cols]
        y = df_prepared[target_col]
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        if model_type == 'xgboost' and HAS_XGBOOST:
            model = xgb.XGBRegressor(
                n_estimators=200,
                max_depth=6,
                learning_rate=0.1,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42
            )
        elif model_type == 'xgboost' and not HAS_XGBOOST:
            logger.warning("XGBoost not installed, using GradientBoosting instead")
            model = GradientBoostingRegressor(
                n_estimators=200,
                max_depth=6,
                learning_rate=0.1,
                random_state=42
            )
        elif model_type == 'random_forest':
            model = RandomForestRegressor(
                n_estimators=200,
                max_depth=10,
                min_samples_split=5,
                random_state=42,
                n_jobs=-1
            )
        else:
            model = GradientBoostingRegressor(
                n_estimators=200,
                max_depth=6,
                learning_rate=0.1,
                random_state=42
            )
        
        model.fit(X_train_scaled, y_train)
        
        y_pred = model.predict(X_test_scaled)
        
        metrics = {
            'mae': mean_absolute_error(y_test, y_pred),
            'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
            'mape': mean_absolute_percentage_error(y_test, y_pred) * 100
        }
        
        cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5, scoring='neg_mean_absolute_error')
        metrics['cv_mae_mean'] = -cv_scores.mean()
        metrics['cv_mae_std'] = cv_scores.std()
        
        if hasattr(model, 'feature_importances_'):
            importance = dict(zip(numeric_cols, model.feature_importances_))
            self.feature_importance[target_col] = dict(sorted(importance.items(), key=lambda x: x[1], reverse=True)[:15])
        
        self.models[target_col] = model
        self.scalers[target_col] = scaler
        
        logger.info(f"Model trained for {target_col}: MAE={metrics['mae']:.2f}, MAPE={metrics['mape']:.2f}%")
        
        return {
            'metrics': metrics,
            'feature_importance': self.feature_importance.get(target_col, {}),
            'feature_columns': numeric_cols
        }
    
    def predict_demand(
        self, 
        df: pd.DataFrame, 
        target_col: str,
        forecast_horizon: int = 30
    ) -> pd.DataFrame:
        """
        Generate demand predictions
        
        Args:
            df: Historical data
            target_col: Target variable
            forecast_horizon: Days to forecast
        """
        
        if target_col not in self.models:
            raise ValueError(f"No model trained for {target_col}. Call train_demand_model first.")
        
        model = self.models[target_col]
        scaler = self.scalers[target_col]
        
        last_date = pd.to_datetime(df['date']).max()
        future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=forecast_horizon)
        
        predictions = []
        df_temp = df.copy()
        
        for future_date in future_dates:
            future_row = {
                'date': future_date,
                'region': df['region'].mode()[0],
                'service_type': df['service_type'].mode()[0],
                target_col: df_temp[target_col].iloc[-1]
            }
            
            for col in ['weather_impact', 'competitor_activity', 'fleet_vehicles_available', 
                       'warehouse_capacity_used', 'labor_available']:
                if col in df.columns:
                    future_row[col] = df[col].median()
            
            df_temp = pd.concat([df_temp, pd.DataFrame([future_row])], ignore_index=True)
            
            df_prepared = self.prepare_features(df_temp.tail(50))
            df_prepared = self.create_lag_features(df_prepared, target_col)
            
            if len(df_prepared) == 0:
                continue
                
            last_row = df_prepared.iloc[[-1]]
            exclude_cols = ['date', target_col, 'weather_impact', 'competitor_activity']
            feature_cols = [c for c in last_row.columns if c not in exclude_cols]
            numeric_cols = last_row[feature_cols].select_dtypes(include=[np.number]).columns.tolist()
            
            X_pred = last_row[numeric_cols].values
            X_pred_scaled = scaler.transform(X_pred)
            
            pred = model.predict(X_pred_scaled)[0]
            df_temp.iloc[-1, df_temp.columns.get_loc(target_col)] = pred
            
            predictions.append({
                'date': future_date,
                'predicted_demand': max(0, pred),
                'lower_bound': max(0, pred * 0.85),
                'upper_bound': pred * 1.15
            })
        
        return pd.DataFrame(predictions)
    
    def save_model(self, target_col: str, path: str):
        """Save trained model to disk"""
        
        model_data = {
            'model': self.models[target_col],
            'scaler': self.scalers[target_col],
            'feature_importance': self.feature_importance.get(target_col, {})
        }
        joblib.dump(model_data, path)
        logger.info(f"Model saved to {path}")
    
    def load_model(self, target_col: str, path: str):
        """Load model from disk"""
        
        model_data = joblib.load(path)
        self.models[target_col] = model_data['model']
        self.scalers[target_col] = model_data['scaler']
        self.feature_importance[target_col] = model_data.get('feature_importance', {})
        logger.info(f"Model loaded from {path}")


class ResourceOptimizer:
    """Optimize resource allocation based on demand forecasts"""
    
    def __init__(self, demand_forecaster: DemandForecaster = None):
        self.forecaster = demand_forecaster or DemandForecaster()
        
    def calculate_fleet_needs(
        self, 
        predicted_demand: pd.DataFrame,
        avg_capacity_per_vehicle: float = 15,
        utilization_target: float = 0.85
    ) -> pd.DataFrame:
        """
        Calculate fleet requirements based on demand forecast
        
        Args:
            predicted_demand: Demand predictions
            avg_capacity_per_vehicle: Average shipments per vehicle
            utilization_target: Target utilization rate
        """
        
        df = predicted_demand.copy()
        
        df['vehicles_needed'] = np.ceil(
            df['predicted_demand'] / (avg_capacity_per_vehicle * utilization_target)
        )
        
        df['vehicles_upper'] = np.ceil(
            df['upper_bound'] / (avg_capacity_per_vehicle * utilization_target)
        )
        
        df['buffer_vehicles'] = df['vehicles_upper'] - df['vehicles_needed']
        
        return df
    
    def calculate_staffing_needs(
        self,
        warehouse_throughput: pd.DataFrame,
        units_per_labor_hour: float = 25,
        shift_hours: float = 8
    ) -> pd.DataFrame:
        """
        Calculate warehouse staffing requirements
        
        Args:
            warehouse_throughput: Predicted throughput
            units_per_labor_hour: Productivity rate
            shift_hours: Hours per shift
        """
        
        df = warehouse_throughput.copy()
        
        if 'predicted_demand' in df.columns:
            df['labor_hours_needed'] = df['predicted_demand'] / units_per_labor_hour
        elif 'throughput_units' in df.columns:
            df['labor_hours_needed'] = df['throughput_units'] / units_per_labor_hour
        
        df['staff_per_shift'] = np.ceil(df['labor_hours_needed'] / shift_hours)
        
        df['overtime_hours'] = np.maximum(0, df['labor_hours_needed'] - df['staff_per_shift'] * shift_hours)
        
        return df
    
    def optimize_maintenance_schedule(
        self,
        fleet_data: pd.DataFrame,
        maintenance_data: pd.DataFrame,
        forecast_days: int = 30
    ) -> pd.DataFrame:
        """
        Predict maintenance needs and optimize scheduling
        """
        
        vehicle_stats = fleet_data.groupby('vehicle_id').agg({
            'miles_driven': 'sum',
            'date': 'max'
        }).reset_index()
        
        last_maintenance = maintenance_data.groupby('vehicle_id').agg({
            'mileage_at_service': 'max',
            'date': 'max'
        }).reset_index()
        last_maintenance.columns = ['vehicle_id', 'last_service_mileage', 'last_service_date']
        
        vehicle_status = vehicle_stats.merge(last_maintenance, on='vehicle_id', how='left')
        
        vehicle_status['miles_since_service'] = vehicle_status['miles_driven'] - vehicle_status['last_service_mileage'].fillna(0)
        
        vehicle_status['days_since_service'] = (
            pd.to_datetime(vehicle_status['date']) - pd.to_datetime(vehicle_status['last_service_date'])
        ).dt.days.fillna(90)
        
        vehicle_status['maintenance_urgency'] = (
            vehicle_status['miles_since_service'] / 15000 * 50 +
            vehicle_status['days_since_service'] / 90 * 50
        ).clip(0, 100)
        
        vehicle_status['recommended_service_date'] = pd.to_datetime(vehicle_status['date']) + pd.to_timedelta(
            np.maximum(1, (100 - vehicle_status['maintenance_urgency']) / 100 * forecast_days), unit='D'
        )
        
        vehicle_status['priority'] = pd.cut(
            vehicle_status['maintenance_urgency'],
            bins=[0, 30, 60, 80, 100],
            labels=['Low', 'Medium', 'High', 'Critical']
        )
        
        return vehicle_status.sort_values('maintenance_urgency', ascending=False)
    
    def generate_resource_plan(
        self,
        regional_demand: pd.DataFrame,
        fleet_data: pd.DataFrame,
        warehouse_data: pd.DataFrame
    ) -> Dict:
        """Generate comprehensive resource allocation plan"""
        
        plan = {
            'generated_at': datetime.now().isoformat(),
            'forecast_period': '30 days',
            'regions': {}
        }
        
        for region in regional_demand['region'].unique():
            region_data = regional_demand[regional_demand['region'] == region]
            
            avg_demand = region_data['shipment_volume'].mean()
            peak_demand = region_data['shipment_volume'].max()
            
            region_fleet = fleet_data[fleet_data['region'] == region] if 'region' in fleet_data.columns else fleet_data
            current_vehicles = region_fleet['vehicle_id'].nunique() if len(region_fleet) > 0 else 0
            
            region_wh = warehouse_data[warehouse_data['region'] == region] if 'region' in warehouse_data.columns else warehouse_data
            avg_throughput = region_wh['throughput_units'].mean() if len(region_wh) > 0 else 0
            
            vehicles_needed = int(np.ceil(peak_demand / 12))
            vehicle_gap = vehicles_needed - current_vehicles
            
            staff_needed = int(np.ceil(avg_throughput / 25 / 8))
            
            plan['regions'][region] = {
                'demand': {
                    'average': round(avg_demand, 0),
                    'peak': round(peak_demand, 0),
                    'trend': 'increasing' if region_data['shipment_volume'].iloc[-5:].mean() > avg_demand else 'stable'
                },
                'fleet': {
                    'current_vehicles': current_vehicles,
                    'vehicles_needed': vehicles_needed,
                    'gap': vehicle_gap,
                    'recommendation': 'Add vehicles' if vehicle_gap > 0 else 'Adequate'
                },
                'staffing': {
                    'staff_per_shift_needed': staff_needed,
                    'recommendation': 'Review staffing levels'
                },
                'warehouse': {
                    'avg_throughput': round(avg_throughput, 0),
                    'capacity_status': 'Normal'
                }
            }
        
        return plan


if __name__ == '__main__':
    from src.data_prep import DataLoader
    
    loader = DataLoader(use_dummy=True)
    datasets = loader.load_all()
    
    forecaster = DemandForecaster()
    
    print("\n=== Training Demand Forecasting Model ===")
    results = forecaster.train_demand_model(
        datasets['regional_demand'],
        target_col='shipment_volume',
        model_type='xgboost'
    )
    
    print(f"\nModel Metrics:")
    print(f"  MAE: {results['metrics']['mae']:.2f}")
    print(f"  RMSE: {results['metrics']['rmse']:.2f}")
    print(f"  MAPE: {results['metrics']['mape']:.2f}%")
    
    print(f"\nTop Feature Importance:")
    for feat, imp in list(results['feature_importance'].items())[:5]:
        print(f"  {feat}: {imp:.4f}")
    
    print("\n=== Generating Resource Plan ===")
    optimizer = ResourceOptimizer(forecaster)
    plan = optimizer.generate_resource_plan(
        datasets['regional_demand'],
        datasets['fleet_operations'],
        datasets['warehouse_metrics']
    )
    
    for region, details in list(plan['regions'].items())[:2]:
        print(f"\n{region}:")
        print(f"  Demand - Avg: {details['demand']['average']}, Peak: {details['demand']['peak']}")
        print(f"  Fleet - Current: {details['fleet']['current_vehicles']}, Needed: {details['fleet']['vehicles_needed']}")
        print(f"  Recommendation: {details['fleet']['recommendation']}")
