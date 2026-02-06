# AWS Implementation Guide
## Penske Logistics Analytics - SageMaker & Bedrock

> **Purpose**: Step-by-step implementation guide for deploying ML solutions on AWS
> **Prerequisites**: AWS account, basic Python knowledge, familiarity with ML concepts
> **Estimated Time**: 4-6 hours for complete setup

---

## Table of Contents
1. [Environment Setup](#1-environment-setup)
2. [SageMaker Implementation](#2-sagemaker-implementation)
3. [Bedrock Implementation](#3-bedrock-implementation)
4. [Integration Patterns](#4-integration-patterns)
5. [Monitoring & Operations](#5-monitoring--operations)
6. [Cost Optimization](#6-cost-optimization)

---

## 1. Environment Setup

### 1.1 AWS CLI Configuration

```bash
# Install AWS CLI (if not installed)
# Windows: Download from https://aws.amazon.com/cli/
# macOS: brew install awscli
# Linux: sudo apt-get install awscli

# Configure credentials
aws configure
```

**Expected Output:**
```
AWS Access Key ID [None]: AKIAIOSFODNN7EXAMPLE
AWS Secret Access Key [None]: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
Default region name [None]: us-east-1
Default output format [None]: json
```

**💡 Learning Note**: AWS CLI credentials are stored in `~/.aws/credentials`. Never commit these to version control. Use IAM roles in production.

### 1.2 Required IAM Permissions

Create an IAM policy with these permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "sagemaker:*",
                "bedrock:*",
                "s3:*",
                "logs:*",
                "ecr:*",
                "iam:PassRole"
            ],
            "Resource": "*"
        }
    ]
}
```

**⚠️ Security Note**: This is a broad policy for development. In production, scope down to specific resources.

### 1.3 Python Environment Setup

```bash
# Create virtual environment
python -m venv aws-ml-env
source aws-ml-env/bin/activate  # Linux/macOS
# or: aws-ml-env\Scripts\activate  # Windows

# Install required packages
pip install boto3 sagemaker pandas numpy scikit-learn
```

### 1.4 Verify Setup

```python
# test_aws_setup.py
import boto3
import sagemaker

# Test AWS connection
sts = boto3.client('sts')
identity = sts.get_caller_identity()
print(f"✅ Connected as: {identity['Arn']}")

# Test SageMaker session
session = sagemaker.Session()
print(f"✅ SageMaker bucket: {session.default_bucket()}")
print(f"✅ Region: {session.boto_region_name}")
```

**Expected Output:**
```
✅ Connected as: arn:aws:iam::123456789012:user/your-username
✅ SageMaker bucket: sagemaker-us-east-1-123456789012
✅ Region: us-east-1
```

---

## 2. SageMaker Implementation

### 2.1 Data Preparation & Upload

```python
# prepare_data.py
import boto3
import pandas as pd
from sagemaker import Session

# Initialize session
sagemaker_session = Session()
bucket = sagemaker_session.default_bucket()
prefix = 'penske-logistics/delivery-prediction'

# Load your logistics data
df = pd.read_csv('logistics_data.csv')

# Feature engineering for delivery prediction
df['pickup_hour'] = pd.to_datetime(df['pickup_time']).dt.hour
df['day_of_week'] = pd.to_datetime(df['pickup_time']).dt.dayofweek
df['distance_miles'] = df['distance_km'] * 0.621371

# Prepare features and target
features = ['pickup_hour', 'day_of_week', 'distance_miles', 
            'weight_kg', 'vehicle_type_encoded', 'route_complexity']
target = 'delivery_time_hours'

# Split data
from sklearn.model_selection import train_test_split
train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)

# Save to CSV (SageMaker XGBoost expects target in first column)
train_df[[target] + features].to_csv('train.csv', index=False, header=False)
test_df[[target] + features].to_csv('test.csv', index=False, header=False)

# Upload to S3
train_path = sagemaker_session.upload_data('train.csv', bucket=bucket, 
                                            key_prefix=f'{prefix}/train')
test_path = sagemaker_session.upload_data('test.csv', bucket=bucket, 
                                           key_prefix=f'{prefix}/test')

print(f"✅ Training data uploaded to: {train_path}")
print(f"✅ Test data uploaded to: {test_path}")
```

**Expected Output:**
```
✅ Training data uploaded to: s3://sagemaker-us-east-1-123456789012/penske-logistics/delivery-prediction/train/train.csv
✅ Test data uploaded to: s3://sagemaker-us-east-1-123456789012/penske-logistics/delivery-prediction/test/test.csv
```

**💡 Learning Note**: SageMaker's built-in algorithms expect data in specific formats. XGBoost requires the target variable in the first column with no headers.

### 2.2 Training with Built-in XGBoost

```python
# train_xgboost.py
import sagemaker
from sagemaker import image_uris
from sagemaker.inputs import TrainingInput

# Get execution role
role = sagemaker.get_execution_role()  # In notebook
# Or specify directly: role = 'arn:aws:iam::123456789012:role/SageMakerRole'

# Get XGBoost container image
container = image_uris.retrieve(
    framework='xgboost',
    region='us-east-1',
    version='1.5-1'
)
print(f"📦 Using container: {container}")

# Configure the estimator
xgb_estimator = sagemaker.estimator.Estimator(
    image_uri=container,
    role=role,
    instance_count=1,
    instance_type='ml.m5.xlarge',
    output_path=f's3://{bucket}/{prefix}/output',
    sagemaker_session=sagemaker_session,
    
    # Hyperparameters
    hyperparameters={
        'objective': 'reg:squarederror',  # Regression for delivery time
        'num_round': 100,
        'max_depth': 6,
        'eta': 0.3,
        'subsample': 0.8,
        'colsample_bytree': 0.8,
        'early_stopping_rounds': 10
    }
)

# Define input channels
train_input = TrainingInput(
    s3_data=train_path,
    content_type='text/csv'
)
validation_input = TrainingInput(
    s3_data=test_path,
    content_type='text/csv'
)

# Start training
print("🚀 Starting training job...")
xgb_estimator.fit({
    'train': train_input,
    'validation': validation_input
}, wait=True)

print(f"✅ Model artifacts: {xgb_estimator.model_data}")
```

**Expected Output:**
```
📦 Using container: 683313688378.dkr.ecr.us-east-1.amazonaws.com/sagemaker-xgboost:1.5-1
🚀 Starting training job...
2024-01-15 10:30:00 Starting - Starting the training job...
2024-01-15 10:32:00 Training - Training image download completed...
2024-01-15 10:35:00 Completed - Training job completed
✅ Model artifacts: s3://sagemaker-us-east-1-123456789012/penske-logistics/delivery-prediction/output/xgboost-2024-01-15-10-30-00/output/model.tar.gz
```

**💡 Learning Note**: Training time depends on data size and instance type. `ml.m5.xlarge` is cost-effective for medium datasets. Use `ml.p3.2xlarge` for deep learning.

### 2.3 Hyperparameter Tuning

```python
# hyperparameter_tuning.py
from sagemaker.tuner import HyperparameterTuner, ContinuousParameter, IntegerParameter

# Define hyperparameter ranges
hyperparameter_ranges = {
    'eta': ContinuousParameter(0.01, 0.3),
    'max_depth': IntegerParameter(3, 10),
    'subsample': ContinuousParameter(0.5, 1.0),
    'colsample_bytree': ContinuousParameter(0.5, 1.0),
    'num_round': IntegerParameter(50, 200)
}

# Create tuner
tuner = HyperparameterTuner(
    estimator=xgb_estimator,
    objective_metric_name='validation:rmse',
    objective_type='Minimize',
    hyperparameter_ranges=hyperparameter_ranges,
    max_jobs=20,
    max_parallel_jobs=4,
    strategy='Bayesian'
)

# Start tuning
print("🔧 Starting hyperparameter tuning...")
tuner.fit({
    'train': train_input,
    'validation': validation_input
}, wait=False)

print(f"📊 Tuning job: {tuner.latest_tuning_job.name}")
```

**Expected Output:**
```
🔧 Starting hyperparameter tuning...
📊 Tuning job: xgboost-tuning-2024-01-15-11-00-00
```

**💡 Learning Note**: Bayesian optimization is more efficient than random search. It learns from previous trials to find better hyperparameters faster.

### 2.4 Deploy Model to Endpoint

```python
# deploy_model.py
from sagemaker.serializers import CSVSerializer
from sagemaker.deserializers import JSONDeserializer

# Deploy the trained model
print("🚀 Deploying model to endpoint...")
predictor = xgb_estimator.deploy(
    initial_instance_count=1,
    instance_type='ml.m5.large',
    serializer=CSVSerializer(),
    deserializer=JSONDeserializer()
)

print(f"✅ Endpoint created: {predictor.endpoint_name}")

# Test the endpoint
test_data = "8,2,45.5,1200,1,3"  # Example: 8am, Tuesday, 45.5 miles, 1200kg, van, medium complexity
result = predictor.predict(test_data)
print(f"📦 Predicted delivery time: {result} hours")
```

**Expected Output:**
```
🚀 Deploying model to endpoint...
✅ Endpoint created: xgboost-2024-01-15-12-00-00
📦 Predicted delivery time: 2.35 hours
```

### 2.5 Batch Transform for Large-Scale Predictions

```python
# batch_transform.py
from sagemaker.transformer import Transformer

# Create transformer
transformer = xgb_estimator.transformer(
    instance_count=1,
    instance_type='ml.m5.xlarge',
    output_path=f's3://{bucket}/{prefix}/batch-predictions'
)

# Run batch transform
print("📊 Starting batch transform...")
transformer.transform(
    data=f's3://{bucket}/{prefix}/batch-input',
    content_type='text/csv',
    split_type='Line'
)
transformer.wait()

print(f"✅ Predictions saved to: {transformer.output_path}")
```

**💡 Learning Note**: Use batch transform for large-scale offline predictions. It's more cost-effective than keeping an endpoint running 24/7.

---

## 3. Bedrock Implementation

### 3.1 Enable Bedrock Model Access

Before using Bedrock, you must request access to foundation models:

1. Go to AWS Console → Amazon Bedrock → Model access
2. Click "Manage model access"
3. Select models (e.g., Claude 3 Sonnet, Titan Embeddings)
4. Submit request (usually approved within minutes)

### 3.2 Basic Text Generation

```python
# bedrock_basic.py
import boto3
import json

# Initialize Bedrock client
bedrock = boto3.client(
    service_name='bedrock-runtime',
    region_name='us-east-1'
)

def generate_text(prompt, model_id='anthropic.claude-3-sonnet-20240229-v1:0'):
    """Generate text using Claude 3 Sonnet"""
    
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1024,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    })
    
    response = bedrock.invoke_model(
        modelId=model_id,
        body=body,
        contentType='application/json',
        accept='application/json'
    )
    
    result = json.loads(response['body'].read())
    return result['content'][0]['text']

