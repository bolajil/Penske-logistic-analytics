#!/bin/bash
# GCP Deployment Script for Penske Logistics Analytics
# Usage: ./deploy.sh [environment]
# Example: ./deploy.sh prod

set -e

# Configuration
ENVIRONMENT=${1:-dev}
PROJECT_ID=${GCP_PROJECT_ID:-$(gcloud config get-value project)}
REGION=${GCP_REGION:-us-central1}

echo "============================================"
echo "GCP Deployment - Penske Logistics Analytics"
echo "============================================"
echo "Environment: $ENVIRONMENT"
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "============================================"

# Step 1: Enable APIs
echo "[1/6] Enabling required APIs..."
gcloud services enable \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    cloudbuild.googleapis.com \
    --quiet

# Step 2: Create Artifact Registry
echo "[2/6] Creating Artifact Registry repository..."
gcloud artifacts repositories create penske-analytics-${ENVIRONMENT} \
    --repository-format=docker \
    --location=$REGION \
    --description="Penske Analytics ${ENVIRONMENT}" \
    2>/dev/null || echo "Repository already exists"

ARTIFACT_REPO="${REGION}-docker.pkg.dev/${PROJECT_ID}/penske-analytics-${ENVIRONMENT}"

# Step 3: Configure Docker and Build
echo "[3/6] Configuring Docker authentication..."
gcloud auth configure-docker ${REGION}-docker.pkg.dev --quiet

echo "[4/6] Building and pushing Docker image..."
cd ../..
docker build -t penske-analytics:latest -f deploy/Dockerfile .
docker tag penske-analytics:latest ${ARTIFACT_REPO}/penske-analytics:latest
docker push ${ARTIFACT_REPO}/penske-analytics:latest
cd deploy/gcp

# Step 5: Deploy API
echo "[5/6] Deploying API to Cloud Run..."
gcloud run deploy penske-api-${ENVIRONMENT} \
    --image=${ARTIFACT_REPO}/penske-analytics:latest \
    --platform=managed \
    --region=$REGION \
    --port=8000 \
    --memory=2Gi \
    --cpu=1 \
    --min-instances=0 \
    --max-instances=10 \
    --timeout=300 \
    --set-env-vars="PYTHONPATH=/app" \
    --allow-unauthenticated \
    --quiet

# Step 6: Deploy Dashboard
echo "[6/6] Deploying Dashboard to Cloud Run..."
gcloud run deploy penske-dashboard-${ENVIRONMENT} \
    --image=${ARTIFACT_REPO}/penske-analytics:latest \
    --platform=managed \
    --region=$REGION \
    --port=8501 \
    --memory=2Gi \
    --cpu=1 \
    --min-instances=0 \
    --max-instances=5 \
    --timeout=300 \
    --set-env-vars="PYTHONPATH=/app" \
    --command="streamlit" \
    --args="run,app/streamlit_dashboard.py,--server.port=8501,--server.address=0.0.0.0" \
    --allow-unauthenticated \
    --quiet

# Get outputs
API_URL=$(gcloud run services describe penske-api-${ENVIRONMENT} --region=$REGION --format='value(status.url)')
DASHBOARD_URL=$(gcloud run services describe penske-dashboard-${ENVIRONMENT} --region=$REGION --format='value(status.url)')

echo ""
echo "============================================"
echo "DEPLOYMENT COMPLETE!"
echo "============================================"
echo "API URL:       ${API_URL}"
echo "Dashboard URL: ${DASHBOARD_URL}"
echo "Project:       ${PROJECT_ID}"
echo "Region:        ${REGION}"
echo "============================================"
