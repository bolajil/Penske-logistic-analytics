# Azure Deployment Guide

Complete step-by-step guide for deploying Penske Logistics Analytics to Azure using Container Apps.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Architecture Overview](#2-architecture-overview)
3. [Step 1: Azure Account Setup](#step-1-azure-account-setup)
4. [Step 2: Create Azure Container Registry](#step-2-create-azure-container-registry)
5. [Step 3: Build and Push Docker Image](#step-3-build-and-push-docker-image)
6. [Step 4: Create Container Apps Environment](#step-4-create-container-apps-environment)
7. [Step 5: Deploy Container App](#step-5-deploy-container-app)
8. [Step 6: Configure Secrets and Environment](#step-6-configure-secrets-and-environment)
9. [Step 7: Verify Deployment](#step-7-verify-deployment)
10. [Step 8: Set Up CI/CD](#step-8-set-up-cicd-azure-devops)
11. [Troubleshooting](#troubleshooting)
12. [Cost Optimization](#cost-optimization)

---

## 1. Prerequisites

### Required Tools

```bash
# Verify Azure CLI is installed
az --version
# Expected: azure-cli 2.50+

# Verify Docker is installed
docker --version
# Expected: Docker version 20.10+

# Login to Azure
az login

# Set subscription (if multiple)
az account set --subscription "Your-Subscription-Name"
```

### Required Azure Permissions

Your account needs these roles:
- `Contributor` on the resource group
- `AcrPush` on Container Registry
- `Key Vault Secrets User` (if using Key Vault)

---

## 2. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                          Azure Region                               │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │                    Resource Group                              │ │
│  │                                                                │ │
│  │  ┌──────────────────────────────────────────────────────────┐ │ │
│  │  │           Container Apps Environment                      │ │ │
│  │  │  ┌─────────────────┐  ┌─────────────────┐                │ │ │
│  │  │  │  API Container  │  │ Dashboard       │                │ │ │
│  │  │  │  (penske-api)   │  │ (penske-dash)   │                │ │ │
│  │  │  │  Port: 8000     │  │ Port: 8501      │                │ │ │
│  │  │  └────────┬────────┘  └────────┬────────┘                │ │ │
│  │  │           └──────────┬─────────┘                          │ │ │
│  │  │                      │                                    │ │ │
│  │  │           ┌──────────┴──────────┐                         │ │ │
│  │  │           │  Ingress Controller │                         │ │ │
│  │  │           │  (HTTPS enabled)    │                         │ │ │
│  │  │           └──────────┬──────────┘                         │ │ │
│  │  └──────────────────────┼────────────────────────────────────┘ │ │
│  │                         │                                      │ │
│  │  ┌──────────────────────┼──────────────────────────────────┐  │ │
│  │  │         Azure Container Registry (ACR)                   │  │ │
│  │  │         penskeacr.azurecr.io                            │  │ │
│  │  └─────────────────────────────────────────────────────────┘  │ │
│  │                                                                │ │
│  │  ┌─────────────────┐  ┌─────────────────┐                     │ │
│  │  │   Key Vault     │  │  Log Analytics  │                     │ │
│  │  │   (Secrets)     │  │  (Monitoring)   │                     │ │
│  │  └─────────────────┘  └─────────────────┘                     │ │
│  └────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

### Components Created

| Component | Description | Purpose |
|-----------|-------------|---------|
| Resource Group | Logical container | Organize all resources |
| Container Registry | Docker image storage | Host application images |
| Container Apps Environment | Managed Kubernetes | Run containers |
| Container App (API) | FastAPI service | Backend API |
| Container App (Dashboard) | Streamlit app | Frontend dashboard |
| Key Vault | Secrets management | Store API keys |
| Log Analytics | Centralized logging | Monitor application |

---

## Step 1: Azure Account Setup

### 1.1 Set Environment Variables

```bash
# Set your variables
export RESOURCE_GROUP="penske-analytics-rg"
export LOCATION="eastus"
export ACR_NAME="penskeacr$(date +%s)"  # Must be globally unique
export ENVIRONMENT_NAME="penske-env"
export APP_NAME="penske-analytics"

# Verify logged in
az account show --query name
```

### 1.2 Create Resource Group

```bash
# Create resource group
az group create \
    --name $RESOURCE_GROUP \
    --location $LOCATION

# Verify
az group show --name $RESOURCE_GROUP --query provisioningState
```

**Expected Output:** `"Succeeded"`

---

## Step 2: Create Azure Container Registry

### 2.1 Create ACR

```bash
# Create Container Registry
az acr create \
    --resource-group $RESOURCE_GROUP \
    --name $ACR_NAME \
    --sku Basic \
    --admin-enabled true

# Get ACR login server
export ACR_LOGIN_SERVER=$(az acr show \
    --name $ACR_NAME \
    --query loginServer \
    --output tsv)

echo "ACR Server: $ACR_LOGIN_SERVER"
```

### 2.2 Login to ACR

```bash
# Login to ACR
az acr login --name $ACR_NAME
```

**Expected Output:** `Login Succeeded`

---

## Step 3: Build and Push Docker Image

### 3.1 Build the Image

```bash
# Navigate to project root
cd /path/to/penske-logistics-analytics

# Build Docker image
docker build -t penske-logistics-analytics:latest -f deploy/Dockerfile .
```

### 3.2 Tag and Push to ACR

```bash
# Tag for ACR
docker tag penske-logistics-analytics:latest $ACR_LOGIN_SERVER/penske-logistics-analytics:latest
docker tag penske-logistics-analytics:latest $ACR_LOGIN_SERVER/penske-logistics-analytics:v1.0.0

# Push to ACR
docker push $ACR_LOGIN_SERVER/penske-logistics-analytics:latest
docker push $ACR_LOGIN_SERVER/penske-logistics-analytics:v1.0.0
```

### 3.3 Verify Image in ACR

```bash
az acr repository list --name $ACR_NAME --output table
az acr repository show-tags --name $ACR_NAME --repository penske-logistics-analytics
```

---

## Step 4: Create Container Apps Environment

### 4.1 Install Container Apps Extension

```bash
# Add extension
az extension add --name containerapp --upgrade

# Register providers
az provider register --namespace Microsoft.App
az provider register --namespace Microsoft.OperationalInsights

# Wait for registration (may take a few minutes)
az provider show -n Microsoft.App --query "registrationState"
```

### 4.2 Create Log Analytics Workspace

```bash
# Create Log Analytics workspace
az monitor log-analytics workspace create \
    --resource-group $RESOURCE_GROUP \
    --workspace-name penske-logs

# Get workspace credentials
export LOG_ANALYTICS_WORKSPACE_ID=$(az monitor log-analytics workspace show \
    --resource-group $RESOURCE_GROUP \
    --workspace-name penske-logs \
    --query customerId \
    --output tsv)

export LOG_ANALYTICS_KEY=$(az monitor log-analytics workspace get-shared-keys \
    --resource-group $RESOURCE_GROUP \
    --workspace-name penske-logs \
    --query primarySharedKey \
    --output tsv)
```

### 4.3 Create Container Apps Environment

```bash
# Create environment
az containerapp env create \
    --name $ENVIRONMENT_NAME \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --logs-workspace-id $LOG_ANALYTICS_WORKSPACE_ID \
    --logs-workspace-key $LOG_ANALYTICS_KEY

# Verify
az containerapp env show \
    --name $ENVIRONMENT_NAME \
    --resource-group $RESOURCE_GROUP \
    --query provisioningState
```

**Expected Output:** `"Succeeded"`

---

## Step 5: Deploy Container App

### 5.1 Get ACR Credentials

```bash
export ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username --output tsv)
export ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query passwords[0].value --output tsv)
```

### 5.2 Deploy API Container

```bash
# Deploy API
az containerapp create \
    --name penske-api \
    --resource-group $RESOURCE_GROUP \
    --environment $ENVIRONMENT_NAME \
    --image $ACR_LOGIN_SERVER/penske-logistics-analytics:latest \
    --target-port 8000 \
    --ingress external \
    --registry-server $ACR_LOGIN_SERVER \
    --registry-username $ACR_USERNAME \
    --registry-password $ACR_PASSWORD \
    --cpu 1.0 \
    --memory 2.0Gi \
    --min-replicas 1 \
    --max-replicas 10 \
    --env-vars "PYTHONPATH=/app"

# Get API URL
export API_URL=$(az containerapp show \
    --name penske-api \
    --resource-group $RESOURCE_GROUP \
    --query properties.configuration.ingress.fqdn \
    --output tsv)

echo "API URL: https://$API_URL"
```

### 5.3 Deploy Dashboard Container

```bash
# Deploy Dashboard
az containerapp create \
    --name penske-dashboard \
    --resource-group $RESOURCE_GROUP \
    --environment $ENVIRONMENT_NAME \
    --image $ACR_LOGIN_SERVER/penske-logistics-analytics:latest \
    --target-port 8501 \
    --ingress external \
    --registry-server $ACR_LOGIN_SERVER \
    --registry-username $ACR_USERNAME \
    --registry-password $ACR_PASSWORD \
    --cpu 1.0 \
    --memory 2.0Gi \
    --min-replicas 1 \
    --max-replicas 5 \
    --command "streamlit" "run" "app/streamlit_dashboard.py" "--server.port=8501" "--server.address=0.0.0.0" \
    --env-vars "PYTHONPATH=/app"

# Get Dashboard URL
export DASHBOARD_URL=$(az containerapp show \
    --name penske-dashboard \
    --resource-group $RESOURCE_GROUP \
    --query properties.configuration.ingress.fqdn \
    --output tsv)

echo "Dashboard URL: https://$DASHBOARD_URL"
```

---

## Step 6: Configure Secrets and Environment

### 6.1 Create Key Vault

```bash
# Create Key Vault
az keyvault create \
    --name penske-kv-$(date +%s) \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION

export KEY_VAULT_NAME=$(az keyvault list \
    --resource-group $RESOURCE_GROUP \
    --query "[0].name" \
    --output tsv)
```

### 6.2 Add Secrets

```bash
# Add OpenAI API Key
az keyvault secret set \
    --vault-name $KEY_VAULT_NAME \
    --name "openai-api-key" \
    --value "sk-your-actual-key-here"
```

### 6.3 Update Container App with Secrets

```bash
# Add secret to container app
az containerapp secret set \
    --name penske-api \
    --resource-group $RESOURCE_GROUP \
    --secrets "openai-key=secretref:$KEY_VAULT_NAME/openai-api-key"

# Update environment variables
az containerapp update \
    --name penske-api \
    --resource-group $RESOURCE_GROUP \
    --set-env-vars "OPENAI_API_KEY=secretref:openai-key"
```

---

## Step 7: Verify Deployment

### 7.1 Check Container App Status

```bash
# Check API status
az containerapp show \
    --name penske-api \
    --resource-group $RESOURCE_GROUP \
    --query "{Status:properties.provisioningState,Replicas:properties.template.scale}" \
    --output table

# Check Dashboard status
az containerapp show \
    --name penske-dashboard \
    --resource-group $RESOURCE_GROUP \
    --query "{Status:properties.provisioningState,Replicas:properties.template.scale}" \
    --output table
```

### 7.2 Test Endpoints

```bash
# Test API health
curl https://$API_URL/

# Test Dashboard (should return HTML)
curl -I https://$DASHBOARD_URL/
```

### 7.3 View Logs

```bash
# View API logs
az containerapp logs show \
    --name penske-api \
    --resource-group $RESOURCE_GROUP \
    --follow

# View Dashboard logs
az containerapp logs show \
    --name penske-dashboard \
    --resource-group $RESOURCE_GROUP \
    --follow
```

### 7.4 Access Applications

```bash
echo "============================================"
echo "DEPLOYMENT COMPLETE!"
echo "============================================"
echo "API URL:       https://$API_URL"
echo "Dashboard URL: https://$DASHBOARD_URL"
echo "============================================"
```

---

## Step 8: Set Up CI/CD (Azure DevOps)

### 8.1 Create Service Connection

1. Go to Azure DevOps > Project Settings > Service Connections
2. Create new "Azure Resource Manager" connection
3. Select subscription and resource group
4. Name it: `penske-azure`

### 8.2 Create Pipeline

The `azure-pipelines.yml` is already configured. To use it:

1. Go to Azure DevOps > Pipelines > New Pipeline
2. Select your repository (GitHub/Azure Repos)
3. Select "Existing Azure Pipelines YAML file"
4. Path: `deploy/azure/azure-pipelines.yml`
5. Save and run

### 8.3 Pipeline Stages

| Stage | Trigger | Action |
|-------|---------|--------|
| Build | All branches | Run tests, build image |
| Docker | After Build | Push to ACR |
| DeployDev | `develop` branch | Deploy to dev environment |
| DeployProd | `main` branch | Deploy to production |

---

## Troubleshooting

### Issue: Container Won't Start

```bash
# Check container logs
az containerapp logs show \
    --name penske-api \
    --resource-group $RESOURCE_GROUP \
    --type console

# Check revision status
az containerapp revision list \
    --name penske-api \
    --resource-group $RESOURCE_GROUP \
    --query "[].{Name:name,Status:properties.healthState,Created:properties.createdTime}" \
    --output table
```

### Issue: Image Pull Failed

```bash
# Verify ACR access
az acr repository show --name $ACR_NAME --repository penske-logistics-analytics

# Re-configure registry credentials
az containerapp registry set \
    --name penske-api \
    --resource-group $RESOURCE_GROUP \
    --server $ACR_LOGIN_SERVER \
    --username $ACR_USERNAME \
    --password $ACR_PASSWORD
```

### Issue: Health Check Failing

```bash
# Update health probe settings
az containerapp update \
    --name penske-api \
    --resource-group $RESOURCE_GROUP \
    --set-env-vars "HEALTH_CHECK_PATH=/"
```

### Common Fixes

| Issue | Solution |
|-------|----------|
| 502 Bad Gateway | Check target port matches app port |
| Image not found | Verify ACR name and image tag |
| Out of memory | Increase memory allocation |
| Timeout | Increase startup probe timeout |

---

## Cost Optimization

### Development Environment

```bash
# Scale down for dev
az containerapp update \
    --name penske-api \
    --resource-group $RESOURCE_GROUP \
    --cpu 0.25 \
    --memory 0.5Gi \
    --min-replicas 0 \
    --max-replicas 1
```

### Production Tips

| Optimization | Savings |
|--------------|---------|
| Scale to zero (dev) | 90%+ when idle |
| Use consumption plan | Pay per request |
| Right-size containers | 20-40% |
| Reserved instances | 30-50% |

### Estimated Monthly Costs

| Component | Dev | Prod |
|-----------|-----|------|
| Container Apps | $10 | $50 |
| ACR (Basic) | $5 | $5 |
| Log Analytics | $5 | $20 |
| Key Vault | $1 | $1 |
| **Total** | **~$21** | **~$76** |

---

## Cleanup

To delete all resources:

```bash
# Delete resource group (deletes everything)
az group delete \
    --name $RESOURCE_GROUP \
    --yes \
    --no-wait

# Verify deletion
az group show --name $RESOURCE_GROUP 2>/dev/null || echo "Resource group deleted"
```

---

## Next Steps

1. **Custom Domain:** Configure Azure DNS and managed certificates
2. **Authentication:** Add Azure AD authentication
3. **Monitoring:** Set up Azure Monitor alerts
4. **Scaling Rules:** Configure HTTP-based scaling

---

**[← Back to Main Guide](../README.md)** | **[AWS Guide](../aws/DEPLOYMENT_GUIDE.md)** | **[GCP Guide →](../gcp/DEPLOYMENT_GUIDE.md)**
