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

## 7. Reusable Templates

> **🔄 This section contains fully reusable code templates that work with ANY dataset.**
> **Simply update the configuration file and the code adapts automatically.**

### 7.1 Configuration File

```yaml
# config/azure_config.yaml
# ═══════════════════════════════════════════════════════════════════════════════
# 🔧 CHANGE THESE VALUES FOR YOUR PROJECT
# ═══════════════════════════════════════════════════════════════════════════════

azure:
  subscription_id: "your-subscription-id"    # ← CHANGE: Your Azure subscription
  resource_group: "my-ml-rg"                 # ← CHANGE: Your resource group name
  workspace_name: "my-ml-workspace"          # ← CHANGE: Your ML workspace name
  location: "eastus"                         # ← CHANGE: Your Azure region

data:
  # ═══════════════════════════════════════════════════════════════════════════
  # 📊 DEFINE YOUR DATA SCHEMA HERE
  # ═══════════════════════════════════════════════════════════════════════════
  source_file: "data/your_data.csv"          # ← CHANGE: Path to your data file
  target_column: "target"                    # ← CHANGE: Column to predict
  
  feature_columns:                           # ← CHANGE: Your feature columns
    - "feature_1"
    - "feature_2"
    - "feature_3"
    - "feature_4"
  
  datetime_columns:                          # ← CHANGE: Columns to parse as datetime
    - "timestamp_column"
  
  datetime_features:
    hour_column: "timestamp_column"
    dayofweek_column: "timestamp_column"

model:
  # ═══════════════════════════════════════════════════════════════════════════
  # 🤖 MODEL CONFIGURATION
  # ═══════════════════════════════════════════════════════════════════════════
  algorithm: "gradient_boosting"             # Options: gradient_boosting, random_forest, xgboost
  task: "regression"                         # Options: regression, classification
  
  hyperparameters:                           # ← CHANGE: Adjust for your use case
    n_estimators: 100
    max_depth: 6
    learning_rate: 0.1

training:
  compute_name: "my-training-cluster"        # ← CHANGE: Your compute cluster name
  vm_size: "Standard_DS3_v2"                 # ← CHANGE: VM size
  min_instances: 0
  max_instances: 4
  test_split: 0.2
  experiment_name: "my-ml-experiment"        # ← CHANGE: Your experiment name

deployment:
  endpoint_name: "my-prediction-endpoint"    # ← CHANGE: Your endpoint name
  deployment_name: "blue"
  instance_type: "Standard_DS2_v2"           # ← CHANGE: Based on traffic
  instance_count: 1

openai:
  resource_name: "my-openai"                 # ← CHANGE: Your OpenAI resource name
  deployment_name: "gpt-4"                   # ← CHANGE: Your model deployment
  embedding_deployment: "text-embedding"
  api_version: "2024-02-15-preview"
  system_prompt: "You are a helpful assistant."  # ← CHANGE: Your system prompt
```

### 7.2 Reusable Data Preparation Module

