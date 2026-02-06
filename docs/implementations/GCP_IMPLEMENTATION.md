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

## 8. Reusable Templates

> **🔄 This section contains fully reusable code templates that work with ANY dataset.**
> **Simply update the configuration file and the code adapts automatically.**

### 8.1 Configuration File

```yaml
# config/gcp_config.yaml
# ═══════════════════════════════════════════════════════════════════════════════
# 🔧 CHANGE THESE VALUES FOR YOUR PROJECT
# ═══════════════════════════════════════════════════════════════════════════════

gcp:
  project_id: "my-gcp-project"           # ← CHANGE: Your GCP project ID
  region: "us-central1"                   # ← CHANGE: Your region
  bucket_name: "my-ml-bucket"             # ← CHANGE: Your GCS bucket

data:
  # ═══════════════════════════════════════════════════════════════════════════
  # 📊 DEFINE YOUR DATA SCHEMA HERE
  # ═══════════════════════════════════════════════════════════════════════════
  source_file: "data/your_data.csv"       # ← CHANGE: Path to your data file
  target_column: "target"                 # ← CHANGE: Column to predict
  
  feature_columns:                        # ← CHANGE: Your feature columns
    - "feature_1"
    - "feature_2"
    - "feature_3"
    - "feature_4"
  
  datetime_columns:                       # ← CHANGE: Columns to parse as datetime
    - "timestamp_column"
  
  datetime_features:
    hour_column: "timestamp_column"
    dayofweek_column: "timestamp_column"

model:
  # ═══════════════════════════════════════════════════════════════════════════
  # 🤖 MODEL CONFIGURATION
  # ═══════════════════════════════════════════════════════════════════════════
  type: "automl"                          # Options: automl, custom, bigquery_ml
  task: "regression"                      # Options: regression, classification
  
  # For custom training
  algorithm: "gradient_boosting"          # Options: gradient_boosting, random_forest
  hyperparameters:
    n_estimators: 100
    max_depth: 6
    learning_rate: 0.1

training:
  machine_type: "n1-standard-4"           # ← CHANGE: Based on data size
  accelerator_type: null                  # Options: null, NVIDIA_TESLA_T4
  accelerator_count: 0
  test_split: 0.2

deployment:
  endpoint_name: "my-prediction-endpoint" # ← CHANGE: Your endpoint name
  machine_type: "n1-standard-2"           # ← CHANGE: Based on traffic
  min_replicas: 1
  max_replicas: 5

bigquery:
  dataset: "my_dataset"                   # ← CHANGE: Your BigQuery dataset
  model_name: "my_model"                  # ← CHANGE: Your model name

gemini:
  model_name: "gemini-1.5-pro"            # Options: gemini-1.5-pro, gemini-1.5-flash
  system_prompt: "You are a helpful assistant."  # ← CHANGE: Your system prompt
  max_tokens: 1024
```

### 8.2 Reusable Data Preparation Module

