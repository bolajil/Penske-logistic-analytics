# Frontend Applications

This directory contains multiple frontend options for the Penske Logistics Analytics platform.

## Available Frontends

| Frontend | Language | Port | Best For |
|----------|----------|------|----------|
| **Streamlit** | Python | 8501 | Dashboards, analytics, rapid prototyping |
| **Gradio** | Python | 7860 | ML demos, quick prototypes |
| **React** | TypeScript | 3000 | Production apps, custom UI |

## Quick Start

### Streamlit (Default)
```bash
cd app
streamlit run streamlit_dashboard.py
```
**URL:** http://localhost:8501

### Gradio (Enhanced - Recommended)
```bash
cd app
python gradio_app_enhanced.py
```
**URL:** http://localhost:7860

**Features:** Interactive charts, analytics dashboard, demand forecasting, AI assistant

### React
```bash
cd app/react-frontend
npm install
npm run dev
```
**URL:** http://localhost:3000

> **Note:** The React lint errors will resolve after running `npm install` in the react-frontend directory.

---

## Directory Structure

```
app/
├── README.md                 # This file
├── streamlit_dashboard.py    # Streamlit dashboard (default)
├── gradio_app_enhanced.py    # Gradio with charts & analytics (recommended)
├── gradio_simple.py          # Lightweight Gradio version
├── api_server.py             # FastAPI backend
├── FRONTEND_TEMPLATES.md     # Detailed templates & code
└── react-frontend/           # React application
    ├── src/
    ├── package.json
    └── ...
```

---

## Comparison

### Streamlit
- **Pros:** Easy to build, Python-native, great for data apps
- **Cons:** Limited customization, not ideal for complex UIs
- **Use when:** Building internal tools, dashboards, prototypes

### Gradio
- **Pros:** Very easy setup, great for ML demos, shareable links
- **Cons:** Less flexible layout, limited styling
- **Use when:** Demoing ML models, quick prototypes

### React
- **Pros:** Full control, professional UI, mobile-friendly, scalable
- **Cons:** Requires JavaScript/TypeScript, longer setup
- **Use when:** Production apps, customer-facing products

---

## Cloud Deployment

All frontends can be deployed to cloud platforms:

| Frontend | AWS | Azure | GCP |
|----------|-----|-------|-----|
| Streamlit | ECS Fargate, App Runner | Container Apps | Cloud Run |
| Gradio | ECS Fargate, App Runner | Container Apps | Cloud Run |
| React | S3 + CloudFront, Amplify | Static Web Apps | Firebase Hosting |

See `FRONTEND_TEMPLATES.md` for detailed deployment guides.

---

## API Integration

All frontends connect to the same backend API:

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND OPTIONS                      │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐            │
│  │Streamlit │   │  Gradio  │   │  React   │            │
│  │  :8501   │   │  :7860   │   │  :3000   │            │
│  └────┬─────┘   └────┬─────┘   └────┬─────┘            │
│       └──────────────┼──────────────┘                   │
│                      ▼                                  │
│              ┌──────────────┐                           │
│              │  API Server  │                           │
│              │    :8000     │                           │
│              └──────┬───────┘                           │
│                     ▼                                   │
│    ┌─────────────────────────────────────┐             │
│    │         Cloud ML Endpoints           │             │
│    │  AWS SageMaker | Azure ML | Vertex   │             │
│    └─────────────────────────────────────┘             │
└─────────────────────────────────────────────────────────┘
```

---

## Environment Variables

Create `.env` file in the app directory:

```env
# API Configuration
API_URL=http://localhost:8000

# AWS
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_REGION=us-east-1

# Azure
AZURE_SUBSCRIPTION_ID=your-subscription
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com
AZURE_OPENAI_KEY=your-key

# GCP
GCP_PROJECT_ID=your-project
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
```
