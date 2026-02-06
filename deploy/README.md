# Penske Logistics Analytics - Deployment Guide

Production deployment guide for AWS, Azure, and GCP cloud platforms.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PENSKE LOGISTICS ANALYTICS                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                     │
│  │   AWS ECS   │    │ Azure ACA   │    │  GCP Cloud  │                     │
│  │   Fargate   │    │  Container  │    │    Run      │                     │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘                     │
│         │                  │                  │                             │
│         └──────────────────┴──────────────────┘                             │
│                            │                                                │
│  ┌─────────────────────────┴─────────────────────────┐                     │
│  │                 Docker Container                   │                     │
│  │  ┌─────────────────┐  ┌─────────────────────────┐ │                     │
│  │  │   FastAPI       │  │    Streamlit Dashboard  │ │                     │
│  │  │   (port 8000)   │  │       (port 8501)       │ │                     │
│  │  └─────────────────┘  └─────────────────────────┘ │                     │
│  └───────────────────────────────────────────────────┘                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Quick Reference

| Cloud Platform | Directory | Primary Service | Guide |
|----------------|-----------|-----------------|-------|
| **AWS** | `deploy/aws/` | ECS Fargate | [AWS Guide](aws/DEPLOYMENT_GUIDE.md) |
| **Azure** | `deploy/azure/` | Container Apps | [Azure Guide](azure/DEPLOYMENT_GUIDE.md) |
| **GCP** | `deploy/gcp/` | Cloud Run | [GCP Guide](gcp/DEPLOYMENT_GUIDE.md) |

---

## Prerequisites (All Platforms)

### 1. Local Development Tools

```bash
# Docker
docker --version  # Required: 20.10+

# Python
python --version  # Required: 3.11+

# Git
git --version
```

### 2. Cloud CLI Tools

```bash
# AWS CLI
aws --version
aws configure  # Set credentials

# Azure CLI
az --version
az login

# Google Cloud SDK
gcloud --version
gcloud auth login
```

### 3. Environment Variables

Create a `.env` file in the project root:

```env
# Required
OPENAI_API_KEY=sk-your-openai-api-key

# Optional
ENVIRONMENT=prod
LOG_LEVEL=INFO
```

---

## Deployment Options

### Option 1: Docker Compose (Local/Dev)

```bash
cd deploy
docker-compose up -d
```

**Access:**
- API: http://localhost:8000
- Dashboard: http://localhost:8501

### Option 2: Cloud Deployment

Choose your cloud platform:

| Platform | Best For | Estimated Cost |
|----------|----------|----------------|
| [AWS ECS](aws/DEPLOYMENT_GUIDE.md) | Enterprise, existing AWS | ~$50-100/month |
| [Azure ACA](azure/DEPLOYMENT_GUIDE.md) | Microsoft ecosystem | ~$40-80/month |
| [GCP Cloud Run](gcp/DEPLOYMENT_GUIDE.md) | Pay-per-use, scale-to-zero | ~$20-60/month |

---

## Directory Structure

```
deploy/
├── README.md                    # This file
├── Dockerfile                   # Base container image
├── docker-compose.yml           # Local development
│
├── aws/                         # AWS Deployment
│   ├── DEPLOYMENT_GUIDE.md      # Step-by-step guide
│   ├── cloudformation.yaml      # Infrastructure as Code
│   ├── buildspec.yml            # CodeBuild config
│   └── ecs-task-definition.json # ECS task config
│
├── azure/                       # Azure Deployment
│   ├── DEPLOYMENT_GUIDE.md      # Step-by-step guide
│   ├── azure-pipelines.yml      # CI/CD pipeline
│   └── arm-template.json        # ARM template
│
├── gcp/                         # GCP Deployment
│   ├── DEPLOYMENT_GUIDE.md      # Step-by-step guide
│   ├── cloudbuild.yaml          # Cloud Build config
│   └── cloudrun-service.yaml    # Cloud Run config
│
└── kubernetes/                  # Kubernetes (any cloud)
    ├── deployment.yaml
    └── service.yaml
```

---

## Deployment Checklist

### Pre-Deployment

- [ ] Docker builds successfully locally
- [ ] All tests pass (`pytest tests/`)
- [ ] Environment variables configured
- [ ] Cloud credentials configured
- [ ] Domain/SSL certificates ready (production)

### Post-Deployment

- [ ] Health check endpoints responding
- [ ] API endpoints functional
- [ ] Dashboard accessible
- [ ] Logs streaming to cloud monitoring
- [ ] Alerts configured

---

## Quick Commands

### Build Docker Image

```bash
# From project root
docker build -t penske-analytics:latest -f deploy/Dockerfile .
```

### Test Locally

```bash
# Run container
docker run -p 8000:8000 -p 8501:8501 \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  penske-analytics:latest
```

### Deploy to Each Cloud

```bash
# AWS
cd deploy/aws && ./deploy.sh

# Azure
cd deploy/azure && ./deploy.sh

# GCP
cd deploy/gcp && ./deploy.sh
```

---

## Support

For deployment issues:
1. Check the platform-specific troubleshooting guide
2. Review CloudWatch/Azure Monitor/Cloud Logging
3. Contact the DevOps team

---

**Next Steps:** Choose your cloud platform and follow the detailed guide:
- [AWS Deployment Guide →](aws/DEPLOYMENT_GUIDE.md)
- [Azure Deployment Guide →](azure/DEPLOYMENT_GUIDE.md)
- [GCP Deployment Guide →](gcp/DEPLOYMENT_GUIDE.md)
