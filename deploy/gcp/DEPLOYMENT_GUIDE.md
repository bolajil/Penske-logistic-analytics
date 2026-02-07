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

Vertex AI ML Platform enables training, deploying, and managing custom ML models for logistics predictions.

### Vertex AI ML Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                     Vertex AI ML Pipeline                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐ │
│  │  GCS Data   │→ │  Training   │→ │   Model     │→ │  Endpoint  │ │
│  │  (input)    │  │   Job       │  │  Registry   │  │ (inference)│ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

### Step 1: Create GCS Bucket for Training Data

```bash
# Create GCS bucket for ML data
gsutil mb -l $REGION gs://penske-vertex-${PROJECT_ID}

# Upload training data
gsutil cp -r data/training/ gs://penske-vertex-${PROJECT_ID}/training/
```

### Step 2: Create Custom Training Job

```python
# src/ml/vertex_training.py
from google.cloud import aiplatform

def train_demand_forecasting_model():
    """Train demand forecasting model on Vertex AI."""
    
    aiplatform.init(project="penske-analytics-prod", location="us-central1")
    
    # Create custom training job
    job = aiplatform.CustomTrainingJob(
        display_name="penske-demand-forecast-training",
        script_path="src/ml/scripts/train.py",
        container_uri="us-docker.pkg.dev/vertex-ai/training/sklearn-cpu.1-0:latest",
        requirements=["pandas", "scikit-learn", "joblib"],
        model_serving_container_image_uri="us-docker.pkg.dev/vertex-ai/prediction/sklearn-cpu.1-0:latest"
    )
    
    # Run training
    model = job.run(
        dataset=None,
        model_display_name="penske-demand-model",
        args=[
            "--data-path", "gs://penske-vertex-PROJECT_ID/training/",
            "--n-estimators", "100",
            "--max-depth", "10"
        ],
        replica_count=1,
        machine_type="n1-standard-4",
        accelerator_type=None,
        accelerator_count=0,
    )
    
    return model

# Training script: src/ml/scripts/train.py
"""
import argparse
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib
from google.cloud import storage
import os

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data-path', type=str)
    parser.add_argument('--n-estimators', type=int, default=100)
    parser.add_argument('--max-depth', type=int, default=10)
    args = parser.parse_args()
    
    # Download data from GCS
    storage_client = storage.Client()
    bucket_name = args.data_path.replace('gs://', '').split('/')[0]
    blob_path = '/'.join(args.data_path.replace('gs://', '').split('/')[1:])
    
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(f'{blob_path}train.csv')
    blob.download_to_filename('/tmp/train.csv')
    
    # Load and train
    train_data = pd.read_csv('/tmp/train.csv')
    model = RandomForestRegressor(
        n_estimators=args.n_estimators,
        max_depth=args.max_depth
    )
    model.fit(train_data.drop('target', axis=1), train_data['target'])
    
    # Save model to AIP_MODEL_DIR
    model_dir = os.environ.get('AIP_MODEL_DIR', '/tmp/model')
    os.makedirs(model_dir, exist_ok=True)
    joblib.dump(model, f'{model_dir}/model.joblib')
"""
```

### Step 3: Deploy Model Endpoint

```python
# Deploy to Vertex AI endpoint
from google.cloud import aiplatform

def deploy_model(model):
    """Deploy trained model to Vertex AI endpoint."""
    
    aiplatform.init(project="penske-analytics-prod", location="us-central1")
    
    # Create endpoint
    endpoint = aiplatform.Endpoint.create(
        display_name="penske-demand-forecast",
        description="Penske demand forecasting endpoint"
    )
    
    # Deploy model to endpoint
    model.deploy(
        endpoint=endpoint,
        deployed_model_display_name="penske-demand-v1",
        machine_type="n1-standard-2",
        min_replica_count=1,
        max_replica_count=5,
        traffic_percentage=100,
        sync=True
    )
    
    return endpoint

# Alternative: Deploy existing model
def deploy_existing_model(model_id):
    """Deploy an existing model from Model Registry."""
    
    model = aiplatform.Model(model_id)
    
    endpoint = model.deploy(
        machine_type="n1-standard-2",
        min_replica_count=1,
        max_replica_count=5,
        accelerator_type=None,
        accelerator_count=0,
    )
    
    return endpoint
```

### Step 4: Invoke Endpoint

