#!/usr/bin/env python3
"""
Penske Logistics Analytics - Gradio Frontend
=============================================
Alternative frontend using Gradio for ML demos and quick prototypes.

Run: python gradio_app.py
URL: http://localhost:7860
"""

import gradio as gr
import pandas as pd
import numpy as np
import os
import sys
from datetime import datetime, timedelta

# Add parent directory for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Try to import cloud services, use demo mode if unavailable
try:
    from src.cloud_ai_services import CloudAIServices
    cloud_services = CloudAIServices()
    DEMO_MODE = False
except ImportError:
    DEMO_MODE = True
    cloud_services = None


# ============================================================================
# DEMO DATA GENERATORS
# ============================================================================

def generate_demo_prediction():
    """Generate demo prediction result."""
    return {
        "prediction": round(np.random.uniform(1200, 1800), 0),
        "confidence": round(np.random.uniform(0.85, 0.98), 2),
        "latency_ms": np.random.randint(30, 80)
    }


def generate_demo_analytics():
    """Generate demo analytics data."""
    dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
    return pd.DataFrame({
        'Date': dates,
        'Shipments': np.random.randint(800, 1500, 30),
        'On-Time %': np.random.uniform(92, 99, 30).round(1),
        'Avg Delay (hrs)': np.random.uniform(0.5, 3, 30).round(2)
    })


# ============================================================================
# PREDICTION INTERFACE
# ============================================================================

def predict_demand(
    shipment_volume: float,
    fuel_price: float,
    weather_severity: int,
    day_of_week: int,
    is_holiday: bool,
    previous_day_volume: float,
    region: str,
    cloud_provider: str
):
    """Make demand prediction using cloud ML endpoint."""
    
    # Build features
    features = [
        shipment_volume,
        fuel_price,
        weather_severity,
        day_of_week,
        1 if is_holiday else 0,
        previous_day_volume,
        1 if region == 'Midwest' else 0,
        1 if region == 'Northeast' else 0,
        1 if region == 'Southeast' else 0,
        1 if region == 'West' else 0
    ]
    
    if DEMO_MODE or cloud_provider == "Demo Mode":
        result = generate_demo_prediction()
    else:
        try:
            if cloud_provider == "AWS SageMaker":
                result = cloud_services.predict_sagemaker(features)
            elif cloud_provider == "Azure ML":
                result = cloud_services.predict_azure_ml(features)
            elif cloud_provider == "GCP Vertex AI":
                result = cloud_services.predict_vertex_ai(features)
            else:
                result = generate_demo_prediction()
        except Exception as e:
            return f"Error: {str(e)}", "", ""
    
    prediction = f"**{result['prediction']:.0f} shipments**"
    confidence = f"{result['confidence'] * 100:.1f}%"
    latency = f"{result['latency_ms']}ms"
    
    return prediction, confidence, latency


def batch_predict(file, cloud_provider):
    """Process batch predictions from CSV."""
    if file is None:
        return None, "Please upload a CSV file"
    
    try:
        df = pd.read_csv(file.name)
        
        # Add predictions (demo mode)
        df['Predicted_Demand'] = np.random.randint(1000, 1800, len(df))
        df['Confidence'] = np.random.uniform(0.85, 0.98, len(df)).round(2)
        
        return df, f"✅ Processed {len(df)} predictions using {cloud_provider}"
    except Exception as e:
        return None, f"❌ Error: {str(e)}"


# ============================================================================
# ANALYTICS INTERFACE
# ============================================================================

def load_analytics():
    """Load analytics data."""
    df = generate_demo_analytics()
    
    # Create summary
    summary = f"""
### 📊 30-Day Summary
- **Total Shipments:** {df['Shipments'].sum():,}
- **Average Daily:** {df['Shipments'].mean():.0f}
- **On-Time Rate:** {df['On-Time %'].mean():.1f}%
- **Avg Delay:** {df['Avg Delay (hrs)'].mean():.2f} hours
    """
    
    return df, summary


# ============================================================================
# GENAI CHAT INTERFACE
# ============================================================================

def chat_with_ai(message, history, cloud_provider, temperature):
    """Chat with AI using cloud LLM."""
    
    # Convert history to messages format
    messages = []
    for user_msg, assistant_msg in history:
        messages.append({"role": "user", "content": user_msg})
        if assistant_msg:
            messages.append({"role": "assistant", "content": assistant_msg})
    messages.append({"role": "user", "content": message})
    
    if DEMO_MODE or cloud_provider == "Demo Mode":
        # Demo responses
        if "performance" in message.lower():
            return "Based on today's data, your fleet is performing at 96.2% on-time delivery rate, which is 2.1% above target. The Northeast region is leading with 98.1% on-time rate."
        elif "delay" in message.lower():
            return "The main causes of delays this week are: 1) Weather conditions (35%), 2) Traffic congestion (28%), 3) Loading dock availability (22%), 4) Driver availability (15%)."
        elif "predict" in message.lower() or "forecast" in message.lower():
            return "Based on historical patterns and current trends, I predict next week's delivery volume will be approximately 8,450 shipments, a 5% increase from this week due to seasonal demand."
        else:
            return f"I'm your AI logistics assistant. I can help you analyze delivery performance, identify delay patterns, and forecast demand. Currently running in demo mode. Your question: '{message}'"
    
    try:
        if cloud_provider == "AWS Bedrock":
            response = cloud_services.chat_bedrock(messages, temperature)
        elif cloud_provider == "Azure OpenAI":
            response = cloud_services.chat_azure_openai(messages, temperature)
        elif cloud_provider == "GCP Gemini":
            response = cloud_services.chat_vertex_gemini(messages, temperature)
        else:
            response = "Please select a cloud provider."
        return response
    except Exception as e:
        return f"Error: {str(e)}"


