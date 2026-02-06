# Cloud ML Services Reference Guide

A comprehensive guide to Machine Learning services across the three major cloud providers: **AWS**, **Microsoft Azure**, and **Google Cloud Platform (GCP)**. This document maps the algorithms from our project to equivalent cloud services and provides learning resources, applications, and examples.

---

## Table of Contents

1. [Overview: Cloud ML Landscape](#overview-cloud-ml-landscape)
2. [AWS Machine Learning Services](#aws-machine-learning-services)
   - [Amazon SageMaker](#amazon-sagemaker)
   - [Amazon Bedrock](#amazon-bedrock)
   - [Other AWS ML Services](#other-aws-ml-services)
3. [Microsoft Azure ML Services](#microsoft-azure-ml-services)
   - [Azure Machine Learning](#azure-machine-learning)
   - [Azure OpenAI Service](#azure-openai-service)
   - [Azure Cognitive Services](#azure-cognitive-services)
4. [Google Cloud ML Services](#google-cloud-ml-services)
   - [Vertex AI](#vertex-ai)
   - [Google Cloud AI APIs](#google-cloud-ai-apis)
   - [BigQuery ML](#bigquery-ml)
5. [Algorithm to Cloud Service Mapping](#algorithm-to-cloud-service-mapping)
6. [Comparison Matrix](#comparison-matrix)
7. [Cost Considerations](#cost-considerations)
8. [Getting Started Guides](#getting-started-guides)
9. [Glossary of Cloud ML Terms](#glossary-of-cloud-ml-terms)

---

## Overview: Cloud ML Landscape

### Why Use Cloud ML Services?

| Benefit | Description |
|---------|-------------|
| **Scalability** | Train models on massive datasets without infrastructure limits |
| **Managed Infrastructure** | No need to manage servers, GPUs, or clusters |
| **Pre-built Models** | Use ready-to-use models for common tasks |
| **AutoML** | Automatically find best algorithms and hyperparameters |
| **MLOps** | Built-in model versioning, deployment, and monitoring |
| **Cost Efficiency** | Pay only for compute time used |

### Cloud Provider Comparison at a Glance

| Aspect | AWS | Azure | GCP |
|--------|-----|-------|-----|
| **Primary ML Platform** | SageMaker | Azure ML | Vertex AI |
| **Generative AI** | Bedrock | Azure OpenAI | Vertex AI + Gemini |
| **AutoML** | SageMaker Autopilot | Azure AutoML | Vertex AI AutoML |
| **Pre-trained APIs** | Rekognition, Comprehend, etc. | Cognitive Services | Cloud AI APIs |
| **SQL-based ML** | Redshift ML | - | BigQuery ML |
| **Market Position** | Leader | Strong enterprise | Innovation leader |

---

## AWS Machine Learning Services

### Amazon SageMaker

**Full Name:** Amazon SageMaker

**What It Is:**
- Fully managed ML platform for building, training, and deploying models
- End-to-end ML workflow from data prep to production
- Supports custom code and built-in algorithms

#### Key Components

| Component | Purpose | Use Case |
|-----------|---------|----------|
| **SageMaker Studio** | Integrated IDE for ML | Development environment |
| **SageMaker Notebooks** | Jupyter notebooks in cloud | Experimentation |
| **SageMaker Training** | Managed model training | Scale training on GPU clusters |
| **SageMaker Inference** | Model deployment | Real-time and batch predictions |
| **SageMaker Autopilot** | AutoML | Automatic model selection |
| **SageMaker Pipelines** | MLOps workflows | CI/CD for ML |
| **SageMaker Feature Store** | Feature management | Centralized feature repository |
| **SageMaker Model Registry** | Model versioning | Track and manage models |
| **SageMaker Ground Truth** | Data labeling | Create training datasets |

#### Built-in Algorithms (Matching Our Project)

| Our Algorithm | SageMaker Equivalent | Use Case |
|---------------|---------------------|----------|
| **XGBoost** | XGBoost (Built-in) | Classification, Regression |
| **Random Forest** | Random Cut Forest | Anomaly detection |
| **Gradient Boosting** | XGBoost or LightGBM | Boosting models |
| **K-Means** | K-Means (Built-in) | Clustering |
| **Linear Regression** | Linear Learner | Regression |
| **Logistic Regression** | Linear Learner | Classification |

#### XGBoost on SageMaker Example

```python
import sagemaker
from sagemaker import get_execution_role
from sagemaker.inputs import TrainingInput
from sagemaker.estimator import Estimator

# Setup
role = get_execution_role()
session = sagemaker.Session()
bucket = session.default_bucket()

# Configure XGBoost
xgboost_container = sagemaker.image_uris.retrieve(
    framework="xgboost",
    region=session.boto_region_name,
    version="1.5-1"
)

# Create estimator
xgb_estimator = Estimator(
    image_uri=xgboost_container,
    role=role,
    instance_count=1,
    instance_type="ml.m5.xlarge",
    output_path=f"s3://{bucket}/xgboost-output",
    sagemaker_session=session
)

# Set hyperparameters
xgb_estimator.set_hyperparameters(
    objective="reg:squarederror",  # For regression
    num_round=200,
    max_depth=6,
    eta=0.1,
    subsample=0.8,
    colsample_bytree=0.8
)

# Train
train_input = TrainingInput(
    s3_data=f"s3://{bucket}/train/data.csv",
    content_type="csv"
)
xgb_estimator.fit({"train": train_input})

# Deploy
predictor = xgb_estimator.deploy(
    initial_instance_count=1,
    instance_type="ml.m5.large"
)
```

#### K-Means Clustering on SageMaker Example

```python
from sagemaker import KMeans

# Configure K-Means
kmeans = KMeans(
    role=role,
    instance_count=1,
    instance_type="ml.m5.xlarge",
    k=5,  # Number of clusters
    output_path=f"s3://{bucket}/kmeans-output"
)

# Train
kmeans.fit(kmeans.record_set(train_data))

# Deploy
kmeans_predictor = kmeans.deploy(
    initial_instance_count=1,
    instance_type="ml.m5.large"
)

# Predict cluster assignments
result = kmeans_predictor.predict(test_data)
```

#### SageMaker Autopilot (AutoML) Example

```python
from sagemaker.automl import AutoML

# Create AutoML job
automl = AutoML(
    role=role,
    target_attribute_name="target_column",
    output_path=f"s3://{bucket}/automl-output",
    max_candidates=20,  # Try up to 20 models
    max_runtime_per_training_job_in_seconds=3600
)

# Run AutoML
automl.fit(
    inputs=f"s3://{bucket}/train/data.csv",
    wait=True
)

# Get best model
best_candidate = automl.best_candidate()
print(f"Best model: {best_candidate['CandidateName']}")

# Deploy best model
predictor = automl.deploy(
    initial_instance_count=1,
    instance_type="ml.m5.large"
)
```

#### Learning Resources

| Resource | Link | Description |
|----------|------|-------------|
| **SageMaker Workshop** | aws.amazon.com/sagemaker/getting-started | Hands-on tutorials |
| **SageMaker Examples** | github.com/aws/amazon-sagemaker-examples | Code examples |
| **AWS ML Specialty Cert** | aws.amazon.com/certification/certified-machine-learning-specialty | Professional certification |
| **SageMaker Documentation** | docs.aws.amazon.com/sagemaker | Official docs |

---

### Amazon Bedrock

**Full Name:** Amazon Bedrock

**What It Is:**
- Fully managed service for **Generative AI** and Foundation Models
- Access to models from Anthropic (Claude), Meta (Llama), Amazon (Titan), and others
- No need to manage infrastructure for LLMs

#### Key Features

| Feature | Description |
|---------|-------------|
| **Foundation Models** | Pre-trained LLMs ready to use |
| **Fine-tuning** | Customize models with your data |
| **RAG Support** | Built-in Retrieval-Augmented Generation |
| **Knowledge Bases** | Connect to your enterprise data |
| **Agents** | Build AI agents that take actions |
| **Guardrails** | Content filtering and safety controls |

#### Available Foundation Models

| Provider | Model | Best For |
|----------|-------|----------|
| **Anthropic** | Claude 3 (Opus, Sonnet, Haiku) | Complex reasoning, coding |
| **Amazon** | Titan Text, Titan Embeddings | General purpose, embeddings |
| **Meta** | Llama 2, Llama 3 | Open-source flexibility |
| **AI21 Labs** | Jurassic-2 | Text generation |
| **Cohere** | Command, Embed | Enterprise search, RAG |
| **Stability AI** | Stable Diffusion | Image generation |

#### Bedrock Example: Text Generation

```python
import boto3
import json

# Initialize Bedrock client
bedrock = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-east-1"
)

# Call Claude model
response = bedrock.invoke_model(
    modelId="anthropic.claude-3-sonnet-20240229-v1:0",
    contentType="application/json",
    accept="application/json",
    body=json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1024,
        "messages": [
            {
                "role": "user",
                "content": "Analyze this logistics data and suggest optimizations..."
            }
        ]
    })
)

result = json.loads(response["body"].read())
print(result["content"][0]["text"])
```

#### Bedrock Example: Embeddings for RAG

```python
import boto3
import json

bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

def get_embeddings(text: str) -> list:
    """Generate embeddings using Amazon Titan."""
    response = bedrock.invoke_model(
        modelId="amazon.titan-embed-text-v1",
        contentType="application/json",
        accept="application/json",
        body=json.dumps({"inputText": text})
    )
    result = json.loads(response["body"].read())
    return result["embedding"]

# Generate embeddings for documents
doc_embedding = get_embeddings("Fleet utilization report for Q4 2024...")
query_embedding = get_embeddings("What was our delivery performance?")
```

#### Bedrock Knowledge Bases (RAG)

```python
import boto3

# Create knowledge base with your documents
bedrock_agent = boto3.client("bedrock-agent", region_name="us-east-1")

# Query knowledge base
response = bedrock_agent.retrieve_and_generate(
    input={
        "text": "What are the main causes of delivery delays?"
    },
    retrieveAndGenerateConfiguration={
        "type": "KNOWLEDGE_BASE",
        "knowledgeBaseConfiguration": {
            "knowledgeBaseId": "your-kb-id",
            "modelArn": "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-sonnet"
        }
    }
)

print(response["output"]["text"])
```

#### Learning Resources

| Resource | Link | Description |
|----------|------|-------------|
| **Bedrock Workshop** | catalog.workshops.aws/bedrock | Hands-on labs |
| **Bedrock User Guide** | docs.aws.amazon.com/bedrock | Official documentation |
| **Generative AI on AWS** | aws.amazon.com/generative-ai | Overview and use cases |

---

### Other AWS ML Services

#### Pre-trained AI Services (No ML Expertise Required)

| Service | Full Name | Use Case | Algorithm Equivalent |
|---------|-----------|----------|---------------------|
| **Rekognition** | Amazon Rekognition | Image/video analysis | CNN |
| **Comprehend** | Amazon Comprehend | NLP, sentiment analysis | Transformers, LSTM |
| **Textract** | Amazon Textract | Document OCR | CNN + NLP |
| **Transcribe** | Amazon Transcribe | Speech-to-text | RNN, Transformers |
| **Polly** | Amazon Polly | Text-to-speech | Neural TTS |
| **Translate** | Amazon Translate | Language translation | Transformers |
| **Forecast** | Amazon Forecast | Time series forecasting | DeepAR, ARIMA |
| **Personalize** | Amazon Personalize | Recommendations | Collaborative filtering |
| **Fraud Detector** | Amazon Fraud Detector | Fraud detection | Ensemble methods |
| **Kendra** | Amazon Kendra | Enterprise search | Semantic search, RAG |

#### Amazon Forecast Example (Time Series)

```python
import boto3

forecast = boto3.client("forecast", region_name="us-east-1")

# Create predictor (automatically selects best algorithm)
response = forecast.create_auto_predictor(
    PredictorName="demand_forecast",
    ForecastHorizon=30,  # Predict 30 days ahead
    ForecastFrequency="D",  # Daily
    DataConfig={
        "DatasetGroupArn": "arn:aws:forecast:...:dataset-group/my_data"
    }
)

# Algorithms Amazon Forecast uses internally:
# - DeepAR+ (deep learning)
# - Prophet
# - ARIMA
# - ETS (Exponential Smoothing)
# - NPTS (Non-Parametric Time Series)
```

---

## Microsoft Azure ML Services

### Azure Machine Learning

**Full Name:** Azure Machine Learning (Azure ML)

**What It Is:**
- Enterprise-grade ML platform for the complete ML lifecycle
- Integrates with familiar tools (VS Code, GitHub, MLflow)
- Strong enterprise security and governance

#### Key Components

| Component | Purpose | Use Case |
|-----------|---------|----------|
| **Azure ML Studio** | Web-based IDE | Visual ML development |
| **Designer** | Drag-and-drop ML | No-code model building |
| **AutoML** | Automatic model selection | Best model without coding |
| **Notebooks** | Jupyter in Azure | Experimentation |
| **Compute Clusters** | Managed compute | Scalable training |
| **Managed Endpoints** | Model deployment | Production inference |
| **Pipelines** | ML workflows | Automated retraining |
| **Data Labeling** | Dataset annotation | Create training data |
| **Responsible AI** | Model explainability | Fairness, interpretability |

#### Built-in Algorithms (Matching Our Project)

| Our Algorithm | Azure ML Equivalent | Service |
|---------------|--------------------| --------|
| **XGBoost** | XGBoost, LightGBM | AutoML, Custom training |
| **Random Forest** | Random Forest | AutoML, Designer |
| **Gradient Boosting** | LightGBM, CatBoost | AutoML |
| **K-Means** | K-Means Clustering | Designer, SDK |
| **Linear Regression** | Linear Regression | AutoML, Designer |
| **Logistic Regression** | Logistic Regression | AutoML, Designer |

#### Azure ML SDK v2 Example: Training XGBoost

```python
from azure.ai.ml import MLClient, command, Input
from azure.identity import DefaultAzureCredential
from azure.ai.ml.entities import Environment

# Connect to workspace
ml_client = MLClient(
    DefaultAzureCredential(),
    subscription_id="your-subscription-id",
    resource_group_name="your-resource-group",
    workspace_name="your-workspace"
)

# Define training job
job = command(
    code="./src",
    command="python train_xgboost.py --data ${{inputs.training_data}}",
    inputs={
        "training_data": Input(
            type="uri_folder",
            path="azureml://datastores/workspaceblobstore/paths/data/"
        )
    },
    environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu@latest",
    compute="cpu-cluster",
    display_name="xgboost-training",
    experiment_name="demand-forecasting"
)

# Submit job
returned_job = ml_client.jobs.create_or_update(job)
print(f"Job URL: {returned_job.studio_url}")
```

#### Azure AutoML Example

```python
from azure.ai.ml import automl, Input
from azure.ai.ml.constants import AssetTypes

# Configure AutoML for classification
classification_job = automl.classification(
    compute="cpu-cluster",
    experiment_name="lead-scoring-automl",
    training_data=Input(
        type=AssetTypes.MLTABLE,
        path="azureml://datastores/workspaceblobstore/paths/leads/"
    ),
    target_column_name="converted",
    primary_metric="AUC_weighted",
    n_cross_validations=5,
    enable_model_explainability=True
)

# Set limits
classification_job.set_limits(
    max_trials=20,
    max_concurrent_trials=4,
    timeout_minutes=60
)

# Enable specific algorithms
classification_job.set_training(
    allowed_training_algorithms=[
        "LightGBM", "XGBoostClassifier", "RandomForest", "LogisticRegression"
    ]
)

# Submit
returned_job = ml_client.jobs.create_or_update(classification_job)
```

#### Azure ML Designer (No-Code)

```
┌─────────────────────────────────────────────────────────────┐
│                    Azure ML Designer                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   [Import Data] ──→ [Select Columns] ──→ [Clean Data]      │
│                                              │              │
│                                              ▼              │
│                                    [Split Data 70/30]       │
│                                         │      │            │
│                                         ▼      ▼            │
│                                    [Train]  [Test]          │
│                                        │       │            │
│                                        ▼       │            │
│                               [Two-Class Boosted            │
│                                Decision Tree]               │
│                                        │       │            │
│                                        ▼       ▼            │
│                                    [Score Model]            │
│                                         │                   │
│                                         ▼                   │
│                                  [Evaluate Model]           │
│                                         │                   │
│                                         ▼                   │
│                               [Deploy as Web Service]       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

#### Learning Resources

| Resource | Link | Description |
|----------|------|-------------|
| **Azure ML Learning Path** | learn.microsoft.com/azure/machine-learning | Microsoft Learn modules |
| **Azure ML Examples** | github.com/Azure/azureml-examples | Code samples |
| **DP-100 Certification** | learn.microsoft.com/certifications/azure-data-scientist | Data Scientist certification |
| **Azure ML Documentation** | docs.microsoft.com/azure/machine-learning | Official docs |

---

### Azure OpenAI Service

**Full Name:** Azure OpenAI Service

**What It Is:**
- Enterprise access to OpenAI models (GPT-4, GPT-3.5, DALL-E, etc.)
- Azure security, compliance, and regional availability
- Same models as OpenAI but with enterprise features

#### Available Models

| Model | Use Case | Description |
|-------|----------|-------------|
| **GPT-4** | Complex reasoning | Most capable language model |
| **GPT-4 Turbo** | Long context | 128K token context window |
| **GPT-4o** | Multimodal | Text + images |
| **GPT-3.5 Turbo** | Fast responses | Cost-effective for simpler tasks |
| **text-embedding-ada-002** | Embeddings | Vector representations for RAG |
| **DALL-E 3** | Image generation | Create images from text |
| **Whisper** | Speech-to-text | Audio transcription |

#### Azure OpenAI Example

```python
from openai import AzureOpenAI

# Initialize client
client = AzureOpenAI(
    api_key="your-api-key",
    api_version="2024-02-15-preview",
    azure_endpoint="https://your-resource.openai.azure.com/"
)

# Chat completion
response = client.chat.completions.create(
    model="gpt-4",  # Your deployment name
    messages=[
        {"role": "system", "content": "You are a logistics analyst."},
        {"role": "user", "content": "Analyze fleet performance trends..."}
    ],
    temperature=0.7,
    max_tokens=1000
)

print(response.choices[0].message.content)
```

#### Azure OpenAI with RAG (On Your Data)

```python
from openai import AzureOpenAI

client = AzureOpenAI(
    api_key="your-api-key",
    api_version="2024-02-15-preview",
    azure_endpoint="https://your-resource.openai.azure.com/"
)

# Query with your indexed data
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "What were our top delivery issues last quarter?"}],
    extra_body={
        "data_sources": [{
            "type": "azure_search",
            "parameters": {
                "endpoint": "https://your-search.search.windows.net",
                "index_name": "logistics-docs",
                "authentication": {
                    "type": "api_key",
                    "key": "your-search-key"
                }
            }
        }]
    }
)
```

---

### Azure Cognitive Services

**Full Name:** Azure Cognitive Services (now Azure AI Services)

**What It Is:**
- Pre-built AI APIs for common tasks
- No ML expertise required
- Easy REST API integration

#### Service Categories

| Category | Services | Algorithm Equivalent |
|----------|----------|---------------------|
| **Vision** | Computer Vision, Custom Vision, Face | CNN |
| **Speech** | Speech-to-Text, Text-to-Speech | Transformers, RNN |
| **Language** | Text Analytics, Translator, LUIS | Transformers, NLP |
| **Decision** | Anomaly Detector, Personalizer | Time series, RL |
| **Search** | Cognitive Search | Semantic search, RAG |

#### Text Analytics Example (Sentiment)

```python
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

# Initialize client
credential = AzureKeyCredential("your-key")
client = TextAnalyticsClient(
    endpoint="https://your-resource.cognitiveservices.azure.com/",
    credential=credential
)

# Analyze sentiment
documents = [
    "The delivery was on time and the driver was professional.",
    "Package arrived damaged and customer service was unhelpful."
]

response = client.analyze_sentiment(documents)

for doc in response:
    print(f"Sentiment: {doc.sentiment}")
    print(f"Positive: {doc.confidence_scores.positive:.2f}")
    print(f"Negative: {doc.confidence_scores.negative:.2f}")
```

---

## Google Cloud ML Services

### Vertex AI

**Full Name:** Vertex AI

**What It Is:**
- Unified ML platform combining AutoML and custom training
- Integration with BigQuery and other GCP services
- Access to Google's foundation models (Gemini, PaLM)

#### Key Components

| Component | Purpose | Use Case |
|-----------|---------|----------|
| **Vertex AI Workbench** | Managed notebooks | Development environment |
| **Vertex AI Training** | Custom model training | Train on GPUs/TPUs |
| **Vertex AI AutoML** | Automated ML | No-code model building |
| **Vertex AI Prediction** | Model deployment | Online/batch inference |
| **Vertex AI Pipelines** | ML workflows | Orchestrate ML steps |
| **Vertex AI Feature Store** | Feature management | Centralized features |
| **Vertex AI Model Registry** | Model versioning | Track experiments |
| **Vertex AI Matching Engine** | Vector search | Similarity search, RAG |
| **Generative AI Studio** | LLM experimentation | Prompt engineering |

#### Built-in Algorithms

| Our Algorithm | Vertex AI Equivalent | Service |
|---------------|---------------------|---------|
| **XGBoost** | XGBoost (pre-built container) | Custom Training |
| **Random Forest** | Scikit-learn containers | Custom Training |
| **Gradient Boosting** | XGBoost, TensorFlow | AutoML, Custom |
| **K-Means** | AutoML Tables (Clustering) | AutoML |
| **Linear Regression** | AutoML Tables | AutoML |
| **Deep Learning** | TensorFlow, PyTorch | Custom Training |

#### Vertex AI Custom Training Example

```python
from google.cloud import aiplatform

# Initialize
aiplatform.init(
    project="your-project-id",
    location="us-central1"
)

# Create custom training job
job = aiplatform.CustomTrainingJob(
    display_name="xgboost-demand-forecast",
    script_path="train.py",
    container_uri="us-docker.pkg.dev/vertex-ai/training/xgboost-cpu.1-6:latest",
    requirements=["pandas", "scikit-learn"],
    model_serving_container_image_uri="us-docker.pkg.dev/vertex-ai/prediction/xgboost-cpu.1-6:latest"
)

# Run training
model = job.run(
    dataset=None,  # Can use Vertex AI Dataset
    model_display_name="demand-forecast-model",
    args=["--data-path", "gs://your-bucket/data/"],
    replica_count=1,
    machine_type="n1-standard-4"
)

# Deploy model
endpoint = model.deploy(
    deployed_model_display_name="demand-forecast-endpoint",
    machine_type="n1-standard-2",
    min_replica_count=1,
    max_replica_count=3
)
```

#### Vertex AI AutoML Example

```python
from google.cloud import aiplatform

aiplatform.init(project="your-project", location="us-central1")

# Create dataset
dataset = aiplatform.TabularDataset.create(
    display_name="customer-churn-data",
    gcs_source="gs://your-bucket/churn_data.csv"
)

# Train AutoML model
job = aiplatform.AutoMLTabularTrainingJob(
    display_name="churn-prediction-automl",
    optimization_prediction_type="classification",
    optimization_objective="maximize-au-roc"
)

model = job.run(
    dataset=dataset,
    target_column="churned",
    training_fraction_split=0.8,
    validation_fraction_split=0.1,
    test_fraction_split=0.1,
    budget_milli_node_hours=1000,  # Training budget
    model_display_name="churn-predictor"
)

# Deploy
endpoint = model.deploy(machine_type="n1-standard-2")
```

#### Vertex AI Generative AI (Gemini)

```python
import vertexai
from vertexai.generative_models import GenerativeModel

# Initialize
vertexai.init(project="your-project", location="us-central1")

# Load Gemini model
model = GenerativeModel("gemini-1.5-pro")

# Generate content
response = model.generate_content(
    "Analyze this logistics data and provide recommendations: "
    "On-time delivery: 94%, Fleet utilization: 78%, "
    "Average delivery time: 2.3 days"
)

print(response.text)
```

#### Vertex AI Embeddings for RAG

```python
from vertexai.language_models import TextEmbeddingModel

# Load embedding model
model = TextEmbeddingModel.from_pretrained("textembedding-gecko@003")

# Generate embeddings
texts = [
    "Fleet maintenance schedule for Q4",
    "Driver performance metrics report",
    "Fuel efficiency optimization strategies"
]

embeddings = model.get_embeddings(texts)

for text, embedding in zip(texts, embeddings):
    print(f"Text: {text[:30]}...")
    print(f"Embedding dimension: {len(embedding.values)}")  # 768 dimensions
```

#### Learning Resources

| Resource | Link | Description |
|----------|------|-------------|
| **Vertex AI Quickstarts** | cloud.google.com/vertex-ai/docs/start | Getting started |
| **ML on GCP Specialization** | coursera.org/specializations/machine-learning-tensorflow-gcp | Coursera course |
| **Google Cloud Skills Boost** | cloudskillsboost.google | Hands-on labs |
| **Vertex AI Samples** | github.com/GoogleCloudPlatform/vertex-ai-samples | Code examples |

---

### BigQuery ML

**Full Name:** BigQuery Machine Learning (BQML)

**What It Is:**
- Train ML models using SQL directly in BigQuery
- No need to export data or learn Python
- Great for analysts familiar with SQL

#### Supported Models

| Model Type | SQL Command | Our Algorithm Equivalent |
|------------|-------------|-------------------------|
| Linear Regression | `LINEAR_REG` | Linear Regression |
| Logistic Regression | `LOGISTIC_REG` | Logistic Regression |
| K-Means Clustering | `KMEANS` | K-Means |
| XGBoost | `BOOSTED_TREE_CLASSIFIER/REGRESSOR` | XGBoost |
| Random Forest | `RANDOM_FOREST_CLASSIFIER/REGRESSOR` | Random Forest |
| Deep Neural Network | `DNN_CLASSIFIER/REGRESSOR` | MLP |
| AutoML Tables | `AUTOML_CLASSIFIER/REGRESSOR` | AutoML |
| Time Series | `ARIMA_PLUS` | ARIMA, Prophet |

#### BigQuery ML Example: XGBoost Classification

```sql
-- Create XGBoost model for lead scoring
CREATE OR REPLACE MODEL `project.dataset.lead_scorer`
OPTIONS(
    model_type='BOOSTED_TREE_CLASSIFIER',
    input_label_cols=['converted'],
    max_iterations=50,
    learn_rate=0.1,
    max_tree_depth=6,
    subsample=0.8,
    colsample_bytree=0.8
) AS
SELECT
    company_size,
    industry,
    lead_source,
    days_since_contact,
    engagement_score,
    converted
FROM `project.dataset.leads_training`;

-- Evaluate model
SELECT *
FROM ML.EVALUATE(MODEL `project.dataset.lead_scorer`);

-- Make predictions
SELECT
    lead_id,
    company_name,
    predicted_converted,
    predicted_converted_probs
FROM ML.PREDICT(
    MODEL `project.dataset.lead_scorer`,
    (SELECT * FROM `project.dataset.new_leads`)
);
```

#### BigQuery ML Example: K-Means Clustering

```sql
-- Create customer segments
CREATE OR REPLACE MODEL `project.dataset.customer_segments`
OPTIONS(
    model_type='KMEANS',
    num_clusters=5,
    standardize_features=TRUE
) AS
SELECT
    contract_value,
    tenure_months,
    satisfaction_score,
    monthly_shipments,
    support_tickets
FROM `project.dataset.customers`;

-- Assign customers to segments
SELECT
    customer_id,
    company_name,
    CENTROID_ID as segment
FROM ML.PREDICT(
    MODEL `project.dataset.customer_segments`,
    (SELECT * FROM `project.dataset.customers`)
);
```

#### BigQuery ML Example: Time Series Forecasting

```sql
-- Create demand forecast model
CREATE OR REPLACE MODEL `project.dataset.demand_forecast`
OPTIONS(
    model_type='ARIMA_PLUS',
    time_series_timestamp_col='date',
    time_series_data_col='shipment_volume',
    time_series_id_col='region',
    horizon=30  -- Forecast 30 days
) AS
SELECT
    date,
    region,
    shipment_volume
FROM `project.dataset.daily_shipments`;

-- Generate forecast
SELECT *
FROM ML.FORECAST(
    MODEL `project.dataset.demand_forecast`,
    STRUCT(30 AS horizon, 0.9 AS confidence_level)
);
```

---

### Google Cloud AI APIs

#### Pre-built AI Services

| Service | Use Case | Algorithm Equivalent |
|---------|----------|---------------------|
| **Vision AI** | Image analysis | CNN |
| **Video AI** | Video analysis | CNN + RNN |
| **Natural Language AI** | Text analysis, NER | Transformers |
| **Speech-to-Text** | Audio transcription | Transformers |
| **Text-to-Speech** | Voice synthesis | Neural TTS |
| **Translation AI** | Language translation | Transformers |
| **Document AI** | Document processing | CNN + Transformers |
| **Recommendations AI** | Product recommendations | Collaborative filtering |

---

## Algorithm to Cloud Service Mapping

### Complete Mapping Table

| Algorithm | AWS | Azure | GCP |
|-----------|-----|-------|-----|
| **XGBoost** | SageMaker XGBoost | Azure ML AutoML | Vertex AI, BQML |
| **Gradient Boosting** | SageMaker XGBoost | LightGBM in Azure ML | Vertex AI |
| **Random Forest** | SageMaker Random Cut Forest | Azure ML Designer | Vertex AI, BQML |
| **K-Means** | SageMaker K-Means | Azure ML Clustering | Vertex AI, BQML |
| **Linear Regression** | SageMaker Linear Learner | Azure ML AutoML | Vertex AI, BQML |
| **Logistic Regression** | SageMaker Linear Learner | Azure ML AutoML | Vertex AI, BQML |
| **Time Series** | Amazon Forecast | Azure ML AutoML | Vertex AI, BQML ARIMA |
| **CNN** | SageMaker + TensorFlow | Azure ML + PyTorch | Vertex AI + TensorFlow |
| **RNN/LSTM** | SageMaker + TensorFlow | Azure ML + PyTorch | Vertex AI + TensorFlow |
| **Transformers** | Bedrock, SageMaker | Azure OpenAI | Vertex AI Gemini |
| **LLMs** | Bedrock (Claude, Titan) | Azure OpenAI (GPT-4) | Vertex AI (Gemini) |
| **Embeddings** | Bedrock Titan Embeddings | Azure OpenAI Embeddings | Vertex AI Embeddings |
| **RAG** | Bedrock Knowledge Bases | Azure AI Search + OpenAI | Vertex AI Search |

### Use Case to Service Mapping

| Use Case | AWS | Azure | GCP |
|----------|-----|-------|-----|
| **Demand Forecasting** | Amazon Forecast, SageMaker | Azure ML AutoML | Vertex AI, BQML |
| **Lead Scoring** | SageMaker Autopilot | Azure ML AutoML | Vertex AI AutoML |
| **Churn Prediction** | SageMaker | Azure ML | Vertex AI |
| **Customer Segmentation** | SageMaker K-Means | Azure ML Clustering | BQML K-Means |
| **Document Processing** | Textract | Document Intelligence | Document AI |
| **Sentiment Analysis** | Comprehend | Text Analytics | Natural Language AI |
| **Chatbot/AI Assistant** | Bedrock Agents | Azure OpenAI | Vertex AI Agents |
| **Image Analysis** | Rekognition | Computer Vision | Vision AI |

---

## Comparison Matrix

### Pricing Comparison (Approximate)

| Service Type | AWS | Azure | GCP |
|--------------|-----|-------|-----|
| **Training (GPU/hr)** | $3.06 (ml.p3.2xlarge) | $3.06 (NC6s_v3) | $2.48 (n1 + V100) |
| **Inference (CPU/hr)** | $0.05 (ml.t2.medium) | $0.05 (B2s) | $0.04 (n1-standard-2) |
| **AutoML (hr)** | ~$15-20/hr | ~$15-20/hr | ~$20/hr |
| **LLM (1K tokens)** | $0.003-0.06 | $0.002-0.06 | $0.00025-0.0025 |
| **Embeddings (1K tokens)** | $0.0001 | $0.0001 | $0.00025 |

*Prices vary by region and change frequently. Check official pricing pages.*

### Feature Comparison

| Feature | AWS | Azure | GCP |
|---------|-----|-------|-----|
| **AutoML** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Pre-built APIs** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Custom Training** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **LLM Access** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **SQL-based ML** | ⭐⭐⭐ (Redshift ML) | ⭐⭐ | ⭐⭐⭐⭐⭐ (BQML) |
| **MLOps** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Enterprise Security** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Documentation** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

### When to Choose Each Provider

| Choose AWS When | Choose Azure When | Choose GCP When |
|-----------------|-------------------|-----------------|
| Already using AWS ecosystem | Microsoft/Office 365 shop | Using BigQuery for analytics |
| Need widest model selection (Bedrock) | Enterprise compliance requirements | Want SQL-based ML (BQML) |
| Require mature MLOps (SageMaker) | Need Azure OpenAI (GPT-4) | Need Gemini models |
| Serverless ML (Lambda + SageMaker) | Hybrid cloud scenarios | Research/innovation focus |
| E-commerce/retail focus | Healthcare/finance compliance | Data engineering focus |

---

## Cost Considerations

### Cost Optimization Strategies

#### 1. Use Spot/Preemptible Instances for Training

| Provider | Feature | Savings |
|----------|---------|---------|
| AWS | Spot Instances | Up to 90% |
| Azure | Spot VMs | Up to 90% |
| GCP | Preemptible VMs | Up to 80% |

#### 2. Right-size Inference Endpoints

```python
# AWS: Use auto-scaling
predictor = estimator.deploy(
    initial_instance_count=1,
    instance_type="ml.t2.medium",  # Start small
    auto_scaling_config={
        "min_instances": 1,
        "max_instances": 10,
        "target_tracking_scaling_policy_configuration": {
            "TargetValue": 70.0,
            "PredefinedMetricSpecification": {
                "PredefinedMetricType": "SageMakerVariantInvocationsPerInstance"
            }
        }
    }
)
```

#### 3. Use Serverless Inference

| Provider | Service | Use Case |
|----------|---------|----------|
| AWS | SageMaker Serverless | Intermittent traffic |
| Azure | Container Instances | Low-volume inference |
| GCP | Cloud Run | Event-driven inference |

#### 4. Batch Processing for Non-Real-Time

```python
# AWS Batch Transform (cheaper than real-time)
transformer = model.transformer(
    instance_count=1,
    instance_type="ml.m5.xlarge",
    output_path=f"s3://{bucket}/predictions/"
)
transformer.transform(
    data=f"s3://{bucket}/batch-input/",
    content_type="text/csv"
)
```

---

## Getting Started Guides

### Quick Start: AWS SageMaker

```bash
# 1. Install AWS CLI and configure
pip install awscli boto3 sagemaker
aws configure

# 2. Create notebook instance (AWS Console)
# Go to SageMaker → Notebook instances → Create

# 3. Clone examples
git clone https://github.com/aws/amazon-sagemaker-examples.git

# 4. Run your first training job
# Open intro_to_xgboost.ipynb
```

### Quick Start: Azure ML

```bash
# 1. Install Azure CLI and ML extension
pip install azure-ai-ml azure-identity
az login

# 2. Create workspace (CLI)
az ml workspace create --name my-workspace --resource-group my-rg

# 3. Clone examples
git clone https://github.com/Azure/azureml-examples.git

# 4. Run quickstart notebook
# Open sdk/python/jobs/single-step/xgboost
```

### Quick Start: Vertex AI

```bash
# 1. Install gcloud CLI
pip install google-cloud-aiplatform

# 2. Authenticate
gcloud auth login
gcloud config set project your-project-id

# 3. Enable APIs
gcloud services enable aiplatform.googleapis.com

# 4. Clone examples
git clone https://github.com/GoogleCloudPlatform/vertex-ai-samples.git

# 5. Run quickstart
# Open notebooks/official/automl/
```

---

## Glossary of Cloud ML Terms

### General Cloud ML Terms

| Term | Full Form | Definition |
|------|-----------|------------|
| **MLOps** | Machine Learning Operations | DevOps practices for ML |
| **AutoML** | Automated Machine Learning | Auto model selection and tuning |
| **SaaS** | Software as a Service | Fully managed cloud software |
| **PaaS** | Platform as a Service | Managed platform for development |
| **IaaS** | Infrastructure as a Service | Virtual machines, storage |
| **SDK** | Software Development Kit | Libraries for programmatic access |
| **API** | Application Programming Interface | Interface to interact with services |
| **REST** | Representational State Transfer | Web API architectural style |
| **GPU** | Graphics Processing Unit | Hardware accelerator for ML |
| **TPU** | Tensor Processing Unit | Google's custom ML accelerator |

### AWS-Specific Terms

| Term | Full Form | Definition |
|------|-----------|------------|
| **S3** | Simple Storage Service | Object storage |
| **EC2** | Elastic Compute Cloud | Virtual machines |
| **IAM** | Identity and Access Management | Permissions and roles |
| **VPC** | Virtual Private Cloud | Isolated network |
| **ARN** | Amazon Resource Name | Unique resource identifier |
| **ECR** | Elastic Container Registry | Docker container storage |
| **EKS** | Elastic Kubernetes Service | Managed Kubernetes |
| **Lambda** | AWS Lambda | Serverless compute |

### Azure-Specific Terms

| Term | Full Form | Definition |
|------|-----------|------------|
| **Blob** | Binary Large Object | Azure object storage |
| **AKS** | Azure Kubernetes Service | Managed Kubernetes |
| **ACR** | Azure Container Registry | Docker container storage |
| **RBAC** | Role-Based Access Control | Permissions system |
| **ARM** | Azure Resource Manager | Infrastructure management |
| **Cosmos DB** | Azure Cosmos DB | Global NoSQL database |

### GCP-Specific Terms

| Term | Full Form | Definition |
|------|-----------|------------|
| **GCS** | Google Cloud Storage | Object storage |
| **GKE** | Google Kubernetes Engine | Managed Kubernetes |
| **GCR** | Google Container Registry | Docker container storage |
| **BigQuery** | Google BigQuery | Serverless data warehouse |
| **Pub/Sub** | Cloud Pub/Sub | Messaging service |
| **Dataflow** | Google Cloud Dataflow | Stream/batch processing |

### Model Deployment Terms

| Term | Definition |
|------|------------|
| **Endpoint** | URL where model accepts prediction requests |
| **Inference** | Making predictions with trained model |
| **Real-time** | Predictions returned immediately (ms) |
| **Batch** | Predictions on large datasets (minutes/hours) |
| **Cold Start** | Delay when serverless instance spins up |
| **Latency** | Time between request and response |
| **Throughput** | Number of predictions per second |
| **Model Artifact** | Saved model files (weights, config) |
| **Container** | Packaged model with dependencies |
| **A/B Testing** | Comparing model versions in production |
| **Shadow Mode** | Running new model alongside old without serving |
| **Canary Deployment** | Gradual rollout to percentage of traffic |

---

## Project Application Examples

### Example 1: Demand Forecasting on Cloud

| Component | AWS | Azure | GCP |
|-----------|-----|-------|-----|
| **Data Storage** | S3 | Blob Storage | GCS |
| **Training** | SageMaker XGBoost | Azure ML AutoML | Vertex AI |
| **Deployment** | SageMaker Endpoint | Azure ML Endpoint | Vertex AI Endpoint |
| **Scheduling** | EventBridge + Lambda | Azure Functions | Cloud Scheduler |
| **Monitoring** | CloudWatch | Azure Monitor | Cloud Monitoring |

### Example 2: Lead Scoring Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                    Lead Scoring on AWS                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  [CRM Data] ──→ [S3] ──→ [SageMaker Processing]                │
│                              │                                  │
│                              ▼                                  │
│                    [SageMaker Autopilot]                        │
│                              │                                  │
│                              ▼                                  │
│                    [Best Model Selected]                        │
│                              │                                  │
│                              ▼                                  │
│                    [SageMaker Endpoint]                         │
│                              │                                  │
│                              ▼                                  │
│  [API Gateway] ──→ [Lambda] ──→ [Return Lead Score]           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Example 3: Customer Insights with GenAI

```
┌─────────────────────────────────────────────────────────────────┐
│             Customer Insights on Azure                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  [Customer Feedback] ──→ [Blob Storage]                        │
│                              │                                  │
│                              ▼                                  │
│                    [Azure AI Search]                            │
│                    (Index & Embeddings)                         │
│                              │                                  │
│                              ▼                                  │
│                    [Azure OpenAI GPT-4]                         │
│                    (RAG with customer data)                     │
│                              │                                  │
│                              ▼                                  │
│  [Power BI Dashboard] ←── [Insights & Summaries]               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Summary

### Key Takeaways

1. **All three cloud providers offer equivalent ML capabilities** for the algorithms in our project
2. **AutoML** can automatically find the best algorithm (XGBoost, Random Forest, etc.)
3. **SQL-based ML (BigQuery ML)** is great for analysts without Python expertise
4. **Generative AI services** (Bedrock, Azure OpenAI, Vertex AI) enable RAG and AI assistants
5. **Choose based on existing cloud investment** and specific feature needs

### Recommended Learning Path

1. **Start with AutoML** - Quick wins without deep ML knowledge
2. **Learn managed training** - Custom models when AutoML isn't enough
3. **Master deployment** - Get models into production
4. **Implement MLOps** - CI/CD for ML models
5. **Add Generative AI** - Enhance with LLMs and RAG

---

*Document created for Penske Logistics Analytics Project*
*Last updated: February 2025*
