#!/bin/bash
# AWS Deployment Script for Penske Logistics Analytics
# Usage: ./deploy.sh [environment]
# Example: ./deploy.sh prod

set -e

# Configuration
ENVIRONMENT=${1:-dev}
AWS_REGION=${AWS_REGION:-us-east-1}
STACK_NAME="penske-analytics-${ENVIRONMENT}"
ECR_REPO_NAME="penske-logistics-analytics"

echo "============================================"
echo "AWS Deployment - Penske Logistics Analytics"
echo "============================================"
echo "Environment: $ENVIRONMENT"
echo "Region: $AWS_REGION"
echo "Stack: $STACK_NAME"
echo "============================================"

# Step 1: Get AWS Account ID
echo "[1/6] Getting AWS Account ID..."
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REPO="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_NAME}"
echo "Account: $AWS_ACCOUNT_ID"

# Step 2: Create ECR Repository (if not exists)
echo "[2/6] Creating ECR repository..."
aws ecr describe-repositories --repository-names $ECR_REPO_NAME --region $AWS_REGION 2>/dev/null || \
    aws ecr create-repository --repository-name $ECR_REPO_NAME --region $AWS_REGION

# Step 3: Login to ECR
echo "[3/6] Logging into ECR..."
aws ecr get-login-password --region $AWS_REGION | \
    docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

# Step 4: Build and Push Docker Image
echo "[4/6] Building Docker image..."
cd ../..
docker build -t ${ECR_REPO_NAME}:latest -f deploy/Dockerfile .
docker tag ${ECR_REPO_NAME}:latest ${ECR_REPO}:latest
docker tag ${ECR_REPO_NAME}:latest ${ECR_REPO}:${ENVIRONMENT}

echo "[5/6] Pushing to ECR..."
docker push ${ECR_REPO}:latest
docker push ${ECR_REPO}:${ENVIRONMENT}
cd deploy/aws

# Step 5: Deploy CloudFormation Stack
echo "[6/6] Deploying CloudFormation stack..."
aws cloudformation deploy \
    --stack-name $STACK_NAME \
    --template-file cloudformation.yaml \
    --parameter-overrides \
        Environment=$ENVIRONMENT \
        ContainerImage=${ECR_REPO}:latest \
    --capabilities CAPABILITY_IAM \
    --region $AWS_REGION \
    --no-fail-on-empty-changeset

# Get outputs
echo ""
echo "============================================"
echo "DEPLOYMENT COMPLETE!"
echo "============================================"
aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query 'Stacks[0].Outputs[*].[OutputKey,OutputValue]' \
    --output table
echo "============================================"