# Example: Analyze delivery delay
prompt = """Analyze this delivery data and suggest improvements:
- Average delay: 45 minutes
- Main causes: Traffic (40%), Weather (25%), Loading time (20%), Route issues (15%)
- Peak delay hours: 7-9 AM, 4-6 PM
Provide 3 actionable recommendations."""

response = generate_text(prompt)
print(response)
```

**Expected Output:**
```
Based on the delivery data analysis, here are 3 actionable recommendations:

1. **Dynamic Route Optimization**: Implement real-time traffic integration to avoid 
   congested routes during peak hours (7-9 AM, 4-6 PM). This could reduce traffic-related 
   delays by 50-60%.

2. **Pre-staging and Loading Optimization**: Standardize loading procedures and 
   pre-stage deliveries the night before. Consider zone-based loading to reduce 
   loading time by 30-40%.

3. **Weather-Adaptive Scheduling**: Build buffer time into schedules during 
   weather-prone seasons and implement predictive weather alerts to proactively 
   adjust routes and timing.
```

### 3.3 Embeddings for Semantic Search

```python
# bedrock_embeddings.py
import boto3
import json
import numpy as np

bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

def get_embedding(text, model_id='amazon.titan-embed-text-v1'):
    """Get text embedding using Titan"""
    
    body = json.dumps({
        "inputText": text
    })
    
    response = bedrock.invoke_model(
        modelId=model_id,
        body=body,
        contentType='application/json',
        accept='application/json'
    )
    
    result = json.loads(response['body'].read())
    return result['embedding']

