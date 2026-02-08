#!/usr/bin/env python3
"""
Penske Logistics Analytics - Enhanced Gradio Frontend
======================================================
Full-featured frontend with charts, analytics, and AI assistant.

Run: python gradio_app_enhanced.py
URL: http://localhost:7860
"""

import gradio as gr
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

# Demo mode
DEMO_MODE = True


# ============================================================================
# DATA GENERATORS
# ============================================================================

def generate_shipment_data(days=30):
    """Generate realistic shipment data."""
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    np.random.seed(42)
    
    base_volume = 1200
    trend = np.linspace(0, 100, days)
    seasonality = 150 * np.sin(np.linspace(0, 4*np.pi, days))
    noise = np.random.normal(0, 50, days)
    
    volumes = base_volume + trend + seasonality + noise
    
    return pd.DataFrame({
        'Date': dates,
        'Actual': volumes.astype(int),
        'Predicted': (volumes + np.random.normal(0, 30, days)).astype(int),
        'On_Time_Pct': np.clip(92 + np.random.normal(0, 3, days), 85, 99).round(1),
        'Avg_Delay_Hrs': np.clip(1.5 + np.random.normal(0, 0.5, days), 0.2, 4).round(2),
        'Region': np.random.choice(['Northeast', 'Midwest', 'Southeast', 'West'], days)
    })


def generate_regional_data():
    """Generate regional performance data."""
    regions = ['Northeast', 'Midwest', 'Southeast', 'West']
    return pd.DataFrame({
        'Region': regions,
        'Shipments': [3450, 2890, 2120, 1540],
        'On_Time_Pct': [96.2, 94.8, 93.5, 95.1],
        'Revenue_M': [4.2, 3.5, 2.8, 2.1],
        'Avg_Cost': [245, 220, 198, 275]
    })


def generate_kpi_data():
    """Generate KPI summary."""
    return {
        'total_shipments': 42850,
        'on_time_rate': 94.7,
        'avg_delay': 1.8,
        'revenue': 12.6,
        'cost_savings': 8.2,
        'fleet_utilization': 87.3
    }


# ============================================================================
# CHART FUNCTIONS
# ============================================================================

def create_shipment_trend_chart():
    """Create shipment volume trend chart."""
    df = generate_shipment_data(30)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['Date'], y=df['Actual'],
        mode='lines+markers',
        name='Actual',
        line=dict(color='#2563eb', width=2),
        marker=dict(size=4)
    ))
    fig.add_trace(go.Scatter(
        x=df['Date'], y=df['Predicted'],
        mode='lines',
        name='Predicted',
        line=dict(color='#10b981', width=2, dash='dash')
    ))
    
    fig.update_layout(
        title='📈 Shipment Volume Trend (30 Days)',
        xaxis_title='Date',
        yaxis_title='Shipments',
        template='plotly_white',
        height=400,
        legend=dict(orientation='h', yanchor='bottom', y=1.02)
    )
    return fig


def create_regional_chart():
    """Create regional performance chart."""
    df = generate_regional_data()
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Shipments by Region', 'On-Time Rate by Region'),
        specs=[[{'type': 'pie'}, {'type': 'bar'}]]
    )
    
    # Pie chart
    fig.add_trace(
        go.Pie(
            labels=df['Region'],
            values=df['Shipments'],
            hole=0.4,
            marker_colors=['#2563eb', '#10b981', '#f59e0b', '#ef4444']
        ),
        row=1, col=1
    )
    
    # Bar chart
    fig.add_trace(
        go.Bar(
            x=df['Region'],
            y=df['On_Time_Pct'],
            marker_color=['#2563eb', '#10b981', '#f59e0b', '#ef4444'],
            text=df['On_Time_Pct'].apply(lambda x: f'{x}%'),
            textposition='outside'
        ),
        row=1, col=2
    )
    
    fig.update_layout(
        title='🌎 Regional Performance Overview',
        template='plotly_white',
        height=400,
        showlegend=False
    )
    fig.update_yaxes(range=[90, 100], row=1, col=2)
    
    return fig