```python
# src/gcp/data_utils.py
"""
🔄 REUSABLE DATA PREPARATION FOR GCP VERTEX AI
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Works with ANY dataset - just update config.yaml
"""

import yaml
import pandas as pd
from google.cloud import storage, aiplatform
from pathlib import Path


def load_config(config_path: str = "config/gcp_config.yaml") -> dict:
    """Load configuration from YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def init_vertex_ai(config: dict):
    """
    Initialize Vertex AI with project settings.
    
    🔧 WHAT CHANGES:
    - project_id, region in config
    """
    aiplatform.init(
        project=config['gcp']['project_id'],
        location=config['gcp']['region'],
        staging_bucket=f"gs://{config['gcp']['bucket_name']}"
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


def upload_to_gcs(
    df: pd.DataFrame,
    config: dict,
    filename: str = "data.csv"
) -> str:
    """
    Upload dataframe to Google Cloud Storage.
    
    🔧 USAGE:
        gcs_path = upload_to_gcs(df, config, "train.csv")
    """
    bucket_name = config['gcp']['bucket_name']
    project_id = config['gcp']['project_id']
    
    # Save locally first
    local_path = f"/tmp/{filename}"
    df.to_csv(local_path, index=False)
    
    # Upload to GCS
    storage_client = storage.Client(project=project_id)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(f"data/{filename}")
    blob.upload_from_filename(local_path)
    
    gcs_path = f"gs://{bucket_name}/data/{filename}"
    print(f"✅ Uploaded to: {gcs_path}")
    return gcs_path


def create_dataset(
    gcs_path: str,
    config: dict,
    display_name: str = None
) -> aiplatform.TabularDataset:
    """
    Create Vertex AI TabularDataset.
    
    🔧 USAGE:
        dataset = create_dataset("gs://bucket/data.csv", config)
    """
    init_vertex_ai(config)
    
    dataset = aiplatform.TabularDataset.create(
        display_name=display_name or f"{config['gcp']['project_id']}-dataset",
        gcs_source=gcs_path
    )
    
    print(f"✅ Dataset created: {dataset.display_name}")
    return dataset


def prepare_and_upload(config_path: str = "config/gcp_config.yaml"):
    """
    Main function to prepare and upload data.
    
    🔧 USAGE:
        python -m src.gcp.data_utils
    """
    from sklearn.model_selection import train_test_split
    
    config = load_config(config_path)
    print(f"📋 Project: {config['gcp']['project_id']}")
    print(f"📊 Target: {config['data']['target_column']}")
    
    # Load and prepare data
    df = pd.read_csv(config['data']['source_file'])
    print(f"📂 Loaded {len(df)} rows")
    
    df = prepare_features(df, config)
    
    # Split
    test_size = config['training'].get('test_split', 0.2)
    train_df, test_df = train_test_split(df, test_size=test_size, random_state=42)
    
    # Upload
    train_path = upload_to_gcs(train_df, config, "train.csv")
    test_path = upload_to_gcs(test_df, config, "test.csv")
    
    # Create dataset
    dataset = create_dataset(train_path, config, "train-dataset")
    
    return dataset, train_path, test_path


if __name__ == "__main__":
    prepare_and_upload()
```

### 8.3 Reusable Training Module

```python
# src/gcp/train.py
"""
🔄 REUSABLE VERTEX AI TRAINING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Works with ANY dataset - just update config.yaml
"""

from google.cloud import aiplatform
from google.cloud.aiplatform import CustomTrainingJob, AutoMLTabularTrainingJob

from .data_utils import load_config, init_vertex_ai


def train_automl(
    dataset: aiplatform.TabularDataset,
    config_path: str = "config/gcp_config.yaml"
):
    """
    Train using AutoML.
    
    🔧 WHAT CHANGES:
    - target_column in config
    - task type (regression/classification)
    """
    config = load_config(config_path)
    init_vertex_ai(config)
    
    # Determine optimization objective
    if config['model']['task'] == 'regression':
        optimization_type = "regression"
        objective = "minimize-rmse"
    else:
        optimization_type = "classification"
        objective = "maximize-au-roc"
    
    job = AutoMLTabularTrainingJob(
        display_name=f"{config['gcp']['project_id']}-automl",
        optimization_prediction_type=optimization_type,
        optimization_objective=objective
    )
    
    print(f"🚀 Starting AutoML training...")
    model = job.run(
        dataset=dataset,
        target_column=config['data']['target_column'],
        training_fraction_split=0.8,
        validation_fraction_split=0.1,
        test_fraction_split=0.1,
        budget_milli_node_hours=1000,
        model_display_name=f"{config['gcp']['project_id']}-model"
    )
    
    print(f"✅ Model trained: {model.display_name}")
    return model


def train_custom(
    train_path: str,
    config_path: str = "config/gcp_config.yaml"
):
    """
    Train using custom training job.
    
    🔧 WHAT CHANGES:
    - Algorithm, hyperparameters from config
    - Machine type from config
    """
    config = load_config(config_path)
    init_vertex_ai(config)
    
    # Build hyperparameter arguments
    hyperparams = config['model']['hyperparameters']
    hyperparam_args = []
    for k, v in hyperparams.items():
        hyperparam_args.extend([f"--{k}", str(v)])
    
    job = CustomTrainingJob(
        display_name=f"{config['gcp']['project_id']}-custom",
        script_path="src/gcp/train_script.py",
        container_uri="us-docker.pkg.dev/vertex-ai/training/scikit-learn-cpu.1-0:latest",
        requirements=["pandas", "numpy", "scikit-learn", "pyyaml"],
        model_serving_container_image_uri="us-docker.pkg.dev/vertex-ai/prediction/sklearn-cpu.1-0:latest"
    )
    
    print(f"🚀 Starting custom training...")
    model = job.run(
        replica_count=1,
        machine_type=config['training']['machine_type'],
        args=[
            "--data-path", train_path,
            "--target", config['data']['target_column'],
            "--task", config['model']['task'],
            "--algorithm", config['model']['algorithm']
        ] + hyperparam_args,
        model_display_name=f"{config['gcp']['project_id']}-model"
    )
    
    print(f"✅ Model trained: {model.display_name}")
    return model


def train_model(config_path: str = "config/gcp_config.yaml", dataset=None, train_path=None):
    """
    Train model based on configuration.
    
    🔧 USAGE:
        from src.gcp.train import train_model
        model = train_model("config/gcp_config.yaml", dataset=my_dataset)
    """
    config = load_config(config_path)
    
    if config['model']['type'] == 'automl':
        if dataset is None:
            raise ValueError("Dataset required for AutoML training")
        return train_automl(dataset, config_path)
    elif config['model']['type'] == 'custom':
        if train_path is None:
            raise ValueError("train_path required for custom training")
        return train_custom(train_path, config_path)
    else:
        raise ValueError(f"Unknown model type: {config['model']['type']}")
```