```python
# src/azure/data_utils.py
"""
🔄 REUSABLE DATA PREPARATION FOR AZURE ML
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Works with ANY dataset - just update config.yaml
"""

import yaml
import pandas as pd
from azure.ai.ml import MLClient
from azure.ai.ml.entities import Data
from azure.ai.ml.constants import AssetTypes
from azure.identity import DefaultAzureCredential
from pathlib import Path


def load_config(config_path: str = "config/azure_config.yaml") -> dict:
    """Load configuration from YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def get_ml_client(config: dict) -> MLClient:
    """
    Create Azure ML client from configuration.
    
    🔧 WHAT CHANGES:
    - subscription_id, resource_group, workspace_name in config
    """
    credential = DefaultAzureCredential()
    return MLClient(
        credential=credential,
        subscription_id=config['azure']['subscription_id'],
        resource_group_name=config['azure']['resource_group'],
        workspace_name=config['azure']['workspace_name']
    )


def prepare_features(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    """
    Prepare features based on configuration.
    
    🔧 WHAT THIS DOES:
    - Parses datetime columns
    - Creates hour and day_of_week features
    - Works with ANY column names from config
    """
    df = df.copy()
    
    # Parse datetime columns
    datetime_cols = config['data'].get('datetime_columns', [])
    for col in datetime_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col])
    
    # Create datetime-derived features
    dt_features = config['data'].get('datetime_features', {})
    if 'hour_column' in dt_features:
        source_col = dt_features['hour_column']
        if source_col in df.columns:
            df['hour'] = df[source_col].dt.hour
    
    if 'dayofweek_column' in dt_features:
        source_col = dt_features['dayofweek_column']
        if source_col in df.columns:
            df['day_of_week'] = df[source_col].dt.dayofweek
    
    return df


def register_data(
    df: pd.DataFrame,
    config: dict,
    name: str = None,
    description: str = None
) -> Data:
    """
    Register dataframe as Azure ML data asset.
    
    🔧 USAGE:
        registered = register_data(df, config, "my-dataset")
    """
    ml_client = get_ml_client(config)
    
    # Save locally first
    local_path = f"./data/{name or 'dataset'}.csv"
    Path(local_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(local_path, index=False)
    
    # Create data asset
    data = Data(
        name=name or f"{config['azure']['workspace_name']}-data",
        path=local_path,
        type=AssetTypes.URI_FILE,
        description=description or "ML training data"
    )
    
    registered = ml_client.data.create_or_update(data)
    print(f"✅ Registered data: {registered.name} v{registered.version}")
    return registered


def prepare_and_register(config_path: str = "config/azure_config.yaml"):
    """
    Main function to prepare and register data.
    
    🔧 USAGE:
        python -m src.azure.data_utils
    """
    from sklearn.model_selection import train_test_split
    
    config = load_config(config_path)
    print(f"📋 Workspace: {config['azure']['workspace_name']}")
    print(f"📊 Target: {config['data']['target_column']}")
    
    # Load and prepare data
    df = pd.read_csv(config['data']['source_file'])
    print(f"📂 Loaded {len(df)} rows")
    
    df = prepare_features(df, config)
    
    # Split
    test_size = config['training'].get('test_split', 0.2)
    train_df, test_df = train_test_split(df, test_size=test_size, random_state=42)
    
    # Register datasets
    train_data = register_data(train_df, config, "train-data", "Training dataset")
    test_data = register_data(test_df, config, "test-data", "Test dataset")
    
    return train_data, test_data


if __name__ == "__main__":
    prepare_and_register()
```

### 7.3 Reusable Training Module