def create_performance_dashboard():
    """Create performance metrics dashboard."""
    df = generate_shipment_data(7)
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Daily On-Time Rate', 'Average Delay Hours',
            'Shipment Distribution', 'Weekly Trend'
        ),
        specs=[
            [{'type': 'scatter'}, {'type': 'bar'}],
            [{'type': 'histogram'}, {'type': 'scatter'}]
        ]
    )
    
    # On-Time Rate
    fig.add_trace(
        go.Scatter(
            x=df['Date'], y=df['On_Time_Pct'],
            mode='lines+markers',
            line=dict(color='#10b981', width=2),
            fill='tozeroy',
            fillcolor='rgba(16, 185, 129, 0.1)'
        ),
        row=1, col=1
    )
    
    # Delay Hours
    colors = ['#ef4444' if x > 2 else '#10b981' for x in df['Avg_Delay_Hrs']]
    fig.add_trace(
        go.Bar(
            x=df['Date'].dt.strftime('%m/%d'),
            y=df['Avg_Delay_Hrs'],
            marker_color=colors
        ),
        row=1, col=2
    )
    
    # Histogram
    df_full = generate_shipment_data(90)
    fig.add_trace(
        go.Histogram(
            x=df_full['Actual'],
            nbinsx=20,
            marker_color='#2563eb'
        ),
        row=2, col=1
    )
    
    # Weekly Trend
    weekly = df_full.groupby(df_full['Date'].dt.isocalendar().week)['Actual'].mean().reset_index()
    fig.add_trace(
        go.Scatter(
            x=weekly['week'],
            y=weekly['Actual'],
            mode='lines+markers',
            line=dict(color='#8b5cf6', width=2)
        ),
        row=2, col=2
    )
    
    fig.update_layout(
        title='📊 Performance Dashboard',
        template='plotly_white',
        height=600,
        showlegend=False
    )
    
    return fig


def create_forecast_chart(days_ahead=14):
    """Create demand forecast chart."""
    historical = generate_shipment_data(30)
    
    # Generate forecast
    last_date = historical['Date'].max()
    forecast_dates = pd.date_range(start=last_date + timedelta(days=1), periods=days_ahead)
    
    base = historical['Actual'].iloc[-7:].mean()
    trend = np.linspace(0, 50, days_ahead)
    forecast_values = base + trend + np.random.normal(0, 30, days_ahead)
    
    # Confidence intervals
    lower = forecast_values - 80
    upper = forecast_values + 80
    
    fig = go.Figure()
    
    # Historical
    fig.add_trace(go.Scatter(
        x=historical['Date'], y=historical['Actual'],
        mode='lines',
        name='Historical',
        line=dict(color='#2563eb', width=2)
    ))
    
    # Forecast
    fig.add_trace(go.Scatter(
        x=forecast_dates, y=forecast_values,
        mode='lines+markers',
        name='Forecast',
        line=dict(color='#10b981', width=2)
    ))
    
    # Confidence interval
    fig.add_trace(go.Scatter(
        x=list(forecast_dates) + list(forecast_dates[::-1]),
        y=list(upper) + list(lower[::-1]),
        fill='toself',
        fillcolor='rgba(16, 185, 129, 0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        name='95% CI'
    ))
    
    fig.update_layout(
        title=f'🔮 {days_ahead}-Day Demand Forecast',
        xaxis_title='Date',
        yaxis_title='Predicted Shipments',
        template='plotly_white',
        height=400
    )
    
    return fig


# ============================================================================
# PREDICTION FUNCTION
# ============================================================================

