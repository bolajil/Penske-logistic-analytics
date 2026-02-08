#!/usr/bin/env python3
"""
Penske Logistics Analytics - Simple Gradio Frontend
====================================================
Simplified version compatible with older Gradio versions.

Run: python gradio_simple.py
URL: http://localhost:7860
"""

import gradio as gr
import pandas as pd
import numpy as np
from datetime import datetime

# Demo mode
DEMO_MODE = True


def generate_demo_prediction():
    """Generate demo prediction result."""
    return {
        "prediction": round(np.random.uniform(1200, 1800), 0),
        "confidence": round(np.random.uniform(0.85, 0.98), 2),
        "latency_ms": np.random.randint(30, 80)
    }


def predict_demand(shipment_volume, fuel_price, weather_severity, day_of_week, region):
    """Make demand prediction."""
    result = generate_demo_prediction()
    
    output = f"""
## Prediction Results

| Metric | Value |
|--------|-------|
| **Predicted Demand** | {result['prediction']:.0f} shipments |
| **Confidence** | {result['confidence'] * 100:.1f}% |
| **Latency** | {result['latency_ms']}ms |

*Region: {region} | Weather: {weather_severity} | Day: {day_of_week}*
"""
    return output


def load_analytics():
    """Load analytics data."""
    dates = pd.date_range(end=datetime.now(), periods=10, freq='D')
    df = pd.DataFrame({
        'Date': dates.strftime('%Y-%m-%d'),
        'Shipments': np.random.randint(800, 1500, 10),
        'On-Time %': np.random.uniform(92, 99, 10).round(1),
        'Avg Delay (hrs)': np.random.uniform(0.5, 3, 10).round(2)
    })
    return df


def chat_response(message, history):
    """Simple chat response."""
    if "performance" in message.lower():
        return "Fleet is performing at 96.2% on-time delivery rate, 2.1% above target."
    elif "delay" in message.lower():
        return "Main delay causes: Weather (35%), Traffic (28%), Loading docks (22%), Driver availability (15%)."
    elif "predict" in message.lower():
        return "Next week forecast: ~8,450 shipments, 5% increase from this week."
    else:
        return f"I'm your logistics AI assistant. Ask about performance, delays, or predictions. You asked: '{message}'"


# Build the interface
with gr.Blocks(title="Penske Logistics Analytics") as demo:
    gr.Markdown("# Penske Logistics Analytics")
    gr.Markdown("### ML-Powered Demand Forecasting")
    
    with gr.Tab("Predictions"):
        gr.Markdown("### Demand Prediction")
        with gr.Row():
            with gr.Column():
                shipment_vol = gr.Number(label="Shipment Volume", value=1250)
                fuel = gr.Number(label="Fuel Price ($/gal)", value=3.45)
                weather = gr.Slider(0, 3, value=0, step=1, label="Weather Severity")
                day = gr.Slider(1, 7, value=2, step=1, label="Day of Week")
                region = gr.Dropdown(["Midwest", "Northeast", "Southeast", "West"], 
                                    value="Northeast", label="Region")
                predict_btn = gr.Button("Predict Demand", variant="primary")
            with gr.Column():
                output = gr.Markdown(label="Results")
        
        predict_btn.click(predict_demand, 
                         inputs=[shipment_vol, fuel, weather, day, region],
                         outputs=output)
    
    with gr.Tab("Analytics"):
        gr.Markdown("### Performance Analytics")
        refresh_btn = gr.Button("Load Data")
        table = gr.Dataframe(label="Recent Performance")
        refresh_btn.click(load_analytics, outputs=table)
    
    with gr.Tab("AI Chat"):
        gr.Markdown("### AI Assistant")
        chatbot = gr.Chatbot(label="Chat")
        msg = gr.Textbox(label="Your message", placeholder="Ask about logistics...")
        send_btn = gr.Button("Send")
        
        def respond(message, chat_history):
            response = chat_response(message, chat_history)
            chat_history.append((message, response))
            return "", chat_history
        
        send_btn.click(respond, [msg, chatbot], [msg, chatbot])
        msg.submit(respond, [msg, chatbot], [msg, chatbot])
    
    gr.Markdown("---")
    gr.Markdown("*Penske Logistics Analytics v1.0 | Demo Mode*")


if __name__ == "__main__":
    print("=" * 50)
    print("PENSKE LOGISTICS - GRADIO FRONTEND")
    print("=" * 50)
    print("URL: http://localhost:7860")
    print("=" * 50)
    demo.launch(server_port=7860)
