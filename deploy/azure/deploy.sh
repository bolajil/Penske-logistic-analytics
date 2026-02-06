#!/bin/bash
# Azure Deployment Script for Penske Logistics Analytics
# Usage: ./deploy.sh [environment]
# Example: ./deploy.sh prod

set -e

# Configuration
ENVIRONMENT=${1:-dev}
LOCATION=${AZURE_LOCATION:-eastus}
RESOURCE_GROUP="penske-analytics-${ENVIRONMENT}-rg"
ACR_NAME="penskeacr${ENVIRONMENT}$(date +%s | tail -c 6)"
ENVIRONMENT_NAME="penske-env-${ENVIRONMENT}"

echo "============================================"
echo "Azure Deployment - Penske Logistics Analytics"
echo "============================================"
echo "Environment: $ENVIRONMENT"
echo "Location: $LOCATION"
echo "Resource Group: $RESOURCE_GROUP"
echo "============================================"

# Step 1: Create Resource Group
echo "[1/7] Creating resource group..."
az group create --name $RESOURCE_GROUP --location $LOCATION --output none

# Step 2: Create ACR
echo "[2/7] Creating Container Registry..."
az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic --admin-enabled true --output none
ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --query loginServer --output tsv)
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username --output tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query passwords[0].value --output tsv)

# Step 3: Login and Push Image
echo "[3/7] Building and pushing Docker image..."
az acr login --name $ACR_NAME
cd ../..
docker build -t penske-analytics:latest -f deploy/Dockerfile .
docker tag penske-analytics:latest ${ACR_LOGIN_SERVER}/penske-analytics:latest
docker push ${ACR_LOGIN_SERVER}/penske-analytics:latest
cd deploy/azure

# Step 4: Create Log Analytics
echo "[4/7] Creating Log Analytics workspace..."
az monitor log-analytics workspace create \
    --resource-group $RESOURCE_GROUP \
    --workspace-name penske-logs-${ENVIRONMENT} \
    --output none

LOG_ANALYTICS_ID=$(az monitor log-analytics workspace show \
    --resource-group $RESOURCE_GROUP \
    --workspace-name penske-logs-${ENVIRONMENT} \
    --query customerId --output tsv)
LOG_ANALYTICS_KEY=$(az monitor log-analytics workspace get-shared-keys \
    --resource-group $RESOURCE_GROUP \
    --workspace-name penske-logs-${ENVIRONMENT} \
    --query primarySharedKey --output tsv)

# Step 5: Create Container Apps Environment
echo "[5/7] Creating Container Apps environment..."
az containerapp env create \
    --name $ENVIRONMENT_NAME \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --logs-workspace-id $LOG_ANALYTICS_ID \
    --logs-workspace-key $LOG_ANALYTICS_KEY \
    --output none

# Step 6: Deploy API
echo "[6/7] Deploying API container..."
az containerapp create \
    --name penske-api-${ENVIRONMENT} \
    --resource-group $RESOURCE_GROUP \
    --environment $ENVIRONMENT_NAME \
    --image ${ACR_LOGIN_SERVER}/penske-analytics:latest \
    --target-port 8000 \
    --ingress external \
    --registry-server $ACR_LOGIN_SERVER \
    --registry-username $ACR_USERNAME \
    --registry-password $ACR_PASSWORD \
    --cpu 1.0 --memory 2.0Gi \
    --min-replicas 1 --max-replicas 10 \
    --output none

# Step 7: Deploy Dashboard
echo "[7/7] Deploying Dashboard container..."
az containerapp create \
    --name penske-dashboard-${ENVIRONMENT} \
    --resource-group $RESOURCE_GROUP \
    --environment $ENVIRONMENT_NAME \
    --image ${ACR_LOGIN_SERVER}/penske-analytics:latest \
    --target-port 8501 \
    --ingress external \
    --registry-server $ACR_LOGIN_SERVER \
    --registry-username $ACR_USERNAME \
    --registry-password $ACR_PASSWORD \
    --cpu 1.0 --memory 2.0Gi \
    --min-replicas 1 --max-replicas 5 \
    --command "streamlit" "run" "app/streamlit_dashboard.py" "--server.port=8501" "--server.address=0.0.0.0" \
    --output none

# Get outputs
API_URL=$(az containerapp show --name penske-api-${ENVIRONMENT} --resource-group $RESOURCE_GROUP --query properties.configuration.ingress.fqdn --output tsv)
DASHBOARD_URL=$(az containerapp show --name penske-dashboard-${ENVIRONMENT} --resource-group $RESOURCE_GROUP --query properties.configuration.ingress.fqdn --output tsv)

echo ""
echo "============================================"
echo "DEPLOYMENT COMPLETE!"
echo "============================================"
echo "API URL:       https://${API_URL}"
echo "Dashboard URL: https://${DASHBOARD_URL}"
echo "Resource Group: $RESOURCE_GROUP"
echo "============================================"