def cosine_similarity(a, b):
    """Calculate cosine similarity between two vectors"""
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# Example: Find similar delivery issues
documents = [
    "Delivery delayed due to heavy traffic on highway",
    "Package damaged during transit",
    "Customer not available at delivery location",
    "Vehicle breakdown caused delivery delay",
    "Incorrect address provided by customer"
]

# Get embeddings for all documents
doc_embeddings = [get_embedding(doc) for doc in documents]

# Search query
query = "Why was my package late?"
query_embedding = get_embedding(query)

# Find most similar documents
similarities = [cosine_similarity(query_embedding, doc_emb) for doc_emb in doc_embeddings]
ranked = sorted(zip(documents, similarities), key=lambda x: x[1], reverse=True)

print("🔍 Most relevant issues:")
for doc, score in ranked[:3]:
    print(f"  [{score:.3f}] {doc}")
```

**Expected Output:**
```
🔍 Most relevant issues:
  [0.892] Delivery delayed due to heavy traffic on highway
  [0.834] Vehicle breakdown caused delivery delay
  [0.756] Customer not available at delivery location
```

### 3.4 Knowledge Base with RAG

```python
# bedrock_knowledge_base.py
import boto3

bedrock_agent = boto3.client('bedrock-agent-runtime', region_name='us-east-1')

def query_knowledge_base(question, kb_id):
    """Query knowledge base using RAG"""
    
    response = bedrock_agent.retrieve_and_generate(
        input={
            "text": question
        },
        retrieveAndGenerateConfiguration={
            "type": "KNOWLEDGE_BASE",
            "knowledgeBaseConfiguration": {
                "knowledgeBaseId": kb_id,
                "modelArn": "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0"
            }
        }
    )
    
    return response["output"]["text"]

# Example usage
kb_id = "your-knowledge-base-id"
question = "What are the main causes of delivery delays in the Midwest region?"
answer = query_knowledge_base(question, kb_id)
print(f"📚 Answer: {answer}")
```

**💡 Learning Note**: RAG (Retrieval Augmented Generation) combines the power of LLMs with your proprietary data. The knowledge base automatically chunks, embeds, and stores your documents.

### 3.5 Streaming Responses

```python
# bedrock_streaming.py
import boto3
import json

bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

def stream_response(prompt):
    """Stream response from Claude for real-time output"""
    
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": prompt}]
    })
    
    response = bedrock.invoke_model_with_response_stream(
        modelId='anthropic.claude-3-sonnet-20240229-v1:0',
        body=body,
        contentType='application/json'
    )
    
    print("🤖 Response: ", end="")
    for event in response['body']:
        chunk = json.loads(event['chunk']['bytes'])
        if chunk['type'] == 'content_block_delta':
            print(chunk['delta'].get('text', ''), end="", flush=True)
    print()

# Example
stream_response("Summarize best practices for logistics route optimization in 3 bullet points.")
```

---

## 4. Integration Patterns

### 4.1 Lambda + SageMaker Endpoint

```python
# lambda_function.py
import boto3
import json

runtime = boto3.client('sagemaker-runtime')

def lambda_handler(event, context):
    """Lambda function to invoke SageMaker endpoint"""
    
    # Parse input
    body = json.loads(event['body'])
    features = body['features']  # [hour, day, distance, weight, vehicle, complexity]
    
    # Format for XGBoost
    payload = ','.join(map(str, features))
    
    # Invoke endpoint
    response = runtime.invoke_endpoint(
        EndpointName='delivery-prediction-endpoint',
        ContentType='text/csv',
        Body=payload
    )
    
    # Parse result
    prediction = json.loads(response['Body'].read().decode())
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'predicted_delivery_hours': prediction,
            'confidence': 0.95
        })
    }
```

### 4.2 API Gateway + Bedrock

```python
# lambda_bedrock.py
import boto3
import json

bedrock = boto3.client('bedrock-runtime')

