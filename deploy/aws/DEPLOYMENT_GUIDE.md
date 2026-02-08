# AWS Deployment Guide

Complete step-by-step guide for deploying Penske Logistics Analytics to AWS using ECS Fargate.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Architecture Overview](#2-architecture-overview)
3. [Step 1: AWS Account Setup](#step-1-aws-account-setup)
4. [Step 2: Create ECR Repository](#step-2-create-ecr-repository)
5. [Step 3: Build and Push Docker Image](#step-3-build-and-push-docker-image)
6. [Step 4: Deploy Infrastructure](#step-4-deploy-infrastructure-cloudformation)
7. [Step 5: Configure Secrets](#step-5-configure-secrets)
8. [Step 6: Verify Deployment](#step-6-verify-deployment)
9. [Step 7: Set Up CI/CD](#step-7-set-up-cicd-optional)
10. [Amazon Bedrock Integration](#amazon-bedrock-integration)
11. [Amazon SageMaker Integration](#amazon-sagemaker-integration)
12. [Troubleshooting](#troubleshooting)
13. [Cost Optimization](#cost-optimization)

---

## 1. Prerequisites

### Required Tools

```bash
# Verify AWS CLI is installed
aws --version
# Expected: aws-cli/2.x.x

# Verify Docker is installed
docker --version
# Expected: Docker version 20.10+

# Configure AWS credentials
aws configure
# Enter: Access Key, Secret Key, Region (us-east-1), Output (json)
```

### Required AWS Permissions

Your IAM user/role needs these permissions:
- `AmazonECS_FullAccess`
- `AmazonEC2ContainerRegistryFullAccess`
- `AmazonVPCFullAccess`
- `ElasticLoadBalancingFullAccess`
- `CloudWatchLogsFullAccess`
- `IAMFullAccess` (for creating roles)
- `SecretsManagerReadWrite`
- `AmazonBedrockFullAccess` (for Bedrock)
- `AmazonSageMakerFullAccess` (for SageMaker)

---

## 2. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                            AWS Region                               │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │                         VPC (10.0.0.0/16)                     │ │
│  │  ┌─────────────────────┐  ┌─────────────────────┐            │ │
│  │  │  Public Subnet 1    │  │  Public Subnet 2    │            │ │
│  │  │    (10.0.1.0/24)    │  │    (10.0.2.0/24)    │            │ │
│  │  │  ┌───────────────┐  │  │  ┌───────────────┐  │            │ │
│  │  │  │  ECS Task     │  │  │  │  ECS Task     │  │            │ │
│  │  │  │  (Fargate)    │  │  │  │  (Fargate)    │  │            │ │
│  │  │  └───────────────┘  │  │  └───────────────┘  │            │ │
│  │  └──────────┬──────────┘  └──────────┬──────────┘            │ │
│  │             └──────────────┬─────────┘                        │ │
│  │                            │                                  │ │
│  │                 ┌──────────┴──────────┐                       │ │
│  │                 │  Application Load   │                       │ │
│  │                 │     Balancer        │                       │ │
│  │                 └──────────┬──────────┘                       │ │
│  └────────────────────────────┼──────────────────────────────────┘ │
│                               │                                     │
│                    ┌──────────┴──────────┐                         │
│                    │  Internet Gateway   │                         │
│                    └──────────┬──────────┘                         │
└───────────────────────────────┼─────────────────────────────────────┘
                                │
                           INTERNET
```

### Components Created

| Component | Description | Quantity |
|-----------|-------------|----------|
| VPC | Virtual Private Cloud | 1 |
| Subnets | Public subnets in 2 AZs | 2 |
| ALB | Application Load Balancer | 1 |
| ECS Cluster | Fargate cluster | 1 |
| ECS Service | Auto-scaling service | 1 |
| ECS Tasks | Container instances | 2-10 |
| Security Groups | Firewall rules | 2 |
| IAM Roles | Execution & task roles | 2 |
| CloudWatch | Logs & monitoring | 1 |

---

## Step 1: AWS Account Setup

### 1.1 Set Environment Variables

```bash
# Set your AWS region
export AWS_REGION=us-east-1
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Verify
echo "Account: $AWS_ACCOUNT_ID"
echo "Region: $AWS_REGION"
```

### 1.2 Create S3 Bucket for Data (Optional)

```bash
aws s3 mb s3://penske-analytics-data-${AWS_ACCOUNT_ID} --region $AWS_REGION
```

---

## Step 2: Create ECR Repository

### 2.1 Create the Repository

```bash
# Create ECR repository
aws ecr create-repository \
    --repository-name penske-logistics-analytics \
    --image-scanning-configuration scanOnPush=true \
    --region $AWS_REGION

# Get repository URI
export ECR_REPO=$(aws ecr describe-repositories \
    --repository-names penske-logistics-analytics \
    --query 'repositories[0].repositoryUri' \
    --output text)

echo "ECR Repository: $ECR_REPO"
```

### 2.2 Login to ECR

```bash
aws ecr get-login-password --region $AWS_REGION | \
    docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
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

### 3.2 Tag and Push

```bash
# Tag for ECR
docker tag penske-logistics-analytics:latest $ECR_REPO:latest
docker tag penske-logistics-analytics:latest $ECR_REPO:v1.0.0

# Push to ECR
docker push $ECR_REPO:latest
docker push $ECR_REPO:v1.0.0
```

### 3.3 Verify Image in ECR

```bash
aws ecr describe-images \
    --repository-name penske-logistics-analytics \
    --query 'imageDetails[*].[imageTags,imagePushedAt]' \
    --output table
```

---

## Step 4: Deploy Infrastructure (CloudFormation)

### 4.1 Deploy the Stack

```bash
# Navigate to AWS deploy directory
cd deploy/aws

# Deploy CloudFormation stack
aws cloudformation create-stack \
    --stack-name penske-analytics-prod \
    --template-body file://cloudformation.yaml \
    --parameters \
        ParameterKey=Environment,ParameterValue=prod \
        ParameterKey=ContainerImage,ParameterValue=$ECR_REPO:latest \
    --capabilities CAPABILITY_IAM \
    --region $AWS_REGION
```

### 4.2 Monitor Stack Creation

```bash
# Watch stack events (takes 5-10 minutes)
aws cloudformation describe-stack-events \
    --stack-name penske-analytics-prod \
    --query 'StackEvents[*].[Timestamp,ResourceStatus,ResourceType,LogicalResourceId]' \
    --output table

# Or wait for completion
aws cloudformation wait stack-create-complete \
    --stack-name penske-analytics-prod
```

### 4.3 Get Stack Outputs

```bash
# Get all outputs
aws cloudformation describe-stacks \
    --stack-name penske-analytics-prod \
    --query 'Stacks[0].Outputs' \
    --output table
```

**Expected Outputs:**

| Output Key | Description | Example Value |
|------------|-------------|---------------|
| LoadBalancerDNS | ALB DNS name | `penske-alb-prod-123456.us-east-1.elb.amazonaws.com` |
| APIEndpoint | API URL | `http://penske-alb-prod-123456.../api/v1` |
| DashboardEndpoint | Dashboard URL | `http://penske-alb-prod-123456...` |

---

## Step 5: Configure Secrets

### 5.1 Store OpenAI API Key

```bash
# Create secret in Secrets Manager
aws secretsmanager create-secret \
    --name penske/openai-api-key \
    --secret-string '{"OPENAI_API_KEY":"sk-your-actual-key-here"}' \
    --region $AWS_REGION
```

### 5.2 Update ECS Task to Use Secrets

The CloudFormation template is pre-configured to access secrets. Verify:

```bash
aws ecs describe-task-definition \
    --task-definition penske-analytics-prod \
    --query 'taskDefinition.containerDefinitions[0].secrets'
```

---

## Step 6: Verify Deployment

### 6.1 Check ECS Service Status

```bash
# Get service status
aws ecs describe-services \
    --cluster penske-analytics-prod \
    --services penske-analytics-service-prod \
    --query 'services[0].[status,runningCount,desiredCount]' \
    --output table
```

**Expected:** `ACTIVE | 2 | 2`

### 6.2 Check Task Health

```bash
# List running tasks
aws ecs list-tasks \
    --cluster penske-analytics-prod \
    --service-name penske-analytics-service-prod

# Get task details
aws ecs describe-tasks \
    --cluster penske-analytics-prod \
    --tasks $(aws ecs list-tasks --cluster penske-analytics-prod --query 'taskArns[0]' --output text)
```

### 6.3 Test Endpoints

```bash
# Get Load Balancer DNS
export ALB_DNS=$(aws cloudformation describe-stacks \
    --stack-name penske-analytics-prod \
    --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerDNS`].OutputValue' \
    --output text)

# Test API health
curl http://$ALB_DNS/

# Test Dashboard (should return HTML)
curl -I http://$ALB_DNS/
```

### 6.4 View Application Logs

```bash
# View recent logs
aws logs tail /ecs/penske-logistics-analytics-prod --follow
```

---

## Step 7: Set Up CI/CD (Optional)

### 7.1 Create CodeBuild Project

The `buildspec.yml` file is already configured. Create the CodeBuild project:

```bash
aws codebuild create-project \
    --name penske-analytics-build \
    --source type=GITHUB,location=https://github.com/your-org/penske-logistics-analytics \
    --artifacts type=NO_ARTIFACTS \
    --environment type=LINUX_CONTAINER,computeType=BUILD_GENERAL1_SMALL,image=aws/codebuild/standard:5.0,privilegedMode=true \
    --service-role arn:aws:iam::$AWS_ACCOUNT_ID:role/CodeBuildServiceRole
```

### 7.2 Create CodePipeline

```bash
# Create pipeline (manual via Console recommended)
# Services > CodePipeline > Create Pipeline
# Source: GitHub
# Build: CodeBuild (penske-analytics-build)
# Deploy: Amazon ECS
```

---

## Amazon Bedrock Integration

Amazon Bedrock provides access to foundation models (FMs) for generative AI capabilities in your logistics analytics application.

### Enable Bedrock Access

```bash
# Enable Bedrock in your region
aws bedrock list-foundation-models --region $AWS_REGION

# Request model access (if needed)
# Go to: AWS Console > Bedrock > Model access > Manage model access
```

### Available Models for Logistics Analytics

| Model | Use Case | Best For |
|-------|----------|----------|
| **Claude 3 (Anthropic)** | Complex reasoning | Route optimization analysis, demand forecasting |
| **Titan Text** | General text | Document summarization, report generation |
| **Titan Embeddings** | Vector search | Semantic search on logistics data |
| **Llama 2 (Meta)** | Cost-effective | High-volume text processing |

### Bedrock API Integration

```python
# src/services/bedrock_service.py
import boto3
import json

class BedrockService:
    def __init__(self, region='us-east-1'):
        self.client = boto3.client('bedrock-runtime', region_name=region)
    
    def analyze_logistics_data(self, prompt: str, model_id: str = 'anthropic.claude-3-sonnet-20240229-v1:0'):
        """Analyze logistics data using Bedrock foundation models."""
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4096,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        })
        
        response = self.client.invoke_model(
            modelId=model_id,
            body=body,
            contentType='application/json',
            accept='application/json'
        )
        
        result = json.loads(response['body'].read())
        return result['content'][0]['text']
    
    def generate_embeddings(self, text: str):
        """Generate embeddings for semantic search."""
        body = json.dumps({"inputText": text})
        
        response = self.client.invoke_model(
            modelId='amazon.titan-embed-text-v1',
            body=body,
            contentType='application/json',
            accept='application/json'
        )
        
        result = json.loads(response['body'].read())
        return result['embedding']
```

### Bedrock Use Cases for Penske Analytics

```python
# Example: Route Optimization Analysis
bedrock = BedrockService()

prompt = """
Analyze this logistics route data and suggest optimizations:
- Current route: Chicago → Indianapolis → Louisville → Nashville
- Total distance: 478 miles
- Average delivery time: 8.5 hours
- Fuel consumption: 65 gallons

Consider traffic patterns, fuel efficiency, and delivery windows.
"""

analysis = bedrock.analyze_logistics_data(prompt)
print(analysis)
```

### IAM Policy for Bedrock

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream",
                "bedrock:ListFoundationModels"
            ],
            "Resource": "*"
        }
    ]
}
```

### Bedrock Costs

| Model | Input (per 1K tokens) | Output (per 1K tokens) |
|-------|----------------------|------------------------|
| Claude 3 Sonnet | $0.003 | $0.015 |
| Claude 3 Haiku | $0.00025 | $0.00125 |
| Titan Text | $0.0003 | $0.0004 |
| Titan Embeddings | $0.0001 | - |

---

## Amazon SageMaker Integration

Amazon SageMaker enables training, deploying, and managing custom ML models for logistics predictions. This section provides a complete walkthrough from data preparation to production deployment.

### What You Will Accomplish

By following this guide, you will:
1. **Prepare training data** - Format and upload logistics data to S3
2. **Train a model** - Run a training job on SageMaker managed infrastructure
3. **Deploy an endpoint** - Host your model for real-time predictions
4. **Make predictions** - Call the endpoint from your application

### SageMaker Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         SageMaker ML Pipeline                                   │
│                                                                                 │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌────────────┐ │
│  │  S3 Bucket   │ ──▶ │  Training    │ ──▶ │   Model      │ ──▶ │  Endpoint  │ │
│  │              │     │   Job        │     │  Artifacts   │     │            │ │
│  │ • train.csv  │     │              │     │              │     │ Real-time  │ │
│  │ • valid.csv  │     │ Runs your    │     │ Saved to S3: │     │ predictions│ │
│  │              │     │ train.py on  │     │ model.tar.gz │     │            │ │
│  └──────────────┘     │ ML instances │     └──────────────┘     └────────────┘ │
│                       └──────────────┘                                         │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

### Step 1: Prepare Your Training Data

**What we're doing:** Creating a properly formatted CSV dataset that SageMaker can use for training.

**Required data format:** Your training data must be a CSV file with:
- Feature columns (inputs to the model)
- A target column (what the model predicts)

#### 1.1 Create Training Data Directory

```bash
# Create local directory structure
mkdir -p data/training

# Your data should have this structure:
# data/
# └── training/
#     ├── train.csv      (80% of data - for training)
#     └── validation.csv (20% of data - for validation)
```

#### 1.2 Training Data Format Example

**File: `data/training/train.csv`**
```csv
date,region,shipment_volume,fuel_price,weather_severity,day_of_week,target
2024-01-01,Northeast,1250,3.45,0,1,1320
2024-01-02,Northeast,1180,3.42,1,2,1205
2024-01-03,Midwest,980,3.38,0,3,1050
2024-01-04,Southeast,1450,3.40,2,4,1380
...
```

| Column | Description | Type |
|--------|-------------|------|
| `date` | Record date | datetime |
| `region` | Geographic region | categorical |
| `shipment_volume` | Historical shipment count | numeric |
| `fuel_price` | Fuel cost per gallon | numeric |
| `weather_severity` | 0=none, 1=minor, 2=severe | numeric |
| `day_of_week` | 1=Mon through 7=Sun | numeric |
| `target` | **What to predict** (next day volume) | numeric |

#### 1.3 Generate Sample Training Data

```python
# scripts/generate_training_data.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_logistics_training_data(num_samples=10000):
    """Generate sample training data for demand forecasting."""
    
    np.random.seed(42)
    
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
    
    # Create target (next day's shipment volume with some logic)
    df['target'] = (
        df['shipment_volume'] * 0.7 + 
        df['previous_day_volume'] * 0.2 +
        np.where(df['weather_severity'] == 2, -100, 0) +
        np.where(df['day_of_week'].isin([6, 7]), -150, 50) +
        np.random.normal(0, 50, num_samples)
    ).astype(int)
    
    # Encode categorical variables
    df = pd.get_dummies(df, columns=['region'], drop_first=True)
    df = df.drop('date', axis=1)  # Remove date for training
    
    # Split into train/validation
    train_size = int(len(df) * 0.8)
    train_df = df[:train_size]
    valid_df = df[train_size:]
    
    # Save to CSV
    train_df.to_csv('data/training/train.csv', index=False)
    valid_df.to_csv('data/training/validation.csv', index=False)
    
    print(f"Training data: {len(train_df)} rows saved to data/training/train.csv")
    print(f"Validation data: {len(valid_df)} rows saved to data/training/validation.csv")
    print(f"Features: {list(train_df.columns)}")
    
    return train_df, valid_df

if __name__ == '__main__':
    generate_logistics_training_data()
```

**Run the script:**
```bash
python scripts/generate_training_data.py
```

**Expected Output:**
```
Training data: 8000 rows saved to data/training/train.csv
Validation data: 2000 rows saved to data/training/validation.csv
Features: ['shipment_volume', 'fuel_price', 'weather_severity', 'day_of_week', 
           'is_holiday', 'previous_day_volume', 'region_Midwest', 'region_Northeast', 
           'region_Southeast', 'region_West', 'target']
```

---

### Step 2: Upload Data to S3

**What we're doing:** Copying training data to S3 where SageMaker can access it.

**Where the data goes:** `s3://penske-sagemaker-{ACCOUNT_ID}/training/`

```bash
# Set your AWS account ID
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
export AWS_REGION=us-east-1

# Create S3 bucket for ML data
aws s3 mb s3://penske-sagemaker-${AWS_ACCOUNT_ID} --region $AWS_REGION

# Upload training data
aws s3 cp data/training/train.csv s3://penske-sagemaker-${AWS_ACCOUNT_ID}/training/train.csv
aws s3 cp data/training/validation.csv s3://penske-sagemaker-${AWS_ACCOUNT_ID}/training/validation.csv

# Verify upload
aws s3 ls s3://penske-sagemaker-${AWS_ACCOUNT_ID}/training/
```

**Expected Output:**
```
2024-01-15 10:30:45     524288 train.csv
2024-01-15 10:30:47     131072 validation.csv
```

---

### Step 3: Create SageMaker Execution Role

**What we're doing:** Creating an IAM role that gives SageMaker permission to:
- Read training data from S3
- Write model artifacts to S3
- Create and manage training jobs
- Deploy endpoints

```bash
# Create IAM role for SageMaker
aws iam create-role \
    --role-name PenskeSageMakerRole \
    --assume-role-policy-document '{
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"Service": "sagemaker.amazonaws.com"},
            "Action": "sts:AssumeRole"
        }]
    }'

# Attach required policies
aws iam attach-role-policy \
    --role-name PenskeSageMakerRole \
    --policy-arn arn:aws:iam::aws:policy/AmazonSageMakerFullAccess

aws iam attach-role-policy \
    --role-name PenskeSageMakerRole \
    --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess

# Get the role ARN (you'll need this later)
aws iam get-role --role-name PenskeSageMakerRole --query 'Role.Arn' --output text
```

**Expected Output:**
```
arn:aws:iam::123456789012:role/PenskeSageMakerRole
```

---

### Step 4: Create Training Script

**What we're doing:** Writing the Python script that SageMaker will execute on the training instance.

**Where this runs:** On a managed ML instance (e.g., ml.m5.xlarge) that SageMaker provisions automatically.

**Create file: `src/ml/scripts/train.py`**

```python
#!/usr/bin/env python3
"""
SageMaker Training Script for Penske Demand Forecasting

This script is executed by SageMaker on a managed training instance.
SageMaker automatically:
  - Provisions the instance
  - Downloads data from S3 to /opt/ml/input/data/
  - Runs this script
  - Uploads saved model from /opt/ml/model/ to S3
"""

import argparse
import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import json

def parse_args():
    """Parse hyperparameters passed by SageMaker."""
    parser = argparse.ArgumentParser()
    
    # Hyperparameters (passed via SageMaker)
    parser.add_argument('--n_estimators', type=int, default=100)
    parser.add_argument('--max_depth', type=int, default=10)
    parser.add_argument('--min_samples_split', type=int, default=5)
    parser.add_argument('--min_samples_leaf', type=int, default=2)
    
    # SageMaker specific paths (set automatically)
    parser.add_argument('--model-dir', type=str, default=os.environ.get('SM_MODEL_DIR', '/opt/ml/model'))
    parser.add_argument('--train', type=str, default=os.environ.get('SM_CHANNEL_TRAIN', '/opt/ml/input/data/train'))
    parser.add_argument('--validation', type=str, default=os.environ.get('SM_CHANNEL_VALIDATION', '/opt/ml/input/data/validation'))
    parser.add_argument('--output-data-dir', type=str, default=os.environ.get('SM_OUTPUT_DATA_DIR', '/opt/ml/output'))
    
    return parser.parse_args()

def load_data(train_path, validation_path):
    """Load training and validation data from S3 (via SageMaker paths)."""
    
    print(f"Loading training data from: {train_path}")
    train_files = [f for f in os.listdir(train_path) if f.endswith('.csv')]
    train_df = pd.read_csv(os.path.join(train_path, train_files[0]))
    print(f"  Training samples: {len(train_df)}")
    print(f"  Features: {list(train_df.columns)}")
    
    print(f"\nLoading validation data from: {validation_path}")
    valid_files = [f for f in os.listdir(validation_path) if f.endswith('.csv')]
    valid_df = pd.read_csv(os.path.join(validation_path, valid_files[0]))
    print(f"  Validation samples: {len(valid_df)}")
    
    return train_df, valid_df

def train_model(train_df, args):
    """Train the Random Forest model."""
    
    # Separate features and target
    X_train = train_df.drop('target', axis=1)
    y_train = train_df['target']
    
    print(f"\nTraining model with hyperparameters:")
    print(f"  n_estimators: {args.n_estimators}")
    print(f"  max_depth: {args.max_depth}")
    print(f"  min_samples_split: {args.min_samples_split}")
    print(f"  min_samples_leaf: {args.min_samples_leaf}")
    
    model = RandomForestRegressor(
        n_estimators=args.n_estimators,
        max_depth=args.max_depth,
        min_samples_split=args.min_samples_split,
        min_samples_leaf=args.min_samples_leaf,
        random_state=42,
        n_jobs=-1  # Use all CPU cores
    )
    
    model.fit(X_train, y_train)
    print("Training complete!")
    
    return model

def evaluate_model(model, valid_df):
    """Evaluate model on validation data."""
    
    X_valid = valid_df.drop('target', axis=1)
    y_valid = valid_df['target']
    
    predictions = model.predict(X_valid)
    
    metrics = {
        'mae': mean_absolute_error(y_valid, predictions),
        'rmse': np.sqrt(mean_squared_error(y_valid, predictions)),
        'r2': r2_score(y_valid, predictions)
    }
    
    print(f"\nValidation Metrics:")
    print(f"  MAE (Mean Absolute Error): {metrics['mae']:.2f}")
    print(f"  RMSE (Root Mean Square Error): {metrics['rmse']:.2f}")
    print(f"  R² Score: {metrics['r2']:.4f}")
    
    return metrics

def save_model(model, model_dir, metrics, feature_names):
    """Save model and metadata to /opt/ml/model/ (SageMaker uploads this to S3)."""
    
    os.makedirs(model_dir, exist_ok=True)
    
    # Save the trained model
    model_path = os.path.join(model_dir, 'model.joblib')
    joblib.dump(model, model_path)
    print(f"\nModel saved to: {model_path}")
    
    # Save feature names for inference
    features_path = os.path.join(model_dir, 'feature_names.json')
    with open(features_path, 'w') as f:
        json.dump(feature_names, f)
    print(f"Feature names saved to: {features_path}")
    
    # Save metrics
    metrics_path = os.path.join(model_dir, 'metrics.json')
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f)
    print(f"Metrics saved to: {metrics_path}")
    
    # Save feature importances
    importances = dict(zip(feature_names, model.feature_importances_.tolist()))
    importances_path = os.path.join(model_dir, 'feature_importances.json')
    with open(importances_path, 'w') as f:
        json.dump(importances, f, indent=2)
    print(f"Feature importances saved to: {importances_path}")

if __name__ == '__main__':
    print("=" * 60)
    print("PENSKE LOGISTICS - DEMAND FORECASTING TRAINING")
    print("=" * 60)
    
    args = parse_args()
    
    # Load data
    train_df, valid_df = load_data(args.train, args.validation)
    
    # Train model
    model = train_model(train_df, args)
    
    # Evaluate model
    metrics = evaluate_model(model, valid_df)
    
    # Save model (SageMaker will upload /opt/ml/model/ to S3)
    feature_names = [col for col in train_df.columns if col != 'target']
    save_model(model, args.model_dir, metrics, feature_names)
    
    print("\n" + "=" * 60)
    print("TRAINING COMPLETE - Model artifacts will be uploaded to S3")
    print("=" * 60)
```

---

### Step 5: Run Training Job

**What we're doing:** Submitting a training job to SageMaker, which will:
1. Provision an ML instance (e.g., ml.m5.xlarge)
2. Download training data from S3
3. Run your `train.py` script
4. Upload trained model to S3
5. Terminate the instance

**Where the output goes:** `s3://penske-sagemaker-{ACCOUNT_ID}/output/{job-name}/output/model.tar.gz`

**Create file: `src/ml/sagemaker_training.py`**

```python
#!/usr/bin/env python3
"""
SageMaker Training Job Launcher for Penske Logistics

This script submits a training job to SageMaker and monitors its progress.
"""

import sagemaker
from sagemaker.sklearn import SKLearn
import boto3
from datetime import datetime

def run_training_job():
    """Submit and monitor a SageMaker training job."""
    
    # Get AWS account info
    sts = boto3.client('sts')
    account_id = sts.get_caller_identity()['Account']
    region = boto3.session.Session().region_name or 'us-east-1'
    
    # SageMaker session
    sagemaker_session = sagemaker.Session()
    role = f'arn:aws:iam::{account_id}:role/PenskeSageMakerRole'
    
    # S3 paths
    bucket = f'penske-sagemaker-{account_id}'
    training_data = f's3://{bucket}/training/train.csv'
    validation_data = f's3://{bucket}/training/validation.csv'
    output_path = f's3://{bucket}/output'
    
    print("=" * 60)
    print("SAGEMAKER TRAINING JOB CONFIGURATION")
    print("=" * 60)
    print(f"Account ID: {account_id}")
    print(f"Region: {region}")
    print(f"Role: {role}")
    print(f"Training Data: {training_data}")
    print(f"Output Path: {output_path}")
    print("=" * 60)
    
    # Create estimator
    sklearn_estimator = SKLearn(
        entry_point='train.py',
        source_dir='src/ml/scripts',
        role=role,
        instance_type='ml.m5.xlarge',  # 4 vCPU, 16 GB RAM - ~$0.23/hour
        instance_count=1,
        framework_version='1.2-1',
        py_version='py3',
        output_path=output_path,
        sagemaker_session=sagemaker_session,
        hyperparameters={
            'n_estimators': 100,
            'max_depth': 10,
            'min_samples_split': 5,
            'min_samples_leaf': 2
        },
        base_job_name='penske-demand-forecast'
    )
    
    print("\nStarting training job...")
    print("This will take 5-15 minutes depending on data size.\n")
    
    # Start training (this blocks until complete)
    sklearn_estimator.fit({
        'train': training_data,
        'validation': validation_data
    })
    
    # Get results
    job_name = sklearn_estimator.latest_training_job.name
    model_artifact = sklearn_estimator.model_data
    
    print("\n" + "=" * 60)
    print("TRAINING COMPLETE!")
    print("=" * 60)
    print(f"Job Name: {job_name}")
    print(f"Model Artifact: {model_artifact}")
    print(f"\nTo deploy this model, use:")
    print(f"  model_artifact = '{model_artifact}'")
    print("=" * 60)
    
    return {
        'job_name': job_name,
        'model_artifact': model_artifact,
        'estimator': sklearn_estimator
    }

if __name__ == '__main__':
    result = run_training_job()
```

**Run the training:**
```bash
python src/ml/sagemaker_training.py
```

**Expected Output:**
```
============================================================
SAGEMAKER TRAINING JOB CONFIGURATION
============================================================
Account ID: 123456789012
Region: us-east-1
Role: arn:aws:iam::123456789012:role/PenskeSageMakerRole
Training Data: s3://penske-sagemaker-123456789012/training/train.csv
Output Path: s3://penske-sagemaker-123456789012/output
============================================================

Starting training job...
This will take 5-15 minutes depending on data size.

2024-01-15 10:45:23 Starting - Starting the training job...
2024-01-15 10:46:01 Starting - Launching requested ML instances...
2024-01-15 10:47:15 Starting - Preparing the instances for training...
2024-01-15 10:48:02 Training - Training image download completed...
2024-01-15 10:48:30 Training - Running training script...
...
2024-01-15 10:52:45 Completed - Training job completed

============================================================
TRAINING COMPLETE!
============================================================
Job Name: penske-demand-forecast-2024-01-15-10-45-23
Model Artifact: s3://penske-sagemaker-123456789012/output/penske-demand-forecast-2024-01-15-10-45-23/output/model.tar.gz

To deploy this model, use:
  model_artifact = 's3://penske-sagemaker-123456789012/output/penske-demand-forecast-2024-01-15-10-45-23/output/model.tar.gz'
============================================================
```

**Verify the output in S3:**
```bash
# List the model artifacts
aws s3 ls s3://penske-sagemaker-${AWS_ACCOUNT_ID}/output/ --recursive

# Download and inspect model.tar.gz contents
aws s3 cp s3://penske-sagemaker-${AWS_ACCOUNT_ID}/output/penske-demand-forecast-TIMESTAMP/output/model.tar.gz .
tar -tzf model.tar.gz
```

**Expected contents of model.tar.gz:**
```
model.joblib           # The trained scikit-learn model
feature_names.json     # List of feature column names
metrics.json           # Training/validation metrics
feature_importances.json  # Feature importance scores
```

---

### Step 6: Deploy Model Endpoint

**What we're doing:** Creating a real-time inference endpoint that:
- Hosts your trained model on a managed instance
- Accepts prediction requests via HTTPS
- Returns predictions in milliseconds
- Auto-scales based on traffic

**Create file: `src/ml/scripts/inference.py`** (Required for deployment)

```python
#!/usr/bin/env python3
"""
SageMaker Inference Script

This script is loaded by SageMaker when serving predictions.
It defines how to load the model and process prediction requests.
"""

import joblib
import json
import numpy as np
import os

def model_fn(model_dir):
    """
    Load the trained model from the model directory.
    
    SageMaker calls this function once when the endpoint starts.
    The model_dir contains the extracted contents of model.tar.gz.
    
    Returns:
        The loaded model object
    """
    model_path = os.path.join(model_dir, 'model.joblib')
    model = joblib.load(model_path)
    
    # Also load feature names for validation
    features_path = os.path.join(model_dir, 'feature_names.json')
    if os.path.exists(features_path):
        with open(features_path, 'r') as f:
            model.feature_names_ = json.load(f)
    
    return model

def input_fn(request_body, request_content_type):
    """
    Deserialize the input data.
    
    SageMaker calls this function for each prediction request.
    
    Args:
        request_body: The request payload
        request_content_type: The content type (e.g., 'application/json')
    
    Returns:
        Deserialized input data as numpy array
    """
    if request_content_type == 'application/json':
        data = json.loads(request_body)
        return np.array(data)
    else:
        raise ValueError(f"Unsupported content type: {request_content_type}")

def predict_fn(input_data, model):
    """
    Make predictions using the loaded model.
    
    Args:
        input_data: The deserialized input from input_fn
        model: The loaded model from model_fn
    
    Returns:
        Model predictions
    """
    predictions = model.predict(input_data)
    return predictions

def output_fn(prediction, response_content_type):
    """
    Serialize the prediction output.
    
    Args:
        prediction: The prediction from predict_fn
        response_content_type: Requested response format
    
    Returns:
        Serialized prediction
    """
    if response_content_type == 'application/json':
        return json.dumps(prediction.tolist())
    else:
        raise ValueError(f"Unsupported response type: {response_content_type}")
```

**Create file: `src/ml/deploy_endpoint.py`**

```python
#!/usr/bin/env python3
"""
Deploy trained model to SageMaker real-time endpoint.
"""

from sagemaker.sklearn import SKLearnModel
import boto3
import sagemaker

def deploy_model(model_artifact_path: str):
    """
    Deploy a trained model to a SageMaker endpoint.
    
    Args:
        model_artifact_path: S3 path to model.tar.gz
    
    Returns:
        The deployed predictor object
    """
    
    sts = boto3.client('sts')
    account_id = sts.get_caller_identity()['Account']
    role = f'arn:aws:iam::{account_id}:role/PenskeSageMakerRole'
    
    print("=" * 60)
    print("DEPLOYING MODEL TO SAGEMAKER ENDPOINT")
    print("=" * 60)
    print(f"Model Artifact: {model_artifact_path}")
    print(f"Endpoint Name: penske-demand-forecast")
    print(f"Instance Type: ml.t2.medium (~$0.056/hour)")
    print("=" * 60)
    
    # Create model object
    model = SKLearnModel(
        model_data=model_artifact_path,
        role=role,
        entry_point='inference.py',
        source_dir='src/ml/scripts',
        framework_version='1.2-1',
        py_version='py3'
    )
    
    print("\nDeploying endpoint (this takes 5-10 minutes)...")
    
    # Deploy to endpoint
    predictor = model.deploy(
        instance_type='ml.t2.medium',
        initial_instance_count=1,
        endpoint_name='penske-demand-forecast'
    )
    
    print("\n" + "=" * 60)
    print("ENDPOINT DEPLOYED SUCCESSFULLY!")
    print("=" * 60)
    print(f"Endpoint Name: penske-demand-forecast")
    print(f"Endpoint URL: https://runtime.sagemaker.{boto3.session.Session().region_name}.amazonaws.com")
    print("\nTo make predictions, use the SageMakerService class.")
    print("=" * 60)
    
    return predictor

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python deploy_endpoint.py <model_artifact_s3_path>")
        print("Example: python deploy_endpoint.py s3://penske-sagemaker-123/output/job-name/output/model.tar.gz")
        sys.exit(1)
    
    model_path = sys.argv[1]
    deploy_model(model_path)
```

**Deploy the model:**
```bash
python src/ml/deploy_endpoint.py s3://penske-sagemaker-${AWS_ACCOUNT_ID}/output/penske-demand-forecast-TIMESTAMP/output/model.tar.gz
```

**Verify endpoint is active:**
```bash
aws sagemaker describe-endpoint --endpoint-name penske-demand-forecast
```

**Expected Output:**
```json
{
    "EndpointName": "penske-demand-forecast",
    "EndpointStatus": "InService",
    "CreationTime": "2024-01-15T11:00:00Z",
    "LastModifiedTime": "2024-01-15T11:08:00Z"
}
```

---

### Step 7: Make Predictions

**What we're doing:** Calling the deployed endpoint to get real-time predictions.

**Create file: `src/services/sagemaker_service.py`**

```python
#!/usr/bin/env python3
"""
SageMaker Service for making predictions against deployed endpoints.
"""

import boto3
import json
import numpy as np
from typing import List, Dict, Union

class SageMakerService:
    """Service class for interacting with SageMaker endpoints."""
    
    def __init__(self, endpoint_name: str = 'penske-demand-forecast'):
        """
        Initialize the SageMaker service.
        
        Args:
            endpoint_name: Name of the deployed SageMaker endpoint
        """
        self.client = boto3.client('sagemaker-runtime')
        self.endpoint_name = endpoint_name
    
    def predict_demand(self, features: List[List[float]]) -> List[float]:
        """
        Predict logistics demand using the deployed model.
        
        Args:
            features: 2D list of feature values, each inner list is one sample
                      Example: [[1250, 3.45, 0, 1, 0, 1180, 0, 1, 0, 0]]
        
        Returns:
            List of predicted demand values
        
        Example:
            >>> service = SageMakerService()
            >>> features = [[1250, 3.45, 0, 1, 0, 1180, 0, 1, 0, 0]]
            >>> predictions = service.predict_demand(features)
            >>> print(f"Predicted demand: {predictions[0]}")
            Predicted demand: 1320
        """
        response = self.client.invoke_endpoint(
            EndpointName=self.endpoint_name,
            ContentType='application/json',
            Body=json.dumps(features)
        )
        
        result = json.loads(response['Body'].read().decode())
        return result
    
    def predict_single(self, 
                       shipment_volume: int,
                       fuel_price: float,
                       weather_severity: int,
                       day_of_week: int,
                       is_holiday: int,
                       previous_day_volume: int,
                       region: str) -> float:
        """
        Predict demand for a single day with named parameters.
        
        Args:
            shipment_volume: Current day's shipment count
            fuel_price: Fuel cost per gallon
            weather_severity: 0=none, 1=minor, 2=severe
            day_of_week: 1=Monday through 7=Sunday
            is_holiday: 0=no, 1=yes
            previous_day_volume: Previous day's shipment count
            region: One of ['Midwest', 'Northeast', 'Southeast', 'Southwest', 'West']
        
        Returns:
            Predicted demand for next day
        """
        # One-hot encode region (drop 'Southwest' as base)
        region_midwest = 1 if region == 'Midwest' else 0
        region_northeast = 1 if region == 'Northeast' else 0
        region_southeast = 1 if region == 'Southeast' else 0
        region_west = 1 if region == 'West' else 0
        
        features = [[
            shipment_volume,
            fuel_price,
            weather_severity,
            day_of_week,
            is_holiday,
            previous_day_volume,
            region_midwest,
            region_northeast,
            region_southeast,
            region_west
        ]]
        
        predictions = self.predict_demand(features)
        return predictions[0]

# Example usage
if __name__ == '__main__':
    service = SageMakerService()
    
    # Example: Predict demand for tomorrow
    prediction = service.predict_single(
        shipment_volume=1250,
        fuel_price=3.45,
        weather_severity=0,
        day_of_week=2,  # Tuesday
        is_holiday=0,
        previous_day_volume=1180,
        region='Northeast'
    )
    
    print(f"Predicted demand for tomorrow: {prediction:.0f} shipments")
```

**Test the endpoint:**
```bash
python src/services/sagemaker_service.py
```

**Expected Output:**
```
Predicted demand for tomorrow: 1320 shipments
```

---

### SageMaker Summary

| Step | What Happens | Output Location |
|------|--------------|-----------------|
| 1. Prepare Data | Create train.csv, validation.csv | `data/training/` |
| 2. Upload to S3 | Copy data files to cloud | `s3://penske-sagemaker-{ID}/training/` |
| 3. Create Role | IAM permissions for SageMaker | AWS IAM |
| 4. Training Script | Define model training logic | `src/ml/scripts/train.py` |
| 5. Run Training | Execute on ML instance | `s3://.../output/model.tar.gz` |
| 6. Deploy Endpoint | Host model for predictions | SageMaker endpoint |
| 7. Make Predictions | Call endpoint API | Real-time results |

### SageMaker Costs

| Resource | Use Case | Cost |
|----------|----------|------|
| ml.m5.xlarge | Training (per hour) | $0.23 |
| ml.t2.medium | Endpoint (per hour) | $0.056 |
| S3 Storage | Data + Models (per GB/month) | $0.023 |
| **Typical Training Job** | 10 min on ml.m5.xlarge | ~$0.04 |
| **Endpoint (24/7)** | ml.t2.medium per month | ~$40 |

### Cleanup SageMaker Resources

```bash
# Delete endpoint (stops billing for hosting)
aws sagemaker delete-endpoint --endpoint-name penske-demand-forecast

# Delete endpoint configuration
aws sagemaker delete-endpoint-config --endpoint-config-name penske-demand-forecast

# Delete model registration
aws sagemaker delete-model --model-name penske-demand-model

# Delete S3 data (optional - keeps training data)
aws s3 rm s3://penske-sagemaker-${AWS_ACCOUNT_ID} --recursive
```

---

## Troubleshooting

### Issue: Tasks Keep Failing

```bash
# Check task stopped reason
aws ecs describe-tasks \
    --cluster penske-analytics-prod \
    --tasks $(aws ecs list-tasks --cluster penske-analytics-prod --desired-status STOPPED --query 'taskArns[0]' --output text) \
    --query 'tasks[0].stoppedReason'

# Check CloudWatch logs for errors
aws logs get-log-events \
    --log-group-name /ecs/penske-logistics-analytics-prod \
    --log-stream-name $(aws logs describe-log-streams --log-group-name /ecs/penske-logistics-analytics-prod --query 'logStreams[0].logStreamName' --output text)
```

### Issue: ALB Returns 502/503

```bash
# Check target group health
aws elbv2 describe-target-health \
    --target-group-arn $(aws elbv2 describe-target-groups --names penske-api-tg-prod --query 'TargetGroups[0].TargetGroupArn' --output text)
```

### Issue: Image Pull Errors

```bash
# Verify ECR permissions
aws ecr get-repository-policy --repository-name penske-logistics-analytics

# Re-login to ECR
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REPO
```

### Common Fixes

| Issue | Solution |
|-------|----------|
| OutOfMemoryError | Increase task memory in CloudFormation |
| Connection timeout | Check security group rules |
| Secret not found | Verify secret name matches exactly |
| Image not found | Push image before deploying stack |

---

## Cost Optimization

### Development Environment

```yaml
# Reduce costs for dev/staging
TaskDefinition:
  Cpu: '256'    # Minimum
  Memory: '512' # Minimum
ECSService:
  DesiredCount: 1
AutoScalingTarget:
  MinCapacity: 1
  MaxCapacity: 2
```

### Production Tips

| Optimization | Savings |
|--------------|---------|
| Use Fargate Spot | 50-70% |
| Right-size tasks | 20-40% |
| Enable auto-scaling | Variable |
| Use Reserved Capacity | 30-50% |

### Estimated Monthly Costs

| Component | Dev | Prod |
|-----------|-----|------|
| ECS Fargate | $15 | $60 |
| ALB | $20 | $20 |
| NAT Gateway | $0 | $35 |
| CloudWatch | $5 | $15 |
| **Total** | **~$40** | **~$130** |

---

## Cleanup

To delete all resources:

```bash
# Delete CloudFormation stack (deletes all resources)
aws cloudformation delete-stack --stack-name penske-analytics-prod

# Wait for deletion
aws cloudformation wait stack-delete-complete --stack-name penske-analytics-prod

# Delete ECR repository (optional)
aws ecr delete-repository \
    --repository-name penske-logistics-analytics \
    --force

# Delete S3 bucket (if created)
aws s3 rb s3://penske-analytics-data-$AWS_ACCOUNT_ID --force
```

---

## Next Steps

1. **Add Custom Domain:** Configure Route 53 and ACM certificate
2. **Enable HTTPS:** Update ALB listener to use SSL
3. **Set Up Monitoring:** Create CloudWatch dashboards and alarms
4. **Configure Backups:** Enable automated snapshots

---

**[← Back to Main Guide](../README.md)** | **[Azure Guide →](../azure/DEPLOYMENT_GUIDE.md)**