```python
# src/azure/train.py
"""
🔄 REUSABLE AZURE ML TRAINING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Works with ANY dataset - just update config.yaml
"""

from azure.ai.ml import MLClient, command, Input
from azure.ai.ml.entities import Environment, AmlCompute
from azure.ai.ml.sweep import Choice, Uniform

from .data_utils import load_config, get_ml_client


def ensure_compute(config: dict) -> str:
    """
    Create or get compute cluster.
    
    🔧 WHAT CHANGES:
    - compute_name, vm_size, min/max instances in config
    """
    ml_client = get_ml_client(config)
    compute_name = config['training']['compute_name']
    
    try:
        ml_client.compute.get(compute_name)
        print(f"✅ Found compute: {compute_name}")
    except:
        compute = AmlCompute(
            name=compute_name,
            type="amlcompute",
            size=config['training']['vm_size'],
            min_instances=config['training']['min_instances'],
            max_instances=config['training']['max_instances']
        )
        ml_client.compute.begin_create_or_update(compute).result()
        print(f"✅ Created compute: {compute_name}")
    
    return compute_name


def create_training_job(config: dict, data_asset_name: str):
    """
    Create training job configuration.
    
    🔧 WHAT CHANGES:
    - Algorithm, hyperparameters from config
    - Data asset name
    - Compute cluster
    """
    ml_client = get_ml_client(config)
    
    # Environment
    env = Environment(
        name=f"{config['azure']['workspace_name']}-env",
        conda_file="./environment.yml",
        image="mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04:latest"
    )
    
    # Build command based on config
    hyperparams = config['model']['hyperparameters']
    hyperparam_args = " ".join([f"--{k} {v}" for k, v in hyperparams.items()])
    
    job = command(
        code="./src",
        command=f"python train_script.py --data ${{{{inputs.data}}}} --target {config['data']['target_column']} --task {config['model']['task']} {hyperparam_args} --model-output ${{{{outputs.model}}}}",
        inputs={
            "data": Input(type="uri_file", path=f"azureml:{data_asset_name}:1")
        },
        outputs={"model": {"type": "uri_folder"}},
        environment=env,
        compute=config['training']['compute_name'],
        experiment_name=config['training']['experiment_name'],
        display_name=f"{config['model']['algorithm']}-training"
    )
    
    return job


def train_model(config_path: str = "config/azure_config.yaml", data_asset: str = "train-data"):
    """
    Train model using Azure ML.
    
    🔧 USAGE:
        from src.azure.train import train_model
        job = train_model("config/azure_config.yaml", "my-training-data")
    """
    config = load_config(config_path)
    ml_client = get_ml_client(config)
    
    # Ensure compute exists
    ensure_compute(config)
    
    # Create and submit job
    job = create_training_job(config, data_asset)
    
    print(f"🚀 Submitting training job...")
    returned_job = ml_client.jobs.create_or_update(job)
    print(f"✅ Job: {returned_job.name}")
    print(f"🔗 Studio: {returned_job.studio_url}")
    
    # Wait for completion
    ml_client.jobs.stream(returned_job.name)
    
    return returned_job


def hyperparameter_sweep(config_path: str = "config/azure_config.yaml", data_asset: str = "train-data"):
    """
    Run hyperparameter sweep.
    
    🔧 WHAT THIS DOES:
    - Automatically tunes hyperparameters
    - Uses Bayesian optimization
    """
    config = load_config(config_path)
    ml_client = get_ml_client(config)
    
    ensure_compute(config)
    job = create_training_job(config, data_asset)
    
    # Define sweep
    sweep_job = job.sweep(
        sampling_algorithm="bayesian",
        primary_metric="rmse" if config['model']['task'] == 'regression' else 'accuracy',
        goal="minimize" if config['model']['task'] == 'regression' else 'maximize'
    )
    
    sweep_job.set_limits(max_total_trials=20, max_concurrent_trials=4)
    sweep_job.inputs["n_estimators"] = Choice([50, 100, 150, 200])
    sweep_job.inputs["max_depth"] = Choice([3, 4, 5, 6, 7, 8])
    sweep_job.inputs["learning_rate"] = Uniform(0.01, 0.3)
    
    print(f"🔧 Starting hyperparameter sweep...")
    returned_sweep = ml_client.jobs.create_or_update(sweep_job)
    print(f"✅ Sweep: {returned_sweep.name}")
    
    return returned_sweep
```

### 7.4 Reusable Training Script