### 8.4 Reusable Training Script

```python
# src/gcp/train_script.py
"""
🔄 GENERIC TRAINING SCRIPT FOR VERTEX AI
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Works with ANY dataset via command-line arguments
"""

import argparse
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor, GradientBoostingClassifier
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, f1_score
import joblib
import os


def get_model(algorithm: str, task: str, **hyperparams):
    """Get model based on algorithm and task."""
    models = {
        ('gradient_boosting', 'regression'): GradientBoostingRegressor,
        ('gradient_boosting', 'classification'): GradientBoostingClassifier,
        ('random_forest', 'regression'): RandomForestRegressor,
        ('random_forest', 'classification'): RandomForestClassifier,
    }
    
    model_class = models.get((algorithm, task))
    if model_class is None:
        raise ValueError(f"Unsupported: {algorithm} + {task}")
    
    # Filter out None values
    hyperparams = {k: v for k, v in hyperparams.items() if v is not None}
    return model_class(**hyperparams, random_state=42)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-path", type=str, required=True)
    parser.add_argument("--target", type=str, required=True)
    parser.add_argument("--task", type=str, default="regression")
    parser.add_argument("--algorithm", type=str, default="gradient_boosting")
    parser.add_argument("--n_estimators", type=int, default=100)
    parser.add_argument("--max_depth", type=int, default=6)
    parser.add_argument("--learning_rate", type=float, default=0.1)
    args = parser.parse_args()
    
    # Load data
    print(f"📂 Loading: {args.data_path}")
    df = pd.read_csv(args.data_path)
    
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
    else:
        acc = accuracy_score(y_test, predictions)
        f1 = f1_score(y_test, predictions, average='weighted')
        print(f"📊 Accuracy: {acc:.4f}, F1: {f1:.4f}")
    
    # Save model (Vertex AI expects model in AIP_MODEL_DIR)
    model_dir = os.environ.get("AIP_MODEL_DIR", "./model")
    os.makedirs(model_dir, exist_ok=True)
    joblib.dump(model, os.path.join(model_dir, "model.joblib"))
    print(f"✅ Model saved to: {model_dir}")


if __name__ == "__main__":
    main()
```

### 8.5 Reusable Deployment Module

