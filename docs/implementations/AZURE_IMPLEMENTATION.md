# Azure Implementation Guide
## Penske Logistics Analytics - Azure ML & Azure OpenAI

> **Purpose**: Step-by-step implementation guide for deploying ML solutions on Microsoft Azure
> **Prerequisites**: Azure subscription, basic Python knowledge, familiarity with ML concepts
> **Estimated Time**: 4-6 hours for complete setup

---

## Table of Contents
1. [Environment Setup](#1-environment-setup)
2. [Azure Machine Learning Implementation](#2-azure-machine-learning-implementation)
3. [Azure OpenAI Implementation](#3-azure-openai-implementation)
4. [Integration Patterns](#4-integration-patterns)
5. [Monitoring & Operations](#5-monitoring--operations)
6. [Cost Optimization](#6-cost-optimization)

---

## 1. Environment Setup

### 1.1 Azure CLI Configuration

```bash
# Install Azure CLI
# Windows: Download from https://aka.ms/installazurecliwindows
# macOS: brew install azure-cli
# Linux: curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Login to Azure
az login

# Set subscription
az account set --subscription "Your-Subscription-Name"

# Verify connection
az account show
```

**Expected Output:**
```json
{
  "environmentName": "AzureCloud",
  "id": "12345678-1234-1234-1234-123456789012",
  "isDefault": true,
  "name": "Your-Subscription-Name",
  "state": "Enabled",
  "tenantId": "87654321-4321-4321-4321-210987654321",
  "user": {
    "name": "your-email@company.com",
    "type": "user"
  }
}
```

**💡 Learning Note**: Azure uses subscription-based billing. Each subscription can contain multiple resource groups for organizing resources.

### 1.2 Create Resource Group & ML Workspace

```bash
# Create resource group
az group create \
    --name penske-ml-rg \
    --location eastus

# Create Azure ML workspace
az ml workspace create \
    --name penske-ml-workspace \
    --resource-group penske-ml-rg \
    --location eastus
```

**Expected Output:**
```json
{
  "applicationInsights": "/subscriptions/.../applicationInsights/penske-ml-workspace...",
  "containerRegistry": "/subscriptions/.../containerRegistries/...",
  "id": "/subscriptions/.../workspaces/penske-ml-workspace",
  "keyVault": "/subscriptions/.../vaults/...",
  "location": "eastus",
  "name": "penske-ml-workspace",
  "storageAccount": "/subscriptions/.../storageAccounts/..."
}
```

### 1.3 Python Environment Setup

```bash
# Create virtual environment
python -m venv azure-ml-env
source azure-ml-env/bin/activate  # Linux/macOS
# or: azure-ml-env\Scripts\activate  # Windows

# Install required packages
pip install azure-ai-ml azure-identity openai pandas numpy scikit-learn
```

### 1.4 Verify Setup

```python
# test_azure_setup.py
from azure.identity import DefaultAzureCredential
from azure.ai.ml import MLClient

# Authenticate
credential = DefaultAzureCredential()

# Connect to workspace
ml_client = MLClient(
    credential=credential,
    subscription_id="your-subscription-id",
    resource_group_name="penske-ml-rg",
    workspace_name="penske-ml-workspace"
)

# Verify connection
workspace = ml_client.workspaces.get("penske-ml-workspace")
print(f"✅ Connected to workspace: {workspace.name}")
print(f"✅ Location: {workspace.location}")
print(f"✅ Resource group: {workspace.resource_group}")
```

**Expected Output:**
```
✅ Connected to workspace: penske-ml-workspace
✅ Location: eastus
✅ Resource group: penske-ml-rg
```

---

## 2. Azure Machine Learning Implementation

### 2.1 Create Compute Resources

```python
# create_compute.py
from azure.ai.ml import MLClient
from azure.ai.ml.entities import AmlCompute
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
ml_client = MLClient(
    credential=credential,
    subscription_id="your-subscription-id",
    resource_group_name="penske-ml-rg",
    workspace_name="penske-ml-workspace"
)

# Create compute cluster for training
cluster_name = "penske-training-cluster"

try:
    compute = ml_client.compute.get(cluster_name)
    print(f"✅ Found existing cluster: {cluster_name}")
except:
    compute = AmlCompute(
        name=cluster_name,
        type="amlcompute",
        size="Standard_DS3_v2",
        min_instances=0,
        max_instances=4,
        idle_time_before_scale_down=120
    )
    ml_client.compute.begin_create_or_update(compute).result()
    print(f"✅ Created cluster: {cluster_name}")
```

**Expected Output:**
```
✅ Created cluster: penske-training-cluster
```

**💡 Learning Note**: `min_instances=0` means the cluster scales to zero when idle, saving costs. `idle_time_before_scale_down=120` waits 2 minutes before scaling down.

### 2.2 Register Data Assets

```python
# register_data.py
from azure.ai.ml.entities import Data
from azure.ai.ml.constants import AssetTypes

# Upload and register training data
training_data = Data(
    name="penske-delivery-data",
    path="./data/logistics_data.csv",
    type=AssetTypes.URI_FILE,
    description="Penske logistics delivery data for ML training",
    tags={"source": "warehouse_system", "year": "2024"}
)

registered_data = ml_client.data.create_or_update(training_data)
print(f"✅ Registered data asset: {registered_data.name}")
print(f"✅ Version: {registered_data.version}")
print(f"✅ Path: {registered_data.path}")
```

**Expected Output:**
```
✅ Registered data asset: penske-delivery-data
✅ Version: 1
✅ Path: azureml://subscriptions/.../datastores/workspaceblobstore/paths/LocalUpload/.../logistics_data.csv
```

### 2.3 Create Training Script

```python
# src/train.py
import argparse
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, r2_score
import mlflow
import joblib
import os

def main():
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=str, help="Path to training data")
    parser.add_argument("--n_estimators", type=int, default=100)
    parser.add_argument("--max_depth", type=int, default=6)
    parser.add_argument("--learning_rate", type=float, default=0.1)
    parser.add_argument("--model_output", type=str, help="Path to save model")
    args = parser.parse_args()
    
    # Enable MLflow autologging
    mlflow.sklearn.autolog()
    
    # Load data
    print(f"📂 Loading data from: {args.data}")
    df = pd.read_csv(args.data)
    
    # Feature engineering
    df['pickup_hour'] = pd.to_datetime(df['pickup_time']).dt.hour
    df['day_of_week'] = pd.to_datetime(df['pickup_time']).dt.dayofweek
    
    # Prepare features
    features = ['pickup_hour', 'day_of_week', 'distance_miles', 
                'weight_kg', 'vehicle_type_encoded', 'route_complexity']
    target = 'delivery_time_hours'
    
    X = df[features]
    y = df[target]
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Train model
    print("🚀 Training model...")
    model = GradientBoostingRegressor(
        n_estimators=args.n_estimators,
        max_depth=args.max_depth,
        learning_rate=args.learning_rate,
        random_state=42
    )
    model.fit(X_train, y_train)
    
    # Evaluate
    predictions = model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))
    r2 = r2_score(y_test, predictions)
    
    print(f"📊 RMSE: {rmse:.4f}")
    print(f"📊 R² Score: {r2:.4f}")
    
    # Log metrics
    mlflow.log_metric("rmse", rmse)
    mlflow.log_metric("r2", r2)
    
    # Save model
    os.makedirs(args.model_output, exist_ok=True)
    model_path = os.path.join(args.model_output, "model.pkl")
    joblib.dump(model, model_path)
    print(f"✅ Model saved to: {model_path}")

if __name__ == "__main__":
    main()
```

### 2.4 Submit Training Job

```python
# submit_training.py
from azure.ai.ml import MLClient, command, Input
from azure.ai.ml.entities import Environment
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
ml_client = MLClient(
    credential=credential,
    subscription_id="your-subscription-id",
    resource_group_name="penske-ml-rg",
    workspace_name="penske-ml-workspace"
)

# Create environment
env = Environment(
    name="penske-sklearn-env",
    conda_file="./environment.yml",
    image="mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04:latest"
)

# Define the training job
training_job = command(
    code="./src",
    command="python train.py --data ${{inputs.training_data}} --n_estimators ${{inputs.n_estimators}} --max_depth ${{inputs.max_depth}} --learning_rate ${{inputs.learning_rate}} --model_output ${{outputs.model}}",
    inputs={
        "training_data": Input(
            type="uri_file",
            path="azureml:penske-delivery-data:1"
        ),
        "n_estimators": 100,
        "max_depth": 6,
        "learning_rate": 0.1
    },
    outputs={
        "model": {"type": "uri_folder"}
    },
    environment=env,
    compute="penske-training-cluster",
    display_name="delivery-time-prediction",
    experiment_name="penske-logistics-experiment"
)

# Submit job
print("🚀 Submitting training job...")
returned_job = ml_client.jobs.create_or_update(training_job)
print(f"✅ Job submitted: {returned_job.name}")
print(f"🔗 Studio URL: {returned_job.studio_url}")

# Wait for completion
ml_client.jobs.stream(returned_job.name)
```

**Expected Output:**
```
🚀 Submitting training job...
✅ Job submitted: delivery-time-prediction_abc123
🔗 Studio URL: https://ml.azure.com/runs/delivery-time-prediction_abc123...

RunId: delivery-time-prediction_abc123
...
📊 RMSE: 0.3421
📊 R² Score: 0.8756
✅ Model saved to: ./outputs/model/model.pkl
```

### 2.5 Hyperparameter Sweep

```python
# hyperparameter_sweep.py
from azure.ai.ml.sweep import Choice, Uniform

# Define sweep job
sweep_job = training_job.sweep(
    sampling_algorithm="bayesian",
    primary_metric="rmse",
    goal="minimize",
    max_total_trials=20,
    max_concurrent_trials=4
)

# Define search space
sweep_job.set_limits(max_total_trials=20, max_concurrent_trials=4, timeout=7200)
sweep_job.inputs["n_estimators"] = Choice([50, 100, 150, 200])
sweep_job.inputs["max_depth"] = Choice([3, 4, 5, 6, 7, 8])
sweep_job.inputs["learning_rate"] = Uniform(0.01, 0.3)

# Submit sweep
print("🔧 Starting hyperparameter sweep...")
returned_sweep = ml_client.jobs.create_or_update(sweep_job)
print(f"✅ Sweep job: {returned_sweep.name}")
print(f"🔗 Studio URL: {returned_sweep.studio_url}")
```

### 2.6 Register & Deploy Model

```python
# deploy_model.py
from azure.ai.ml.entities import Model, ManagedOnlineEndpoint, ManagedOnlineDeployment
from azure.ai.ml.constants import AssetTypes

# Register the model
model = Model(
    path="./outputs/model",
    name="penske-delivery-model",
    description="Delivery time prediction model",
    type=AssetTypes.CUSTOM_MODEL
)
registered_model = ml_client.models.create_or_update(model)
print(f"✅ Model registered: {registered_model.name} v{registered_model.version}")

# Create online endpoint
endpoint = ManagedOnlineEndpoint(
    name="penske-delivery-endpoint",
    description="Real-time delivery prediction endpoint",
    auth_mode="key"
)
ml_client.online_endpoints.begin_create_or_update(endpoint).result()
print(f"✅ Endpoint created: {endpoint.name}")

# Create deployment
deployment = ManagedOnlineDeployment(
    name="blue",
    endpoint_name="penske-delivery-endpoint",
    model=registered_model,
    instance_type="Standard_DS2_v2",
    instance_count=1,
    code_configuration={
        "code": "./score",
        "scoring_script": "score.py"
    },
    environment=env
)
ml_client.online_deployments.begin_create_or_update(deployment).result()
print(f"✅ Deployment created: {deployment.name}")

# Set traffic to 100%
endpoint.traffic = {"blue": 100}
ml_client.online_endpoints.begin_create_or_update(endpoint).result()
print("✅ Traffic routed to deployment")
```

### 2.7 Scoring Script

```python
# score/score.py
import json
import joblib
import numpy as np
import os

def init():
    global model
    model_path = os.path.join(os.getenv("AZUREML_MODEL_DIR"), "model.pkl")
    model = joblib.load(model_path)

def run(raw_data):
    try:
        data = json.loads(raw_data)
        features = np.array(data["features"])
        
        if features.ndim == 1:
            features = features.reshape(1, -1)
        
        predictions = model.predict(features)
        
        return json.dumps({
            "predictions": predictions.tolist(),
            "status": "success"
        })
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "status": "error"
        })
```

### 2.8 Test the Endpoint

```python
# test_endpoint.py
import json

# Get endpoint details
endpoint = ml_client.online_endpoints.get("penske-delivery-endpoint")
scoring_uri = endpoint.scoring_uri
api_key = ml_client.online_endpoints.get_keys("penske-delivery-endpoint").primary_key

# Test prediction
import requests

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

data = {
    "features": [8, 2, 45.5, 1200, 1, 3]  # hour, day, distance, weight, vehicle, complexity
}

response = requests.post(scoring_uri, headers=headers, json=data)
print(f"📦 Prediction: {response.json()}")
```

**Expected Output:**
```
📦 Prediction: {"predictions": [2.35], "status": "success"}
```

---

## 3. Azure OpenAI Implementation

### 3.1 Create Azure OpenAI Resource

```bash
# Create Azure OpenAI resource
az cognitiveservices account create \
    --name penske-openai \
    --resource-group penske-ml-rg \
    --kind OpenAI \
    --sku S0 \
    --location eastus

# Get endpoint and key
az cognitiveservices account show \
    --name penske-openai \
    --resource-group penske-ml-rg \
    --query "properties.endpoint" -o tsv

az cognitiveservices account keys list \
    --name penske-openai \
    --resource-group penske-ml-rg \
    --query "key1" -o tsv
```

### 3.2 Deploy Models

```bash
# Deploy GPT-4 model
az cognitiveservices account deployment create \
    --name penske-openai \
    --resource-group penske-ml-rg \
    --deployment-name gpt-4 \
    --model-name gpt-4 \
    --model-version "0613" \
    --model-format OpenAI \
    --sku-capacity 10 \
    --sku-name Standard

# Deploy text-embedding-ada-002 for embeddings
az cognitiveservices account deployment create \
    --name penske-openai \
    --resource-group penske-ml-rg \
    --deployment-name text-embedding \
    --model-name text-embedding-ada-002 \
    --model-version "2" \
    --model-format OpenAI \
    --sku-capacity 10 \
    --sku-name Standard
```

### 3.3 Basic Text Generation

```python
# azure_openai_basic.py
from openai import AzureOpenAI
import os

# Initialize client
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version="2024-02-15-preview",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

def generate_text(prompt, max_tokens=1024):
    """Generate text using GPT-4"""
    
    response = client.chat.completions.create(
        model="gpt-4",  # deployment name
        messages=[
            {"role": "system", "content": "You are a logistics analytics expert."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=max_tokens,
        temperature=0.7
    )
    
    return response.choices[0].message.content

# Example: Analyze delivery performance
prompt = """Analyze this delivery performance data and provide recommendations:
- On-time delivery rate: 87%
- Average delay when late: 23 minutes
- Top delay reasons: Traffic (35%), Weather (20%), Loading (25%), Customer (20%)
- Busiest delivery windows: 10am-2pm, 5pm-8pm"""

response = generate_text(prompt)
print(response)
```

**Expected Output:**
```
Based on the delivery performance analysis:

**Key Observations:**
1. 87% on-time rate is slightly below industry standard (90%+)
2. Traffic and loading combined cause 60% of delays
3. Peak windows create capacity pressure

**Recommendations:**
1. **Route Optimization**: Implement real-time traffic integration to reduce 
   the 35% traffic-related delays
2. **Loading Process Improvement**: Standardize loading procedures and 
   pre-stage deliveries to reduce 25% loading delays
3. **Demand Smoothing**: Offer delivery window incentives to shift volume 
   from peak periods
```

### 3.4 Embeddings for Semantic Search

```python
# azure_embeddings.py
from openai import AzureOpenAI
import numpy as np

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version="2024-02-15-preview",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

def get_embedding(text):
    """Get embedding using text-embedding-ada-002"""
    
    response = client.embeddings.create(
        model="text-embedding",  # deployment name
        input=text
    )
    
    return response.data[0].embedding

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# Example: Semantic search over delivery issues
issues = [
    "Package arrived with visible damage to outer box",
    "Delivery was 2 hours later than scheduled window",
    "Driver could not locate the delivery address",
    "Customer was not available to receive package",
    "Shipment was misrouted to wrong distribution center"
]

# Embed all issues
issue_embeddings = [get_embedding(issue) for issue in issues]

# Search
query = "My delivery came late"
query_embedding = get_embedding(query)

# Find similar
similarities = [cosine_similarity(query_embedding, emb) for emb in issue_embeddings]
ranked = sorted(zip(issues, similarities), key=lambda x: x[1], reverse=True)

print("🔍 Most relevant issues:")
for issue, score in ranked[:3]:
    print(f"  [{score:.3f}] {issue}")
```

**Expected Output:**
```
🔍 Most relevant issues:
  [0.912] Delivery was 2 hours later than scheduled window
  [0.834] Shipment was misrouted to wrong distribution center
  [0.789] Driver could not locate the delivery address
```

### 3.5 Function Calling

```python
# azure_functions.py
import json

# Define available functions
functions = [
    {
        "name": "get_delivery_status",
        "description": "Get the current status of a delivery by tracking number",
        "parameters": {
            "type": "object",
            "properties": {
                "tracking_number": {
                    "type": "string",
                    "description": "The tracking number of the shipment"
                }
            },
            "required": ["tracking_number"]
        }
    },
    {
        "name": "estimate_delivery_time",
        "description": "Estimate delivery time based on origin, destination, and shipment details",
        "parameters": {
            "type": "object",
            "properties": {
                "origin": {"type": "string"},
                "destination": {"type": "string"},
                "weight_kg": {"type": "number"},
                "priority": {"type": "string", "enum": ["standard", "express", "overnight"]}
            },
            "required": ["origin", "destination"]
        }
    }
]

def process_with_functions(user_message):
    """Process message with function calling"""
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": user_message}],
        functions=functions,
        function_call="auto"
    )
    
    message = response.choices[0].message
    
    if message.function_call:
        func_name = message.function_call.name
        func_args = json.loads(message.function_call.arguments)
        print(f"🔧 Function called: {func_name}")
        print(f"📋 Arguments: {func_args}")
        return func_name, func_args
    
    return None, message.content

# Example
func, args = process_with_functions("When will tracking number PK123456789 arrive?")
```

**Expected Output:**
```
🔧 Function called: get_delivery_status
📋 Arguments: {"tracking_number": "PK123456789"}
```

### 3.6 Streaming Responses

```python
# azure_streaming.py
def stream_response(prompt):
    """Stream response for real-time output"""
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        stream=True
    )
    
    print("🤖 Response: ", end="")
    for chunk in response:
        if chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)
    print()

stream_response("List 3 ways to reduce delivery delays.")
```

---

## 4. Integration Patterns

### 4.1 Azure Function + ML Endpoint

```python
# function_app.py
import azure.functions as func
import requests
import json
import os

app = func.FunctionApp()

@app.route(route="predict")
def predict_delivery(req: func.HttpRequest) -> func.HttpResponse:
    """Azure Function to call ML endpoint"""
    
    try:
        body = req.get_json()
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.environ['ML_ENDPOINT_KEY']}"
        }
        
        response = requests.post(
            os.environ['ML_ENDPOINT_URL'],
            headers=headers,
            json={"features": body["features"]}
        )
        
        return func.HttpResponse(
            response.text,
            mimetype="application/json"
        )
    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500
        )
```

### 4.2 Logic App Integration

```json
{
    "definition": {
        "$schema": "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#",
        "triggers": {
            "When_a_HTTP_request_is_received": {
                "type": "Request",
                "kind": "Http"
            }
        },
        "actions": {
            "Call_ML_Endpoint": {
                "type": "Http",
                "inputs": {
                    "method": "POST",
                    "uri": "@parameters('mlEndpointUrl')",
                    "headers": {
                        "Authorization": "Bearer @{parameters('mlEndpointKey')}"
                    },
                    "body": "@triggerBody()"
                }
            },
            "Response": {
                "type": "Response",
                "inputs": {
                    "statusCode": 200,
                    "body": "@body('Call_ML_Endpoint')"
                }
            }
        }
    }
}
```

---

## 5. Monitoring & Operations

### 5.1 Application Insights

```python
# setup_monitoring.py
from azure.ai.ml.entities import MonitoringTarget, AlertNotification

# Enable monitoring for endpoint
from azure.monitor.query import LogsQueryClient

logs_client = LogsQueryClient(credential)

# Query endpoint metrics
query = """
AzureMLOnlineEndpoint
| where EndpointName == 'penske-delivery-endpoint'
| summarize avg(RequestLatency), count() by bin(TimeGenerated, 1h)
| order by TimeGenerated desc
"""

response = logs_client.query_workspace(
    workspace_id="your-log-analytics-workspace-id",
    query=query,
    timespan="P1D"
)

for row in response.tables[0].rows:
    print(f"Time: {row[0]}, Avg Latency: {row[1]:.2f}ms, Requests: {row[2]}")
```

### 5.2 Create Alerts

```bash
# Create alert for high latency
az monitor metrics alert create \
    --name "HighLatencyAlert" \
    --resource-group penske-ml-rg \
    --scopes "/subscriptions/.../endpoints/penske-delivery-endpoint" \
    --condition "avg RequestLatency > 1000" \
    --window-size 5m \
    --evaluation-frequency 1m \
    --action-group "/subscriptions/.../actionGroups/ml-alerts"
```

---

## 6. Cost Optimization

### 6.1 VM Size Recommendations

| Use Case | VM Size | vCPUs | RAM | Cost/hr | Notes |
|----------|---------|-------|-----|---------|-------|
| Dev/Test | Standard_DS2_v2 | 2 | 7 GB | $0.15 | Good for testing |
| Small Prod | Standard_DS3_v2 | 4 | 14 GB | $0.29 | Balanced |
| High CPU | Standard_F4s_v2 | 4 | 8 GB | $0.17 | CPU optimized |
| GPU Training | Standard_NC6 | 6 | 56 GB | $0.90 | K80 GPU |
| GPU Inference | Standard_NC4as_T4_v3 | 4 | 28 GB | $0.53 | T4 GPU |

### 6.2 Auto-Scaling

```python
# autoscale_config.py
from azure.ai.ml.entities import OnlineDeployment

# Update deployment with auto-scaling
deployment = ManagedOnlineDeployment(
    name="blue",
    endpoint_name="penske-delivery-endpoint",
    model=registered_model,
    instance_type="Standard_DS2_v2",
    instance_count=1,
    scale_settings={
        "scale_type": "target_utilization",
        "min_instances": 1,
        "max_instances": 5,
        "target_utilization_percentage": 70,
        "polling_interval": 10,
        "cooldown_period": 60
    }
)

ml_client.online_deployments.begin_create_or_update(deployment).result()
print("✅ Auto-scaling configured")
```

### 6.3 Cleanup Script

```python
# cleanup.py
from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
ml_client = MLClient(credential, subscription_id, resource_group, workspace_name)

def cleanup_resources():
    """Clean up Azure ML resources"""
    
    # Delete endpoint (also deletes deployments)
    try:
        ml_client.online_endpoints.begin_delete("penske-delivery-endpoint").result()
        print("✅ Endpoint deleted")
    except Exception as e:
        print(f"⚠️ {e}")
    
    # Delete compute cluster
    try:
        ml_client.compute.begin_delete("penske-training-cluster").result()
        print("✅ Compute cluster deleted")
    except Exception as e:
        print(f"⚠️ {e}")

if __name__ == '__main__':
    cleanup_resources()
```

---

## Quick Reference

### Common Commands

```bash
# List ML workspaces
az ml workspace list -o table

# List compute targets
az ml compute list --workspace-name penske-ml-workspace -g penske-ml-rg

# List endpoints
az ml online-endpoint list --workspace-name penske-ml-workspace -g penske-ml-rg

# Get endpoint logs
az ml online-deployment get-logs --endpoint-name penske-delivery-endpoint --name blue
```

### Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| AuthorizationFailed | Missing RBAC permissions | Add Contributor role to workspace |
| QuotaExceeded | Subscription limits | Request quota increase |
| ModelDeploymentFailed | Scoring script error | Check logs with `get-logs` |
| EndpointTimeout | Instance undersized | Scale up or add instances |
| OpenAI RateLimited | TPM limit exceeded | Implement backoff or increase quota |

---

## Next Steps

1. ✅ **AWS Setup Complete** - See `AWS_IMPLEMENTATION.md`
2. ✅ **Azure Setup Complete** - Azure ML and OpenAI configured
3. 📋 **GCP Implementation** - See `GCP_IMPLEMENTATION.md`

---

*Last Updated: January 2024*
*Author: Penske Logistics Analytics Team*