def predict_demand(shipment_volume, fuel_price, weather_severity, day_of_week, region):
    """Make demand prediction with visualization."""
    # Simulate prediction
    base_prediction = shipment_volume * 1.05
    weather_impact = -weather_severity * 50
    fuel_impact = (fuel_price - 3.5) * -20
    day_factor = 1.1 if day_of_week <= 5 else 0.85
    
    prediction = int((base_prediction + weather_impact + fuel_impact) * day_factor)
    confidence = round(np.random.uniform(0.88, 0.96), 2)
    
    # Create gauge chart
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=prediction,
        delta={'reference': int(shipment_volume), 'relative': True},
        title={'text': "Predicted Demand"},
        gauge={
            'axis': {'range': [800, 2000]},
            'bar': {'color': "#2563eb"},
            'steps': [
                {'range': [800, 1200], 'color': "#fef3c7"},
                {'range': [1200, 1600], 'color': "#d1fae5"},
                {'range': [1600, 2000], 'color': "#dbeafe"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': prediction * 1.1
            }
        }
    ))
    
    fig.update_layout(height=300, template='plotly_white')
    
    summary = f"""
### Prediction Results

| Metric | Value |
|--------|-------|
| **Predicted Demand** | {prediction:,} shipments |
| **Confidence** | {confidence * 100:.1f}% |
| **Change from Current** | {((prediction/shipment_volume)-1)*100:+.1f}% |
| **Region** | {region} |
| **Weather Impact** | {weather_impact:+.0f} units |
| **Fuel Impact** | {fuel_impact:+.0f} units |
"""
    
    return fig, summary


# ============================================================================
# ANALYTICS FUNCTIONS
# ============================================================================

def generate_analytics_report():
    """Generate comprehensive analytics report."""
    kpis = generate_kpi_data()
    df = generate_shipment_data(30)
    regional = generate_regional_data()
    
    report = f"""
# 📊 Analytics Report
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

## Key Performance Indicators

| Metric | Value | Status |
|--------|-------|--------|
| **Total Shipments (MTD)** | {kpis['total_shipments']:,} | ✅ On Track |
| **On-Time Delivery Rate** | {kpis['on_time_rate']}% | {'✅' if kpis['on_time_rate'] > 94 else '⚠️'} |
| **Average Delay** | {kpis['avg_delay']} hrs | {'✅' if kpis['avg_delay'] < 2 else '⚠️'} |
| **Revenue (MTD)** | ${kpis['revenue']}M | ✅ |
| **Cost Savings** | {kpis['cost_savings']}% | ✅ |
| **Fleet Utilization** | {kpis['fleet_utilization']}% | ✅ |

---

## Regional Summary

| Region | Shipments | On-Time % | Revenue |
|--------|-----------|-----------|---------|
"""
    
    for _, row in regional.iterrows():
        status = '✅' if row['On_Time_Pct'] > 94 else '⚠️'
        report += f"| {row['Region']} | {row['Shipments']:,} | {row['On_Time_Pct']}% {status} | ${row['Revenue_M']}M |\n"
    
    report += f"""
---

## 7-Day Trend Analysis

| Day | Shipments | On-Time % | Delay (hrs) |
|-----|-----------|-----------|-------------|
"""
    
    for _, row in df.tail(7).iterrows():
        report += f"| {row['Date'].strftime('%m/%d')} | {row['Actual']:,} | {row['On_Time_Pct']}% | {row['Avg_Delay_Hrs']} |\n"
    
    report += """
---

## Insights & Recommendations

1. **Strong Performance**: Overall on-time rate exceeds target of 94%
2. **Regional Focus**: Southeast region showing improvement opportunity
3. **Forecast**: Expect 5-8% volume increase next week due to seasonal demand
4. **Cost Optimization**: Current fleet utilization supports additional capacity
"""
    
    return report


def load_performance_table():
    """Load detailed performance data."""
    df = generate_shipment_data(14)
    df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
    df['Status'] = df['On_Time_Pct'].apply(lambda x: '✅ Good' if x > 94 else '⚠️ Below Target')
    return df[['Date', 'Actual', 'Predicted', 'On_Time_Pct', 'Avg_Delay_Hrs', 'Region', 'Status']]


# ============================================================================
# CHAT FUNCTION
# ============================================================================