def lambda_handler(event, context):
    """Lambda function for Bedrock text generation"""
    
    body = json.loads(event['body'])
    prompt = body['prompt']
    
    bedrock_body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": prompt}]
    })
    
    response = bedrock.invoke_model(
        modelId='anthropic.claude-3-sonnet-20240229-v1:0',
        body=bedrock_body,
        contentType='application/json'
    )
    
    result = json.loads(response['body'].read())
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'response': result['content'][0]['text']
        })
    }
```

---

## 5. Monitoring & Operations

### 5.1 CloudWatch Metrics

```python
# setup_monitoring.py
import boto3

cloudwatch = boto3.client('cloudwatch')

# Create alarm for endpoint latency
cloudwatch.put_metric_alarm(
    AlarmName='SageMaker-HighLatency',
    MetricName='ModelLatency',
    Namespace='AWS/SageMaker',
    Statistic='Average',
    Period=300,
    EvaluationPeriods=2,
    Threshold=1000,  # 1 second
    ComparisonOperator='GreaterThanThreshold',
    Dimensions=[
        {'Name': 'EndpointName', 'Value': 'delivery-prediction-endpoint'},
        {'Name': 'VariantName', 'Value': 'AllTraffic'}
    ],
    AlarmActions=['arn:aws:sns:us-east-1:123456789012:ml-alerts']
)

print("✅ Latency alarm created")
```

### 5.2 Model Monitoring

```python
# model_monitoring.py
from sagemaker.model_monitor import DataCaptureConfig, DefaultModelMonitor

# Enable data capture on endpoint
data_capture_config = DataCaptureConfig(
    enable_capture=True,
    sampling_percentage=100,
    destination_s3_uri=f's3://{bucket}/{prefix}/data-capture'
)

# Create monitoring schedule
monitor = DefaultModelMonitor(
    role=role,
    instance_count=1,
    instance_type='ml.m5.large',
    volume_size_in_gb=20
)

monitor.create_monitoring_schedule(
    monitor_schedule_name='delivery-model-monitor',
    endpoint_input=predictor.endpoint_name,
    output_s3_uri=f's3://{bucket}/{prefix}/monitoring-output',
    schedule_cron_expression='cron(0 * ? * * *)'  # Hourly
)

print("✅ Model monitoring schedule created")
```

---

## 6. Cost Optimization

### 6.1 Instance Selection Guide

| Use Case | Recommended Instance | Hourly Cost | Notes |
|----------|---------------------|-------------|-------|
| Development/Testing | ml.t3.medium | $0.05 | Burstable, cost-effective |
| Small Production | ml.m5.large | $0.12 | Balanced compute |
| High Throughput | ml.c5.xlarge | $0.20 | CPU optimized |
| Deep Learning | ml.p3.2xlarge | $3.82 | GPU for training |
| Inference at Scale | ml.inf1.xlarge | $0.30 | Inferentia chip |

### 6.2 Auto-Scaling Configuration

```python
# autoscaling.py
import boto3

asg = boto3.client('application-autoscaling')

# Register scalable target
asg.register_scalable_target(
    ServiceNamespace='sagemaker',
    ResourceId=f'endpoint/{predictor.endpoint_name}/variant/AllTraffic',
    ScalableDimension='sagemaker:variant:DesiredInstanceCount',
    MinCapacity=1,
    MaxCapacity=10
)

# Create scaling policy
asg.put_scaling_policy(
    PolicyName='delivery-endpoint-scaling',
    ServiceNamespace='sagemaker',
    ResourceId=f'endpoint/{predictor.endpoint_name}/variant/AllTraffic',
    ScalableDimension='sagemaker:variant:DesiredInstanceCount',
    PolicyType='TargetTrackingScaling',
    TargetTrackingScalingPolicyConfiguration={
        'TargetValue': 1000,  # Target invocations per instance per minute
        'PredefinedMetricSpecification': {
            'PredefinedMetricType': 'SageMakerVariantInvocationsPerInstance'
        },
        'ScaleInCooldown': 300,
        'ScaleOutCooldown': 60
    }
)

print("✅ Auto-scaling configured")
```

### 6.3 Cleanup Script

```python
# cleanup.py
import boto3

def cleanup_resources():
    """Clean up AWS resources to avoid charges"""
    
    sm = boto3.client('sagemaker')
    
    # Delete endpoint
    try:
        sm.delete_endpoint(EndpointName='delivery-prediction-endpoint')
        print("✅ Endpoint deleted")
    except: pass
    
    # Delete endpoint config
    try:
        sm.delete_endpoint_config(EndpointConfigName='delivery-prediction-endpoint')
        print("✅ Endpoint config deleted")
    except: pass
    
    # Delete model
    try:
        sm.delete_model(ModelName='xgboost-delivery-model')
        print("✅ Model deleted")
    except: pass

if __name__ == '__main__':
    cleanup_resources()
```

---

## Quick Reference

### Common Commands

```bash
# List SageMaker endpoints
aws sagemaker list-endpoints

# Describe endpoint
aws sagemaker describe-endpoint --endpoint-name delivery-prediction-endpoint

# List Bedrock models
aws bedrock list-foundation-models

# Check training job status
aws sagemaker describe-training-job --training-job-name <job-name>
```

### Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| AccessDeniedException | Missing IAM permissions | Add required permissions to role |
| ResourceLimitExceeded | Account limits | Request limit increase via AWS Support |
| ModelError 500 | Serialization issue | Check input data format |
| Endpoint timeout | Instance too small | Scale up or enable auto-scaling |
| Bedrock throttling | Rate limits | Implement exponential backoff |

---

## 7. Reusable Templates

> **🔄 This section contains fully reusable code templates that work with ANY dataset.**
> **Simply update the configuration file and the code adapts automatically.**

### 7.1 Configuration File

Create this configuration file to define your project settings:

```yaml
# config/aws_config.yaml
# ═══════════════════════════════════════════════════════════════════════════════
# 🔧 CHANGE THESE VALUES FOR YOUR PROJECT
# ═══════════════════════════════════════════════════════════════════════════════

