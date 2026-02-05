# Penske Logistics Analytics - Deployment Guide

Complete deployment documentation for production environments.

---

## Deployment Options

| Option | Best For | Complexity |
|--------|----------|------------|
| Local Docker | Development/Testing | Low |
| Docker Compose | Small teams | Low |
| Kubernetes | Production scale | Medium |
| Azure Container Apps | Azure environments | Medium |
| AWS ECS/Fargate | AWS environments | Medium |

---

## Option 1: Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Generate test data
python -m src.data_generator

# Run dashboard
streamlit run app/streamlit_dashboard.py

# Run API (separate terminal)
uvicorn app.api_server:app --reload --port 8000
```

---

## Option 2: Docker Compose (Recommended for Demo)

### Build and Run

```bash
cd deploy

# Set environment variables
echo OPENAI_API_KEY=your-key-here > .env

# Build and start
docker-compose up --build -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### Access Points
- **Dashboard**: http://localhost:8501
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Stop Services
```bash
docker-compose down
```

---

## Option 3: Kubernetes Deployment

### Prerequisites
- Kubernetes cluster (AKS, EKS, GKE, or local)
- kubectl configured
- Container registry access

### Step 1: Build and Push Image

```bash
# Build image
docker build -t penske-logistics-analytics:latest -f deploy/Dockerfile .

# Tag for registry
docker tag penske-logistics-analytics:latest your-registry/penske-logistics-analytics:v1.0.0

# Push
docker push your-registry/penske-logistics-analytics:v1.0.0
```

### Step 2: Create Secrets

```bash
# Create namespace
kubectl create namespace penske-analytics

# Create secrets
kubectl create secret generic penske-secrets \
  --namespace penske-analytics \
  --from-literal=openai-api-key=your-api-key
```

### Step 3: Deploy

```bash
# Update image in deployment.yaml, then:
kubectl apply -f deploy/kubernetes/deployment.yaml -n penske-analytics
kubectl apply -f deploy/kubernetes/service.yaml -n penske-analytics

# Check status
kubectl get pods -n penske-analytics
kubectl get services -n penske-analytics
```

### Step 4: Access

```bash
# Port forward for testing
kubectl port-forward svc/penske-analytics-dashboard 8501:80 -n penske-analytics

# Or get LoadBalancer IP
kubectl get svc penske-analytics-dashboard -n penske-analytics
```

---

## Option 4: Azure Deployment

### Azure Container Apps

```bash
# Login
az login

# Create resource group
az group create --name penske-analytics-rg --location eastus

# Create container app environment
az containerapp env create \
  --name penske-analytics-env \
  --resource-group penske-analytics-rg \
  --location eastus

# Deploy API
az containerapp create \
  --name penske-api \
  --resource-group penske-analytics-rg \
  --environment penske-analytics-env \
  --image your-registry/penske-logistics-analytics:v1.0.0 \
  --target-port 8000 \
  --ingress external \
  --env-vars OPENAI_API_KEY=secretref:openai-key

# Deploy Dashboard
az containerapp create \
  --name penske-dashboard \
  --resource-group penske-analytics-rg \
  --environment penske-analytics-env \
  --image your-registry/penske-logistics-analytics:v1.0.0 \
  --target-port 8501 \
  --ingress external \
  --command "streamlit" "run" "app/streamlit_dashboard.py"
```

---

## Option 5: AWS ECS/Fargate Deployment

### Prerequisites
- AWS CLI configured with appropriate permissions
- ECR repository created
- AWS account with ECS, ECR, and VPC access

### Step 1: Create ECR Repository

```bash
# Create ECR repository
aws ecr create-repository \
  --repository-name penske-logistics-analytics \
  --region us-east-1

# Get login credentials
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com
```

### Step 2: Build and Push Image

```bash
# Build image
docker build -t penske-logistics-analytics:latest -f deploy/Dockerfile .

# Tag for ECR
docker tag penske-logistics-analytics:latest \
  <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/penske-logistics-analytics:latest

# Push to ECR
docker push <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/penske-logistics-analytics:latest
```

### Step 3: Store Secrets

```bash
# Create secret for OpenAI API key
aws secretsmanager create-secret \
  --name penske/openai-api-key \
  --secret-string "your-openai-api-key"
```