```python
# src/train_script.py
"""
🔄 GENERIC TRAINING SCRIPT FOR AZURE ML
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Works with ANY dataset via command-line arguments
"""

import argparse
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor, GradientBoostingClassifier
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, f1_score
import mlflow
import joblib
import os


def get_model(algorithm: str, task: str, **hyperparams):
    """
    Get model based on algorithm and task type.
    
    🔧 SUPPORTS:
    - gradient_boosting (regression/classification)
    - random_forest (regression/classification)
    """
    models = {
        ('gradient_boosting', 'regression'): GradientBoostingRegressor,
        ('gradient_boosting', 'classification'): GradientBoostingClassifier,
        ('random_forest', 'regression'): RandomForestRegressor,
        ('random_forest', 'classification'): RandomForestClassifier,
    }
    
    model_class = models.get((algorithm, task))
    if model_class is None:
        raise ValueError(f"Unsupported: {algorithm} + {task}")
    
    return model_class(**hyperparams, random_state=42)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=str, required=True)
    parser.add_argument("--target", type=str, required=True)
    parser.add_argument("--task", type=str, default="regression")
    parser.add_argument("--algorithm", type=str, default="gradient_boosting")
    parser.add_argument("--n_estimators", type=int, default=100)
    parser.add_argument("--max_depth", type=int, default=6)
    parser.add_argument("--learning_rate", type=float, default=0.1)
    parser.add_argument("--model-output", type=str, required=True)
    args = parser.parse_args()
    
    mlflow.sklearn.autolog()
    
    # Load data
    print(f"📂 Loading: {args.data}")
    df = pd.read_csv(args.data)
    
    # Separate features and target
    target_col = args.target
    feature_cols = [c for c in df.columns if c != target_col]
    
    X = df[feature_cols]
    y = df[target_col]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train
    print(f"🚀 Training {args.algorithm} for {args.task}...")
    model = get_model(
        args.algorithm,
        args.task,
        n_estimators=args.n_estimators,
        max_depth=args.max_depth,
        learning_rate=args.learning_rate if args.algorithm == 'gradient_boosting' else None
    )
    model.fit(X_train, y_train)
    
    # Evaluate
    predictions = model.predict(X_test)
    
    if args.task == 'regression':
        rmse = np.sqrt(mean_squared_error(y_test, predictions))
        r2 = r2_score(y_test, predictions)
        print(f"📊 RMSE: {rmse:.4f}, R²: {r2:.4f}")
        mlflow.log_metrics({"rmse": rmse, "r2": r2})
    else:
        acc = accuracy_score(y_test, predictions)
        f1 = f1_score(y_test, predictions, average='weighted')
        print(f"📊 Accuracy: {acc:.4f}, F1: {f1:.4f}")
        mlflow.log_metrics({"accuracy": acc, "f1": f1})
    
    # Save
    os.makedirs(args.model_output, exist_ok=True)
    joblib.dump(model, os.path.join(args.model_output, "model.pkl"))
    print(f"✅ Model saved")


if __name__ == "__main__":
    main()
```

### 7.5 Reusable Deployment Module