```python
# src/gcp/deploy.py
"""
🔄 REUSABLE VERTEX AI DEPLOYMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Works with ANY model - just update config.yaml
"""

from google.cloud import aiplatform

from .data_utils import load_config, init_vertex_ai


def deploy_model(
    model: aiplatform.Model,
    config_path: str = "config/gcp_config.yaml"
):
    """
    Deploy model to endpoint.
    
    🔧 USAGE:
        from src.gcp.deploy import deploy_model
        endpoint = deploy_model(model, "config/gcp_config.yaml")
    """
    config = load_config(config_path)
    init_vertex_ai(config)
    
    # Create endpoint
    print(f"🚀 Creating endpoint: {config['deployment']['endpoint_name']}")
    endpoint = aiplatform.Endpoint.create(
        display_name=config['deployment']['endpoint_name'],
        project=config['gcp']['project_id'],
        location=config['gcp']['region']
    )
    
    # Deploy model
    print(f"🚀 Deploying model...")
    deployed_model = model.deploy(
        endpoint=endpoint,
        deployed_model_display_name=f"{config['gcp']['project_id']}-deployed",
        machine_type=config['deployment']['machine_type'],
        min_replica_count=config['deployment']['min_replicas'],
        max_replica_count=config['deployment']['max_replicas'],
        traffic_percentage=100
    )
    
    print(f"✅ Endpoint: {endpoint.display_name}")
    print(f"✅ Resource: {endpoint.resource_name}")
    return endpoint


def predict(features: list, config_path: str = "config/gcp_config.yaml"):
    """
    Make prediction using deployed endpoint.
    
    🔧 USAGE:
        result = predict([1.2, 3.4, 5.6], "config/gcp_config.yaml")
    """
    config = load_config(config_path)
    init_vertex_ai(config)
    
    # Get endpoint
    endpoints = aiplatform.Endpoint.list(
        filter=f'display_name="{config["deployment"]["endpoint_name"]}"'
    )
    
    if not endpoints:
        raise ValueError(f"Endpoint not found: {config['deployment']['endpoint_name']}")
    
    endpoint = endpoints[0]
    predictions = endpoint.predict(instances=[features])
    
    return predictions.predictions


def cleanup(config_path: str = "config/gcp_config.yaml"):
    """Clean up GCP resources."""
    config = load_config(config_path)
    init_vertex_ai(config)
    
    # Delete endpoints
    for endpoint in aiplatform.Endpoint.list():
        if config['gcp']['project_id'] in endpoint.display_name.lower():
            print(f"Deleting endpoint: {endpoint.display_name}")
            endpoint.undeploy_all()
            endpoint.delete()
    
    # Delete models
    for model in aiplatform.Model.list():
        if config['gcp']['project_id'] in model.display_name.lower():
            print(f"Deleting model: {model.display_name}")
            model.delete()
    
    print("✅ Cleanup complete")
```

### 8.6 Reusable BigQuery ML Module