def chat_response(message, history):
    """AI chat with context-aware responses."""
    msg = message.lower()
    kpis = generate_kpi_data()
    
    if any(word in msg for word in ['performance', 'how', 'doing', 'status']):
        return f"""Based on today's data:

**Fleet Performance Summary:**
- 📦 Total Shipments: {kpis['total_shipments']:,}
- ⏱️ On-Time Rate: {kpis['on_time_rate']}% (Target: 94%)
- ⏳ Avg Delay: {kpis['avg_delay']} hours
- 💰 Revenue MTD: ${kpis['revenue']}M

The fleet is performing **above target** with strong on-time delivery rates. Northeast region leads at 96.2%."""
        
    elif any(word in msg for word in ['delay', 'late', 'issue', 'problem']):
        return """**Delay Analysis (This Week):**

| Cause | Percentage | Trend |
|-------|------------|-------|
| Weather conditions | 35% | ↑ |
| Traffic congestion | 28% | ↔ |
| Loading dock delays | 22% | ↓ |
| Driver availability | 15% | ↔ |

**Recommendation:** Focus on weather contingency routes for Northeast region where 60% of weather delays occur."""
        
    elif any(word in msg for word in ['predict', 'forecast', 'next', 'expect']):
        return """**Demand Forecast (Next 7 Days):**

| Day | Predicted | Confidence |
|-----|-----------|------------|
| Mon | 1,420 | 94% |
| Tue | 1,385 | 93% |
| Wed | 1,510 | 91% |
| Thu | 1,475 | 92% |
| Fri | 1,620 | 89% |
| Sat | 980 | 87% |
| Sun | 850 | 85% |

**Total Week:** ~8,240 shipments (+5.2% vs last week)
**Key Driver:** Seasonal demand increase in Midwest region"""
        
    elif any(word in msg for word in ['cost', 'save', 'optimize', 'efficiency']):
        return f"""**Cost Optimization Insights:**

- Current fleet utilization: {kpis['fleet_utilization']}%
- Cost savings YTD: {kpis['cost_savings']}%

**Opportunities:**
1. Route optimization could save additional 3-4%
2. Off-peak scheduling for non-urgent deliveries
3. Consolidation in low-density regions

**Estimated Annual Savings:** $1.2M - $1.8M"""
        
    else:
        return f"""I'm your AI logistics assistant. I can help with:

- 📊 **Performance**: "How is the fleet performing today?"
- ⏱️ **Delays**: "What are the main causes of delays?"
- 🔮 **Forecasts**: "Predict demand for next week"
- 💰 **Costs**: "How can we optimize costs?"

Current Status: {kpis['total_shipments']:,} shipments | {kpis['on_time_rate']}% on-time"""


# ============================================================================
# GRADIO APP
# ============================================================================