```python
# src/services/vertex_ml_service.py
from google.cloud import aiplatform
import json

class VertexMLService:
    def __init__(self, endpoint_name: str, project: str, location: str = "us-central1"):
        aiplatform.init(project=project, location=location)
        self.endpoint = aiplatform.Endpoint(endpoint_name)
    
    def predict_demand(self, features: list):
        """Predict logistics demand using deployed model."""
        response = self.endpoint.predict(instances=features)
        return response.predictions
    
    def batch_predict(self, gcs_source: str, gcs_destination: str):
        """Run batch predictions for large datasets."""
        model = aiplatform.Model("projects/.../models/penske-demand-model")
        
        batch_prediction_job = model.batch_predict(
            job_display_name="penske-batch-prediction",
            gcs_source=gcs_source,
            gcs_destination_prefix=gcs_destination,
            machine_type="n1-standard-4",
            starting_replica_count=1,
            max_replica_count=5,
        )
        
        batch_prediction_job.wait()
        return batch_prediction_job

# Example usage
vertex_ml = VertexMLService(
    endpoint_name="projects/123/locations/us-central1/endpoints/456",
    project="penske-analytics-prod"
)

# Single prediction
features = [[100, 5, 3, 0.8, 25]]  # Example features
predictions = vertex_ml.predict_demand(features)
print(f"Predicted demand: {predictions}")
```

### AutoML for Quick Model Training

```python
# Use AutoML for quick model training without custom code
from google.cloud import aiplatform

def train_automl_model():
    """Train model using Vertex AI AutoML."""
    
    aiplatform.init(project="penske-analytics-prod", location="us-central1")
    
    # Create dataset
    dataset = aiplatform.TabularDataset.create(
        display_name="penske-demand-dataset",
        gcs_source="gs://penske-vertex-PROJECT_ID/training/train.csv"
    )
    
    # Train AutoML model
    job = aiplatform.AutoMLTabularTrainingJob(
        display_name="penske-automl-demand",
        optimization_prediction_type="regression",
        optimization_objective="minimize-rmse"
    )
    
    model = job.run(
        dataset=dataset,
        target_column="target",
        training_fraction_split=0.8,
        validation_fraction_split=0.1,
        test_fraction_split=0.1,
        model_display_name="penske-automl-model",
        budget_milli_node_hours=1000,  # 1 node hour
    )
    
    return model
```

### Vertex AI ML Use Cases for Penske Analytics

| Use Case | Model Type | Description |
|----------|------------|-------------|
| **Demand Forecasting** | Time Series / AutoML | Predict shipment volumes |
| **Route Optimization** | Custom Training | Optimize delivery routes |
| **ETD Prediction** | AutoML Regression | Estimate delivery times |
| **Anomaly Detection** | Custom Training | Detect logistics anomalies |
| **Cost Prediction** | AutoML Regression | Forecast shipping costs |

### Vertex AI ML Costs

| Resource | Use Case | Cost/Hour |
|----------|----------|-----------|
| n1-standard-2 | Dev/Test endpoints | $0.095 |
| n1-standard-4 | Training | $0.19 |
| n1-standard-8 | Production endpoint | $0.38 |
| n1-highmem-4 | Memory-intensive | $0.24 |
| AutoML Training | Per node hour | $19.32 |

### Auto-Scaling Endpoint

```bash
# Configure auto-scaling for production
gcloud ai endpoints deploy-model ENDPOINT_ID \
    --project=$PROJECT_ID \
    --region=$REGION \
    --model=MODEL_ID \
    --display-name="penske-demand-v1" \
    --machine-type=n1-standard-2 \
    --min-replica-count=1 \
    --max-replica-count=10 \
    --traffic-split=0=100
```

### Vertex AI Pipelines for MLOps

```python
# Create ML pipeline for automated retraining
from kfp import dsl
from kfp.v2 import compiler
from google.cloud import aiplatform

@dsl.pipeline(name="penske-ml-pipeline")
def ml_pipeline(
    project: str,
    location: str,
    training_data: str
):
    # Data preprocessing
    preprocess_op = dsl.ContainerOp(
        name="preprocess",
        image="gcr.io/PROJECT_ID/preprocess:latest",
        arguments=["--input", training_data]
    )
    
    # Training
    train_op = dsl.ContainerOp(
        name="train",
        image="gcr.io/PROJECT_ID/train:latest",
        arguments=["--data", preprocess_op.output]
    )
    
    # Deploy
    deploy_op = dsl.ContainerOp(
        name="deploy",
        image="gcr.io/PROJECT_ID/deploy:latest",
        arguments=["--model", train_op.output]
    )

# Compile and run
compiler.Compiler().compile(ml_pipeline, "pipeline.json")

aiplatform.PipelineJob(
    display_name="penske-ml-pipeline",
    template_path="pipeline.json",
    parameter_values={
        "project": "penske-analytics-prod",
        "location": "us-central1",
        "training_data": "gs://penske-vertex-PROJECT_ID/training/"
    }
).run()
```

### Cleanup Vertex AI Resources

```bash
# Delete endpoint
gcloud ai endpoints delete ENDPOINT_ID \
    --project=$PROJECT_ID \
    --region=$REGION \
    --quiet

# Delete model
gcloud ai models delete MODEL_ID \
    --project=$PROJECT_ID \
    --region=$REGION \
    --quiet

# Delete training jobs
gcloud ai custom-jobs cancel JOB_ID \
    --project=$PROJECT_ID \
    --region=$REGION

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