```python
# src/gcp/bigquery_ml.py
"""
🔄 REUSABLE BIGQUERY ML UTILITIES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Works with ANY dataset - just update config.yaml
"""

from google.cloud import bigquery
from typing import List

from .data_utils import load_config


class BigQueryMLClient:
    """
    Reusable BigQuery ML client.
    
    🔧 USAGE:
        client = BigQueryMLClient("config/gcp_config.yaml")
        client.create_model(["feature1", "feature2"], "target")
        predictions = client.predict("SELECT * FROM my_table")
    """
    
    def __init__(self, config_path: str = "config/gcp_config.yaml"):
        self.config = load_config(config_path)
        self.client = bigquery.Client(project=self.config['gcp']['project_id'])
        self.dataset = self.config['bigquery']['dataset']
        self.model_name = self.config['bigquery']['model_name']
    
    def create_model(
        self,
        feature_columns: List[str],
        target_column: str,
        source_table: str
    ) -> str:
        """
        Create BigQuery ML model.
        
        🔧 USAGE:
            client.create_model(["col1", "col2"], "target", "my_dataset.my_table")
        """
        task = self.config['model']['task']
        
        if task == 'regression':
            model_type = 'BOOSTED_TREE_REGRESSOR'
        else:
            model_type = 'BOOSTED_TREE_CLASSIFIER'
        
        columns = ', '.join(feature_columns + [target_column])
        
        query = f"""
        CREATE OR REPLACE MODEL `{self.dataset}.{self.model_name}`
        OPTIONS(
            model_type = '{model_type}',
            input_label_cols = ['{target_column}'],
            data_split_method = 'AUTO_SPLIT',
            enable_global_explain = TRUE
        ) AS
        SELECT {columns}
        FROM `{source_table}`
        """
        
        print(f"🚀 Creating BigQuery ML model...")
        job = self.client.query(query)
        job.result()
        
        print(f"✅ Model created: {self.dataset}.{self.model_name}")
        return f"{self.dataset}.{self.model_name}"
    
    def evaluate(self) -> dict:
        """Evaluate model performance."""
        query = f"SELECT * FROM ML.EVALUATE(MODEL `{self.dataset}.{self.model_name}`)"
        result = self.client.query(query).result()
        
        metrics = {}
        for row in result:
            metrics = dict(row.items())
        
        print(f"📊 Metrics: {metrics}")
        return metrics
    
    def predict(self, source_query: str) -> list:
        """Make predictions on new data."""
        query = f"""
        SELECT *
        FROM ML.PREDICT(
            MODEL `{self.dataset}.{self.model_name}`,
            ({source_query})
        )
        """
        
        result = self.client.query(query).result()
        predictions = [dict(row.items()) for row in result]
        return predictions
    
    def feature_importance(self) -> list:
        """Get feature importance."""
        query = f"""
        SELECT * FROM ML.GLOBAL_EXPLAIN(MODEL `{self.dataset}.{self.model_name}`)
        ORDER BY attribution DESC
        """
        
        result = self.client.query(query).result()
        importance = [dict(row.items()) for row in result]
        
        print("📊 Feature Importance:")
        for feat in importance:
            print(f"  {feat['feature']}: {feat['attribution']:.4f}")
        
        return importance
```

### 8.7 Reusable Gemini Module

```python
# src/gcp/gemini_utils.py
"""
🔄 REUSABLE GEMINI UTILITIES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Works with ANY use case - just update config.yaml
"""

import vertexai
from vertexai.generative_models import GenerativeModel
from vertexai.language_models import TextEmbeddingModel
import numpy as np
from typing import List, Dict, Any

from .data_utils import load_config


class GeminiClient:
    """
    Reusable Gemini client.
    
    🔧 USAGE:
        client = GeminiClient("config/gcp_config.yaml")
        response = client.generate("Hello!")
        embeddings = client.get_embeddings(["text1", "text2"])
    """
    
    def __init__(self, config_path: str = "config/gcp_config.yaml"):
        self.config = load_config(config_path)
        
        vertexai.init(
            project=self.config['gcp']['project_id'],
            location=self.config['gcp']['region']
        )
        
        self.model = GenerativeModel(
            self.config['gemini']['model_name'],
            system_instruction=self.config['gemini'].get('system_prompt', '')
        )
        self.embedding_model = TextEmbeddingModel.from_pretrained("textembedding-gecko@003")
    
    def generate(self, prompt: str, max_tokens: int = None) -> str:
        """Generate text using Gemini."""
        max_tokens = max_tokens or self.config['gemini']['max_tokens']
        
        response = self.model.generate_content(
            prompt,
            generation_config={"max_output_tokens": max_tokens}
        )
        return response.text
    
    def chat(self, messages: List[str]) -> str:
        """Multi-turn chat conversation."""
        chat = self.model.start_chat()
        
        response = None
        for message in messages:
            response = chat.send_message(message)
        
        return response.text if response else ""
    
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for texts."""
        embeddings = self.embedding_model.get_embeddings(texts, task_type="RETRIEVAL_DOCUMENT")
        return [emb.values for emb in embeddings]
    
    def semantic_search(self, query: str, documents: List[str], top_k: int = 3) -> List[Dict]:
        """Search documents by semantic similarity."""
        query_emb = self.embedding_model.get_embeddings([query], task_type="RETRIEVAL_QUERY")[0].values
        doc_embs = self.get_embeddings(documents)
        
        similarities = []
        for i, doc_emb in enumerate(doc_embs):
            sim = np.dot(query_emb, doc_emb) / (np.linalg.norm(query_emb) * np.linalg.norm(doc_emb))
            similarities.append({'document': documents[i], 'score': float(sim), 'index': i})
        
        return sorted(similarities, key=lambda x: x['score'], reverse=True)[:top_k]


# Convenience functions
def generate(prompt: str, config_path: str = "config/gcp_config.yaml") -> str:
    return GeminiClient(config_path).generate(prompt)

def search(query: str, docs: List[str], config_path: str = "config/gcp_config.yaml") -> List[Dict]:
    return GeminiClient(config_path).semantic_search(query, docs)
```