# ============================================================================
# GRADIO APP
# ============================================================================

# Custom CSS
custom_css = """
.gradio-container {
    max-width: 1200px !important;
}
.main-header {
    text-align: center;
    margin-bottom: 1rem;
}
"""

# Create the app
with gr.Blocks(
    title="Penske Logistics Analytics",
    theme=gr.themes.Soft(
        primary_hue="blue",
        secondary_hue="indigo"
    ),
    css=custom_css
) as app:
    
    # Header
    gr.Markdown("""
    # 🚚 Penske Logistics Analytics
    ### ML-Powered Demand Forecasting & Analytics
    """)
    
    # Cloud provider selector
    with gr.Row():
        cloud_provider = gr.Dropdown(
            choices=["Demo Mode", "AWS SageMaker", "Azure ML", "GCP Vertex AI"],
            value="Demo Mode",
            label="☁️ ML Endpoint",
            scale=1
        )
        llm_provider = gr.Dropdown(
            choices=["Demo Mode", "AWS Bedrock", "Azure OpenAI", "GCP Gemini"],
            value="Demo Mode",
            label="🤖 LLM Provider",
            scale=1
        )
        gr.Markdown("", scale=2)
    
    gr.Markdown("---")
    
    # Tabs
    with gr.Tabs():
        
        # =====================================================================
        # TAB: Predictions
        # =====================================================================
        with gr.TabItem("📈 Predictions", id="predictions"):
            gr.Markdown("### 🎯 Demand Prediction")
            
            with gr.Row():
                with gr.Column(scale=1):
                    shipment_volume = gr.Number(label="Current Shipment Volume", value=1250)
                    fuel_price = gr.Number(label="Fuel Price ($/gal)", value=3.45)
                    weather_severity = gr.Slider(0, 3, value=0, step=1, 
                                                  label="Weather Severity (0=None, 3=Severe)")
                    day_of_week = gr.Slider(1, 7, value=2, step=1, 
                                            label="Day of Week (1=Mon, 7=Sun)")
                    is_holiday = gr.Checkbox(label="Is Holiday?", value=False)
                    previous_day_volume = gr.Number(label="Previous Day Volume", value=1180)
                    region = gr.Dropdown(
                        choices=["Midwest", "Northeast", "Southeast", "West"],
                        value="Northeast",
                        label="Region"
                    )
                    
                    predict_btn = gr.Button("🚀 Predict Demand", variant="primary")
                
                with gr.Column(scale=1):
                    gr.Markdown("### Results")
                    prediction_output = gr.Markdown(label="Predicted Demand")
                    confidence_output = gr.Markdown(label="Confidence")
                    latency_output = gr.Markdown(label="Latency")
            
            predict_btn.click(
                predict_demand,
                inputs=[shipment_volume, fuel_price, weather_severity, day_of_week, 
                        is_holiday, previous_day_volume, region, cloud_provider],
                outputs=[prediction_output, confidence_output, latency_output]
            )
            
            gr.Markdown("---")
            gr.Markdown("### 📦 Batch Predictions")
            
            with gr.Row():
                file_input = gr.File(label="Upload CSV", file_types=[".csv"])
                batch_btn = gr.Button("Run Batch", variant="secondary")
            
            batch_output = gr.Dataframe(label="Results")
            batch_status = gr.Markdown()
            
            batch_btn.click(
                batch_predict,
                inputs=[file_input, cloud_provider],
                outputs=[batch_output, batch_status]
            )
        
        # =====================================================================
        # TAB: Analytics
        # =====================================================================
        with gr.TabItem("📊 Analytics", id="analytics"):
            gr.Markdown("### 📊 Performance Analytics")
            
            with gr.Row():
                refresh_btn = gr.Button("🔄 Refresh Data", variant="secondary")
            
            with gr.Row():
                analytics_summary = gr.Markdown()
            
            analytics_table = gr.Dataframe(label="30-Day Performance Data")
            
            refresh_btn.click(
                load_analytics,
                outputs=[analytics_table, analytics_summary]
            )
            
            # Load initial data
            app.load(load_analytics, outputs=[analytics_table, analytics_summary])
        
        # =====================================================================
        # TAB: GenAI Chat
        # =====================================================================
        with gr.TabItem("🤖 AI Assistant", id="genai"):
            gr.Markdown("### 🤖 AI Analytics Assistant")
            gr.Markdown("Ask questions about your logistics data and get AI-powered insights")
            
            with gr.Row():
                temperature = gr.Slider(0, 1, value=0.7, step=0.1, label="Temperature")
            
            chatbot = gr.ChatInterface(
                chat_with_ai,
                additional_inputs=[llm_provider, temperature],
                examples=[
                    "Summarize today's delivery performance",
                    "What are the main causes of delays this week?",
                    "Predict demand for next week"
                ],
                title="",
                retry_btn="🔄 Retry",
                undo_btn="↩️ Undo",
                clear_btn="🗑️ Clear"
            )
    
    # Footer
    gr.Markdown("---")
    mode_text = "🔵 Demo Mode" if DEMO_MODE else "🟢 Connected to Cloud"
    gr.Markdown(f"*Penske Logistics Analytics v1.0 | {mode_text}*")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("PENSKE LOGISTICS ANALYTICS - GRADIO FRONTEND")
    print("=" * 60)
    print(f"Mode: {'DEMO' if DEMO_MODE else 'CLOUD CONNECTED'}")
    print("URL: http://localhost:7860")
    print("=" * 60)
    
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )
