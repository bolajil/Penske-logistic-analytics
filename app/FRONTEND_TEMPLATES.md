# Frontend Templates for Cloud ML Deployments
## Streamlit, Gradio, and React Applications

> **Purpose**: Ready-to-use frontend templates that connect to your cloud ML endpoints
> **Supports**: AWS, Azure, GCP backends with Streamlit, Gradio, and React frontends

---

## Table of Contents
1. [Overview & Comparison](#1-overview--comparison)
2. [Streamlit Templates](#2-streamlit-templates)
3. [Gradio Templates](#3-gradio-templates)
4. [React Templates](#4-react-templates)
5. [Cloud Deployment Guides](#5-cloud-deployment-guides)
6. [Configuration](#6-configuration)

---

## 1. Overview & Comparison

### Which Frontend to Choose?

| Criteria | Streamlit | Gradio | React |
|----------|-----------|--------|-------|
| **Best For** | Dashboards, analytics | ML demos, quick prototypes | Production apps |
| **Learning Curve** | Low | Very Low | Medium-High |
| **Customization** | Medium | Low | High |
| **Performance** | Good | Good | Excellent |
| **Mobile Support** | Limited | Limited | Excellent |
| **Deployment** | Easy | Very Easy | Requires build |
| **Language** | Python | Python | JavaScript/TypeScript |

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND OPTIONS                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │  Streamlit   │  │   Gradio     │  │    React     │           │
│  │  (Python)    │  │  (Python)    │  │ (JavaScript) │           │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘           │
│         │                 │                 │                    │
│         └────────────┬────┴────────────────┘                    │
│                      │                                           │
│                      ▼                                           │
│              ┌───────────────┐                                   │
│              │   API Layer   │                                   │
│              └───────┬───────┘                                   │
│                      │                                           │
│    ┌─────────────────┼─────────────────┐                        │
│    │                 │                 │                         │
│    ▼                 ▼                 ▼                         │
│ ┌──────┐        ┌──────┐        ┌──────┐                        │
│ │ AWS  │        │Azure │        │ GCP  │                        │
│ │Endpt │        │Endpt │        │Endpt │                        │
│ └──────┘        └──────┘        └──────┘                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Streamlit Templates

### 2.1 Project Structure

```
streamlit-app/
├── app.py                    # Main application
├── pages/
│   ├── 1_Predictions.py      # ML predictions page
│   ├── 2_Analytics.py        # Analytics dashboard
│   └── 3_GenAI.py            # GenAI chat interface
├── components/
│   ├── __init__.py
│   ├── api_client.py         # Cloud API client
│   └── charts.py             # Visualization components
├── config/
│   └── config.yaml           # Configuration
├── requirements.txt
├── Dockerfile
└── .streamlit/
    └── config.toml           # Streamlit config
```

### 2.2 Main Application

```python
# app.py
"""
🚀 ML Dashboard - Streamlit Frontend
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Works with AWS, Azure, or GCP backends
"""

import streamlit as st
import yaml
from pathlib import Path

# Page config
st.set_page_config(
    page_title="ML Analytics Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load config
@st.cache_data
def load_config():
    config_path = Path("config/config.yaml")
    if config_path.exists():
        with open(config_path) as f:
            return yaml.safe_load(f)
    return {}

config = load_config()

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/150x50?text=Logo", width=150)
    st.markdown("---")
    
    # Cloud provider selection
    cloud_provider = st.selectbox(
        "☁️ Cloud Provider",
        ["AWS", "Azure", "GCP"],
        index=0
    )
    
    st.markdown("---")
    st.markdown("### 📊 Quick Stats")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Models", "5")
    with col2:
        st.metric("Endpoints", "3")

# Main content
st.markdown('<p class="main-header">🚀 ML Analytics Dashboard</p>', unsafe_allow_html=True)

# Hero metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Total Predictions",
        value="12,543",
        delta="↑ 12%"
    )

with col2:
    st.metric(
        label="Avg Response Time",
        value="45ms",
        delta="↓ 5ms"
    )

with col3:
    st.metric(
        label="Model Accuracy",
        value="94.2%",
        delta="↑ 0.3%"
    )

with col4:
    st.metric(
        label="Active Users",
        value="234",
        delta="↑ 15"
    )

st.markdown("---")

# Navigation cards
st.markdown("### 🎯 Quick Actions")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="metric-card">
        <h3>📈 Predictions</h3>
        <p>Make real-time predictions using ML models</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Go to Predictions", key="pred"):
        st.switch_page("pages/1_Predictions.py")

with col2:
    st.markdown("""
    <div class="metric-card">
        <h3>📊 Analytics</h3>
        <p>View dashboards and performance metrics</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Go to Analytics", key="analytics"):
        st.switch_page("pages/2_Analytics.py")

with col3:
    st.markdown("""
    <div class="metric-card">
        <h3>🤖 GenAI Chat</h3>
        <p>Ask questions about your data</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Go to GenAI", key="genai"):
        st.switch_page("pages/3_GenAI.py")

# Footer
st.markdown("---")
st.markdown(f"*Connected to: **{cloud_provider}** | Last updated: Just now*")
```

### 2.3 Predictions Page

```python
# pages/1_Predictions.py
"""
📈 Predictions Page
"""

import streamlit as st
import pandas as pd
from components.api_client import get_prediction

st.set_page_config(page_title="Predictions", page_icon="📈", layout="wide")

st.title("📈 ML Predictions")
st.markdown("Make predictions using your deployed models")

# Model selection
col1, col2 = st.columns([1, 2])

with col1:
    model_type = st.selectbox(
        "Select Model",
        ["Delivery Time Prediction", "Churn Classification", "Demand Forecast"]
    )
    
    task_type = st.radio(
        "Task Type",
        ["Regression", "Classification"]
    )

with col2:
    st.markdown("### Input Features")
    
    if model_type == "Delivery Time Prediction":
        col_a, col_b = st.columns(2)
        with col_a:
            distance = st.number_input("Distance (miles)", min_value=0.0, value=50.0)
            weight = st.number_input("Weight (kg)", min_value=0.0, value=100.0)
        with col_b:
            hour = st.slider("Hour of Day", 0, 23, 10)
            day = st.selectbox("Day of Week", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
        
        features = {
            "distance_miles": distance,
            "weight_kg": weight,
            "hour": hour,
            "day_of_week": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"].index(day)
        }

st.markdown("---")

# Prediction button
if st.button("🚀 Get Prediction", type="primary", use_container_width=True):
    with st.spinner("Making prediction..."):
        try:
            # Get cloud provider from session state or default
            cloud_provider = st.session_state.get("cloud_provider", "aws")
            
            result = get_prediction(
                features=list(features.values()),
                cloud_provider=cloud_provider,
                model_type=task_type.lower()
            )
            
            # Display result
            st.success("✅ Prediction Complete!")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if task_type == "Regression":
                    st.metric("Predicted Value", f"{result['prediction']:.2f} hours")
                else:
                    st.metric("Predicted Class", result['prediction'])
            with col2:
                st.metric("Confidence", f"{result.get('confidence', 0.95) * 100:.1f}%")
            with col3:
                st.metric("Latency", f"{result.get('latency_ms', 45)}ms")
            
            # Feature importance (if available)
            if 'feature_importance' in result:
                st.markdown("### Feature Importance")
                importance_df = pd.DataFrame(result['feature_importance'])
                st.bar_chart(importance_df.set_index('feature')['importance'])
                
        except Exception as e:
            st.error(f"❌ Prediction failed: {str(e)}")

# Batch predictions
st.markdown("---")
st.markdown("### 📦 Batch Predictions")

uploaded_file = st.file_uploader("Upload CSV for batch predictions", type=['csv'])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.dataframe(df.head())
    
    if st.button("Run Batch Prediction"):
        with st.spinner("Processing batch..."):
            progress = st.progress(0)
            for i in range(100):
                progress.progress(i + 1)
            st.success(f"✅ Processed {len(df)} predictions!")
            
            # Show sample results
            df['prediction'] = [2.5] * len(df)  # Placeholder
            st.dataframe(df)
            
            # Download button
            csv = df.to_csv(index=False)
            st.download_button(
                "📥 Download Results",
                csv,
                "predictions.csv",
                "text/csv"
            )
```

### 2.4 GenAI Chat Page

```python
# pages/3_GenAI.py
"""
🤖 GenAI Chat Interface
"""

import streamlit as st
from components.api_client import chat_with_llm

st.set_page_config(page_title="GenAI Chat", page_icon="🤖", layout="wide")

st.title("🤖 GenAI Assistant")
st.markdown("Ask questions about your data and get AI-powered insights")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I'm your AI analytics assistant. Ask me anything about your logistics data, predictions, or performance metrics."}
    ]

# Model selection
with st.sidebar:
    st.markdown("### 🔧 Settings")
    
    cloud_provider = st.selectbox(
        "Cloud Provider",
        ["AWS (Bedrock)", "Azure (OpenAI)", "GCP (Gemini)"]
    )
    
    model = st.selectbox(
        "Model",
        ["Claude 3 Sonnet", "GPT-4", "Gemini 1.5 Pro"]
    )
    
    temperature = st.slider("Temperature", 0.0, 1.0, 0.7)
    
    st.markdown("---")
    
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask a question..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = chat_with_llm(
                    messages=st.session_state.messages,
                    cloud_provider=cloud_provider.split()[0].lower(),
                    model=model,
                    temperature=temperature
                )
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                error_msg = f"❌ Error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Quick prompts
st.markdown("---")
st.markdown("### 💡 Quick Prompts")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📊 Summarize today's performance"):
        st.session_state.messages.append({"role": "user", "content": "Summarize today's delivery performance"})
        st.rerun()

with col2:
    if st.button("🔍 Find delayed deliveries"):
        st.session_state.messages.append({"role": "user", "content": "What are the main causes of delayed deliveries this week?"})
        st.rerun()

with col3:
    if st.button("📈 Predict next week"):
        st.session_state.messages.append({"role": "user", "content": "What is the predicted delivery volume for next week?"})
        st.rerun()
```

### 2.5 API Client Component

```python
# components/api_client.py
"""
🔌 Universal API Client for Cloud ML Endpoints
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Supports AWS, Azure, and GCP
"""

import os
import json
import requests
import yaml
from typing import List, Dict, Any
from pathlib import Path

# Load config
def load_config():
    config_path = Path("config/config.yaml")
    if config_path.exists():
        with open(config_path) as f:
            return yaml.safe_load(f)
    return {}

CONFIG = load_config()


class AWSClient:
    """AWS SageMaker/Bedrock client"""
    
    def __init__(self):
        self.endpoint_url = os.getenv("AWS_ENDPOINT_URL", CONFIG.get("aws", {}).get("endpoint_url"))
        self.bedrock_url = os.getenv("AWS_BEDROCK_URL", CONFIG.get("aws", {}).get("bedrock_url"))
        self.api_key = os.getenv("AWS_API_KEY")
    
    def predict(self, features: List[float]) -> Dict:
        response = requests.post(
            self.endpoint_url,
            json={"features": features},
            headers={"x-api-key": self.api_key}
        )
        return response.json()
    
    def chat(self, messages: List[Dict], model: str, temperature: float) -> str:
        import boto3
        
        bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")
        
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1024,
            "temperature": temperature,
            "messages": [{"role": m["role"], "content": m["content"]} for m in messages if m["role"] != "system"]
        })
        
        response = bedrock.invoke_model(
            modelId="anthropic.claude-3-sonnet-20240229-v1:0",
            body=body
        )
        
        result = json.loads(response["body"].read())
        return result["content"][0]["text"]


class AzureClient:
    """Azure ML/OpenAI client"""
    
    def __init__(self):
        self.endpoint_url = os.getenv("AZURE_ENDPOINT_URL", CONFIG.get("azure", {}).get("endpoint_url"))
        self.openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_key = os.getenv("AZURE_API_KEY")
        self.openai_key = os.getenv("AZURE_OPENAI_KEY")
    
    def predict(self, features: List[float]) -> Dict:
        response = requests.post(
            self.endpoint_url,
            json={"features": features},
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        return response.json()
    
    def chat(self, messages: List[Dict], model: str, temperature: float) -> str:
        from openai import AzureOpenAI
        
        client = AzureOpenAI(
            api_key=self.openai_key,
            api_version="2024-02-15-preview",
            azure_endpoint=self.openai_endpoint
        )
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=temperature
        )
        
        return response.choices[0].message.content


class GCPClient:
    """GCP Vertex AI/Gemini client"""
    
    def __init__(self):
        self.endpoint_url = os.getenv("GCP_ENDPOINT_URL", CONFIG.get("gcp", {}).get("endpoint_url"))
        self.project_id = os.getenv("GCP_PROJECT_ID", CONFIG.get("gcp", {}).get("project_id"))
        self.region = os.getenv("GCP_REGION", "us-central1")
    
    def predict(self, features: List[float]) -> Dict:
        from google.cloud import aiplatform
        
        aiplatform.init(project=self.project_id, location=self.region)
        endpoint = aiplatform.Endpoint(self.endpoint_url)
        
        predictions = endpoint.predict(instances=[features])
        return {"prediction": predictions.predictions[0]}
    
    def chat(self, messages: List[Dict], model: str, temperature: float) -> str:
        import vertexai
        from vertexai.generative_models import GenerativeModel
        
        vertexai.init(project=self.project_id, location=self.region)
        model = GenerativeModel("gemini-1.5-pro")
        
        # Convert messages to Gemini format
        prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
        response = model.generate_content(prompt)
        
        return response.text


# Factory function
def get_client(cloud_provider: str):
    clients = {
        "aws": AWSClient,
        "azure": AzureClient,
        "gcp": GCPClient
    }
    return clients.get(cloud_provider.lower(), AWSClient)()


# Public API
def get_prediction(
    features: List[float],
    cloud_provider: str = "aws",
    model_type: str = "regression"
) -> Dict:
    """
    Get prediction from cloud endpoint.
    
    Usage:
        result = get_prediction([1.0, 2.0, 3.0], cloud_provider="aws")
    """
    import time
    start = time.time()
    
    client = get_client(cloud_provider)
    result = client.predict(features)
    
    result["latency_ms"] = int((time.time() - start) * 1000)
    return result


def chat_with_llm(
    messages: List[Dict],
    cloud_provider: str = "aws",
    model: str = "Claude 3 Sonnet",
    temperature: float = 0.7
) -> str:
    """
    Chat with LLM via cloud provider.
    
    Usage:
        response = chat_with_llm([{"role": "user", "content": "Hello"}], cloud_provider="aws")
    """
    client = get_client(cloud_provider)
    return client.chat(messages, model, temperature)
```

### 2.6 Streamlit Requirements & Config

```txt
# requirements.txt
streamlit>=1.30.0
pandas>=2.0.0
numpy>=1.24.0
plotly>=5.18.0
requests>=2.31.0
pyyaml>=6.0
boto3>=1.33.0
openai>=1.0.0
google-cloud-aiplatform>=1.38.0
vertexai>=1.38.0
python-dotenv>=1.0.0
```

```yaml
# config/config.yaml
app:
  name: "ML Analytics Dashboard"
  version: "1.0.0"

aws:
  endpoint_url: "https://your-sagemaker-endpoint.amazonaws.com"
  bedrock_url: "https://bedrock-runtime.us-east-1.amazonaws.com"
  region: "us-east-1"

azure:
  endpoint_url: "https://your-endpoint.azureml.com"
  openai_endpoint: "https://your-openai.openai.azure.com"
  region: "eastus"

gcp:
  endpoint_url: "projects/YOUR_PROJECT/locations/us-central1/endpoints/ENDPOINT_ID"
  project_id: "your-project-id"
  region: "us-central1"
```

```toml
# .streamlit/config.toml
[theme]
primaryColor = "#667eea"
backgroundColor = "#0e1117"
secondaryBackgroundColor = "#262730"
textColor = "#fafafa"
font = "sans serif"

[server]
port = 8501
enableCORS = false
enableXsrfProtection = true
```

---

## 3. Gradio Templates

### 3.1 Project Structure

```
gradio-app/
├── app.py                    # Main application
├── interfaces/
│   ├── __init__.py
│   ├── prediction.py         # Prediction interface
│   ├── analytics.py          # Analytics interface
│   └── genai.py              # GenAI interface
├── utils/
│   ├── __init__.py
│   └── api_client.py         # Cloud API client
├── config.yaml
├── requirements.txt
└── Dockerfile
```

### 3.2 Main Application

```python
# app.py
"""
🚀 ML Dashboard - Gradio Frontend
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Works with AWS, Azure, or GCP backends
"""

import gradio as gr
from interfaces.prediction import create_prediction_interface
from interfaces.genai import create_genai_interface
from interfaces.analytics import create_analytics_interface

# Custom CSS
custom_css = """
.gradio-container {
    max-width: 1200px !important;
}
.main-header {
    text-align: center;
    margin-bottom: 2rem;
}
.tab-nav button {
    font-size: 1.1rem !important;
}
"""

# Create main app with tabs
with gr.Blocks(
    title="ML Analytics Dashboard",
    theme=gr.themes.Soft(
        primary_hue="indigo",
        secondary_hue="purple"
    ),
    css=custom_css
) as app:
    
    # Header
    gr.Markdown("""
    # 🚀 ML Analytics Dashboard
    ### Powered by Cloud ML - AWS | Azure | GCP
    """)
    
    # Cloud provider selector
    with gr.Row():
        cloud_provider = gr.Dropdown(
            choices=["AWS", "Azure", "GCP"],
            value="AWS",
            label="☁️ Cloud Provider",
            scale=1
        )
        gr.Markdown("", scale=3)  # Spacer
    
    gr.Markdown("---")
    
    # Tabs
    with gr.Tabs():
        with gr.TabItem("📈 Predictions", id="predictions"):
            create_prediction_interface(cloud_provider)
        
        with gr.TabItem("📊 Analytics", id="analytics"):
            create_analytics_interface()
        
        with gr.TabItem("🤖 GenAI Chat", id="genai"):
            create_genai_interface(cloud_provider)
    
    # Footer
    gr.Markdown("---")
    gr.Markdown("*ML Analytics Dashboard v1.0 | Connected to cloud endpoints*")


# Launch
if __name__ == "__main__":
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )
```

### 3.3 Prediction Interface

```python
# interfaces/prediction.py
"""
📈 Prediction Interface
"""

import gradio as gr
import pandas as pd
from utils.api_client import get_prediction

def create_prediction_interface(cloud_provider_dropdown):
    """Create the prediction tab interface"""
    
    def predict(distance, weight, hour, day, cloud_provider):
        """Make prediction"""
        features = [distance, weight, hour, day]
        
        try:
            result = get_prediction(
                features=features,
                cloud_provider=cloud_provider.lower()
            )
            
            prediction = result.get("prediction", 0)
            confidence = result.get("confidence", 0.95)
            latency = result.get("latency_ms", 45)
            
            return (
                f"**{prediction:.2f} hours**",
                f"{confidence * 100:.1f}%",
                f"{latency}ms",
                "✅ Prediction successful!"
            )
        except Exception as e:
            return ("Error", "N/A", "N/A", f"❌ {str(e)}")
    
    def batch_predict(file, cloud_provider):
        """Batch prediction from CSV"""
        if file is None:
            return None, "Please upload a CSV file"
        
        try:
            df = pd.read_csv(file.name)
            # Placeholder: Add predictions
            df["prediction"] = [2.5] * len(df)
            df["confidence"] = [0.95] * len(df)
            
            return df, f"✅ Processed {len(df)} predictions"
        except Exception as e:
            return None, f"❌ {str(e)}"
    
    with gr.Column():
        gr.Markdown("### 🎯 Single Prediction")
        
        with gr.Row():
            with gr.Column(scale=1):
                distance = gr.Number(label="Distance (miles)", value=50)
                weight = gr.Number(label="Weight (kg)", value=100)
                hour = gr.Slider(0, 23, value=10, step=1, label="Hour of Day")
                day = gr.Dropdown(
                    choices=list(range(7)),
                    value=0,
                    label="Day of Week (0=Mon)"
                )
                
                predict_btn = gr.Button("🚀 Predict", variant="primary")
            
            with gr.Column(scale=1):
                prediction_output = gr.Markdown(label="Prediction")
                confidence_output = gr.Markdown(label="Confidence")
                latency_output = gr.Markdown(label="Latency")
                status_output = gr.Markdown(label="Status")
        
        predict_btn.click(
            predict,
            inputs=[distance, weight, hour, day, cloud_provider_dropdown],
            outputs=[prediction_output, confidence_output, latency_output, status_output]
        )
        
        gr.Markdown("---")
        gr.Markdown("### 📦 Batch Prediction")
        
        with gr.Row():
            file_input = gr.File(label="Upload CSV", file_types=[".csv"])
            batch_btn = gr.Button("Run Batch", variant="secondary")
        
        batch_output = gr.Dataframe(label="Results")
        batch_status = gr.Markdown()
        
        batch_btn.click(
            batch_predict,
            inputs=[file_input, cloud_provider_dropdown],
            outputs=[batch_output, batch_status]
        )
```

### 3.4 GenAI Chat Interface

```python
# interfaces/genai.py
"""
🤖 GenAI Chat Interface
"""

import gradio as gr
from utils.api_client import chat_with_llm

def create_genai_interface(cloud_provider_dropdown):
    """Create the GenAI chat interface"""
    
    def chat(message, history, cloud_provider, temperature):
        """Process chat message"""
        # Convert history to messages format
        messages = []
        for user_msg, assistant_msg in history:
            messages.append({"role": "user", "content": user_msg})
            if assistant_msg:
                messages.append({"role": "assistant", "content": assistant_msg})
        messages.append({"role": "user", "content": message})
        
        try:
            response = chat_with_llm(
                messages=messages,
                cloud_provider=cloud_provider.lower()
            )
            return response
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    with gr.Column():
        gr.Markdown("### 🤖 AI Assistant")
        gr.Markdown("Ask questions about your data and get AI-powered insights")
        
        with gr.Row():
            temperature = gr.Slider(
                0, 1, value=0.7, step=0.1,
                label="Temperature"
            )
        
        chatbot = gr.ChatInterface(
            chat,
            additional_inputs=[cloud_provider_dropdown, temperature],
            examples=[
                "Summarize today's delivery performance",
                "What are the main causes of delays?",
                "Predict demand for next week"
            ],
            title="",
            retry_btn="🔄 Retry",
            undo_btn="↩️ Undo",
            clear_btn="🗑️ Clear"
        )
```

### 3.5 Gradio Requirements

```txt
# requirements.txt
gradio>=4.15.0
pandas>=2.0.0
numpy>=1.24.0
plotly>=5.18.0
requests>=2.31.0
pyyaml>=6.0
boto3>=1.33.0
openai>=1.0.0
google-cloud-aiplatform>=1.38.0
python-dotenv>=1.0.0
```

---

## 4. React Templates

### 4.1 Project Structure

```
react-app/
├── src/
│   ├── App.tsx
│   ├── main.tsx
│   ├── index.css
│   ├── components/
│   │   ├── Layout/
│   │   │   ├── Navbar.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── Footer.tsx
│   │   ├── Predictions/
│   │   │   ├── PredictionForm.tsx
│   │   │   └── PredictionResult.tsx
│   │   ├── Analytics/
│   │   │   ├── Dashboard.tsx
│   │   │   └── Charts.tsx
│   │   └── GenAI/
│   │       ├── ChatInterface.tsx
│   │       └── MessageBubble.tsx
│   ├── hooks/
│   │   ├── useApi.ts
│   │   └── useChat.ts
│   ├── services/
│   │   ├── api.ts
│   │   └── cloudProviders.ts
│   ├── types/
│   │   └── index.ts
│   └── config/
│       └── config.ts
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
├── Dockerfile
└── .env.example
```

### 4.2 Main Application

```tsx
// src/App.tsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Predictions from './pages/Predictions';
import Analytics from './pages/Analytics';
import GenAIChat from './pages/GenAIChat';
import { CloudProviderProvider } from './context/CloudProviderContext';

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <CloudProviderProvider>
        <BrowserRouter>
          <Toaster position="top-right" />
          <Layout>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/predictions" element={<Predictions />} />
              <Route path="/analytics" element={<Analytics />} />
              <Route path="/chat" element={<GenAIChat />} />
            </Routes>
          </Layout>
        </BrowserRouter>
      </CloudProviderProvider>
    </QueryClientProvider>
  );
}

export default App;
```

### 4.3 API Service

```typescript
// src/services/api.ts
import axios from 'axios';
import { CloudProvider, PredictionRequest, PredictionResponse, ChatMessage } from '../types';

const API_ENDPOINTS = {
  aws: import.meta.env.VITE_AWS_ENDPOINT || 'http://localhost:8000/aws',
  azure: import.meta.env.VITE_AZURE_ENDPOINT || 'http://localhost:8000/azure',
  gcp: import.meta.env.VITE_GCP_ENDPOINT || 'http://localhost:8000/gcp',
};

class APIService {
  private cloudProvider: CloudProvider = 'aws';

  setCloudProvider(provider: CloudProvider) {
    this.cloudProvider = provider;
  }

  private getBaseUrl(): string {
    return API_ENDPOINTS[this.cloudProvider];
  }

  async predict(features: number[]): Promise<PredictionResponse> {
    const startTime = Date.now();
    
    const response = await axios.post<PredictionResponse>(
      `${this.getBaseUrl()}/predict`,
      { features }
    );
    
    return {
      ...response.data,
      latencyMs: Date.now() - startTime,
    };
  }

  async chat(messages: ChatMessage[]): Promise<string> {
    const response = await axios.post<{ response: string }>(
      `${this.getBaseUrl()}/chat`,
      { messages }
    );
    
    return response.data.response;
  }

  async getAnalytics(): Promise<any> {
    const response = await axios.get(`${this.getBaseUrl()}/analytics`);
    return response.data;
  }
}

export const apiService = new APIService();
```

### 4.4 Prediction Form Component

```tsx
// src/components/Predictions/PredictionForm.tsx
import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { apiService } from '../../services/api';
import { toast } from 'react-hot-toast';

interface FormData {
  distance: number;
  weight: number;
  hour: number;
  dayOfWeek: number;
}

export default function PredictionForm() {
  const [formData, setFormData] = useState<FormData>({
    distance: 50,
    weight: 100,
    hour: 10,
    dayOfWeek: 0,
  });

  const mutation = useMutation({
    mutationFn: (features: number[]) => apiService.predict(features),
    onSuccess: (data) => {
      toast.success('Prediction successful!');
    },
    onError: (error) => {
      toast.error(`Prediction failed: ${error}`);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const features = [
      formData.distance,
      formData.weight,
      formData.hour,
      formData.dayOfWeek,
    ];
    mutation.mutate(features);
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <h2 className="text-2xl font-bold mb-6 text-gray-800">
        📈 Make Prediction
      </h2>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Distance (miles)
            </label>
            <input
              type="number"
              value={formData.distance}
              onChange={(e) => setFormData({ ...formData, distance: +e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Weight (kg)
            </label>
            <input
              type="number"
              value={formData.weight}
              onChange={(e) => setFormData({ ...formData, weight: +e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Hour of Day
            </label>
            <input
              type="range"
              min="0"
              max="23"
              value={formData.hour}
              onChange={(e) => setFormData({ ...formData, hour: +e.target.value })}
              className="w-full"
            />
            <span className="text-sm text-gray-500">{formData.hour}:00</span>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Day of Week
            </label>
            <select
              value={formData.dayOfWeek}
              onChange={(e) => setFormData({ ...formData, dayOfWeek: +e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
            >
              {['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'].map((day, i) => (
                <option key={day} value={i}>{day}</option>
              ))}
            </select>
          </div>
        </div>
        
        <button
          type="submit"
          disabled={mutation.isPending}
          className="w-full py-3 px-4 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold rounded-lg hover:from-indigo-700 hover:to-purple-700 transition-all disabled:opacity-50"
        >
          {mutation.isPending ? (
            <span className="flex items-center justify-center">
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Predicting...
            </span>
          ) : (
            '🚀 Get Prediction'
          )}
        </button>
      </form>
      
      {/* Result Display */}
      {mutation.data && (
        <div className="mt-6 p-4 bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg border border-green-200">
          <h3 className="font-semibold text-green-800 mb-2">✅ Prediction Result</h3>
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-700">
                {mutation.data.prediction?.toFixed(2)} hrs
              </div>
              <div className="text-sm text-gray-600">Predicted Time</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-700">
                {((mutation.data.confidence || 0.95) * 100).toFixed(1)}%
              </div>
              <div className="text-sm text-gray-600">Confidence</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-700">
                {mutation.data.latencyMs}ms
              </div>
              <div className="text-sm text-gray-600">Latency</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
```

### 4.5 Chat Interface Component

```tsx
// src/components/GenAI/ChatInterface.tsx
import { useState, useRef, useEffect } from 'react';
import { useMutation } from '@tanstack/react-query';
import { apiService } from '../../services/api';
import MessageBubble from './MessageBubble';
import { ChatMessage } from '../../types';

export default function ChatInterface() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: 'assistant',
      content: "Hello! I'm your AI analytics assistant. Ask me anything about your logistics data.",
    },
  ]);
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const mutation = useMutation({
    mutationFn: (messages: ChatMessage[]) => apiService.chat(messages),
    onSuccess: (response) => {
      setMessages((prev) => [...prev, { role: 'assistant', content: response }]);
    },
    onError: (error) => {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: `❌ Error: ${error}` },
      ]);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const newMessage: ChatMessage = { role: 'user', content: input };
    const updatedMessages = [...messages, newMessage];
    setMessages(updatedMessages);
    setInput('');
    mutation.mutate(updatedMessages);
  };

  const quickPrompts = [
    "Summarize today's performance",
    "What caused the most delays?",
    "Predict next week's demand",
  ];

  return (
    <div className="flex flex-col h-[600px] bg-white rounded-xl shadow-lg">
      {/* Header */}
      <div className="p-4 border-b bg-gradient-to-r from-indigo-600 to-purple-600 rounded-t-xl">
        <h2 className="text-xl font-bold text-white">🤖 AI Assistant</h2>
        <p className="text-indigo-100 text-sm">Powered by Cloud AI</p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message, index) => (
          <MessageBubble key={index} message={message} />
        ))}
        {mutation.isPending && (
          <div className="flex items-center space-x-2 text-gray-500">
            <div className="animate-bounce">●</div>
            <div className="animate-bounce delay-100">●</div>
            <div className="animate-bounce delay-200">●</div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Quick Prompts */}
      <div className="px-4 py-2 border-t flex gap-2 overflow-x-auto">
        {quickPrompts.map((prompt) => (
          <button
            key={prompt}
            onClick={() => setInput(prompt)}
            className="px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded-full text-sm whitespace-nowrap transition-colors"
          >
            {prompt}
          </button>
        ))}
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="p-4 border-t">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            disabled={mutation.isPending}
          />
          <button
            type="submit"
            disabled={mutation.isPending || !input.trim()}
            className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 transition-colors"
          >
            Send
          </button>
        </div>
      </form>
    </div>
  );
}
```

### 4.6 Package.json

```json
{
  "name": "ml-dashboard-react",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext ts,tsx"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.21.0",
    "@tanstack/react-query": "^5.17.0",
    "axios": "^1.6.5",
    "react-hot-toast": "^2.4.1",
    "recharts": "^2.10.3",
    "lucide-react": "^0.303.0",
    "clsx": "^2.1.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.45",
    "@types/react-dom": "^18.2.18",
    "@vitejs/plugin-react": "^4.2.1",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.33",
    "tailwindcss": "^3.4.1",
    "typescript": "^5.3.3",
    "vite": "^5.0.11"
  }
}
```

---

## 5. Cloud Deployment Guides

### 5.1 Deploy Streamlit

**AWS (App Runner / ECS)**
```bash
# Build and push to ECR
docker build -t ml-dashboard-streamlit .
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $ECR_URL
docker tag ml-dashboard-streamlit:latest $ECR_URL/ml-dashboard-streamlit:latest
docker push $ECR_URL/ml-dashboard-streamlit:latest

# Deploy to App Runner
aws apprunner create-service \
  --service-name ml-dashboard \
  --source-configuration '{
    "ImageRepository": {
      "ImageIdentifier": "'$ECR_URL'/ml-dashboard-streamlit:latest",
      "ImageRepositoryType": "ECR"
    }
  }'
```

**Azure (Container Apps)**
```bash
az containerapp create \
  --name ml-dashboard \
  --resource-group myResourceGroup \
  --image $ACR_URL/ml-dashboard-streamlit:latest \
  --target-port 8501 \
  --ingress external
```

**GCP (Cloud Run)**
```bash
gcloud run deploy ml-dashboard \
  --image gcr.io/$PROJECT_ID/ml-dashboard-streamlit \
  --platform managed \
  --port 8501 \
  --allow-unauthenticated
```

### 5.2 Deploy Gradio

**Hugging Face Spaces (Easiest)**
```bash
# Push to Hugging Face
huggingface-cli login
huggingface-cli repo create ml-dashboard --type space --space-sdk gradio
git remote add space https://huggingface.co/spaces/username/ml-dashboard
git push space main
```

**Cloud Run / App Runner**
```dockerfile
# Dockerfile for Gradio
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 7860
CMD ["python", "app.py"]
```

### 5.3 Deploy React

**Vercel (Recommended)**
```bash
npm i -g vercel
vercel
```

**AWS Amplify**
```bash
amplify init
amplify add hosting
amplify publish
```

**Azure Static Web Apps**
```bash
az staticwebapp create \
  --name ml-dashboard \
  --resource-group myResourceGroup \
  --source https://github.com/user/ml-dashboard \
  --branch main \
  --app-location "/" \
  --output-location "dist"
```

---

## 6. Configuration

### Environment Variables

```bash
# .env
# AWS
VITE_AWS_ENDPOINT=https://your-api.execute-api.us-east-1.amazonaws.com
AWS_ENDPOINT_URL=https://your-sagemaker-endpoint.amazonaws.com
AWS_API_KEY=your-api-key

# Azure
VITE_AZURE_ENDPOINT=https://your-function.azurewebsites.net
AZURE_ENDPOINT_URL=https://your-ml-endpoint.azureml.com
AZURE_OPENAI_ENDPOINT=https://your-openai.openai.azure.com
AZURE_OPENAI_KEY=your-openai-key

# GCP
VITE_GCP_ENDPOINT=https://your-cloudrun-url.run.app
GCP_PROJECT_ID=your-project-id
GCP_ENDPOINT_URL=projects/xxx/locations/us-central1/endpoints/xxx
```

---

## Quick Start Commands

```bash
# Streamlit
cd streamlit-app
pip install -r requirements.txt
streamlit run app.py

# Gradio
cd gradio-app
pip install -r requirements.txt
python app.py

# React
cd react-app
npm install
npm run dev
```

---

*Last Updated: January 2024*
*Author: Penske Logistics Analytics Team*