with gr.Blocks(title="Penske Logistics Analytics") as demo:
    
    gr.Markdown("""
    # 🚚 Penske Logistics Analytics
    ### ML-Powered Demand Forecasting & Performance Analytics
    """)
    
    with gr.Tabs():
        
        # =====================================================================
        # TAB: Dashboard
        # =====================================================================
        with gr.Tab("📊 Dashboard"):
            gr.Markdown("### Real-Time Performance Overview")
            
            with gr.Row():
                with gr.Column(scale=2):
                    trend_chart = gr.Plot(label="Shipment Trend")
                with gr.Column(scale=1):
                    gr.Markdown("""
                    ### Quick Stats
                    - **Total Shipments:** 42,850
                    - **On-Time Rate:** 94.7%
                    - **Avg Delay:** 1.8 hrs
                    - **Fleet Util:** 87.3%
                    """)
            
            with gr.Row():
                regional_chart = gr.Plot(label="Regional Performance")
            
            refresh_dash_btn = gr.Button("🔄 Refresh Dashboard", variant="primary")
            
            def refresh_dashboard():
                return create_shipment_trend_chart(), create_regional_chart()
            
            refresh_dash_btn.click(refresh_dashboard, outputs=[trend_chart, regional_chart])
            demo.load(refresh_dashboard, outputs=[trend_chart, regional_chart])
        
        # =====================================================================
        # TAB: Predictions
        # =====================================================================
        with gr.Tab("🎯 Predictions"):
            gr.Markdown("### Demand Prediction Engine")
            
            with gr.Row():
                with gr.Column():
                    shipment_vol = gr.Number(label="Current Shipment Volume", value=1250)
                    fuel = gr.Number(label="Fuel Price ($/gal)", value=3.45)
                    weather = gr.Slider(0, 3, value=0, step=1, 
                                       label="Weather Severity (0=Clear, 3=Severe)")
                    day = gr.Slider(1, 7, value=2, step=1, 
                                   label="Day of Week (1=Mon, 7=Sun)")
                    region = gr.Dropdown(
                        ["Northeast", "Midwest", "Southeast", "West"],
                        value="Northeast", label="Region"
                    )
                    predict_btn = gr.Button("🚀 Generate Prediction", variant="primary")
                
                with gr.Column():
                    pred_gauge = gr.Plot(label="Prediction Gauge")
                    pred_summary = gr.Markdown()
            
            predict_btn.click(
                predict_demand,
                inputs=[shipment_vol, fuel, weather, day, region],
                outputs=[pred_gauge, pred_summary]
            )
            
            gr.Markdown("---")
            gr.Markdown("### Demand Forecast")
            
            forecast_days = gr.Slider(7, 30, value=14, step=1, label="Forecast Days")
            forecast_chart = gr.Plot(label="Forecast")
            forecast_btn = gr.Button("📈 Generate Forecast")
            
            forecast_btn.click(
                create_forecast_chart,
                inputs=[forecast_days],
                outputs=[forecast_chart]
            )
        
        # =====================================================================
        # TAB: Analytics
        # =====================================================================
        with gr.Tab("📈 Analytics"):
            gr.Markdown("### Performance Analytics")
            
            perf_dashboard = gr.Plot(label="Performance Metrics")
            refresh_perf_btn = gr.Button("🔄 Refresh Charts", variant="secondary")
            
            refresh_perf_btn.click(create_performance_dashboard, outputs=[perf_dashboard])
            demo.load(create_performance_dashboard, outputs=[perf_dashboard])
            
            gr.Markdown("---")
            gr.Markdown("### Detailed Report")
            
            report_output = gr.Markdown()
            generate_report_btn = gr.Button("📋 Generate Report", variant="primary")
            generate_report_btn.click(generate_analytics_report, outputs=[report_output])
            
            gr.Markdown("---")
            gr.Markdown("### Performance Data")
            
            perf_table = gr.Dataframe(label="14-Day Performance")
            load_table_btn = gr.Button("📊 Load Data")
            load_table_btn.click(load_performance_table, outputs=[perf_table])
        
        # =====================================================================
        # TAB: AI Assistant
        # =====================================================================
        with gr.Tab("🤖 AI Assistant"):
            gr.Markdown("### AI-Powered Logistics Assistant")
            gr.Markdown("Ask questions about performance, delays, forecasts, or cost optimization.")
            
            chatbot = gr.Chatbot(label="Chat", height=400)
            msg = gr.Textbox(label="Your question", placeholder="How is the fleet performing today?")
            
            with gr.Row():
                send_btn = gr.Button("Send", variant="primary")
                clear_btn = gr.Button("Clear")
            
            gr.Markdown("**Quick prompts:**")
            with gr.Row():
                q1 = gr.Button("📊 Performance summary", size="sm")
                q2 = gr.Button("⏱️ Delay analysis", size="sm")
                q3 = gr.Button("🔮 Weekly forecast", size="sm")
                q4 = gr.Button("💰 Cost optimization", size="sm")
            
            def respond(message, chat_history):
                if not message:
                    return "", chat_history
                response = chat_response(message, chat_history)
                chat_history = chat_history + [
                    {"role": "user", "content": message},
                    {"role": "assistant", "content": response}
                ]
                return "", chat_history
            
            send_btn.click(respond, [msg, chatbot], [msg, chatbot])
            msg.submit(respond, [msg, chatbot], [msg, chatbot])
            clear_btn.click(lambda: [], outputs=[chatbot])
            
            q1.click(lambda h: respond("How is the fleet performing?", h), [chatbot], [msg, chatbot])
            q2.click(lambda h: respond("What are the main causes of delays?", h), [chatbot], [msg, chatbot])
            q3.click(lambda h: respond("Predict demand for next week", h), [chatbot], [msg, chatbot])
            q4.click(lambda h: respond("How can we optimize costs?", h), [chatbot], [msg, chatbot])
    
    gr.Markdown("---")
    gr.Markdown("*Penske Logistics Analytics v2.0 | Demo Mode | Powered by ML*")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("PENSKE LOGISTICS ANALYTICS - ENHANCED GRADIO FRONTEND")
    print("=" * 60)
    print("URL: http://localhost:7860")
    print("=" * 60)
    demo.launch(server_port=7860)