project:
  name: "my-ml-project"              # ← CHANGE: Your project name
  prefix: "my-company"               # ← CHANGE: S3 prefix for your organization
  region: "us-east-1"                # ← CHANGE: Your AWS region

data:
  # ═══════════════════════════════════════════════════════════════════════════
  # 📊 DEFINE YOUR DATA SCHEMA HERE
  # ═══════════════════════════════════════════════════════════════════════════
  source_file: "data/your_data.csv"  # ← CHANGE: Path to your data file
  target_column: "target"            # ← CHANGE: Column you want to predict
  
  # Feature columns to use for training
  feature_columns:                   # ← CHANGE: List your feature columns
    - "feature_1"
    - "feature_2"
    - "feature_3"
    - "feature_4"
  
  # Optional: Columns that need datetime parsing
  datetime_columns:                  # ← CHANGE: Columns to parse as datetime
    - "timestamp_column"
  
  # Optional: Columns to create from datetime
  datetime_features:                 # ← CHANGE: Features to extract from datetime
    hour_column: "timestamp_column"  # Creates 'hour' feature
    dayofweek_column: "timestamp_column"  # Creates 'day_of_week' feature

model:
  # ═══════════════════════════════════════════════════════════════════════════
  # 🤖 MODEL CONFIGURATION
  # ═══════════════════════════════════════════════════════════════════════════
  type: "xgboost"                    # Options: xgboost, linear-learner, sklearn
  task: "regression"                 # Options: regression, classification
  
  hyperparameters:                   # ← CHANGE: Adjust for your use case
    num_round: 100
    max_depth: 6
    eta: 0.3
    subsample: 0.8
    objective: "reg:squarederror"    # Use "binary:logistic" for classification

training:
  instance_type: "ml.m5.xlarge"      # ← CHANGE: Based on data size
  instance_count: 1
  test_split: 0.2

deployment:
  instance_type: "ml.m5.large"       # ← CHANGE: Based on expected traffic
  initial_instance_count: 1
  endpoint_name: "my-prediction-endpoint"  # ← CHANGE: Your endpoint name

bedrock:
  model_id: "anthropic.claude-3-sonnet-20240229-v1:0"
  max_tokens: 1024
  system_prompt: "You are a helpful assistant."  # ← CHANGE: Your system prompt
```

### 7.2 Reusable Data Preparation Module

```python
# src/aws/data_utils.py
"""
🔄 REUSABLE DATA PREPARATION FOR AWS SAGEMAKER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Works with ANY dataset - just update config.yaml
"""

import yaml
import pandas as pd
import boto3
from sagemaker import Session
from pathlib import Path


def load_config(config_path: str = "config/aws_config.yaml") -> dict:
    """Load configuration from YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def prepare_features(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    """
    Prepare features based on configuration.
    
    🔧 WHAT THIS DOES:
    - Parses datetime columns specified in config
    - Creates datetime-derived features (hour, day_of_week)
    - Selects only the columns specified in config
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


def upload_to_s3(
    df: pd.DataFrame,
    config: dict,
    dataset_type: str = "train"
) -> str:
    """
    Upload dataframe to S3 in SageMaker-compatible format.
    
    🔧 WHAT THIS DOES:
    - Reorders columns (target first for XGBoost)
    - Uploads to S3 bucket
    - Returns S3 path
    """
    session = Session()
    bucket = session.default_bucket()
    prefix = f"{config['project']['prefix']}/{config['project']['name']}"
    
    # Get columns from config
    target_col = config['data']['target_column']
    feature_cols = config['data']['feature_columns']
    
    # Add datetime-derived features if they exist
    if 'hour' in df.columns:
        feature_cols = ['hour'] + [c for c in feature_cols if c != 'hour']
    if 'day_of_week' in df.columns:
        feature_cols = ['day_of_week'] + [c for c in feature_cols if c != 'day_of_week']
    
    # Reorder: target first (required for XGBoost)
    columns_order = [target_col] + feature_cols
    df_ordered = df[columns_order]
    
    # Save and upload
    local_path = f"/tmp/{dataset_type}.csv"
    df_ordered.to_csv(local_path, index=False, header=False)
    
    s3_path = session.upload_data(
        local_path, 
        bucket=bucket, 
        key_prefix=f"{prefix}/{dataset_type}"
    )
    
    print(f"✅ Uploaded {dataset_type} data to: {s3_path}")
    return s3_path


def prepare_and_upload(config_path: str = "config/aws_config.yaml"):
    """
    Main function to prepare and upload data.
    
    🔧 USAGE:
        python -m src.aws.data_utils
        
    Or in code:
        from src.aws.data_utils import prepare_and_upload
        train_path, test_path = prepare_and_upload("config/aws_config.yaml")
    """
    from sklearn.model_selection import train_test_split
    
    # Load config
    config = load_config(config_path)
    print(f"📋 Project: {config['project']['name']}")
    print(f"📊 Target column: {config['data']['target_column']}")
    print(f"📊 Feature columns: {config['data']['feature_columns']}")
    
    # Load data
    df = pd.read_csv(config['data']['source_file'])
    print(f"📂 Loaded {len(df)} rows from {config['data']['source_file']}")
    
    # Prepare features
    df = prepare_features(df, config)
    
    # Split data
    test_size = config['training'].get('test_split', 0.2)
    train_df, test_df = train_test_split(df, test_size=test_size, random_state=42)
    print(f"📊 Train: {len(train_df)} rows, Test: {len(test_df)} rows")
    
    # Upload to S3
    train_path = upload_to_s3(train_df, config, "train")
    test_path = upload_to_s3(test_df, config, "test")
    
    return train_path, test_path


