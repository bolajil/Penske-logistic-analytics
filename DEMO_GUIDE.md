# Penske Logistics Analytics - Demo Guide

Step-by-step guide to demonstrate the analytics platform capabilities.

---

## Prerequisites

```bash
# 1. Navigate to project directory
cd penske-logistics-analytics

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Generate dummy data
python -m src.data_generator
```

---

## Demo Flow

### Part 1: Data Overview (5 minutes)

**Show the generated data:**
```bash
# Check generated files
dir data\dummy_data
```

**Expected output:**
- `fleet_operations.csv` - 10,000 records
- `warehouse_metrics.csv` - 5,000 records
- `customer_data.csv` - 500 records
- `maintenance_records.csv` - 8,000 records
- `delivery_performance.csv` - 15,000 records
- `regional_demand.csv` - 4,000 records
- `sales_leads.csv` - 1,000 records

---

### Part 2: Performance Analysis (10 minutes)

**Run the performance analyzer:**
```python
from src.data_prep import DataLoader
from src.service_performance import ServicePerformanceAnalyzer

# Load data
loader = DataLoader(use_dummy=True)
datasets = loader.load_all()

# Initialize analyzer
analyzer = ServicePerformanceAnalyzer(datasets)

# Get KPIs
kpis = analyzer.calculate_overall_kpis()
print("=== Key Performance Indicators ===")
for k, v in kpis.items():
    print(f"  {k}: {v:.2f}")

# Get executive summary
summary = analyzer.get_executive_summary()
print(f"\nOverall Score: {summary['overall_score']}/100")
print(f"Health Status: {summary['health_status']}")

# Show recommendations
print("\nRecommendations:")
for rec in summary['recommendations'][:5]:
    print(f"  - {rec}")
```

**Key talking points:**
- On-time delivery rate vs 95% target
- Fleet utilization efficiency
- Regional performance variations
- Actionable recommendations

---

### Part 3: Resource Prediction (10 minutes)

**Demonstrate demand forecasting:**
```python
from src.resource_prediction import DemandForecaster, ResourceOptimizer

# Train demand model
forecaster = DemandForecaster()
results = forecaster.train_demand_model(
    datasets['regional_demand'],
    target_col='shipment_volume',
    model_type='xgboost'
)

print(f"Model Performance:")
print(f"  MAE: {results['metrics']['mae']:.2f}")
print(f"  MAPE: {results['metrics']['mape']:.2f}%")

print(f"\nTop Predictive Features:")
for feat, imp in list(results['feature_importance'].items())[:5]:
    print(f"  {feat}: {imp:.4f}")

# Generate resource plan
optimizer = ResourceOptimizer(forecaster)
plan = optimizer.generate_resource_plan(
    datasets['regional_demand'],
    datasets['fleet_operations'],
    datasets['warehouse_metrics']
)

print("\n=== Resource Allocation Plan ===")
for region, details in plan['regions'].items():
    print(f"\n{region}:")
    print(f"  Demand - Avg: {details['demand']['average']}, Peak: {details['demand']['peak']}")
    print(f"  Fleet Gap: {details['fleet']['gap']} vehicles")
    print(f"  Recommendation: {details['fleet']['recommendation']}")
```

---

### Part 4: Customer Intelligence (10 minutes)

**Lead Scoring Demo:**
```python
from src.customer_acquisition import LeadScorer, ChurnPredictor, CustomerSegmenter

# Train lead scoring model
scorer = LeadScorer()
results = scorer.train(datasets['sales_leads'])

print("=== Lead Scoring Model ===")
print(f"AUC-ROC: {results['metrics']['auc_roc']:.3f}")
print(f"Precision: {results['metrics']['precision']:.3f}")
print(f"Recall: {results['metrics']['recall']:.3f}")

# Score leads
scored_leads = scorer.score_leads(datasets['sales_leads'])
print("\nTop 5 Leads:")
print(scored_leads[['company_name', 'lead_score', 'priority']].head())
```

**Churn Prediction Demo:**
```python
# Train churn model
churn_predictor = ChurnPredictor()
results = churn_predictor.train(datasets['customer_data'])

print("\n=== Churn Prediction Model ===")
print(f"AUC-ROC: {results['metrics']['auc_roc']:.3f}")

# Get at-risk customers
churn_risks = churn_predictor.predict_churn_risk(datasets['customer_data'])
high_risk = churn_risks[churn_risks['risk_level'].isin(['High', 'Critical'])]

print(f"\nHigh-Risk Customers: {len(high_risk)}")
print(f"Revenue at Risk: ${high_risk['revenue_at_risk'].sum():,.0f}")
```

**Customer Segmentation:**
```python
# Segment customers
segmenter = CustomerSegmenter(n_segments=5)
results = segmenter.fit_segments(datasets['customer_data'])

print("\n=== Customer Segments ===")
for seg_id, profile in results['segment_profiles'].items():
    print(f"\n{profile['name']}:")
    print(f"  Count: {profile['count']} ({profile['pct_of_total']:.1f}%)")
    print(f"  Avg Contract: ${profile['avg_contract_value']:,.0f}")
```

---

### Part 5: Interactive Dashboard (10 minutes)

**Launch Streamlit Dashboard:**
```bash
streamlit run app/streamlit_dashboard.py
```

**Dashboard walkthrough:**
1. **Executive Dashboard** - Overall KPIs and scorecard
2. **Fleet Operations** - Vehicle utilization and maintenance
3. **Warehouse Analytics** - Throughput and efficiency
4. **Customer Intelligence** - Lead scoring, churn, segmentation
5. **Demand Forecasting** - Trends and predictions
6. **AI Insights** - Natural language analysis

---

### Part 6: API Demo (5 minutes)

**Start API Server:**
```bash
uvicorn app.api_server:app --reload
```

**Test endpoints:**
```bash
# Health check
curl http://localhost:8000/

# Get performance summary
curl http://localhost:8000/api/v1/performance/summary

# Get alerts
curl http://localhost:8000/api/v1/alerts

# Generate insights
curl -X POST http://localhost:8000/api/v1/insights/generate \
  -H "Content-Type: application/json" \
  -d '{"insight_type": "performance"}'
```

**API Documentation:**
- Open http://localhost:8000/docs for Swagger UI

---

## Using Real Data

To switch from dummy data to real Penske data:

1. **Place data files** in `data/real_data/` following the format in `data/real_data/README.md`

2. **Update code** to use real data:
```python
loader = DataLoader(use_dummy=False)  # Changed from True
datasets = loader.load_all()
```

3. **Validate data:**
```bash
python -m src.data_prep --validate --path data/real_data/
```

---

## Key Metrics to Highlight

| Metric | Dummy Data Value | Target |
|--------|-----------------|--------|
| On-Time Delivery | ~88% | 95% |
| Fleet Utilization | ~75% | 85% |
| Customer Satisfaction | ~7.5/10 | 8.5/10 |
| Lead Conversion (Model) | AUC 0.87 | - |
| Demand Forecast | MAPE 8-10% | <10% |

---

## Troubleshooting

**Issue: Module not found**
```bash
set PYTHONPATH=%cd%
```

**Issue: No data**
```bash
python -m src.data_generator
```

**Issue: OpenAI API errors**
- GenAI features work in mock mode without API key
- Set `OPENAI_API_KEY` environment variable for full functionality
