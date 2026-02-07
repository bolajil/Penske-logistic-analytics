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

Azure Machine Learning (Azure ML) enables training, deploying, and managing custom ML models for logistics predictions.

### Azure ML Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                     Azure ML Pipeline                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐ │
│  │  Blob Data  │→ │  Compute    │→ │   Model     │→ │  Managed   │ │
│  │  (input)    │  │  Cluster    │  │  Registry   │  │  Endpoint  │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

### Step 1: Create Azure ML Workspace

```bash
# Install ML extension
az extension add --name ml

# Create ML workspace
az ml workspace create \
    --name penske-ml-workspace \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION

# Get workspace details
az ml workspace show \
    --name penske-ml-workspace \
    --resource-group $RESOURCE_GROUP
```

### Step 2: Create Compute Cluster

```bash
# Create compute cluster for training
az ml compute create \
    --name penske-cluster \
    --type AmlCompute \
    --size Standard_DS3_v2 \
    --min-instances 0 \
    --max-instances 4 \
    --workspace-name penske-ml-workspace \
    --resource-group $RESOURCE_GROUP
```

### Step 3: Create Training Data

```bash
# Create data asset
az ml data create \
    --name penske-training-data \
    --version 1 \
    --path azureml://datastores/workspaceblobstore/paths/training/ \
    --type uri_folder \
    --workspace-name penske-ml-workspace \
    --resource-group $RESOURCE_GROUP
```

### Step 4: Train Custom Model

```python
# src/ml/azure_ml_training.py
from azure.ai.ml import MLClient, command, Input
from azure.ai.ml.entities import Environment, AmlCompute
from azure.identity import DefaultAzureCredential

def train_demand_forecasting_model():
    """Train demand forecasting model on Azure ML."""
    
    # Connect to workspace
    ml_client = MLClient(
        DefaultAzureCredential(),
        subscription_id="your-subscription-id",
        resource_group_name="penske-analytics-rg",
        workspace_name="penske-ml-workspace"
    )
    
    # Define training job
    job = command(
        code="./src/ml/scripts",
        command="python train.py --data ${{inputs.training_data}} --n_estimators 100 --max_depth 10",
        inputs={
            "training_data": Input(
                type="uri_folder",
                path="azureml://datastores/workspaceblobstore/paths/training/"
            )
        },
        environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu@latest",
        compute="penske-cluster",
        display_name="penske-demand-forecast-training",
        experiment_name="penske-logistics"
    )
    
    # Submit job
    returned_job = ml_client.jobs.create_or_update(job)
    ml_client.jobs.stream(returned_job.name)
    
    return returned_job

# Training script: src/ml/scripts/train.py
"""
import argparse
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib
import mlflow

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=str)
    parser.add_argument('--n_estimators', type=int, default=100)
    parser.add_argument('--max_depth', type=int, default=10)
    args = parser.parse_args()
    
    # Enable MLflow autologging
    mlflow.sklearn.autolog()
    
    # Load data
    train_data = pd.read_csv(f'{args.data}/train.csv')
    
    # Train model
    model = RandomForestRegressor(
        n_estimators=args.n_estimators,
        max_depth=args.max_depth
    )
    model.fit(train_data.drop('target', axis=1), train_data['target'])
    
    # Save model
    joblib.dump(model, 'outputs/model.joblib')
"""
```

### Step 5: Deploy Model Endpoint

```python
# Deploy to managed online endpoint
from azure.ai.ml.entities import (
    ManagedOnlineEndpoint,
    ManagedOnlineDeployment,
    Model,
    Environment,
    CodeConfiguration
)

def deploy_model(ml_client, model_path):
    """Deploy trained model to Azure ML managed endpoint."""
    
    # Create endpoint
    endpoint = ManagedOnlineEndpoint(
        name="penske-demand-forecast",
        description="Penske demand forecasting endpoint",
        auth_mode="key"
    )
    ml_client.online_endpoints.begin_create_or_update(endpoint).result()
    
    # Register model
    model = Model(
        path=model_path,
        name="penske-demand-model",
        description="Demand forecasting model"
    )
    ml_client.models.create_or_update(model)
    
    # Create deployment
    deployment = ManagedOnlineDeployment(
        name="blue",
        endpoint_name="penske-demand-forecast",
        model=model,
        instance_type="Standard_DS2_v2",
        instance_count=1
    )
    ml_client.online_deployments.begin_create_or_update(deployment).result()
    
    # Set traffic
    endpoint.traffic = {"blue": 100}
    ml_client.online_endpoints.begin_create_or_update(endpoint).result()
    
    return endpoint
```

### Step 6: Invoke Endpoint

```python
# src/services/azure_ml_service.py
from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential
import json

class AzureMLService:
    def __init__(self, endpoint_name='penske-demand-forecast'):
        self.ml_client = MLClient(
            DefaultAzureCredential(),
            subscription_id="your-subscription-id",
            resource_group_name="penske-analytics-rg",
            workspace_name="penske-ml-workspace"
        )
        self.endpoint_name = endpoint_name
    
    def predict_demand(self, features: list):
        """Predict logistics demand using deployed model."""
        response = self.ml_client.online_endpoints.invoke(
            endpoint_name=self.endpoint_name,
            request_file=None,
            deployment_name="blue",
            request=json.dumps({"data": features})
        )
        return json.loads(response)
    
    def batch_predict(self, data_path: str, output_path: str):
        """Run batch predictions using batch endpoint."""
        from azure.ai.ml.entities import BatchEndpoint, BatchDeployment
        
        job = self.ml_client.batch_endpoints.invoke(
            endpoint_name="penske-batch-endpoint",
            input=Input(path=data_path)
        )
        return job
```

### Azure ML Use Cases for Penske Analytics

| Use Case | Model Type | Description |
|----------|------------|-------------|
| **Demand Forecasting** | Time Series | Predict shipment volumes |
| **Route Optimization** | Reinforcement Learning | Optimize delivery routes |
| **ETD Prediction** | Regression | Estimate delivery times |
| **Anomaly Detection** | Unsupervised | Detect logistics anomalies |
| **Cost Prediction** | Regression | Forecast shipping costs |

### Azure ML Costs

| Resource | Use Case | Cost/Hour |
|----------|----------|-----------|
| Standard_DS2_v2 | Dev/Test endpoints | $0.146 |
| Standard_DS3_v2 | Training | $0.293 |
| Standard_DS4_v2 | Production endpoint | $0.585 |
| Standard_NC6 | GPU Training | $0.90 |

### Auto-Scaling Endpoint

```bash
# Configure auto-scaling for production
az ml online-deployment update \
    --name blue \
    --endpoint-name penske-demand-forecast \
    --workspace-name penske-ml-workspace \
    --resource-group $RESOURCE_GROUP \
    --instance-count 2

# Enable autoscale
az monitor autoscale create \
    --resource-group $RESOURCE_GROUP \
    --name penske-autoscale \
    --min-count 1 \
    --max-count 5 \
    --count 2 \
    --resource /subscriptions/.../endpoints/penske-demand-forecast
```

### Cleanup Azure ML Resources

```bash
# Delete endpoint
az ml online-endpoint delete \
    --name penske-demand-forecast \
    --workspace-name penske-ml-workspace \
    --resource-group $RESOURCE_GROUP \
    --yes

# Delete compute cluster
az ml compute delete \
    --name penske-cluster \
    --workspace-name penske-ml-workspace \
    --resource-group $RESOURCE_GROUP \
    --yes

# Delete workspace (optional)
az ml workspace delete \
    --name penske-ml-workspace \
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
