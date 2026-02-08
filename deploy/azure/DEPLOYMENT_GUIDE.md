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
11. [Azure OpenAI Service Integration](#azure-openai-service-integration)
12. [Azure Machine Learning Integration](#azure-machine-learning-integration)
13. [Troubleshooting](#troubleshooting)
14. [Cost Optimization](#cost-optimization)

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

## Azure OpenAI Service Integration

Azure OpenAI Service provides access to OpenAI's powerful language models with enterprise security and compliance.

### Create Azure OpenAI Resource

```bash
# Create Azure OpenAI resource
az cognitiveservices account create \
    --name penske-openai \
    --resource-group $RESOURCE_GROUP \
    --kind OpenAI \
    --sku S0 \
    --location eastus \
    --custom-domain penske-openai

# Get endpoint and key
export AZURE_OPENAI_ENDPOINT=$(az cognitiveservices account show \
    --name penske-openai \
    --resource-group $RESOURCE_GROUP \
    --query properties.endpoint \
    --output tsv)

export AZURE_OPENAI_KEY=$(az cognitiveservices account keys list \
    --name penske-openai \
    --resource-group $RESOURCE_GROUP \
    --query key1 \
    --output tsv)
```

### Deploy Models

```bash
# Deploy GPT-4 model
az cognitiveservices account deployment create \
    --name penske-openai \
    --resource-group $RESOURCE_GROUP \
    --deployment-name gpt-4 \
    --model-name gpt-4 \
    --model-version "0613" \
    --model-format OpenAI \
    --sku-capacity 10 \
    --sku-name Standard

# Deploy text-embedding-ada-002 for embeddings
az cognitiveservices account deployment create \
    --name penske-openai \
    --resource-group $RESOURCE_GROUP \
    --deployment-name text-embedding \
    --model-name text-embedding-ada-002 \
    --model-version "2" \
    --model-format OpenAI \
    --sku-capacity 10 \
    --sku-name Standard
```

### Available Models for Logistics Analytics

| Model | Use Case | Best For |
|-------|----------|----------|
| **GPT-4** | Complex reasoning | Route optimization, demand analysis |
| **GPT-4 Turbo** | Fast responses | Real-time logistics queries |
| **GPT-3.5 Turbo** | Cost-effective | High-volume text processing |
| **text-embedding-ada-002** | Vector search | Semantic search on logistics data |

### Azure OpenAI API Integration

```python
# src/services/azure_openai_service.py
from openai import AzureOpenAI
import os

class AzureOpenAIService:
    def __init__(self):
        self.client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_KEY"),
            api_version="2024-02-15-preview",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
    
    def analyze_logistics_data(self, prompt: str, deployment_name: str = "gpt-4"):
        """Analyze logistics data using Azure OpenAI."""
        response = self.client.chat.completions.create(
            model=deployment_name,
            messages=[
                {"role": "system", "content": "You are a logistics analytics expert."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=4096,
            temperature=0.7
        )
        return response.choices[0].message.content
    
    def generate_embeddings(self, text: str, deployment_name: str = "text-embedding"):
        """Generate embeddings for semantic search."""
        response = self.client.embeddings.create(
            model=deployment_name,
            input=text
        )
        return response.data[0].embedding
    
    def stream_analysis(self, prompt: str, deployment_name: str = "gpt-4"):
        """Stream logistics analysis for real-time updates."""
        response = self.client.chat.completions.create(
            model=deployment_name,
            messages=[
                {"role": "system", "content": "You are a logistics analytics expert."},
                {"role": "user", "content": prompt}
            ],
            stream=True
        )
        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
```

### Azure OpenAI Use Cases for Penske Analytics

```python
# Example: Route Optimization Analysis
azure_openai = AzureOpenAIService()

prompt = """
Analyze this logistics route data and suggest optimizations:
- Current route: Chicago → Indianapolis → Louisville → Nashville
- Total distance: 478 miles
- Average delivery time: 8.5 hours
- Fuel consumption: 65 gallons

Consider traffic patterns, fuel efficiency, and delivery windows.
"""

analysis = azure_openai.analyze_logistics_data(prompt)
print(analysis)
```

### Store Secrets in Key Vault

```bash
# Store Azure OpenAI credentials
az keyvault secret set \
    --vault-name $KEY_VAULT_NAME \
    --name "azure-openai-key" \
    --value "$AZURE_OPENAI_KEY"

az keyvault secret set \
    --vault-name $KEY_VAULT_NAME \
    --name "azure-openai-endpoint" \
    --value "$AZURE_OPENAI_ENDPOINT"

# Update Container App with secrets
az containerapp secret set \
    --name penske-api-${ENVIRONMENT} \
    --resource-group $RESOURCE_GROUP \
    --secrets "azure-openai-key=keyvaultref:${KEY_VAULT_NAME}/azure-openai-key,identityref:/subscriptions/.../identities/..."
```

### Azure OpenAI Costs

| Model | Input (per 1K tokens) | Output (per 1K tokens) |
|-------|----------------------|------------------------|
| GPT-4 | $0.03 | $0.06 |
| GPT-4 Turbo | $0.01 | $0.03 |
| GPT-3.5 Turbo | $0.0005 | $0.0015 |
| text-embedding-ada-002 | $0.0001 | - |

---

## Azure Machine Learning Integration

Azure Machine Learning (Azure ML) enables training, deploying, and managing custom ML models for logistics predictions. This section provides a complete walkthrough from data preparation to production deployment.

### What You Will Accomplish

By following this guide, you will:
1. **Set up Azure ML workspace** - Create the infrastructure for ML operations
2. **Prepare and upload training data** - Format logistics data for model training
3. **Train a custom model** - Run training jobs on Azure compute clusters
4. **Deploy to managed endpoint** - Host your model for real-time predictions
5. **Make predictions** - Call the endpoint from your application

### Azure ML Architecture Overview

```
┌───────────────────────────────────────────────────────────────────────────────────┐
│                           Azure ML Pipeline                                        │
│                                                                                    │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐  │
│  │  Blob Store  │ ──▶ │   Compute    │ ──▶ │    Model     │ ──▶ │   Managed    │  │
│  │              │     │   Cluster    │     │   Registry   │     │   Endpoint   │  │
│  │ • train.csv  │     │              │     │              │     │              │  │
│  │ • valid.csv  │     │ Runs your    │     │ Versioned    │     │ Real-time    │  │
│  │              │     │ train.py     │     │ model files  │     │ predictions  │  │
│  └──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘  │
│                                                                                    │
│  Data stored in:       Training runs on:   Model saved to:      Endpoint URL:     │
│  workspaceblobstore    penske-cluster      penske-demand-model  *.inference.ml    │
└───────────────────────────────────────────────────────────────────────────────────┘
```

---

### Step 1: Create Azure ML Workspace

**What we're doing:** Creating an Azure ML workspace which serves as the central hub for all ML operations including experiments, models, endpoints, and compute resources.

**What gets created:**
- ML Workspace (control plane)
- Storage Account (for data and models)
- Key Vault (for secrets)
- Application Insights (for monitoring)
- Container Registry (for Docker images)

```bash
# Set environment variables
export RESOURCE_GROUP="penske-analytics-rg"
export LOCATION="eastus"
export WORKSPACE_NAME="penske-ml-workspace"

# Install Azure ML CLI extension
az extension add --name ml --upgrade

# Create resource group if not exists
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create ML workspace
az ml workspace create \
    --name $WORKSPACE_NAME \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION

# Verify workspace creation
az ml workspace show \
    --name $WORKSPACE_NAME \
    --resource-group $RESOURCE_GROUP \
    --query "{name:name, location:location, storageAccount:storage_account}"
```

**Expected Output:**
```json
{
  "name": "penske-ml-workspace",
  "location": "eastus",
  "storageAccount": "/subscriptions/.../storageAccounts/penskemlworkspace1234"
}
```

---

### Step 2: Prepare Training Data

**What we're doing:** Creating properly formatted CSV files and uploading them to Azure Blob Storage (the workspace's default datastore).

**Data format requirements:**
- CSV files with feature columns and a `target` column
- Split into training (80%) and validation (20%) sets

#### 2.1 Create Training Data Locally

**Create file: `scripts/generate_azure_training_data.py`**

```python
#!/usr/bin/env python3
"""
Generate training data for Azure ML demand forecasting model.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def generate_logistics_training_data(num_samples=10000, output_dir='data/azure_training'):
    """Generate sample training data for demand forecasting."""
    
    np.random.seed(42)
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate date range
    start_date = datetime(2023, 1, 1)
    dates = [start_date + timedelta(days=i) for i in range(num_samples)]
    
    # Generate features
    data = {
        'date': dates,
        'region': np.random.choice(['Northeast', 'Midwest', 'Southeast', 'Southwest', 'West'], num_samples),
        'shipment_volume': np.random.randint(500, 2000, num_samples),
        'fuel_price': np.random.uniform(3.0, 4.5, num_samples).round(2),
        'weather_severity': np.random.choice([0, 1, 2], num_samples, p=[0.7, 0.2, 0.1]),
        'day_of_week': [d.isoweekday() for d in dates],
        'is_holiday': np.random.choice([0, 1], num_samples, p=[0.95, 0.05]),
        'previous_day_volume': np.random.randint(500, 2000, num_samples),
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
    
    # Encode categorical variables
    df = pd.get_dummies(df, columns=['region'], drop_first=True)
    df = df.drop('date', axis=1)
    
    # Split into train/validation
    train_size = int(len(df) * 0.8)
    train_df = df[:train_size]
    valid_df = df[train_size:]
    
    # Save to CSV
    train_path = os.path.join(output_dir, 'train.csv')
    valid_path = os.path.join(output_dir, 'validation.csv')
    
    train_df.to_csv(train_path, index=False)
    valid_df.to_csv(valid_path, index=False)
    
    print(f"=" * 60)
    print("AZURE ML TRAINING DATA GENERATED")
    print(f"=" * 60)
    print(f"Training data: {len(train_df)} rows → {train_path}")
    print(f"Validation data: {len(valid_df)} rows → {valid_path}")
    print(f"\nFeatures ({len(train_df.columns) - 1}):")
    for col in train_df.columns:
        if col != 'target':
            print(f"  - {col}")
    print(f"\nTarget column: target")
    print(f"=" * 60)
    
    return train_df, valid_df

if __name__ == '__main__':
    generate_logistics_training_data()
```

**Run the script:**
```bash
python scripts/generate_azure_training_data.py
```

**Expected Output:**
```
============================================================
AZURE ML TRAINING DATA GENERATED
============================================================
Training data: 8000 rows → data/azure_training/train.csv
Validation data: 2000 rows → data/azure_training/validation.csv

Features (10):
  - shipment_volume
  - fuel_price
  - weather_severity
  - day_of_week
  - is_holiday
  - previous_day_volume
  - region_Midwest
  - region_Northeast
  - region_Southeast
  - region_West

Target column: target
============================================================
```

#### 2.2 Upload Data to Azure ML Datastore

```bash
# Upload training data to workspace default datastore
az ml data create \
    --name penske-training-data \
    --version 1 \
    --path data/azure_training/ \
    --type uri_folder \
    --workspace-name $WORKSPACE_NAME \
    --resource-group $RESOURCE_GROUP

# Verify upload
az ml data show \
    --name penske-training-data \
    --version 1 \
    --workspace-name $WORKSPACE_NAME \
    --resource-group $RESOURCE_GROUP
```

**Expected Output:**
```json
{
  "name": "penske-training-data",
  "version": "1",
  "path": "azureml://datastores/workspaceblobstore/paths/LocalUpload/.../penske-training-data/",
  "type": "uri_folder"
}
```

**Where the data is stored:** `azureml://datastores/workspaceblobstore/paths/LocalUpload/.../`

---

### Step 3: Create Compute Cluster

**What we're doing:** Creating a managed compute cluster that automatically scales from 0 to N nodes based on training job demand.

**Why scale to 0:** When no jobs are running, the cluster scales down to 0 nodes, so you only pay when training.

```bash
# Create compute cluster for training
az ml compute create \
    --name penske-cluster \
    --type AmlCompute \
    --size Standard_DS3_v2 \
    --min-instances 0 \
    --max-instances 4 \
    --idle-time-before-scale-down 1800 \
    --workspace-name $WORKSPACE_NAME \
    --resource-group $RESOURCE_GROUP

# Verify cluster creation
az ml compute show \
    --name penske-cluster \
    --workspace-name $WORKSPACE_NAME \
    --resource-group $RESOURCE_GROUP
```

**Expected Output:**
```json
{
  "name": "penske-cluster",
  "type": "amlcompute",
  "size": "STANDARD_DS3_V2",
  "min_instances": 0,
  "max_instances": 4,
  "provisioning_state": "Succeeded"
}
```

| VM Size | vCPUs | RAM | Cost/Hour | Best For |
|---------|-------|-----|-----------|----------|
| Standard_DS2_v2 | 2 | 7 GB | $0.146 | Small models |
| Standard_DS3_v2 | 4 | 14 GB | $0.293 | Medium models |
| Standard_DS4_v2 | 8 | 28 GB | $0.585 | Large models |

---

### Step 4: Create Training Script

**What we're doing:** Writing the Python script that Azure ML will execute on the compute cluster.

**Where this runs:** On a node in `penske-cluster` that Azure ML provisions automatically.

**Output location:** Model files are saved to `./outputs/` which Azure ML automatically uploads to the run's artifacts.

**Create file: `src/ml/scripts/train_azure.py`**

```python
#!/usr/bin/env python3
"""
Azure ML Training Script for Penske Demand Forecasting

This script runs on Azure ML compute cluster.
Azure ML automatically:
  - Provisions compute nodes
  - Mounts data from datastore to --data path
  - Uploads ./outputs/ and ./logs/ to run artifacts
  - Logs metrics to MLflow (integrated with Azure ML)
"""

import argparse
import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import json
import mlflow

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser()
    
    # Data path (mounted by Azure ML)
    parser.add_argument('--data', type=str, required=True,
                       help='Path to training data folder')
    
    # Hyperparameters
    parser.add_argument('--n_estimators', type=int, default=100)
    parser.add_argument('--max_depth', type=int, default=10)
    parser.add_argument('--min_samples_split', type=int, default=5)
    parser.add_argument('--min_samples_leaf', type=int, default=2)
    
    return parser.parse_args()

def load_data(data_path):
    """Load training and validation data from mounted datastore."""
    
    train_path = os.path.join(data_path, 'train.csv')
    valid_path = os.path.join(data_path, 'validation.csv')
    
    print(f"Loading training data from: {train_path}")
    train_df = pd.read_csv(train_path)
    print(f"  Training samples: {len(train_df)}")
    
    print(f"Loading validation data from: {valid_path}")
    valid_df = pd.read_csv(valid_path)
    print(f"  Validation samples: {len(valid_df)}")
    
    return train_df, valid_df

def train_model(train_df, args):
    """Train the Random Forest model."""
    
    X_train = train_df.drop('target', axis=1)
    y_train = train_df['target']
    
    print(f"\nTraining with hyperparameters:")
    print(f"  n_estimators: {args.n_estimators}")
    print(f"  max_depth: {args.max_depth}")
    
    # Log hyperparameters to MLflow
    mlflow.log_param("n_estimators", args.n_estimators)
    mlflow.log_param("max_depth", args.max_depth)
    mlflow.log_param("min_samples_split", args.min_samples_split)
    mlflow.log_param("min_samples_leaf", args.min_samples_leaf)
    
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
    """Evaluate model and log metrics to MLflow."""
    
    X_valid = valid_df.drop('target', axis=1)
    y_valid = valid_df['target']
    
    predictions = model.predict(X_valid)
    
    mae = mean_absolute_error(y_valid, predictions)
    rmse = np.sqrt(mean_squared_error(y_valid, predictions))
    r2 = r2_score(y_valid, predictions)
    
    # Log metrics to MLflow (visible in Azure ML Studio)
    mlflow.log_metric("mae", mae)
    mlflow.log_metric("rmse", rmse)
    mlflow.log_metric("r2", r2)
    
    print(f"\nValidation Metrics:")
    print(f"  MAE: {mae:.2f}")
    print(f"  RMSE: {rmse:.2f}")
    print(f"  R²: {r2:.4f}")
    
    return {"mae": mae, "rmse": rmse, "r2": r2}

def save_model(model, metrics, feature_names):
    """Save model to ./outputs/ (Azure ML uploads this automatically)."""
    
    output_dir = './outputs'
    os.makedirs(output_dir, exist_ok=True)
    
    # Save model
    model_path = os.path.join(output_dir, 'model.joblib')
    joblib.dump(model, model_path)
    print(f"\nModel saved to: {model_path}")
    
    # Save feature names
    features_path = os.path.join(output_dir, 'feature_names.json')
    with open(features_path, 'w') as f:
        json.dump(feature_names, f)
    
    # Save metrics
    metrics_path = os.path.join(output_dir, 'metrics.json')
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f)
    
    # Save feature importances
    importances = dict(zip(feature_names, model.feature_importances_.tolist()))
    importances_path = os.path.join(output_dir, 'feature_importances.json')
    with open(importances_path, 'w') as f:
        json.dump(importances, f, indent=2)
    
    # Log model to MLflow
    mlflow.sklearn.log_model(model, "model")
    
    print(f"All artifacts saved to: {output_dir}")

if __name__ == '__main__':
    print("=" * 60)
    print("PENSKE LOGISTICS - AZURE ML TRAINING")
    print("=" * 60)
    
    # Start MLflow run (Azure ML auto-configures tracking)
    with mlflow.start_run():
        args = parse_args()
        
        train_df, valid_df = load_data(args.data)
        model = train_model(train_df, args)
        metrics = evaluate_model(model, valid_df)
        
        feature_names = [col for col in train_df.columns if col != 'target']
        save_model(model, metrics, feature_names)
    
    print("\n" + "=" * 60)
    print("TRAINING COMPLETE - Artifacts uploaded to Azure ML")
    print("=" * 60)
```

---

### Step 5: Submit Training Job

**What we're doing:** Submitting a training job to Azure ML, which will:
1. Provision a node from `penske-cluster`
2. Mount training data to the `--data` path
3. Execute your `train_azure.py` script
4. Upload outputs to run artifacts
5. Log metrics to MLflow
6. Deallocate the node when done

**Where outputs go:** 
- Model artifacts: `azureml://jobs/{run-id}/outputs/`
- MLflow model: Registered in workspace model registry
- Metrics: Visible in Azure ML Studio > Jobs

**Create file: `src/ml/azure_ml_training.py`**

```python
#!/usr/bin/env python3
"""
Submit training job to Azure ML.
"""

from azure.ai.ml import MLClient, command, Input
from azure.ai.ml.constants import AssetTypes
from azure.identity import DefaultAzureCredential
import os

def run_training_job(
    subscription_id: str,
    resource_group: str = "penske-analytics-rg",
    workspace_name: str = "penske-ml-workspace"
):
    """Submit and monitor an Azure ML training job."""
    
    print("=" * 60)
    print("AZURE ML TRAINING JOB")
    print("=" * 60)
    
    # Connect to workspace
    ml_client = MLClient(
        DefaultAzureCredential(),
        subscription_id=subscription_id,
        resource_group_name=resource_group,
        workspace_name=workspace_name
    )
    
    print(f"Workspace: {workspace_name}")
    print(f"Resource Group: {resource_group}")
    print("=" * 60)
    
    # Define training job
    job = command(
        code="./src/ml/scripts",  # Local folder with train_azure.py
        command="python train_azure.py --data ${{inputs.training_data}} --n_estimators 100 --max_depth 10",
        inputs={
            "training_data": Input(
                type=AssetTypes.URI_FOLDER,
                path="azureml:penske-training-data:1"  # Reference to uploaded data
            )
        },
        environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu@latest",
        compute="penske-cluster",
        display_name="penske-demand-forecast-training",
        experiment_name="penske-logistics",
        description="Train demand forecasting model for Penske Logistics"
    )
    
    print("\nSubmitting training job...")
    print("This will take 10-20 minutes (includes cluster startup).\n")
    
    # Submit job
    returned_job = ml_client.jobs.create_or_update(job)
    
    print(f"Job submitted: {returned_job.name}")
    print(f"Studio URL: {returned_job.studio_url}")
    print("\nStreaming logs...\n")
    
    # Stream logs until complete
    ml_client.jobs.stream(returned_job.name)
    
    # Get final status
    job_status = ml_client.jobs.get(returned_job.name)
    
    print("\n" + "=" * 60)
    print("TRAINING COMPLETE!")
    print("=" * 60)
    print(f"Job Name: {returned_job.name}")
    print(f"Status: {job_status.status}")
    print(f"Outputs: azureml://jobs/{returned_job.name}/outputs/")
    print(f"\nView in Azure ML Studio:")
    print(f"  {returned_job.studio_url}")
    print("=" * 60)
    
    return returned_job

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python azure_ml_training.py <subscription_id>")
        print("Get your subscription ID: az account show --query id -o tsv")
        sys.exit(1)
    
    subscription_id = sys.argv[1]
    run_training_job(subscription_id)
```

**Run the training job:**
```bash
# Get your subscription ID
SUBSCRIPTION_ID=$(az account show --query id -o tsv)

# Submit training job
python src/ml/azure_ml_training.py $SUBSCRIPTION_ID
```

**Expected Output:**
```
============================================================
AZURE ML TRAINING JOB
============================================================
Workspace: penske-ml-workspace
Resource Group: penske-analytics-rg
============================================================

Submitting training job...
This will take 10-20 minutes (includes cluster startup).

Job submitted: penske-demand-forecast-training_abc123
Studio URL: https://ml.azure.com/runs/penske-demand-forecast-training_abc123

Streaming logs...

[2024-01-15 10:45:00] Starting job...
[2024-01-15 10:46:30] Cluster scaling up...
[2024-01-15 10:48:00] Running training script...
...
[2024-01-15 10:55:00] Training complete!

============================================================
TRAINING COMPLETE!
============================================================
Job Name: penske-demand-forecast-training_abc123
Status: Completed
Outputs: azureml://jobs/penske-demand-forecast-training_abc123/outputs/

View in Azure ML Studio:
  https://ml.azure.com/runs/penske-demand-forecast-training_abc123
============================================================
```

---

### Step 6: Register and Deploy Model

**What we're doing:** 
1. Registering the trained model in Azure ML Model Registry (version controlled)
2. Creating a managed online endpoint for real-time predictions
3. Deploying the model to the endpoint

**Where the endpoint lives:** `https://penske-demand-forecast.eastus.inference.ml.azure.com`

**Create file: `src/ml/azure_ml_deploy.py`**

```python
#!/usr/bin/env python3
"""
Register model and deploy to Azure ML managed endpoint.
"""

from azure.ai.ml import MLClient
from azure.ai.ml.entities import (
    Model,
    ManagedOnlineEndpoint,
    ManagedOnlineDeployment,
    CodeConfiguration,
    Environment
)
from azure.ai.ml.constants import AssetTypes
from azure.identity import DefaultAzureCredential
import os

def deploy_model(
    subscription_id: str,
    job_name: str,
    resource_group: str = "penske-analytics-rg",
    workspace_name: str = "penske-ml-workspace"
):
    """Register model and deploy to managed endpoint."""
    
    print("=" * 60)
    print("AZURE ML MODEL DEPLOYMENT")
    print("=" * 60)
    
    ml_client = MLClient(
        DefaultAzureCredential(),
        subscription_id=subscription_id,
        resource_group_name=resource_group,
        workspace_name=workspace_name
    )
    
    # Step 1: Register model from job outputs
    print("\n[1/4] Registering model...")
    
    model = Model(
        path=f"azureml://jobs/{job_name}/outputs/artifacts/paths/outputs/",
        name="penske-demand-model",
        description="Demand forecasting model for Penske Logistics",
        type=AssetTypes.CUSTOM_MODEL
    )
    
    registered_model = ml_client.models.create_or_update(model)
    print(f"  Model registered: {registered_model.name} v{registered_model.version}")
    
    # Step 2: Create endpoint
    print("\n[2/4] Creating endpoint...")
    
    endpoint = ManagedOnlineEndpoint(
        name="penske-demand-forecast",
        description="Penske demand forecasting endpoint",
        auth_mode="key"
    )
    
    ml_client.online_endpoints.begin_create_or_update(endpoint).result()
    print(f"  Endpoint created: penske-demand-forecast")
    
    # Step 3: Create deployment
    print("\n[3/4] Deploying model (this takes 5-10 minutes)...")
    
    deployment = ManagedOnlineDeployment(
        name="blue",
        endpoint_name="penske-demand-forecast",
        model=registered_model,
        instance_type="Standard_DS2_v2",
        instance_count=1
    )
    
    ml_client.online_deployments.begin_create_or_update(deployment).result()
    print(f"  Deployment created: blue")
    
    # Step 4: Set traffic
    print("\n[4/4] Routing traffic...")
    
    endpoint.traffic = {"blue": 100}
    ml_client.online_endpoints.begin_create_or_update(endpoint).result()
    
    # Get endpoint details
    endpoint_details = ml_client.online_endpoints.get("penske-demand-forecast")
    
    print("\n" + "=" * 60)
    print("DEPLOYMENT COMPLETE!")
    print("=" * 60)
    print(f"Endpoint Name: penske-demand-forecast")
    print(f"Endpoint URL: {endpoint_details.scoring_uri}")
    print(f"Auth Mode: key")
    print(f"\nGet scoring key:")
    print(f"  az ml online-endpoint get-credentials --name penske-demand-forecast")
    print("=" * 60)
    
    return endpoint_details

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:
        print("Usage: python azure_ml_deploy.py <subscription_id> <job_name>")
        print("Example: python azure_ml_deploy.py abc-123 penske-demand-forecast-training_xyz")
        sys.exit(1)
    
    subscription_id = sys.argv[1]
    job_name = sys.argv[2]
    deploy_model(subscription_id, job_name)
```

**Deploy the model:**
```bash
python src/ml/azure_ml_deploy.py $SUBSCRIPTION_ID penske-demand-forecast-training_abc123
```

**Get the endpoint key:**
```bash
az ml online-endpoint get-credentials \
    --name penske-demand-forecast \
    --workspace-name $WORKSPACE_NAME \
    --resource-group $RESOURCE_GROUP
```

---

### Step 7: Make Predictions

**What we're doing:** Calling the deployed endpoint to get real-time predictions.

**Create file: `src/services/azure_ml_service.py`**

```python
#!/usr/bin/env python3
"""
Azure ML Service for making predictions.
"""

from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential
import json
import urllib.request
import ssl

class AzureMLService:
    """Service for Azure ML endpoint predictions."""
    
    def __init__(
        self,
        subscription_id: str,
        resource_group: str = "penske-analytics-rg",
        workspace_name: str = "penske-ml-workspace",
        endpoint_name: str = "penske-demand-forecast"
    ):
        self.ml_client = MLClient(
            DefaultAzureCredential(),
            subscription_id=subscription_id,
            resource_group_name=resource_group,
            workspace_name=workspace_name
        )
        self.endpoint_name = endpoint_name
        
        # Get endpoint URL and key
        endpoint = self.ml_client.online_endpoints.get(endpoint_name)
        self.scoring_uri = endpoint.scoring_uri
        
        keys = self.ml_client.online_endpoints.get_keys(endpoint_name)
        self.api_key = keys.primary_key
    
    def predict_demand(self, features: list) -> list:
        """
        Predict demand using the deployed model.
        
        Args:
            features: 2D list of feature values
                     Example: [[1250, 3.45, 0, 1, 0, 1180, 0, 1, 0, 0]]
        
        Returns:
            List of predicted demand values
        """
        data = {"data": features}
        body = json.dumps(data).encode('utf-8')
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
        
        req = urllib.request.Request(self.scoring_uri, body, headers)
        
        # Make request
        context = ssl.create_default_context()
        response = urllib.request.urlopen(req, context=context)
        result = json.loads(response.read().decode('utf-8'))
        
        return result
    
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
        print("Usage: python azure_ml_service.py <subscription_id>")
        sys.exit(1)
    
    service = AzureMLService(subscription_id=sys.argv[1])
    
    prediction = service.predict_single(
        shipment_volume=1250,
        fuel_price=3.45,
        weather_severity=0,
        day_of_week=2,
        is_holiday=0,
        previous_day_volume=1180,
        region='Northeast'
    )
    
    print(f"Predicted demand for tomorrow: {prediction:.0f} shipments")
```

**Test predictions:**
```bash
python src/services/azure_ml_service.py $SUBSCRIPTION_ID
```

**Expected Output:**
```
Predicted demand for tomorrow: 1320 shipments
```

---

### Azure ML Summary

| Step | What Happens | Output Location |
|------|--------------|-----------------|
| 1. Create Workspace | Set up ML infrastructure | Azure Portal |
| 2. Prepare Data | Create and upload train.csv | `azureml://datastores/workspaceblobstore/` |
| 3. Create Compute | Provision cluster (scales to 0) | penske-cluster |
| 4. Training Script | Define model logic | `src/ml/scripts/train_azure.py` |
| 5. Submit Job | Train on cluster | `azureml://jobs/{id}/outputs/` |
| 6. Deploy Model | Create endpoint | `*.inference.ml.azure.com` |
| 7. Predictions | Call endpoint API | Real-time results |

### Azure ML Studio URLs - View Your Results

After each step, you can view your resources in Azure ML Studio:

| Resource | URL |
|----------|-----|
| **ML Studio Home** | https://ml.azure.com |
| **Training Data** | https://ml.azure.com → Data → Data assets |
| **Training Jobs** | https://ml.azure.com → Jobs |
| **Model Artifacts** | https://ml.azure.com → Models |
| **Endpoints** | https://ml.azure.com → Endpoints → Real-time endpoints |
| **Compute Clusters** | https://ml.azure.com → Compute → Compute clusters |
| **Experiments & Metrics** | https://ml.azure.com → Jobs → (select job) → Metrics |

**Direct workspace link:**
```
https://ml.azure.com/experiments?wsid=/subscriptions/{SUBSCRIPTION_ID}/resourceGroups/penske-rg/providers/Microsoft.MachineLearningServices/workspaces/penske-ml-workspace
```

> **Tip:** Replace `{SUBSCRIPTION_ID}` with your Azure subscription ID. Find it by running: `az account show --query id -o tsv`

### Azure ML Costs

| Resource | Use Case | Cost |
|----------|----------|------|
| Standard_DS3_v2 | Training (per hour) | $0.293 |
| Standard_DS2_v2 | Endpoint (per hour) | $0.146 |
| Storage | Data + Models (per GB/month) | $0.018 |
| **Typical Training Job** | 15 min on DS3_v2 | ~$0.07 |
| **Endpoint (24/7)** | DS2_v2 per month | ~$105 |

### Cleanup Azure ML Resources

```bash
# Delete endpoint (stops billing immediately)
az ml online-endpoint delete \
    --name penske-demand-forecast \
    --workspace-name $WORKSPACE_NAME \
    --resource-group $RESOURCE_GROUP \
    --yes

# Delete compute cluster
az ml compute delete \
    --name penske-cluster \
    --workspace-name $WORKSPACE_NAME \
    --resource-group $RESOURCE_GROUP \
    --yes

# Delete workspace (removes all resources)
az ml workspace delete \
    --name $WORKSPACE_NAME \
    --resource-group $RESOURCE_GROUP \
    --yes
```

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
