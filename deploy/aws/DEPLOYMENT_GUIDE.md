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

Amazon SageMaker enables training, deploying, and managing custom ML models for logistics predictions.

### SageMaker Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                     SageMaker ML Pipeline                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐ │
│  │  S3 Data    │→ │  Training   │→ │   Model     │→ │  Endpoint  │ │
│  │  (input)    │  │   Job       │  │  Registry   │  │ (inference)│ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

### Step 1: Create S3 Bucket for Training Data

```bash
# Create S3 bucket for ML data
aws s3 mb s3://penske-sagemaker-${AWS_ACCOUNT_ID} --region $AWS_REGION

# Upload training data
aws s3 cp data/training/ s3://penske-sagemaker-${AWS_ACCOUNT_ID}/training/ --recursive
```

### Step 2: Create SageMaker Execution Role

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

# Attach policies
aws iam attach-role-policy \
    --role-name PenskeSageMakerRole \
    --policy-arn arn:aws:iam::aws:policy/AmazonSageMakerFullAccess

aws iam attach-role-policy \
    --role-name PenskeSageMakerRole \
    --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
```

### Step 3: Train Custom Model

```python
# src/ml/sagemaker_training.py
import sagemaker
from sagemaker.sklearn import SKLearn

def train_demand_forecasting_model():
    """Train demand forecasting model on SageMaker."""
    
    role = 'arn:aws:iam::YOUR_ACCOUNT:role/PenskeSageMakerRole'
    
    sklearn_estimator = SKLearn(
        entry_point='train.py',
        source_dir='src/ml/scripts',
        role=role,
        instance_type='ml.m5.xlarge',
        instance_count=1,
        framework_version='1.2-1',
        py_version='py3',
        hyperparameters={
            'n_estimators': 100,
            'max_depth': 10,
            'forecast_horizon': 30
        }
    )
    
    sklearn_estimator.fit({
        'train': 's3://penske-sagemaker-YOUR_ACCOUNT/training/train.csv',
        'validation': 's3://penske-sagemaker-YOUR_ACCOUNT/training/validation.csv'
    })
    
    return sklearn_estimator

# Training script: src/ml/scripts/train.py
"""
import argparse
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib
import os

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--n_estimators', type=int, default=100)
    parser.add_argument('--max_depth', type=int, default=10)
    args = parser.parse_args()
    
    # Load data
    train_data = pd.read_csv('/opt/ml/input/data/train/train.csv')
    
    # Train model
    model = RandomForestRegressor(
        n_estimators=args.n_estimators,
        max_depth=args.max_depth
    )
    model.fit(train_data.drop('target', axis=1), train_data['target'])
    
    # Save model
    joblib.dump(model, '/opt/ml/model/model.joblib')
"""
```

### Step 4: Deploy Model Endpoint

```python
# Deploy to real-time endpoint
from sagemaker.sklearn import SKLearnModel

def deploy_model(model_artifact_path):
    """Deploy trained model to SageMaker endpoint."""
    
    model = SKLearnModel(
        model_data=model_artifact_path,
        role='arn:aws:iam::YOUR_ACCOUNT:role/PenskeSageMakerRole',
        entry_point='inference.py',
        source_dir='src/ml/scripts',
        framework_version='1.2-1',
        py_version='py3'
    )
    
    predictor = model.deploy(
        instance_type='ml.t2.medium',
        initial_instance_count=1,
        endpoint_name='penske-demand-forecast'
    )
    
    return predictor

# Inference script: src/ml/scripts/inference.py
"""
import joblib
import numpy as np

def model_fn(model_dir):
    return joblib.load(f'{model_dir}/model.joblib')

def predict_fn(input_data, model):
    return model.predict(input_data)
"""
```

### Step 5: Invoke Endpoint

```python
# src/services/sagemaker_service.py
import boto3
import json

class SageMakerService:
    def __init__(self, endpoint_name='penske-demand-forecast'):
        self.client = boto3.client('sagemaker-runtime')
        self.endpoint_name = endpoint_name
    
    def predict_demand(self, features: list):
        """Predict logistics demand using deployed model."""
        response = self.client.invoke_endpoint(
            EndpointName=self.endpoint_name,
            ContentType='application/json',
            Body=json.dumps(features)
        )
        
        result = json.loads(response['Body'].read().decode())
        return result
    
    def batch_predict(self, data_s3_path: str, output_s3_path: str):
        """Run batch predictions for large datasets."""
        transformer = sagemaker.transformer.Transformer(
            model_name='penske-demand-model',
            instance_count=1,
            instance_type='ml.m5.xlarge',
            output_path=output_s3_path
        )
        
        transformer.transform(
            data=data_s3_path,
            content_type='text/csv',
            split_type='Line'
        )
```

### SageMaker Use Cases for Penske Analytics

| Use Case | Model Type | Description |
|----------|------------|-------------|
| **Demand Forecasting** | Time Series | Predict shipment volumes |
| **Route Optimization** | Reinforcement Learning | Optimize delivery routes |
| **ETD Prediction** | Regression | Estimate delivery times |
| **Anomaly Detection** | Unsupervised | Detect logistics anomalies |
| **Cost Prediction** | Regression | Forecast shipping costs |

### SageMaker Costs

| Instance Type | Use Case | Cost/Hour |
|---------------|----------|-----------|
| ml.t2.medium | Dev/Test endpoints | $0.056 |
| ml.m5.xlarge | Training | $0.23 |
| ml.m5.large | Production endpoint | $0.115 |
| ml.c5.xlarge | High-throughput inference | $0.204 |

### Auto-Scaling Endpoint

```bash
# Configure auto-scaling for production
aws application-autoscaling register-scalable-target \
    --service-namespace sagemaker \
    --resource-id endpoint/penske-demand-forecast/variant/AllTraffic \
    --scalable-dimension sagemaker:variant:DesiredInstanceCount \
    --min-capacity 1 \
    --max-capacity 5

# Create scaling policy
aws application-autoscaling put-scaling-policy \
    --policy-name penske-scaling-policy \
    --service-namespace sagemaker \
    --resource-id endpoint/penske-demand-forecast/variant/AllTraffic \
    --scalable-dimension sagemaker:variant:DesiredInstanceCount \
    --policy-type TargetTrackingScaling \
    --target-tracking-scaling-policy-configuration '{
        "TargetValue": 70.0,
        "PredefinedMetricSpecification": {
            "PredefinedMetricType": "SageMakerVariantInvocationsPerInstance"
        },
        "ScaleOutCooldown": 60,
        "ScaleInCooldown": 300
    }'
```

### Cleanup SageMaker Resources

```bash
# Delete endpoint
aws sagemaker delete-endpoint --endpoint-name penske-demand-forecast

# Delete endpoint configuration
aws sagemaker delete-endpoint-config --endpoint-config-name penske-demand-forecast

# Delete model
aws sagemaker delete-model --model-name penske-demand-model

# Delete S3 data (optional)
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