if __name__ == "__main__":
    prepare_and_upload()
```

### 7.3 Reusable Training Module

```python
# src/aws/train.py
"""
🔄 REUSABLE SAGEMAKER TRAINING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Works with ANY dataset - just update config.yaml
"""

import sagemaker
from sagemaker import image_uris
from sagemaker.inputs import TrainingInput
from sagemaker.tuner import HyperparameterTuner, ContinuousParameter, IntegerParameter

from .data_utils import load_config


def get_estimator(config: dict, role: str):
    """
    Create SageMaker estimator based on configuration.
    
    🔧 WHAT CHANGES:
    - Model type (xgboost, linear-learner, etc.)
    - Hyperparameters
    - Instance type and count
    """
    session = sagemaker.Session()
    bucket = session.default_bucket()
    prefix = f"{config['project']['prefix']}/{config['project']['name']}"
    
    # Get container image
    container = image_uris.retrieve(
        framework=config['model']['type'],
        region=config['project']['region'],
        version='1.5-1' if config['model']['type'] == 'xgboost' else 'latest'
    )
    
    # Create estimator
    estimator = sagemaker.estimator.Estimator(
        image_uri=container,
        role=role,
        instance_count=config['training']['instance_count'],
        instance_type=config['training']['instance_type'],
        output_path=f's3://{bucket}/{prefix}/output',
        sagemaker_session=session,
        hyperparameters=config['model']['hyperparameters']
    )
    
    return estimator


def train_model(
    train_path: str,
    test_path: str,
    config_path: str = "config/aws_config.yaml",
    role: str = None
):
    """
    Train model using SageMaker.
    
    🔧 USAGE:
        from src.aws.train import train_model
        estimator = train_model(train_path, test_path, "config/aws_config.yaml")
    """
    config = load_config(config_path)
    
    if role is None:
        role = sagemaker.get_execution_role()
    
    print(f"🚀 Starting training for: {config['project']['name']}")
    print(f"📦 Model type: {config['model']['type']}")
    print(f"🎯 Task: {config['model']['task']}")
    
    # Create estimator
    estimator = get_estimator(config, role)
    
    # Define inputs
    train_input = TrainingInput(s3_data=train_path, content_type='text/csv')
    test_input = TrainingInput(s3_data=test_path, content_type='text/csv')
    
    # Train
    estimator.fit({
        'train': train_input,
        'validation': test_input
    }, wait=True)
    
    print(f"✅ Model trained: {estimator.model_data}")
    return estimator


def hyperparameter_tuning(
    train_path: str,
    test_path: str,
    config_path: str = "config/aws_config.yaml",
    role: str = None,
    max_jobs: int = 20,
    max_parallel_jobs: int = 4
):
    """
    Run hyperparameter tuning.
    
    🔧 WHAT THIS DOES:
    - Automatically tunes hyperparameters
    - Uses Bayesian optimization
    - Returns best model
    """
    config = load_config(config_path)
    
    if role is None:
        role = sagemaker.get_execution_role()
    
    estimator = get_estimator(config, role)
    
    # Define search space based on model type
    if config['model']['type'] == 'xgboost':
        hyperparameter_ranges = {
            'eta': ContinuousParameter(0.01, 0.3),
            'max_depth': IntegerParameter(3, 10),
            'subsample': ContinuousParameter(0.5, 1.0),
            'num_round': IntegerParameter(50, 200)
        }
        objective_metric = 'validation:rmse' if config['model']['task'] == 'regression' else 'validation:error'
    else:
        hyperparameter_ranges = {}
        objective_metric = 'validation:objective_loss'
    
    # Create tuner
    tuner = HyperparameterTuner(
        estimator=estimator,
        objective_metric_name=objective_metric,
        objective_type='Minimize',
        hyperparameter_ranges=hyperparameter_ranges,
        max_jobs=max_jobs,
        max_parallel_jobs=max_parallel_jobs,
        strategy='Bayesian'
    )
    
    # Define inputs
    train_input = TrainingInput(s3_data=train_path, content_type='text/csv')
    test_input = TrainingInput(s3_data=test_path, content_type='text/csv')
    
    print(f"🔧 Starting hyperparameter tuning: {max_jobs} jobs")
    tuner.fit({'train': train_input, 'validation': test_input}, wait=False)
    
    print(f"📊 Tuning job: {tuner.latest_tuning_job.name}")
    return tuner


if __name__ == "__main__":
    from .data_utils import prepare_and_upload
    train_path, test_path = prepare_and_upload()
    train_model(train_path, test_path)
```

### 7.4 Reusable Deployment Module

```python
# src/aws/deploy.py
"""
🔄 REUSABLE SAGEMAKER DEPLOYMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Works with ANY model - just update config.yaml
"""

from sagemaker.serializers import CSVSerializer
from sagemaker.deserializers import JSONDeserializer

from .data_utils import load_config