### Step 4: Deploy with CloudFormation

```bash
# Deploy the full stack
aws cloudformation create-stack \
  --stack-name penske-analytics-prod \
  --template-body file://deploy/aws/cloudformation.yaml \
  --parameters \
    ParameterKey=Environment,ParameterValue=prod \
    ParameterKey=ContainerImage,ParameterValue=<ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/penske-logistics-analytics:latest \
  --capabilities CAPABILITY_IAM

# Check stack status
aws cloudformation describe-stacks --stack-name penske-analytics-prod

# Get outputs (ALB DNS, endpoints)
aws cloudformation describe-stacks --stack-name penske-analytics-prod \
  --query "Stacks[0].Outputs"
```

### Alternative: Manual ECS Deployment

```bash
# Create ECS cluster
aws ecs create-cluster --cluster-name penske-analytics-cluster

# Register task definition
aws ecs register-task-definition \
  --cli-input-json file://deploy/aws/ecs-task-definition.json

# Create service
aws ecs create-service \
  --cluster penske-analytics-cluster \
  --service-name penske-analytics-service \
  --task-definition penske-logistics-analytics \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
```

### AWS CI/CD with CodePipeline

The project includes `deploy/aws/buildspec.yml` for AWS CodeBuild. Set up a pipeline:

1. **Source**: Connect to your Git repository
2. **Build**: Use CodeBuild with `buildspec.yml`
3. **Deploy**: ECS deployment action

```bash
# Create CodeBuild project
aws codebuild create-project \
  --name penske-analytics-build \
  --source type=GITHUB,location=https://github.com/your-repo \
  --artifacts type=NO_ARTIFACTS \
  --environment type=LINUX_CONTAINER,computeType=BUILD_GENERAL1_SMALL,image=aws/codebuild/standard:5.0,privilegedMode=true
```

### AWS Access Points

After deployment:
- **Dashboard**: `http://<ALB-DNS>/`
- **API**: `http://<ALB-DNS>/api/v1`
- **API Docs**: `http://<ALB-DNS>/api/v1/docs`

### AWS Cost Optimization

| Resource | Recommendation |
|----------|---------------|
| ECS | Use Fargate Spot for non-prod (70% savings) |
| NAT Gateway | Use VPC endpoints for ECR/S3 |
| ALB | Use single ALB with path-based routing |
| Logs | Set retention policy (30 days for prod) |

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | No | OpenAI API key for GenAI features |
| `PYTHONPATH` | Yes | Set to `/app` in containers |
| `DATA_PATH` | No | Custom data directory path |
| `LOG_LEVEL` | No | Logging level (INFO/DEBUG/WARNING) |

---

## Data Persistence

### For Production

Mount persistent volumes for:
- `/app/data` - Input data files
- `/app/models` - Trained model artifacts
- `/app/logs` - Application logs

### Docker Compose Example
```yaml
volumes:
  - ./data:/app/data
  - ./models:/app/models
```

### Kubernetes PVC
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: penske-data-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
```

---

## Health Checks

### API Health Endpoint
```
GET /
Response: {"status": "healthy", ...}
```

### Kubernetes Probes
```yaml
livenessProbe:
  httpGet:
    path: /
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
```

---

## Scaling Recommendations

| Component | Min Replicas | Max Replicas | CPU Request | Memory Request |
|-----------|--------------|--------------|-------------|----------------|
| API | 2 | 10 | 250m | 512Mi |
| Dashboard | 2 | 5 | 500m | 1Gi |

### Horizontal Pod Autoscaler
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: penske-api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: penske-analytics-api
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

---

## Security Checklist

- [ ] API keys stored in secrets management
- [ ] HTTPS enabled via ingress/load balancer
- [ ] Network policies configured
- [ ] Container runs as non-root user
- [ ] Resource limits set
- [ ] Logging and monitoring enabled
- [ ] Data encryption at rest
- [ ] Regular security scans

---

## Monitoring

### Recommended Stack
- **Metrics**: Prometheus + Grafana
- **Logs**: ELK Stack or Azure Monitor
- **Tracing**: Jaeger or Azure Application Insights

### Key Metrics to Monitor
- API response time (p50, p95, p99)
- Request rate and error rate
- Model prediction latency
- Memory and CPU utilization
- Data pipeline freshness