```python
# src/azure/deploy.py
"""
🔄 REUSABLE AZURE ML DEPLOYMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Works with ANY model - just update config.yaml
"""

from azure.ai.ml.entities import (
    Model, ManagedOnlineEndpoint, ManagedOnlineDeployment,
    CodeConfiguration, Environment
)
from azure.ai.ml.constants import AssetTypes

from .data_utils import load_config, get_ml_client


def deploy_model(
    model_path: str,
    config_path: str = "config/azure_config.yaml"
):
    """
    Deploy model to online endpoint.
    
    🔧 USAGE:
        from src.azure.deploy import deploy_model
        endpoint = deploy_model("./outputs/model", "config/azure_config.yaml")
    """
    config = load_config(config_path)
    ml_client = get_ml_client(config)
    
    # Register model
    model = Model(
        path=model_path,
        name=f"{config['azure']['workspace_name']}-model",
        type=AssetTypes.CUSTOM_MODEL
    )
    registered_model = ml_client.models.create_or_update(model)
    print(f"✅ Model registered: {registered_model.name}")
    
    # Create endpoint
    endpoint = ManagedOnlineEndpoint(
        name=config['deployment']['endpoint_name'],
        auth_mode="key"
    )
    ml_client.online_endpoints.begin_create_or_update(endpoint).result()
    print(f"✅ Endpoint created: {endpoint.name}")
    
    # Create deployment
    env = Environment(
        name=f"{config['azure']['workspace_name']}-inference-env",
        conda_file="./environment.yml",
        image="mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04:latest"
    )
    
    deployment = ManagedOnlineDeployment(
        name=config['deployment']['deployment_name'],
        endpoint_name=config['deployment']['endpoint_name'],
        model=registered_model,
        instance_type=config['deployment']['instance_type'],
        instance_count=config['deployment']['instance_count'],
        code_configuration=CodeConfiguration(
            code="./src/azure",
            scoring_script="score.py"
        ),
        environment=env
    )
    ml_client.online_deployments.begin_create_or_update(deployment).result()
    print(f"✅ Deployment created: {deployment.name}")
    
    # Set traffic
    endpoint.traffic = {config['deployment']['deployment_name']: 100}
    ml_client.online_endpoints.begin_create_or_update(endpoint).result()
    
    return endpoint


def predict(features: list, config_path: str = "config/azure_config.yaml"):
    """
    Make prediction using deployed endpoint.
    
    🔧 USAGE:
        result = predict([1.2, 3.4, 5.6], "config/azure_config.yaml")
    """
    import requests
    
    config = load_config(config_path)
    ml_client = get_ml_client(config)
    
    endpoint = ml_client.online_endpoints.get(config['deployment']['endpoint_name'])
    api_key = ml_client.online_endpoints.get_keys(config['deployment']['endpoint_name']).primary_key
    
    response = requests.post(
        endpoint.scoring_uri,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={"features": features}
    )
    
    return response.json()


def cleanup(config_path: str = "config/azure_config.yaml"):
    """Clean up Azure resources."""
    config = load_config(config_path)
    ml_client = get_ml_client(config)
    
    try:
        ml_client.online_endpoints.begin_delete(config['deployment']['endpoint_name']).result()
        print(f"✅ Deleted endpoint")
    except Exception as e:
        print(f"⚠️ {e}")
    
    try:
        ml_client.compute.begin_delete(config['training']['compute_name']).result()
        print(f"✅ Deleted compute")
    except Exception as e:
        print(f"⚠️ {e}")
```

### 7.6 Reusable OpenAI Module

```python
# src/azure/openai_utils.py
"""
🔄 REUSABLE AZURE OPENAI UTILITIES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Works with ANY use case - just update config.yaml
"""

import os
import numpy as np
from openai import AzureOpenAI
from typing import List, Dict, Any

from .data_utils import load_config


class AzureOpenAIClient:
    """
    Reusable Azure OpenAI client.
    
    🔧 USAGE:
        client = AzureOpenAIClient("config/azure_config.yaml")
        response = client.generate("Hello!")
        embeddings = client.get_embeddings(["text1", "text2"])
    """
    
    def __init__(self, config_path: str = "config/azure_config.yaml"):
        self.config = load_config(config_path)
        openai_config = self.config['openai']
        
        self.client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_KEY"),
            api_version=openai_config['api_version'],
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        self.deployment = openai_config['deployment_name']
        self.embedding_deployment = openai_config['embedding_deployment']
        self.system_prompt = openai_config.get('system_prompt', '')
    
    def generate(self, prompt: str, max_tokens: int = 1024, temperature: float = 0.7) -> str:
        """Generate text using GPT-4."""
        messages = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat.completions.create(
            model=self.deployment,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response.choices[0].message.content
    
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for texts."""
        embeddings = []
        for text in texts:
            response = self.client.embeddings.create(
                model=self.embedding_deployment,
                input=text
            )
            embeddings.append(response.data[0].embedding)
        return embeddings
    
    def semantic_search(self, query: str, documents: List[str], top_k: int = 3) -> List[Dict]:
        """Search documents by semantic similarity."""
        query_emb = self.get_embeddings([query])[0]
        doc_embs = self.get_embeddings(documents)
        
        similarities = []
        for i, doc_emb in enumerate(doc_embs):
            sim = np.dot(query_emb, doc_emb) / (np.linalg.norm(query_emb) * np.linalg.norm(doc_emb))
            similarities.append({'document': documents[i], 'score': float(sim), 'index': i})
        
        return sorted(similarities, key=lambda x: x['score'], reverse=True)[:top_k]


# Convenience functions
def generate(prompt: str, config_path: str = "config/azure_config.yaml") -> str:
    return AzureOpenAIClient(config_path).generate(prompt)

def search(query: str, docs: List[str], config_path: str = "config/azure_config.yaml") -> List[Dict]:
    return AzureOpenAIClient(config_path).semantic_search(query, docs)
```