def deploy_model(
    estimator,
    config_path: str = "config/aws_config.yaml"
):
    """
    Deploy trained model to endpoint.
    
    🔧 USAGE:
        from src.aws.deploy import deploy_model
        predictor = deploy_model(estimator, "config/aws_config.yaml")
    """
    config = load_config(config_path)
    
    print(f"🚀 Deploying to endpoint: {config['deployment']['endpoint_name']}")
    
    predictor = estimator.deploy(
        initial_instance_count=config['deployment']['initial_instance_count'],
        instance_type=config['deployment']['instance_type'],
        endpoint_name=config['deployment']['endpoint_name'],
        serializer=CSVSerializer(),
        deserializer=JSONDeserializer()
    )
    
    print(f"✅ Endpoint created: {predictor.endpoint_name}")
    return predictor


def predict(predictor, features: list):
    """
    Make prediction using deployed model.
    
    🔧 USAGE:
        prediction = predict(predictor, [1.2, 3.4, 5.6, 7.8])
    
    Args:
        predictor: SageMaker predictor object
        features: List of feature values in same order as config
    """
    # Convert to CSV format
    payload = ','.join(map(str, features))
    result = predictor.predict(payload)
    return result


def batch_predict(
    input_s3_path: str,
    output_s3_path: str,
    estimator,
    config_path: str = "config/aws_config.yaml"
):
    """
    Run batch predictions on large datasets.
    
    🔧 USAGE:
        batch_predict(
            "s3://bucket/input/",
            "s3://bucket/output/",
            estimator
        )
    """
    config = load_config(config_path)
    
    transformer = estimator.transformer(
        instance_count=1,
        instance_type=config['deployment']['instance_type'],
        output_path=output_s3_path
    )
    
    print(f"📊 Starting batch transform...")
    transformer.transform(
        data=input_s3_path,
        content_type='text/csv',
        split_type='Line'
    )
    transformer.wait()
    
    print(f"✅ Predictions saved to: {output_s3_path}")
    return transformer


def cleanup(endpoint_name: str = None, config_path: str = "config/aws_config.yaml"):
    """
    Clean up AWS resources.
    
    🔧 USAGE:
        cleanup()  # Uses endpoint name from config
        cleanup("my-custom-endpoint")
    """
    import boto3
    
    config = load_config(config_path)
    endpoint = endpoint_name or config['deployment']['endpoint_name']
    
    sm = boto3.client('sagemaker')
    
    try:
        sm.delete_endpoint(EndpointName=endpoint)
        print(f"✅ Deleted endpoint: {endpoint}")
    except Exception as e:
        print(f"⚠️ {e}")
    
    try:
        sm.delete_endpoint_config(EndpointConfigName=endpoint)
        print(f"✅ Deleted endpoint config: {endpoint}")
    except Exception as e:
        print(f"⚠️ {e}")
```

### 7.5 Reusable Bedrock Module

```python
# src/aws/bedrock_utils.py
"""
🔄 REUSABLE BEDROCK UTILITIES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Works with ANY use case - just update config.yaml
"""

import boto3
import json
import numpy as np
from typing import List, Dict, Any

from .data_utils import load_config


