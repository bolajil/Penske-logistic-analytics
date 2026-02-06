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

## Next Steps

1. ✅ **AWS Setup Complete** - SageMaker and Bedrock configured
2. 📋 **Azure Implementation** - See `AZURE_IMPLEMENTATION.md`
3. 📋 **GCP Implementation** - See `GCP_IMPLEMENTATION.md`

---

*Last Updated: January 2024*
*Author: Penske Logistics Analytics Team*