### 8.8 Complete Pipeline Example

```python
# run_gcp_pipeline.py
"""
🔄 COMPLETE GCP ML PIPELINE
━━━━━━━━━━━━━━━━━━━━━━━━━━━
Run the entire pipeline with one command!

🔧 USAGE:
    python run_gcp_pipeline.py --config config/gcp_config.yaml
    python run_gcp_pipeline.py --config config/gcp_config.yaml --automl
"""

import argparse
from src.gcp.data_utils import prepare_and_upload, load_config
from src.gcp.train import train_model
from src.gcp.deploy import deploy_model, predict


def main():
    parser = argparse.ArgumentParser(description="GCP ML Pipeline")
    parser.add_argument("--config", default="config/gcp_config.yaml")
    parser.add_argument("--automl", action="store_true", help="Use AutoML")
    parser.add_argument("--skip-train", action="store_true")
    parser.add_argument("--test", action="store_true")
    args = parser.parse_args()
    
    config = load_config(args.config)
    print("=" * 60)
    print(f"🚀 GCP ML Pipeline: {config['gcp']['project_id']}")
    print("=" * 60)
    
    # Step 1: Prepare data
    print("\n📊 Step 1: Preparing and uploading data...")
    dataset, train_path, test_path = prepare_and_upload(args.config)
    
    # Step 2: Train
    if not args.skip_train:
        print("\n🚀 Step 2: Training model...")
        if args.automl:
            model = train_model(args.config, dataset=dataset)
        else:
            model = train_model(args.config, train_path=train_path)
    
    # Step 3: Deploy
    print("\n🌐 Step 3: Deploying model...")
    endpoint = deploy_model(model, args.config)
    
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

### 8.9 What to Change Summary

| Component | What to Change | Where to Change |
|-----------|----------------|-----------------|
| **GCP project** | `gcp.project_id` | `config/gcp_config.yaml` |
| **Region** | `gcp.region` | `config/gcp_config.yaml` |
| **Bucket** | `gcp.bucket_name` | `config/gcp_config.yaml` |
| **Data file** | `data.source_file` | `config/gcp_config.yaml` |
| **Target column** | `data.target_column` | `config/gcp_config.yaml` |
| **Feature columns** | `data.feature_columns` | `config/gcp_config.yaml` |
| **Model type** | `model.type` (automl/custom/bigquery_ml) | `config/gcp_config.yaml` |
| **Task type** | `model.task` | `config/gcp_config.yaml` |
| **Algorithm** | `model.algorithm` | `config/gcp_config.yaml` |
| **Hyperparameters** | `model.hyperparameters` | `config/gcp_config.yaml` |
| **Machine type** | `training.machine_type`, `deployment.machine_type` | `config/gcp_config.yaml` |
| **Endpoint** | `deployment.endpoint_name` | `config/gcp_config.yaml` |
| **BigQuery dataset** | `bigquery.dataset` | `config/gcp_config.yaml` |
| **Gemini model** | `gemini.model_name` | `config/gcp_config.yaml` |
| **System prompt** | `gemini.system_prompt` | `config/gcp_config.yaml` |

---

## Next Steps

1. ✅ **AWS Setup Complete** - See `AWS_IMPLEMENTATION.md`
2. ✅ **Azure Setup Complete** - See `AZURE_IMPLEMENTATION.md`
3. ✅ **GCP Setup Complete** - Vertex AI, BigQuery ML, and Gemini configured

---

*Last Updated: January 2024*
*Author: Penske Logistics Analytics Team*
