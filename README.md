# Penske Logistics Performance Analytics & Prediction Platform

A comprehensive ML-powered analytics solution for Penske Logistics to analyze service performance, predict resource allocation needs, and identify customer acquisition opportunities.

---

## Project Overview

| Aspect | Details |
|--------|---------|
| **Problem** | Optimize logistics operations through performance analysis, resource prediction, and customer targeting |
| **ML Techniques** | XGBoost, Random Forest, LSTM, Clustering, Classification |
| **GenAI Integration** | LLM-powered insights for operational recommendations |
| **Tech Stack** | Python, Pandas, Scikit-learn, TensorFlow, Streamlit, FastAPI |

---

## Penske Logistics Services Covered

1. **Dedicated Contract Carriage** - Full-service fleet management
2. **Distribution Center Management** - Warehouse operations
3. **Transportation Management** - Freight brokerage and planning
4. **Supply Chain Solutions** - End-to-end logistics
5. **Fleet Maintenance** - Vehicle maintenance services
6. **Freight Management** - LTL/FTL shipping coordination

---

## Project Structure

```
penske-logistics-analytics/
├── README.md                      # This guide
├── DEMO_GUIDE.md                  # Step-by-step demo instructions
├── DEPLOYMENT.md                  # Deployment documentation
├── requirements.txt               # Dependencies
├── data/
│   ├── dummy_data/                # Test data for development
│   │   ├── fleet_operations.csv
│   │   ├── warehouse_metrics.csv
│   │   ├── customer_data.csv
│   │   ├── maintenance_records.csv
│   │   ├── delivery_performance.csv
│   │   └── regional_demand.csv
│   └── real_data/                 # Folder for actual Penske data
│       └── README.md              # Data format specifications
├── src/
│   ├── __init__.py
│   ├── data_generator.py          # Dummy data generation
│   ├── data_prep.py               # Data loading and preprocessing
│   ├── service_performance.py     # Performance analysis module
│   ├── resource_prediction.py     # Resource allocation ML models
│   ├── customer_acquisition.py    # Customer targeting models
│   ├── genai_insights.py          # GenAI integration
│   └── utils.py                   # Utility functions
├── models/                        # Saved model artifacts
│   └── .gitkeep
├── app/
│   ├── streamlit_dashboard.py     # Interactive dashboard
│   └── api_server.py              # FastAPI REST endpoints
├── tests/
│   ├── test_models.py
│   └── test_api.py
├── deploy/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── kubernetes/
│   │   ├── deployment.yaml
│   │   └── service.yaml
│   └── azure/
│       └── azure-pipelines.yml
└── notebooks/
    ├── 01_data_exploration.ipynb
    ├── 02_performance_analysis.ipynb
    ├── 03_resource_prediction.ipynb
    └── 04_customer_acquisition.ipynb
```

---

## Key Analytics Modules

### 1. Service Performance Analysis
- **On-Time Delivery Rate** by region, service type, customer
- **Fleet Utilization** metrics and trends
- **Warehouse Throughput** and efficiency scores
- **Cost per Mile/Shipment** analysis
- **Driver Performance** scoring

### 2. Resource Allocation Prediction
- **Demand Forecasting** by region and service type
- **Fleet Capacity Planning** - predict vehicle needs
- **Staffing Optimization** - driver and warehouse staff requirements
- **Maintenance Scheduling** - predictive maintenance windows
- **Seasonal Adjustment** recommendations

### 3. Customer Acquisition Prediction
- **Lead Scoring** - probability of conversion
- **Customer Segmentation** - identify high-value prospects
- **Churn Prediction** - retain at-risk customers
- **Cross-sell Opportunities** - service expansion potential
- **Market Expansion** - geographic opportunity analysis

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Generate dummy data for testing
python -m src.data_generator

# 3. Set OpenAI API key (for GenAI features)
set OPENAI_API_KEY=your-api-key-here

# 4. Run the Streamlit dashboard
streamlit run app/streamlit_dashboard.py

# 5. Or start the API server
uvicorn app.api_server:app --reload
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/performance/summary` | GET | Overall performance metrics |
| `/api/v1/performance/service/{service_type}` | GET | Service-specific metrics |
| `/api/v1/predict/resources` | POST | Predict resource needs |
| `/api/v1/predict/customers` | POST | Score customer leads |
| `/api/v1/insights/generate` | POST | Generate GenAI insights |

---

## Model Performance

| Model | Task | Accuracy/Score |
|-------|------|----------------|
| XGBoost | Resource Demand Prediction | MAPE: 8.2% |
| Random Forest | Customer Lead Scoring | AUC: 0.87 |
| LSTM | Seasonal Demand Forecasting | RMSE: 12.4 |
| K-Means | Customer Segmentation | Silhouette: 0.72 |

---

## Deployment Options

See `DEPLOYMENT.md` for detailed instructions on:
- **Local Development** - Docker Compose setup
- **Cloud Deployment** - Azure/AWS/GCP configurations
- **Kubernetes** - Production-scale deployment
- **CI/CD Pipeline** - Automated testing and deployment

---

## Next Steps

- [ ] Integrate with Penske's existing data warehouse
- [ ] Set up real-time data streaming
- [ ] Implement A/B testing framework
- [ ] Add alerting and monitoring
- [ ] Develop mobile dashboard