class BedrockClient:
    """
    Reusable Bedrock client for text generation and embeddings.
    
    🔧 USAGE:
        client = BedrockClient("config/aws_config.yaml")
        response = client.generate("What is machine learning?")
        embeddings = client.get_embeddings(["text1", "text2"])
    """
    
    def __init__(self, config_path: str = "config/aws_config.yaml"):
        self.config = load_config(config_path)
        self.bedrock = boto3.client(
            'bedrock-runtime',
            region_name=self.config['project']['region']
        )
        self.bedrock_agent = boto3.client(
            'bedrock-agent-runtime',
            region_name=self.config['project']['region']
        )
    
    def generate(
        self,
        prompt: str,
        system_prompt: str = None,
        max_tokens: int = None,
        temperature: float = 0.7
    ) -> str:
        """
        Generate text using Claude.
        
        🔧 WHAT CHANGES:
        - model_id in config
        - system_prompt in config or parameter
        - max_tokens in config or parameter
        """
        model_id = self.config['bedrock']['model_id']
        max_tokens = max_tokens or self.config['bedrock']['max_tokens']
        system_prompt = system_prompt or self.config['bedrock'].get('system_prompt', '')
        
        messages = [{"role": "user", "content": prompt}]
        
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "messages": messages,
            "temperature": temperature
        }
        
        if system_prompt:
            body["system"] = system_prompt
        
        response = self.bedrock.invoke_model(
            modelId=model_id,
            body=json.dumps(body),
            contentType='application/json'
        )
        
        result = json.loads(response['body'].read())
        return result['content'][0]['text']
    
    def get_embeddings(
        self,
        texts: List[str],
        model_id: str = "amazon.titan-embed-text-v1"
    ) -> List[List[float]]:
        """
        Get embeddings for a list of texts.
        
        🔧 USAGE:
            embeddings = client.get_embeddings(["text1", "text2"])
        """
        embeddings = []
        
        for text in texts:
            response = self.bedrock.invoke_model(
                modelId=model_id,
                body=json.dumps({"inputText": text}),
                contentType='application/json'
            )
            result = json.loads(response['body'].read())
            embeddings.append(result['embedding'])
        
        return embeddings
    
    def semantic_search(
        self,
        query: str,
        documents: List[str],
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Search documents by semantic similarity.
        
        🔧 USAGE:
            results = client.semantic_search(
                "my query",
                ["doc1", "doc2", "doc3"],
                top_k=2
            )
        """
        # Get embeddings
        query_embedding = self.get_embeddings([query])[0]
        doc_embeddings = self.get_embeddings(documents)
        
        # Calculate similarities
        similarities = []
        for i, doc_emb in enumerate(doc_embeddings):
            similarity = np.dot(query_embedding, doc_emb) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(doc_emb)
            )
            similarities.append({
                'document': documents[i],
                'score': float(similarity),
                'index': i
            })
        
        # Sort by similarity
        similarities.sort(key=lambda x: x['score'], reverse=True)
        return similarities[:top_k]
    
    def query_knowledge_base(
        self,
        question: str,
        knowledge_base_id: str
    ) -> str:
        """
        Query a Bedrock Knowledge Base (RAG).
        
        🔧 USAGE:
            answer = client.query_knowledge_base(
                "What is the refund policy?",
                "your-kb-id"
            )
        """
        response = self.bedrock_agent.retrieve_and_generate(
            input={"text": question},
            retrieveAndGenerateConfiguration={
                "type": "KNOWLEDGE_BASE",
                "knowledgeBaseConfiguration": {
                    "knowledgeBaseId": knowledge_base_id,
                    "modelArn": f"arn:aws:bedrock:{self.config['project']['region']}::foundation-model/{self.config['bedrock']['model_id']}"
                }
            }
        )
        
        return response["output"]["text"]


# Convenience functions
def generate(prompt: str, config_path: str = "config/aws_config.yaml") -> str:
    """Quick function for text generation."""
    client = BedrockClient(config_path)
    return client.generate(prompt)


def search(query: str, documents: List[str], config_path: str = "config/aws_config.yaml") -> List[Dict]:
    """Quick function for semantic search."""
    client = BedrockClient(config_path)
    return client.semantic_search(query, documents)
```

### 7.6 Complete Pipeline Example

```python
# run_aws_pipeline.py
"""
🔄 COMPLETE AWS ML PIPELINE
━━━━━━━━━━━━━━━━━━━━━━━━━━━
Run the entire pipeline with one command!

🔧 USAGE:
    python run_aws_pipeline.py --config config/aws_config.yaml
    python run_aws_pipeline.py --config config/aws_config.yaml --tune
"""

import argparse
from src.aws.data_utils import prepare_and_upload, load_config
from src.aws.train import train_model, hyperparameter_tuning
from src.aws.deploy import deploy_model, predict


def main():
    parser = argparse.ArgumentParser(description="AWS ML Pipeline")
    parser.add_argument("--config", default="config/aws_config.yaml", help="Path to config file")
    parser.add_argument("--tune", action="store_true", help="Run hyperparameter tuning")
    parser.add_argument("--skip-train", action="store_true", help="Skip training, only deploy")
    parser.add_argument("--test", action="store_true", help="Test the endpoint after deployment")
    args = parser.parse_args()
    
    config = load_config(args.config)
    print("=" * 60)
    print(f"🚀 AWS ML Pipeline: {config['project']['name']}")
    print("=" * 60)
    
    # Step 1: Prepare and upload data
    print("\n📊 Step 1: Preparing and uploading data...")
    train_path, test_path = prepare_and_upload(args.config)
    
    # Step 2: Train model
    if not args.skip_train:
        if args.tune:
            print("\n🔧 Step 2: Running hyperparameter tuning...")
            tuner = hyperparameter_tuning(train_path, test_path, args.config)
            print(f"⏳ Tuning job started. Monitor in SageMaker console.")
            print(f"   Run 'aws sagemaker describe-hyper-parameter-tuning-job --hyper-parameter-tuning-job-name {tuner.latest_tuning_job.name}'")
            return
        else:
            print("\n🚀 Step 2: Training model...")
            estimator = train_model(train_path, test_path, args.config)
    
    # Step 3: Deploy model
    print("\n🌐 Step 3: Deploying model...")
    predictor = deploy_model(estimator, args.config)
    
    # Step 4: Test endpoint
    if args.test:
        print("\n🧪 Step 4: Testing endpoint...")
        # Create sample features based on config
        num_features = len(config['data']['feature_columns'])
        sample_features = [1.0] * num_features  # Placeholder values
        result = predict(predictor, sample_features)
        print(f"📦 Test prediction: {result}")
    
    print("\n" + "=" * 60)
    print("✅ Pipeline complete!")
    print(f"🌐 Endpoint: {config['deployment']['endpoint_name']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
```

### 7.7 What to Change Summary

| Component | What to Change | Where to Change |
|-----------|----------------|-----------------|
| **Project name** | `project.name`, `project.prefix` | `config/aws_config.yaml` |
| **AWS region** | `project.region` | `config/aws_config.yaml` |
| **Data file** | `data.source_file` | `config/aws_config.yaml` |
| **Target column** | `data.target_column` | `config/aws_config.yaml` |
| **Feature columns** | `data.feature_columns` | `config/aws_config.yaml` |
| **Datetime parsing** | `data.datetime_columns` | `config/aws_config.yaml` |
| **Model type** | `model.type` | `config/aws_config.yaml` |
| **Task type** | `model.task` | `config/aws_config.yaml` |
| **Hyperparameters** | `model.hyperparameters` | `config/aws_config.yaml` |
| **Instance types** | `training.instance_type`, `deployment.instance_type` | `config/aws_config.yaml` |
| **LLM model** | `bedrock.model_id` | `config/aws_config.yaml` |
| **System prompt** | `bedrock.system_prompt` | `config/aws_config.yaml` |

---

## Next Steps

1. ✅ **AWS Setup Complete** - SageMaker and Bedrock configured
2. 📋 **Azure Implementation** - See `AZURE_IMPLEMENTATION.md`
3. 📋 **GCP Implementation** - See `GCP_IMPLEMENTATION.md`

---

*Last Updated: January 2024*
*Author: Penske Logistics Analytics Team*