### 7.7 Complete Pipeline Example

```python
# run_azure_pipeline.py
"""
🔄 COMPLETE AZURE ML PIPELINE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Run the entire pipeline with one command!

🔧 USAGE:
    python run_azure_pipeline.py --config config/azure_config.yaml
    python run_azure_pipeline.py --config config/azure_config.yaml --sweep
"""

import argparse
from src.azure.data_utils import prepare_and_register, load_config
from src.azure.train import train_model, hyperparameter_sweep
from src.azure.deploy import deploy_model, predict


def main():
    parser = argparse.ArgumentParser(description="Azure ML Pipeline")
    parser.add_argument("--config", default="config/azure_config.yaml")
    parser.add_argument("--sweep", action="store_true", help="Run hyperparameter sweep")
    parser.add_argument("--skip-train", action="store_true")
    parser.add_argument("--test", action="store_true")
    args = parser.parse_args()
    
    config = load_config(args.config)
    print("=" * 60)
    print(f"🚀 Azure ML Pipeline: {config['azure']['workspace_name']}")
    print("=" * 60)
    
    # Step 1: Prepare data
    print("\n📊 Step 1: Preparing and registering data...")
    train_data, test_data = prepare_and_register(args.config)
    
    # Step 2: Train
    if not args.skip_train:
        if args.sweep:
            print("\n🔧 Step 2: Running hyperparameter sweep...")
            hyperparameter_sweep(args.config, train_data.name)
            return
        else:
            print("\n🚀 Step 2: Training model...")
            job = train_model(args.config, train_data.name)
    
    # Step 3: Deploy
    print("\n🌐 Step 3: Deploying model...")
    endpoint = deploy_model("./outputs/model", args.config)
    
    # Step 4: Test
    if args.test:
        print("\n🧪 Step 4: Testing...")
        result = predict([1.0] * len(config['data']['feature_columns']), args.config)
        print(f"📦 Prediction: {result}")
    
    print("\n" + "=" * 60)
    print("✅ Pipeline complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
```

### 7.8 What to Change Summary

| Component | What to Change | Where to Change |
|-----------|----------------|-----------------|
| **Azure subscription** | `azure.subscription_id` | `config/azure_config.yaml` |
| **Resource group** | `azure.resource_group` | `config/azure_config.yaml` |
| **Workspace** | `azure.workspace_name` | `config/azure_config.yaml` |
| **Data file** | `data.source_file` | `config/azure_config.yaml` |
| **Target column** | `data.target_column` | `config/azure_config.yaml` |
| **Feature columns** | `data.feature_columns` | `config/azure_config.yaml` |
| **Algorithm** | `model.algorithm` | `config/azure_config.yaml` |
| **Task type** | `model.task` | `config/azure_config.yaml` |
| **Hyperparameters** | `model.hyperparameters` | `config/azure_config.yaml` |
| **Compute cluster** | `training.compute_name`, `training.vm_size` | `config/azure_config.yaml` |
| **Endpoint** | `deployment.endpoint_name` | `config/azure_config.yaml` |
| **OpenAI model** | `openai.deployment_name` | `config/azure_config.yaml` |
| **System prompt** | `openai.system_prompt` | `config/azure_config.yaml` |

---

## Next Steps

1. ✅ **AWS Setup Complete** - See `AWS_IMPLEMENTATION.md`
2. ✅ **Azure Setup Complete** - Azure ML and OpenAI configured
3. 📋 **GCP Implementation** - See `GCP_IMPLEMENTATION.md`

---

*Last Updated: January 2024*
*Author: Penske Logistics Analytics Team*
