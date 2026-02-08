# GCP Deployment Guide

Complete step-by-step guide for deploying Penske Logistics Analytics to Google Cloud using Cloud Run.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Architecture Overview](#2-architecture-overview)
3. [Step 1: GCP Project Setup](#step-1-gcp-project-setup)
4. [Step 2: Create Artifact Registry](#step-2-create-artifact-registry)
5. [Step 3: Build and Push Docker Image](#step-3-build-and-push-docker-image)
6. [Step 4: Deploy to Cloud Run](#step-4-deploy-to-cloud-run)
7. [Step 5: Configure Secrets](#step-5-configure-secrets)
8. [Step 6: Set Up Load Balancer](#step-6-set-up-load-balancer-optional)
9. [Step 7: Verify Deployment](#step-7-verify-deployment)
10. [Step 8: Set Up CI/CD](#step-8-set-up-cicd-cloud-build)
11. [Vertex AI Generative AI Integration](#vertex-ai-generative-ai-integration)
12. [Vertex AI ML Platform Integration](#vertex-ai-ml-platform-integration)
13. [Troubleshooting](#troubleshooting)
14. [Cost Optimization](#cost-optimization)

---

## 1. Prerequisites

### Required Tools

```bash
# Verify Google Cloud SDK is installed
gcloud --version
# Expected: Google Cloud SDK 400+

# Verify Docker is installed
docker --version
# Expected: Docker version 20.10+

# Login to Google Cloud
gcloud auth login

# Configure Docker for GCR/Artifact Registry
gcloud auth configure-docker
```

### Required GCP Permissions

Your account needs these roles:
- `roles/run.admin` - Cloud Run Admin
- `roles/artifactregistry.admin` - Artifact Registry Admin
- `roles/secretmanager.admin` - Secret Manager Admin
- `roles/iam.serviceAccountUser` - Service Account User

---

## 2. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                          GCP Project                                │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │                     Cloud Run Services                        │ │
│  │  ┌─────────────────────┐  ┌─────────────────────┐            │ │
│  │  │  penske-api         │  │  penske-dashboard   │            │ │
│  │  │  (Cloud Run)        │  │  (Cloud Run)        │            │ │
│  │  │  Port: 8000         │  │  Port: 8501         │            │ │
│  │  │  Auto-scaling 0-10  │  │  Auto-scaling 0-5   │            │ │
│  │  └──────────┬──────────┘  └──────────┬──────────┘            │ │
│  │             │                        │                        │ │
│  │             └────────────┬───────────┘                        │ │
│  │                          │                                    │ │
│  │               ┌──────────┴──────────┐                         │ │
│  │               │  Cloud Load Balancer │ (Optional)             │ │
│  │               │  (HTTPS + Custom DNS) │                        │ │
│  │               └──────────┬──────────┘                         │ │
│  └──────────────────────────┼────────────────────────────────────┘ │
│                             │                                      │
│  ┌──────────────────────────┴──────────────────────────────────┐  │
│  │                    Supporting Services                       │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │  │
│  │  │  Artifact   │  │   Secret    │  │   Cloud     │         │  │
│  │  │  Registry   │  │   Manager   │  │   Logging   │         │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘         │  │
│  └─────────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────────┘
```

### Components Created

| Component | Description | Purpose |
|-----------|-------------|---------|
| Cloud Run (API) | Serverless container | Backend FastAPI service |
| Cloud Run (Dashboard) | Serverless container | Streamlit dashboard |
| Artifact Registry | Docker registry | Store container images |
| Secret Manager | Secrets storage | Store API keys securely |
| Cloud Logging | Centralized logs | Application monitoring |
| Load Balancer | Traffic management | Custom domain & SSL |

---

## Step 1: GCP Project Setup

### 1.1 Set Environment Variables

```bash
# Set your project ID
export PROJECT_ID="penske-analytics-prod"
export REGION="us-central1"
export SERVICE_ACCOUNT="penske-cloudrun@${PROJECT_ID}.iam.gserviceaccount.com"

# Set project
gcloud config set project $PROJECT_ID

# Verify
gcloud config get-value project
```

### 1.2 Enable Required APIs

```bash
# Enable all required APIs
gcloud services enable \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    secretmanager.googleapis.com \
    cloudbuild.googleapis.com \
    logging.googleapis.com \
    monitoring.googleapis.com

# Verify enabled APIs
gcloud services list --enabled | grep -E "(run|artifact|secret|cloudbuild)"
```

### 1.3 Create Service Account

```bash
# Create service account
gcloud iam service-accounts create penske-cloudrun \
    --display-name="Penske Cloud Run Service Account"

# Grant necessary roles
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/secretmanager.secretAccessor"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/logging.logWriter"
```

---

## Step 2: Create Artifact Registry

### 2.1 Create Repository

```bash
# Create Artifact Registry repository
gcloud artifacts repositories create penske-analytics \
    --repository-format=docker \
    --location=$REGION \
    --description="Penske Logistics Analytics images"

# Get repository URL
export ARTIFACT_REPO="${REGION}-docker.pkg.dev/${PROJECT_ID}/penske-analytics"

echo "Artifact Registry: $ARTIFACT_REPO"
```

### 2.2 Configure Docker Authentication

```bash
# Configure Docker to use Artifact Registry
gcloud auth configure-docker ${REGION}-docker.pkg.dev

# Verify authentication
docker pull hello-world 2>/dev/null && echo "Docker configured successfully"
```

---

## Step 3: Build and Push Docker Image

### 3.1 Build the Image

```bash
# Navigate to project root
cd /path/to/penske-logistics-analytics

# Build Docker image
docker build -t penske-logistics-analytics:latest -f deploy/Dockerfile .
```

### 3.2 Tag and Push to Artifact Registry

```bash
# Tag for Artifact Registry
docker tag penske-logistics-analytics:latest $ARTIFACT_REPO/penske-analytics:latest
docker tag penske-logistics-analytics:latest $ARTIFACT_REPO/penske-analytics:v1.0.0

# Push to Artifact Registry
docker push $ARTIFACT_REPO/penske-analytics:latest
docker push $ARTIFACT_REPO/penske-analytics:v1.0.0
```

### 3.3 Alternative: Build with Cloud Build

```bash
# Build directly in cloud (no local Docker needed)
gcloud builds submit \
    --tag $ARTIFACT_REPO/penske-analytics:latest \
    --timeout=20m
```

### 3.4 Verify Image

```bash
# List images in repository
gcloud artifacts docker images list $ARTIFACT_REPO \
    --include-tags \
    --format="table(package,tags,createTime)"
```

---

## Step 4: Deploy to Cloud Run

### 4.1 Deploy API Service

```bash
# Deploy API to Cloud Run
gcloud run deploy penske-api \
    --image=$ARTIFACT_REPO/penske-analytics:latest \
    --platform=managed \
    --region=$REGION \
    --port=8000 \
    --memory=2Gi \
    --cpu=1 \
    --min-instances=0 \
    --max-instances=10 \
    --timeout=300 \
    --concurrency=80 \
    --service-account=$SERVICE_ACCOUNT \
    --set-env-vars="PYTHONPATH=/app" \
    --allow-unauthenticated

# Get API URL
export API_URL=$(gcloud run services describe penske-api \
    --platform=managed \
    --region=$REGION \
    --format='value(status.url)')

echo "API URL: $API_URL"
```

### 4.2 Deploy Dashboard Service

```bash
# Deploy Dashboard to Cloud Run
gcloud run deploy penske-dashboard \
    --image=$ARTIFACT_REPO/penske-analytics:latest \
    --platform=managed \
    --region=$REGION \
    --port=8501 \
    --memory=2Gi \
    --cpu=1 \
    --min-instances=0 \
    --max-instances=5 \
    --timeout=300 \
    --concurrency=50 \
    --service-account=$SERVICE_ACCOUNT \
    --set-env-vars="PYTHONPATH=/app" \
    --command="streamlit" \
    --args="run,app/streamlit_dashboard.py,--server.port=8501,--server.address=0.0.0.0" \
    --allow-unauthenticated

# Get Dashboard URL
export DASHBOARD_URL=$(gcloud run services describe penske-dashboard \
    --platform=managed \
    --region=$REGION \
    --format='value(status.url)')

echo "Dashboard URL: $DASHBOARD_URL"
```

---

## Step 5: Configure Secrets

### 5.1 Create Secret

```bash
# Create secret for OpenAI API key
echo -n "sk-your-actual-openai-key" | \
    gcloud secrets create openai-api-key \
    --data-file=- \
    --replication-policy="automatic"

# Grant access to service account
gcloud secrets add-iam-policy-binding openai-api-key \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/secretmanager.secretAccessor"
```

### 5.2 Update Cloud Run with Secrets

```bash
# Update API service with secret
gcloud run services update penske-api \
    --platform=managed \
    --region=$REGION \
    --set-secrets="OPENAI_API_KEY=openai-api-key:latest"

# Update Dashboard service with secret
gcloud run services update penske-dashboard \
    --platform=managed \
    --region=$REGION \
    --set-secrets="OPENAI_API_KEY=openai-api-key:latest"
```

### 5.3 Verify Secrets

```bash
# List secrets
gcloud secrets list

# View secret versions
gcloud secrets versions list openai-api-key
```

---

## Step 6: Set Up Load Balancer (Optional)

For custom domain and advanced routing:

### 6.1 Reserve Static IP

```bash
# Reserve global static IP
gcloud compute addresses create penske-ip \
    --global

# Get IP address
export STATIC_IP=$(gcloud compute addresses describe penske-ip \
    --global \
    --format='value(address)')

echo "Static IP: $STATIC_IP"
```

### 6.2 Create Serverless NEG

```bash
# Create NEG for API
gcloud compute network-endpoint-groups create penske-api-neg \
    --region=$REGION \
    --network-endpoint-type=serverless \
    --cloud-run-service=penske-api

# Create NEG for Dashboard
gcloud compute network-endpoint-groups create penske-dashboard-neg \
    --region=$REGION \
    --network-endpoint-type=serverless \
    --cloud-run-service=penske-dashboard
```

### 6.3 Create Load Balancer

```bash
# Create backend services
gcloud compute backend-services create penske-api-backend \
    --global \
    --load-balancing-scheme=EXTERNAL_MANAGED
gcloud compute backend-services add-backend penske-api-backend \
    --global \
    --network-endpoint-group=penske-api-neg \
    --network-endpoint-group-region=$REGION

gcloud compute backend-services create penske-dashboard-backend \
    --global \
    --load-balancing-scheme=EXTERNAL_MANAGED
gcloud compute backend-services add-backend penske-dashboard-backend \
    --global \
    --network-endpoint-group=penske-dashboard-neg \
    --network-endpoint-group-region=$REGION

# Create URL map
gcloud compute url-maps create penske-lb \
    --default-service=penske-dashboard-backend

# Add path rule for API
gcloud compute url-maps add-path-matcher penske-lb \
    --path-matcher-name=api-matcher \
    --default-service=penske-dashboard-backend \
    --path-rules="/api/*=penske-api-backend"

# Create HTTP(S) proxy
gcloud compute target-http-proxies create penske-http-proxy \
    --url-map=penske-lb

# Create forwarding rule
gcloud compute forwarding-rules create penske-http-rule \
    --global \
    --target-http-proxy=penske-http-proxy \
    --ports=80 \
    --address=penske-ip
```

---

## Step 7: Verify Deployment

### 7.1 Check Service Status

```bash
# Check API service
gcloud run services describe penske-api \
    --platform=managed \
    --region=$REGION \
    --format="table(status.conditions[0].type,status.conditions[0].status)"

# Check Dashboard service
gcloud run services describe penske-dashboard \
    --platform=managed \
    --region=$REGION \
    --format="table(status.conditions[0].type,status.conditions[0].status)"
```

### 7.2 Test Endpoints

```bash
# Test API
curl $API_URL/

# Test Dashboard (should return HTML)
curl -I $DASHBOARD_URL/

# Test with authentication (if required)
curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" $API_URL/
```

### 7.3 View Logs

```bash
# View API logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=penske-api" \
    --limit=50 \
    --format="table(timestamp,jsonPayload.message)"

# Stream logs in real-time
gcloud beta run services logs read penske-api --region=$REGION --tail=50
```

### 7.4 Access Applications

```bash
echo "============================================"
echo "DEPLOYMENT COMPLETE!"
echo "============================================"
echo "API URL:       $API_URL"
echo "Dashboard URL: $DASHBOARD_URL"
if [ ! -z "$STATIC_IP" ]; then
echo "Load Balancer: http://$STATIC_IP"
fi
echo "============================================"
```

---

## Step 8: Set Up CI/CD (Cloud Build)

### 8.1 Create Cloud Build Config

Create `deploy/gcp/cloudbuild.yaml`:

```yaml
steps:
  # Run tests
  - name: 'python:3.11-slim'
    entrypoint: 'bash'
    args:
      - '-c'
      - |
        pip install -r requirements.txt
        pip install pytest
        pytest tests/ -v

  # Build Docker image
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', '${_REGION}-docker.pkg.dev/${PROJECT_ID}/penske-analytics/penske-analytics:${SHORT_SHA}', '-f', 'deploy/Dockerfile', '.']

  # Push to Artifact Registry
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', '${_REGION}-docker.pkg.dev/${PROJECT_ID}/penske-analytics/penske-analytics:${SHORT_SHA}']

  # Deploy API to Cloud Run
  - name: 'gcr.io/cloud-builders/gcloud'
    args:
      - 'run'
      - 'deploy'
      - 'penske-api'
      - '--image=${_REGION}-docker.pkg.dev/${PROJECT_ID}/penske-analytics/penske-analytics:${SHORT_SHA}'
      - '--region=${_REGION}'
      - '--platform=managed'

  # Deploy Dashboard to Cloud Run
  - name: 'gcr.io/cloud-builders/gcloud'
    args:
      - 'run'
      - 'deploy'
      - 'penske-dashboard'
      - '--image=${_REGION}-docker.pkg.dev/${PROJECT_ID}/penske-analytics/penske-analytics:${SHORT_SHA}'
      - '--region=${_REGION}'
      - '--platform=managed'

substitutions:
  _REGION: us-central1

options:
  logging: CLOUD_LOGGING_ONLY

images:
  - '${_REGION}-docker.pkg.dev/${PROJECT_ID}/penske-analytics/penske-analytics:${SHORT_SHA}'
```

### 8.2 Create Build Trigger

```bash
# Create trigger for main branch
gcloud builds triggers create github \
    --repo-name="penske-logistics-analytics" \
    --repo-owner="your-org" \
    --branch-pattern="^main$" \
    --build-config="deploy/gcp/cloudbuild.yaml" \
    --name="penske-prod-deploy"
```

---

## Vertex AI Generative AI Integration

Vertex AI provides access to Google's foundation models (Gemini, PaLM) for generative AI capabilities in your logistics analytics application.

### Enable Vertex AI APIs

```bash
# Enable required APIs
gcloud services enable \
    aiplatform.googleapis.com \
    generativelanguage.googleapis.com \
    --project=$PROJECT_ID

# Verify APIs are enabled
gcloud services list --enabled | grep -E "(aiplatform|generativelanguage)"
```

### Available Models for Logistics Analytics

| Model | Use Case | Best For |
|-------|----------|----------|
| **Gemini 1.5 Pro** | Complex reasoning | Route optimization, demand analysis |
| **Gemini 1.5 Flash** | Fast responses | Real-time logistics queries |
| **Gemini 1.0 Pro** | Cost-effective | General text processing |
| **text-embedding-004** | Vector search | Semantic search on logistics data |
| **code-bison** | Code generation | Automation scripts |

### Vertex AI Generative AI Integration

```python
# src/services/vertex_ai_service.py
import vertexai
from vertexai.generative_models import GenerativeModel, Part
from vertexai.language_models import TextEmbeddingModel
import os

class VertexAIService:
    def __init__(self, project_id: str, location: str = "us-central1"):
        vertexai.init(project=project_id, location=location)
        self.model = GenerativeModel("gemini-1.5-pro")
        self.embedding_model = TextEmbeddingModel.from_pretrained("text-embedding-004")
    
    def analyze_logistics_data(self, prompt: str):
        """Analyze logistics data using Vertex AI Gemini."""
        system_instruction = "You are a logistics analytics expert specializing in route optimization and demand forecasting."
        
        response = self.model.generate_content(
            prompt,
            generation_config={
                "max_output_tokens": 4096,
                "temperature": 0.7,
                "top_p": 0.95,
            }
        )
        return response.text
    
    def generate_embeddings(self, texts: list):
        """Generate embeddings for semantic search."""
        embeddings = self.embedding_model.get_embeddings(texts)
        return [embedding.values for embedding in embeddings]
    
    def stream_analysis(self, prompt: str):
        """Stream logistics analysis for real-time updates."""
        responses = self.model.generate_content(
            prompt,
            stream=True,
            generation_config={
                "max_output_tokens": 4096,
                "temperature": 0.7,
            }
        )
        for response in responses:
            yield response.text
    
    def analyze_with_context(self, prompt: str, context_docs: list):
        """Analyze with RAG context from logistics documents."""
        context = "\n\n".join([f"Document {i+1}:\n{doc}" for i, doc in enumerate(context_docs)])
        
        full_prompt = f"""Based on the following logistics documents:

{context}

Answer this question: {prompt}"""
        
        return self.analyze_logistics_data(full_prompt)
```

### Vertex AI Use Cases for Penske Analytics

```python
# Example: Route Optimization Analysis
vertex_ai = VertexAIService(project_id="penske-analytics-prod")

prompt = """
Analyze this logistics route data and suggest optimizations:
- Current route: Chicago → Indianapolis → Louisville → Nashville
- Total distance: 478 miles
- Average delivery time: 8.5 hours
- Fuel consumption: 65 gallons

Consider traffic patterns, fuel efficiency, and delivery windows.
"""

analysis = vertex_ai.analyze_logistics_data(prompt)
print(analysis)

# Example: Generate embeddings for semantic search
documents = [
    "Shipment delayed due to weather conditions in Chicago",
    "Route optimization reduced fuel consumption by 15%",
    "Peak demand expected during holiday season"
]
embeddings = vertex_ai.generate_embeddings(documents)
```

### Store Credentials in Secret Manager

```bash
# Service account is used automatically via Application Default Credentials
# For additional API keys, store in Secret Manager

gcloud secrets create vertex-ai-config \
    --data-file=- <<EOF
{
    "project_id": "$PROJECT_ID",
    "location": "us-central1",
    "model": "gemini-1.5-pro"
}
EOF

# Grant Cloud Run access
gcloud secrets add-iam-policy-binding vertex-ai-config \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/secretmanager.secretAccessor"
```

### IAM Permissions for Vertex AI

```bash
# Grant Vertex AI permissions to service account
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/ml.developer"
```

### Vertex AI Generative AI Costs

| Model | Input (per 1K chars) | Output (per 1K chars) |
|-------|---------------------|----------------------|
| Gemini 1.5 Pro | $0.00125 | $0.00375 |
| Gemini 1.5 Flash | $0.000125 | $0.000375 |
| Gemini 1.0 Pro | $0.000125 | $0.000375 |
| text-embedding-004 | $0.000025 | - |

---

## Vertex AI ML Platform Integration

Vertex AI ML Platform enables training, deploying, and managing custom ML models for logistics predictions. This section provides a complete walkthrough from data preparation to production deployment.

### What You Will Accomplish

By following this guide, you will:
1. **Prepare and upload training data** - Format logistics data and upload to Google Cloud Storage
2. **Create a training job** - Run custom training on Vertex AI managed infrastructure
3. **Deploy to endpoint** - Host your model for real-time predictions
4. **Make predictions** - Call the endpoint from your application

### Vertex AI ML Architecture Overview

```
┌───────────────────────────────────────────────────────────────────────────────────┐
│                          Vertex AI ML Pipeline                                     │
│                                                                                    │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐  │
│  │  GCS Bucket  │ ──▶ │  Training    │ ──▶ │    Model     │ ──▶ │   Endpoint   │  │
│  │              │     │   Job        │     │   Registry   │     │              │  │
│  │ • train.csv  │     │              │     │              │     │ Real-time    │  │
│  │ • valid.csv  │     │ Runs your    │     │ Versioned    │     │ predictions  │  │
│  │              │     │ train.py     │     │ model files  │     │              │  │
│  └──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘  │
│                                                                                    │
│  Data stored in:       Training runs on:   Model saved to:      Endpoint URL:     │
│  gs://penske-vertex    n1-standard-4       Model Registry       *.endpoints.ai    │
└───────────────────────────────────────────────────────────────────────────────────┘
```

---

### Step 1: Set Up GCP Project and Enable APIs

**What we're doing:** Configuring your GCP project and enabling the required Vertex AI APIs.

```bash
# Set environment variables
export PROJECT_ID="penske-analytics-prod"
export REGION="us-central1"

# Set default project
gcloud config set project $PROJECT_ID

# Enable required APIs
gcloud services enable \
    aiplatform.googleapis.com \
    storage.googleapis.com \
    compute.googleapis.com

# Verify APIs are enabled
gcloud services list --enabled | grep -E "(aiplatform|storage)"
```

**Expected Output:**
```
aiplatform.googleapis.com      Vertex AI API
storage.googleapis.com         Cloud Storage API
```

---

### Step 2: Prepare Training Data

**What we're doing:** Creating properly formatted CSV files for model training.

**Data format requirements:**
- CSV files with feature columns and a `target` column
- Split into training (80%) and validation (20%) sets

**Create file: `scripts/generate_gcp_training_data.py`**

```python
#!/usr/bin/env python3
"""
Generate training data for Vertex AI demand forecasting model.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def generate_logistics_training_data(num_samples=10000, output_dir='data/gcp_training'):
    """Generate sample training data for demand forecasting."""
    
    np.random.seed(42)
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate date range
    start_date = datetime(2023, 1, 1)
    dates = [start_date + timedelta(days=i) for i in range(num_samples)]
    
    # Generate features
    data = {
        'shipment_volume': np.random.randint(500, 2000, num_samples),
        'fuel_price': np.random.uniform(3.0, 4.5, num_samples).round(2),
        'weather_severity': np.random.choice([0, 1, 2], num_samples, p=[0.7, 0.2, 0.1]),
        'day_of_week': [d.isoweekday() for d in dates],
        'is_holiday': np.random.choice([0, 1], num_samples, p=[0.95, 0.05]),
        'previous_day_volume': np.random.randint(500, 2000, num_samples),
        'region_midwest': np.random.choice([0, 1], num_samples),
        'region_northeast': np.random.choice([0, 1], num_samples),
        'region_southeast': np.random.choice([0, 1], num_samples),
        'region_west': np.random.choice([0, 1], num_samples),
    }
    
    df = pd.DataFrame(data)
    
    # Create target (next day's shipment volume)
    df['target'] = (
        df['shipment_volume'] * 0.7 + 
        df['previous_day_volume'] * 0.2 +
        np.where(df['weather_severity'] == 2, -100, 0) +
        np.where(df['day_of_week'].isin([6, 7]), -150, 50) +
        np.random.normal(0, 50, num_samples)
    ).astype(int)
    
    # Split into train/validation
    train_size = int(len(df) * 0.8)
    train_df = df[:train_size]
    valid_df = df[train_size:]
    
    # Save to CSV
    train_path = os.path.join(output_dir, 'train.csv')
    valid_path = os.path.join(output_dir, 'validation.csv')
    
    train_df.to_csv(train_path, index=False)
    valid_df.to_csv(valid_path, index=False)
    
    print("=" * 60)
    print("VERTEX AI TRAINING DATA GENERATED")
    print("=" * 60)
    print(f"Training data: {len(train_df)} rows → {train_path}")
    print(f"Validation data: {len(valid_df)} rows → {valid_path}")
    print(f"\nFeatures ({len(train_df.columns) - 1}):")
    for col in train_df.columns:
        if col != 'target':
            print(f"  - {col}")
    print(f"\nTarget column: target")
    print("=" * 60)
    
    return train_df, valid_df

if __name__ == '__main__':
    generate_logistics_training_data()
```

**Run the script:**
```bash
python scripts/generate_gcp_training_data.py
```

**Expected Output:**
```
============================================================
VERTEX AI TRAINING DATA GENERATED
============================================================
Training data: 8000 rows → data/gcp_training/train.csv
Validation data: 2000 rows → data/gcp_training/validation.csv

Features (10):
  - shipment_volume
  - fuel_price
  - weather_severity
  - day_of_week
  - is_holiday
  - previous_day_volume
  - region_midwest
  - region_northeast
  - region_southeast
  - region_west

Target column: target
============================================================
```

---

### Step 3: Upload Data to Google Cloud Storage

**What we're doing:** Creating a GCS bucket and uploading training data where Vertex AI can access it.

**Where the data goes:** `gs://penske-vertex-{PROJECT_ID}/training/`

```bash
# Create GCS bucket for ML data
gsutil mb -l $REGION gs://penske-vertex-${PROJECT_ID}

# Upload training data
gsutil cp data/gcp_training/train.csv gs://penske-vertex-${PROJECT_ID}/training/train.csv
gsutil cp data/gcp_training/validation.csv gs://penske-vertex-${PROJECT_ID}/training/validation.csv

# Verify upload
gsutil ls -l gs://penske-vertex-${PROJECT_ID}/training/
```

**Expected Output:**
```
    524288  2024-01-15T10:30:45Z  gs://penske-vertex-penske-analytics-prod/training/train.csv
    131072  2024-01-15T10:30:47Z  gs://penske-vertex-penske-analytics-prod/training/validation.csv
```

---

### Step 4: Create Training Script

**What we're doing:** Writing the Python script that Vertex AI will execute on managed training infrastructure.

**Where this runs:** On a managed VM (e.g., n1-standard-4) that Vertex AI provisions automatically.

**Output location:** Model files are saved to `AIP_MODEL_DIR` environment variable, which Vertex AI automatically uploads to Model Registry.

**Create file: `src/ml/scripts/train_vertex.py`**

```python
#!/usr/bin/env python3
"""
Vertex AI Training Script for Penske Demand Forecasting

This script runs on Vertex AI managed training infrastructure.
Vertex AI automatically:
  - Provisions compute resources
  - Sets AIP_MODEL_DIR for model output
  - Uploads model artifacts to Model Registry
"""

import argparse
import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import json
from google.cloud import storage

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser()
    
    # GCS path to training data
    parser.add_argument('--data-path', type=str, required=True,
                       help='GCS path to training data folder (gs://bucket/path/)')
    
    # Hyperparameters
    parser.add_argument('--n-estimators', type=int, default=100)
    parser.add_argument('--max-depth', type=int, default=10)
    parser.add_argument('--min-samples-split', type=int, default=5)
    parser.add_argument('--min-samples-leaf', type=int, default=2)
    
    return parser.parse_args()

def download_from_gcs(gcs_path: str, local_path: str):
    """Download file from GCS to local path."""
    
    # Parse GCS path
    path_parts = gcs_path.replace('gs://', '').split('/')
    bucket_name = path_parts[0]
    blob_path = '/'.join(path_parts[1:])
    
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_path)
    
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    blob.download_to_filename(local_path)
    print(f"Downloaded: {gcs_path} → {local_path}")

def load_data(gcs_data_path: str):
    """Load training and validation data from GCS."""
    
    # Download files from GCS
    train_gcs = f"{gcs_data_path.rstrip('/')}/train.csv"
    valid_gcs = f"{gcs_data_path.rstrip('/')}/validation.csv"
    
    download_from_gcs(train_gcs, '/tmp/train.csv')
    download_from_gcs(valid_gcs, '/tmp/validation.csv')
    
    # Load data
    train_df = pd.read_csv('/tmp/train.csv')
    valid_df = pd.read_csv('/tmp/validation.csv')
    
    print(f"Training samples: {len(train_df)}")
    print(f"Validation samples: {len(valid_df)}")
    print(f"Features: {list(train_df.columns)}")
    
    return train_df, valid_df

def train_model(train_df, args):
    """Train the Random Forest model."""
    
    X_train = train_df.drop('target', axis=1)
    y_train = train_df['target']
    
    print(f"\nTraining with hyperparameters:")
    print(f"  n_estimators: {args.n_estimators}")
    print(f"  max_depth: {args.max_depth}")
    print(f"  min_samples_split: {args.min_samples_split}")
    print(f"  min_samples_leaf: {args.min_samples_leaf}")
    
    model = RandomForestRegressor(
        n_estimators=args.n_estimators,
        max_depth=args.max_depth,
        min_samples_split=args.min_samples_split,
        min_samples_leaf=args.min_samples_leaf,
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    print("Training complete!")
    
    return model

def evaluate_model(model, valid_df):
    """Evaluate model on validation data."""
    
    X_valid = valid_df.drop('target', axis=1)
    y_valid = valid_df['target']
    
    predictions = model.predict(X_valid)
    
    mae = mean_absolute_error(y_valid, predictions)
    rmse = np.sqrt(mean_squared_error(y_valid, predictions))
    r2 = r2_score(y_valid, predictions)
    
    print(f"\nValidation Metrics:")
    print(f"  MAE: {mae:.2f}")
    print(f"  RMSE: {rmse:.2f}")
    print(f"  R²: {r2:.4f}")
    
    return {"mae": float(mae), "rmse": float(rmse), "r2": float(r2)}

def save_model(model, metrics, feature_names):
    """Save model to AIP_MODEL_DIR (Vertex AI uploads this automatically)."""
    
    # AIP_MODEL_DIR is set by Vertex AI
    model_dir = os.environ.get('AIP_MODEL_DIR', '/tmp/model')
    os.makedirs(model_dir, exist_ok=True)
    
    # Save model
    model_path = os.path.join(model_dir, 'model.joblib')
    joblib.dump(model, model_path)
    print(f"\nModel saved to: {model_path}")
    
    # Save feature names (needed for prediction)
    features_path = os.path.join(model_dir, 'feature_names.json')
    with open(features_path, 'w') as f:
        json.dump(feature_names, f)
    print(f"Feature names saved to: {features_path}")
    
    # Save metrics
    metrics_path = os.path.join(model_dir, 'metrics.json')
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f)
    print(f"Metrics saved to: {metrics_path}")
    
    # Save feature importances
    importances = dict(zip(feature_names, model.feature_importances_.tolist()))
    importances_path = os.path.join(model_dir, 'feature_importances.json')
    with open(importances_path, 'w') as f:
        json.dump(importances, f, indent=2)
    print(f"Feature importances saved to: {importances_path}")
    
    print(f"\nAll artifacts saved to: {model_dir}")
    print("Vertex AI will upload these to Model Registry automatically.")

if __name__ == '__main__':
    print("=" * 60)
    print("PENSKE LOGISTICS - VERTEX AI TRAINING")
    print("=" * 60)
    
    args = parse_args()
    
    # Load data from GCS
    train_df, valid_df = load_data(args.data_path)
    
    # Train model
    model = train_model(train_df, args)
    
    # Evaluate model
    metrics = evaluate_model(model, valid_df)
    
    # Save model (Vertex AI uploads AIP_MODEL_DIR to Model Registry)
    feature_names = [col for col in train_df.columns if col != 'target']
    save_model(model, metrics, feature_names)
    
    print("\n" + "=" * 60)
    print("TRAINING COMPLETE - Model uploaded to Vertex AI Model Registry")
    print("=" * 60)
```

---

### Step 5: Submit Training Job

**What we're doing:** Submitting a training job to Vertex AI, which will:
1. Provision a VM (e.g., n1-standard-4)
2. Run your `train_vertex.py` script
3. Upload model artifacts to Model Registry
4. Terminate the VM when done

**Where outputs go:** 
- Model artifacts: Vertex AI Model Registry
- Training logs: Cloud Logging

**Create file: `src/ml/vertex_training.py`**

```python
#!/usr/bin/env python3
"""
Submit training job to Vertex AI.
"""

from google.cloud import aiplatform
import os

def run_training_job(
    project_id: str,
    region: str = "us-central1",
    bucket_name: str = None
):
    """Submit and monitor a Vertex AI training job."""
    
    if bucket_name is None:
        bucket_name = f"penske-vertex-{project_id}"
    
    print("=" * 60)
    print("VERTEX AI TRAINING JOB")
    print("=" * 60)
    print(f"Project: {project_id}")
    print(f"Region: {region}")
    print(f"Data Bucket: gs://{bucket_name}/training/")
    print("=" * 60)
    
    # Initialize Vertex AI
    aiplatform.init(project=project_id, location=region)
    
    # Create custom training job
    job = aiplatform.CustomTrainingJob(
        display_name="penske-demand-forecast-training",
        script_path="src/ml/scripts/train_vertex.py",
        container_uri="us-docker.pkg.dev/vertex-ai/training/sklearn-cpu.1-0:latest",
        requirements=["pandas", "scikit-learn", "joblib", "google-cloud-storage"],
        model_serving_container_image_uri="us-docker.pkg.dev/vertex-ai/prediction/sklearn-cpu.1-0:latest"
    )
    
    print("\nSubmitting training job...")
    print("This will take 10-20 minutes.\n")
    
    # Run training
    model = job.run(
        model_display_name="penske-demand-model",
        args=[
            "--data-path", f"gs://{bucket_name}/training/",
            "--n-estimators", "100",
            "--max-depth", "10",
            "--min-samples-split", "5",
            "--min-samples-leaf", "2"
        ],
        replica_count=1,
        machine_type="n1-standard-4",  # 4 vCPU, 15 GB RAM
        accelerator_type=None,
        accelerator_count=0,
    )
    
    print("\n" + "=" * 60)
    print("TRAINING COMPLETE!")
    print("=" * 60)
    print(f"Model Name: {model.display_name}")
    print(f"Model Resource: {model.resource_name}")
    print(f"\nView in Cloud Console:")
    print(f"  https://console.cloud.google.com/vertex-ai/models?project={project_id}")
    print("=" * 60)
    
    return model

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python vertex_training.py <project_id>")
        print("Example: python vertex_training.py penske-analytics-prod")
        sys.exit(1)
    
    project_id = sys.argv[1]
    run_training_job(project_id)
```

**Run the training:**
```bash
python src/ml/vertex_training.py $PROJECT_ID
```

**Expected Output:**
```
============================================================
VERTEX AI TRAINING JOB
============================================================
Project: penske-analytics-prod
Region: us-central1
Data Bucket: gs://penske-vertex-penske-analytics-prod/training/
============================================================

Submitting training job...
This will take 10-20 minutes.

Training job running...
View logs: https://console.cloud.google.com/logs/...

============================================================
TRAINING COMPLETE!
============================================================
Model Name: penske-demand-model
Model Resource: projects/123456/locations/us-central1/models/7890

View in Cloud Console:
  https://console.cloud.google.com/vertex-ai/models?project=penske-analytics-prod
============================================================
```

**Verify in Cloud Console:**
```bash
# List models in registry
gcloud ai models list --region=$REGION --project=$PROJECT_ID
```

---

### Step 6: Deploy Model to Endpoint

**What we're doing:** 
1. Creating a Vertex AI endpoint for real-time predictions
2. Deploying the trained model to the endpoint
3. Configuring traffic routing

**Where the endpoint lives:** `https://{region}-aiplatform.googleapis.com/v1/projects/{project}/locations/{region}/endpoints/{endpoint_id}:predict`

**Create file: `src/ml/vertex_deploy.py`**

```python
#!/usr/bin/env python3
"""
Deploy trained model to Vertex AI endpoint.
"""

from google.cloud import aiplatform

def deploy_model(
    project_id: str,
    model_name: str = "penske-demand-model",
    region: str = "us-central1"
):
    """Deploy trained model to Vertex AI endpoint."""
    
    print("=" * 60)
    print("VERTEX AI MODEL DEPLOYMENT")
    print("=" * 60)
    
    # Initialize Vertex AI
    aiplatform.init(project=project_id, location=region)
    
    # Get the model
    print(f"\n[1/3] Finding model '{model_name}'...")
    models = aiplatform.Model.list(
        filter=f'display_name="{model_name}"',
        order_by="create_time desc"
    )
    
    if not models:
        print(f"Error: No model found with name '{model_name}'")
        return None
    
    model = models[0]
    print(f"  Found: {model.resource_name}")
    
    # Create endpoint
    print(f"\n[2/3] Creating endpoint...")
    endpoint = aiplatform.Endpoint.create(
        display_name="penske-demand-forecast",
        description="Penske demand forecasting endpoint",
        project=project_id,
        location=region
    )
    print(f"  Endpoint created: {endpoint.resource_name}")
    
    # Deploy model to endpoint
    print(f"\n[3/3] Deploying model (this takes 5-10 minutes)...")
    model.deploy(
        endpoint=endpoint,
        deployed_model_display_name="penske-demand-v1",
        machine_type="n1-standard-2",
        min_replica_count=1,
        max_replica_count=5,
        traffic_percentage=100,
        sync=True
    )
    
    print("\n" + "=" * 60)
    print("DEPLOYMENT COMPLETE!")
    print("=" * 60)
    print(f"Endpoint Name: penske-demand-forecast")
    print(f"Endpoint ID: {endpoint.name}")
    print(f"Endpoint Resource: {endpoint.resource_name}")
    print(f"\nPrediction URL:")
    print(f"  https://{region}-aiplatform.googleapis.com/v1/{endpoint.resource_name}:predict")
    print("=" * 60)
    
    return endpoint

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python vertex_deploy.py <project_id>")
        sys.exit(1)
    
    project_id = sys.argv[1]
    deploy_model(project_id)
```

**Deploy the model:**
```bash
python src/ml/vertex_deploy.py $PROJECT_ID
```

**Verify endpoint:**
```bash
gcloud ai endpoints list --region=$REGION --project=$PROJECT_ID
```

**Expected Output:**
```
ENDPOINT_ID  DISPLAY_NAME            
1234567890   penske-demand-forecast
```

---

### Step 7: Make Predictions

**What we're doing:** Calling the deployed endpoint to get real-time predictions.

**Create file: `src/services/vertex_ml_service.py`**

```python
#!/usr/bin/env python3
"""
Vertex AI Service for making predictions.
"""

from google.cloud import aiplatform
from typing import List

class VertexMLService:
    """Service for Vertex AI endpoint predictions."""
    
    def __init__(
        self,
        project_id: str,
        endpoint_name: str = "penske-demand-forecast",
        region: str = "us-central1"
    ):
        aiplatform.init(project=project_id, location=region)
        
        # Find endpoint by display name
        endpoints = aiplatform.Endpoint.list(
            filter=f'display_name="{endpoint_name}"'
        )
        
        if not endpoints:
            raise ValueError(f"Endpoint '{endpoint_name}' not found")
        
        self.endpoint = endpoints[0]
        self.project_id = project_id
        self.region = region
        
        print(f"Connected to endpoint: {self.endpoint.resource_name}")
    
    def predict_demand(self, features: List[List[float]]) -> List[float]:
        """
        Predict demand using the deployed model.
        
        Args:
            features: 2D list of feature values
                     Example: [[1250, 3.45, 0, 1, 0, 1180, 0, 1, 0, 0]]
        
        Returns:
            List of predicted demand values
        """
        response = self.endpoint.predict(instances=features)
        return response.predictions
    
    def predict_single(
        self,
        shipment_volume: int,
        fuel_price: float,
        weather_severity: int,
        day_of_week: int,
        is_holiday: int,
        previous_day_volume: int,
        region: str
    ) -> float:
        """Predict demand with named parameters."""
        
        # One-hot encode region
        features = [[
            shipment_volume,
            fuel_price,
            weather_severity,
            day_of_week,
            is_holiday,
            previous_day_volume,
            1 if region == 'Midwest' else 0,
            1 if region == 'Northeast' else 0,
            1 if region == 'Southeast' else 0,
            1 if region == 'West' else 0
        ]]
        
        predictions = self.predict_demand(features)
        return predictions[0]

# Example usage
if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python vertex_ml_service.py <project_id>")
        sys.exit(1)
    
    service = VertexMLService(project_id=sys.argv[1])
    
    # Predict demand for tomorrow
    prediction = service.predict_single(
        shipment_volume=1250,
        fuel_price=3.45,
        weather_severity=0,
        day_of_week=2,  # Tuesday
        is_holiday=0,
        previous_day_volume=1180,
        region='Northeast'
    )
    
    print(f"Predicted demand for tomorrow: {prediction:.0f} shipments")
```

**Test predictions:**
```bash
python src/services/vertex_ml_service.py $PROJECT_ID
```

**Expected Output:**
```
Connected to endpoint: projects/123456/locations/us-central1/endpoints/7890
Predicted demand for tomorrow: 1320 shipments
```

---

### Vertex AI ML Summary

| Step | What Happens | Output Location |
|------|--------------|-----------------|
| 1. Set Up Project | Enable APIs | GCP Console |
| 2. Prepare Data | Create train.csv, validation.csv | `data/gcp_training/` |
| 3. Upload to GCS | Copy files to cloud storage | `gs://penske-vertex-{ID}/training/` |
| 4. Training Script | Define model logic | `src/ml/scripts/train_vertex.py` |
| 5. Submit Job | Train on managed VM | Model Registry |
| 6. Deploy Model | Create endpoint | Vertex AI Endpoints |
| 7. Predictions | Call endpoint API | Real-time results |

### Vertex AI ML Costs

| Resource | Use Case | Cost |
|----------|----------|------|
| n1-standard-4 | Training (per hour) | $0.19 |
| n1-standard-2 | Endpoint (per hour) | $0.095 |
| GCS Storage | Data + Models (per GB/month) | $0.020 |
| **Typical Training Job** | 15 min on n1-standard-4 | ~$0.05 |
| **Endpoint (24/7)** | n1-standard-2 per month | ~$68 |

### Cleanup Vertex AI Resources

```bash
# Get endpoint ID
ENDPOINT_ID=$(gcloud ai endpoints list --region=$REGION --format="value(ENDPOINT_ID)" --filter="displayName=penske-demand-forecast")

# Undeploy model from endpoint
gcloud ai endpoints undeploy-model $ENDPOINT_ID \
    --project=$PROJECT_ID \
    --region=$REGION \
    --deployed-model-id=$(gcloud ai endpoints describe $ENDPOINT_ID --region=$REGION --format="value(deployedModels[0].id)")

# Delete endpoint
gcloud ai endpoints delete $ENDPOINT_ID \
    --project=$PROJECT_ID \
    --region=$REGION \
    --quiet

# Get model ID and delete
MODEL_ID=$(gcloud ai models list --region=$REGION --format="value(MODEL_ID)" --filter="displayName=penske-demand-model")
gcloud ai models delete $MODEL_ID \
    --project=$PROJECT_ID \
    --region=$REGION \
    --quiet

# Delete GCS data (optional)
gsutil rm -r gs://penske-vertex-${PROJECT_ID}
```

---

## Troubleshooting

### Issue: Container Won't Start

```bash
# Check logs
gcloud logging read \
    "resource.type=cloud_run_revision AND resource.labels.service_name=penske-api AND severity>=ERROR" \
    --limit=20

# Check revision status
gcloud run revisions list \
    --service=penske-api \
    --region=$REGION \
    --format="table(name,status.conditions[0].status,createTime)"
```

### Issue: Permission Denied

```bash
# Verify service account permissions
gcloud projects get-iam-policy $PROJECT_ID \
    --flatten="bindings[].members" \
    --filter="bindings.members:$SERVICE_ACCOUNT"

# Re-grant permissions if needed
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/secretmanager.secretAccessor"
```

### Issue: Cold Start Timeout

```bash
# Set minimum instances to avoid cold starts
gcloud run services update penske-api \
    --region=$REGION \
    --min-instances=1

# Increase timeout
gcloud run services update penske-api \
    --region=$REGION \
    --timeout=600
```

### Common Fixes

| Issue | Solution |
|-------|----------|
| Port mismatch | Verify `--port` matches app's listening port |
| Image not found | Check Artifact Registry path and permissions |
| Out of memory | Increase `--memory` allocation |
| Slow startup | Set `--min-instances=1` |
| Secret not found | Verify secret name and service account access |

---

## Cost Optimization

### Development Environment

```bash
# Scale to zero when not in use (default)
gcloud run services update penske-api \
    --region=$REGION \
    --min-instances=0 \
    --max-instances=1

# Use smaller instance
gcloud run services update penske-api \
    --region=$REGION \
    --memory=512Mi \
    --cpu=0.5
```

### Production Tips

| Optimization | Savings |
|--------------|---------|
| Scale to zero | 100% when idle |
| Right-size CPU/Memory | 20-50% |
| Use committed use | 20-30% |
| Regional vs global LB | 30% |

### Estimated Monthly Costs

| Component | Dev | Prod |
|-----------|-----|------|
| Cloud Run (API) | $5 | $30 |
| Cloud Run (Dashboard) | $5 | $20 |
| Artifact Registry | $1 | $5 |
| Secret Manager | $0 | $1 |
| Cloud Logging | $0 | $10 |
| Load Balancer | $0 | $18 |
| **Total** | **~$11** | **~$84** |

*Note: Cloud Run bills per request + CPU/memory time. Costs vary significantly based on traffic.*

---

## Cleanup

To delete all resources:

```bash
# Delete Cloud Run services
gcloud run services delete penske-api --region=$REGION --quiet
gcloud run services delete penske-dashboard --region=$REGION --quiet

# Delete secrets
gcloud secrets delete openai-api-key --quiet

# Delete Artifact Registry images
gcloud artifacts docker images delete $ARTIFACT_REPO/penske-analytics --delete-tags --quiet

# Delete Artifact Registry repository
gcloud artifacts repositories delete penske-analytics --location=$REGION --quiet

# Delete Load Balancer components (if created)
gcloud compute forwarding-rules delete penske-http-rule --global --quiet
gcloud compute target-http-proxies delete penske-http-proxy --quiet
gcloud compute url-maps delete penske-lb --quiet
gcloud compute backend-services delete penske-api-backend --global --quiet
gcloud compute backend-services delete penske-dashboard-backend --global --quiet
gcloud compute network-endpoint-groups delete penske-api-neg --region=$REGION --quiet
gcloud compute network-endpoint-groups delete penske-dashboard-neg --region=$REGION --quiet
gcloud compute addresses delete penske-ip --global --quiet

# Delete service account
gcloud iam service-accounts delete $SERVICE_ACCOUNT --quiet
```

---

## Next Steps

1. **Custom Domain:** Configure Cloud DNS and SSL certificate
2. **Authentication:** Add Identity-Aware Proxy (IAP)
3. **Monitoring:** Set up Cloud Monitoring dashboards
4. **VPC Connector:** Connect to private resources

---

**[← Back to Main Guide](../README.md)** | **[AWS Guide](../aws/DEPLOYMENT_GUIDE.md)** | **[Azure Guide](../azure/DEPLOYMENT_GUIDE.md)**
