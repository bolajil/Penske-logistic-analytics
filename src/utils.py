"""
Utility Functions for Penske Logistics Analytics
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging
import json
from pathlib import Path

logger = logging.getLogger(__name__)


def setup_logging(log_level: str = 'INFO', log_file: str = None):
    """Configure logging for the application"""
    handlers = [logging.StreamHandler()]
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )


def calculate_mape(actual: np.ndarray, predicted: np.ndarray) -> float:
    """Calculate Mean Absolute Percentage Error"""
    mask = actual != 0
    return np.mean(np.abs((actual[mask] - predicted[mask]) / actual[mask])) * 100


def calculate_rmse(actual: np.ndarray, predicted: np.ndarray) -> float:
    """Calculate Root Mean Squared Error"""
    return np.sqrt(np.mean((actual - predicted) ** 2))


def format_currency(value: float, symbol: str = '$') -> str:
    """Format number as currency"""
    if abs(value) >= 1e9:
        return f"{symbol}{value/1e9:.1f}B"
    elif abs(value) >= 1e6:
        return f"{symbol}{value/1e6:.1f}M"
    elif abs(value) >= 1e3:
        return f"{symbol}{value/1e3:.1f}K"
    return f"{symbol}{value:,.2f}"


def format_percentage(value: float, decimals: int = 1) -> str:
    """Format number as percentage"""
    return f"{value:.{decimals}f}%"


def get_date_range(period: str = 'last_30_days') -> tuple:
    """Get date range based on period string"""
    today = datetime.now().date()
    periods = {
        'today': (today, today),
        'last_7_days': (today - timedelta(days=7), today),
        'last_30_days': (today - timedelta(days=30), today),
        'last_90_days': (today - timedelta(days=90), today),
        'mtd': (today.replace(day=1), today),
        'ytd': (today.replace(month=1, day=1), today)
    }
    return periods.get(period, periods['last_30_days'])


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers"""
    if denominator == 0:
        return default
    return numerator / denominator


def load_config(config_path: str) -> Dict:
    """Load configuration from JSON file"""
    path = Path(config_path)
    if not path.exists():
        return {}
    with open(path, 'r') as f:
        return json.load(f)
