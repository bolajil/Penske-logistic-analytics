# GCP Implementation Guide
## Penske Logistics Analytics - Vertex AI & BigQuery ML

> **Purpose**: Step-by-step implementation guide for deploying ML solutions on Google Cloud Platform
> **Prerequisites**: GCP account, basic Python knowledge, familiarity with ML concepts
> **Estimated Time**: 4-6 hours for complete setup

---

## Table of Contents
1. [Environment Setup](#1-environment-setup)
2. [Vertex AI Implementation](#2-vertex-ai-implementation)
3. [BigQuery ML Implementation](#3-bigquery-ml-implementation)
4. [Generative AI (Gemini)](#4-generative-ai-gemini)
5. [Integration Patterns](#5-integration-patterns)
6. [Monitoring & Operations](#6-monitoring--operations)
7. [Cost Optimization](#7-cost-optimization)

---

## 1. Environment Setup

### 1.1 Google Cloud CLI Configuration

```bash
# Install gcloud CLI
# Windows: Download from https://cloud.google.com/sdk/docs/install
# macOS: brew install google-cloud-sdk
# Linux: curl https://sdk.cloud.google.com | bash

# Initialize and authenticate
gcloud init

# Set project
gcloud config set project penske-logistics-ml

# Enable required APIs
gcloud services enable \
    aiplatform.googleapis.com \
    bigquery.googleapis.com \
    storage.googleapis.com \
    cloudfunctions.googleapis.com

# Verify configuration
gcloud config list
```

**Expected Output:**
```
[core]
account = your-email@company.com
project = penske-logistics-ml

[compute]
region = us-central1
zone = us-central1-a
```

**💡 Learning Note**: GCP uses project-based organization. Enable only the APIs you need to minimize security surface and potential costs.

### 1.2 Create Service Account

```bash
# Create service account for ML workloads
gcloud iam service-accounts create penske-ml-sa \
    --display-name="Penske ML Service Account"

# Grant necessary roles
gcloud projects add-iam-policy-binding penske-logistics-ml \
    --member="serviceAccount:penske-ml-sa@penske-logistics-ml.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding penske-logistics-ml \
    --member="serviceAccount:penske-ml-sa@penske-logistics-ml.iam.gserviceaccount.com" \
    --role="roles/bigquery.dataEditor"

gcloud projects add-iam-policy-binding penske-logistics-ml \
    --member="serviceAccount:penske-ml-sa@penske-logistics-ml.iam.gserviceaccount.com" \
    --role="roles/storage.objectAdmin"

# Create and download key (for local development)
gcloud iam service-accounts keys create ~/penske-ml-key.json \
    --iam-account=penske-ml-sa@penske-logistics-ml.iam.gserviceaccount.com

# Set environment variable
export GOOGLE_APPLICATION_CREDENTIALS=~/penske-ml-key.json
```

### 1.3 Python Environment Setup

```bash
# Create virtual environment
python -m venv gcp-ml-env
source gcp-ml-env/bin/activate  # Linux/macOS
# or: gcp-ml-env\Scripts\activate  # Windows

# Install required packages
pip install google-cloud-aiplatform google-cloud-bigquery google-cloud-storage pandas numpy scikit-learn
```

### 1.4 Verify Setup

```python
# test_gcp_setup.py
from google.cloud import aiplatform
from google.cloud import bigquery
from google.cloud import storage

PROJECT_ID = "penske-logistics-ml"
REGION = "us-central1"

# Initialize Vertex AI
aiplatform.init(project=PROJECT_ID, location=REGION)
print(f"✅ Vertex AI initialized for project: {PROJECT_ID}")

# Test BigQuery connection
bq_client = bigquery.Client(project=PROJECT_ID)
datasets = list(bq_client.list_datasets())
print(f"✅ BigQuery connected. Datasets: {len(datasets)}")

# Test Cloud Storage
storage_client = storage.Client(project=PROJECT_ID)
buckets = list(storage_client.list_buckets())
print(f"✅ Cloud Storage connected. Buckets: {len(buckets)}")
```

**Expected Output:**
```
✅ Vertex AI initialized for project: penske-logistics-ml
✅ BigQuery connected. Datasets: 3
✅ Cloud Storage connected. Buckets: 2
```

---

## 2. Vertex AI Implementation

### 2.1 Create Cloud Storage Bucket

```python
# create_bucket.py
from google.cloud import storage

PROJECT_ID = "penske-logistics-ml"
BUCKET_NAME = f"{PROJECT_ID}-ml-data"
REGION = "us-central1"

storage_client = storage.Client()

# Create bucket
bucket = storage_client.bucket(BUCKET_NAME)
bucket.storage_class = "STANDARD"
new_bucket = storage_client.create_bucket(bucket, location=REGION)

print(f"✅ Created bucket: {new_bucket.name}")
print(f"✅ Location: {new_bucket.location}")
```

### 2.2 Upload Training Data

```python
# upload_data.py
from google.cloud import storage
import pandas as pd

BUCKET_NAME = "penske-logistics-ml-ml-data"

# Load and prepare data
df = pd.read_csv('logistics_data.csv')

# Feature engineering
df['pickup_hour'] = pd.to_datetime(df['pickup_time']).dt.hour
df['day_of_week'] = pd.to_datetime(df['pickup_time']).dt.dayofweek

# Split data
from sklearn.model_selection import train_test_split
train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)

# Save locally
train_df.to_csv('train.csv', index=False)
test_df.to_csv('test.csv', index=False)

# Upload to GCS
storage_client = storage.Client()
bucket = storage_client.bucket(BUCKET_NAME)

for file_name in ['train.csv', 'test.csv']:
    blob = bucket.blob(f'penske-delivery/{file_name}')
    blob.upload_from_filename(file_name)
    print(f"✅ Uploaded: gs://{BUCKET_NAME}/penske-delivery/{file_name}")
```

**Expected Output:**
```
✅ Uploaded: gs://penske-logistics-ml-ml-data/penske-delivery/train.csv
✅ Uploaded: gs://penske-logistics-ml-ml-data/penske-delivery/test.csv
```

### 2.3 Create Vertex AI Dataset

```python
# create_dataset.py
from google.cloud import aiplatform

PROJECT_ID = "penske-logistics-ml"
REGION = "us-central1"
BUCKET_NAME = "penske-logistics-ml-ml-data"

aiplatform.init(project=PROJECT_ID, location=REGION)

# Create tabular dataset
dataset = aiplatform.TabularDataset.create(
    display_name="penske-delivery-dataset",
    gcs_source=f"gs://{BUCKET_NAME}/penske-delivery/train.csv"
)

print(f"✅ Dataset created: {dataset.display_name}")
print(f"✅ Resource name: {dataset.resource_name}")
```

**Expected Output:**
```
✅ Dataset created: penske-delivery-dataset
✅ Resource name: projects/123456/locations/us-central1/datasets/7890123456
```

### 2.4 AutoML Training

```python
# automl_training.py
from google.cloud import aiplatform

PROJECT_ID = "penske-logistics-ml"
REGION = "us-central1"

aiplatform.init(project=PROJECT_ID, location=REGION)

# Get dataset
dataset = aiplatform.TabularDataset.list(
    filter='display_name="penske-delivery-dataset"'
)[0]

# Define training job
job = aiplatform.AutoMLTabularTrainingJob(
    display_name="penske-delivery-automl",
    optimization_prediction_type="regression",
    optimization_objective="minimize-rmse"
)

# Start training
print("🚀 Starting AutoML training...")
model = job.run(
    dataset=dataset,
    target_column="delivery_time_hours",
    training_fraction_split=0.8,
    validation_fraction_split=0.1,
    test_fraction_split=0.1,
    budget_milli_node_hours=1000,  # 1 node-hour
    model_display_name="penske-delivery-model-automl"
)

print(f"✅ Model trained: {model.display_name}")
print(f"✅ Resource name: {model.resource_name}")
```

**Expected Output:**
```
🚀 Starting AutoML training...
Training AutoML Tabular regression model...
AutoMLTabularTrainingJob run completed. Model: penske-delivery-model-automl
✅ Model trained: penske-delivery-model-automl
✅ Resource name: projects/123456/locations/us-central1/models/7890123456
```

**💡 Learning Note**: AutoML automatically handles feature engineering, model selection, and hyperparameter tuning. `budget_milli_node_hours=1000` means 1 node-hour of training.

### 2.5 Custom Training with scikit-learn

```python
# custom_training.py
from google.cloud import aiplatform
from google.cloud.aiplatform import CustomTrainingJob

PROJECT_ID = "penske-logistics-ml"
REGION = "us-central1"
BUCKET_NAME = "penske-logistics-ml-ml-data"

aiplatform.init(project=PROJECT_ID, location=REGION, staging_bucket=f"gs://{BUCKET_NAME}")

# Define custom training job
job = CustomTrainingJob(
    display_name="penske-delivery-custom",
    script_path="train.py",
    container_uri="us-docker.pkg.dev/vertex-ai/training/scikit-learn-cpu.1-0:latest",
    requirements=["pandas", "numpy", "scikit-learn"],
    model_serving_container_image_uri="us-docker.pkg.dev/vertex-ai/prediction/sklearn-cpu.1-0:latest"
)

# Run training
print("🚀 Starting custom training...")
model = job.run(
    replica_count=1,
    machine_type="n1-standard-4",
    args=[
        "--data-path", f"gs://{BUCKET_NAME}/penske-delivery/train.csv",
        "--model-dir", f"gs://{BUCKET_NAME}/models"
    ],
    model_display_name="penske-delivery-model-custom"
)

print(f"✅ Model trained: {model.display_name}")
```

### 2.6 Training Script for Custom Job

```python
# train.py
import argparse
import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import os

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-path", type=str, required=True)
    parser.add_argument("--model-dir", type=str, required=True)
    args = parser.parse_args()
    
    # Load data from GCS
    print(f"📂 Loading data from: {args.data_path}")
    df = pd.read_csv(args.data_path)
    
    # Prepare features
    features = ['pickup_hour', 'day_of_week', 'distance_miles', 
                'weight_kg', 'vehicle_type_encoded', 'route_complexity']
    target = 'delivery_time_hours'
    
    X = df[features]
    y = df[target]
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Train model
    print("🚀 Training model...")
    model = GradientBoostingRegressor(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        random_state=42
    )
    model.fit(X_train, y_train)
    
    # Evaluate
    predictions = model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))
    r2 = r2_score(y_test, predictions)
    
    print(f"📊 RMSE: {rmse:.4f}")
    print(f"📊 R² Score: {r2:.4f}")
    
    # Save model (Vertex AI expects model in AIP_MODEL_DIR)
    model_path = os.environ.get("AIP_MODEL_DIR", args.model_dir)
    os.makedirs(model_path, exist_ok=True)
    joblib.dump(model, os.path.join(model_path, "model.joblib"))
    print(f"✅ Model saved to: {model_path}")

if __name__ == "__main__":
    main()
```

### 2.7 Deploy to Endpoint

```python
# deploy_model.py
from google.cloud import aiplatform

PROJECT_ID = "penske-logistics-ml"
REGION = "us-central1"

aiplatform.init(project=PROJECT_ID, location=REGION)

# Get the trained model
model = aiplatform.Model.list(
    filter='display_name="penske-delivery-model-custom"'
)[0]

# Create endpoint
print("🚀 Creating endpoint...")
endpoint = aiplatform.Endpoint.create(
    display_name="penske-delivery-endpoint",
    project=PROJECT_ID,
    location=REGION
)

# Deploy model
print("🚀 Deploying model...")
deployed_model = model.deploy(
    endpoint=endpoint,
    deployed_model_display_name="penske-delivery-v1",
    machine_type="n1-standard-2",
    min_replica_count=1,
    max_replica_count=5,
    traffic_percentage=100
)

print(f"✅ Endpoint: {endpoint.display_name}")
print(f"✅ Endpoint ID: {endpoint.name}")
```

**Expected Output:**
```
🚀 Creating endpoint...
🚀 Deploying model...
✅ Endpoint: penske-delivery-endpoint
✅ Endpoint ID: projects/123456/locations/us-central1/endpoints/7890123456
```

### 2.8 Make Predictions

```python
# predict.py
from google.cloud import aiplatform

PROJECT_ID = "penske-logistics-ml"
REGION = "us-central1"

aiplatform.init(project=PROJECT_ID, location=REGION)

# Get endpoint
endpoint = aiplatform.Endpoint.list(
    filter='display_name="penske-delivery-endpoint"'
)[0]

# Make prediction
instances = [
    [8, 2, 45.5, 1200, 1, 3],  # hour, day, distance, weight, vehicle, complexity
    [14, 4, 30.0, 800, 0, 2]
]

predictions = endpoint.predict(instances=instances)
print(f"📦 Predictions: {predictions.predictions}")
```

**Expected Output:**
```
📦 Predictions: [2.35, 1.87]
```

---

## 3. BigQuery ML Implementation

### 3.1 Create Dataset in BigQuery

```sql
-- Create dataset
CREATE SCHEMA IF NOT EXISTS penske_logistics
OPTIONS(
  location = 'US',
  description = 'Penske Logistics Analytics Dataset'
);
```

### 3.2 Load Data

```python
# load_to_bigquery.py
from google.cloud import bigquery
import pandas as pd

PROJECT_ID = "penske-logistics-ml"

client = bigquery.Client(project=PROJECT_ID)

# Load data
df = pd.read_csv('logistics_data.csv')

# Feature engineering
df['pickup_hour'] = pd.to_datetime(df['pickup_time']).dt.hour
df['day_of_week'] = pd.to_datetime(df['pickup_time']).dt.dayofweek

# Load to BigQuery
table_id = f"{PROJECT_ID}.penske_logistics.delivery_data"

job_config = bigquery.LoadJobConfig(
    write_disposition="WRITE_TRUNCATE",
    autodetect=True
)

job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
job.result()

table = client.get_table(table_id)
print(f"✅ Loaded {table.num_rows} rows to {table_id}")
```

### 3.3 Train Model with BigQuery ML

```sql
-- Create linear regression model
CREATE OR REPLACE MODEL `penske_logistics.delivery_time_model`
OPTIONS(
  model_type = 'LINEAR_REG',
  input_label_cols = ['delivery_time_hours'],
  data_split_method = 'AUTO_SPLIT',
  enable_global_explain = TRUE
) AS
SELECT
  pickup_hour,
  day_of_week,
  distance_miles,
  weight_kg,
  vehicle_type_encoded,
  route_complexity,
  delivery_time_hours
FROM `penske_logistics.delivery_data`;
```

**Expected Output:**
```
Query complete. Model penske_logistics.delivery_time_model created.
Training data: 8000 rows
Evaluation data: 2000 rows
```

### 3.4 Evaluate Model

```sql
-- Evaluate model performance
SELECT *
FROM ML.EVALUATE(MODEL `penske_logistics.delivery_time_model`);
```

**Expected Output:**
| mean_absolute_error | mean_squared_error | r2_score | explained_variance |
|---------------------|-------------------|----------|-------------------|
| 0.234 | 0.089 | 0.876 | 0.878 |

### 3.5 Feature Importance

```sql
-- Get feature importance
SELECT *
FROM ML.GLOBAL_EXPLAIN(MODEL `penske_logistics.delivery_time_model`)
ORDER BY attribution DESC;
```

**Expected Output:**
| feature | attribution |
|---------|-------------|
| distance_miles | 0.45 |
| pickup_hour | 0.22 |
| weight_kg | 0.15 |
| route_complexity | 0.10 |
| day_of_week | 0.05 |
| vehicle_type_encoded | 0.03 |

**💡 Learning Note**: BigQuery ML's `GLOBAL_EXPLAIN` shows which features contribute most to predictions. Distance is the strongest predictor here.

### 3.6 Make Predictions

```sql
-- Predict delivery time for new shipments
SELECT
  shipment_id,
  origin,
  destination,
  predicted_delivery_time_hours
FROM ML.PREDICT(
  MODEL `penske_logistics.delivery_time_model`,
  (SELECT
    shipment_id,
    origin,
    destination,
    pickup_hour,
    day_of_week,
    distance_miles,
    weight_kg,
    vehicle_type_encoded,
    route_complexity
  FROM `penske_logistics.pending_shipments`)
);
```

### 3.7 Advanced Models

```sql
-- XGBoost model for better accuracy
CREATE OR REPLACE MODEL `penske_logistics.delivery_time_xgboost`
OPTIONS(
  model_type = 'BOOSTED_TREE_REGRESSOR',
  input_label_cols = ['delivery_time_hours'],
  num_parallel_tree = 1,
  max_iterations = 100,
  learn_rate = 0.1,
  l2_reg = 0.1,
  early_stop = TRUE,
  data_split_method = 'AUTO_SPLIT'
) AS
SELECT
  pickup_hour,
  day_of_week,
  distance_miles,
  weight_kg,
  vehicle_type_encoded,
  route_complexity,
  delivery_time_hours
FROM `penske_logistics.delivery_data`;

-- DNN model for complex patterns
CREATE OR REPLACE MODEL `penske_logistics.delivery_time_dnn`
OPTIONS(
  model_type = 'DNN_REGRESSOR',
  input_label_cols = ['delivery_time_hours'],
  hidden_units = [128, 64, 32],
  dropout = 0.2,
  batch_size = 256,
  learn_rate = 0.001
) AS
SELECT
  pickup_hour,
  day_of_week,
  distance_miles,
  weight_kg,
  vehicle_type_encoded,
  route_complexity,
  delivery_time_hours
FROM `penske_logistics.delivery_data`;
```

### 3.8 Export Model to Vertex AI

```sql
-- Export BigQuery ML model to Vertex AI
EXPORT MODEL `penske_logistics.delivery_time_xgboost`
OPTIONS(
  URI = 'gs://penske-logistics-ml-ml-data/bqml-export/delivery_model'
);
```

---

## 4. Generative AI (Gemini)

### 4.1 Basic Text Generation

```python
# gemini_basic.py
import vertexai
from vertexai.generative_models import GenerativeModel

PROJECT_ID = "penske-logistics-ml"
REGION = "us-central1"

vertexai.init(project=PROJECT_ID, location=REGION)

def generate_text(prompt, model_name="gemini-1.5-pro"):
    """Generate text using Gemini"""
    
    model = GenerativeModel(model_name)
    response = model.generate_content(prompt)
    return response.text

# Example: Analyze delivery patterns
prompt = """Analyze this logistics data and provide insights:
- On-time rate: 85%
- Average delay: 28 minutes
- Peak delay times: 7-9 AM, 4-7 PM
- Top routes with delays: Chicago-Detroit (45%), LA-Phoenix (38%)
Provide 3 actionable recommendations."""

response = generate_text(prompt)
print(response)
```

**Expected Output:**
```
Based on the logistics data analysis:

**Key Insights:**
1. The 85% on-time rate falls below industry standard (90%+)
2. Peak delays align with rush hour traffic
3. Chicago-Detroit route shows significant infrastructure issues

**Recommendations:**
1. **Dynamic Departure Scheduling**: Shift departures on high-delay routes to 
   avoid rush hours. For Chicago-Detroit, consider early morning (5-6 AM) or 
   mid-day (10 AM-2 PM) departures.

2. **Route Diversification**: Implement alternative routing for the top 2 
   delay-prone corridors. Use I-94 alternatives for Chicago-Detroit and 
   I-10 alternatives for LA-Phoenix.

3. **Predictive Delay Alerts**: Deploy ML-based delay prediction to proactively 
   notify customers and adjust schedules before delays occur.
```

### 4.2 Chat with Context

```python
# gemini_chat.py
from vertexai.generative_models import GenerativeModel, ChatSession

def create_logistics_assistant():
    """Create a logistics-focused chat assistant"""
    
    model = GenerativeModel(
        "gemini-1.5-pro",
        system_instruction="""You are a logistics analytics expert for Penske Logistics. 
        You help analyze delivery data, optimize routes, and improve operational efficiency.
        Always provide data-driven recommendations with specific metrics when possible."""
    )
    
    return model.start_chat()

# Start conversation
chat = create_logistics_assistant()

# Multi-turn conversation
response1 = chat.send_message("What factors most affect delivery times?")
print(f"🤖 Assistant: {response1.text}\n")

response2 = chat.send_message("How can we reduce traffic-related delays specifically?")
print(f"🤖 Assistant: {response2.text}")
```

### 4.3 Embeddings

```python
# gemini_embeddings.py
from vertexai.language_models import TextEmbeddingModel
import numpy as np

def get_embeddings(texts, task="RETRIEVAL_DOCUMENT"):
    """Get embeddings using Vertex AI"""
    
    model = TextEmbeddingModel.from_pretrained("textembedding-gecko@003")
    embeddings = model.get_embeddings(texts, task_type=task)
    return [emb.values for emb in embeddings]

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# Example: Semantic search over delivery issues
issues = [
    "Package was damaged during shipping",
    "Delivery arrived 3 hours late",
    "Wrong item delivered to customer",
    "Driver couldn't find delivery address",
    "Package marked delivered but not received"
]

# Get embeddings
issue_embeddings = get_embeddings(issues)

# Search
query = "My package is late"
query_embedding = get_embeddings([query], task="RETRIEVAL_QUERY")[0]

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
  [0.923] Delivery arrived 3 hours late
  [0.812] Package marked delivered but not received
  [0.756] Driver couldn't find delivery address
```

### 4.4 Function Calling

```python
# gemini_functions.py
from vertexai.generative_models import GenerativeModel, Tool, FunctionDeclaration

# Define functions
get_delivery_status = FunctionDeclaration(
    name="get_delivery_status",
    description="Get current status of a delivery by tracking number",
    parameters={
        "type": "object",
        "properties": {
            "tracking_number": {
                "type": "string",
                "description": "The shipment tracking number"
            }
        },
        "required": ["tracking_number"]
    }
)

estimate_delivery = FunctionDeclaration(
    name="estimate_delivery",
    description="Estimate delivery time based on origin and destination",
    parameters={
        "type": "object",
        "properties": {
            "origin": {"type": "string"},
            "destination": {"type": "string"},
            "priority": {"type": "string", "enum": ["standard", "express"]}
        },
        "required": ["origin", "destination"]
    }
)

# Create tool
logistics_tool = Tool(function_declarations=[get_delivery_status, estimate_delivery])

# Create model with tools
model = GenerativeModel(
    "gemini-1.5-pro",
    tools=[logistics_tool]
)

# Generate with function calling
response = model.generate_content("Where is my package PK123456789?")

# Check for function calls
for candidate in response.candidates:
    for part in candidate.content.parts:
        if hasattr(part, 'function_call'):
            print(f"🔧 Function: {part.function_call.name}")
            print(f"📋 Args: {dict(part.function_call.args)}")
```

---

## 5. Integration Patterns

### 5.1 Cloud Functions + Vertex AI

```python
# main.py (Cloud Function)
import functions_framework
from google.cloud import aiplatform
import json

PROJECT_ID = "penske-logistics-ml"
REGION = "us-central1"
ENDPOINT_ID = "your-endpoint-id"

@functions_framework.http
def predict_delivery(request):
    """Cloud Function to call Vertex AI endpoint"""
    
    request_json = request.get_json(silent=True)
    
    if not request_json or 'features' not in request_json:
        return json.dumps({"error": "Missing features"}), 400
    
    aiplatform.init(project=PROJECT_ID, location=REGION)
    
    endpoint = aiplatform.Endpoint(ENDPOINT_ID)
    predictions = endpoint.predict(instances=[request_json['features']])
    
    return json.dumps({
        "prediction": predictions.predictions[0],
        "status": "success"
    })
```

### 5.2 Cloud Run + Gemini

```python
# app.py (Cloud Run)
from flask import Flask, request, jsonify
import vertexai
from vertexai.generative_models import GenerativeModel

app = Flask(__name__)

PROJECT_ID = "penske-logistics-ml"
REGION = "us-central1"

vertexai.init(project=PROJECT_ID, location=REGION)
model = GenerativeModel("gemini-1.5-pro")

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    prompt = data.get('prompt', '')
    
    response = model.generate_content(prompt)
    
    return jsonify({
        "response": response.text,
        "status": "success"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
```

---

## 6. Monitoring & Operations

### 6.1 Cloud Monitoring

```python
# setup_monitoring.py
from google.cloud import monitoring_v3

client = monitoring_v3.MetricServiceClient()
project_name = f"projects/{PROJECT_ID}"

# Query endpoint latency
interval = monitoring_v3.TimeInterval({
    "end_time": {"seconds": int(time.time())},
    "start_time": {"seconds": int(time.time()) - 3600}
})

results = client.list_time_series(
    request={
        "name": project_name,
        "filter": 'metric.type="aiplatform.googleapis.com/prediction/online/latency"',
        "interval": interval,
        "view": monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL
    }
)

for result in results:
    print(f"Endpoint: {result.metric.labels['endpoint_id']}")
    for point in result.points:
        print(f"  Latency: {point.value.double_value}ms")
```

### 6.2 Create Alerts

```bash
# Create alert policy for high latency
gcloud alpha monitoring policies create \
    --display-name="High Prediction Latency" \
    --condition-display-name="Latency > 1s" \
    --condition-filter='metric.type="aiplatform.googleapis.com/prediction/online/latency" AND resource.type="aiplatform.googleapis.com/Endpoint"' \
    --condition-threshold-value=1000 \
    --condition-threshold-duration=300s \
    --notification-channels="projects/penske-logistics-ml/notificationChannels/123456"
```

---

## 7. Cost Optimization

### 7.1 Machine Type Recommendations

| Use Case | Machine Type | vCPUs | RAM | Cost/hr | Notes |
|----------|--------------|-------|-----|---------|-------|
| Dev/Test | n1-standard-2 | 2 | 7.5 GB | $0.10 | Basic testing |
| Small Prod | n1-standard-4 | 4 | 15 GB | $0.19 | Balanced |
| High Memory | n1-highmem-4 | 4 | 26 GB | $0.24 | Large models |
| GPU Training | n1-standard-8 + T4 | 8 | 30 GB | $0.76 | ML training |
| GPU Inference | n1-standard-4 + T4 | 4 | 15 GB | $0.54 | Real-time inference |

### 7.2 Auto-Scaling

```python
# autoscaling.py
from google.cloud import aiplatform

endpoint = aiplatform.Endpoint("projects/.../endpoints/...")

# Update with auto-scaling
endpoint.deploy(
    model=model,
    deployed_model_display_name="penske-delivery-autoscale",
    machine_type="n1-standard-2",
    min_replica_count=1,
    max_replica_count=10,
    autoscaling_target_cpu_utilization=70,
    autoscaling_target_accelerator_duty_cycle=60
)

print("✅ Auto-scaling configured")
```

### 7.3 Cleanup Script

```python
# cleanup.py
from google.cloud import aiplatform

PROJECT_ID = "penske-logistics-ml"
REGION = "us-central1"

aiplatform.init(project=PROJECT_ID, location=REGION)

def cleanup_resources():
    """Clean up GCP ML resources"""
    
    # Undeploy and delete endpoints
    for endpoint in aiplatform.Endpoint.list():
        if "penske" in endpoint.display_name.lower():
            print(f"Deleting endpoint: {endpoint.display_name}")
            endpoint.undeploy_all()
            endpoint.delete()
    
    # Delete models
    for model in aiplatform.Model.list():
        if "penske" in model.display_name.lower():
            print(f"Deleting model: {model.display_name}")
            model.delete()
    
    print("✅ Cleanup complete")

if __name__ == '__main__':
    cleanup_resources()
```

---

## Quick Reference

### Common Commands

```bash
# List Vertex AI models
gcloud ai models list --region=us-central1

# List endpoints
gcloud ai endpoints list --region=us-central1

# Get endpoint details
gcloud ai endpoints describe ENDPOINT_ID --region=us-central1

# List BigQuery ML models
bq ls --models penske_logistics

# Describe model
bq show --model penske_logistics.delivery_time_model
```

### Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Permission denied | Missing IAM roles | Add required roles to service account |
| Quota exceeded | Project limits | Request quota increase |
| Model deploy failed | Container issue | Check container logs in Cloud Logging |
| Prediction timeout | Instance undersized | Scale up machine type |
| BigQuery ML error | Invalid SQL | Validate column types match model |

---

## Next Steps

1. ✅ **AWS Setup Complete** - See `AWS_IMPLEMENTATION.md`
2. ✅ **Azure Setup Complete** - See `AZURE_IMPLEMENTATION.md`
3. ✅ **GCP Setup Complete** - Vertex AI, BigQuery ML, and Gemini configured

---

*Last Updated: January 2024*
*Author: Penske Logistics Analytics Team*
