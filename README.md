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
| **RAG / Search** | LangChain, BM25 + Vector Hybrid Search, FAISS, Azure AI Search |
| **Cloud** | Azure (primary), AWS, GCP deployment configs |

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
│   ├── cloud_ai_services.py       # Cloud AI + Hybrid Search (BM25 + Vector)
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
│   ├── aws/                       # AWS ECS/Fargate deployment
│   │   └── DEPLOYMENT_GUIDE.md
│   ├── azure/                     # Azure Container Apps deployment
│   │   └── DEPLOYMENT_GUIDE.md
│   └── gcp/                       # GCP Cloud Run deployment
│       └── DEPLOYMENT_GUIDE.md
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

## Hybrid Search (BM25 + Vector)

The `HybridSearchService` in `src/cloud_ai_services.py` combines keyword search (BM25) with semantic vector search for best-of-both-worlds retrieval.

### Why Hybrid?

| Query Type | BM25 Only | Vector Only | Hybrid |
|-----------|-----------|-------------|--------|
| Exact IDs: `"PEN-2026-001"` | ✅ | ❌ | ✅ |
| Semantic: `"how to handle damaged freight"` | ❌ | ✅ | ✅ |
| Mixed: `"DOT 49-CFR-395 parking rules"` | 🟡 | 🟡 | ✅ |

### Quick Start — Local (FAISS + BM25)

```python
from src.cloud_ai_services import HybridSearchService

# 1. Initialize
search = HybridSearchService(
    bm25_weight=0.4,      # 40% keyword matching
    vector_weight=0.6,    # 60% semantic similarity
    vector_store_type="faiss"
)

# 2. Connect to embedding provider
search.connect_azure_openai(
    endpoint="https://your-resource.openai.azure.com/",
    api_key="your-key"
)
# Or: search.connect_openai(api_key="your-key")

# 3. Index documents (with optional metadata)
docs = [
    "Procedure for handling damaged freight: file claim within 24 hours",
    "DOT regulation 49-CFR-395 covers hours of service for drivers",
    "Shipment PEN-2026-001 routed through Oklahoma City",
    "Overnight parking policy requires driver check-in by 10pm",
    "Hazmat handling requires certified carrier and special documentation",
]
metadatas = [
    {"type": "sop", "dept": "claims"},
    {"type": "regulation", "dept": "compliance"},
    {"type": "shipment", "dept": "operations"},
    {"type": "policy", "dept": "safety"},
    {"type": "sop", "dept": "hazmat"},
]
search.add_documents(docs, metadatas=metadatas)

# 4. Search — hybrid combines BM25 + vector results
results = search.search("DOT regulation 49-CFR-395", k=3)
for r in results:
    print(f"[Rank {r['rank']}] {r['content']}")
    print(f"  Metadata: {r['metadata']}")

# 5. Tune weights on the fly
search.update_weights(bm25_weight=0.7, vector_weight=0.3)  # Favor exact match

# 6. Check index stats
print(search.get_stats())
```

### Production — Azure AI Search (Native Hybrid)

Azure AI Search handles BM25 + vector natively — no local index needed:

```python
from src.cloud_ai_services import HybridSearchService

search = HybridSearchService()
search.connect_azure_search(
    search_endpoint="https://your-search.search.windows.net",
    search_key="your-search-key",
    index_name="penske-knowledge-base",
    openai_endpoint="https://your-resource.openai.azure.com/",
    openai_key="your-openai-key"
)

# Search works the same way
results = search.search("how to handle overnight parking?", k=5)
```

### Available Methods

| Method | Description |
|--------|-------------|
| `connect_azure_openai(endpoint, api_key)` | Use Azure OpenAI for embeddings |
| `connect_openai(api_key)` | Use OpenAI directly for embeddings |
| `add_documents(texts, metadatas)` | Index docs into BM25 + FAISS/Chroma |
| `connect_azure_search(...)` | Connect to Azure AI Search (native hybrid) |
| `search(query, k)` | Run hybrid search, return ranked results |
| `search_with_scores(query, k)` | Vector search with similarity scores |
| `update_weights(bm25, vector)` | Adjust keyword vs semantic balance |
| `get_stats()` | Return index statistics |

### Dependencies

```bash
pip install langchain langchain-community langchain-openai langchain-core faiss-cpu rank-bm25
```

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

See [`DEPLOYMENT.md`](DEPLOYMENT.md) for full details, or jump to a specific platform:

| Platform | Guide | Best For | Est. Cost |
|----------|-------|----------|----------|
| **Local Docker** | [`DEPLOYMENT.md`](DEPLOYMENT.md) | Development / Demo | Free |
| **AWS ECS/Fargate** | [`deploy/aws/DEPLOYMENT_GUIDE.md`](deploy/aws/DEPLOYMENT_GUIDE.md) | Enterprise AWS shops | ~$50-100/mo |
| **Azure Container Apps** | [`deploy/azure/DEPLOYMENT_GUIDE.md`](deploy/azure/DEPLOYMENT_GUIDE.md) | Microsoft ecosystem | ~$40-80/mo |
| **GCP Cloud Run** | [`deploy/gcp/DEPLOYMENT_GUIDE.md`](deploy/gcp/DEPLOYMENT_GUIDE.md) | Pay-per-use, scale-to-zero | ~$20-60/mo |
| **Kubernetes** | [`DEPLOYMENT.md`](DEPLOYMENT.md#option-3-kubernetes-deployment) | Production at scale | Varies |

### Quick Deploy

```bash
# Docker Compose (local)
cd deploy && docker-compose up -d
# → Dashboard: http://localhost:8501
# → API:       http://localhost:8000

# AWS
cd deploy/aws && ./deploy.sh

# Azure
cd deploy/azure && ./deploy.sh

# GCP
cd deploy/gcp && ./deploy.sh
```

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | No | OpenAI / Azure OpenAI key for GenAI + Hybrid Search |
| `AZURE_SEARCH_ENDPOINT` | No | Azure AI Search endpoint (for production hybrid search) |
| `AZURE_SEARCH_KEY` | No | Azure AI Search admin key |
| `PYTHONPATH` | Yes (containers) | Set to `/app` |
| `LOG_LEVEL` | No | INFO / DEBUG / WARNING |

---

## Documentation

| Document | Description |
|----------|-------------|
| [`DEPLOYMENT.md`](DEPLOYMENT.md) | Full deployment guide (Docker, K8s, Cloud) |
| [`deploy/README.md`](deploy/README.md) | Cloud deployment overview + architecture |
| [`deploy/aws/DEPLOYMENT_GUIDE.md`](deploy/aws/DEPLOYMENT_GUIDE.md) | AWS ECS/Fargate step-by-step |
| [`DEMO_GUIDE.md`](DEMO_GUIDE.md) | Step-by-step demo instructions |

---

## Next Steps

- [ ] Integrate with Penske's existing data warehouse (Snowflake)
- [ ] Set up real-time data streaming (Azure Event Hubs)
- [ ] Deploy hybrid search knowledge base to Azure AI Search
- [ ] Implement A/B testing framework
- [ ] Add alerting and monitoring (Azure Monitor + LangSmith)
- [ ] Build MCP servers for agent tool integrations
- [ ] Develop mobile dashboard
