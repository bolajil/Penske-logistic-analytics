"""
Penske Logistics Analytics Dashboard
Interactive Streamlit application for performance monitoring and predictions
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_prep import DataLoader, DataPreprocessor
from src.service_performance import ServicePerformanceAnalyzer
from src.resource_prediction import DemandForecaster, ResourceOptimizer
from src.customer_acquisition import LeadScorer, ChurnPredictor, CustomerSegmenter
from src.genai_insights import InsightGenerator

st.set_page_config(
    page_title="Penske Logistics Analytics",
    page_icon="🚛",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
    }
    [data-testid="stMetric"] {
        background-color: #1e1e1e;
        padding: 15px 20px;
        border-radius: 8px;
        border: 1px solid #333;
    }
    [data-testid="stMetricLabel"] {
        font-size: 14px !important;
        color: #aaa !important;
    }
    [data-testid="stMetricValue"] {
        font-size: 28px !important;
        font-weight: bold !important;
        color: #fff !important;
    }
    [data-testid="stMetricDelta"] {
        font-size: 12px !important;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data(use_dummy: bool = True):
    """Load and cache data"""
    loader = DataLoader(use_dummy=use_dummy)
    return loader.load_all()


@st.cache_resource
def get_analyzer(datasets):
    """Get cached performance analyzer"""
    return ServicePerformanceAnalyzer(datasets)


def render_sidebar():
    """Render sidebar navigation"""
    st.sidebar.image("https://www.penskelogistics.com/images/penske-logo.svg", width=200)
    st.sidebar.title("Navigation")
    
    page = st.sidebar.radio(
        "Select View",
        ["📊 Executive Dashboard", "🚛 Fleet Operations", "🏭 Warehouse Analytics",
         "👥 Customer Intelligence", "📈 Demand Forecasting", "🤖 AI Insights"]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("Filters")
    
    date_range = st.sidebar.date_input(
        "Date Range",
        value=(datetime.now() - timedelta(days=30), datetime.now()),
        max_value=datetime.now()
    )
    
    regions = st.sidebar.multiselect(
        "Regions",
        ["Northeast", "Southeast", "Midwest", "Southwest", "West", "Northwest"],
        default=["Northeast", "Southeast", "Midwest", "Southwest", "West", "Northwest"]
    )
    
    return page, date_range, regions


def render_executive_dashboard(datasets, analyzer):
    """Render executive dashboard view"""
    st.title("🚛 Penske Logistics Executive Dashboard")
    st.markdown("Real-time operational intelligence and performance metrics")
    
    summary = analyzer.get_executive_summary()
    kpis = analyzer.calculate_overall_kpis()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Overall Score",
            f"{summary['overall_score']:.0f}/100",
            delta=f"{summary['health_status']}"
        )
    
    with col2:
        st.metric(
            "On-Time Delivery",
            f"{kpis.get('on_time_delivery_rate', 0):.1f}%",
            delta=f"{kpis.get('on_time_delivery_rate', 0) - 95:.1f}% vs target"
        )
    
    with col3:
        st.metric(
            "Fleet Utilization",
            f"{kpis.get('fleet_utilization', 0):.1f}%",
            delta=f"{kpis.get('fleet_utilization', 0) - 85:.1f}% vs target"
        )
    
    with col4:
        st.metric(
            "Customer Satisfaction",
            f"{kpis.get('customer_satisfaction_avg', 0):.1f}/10",
            delta="Good" if kpis.get('customer_satisfaction_avg', 0) > 7 else "Needs Attention"
        )
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📍 Regional Performance")
        regional = analyzer.analyze_by_region()
        if not regional.empty and 'on_time_rate' in regional.columns:
            fig = px.bar(
                regional.reset_index(),
                x='index',
                y='on_time_rate',
                color='on_time_rate',
                color_continuous_scale='RdYlGn',
                labels={'index': 'Region', 'on_time_rate': 'On-Time Rate'}
            )
            fig.update_layout(showlegend=False, height=350)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📦 Service Performance")
        service = analyzer.analyze_by_service_type()
        if not service.empty:
            numeric_cols = service.select_dtypes(include=[np.number]).columns[:4]
            fig = go.Figure()
            for col in numeric_cols:
                fig.add_trace(go.Bar(name=col, x=service.index, y=service[col]))
            fig.update_layout(barmode='group', height=350)
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    st.subheader("⚠️ Alerts & Recommendations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Critical Areas:**")
        for area in summary.get('critical_areas', ['None identified']):
            st.warning(f"🔴 {area}")
    
    with col2:
        st.markdown("**Top Recommendations:**")
        for rec in summary.get('recommendations', [])[:5]:
            st.info(f"💡 {rec}")


def render_fleet_operations(datasets):
    """Render fleet operations view"""
    st.title("🚛 Fleet Operations Analytics")
    
    if 'fleet_operations' not in datasets:
        st.warning("Fleet operations data not available")
        return
    
    df = datasets['fleet_operations']
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Vehicles", df['vehicle_id'].nunique())
    with col2:
        st.metric("Avg Miles/Day", f"{df['miles_driven'].mean():.0f}")
    with col3:
        st.metric("Avg Utilization", f"{df['load_capacity_used'].mean():.1f}%")
    with col4:
        st.metric("On-Time Rate", f"{df['on_time_rate'].mean()*100:.1f}%")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Fleet Utilization by Region")
        util_by_region = df.groupby('region')['load_capacity_used'].mean().reset_index()
        fig = px.bar(util_by_region, x='region', y='load_capacity_used',
                    color='load_capacity_used', color_continuous_scale='Blues')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Fuel Efficiency Trends")
        df['date'] = pd.to_datetime(df['date'])
        daily_fuel = df.groupby('date').agg({
            'miles_driven': 'sum',
            'fuel_consumed': 'sum'
        }).reset_index()
        daily_fuel['mpg'] = daily_fuel['miles_driven'] / daily_fuel['fuel_consumed']
        fig = px.line(daily_fuel, x='date', y='mpg')
        st.plotly_chart(fig, use_container_width=True)
    
    if 'maintenance_records' in datasets:
        st.subheader("🔧 Maintenance Overview")
        maint = datasets['maintenance_records']
        
        col1, col2 = st.columns(2)
        with col1:
            maint_by_type = maint['maintenance_type'].value_counts()
            fig = px.pie(values=maint_by_type.values, names=maint_by_type.index,
                        title="Maintenance by Type")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            avg_cost = maint.groupby('maintenance_type')['cost'].mean().reset_index()
            fig = px.bar(avg_cost, x='maintenance_type', y='cost',
                        title="Average Cost by Type")
            st.plotly_chart(fig, use_container_width=True)


def render_warehouse_analytics(datasets):
    """Render warehouse analytics view"""
    st.title("🏭 Warehouse Analytics")
    
    if 'warehouse_metrics' not in datasets:
        st.warning("Warehouse data not available")
        return
    
    df = datasets['warehouse_metrics']
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Warehouses", df['warehouse_id'].nunique())
    with col2:
        st.metric("Avg Throughput", f"{df['throughput_units'].mean():,.0f}")
    with col3:
        st.metric("Inventory Accuracy", f"{df['inventory_accuracy'].mean():.1f}%")
    with col4:
        st.metric("Order Fill Rate", f"{df['order_fill_rate'].mean():.1f}%")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Throughput by Region")
        throughput = df.groupby('region')['throughput_units'].mean().reset_index()
        fig = px.bar(throughput, x='region', y='throughput_units', color='throughput_units')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Efficiency Metrics")
        metrics = df.groupby('region').agg({
            'order_fill_rate': 'mean',
            'inventory_accuracy': 'mean',
            'dock_utilization': 'mean'
        }).reset_index()
        fig = go.Figure()
        for col in ['order_fill_rate', 'inventory_accuracy', 'dock_utilization']:
            fig.add_trace(go.Bar(name=col, x=metrics['region'], y=metrics[col]))
        fig.update_layout(barmode='group')
        st.plotly_chart(fig, use_container_width=True)


def render_customer_intelligence(datasets):
    """Render customer intelligence view"""
    st.title("👥 Customer Intelligence")
    
    tab1, tab2, tab3 = st.tabs(["Lead Scoring", "Churn Risk", "Segmentation"])
    
    with tab1:
        if 'sales_leads' in datasets:
            st.subheader("🎯 Lead Scoring")
            leads = datasets['sales_leads']
            
            scorer = LeadScorer()
            try:
                scorer.train(leads)
                scored = scorer.score_leads(leads)
                
                col1, col2 = st.columns(2)
                with col1:
                    priority_counts = scored['priority'].value_counts()
                    fig = px.pie(values=priority_counts.values, names=priority_counts.index,
                                title="Leads by Priority", color_discrete_sequence=px.colors.sequential.RdBu)
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    st.dataframe(
                        scored[['company_name', 'lead_score', 'priority']].head(10),
                        use_container_width=True
                    )
            except Exception as e:
                st.error(f"Error scoring leads: {e}")
    
    with tab2:
        if 'customer_data' in datasets:
            st.subheader("⚠️ Churn Risk Analysis")
            customers = datasets['customer_data']
            
            predictor = ChurnPredictor()
            try:
                predictor.train(customers)
                churn_risks = predictor.predict_churn_risk(customers)
                
                col1, col2 = st.columns(2)
                with col1:
                    risk_counts = churn_risks['risk_level'].value_counts()
                    fig = px.pie(values=risk_counts.values, names=risk_counts.index,
                                title="Customers by Risk Level")
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    total_risk = churn_risks['revenue_at_risk'].sum()
                    st.metric("Total Revenue at Risk", f"${total_risk:,.0f}")
                    st.dataframe(
                        churn_risks[['company_name', 'churn_risk_score', 'risk_level']].head(10),
                        use_container_width=True
                    )
            except Exception as e:
                st.error(f"Error predicting churn: {e}")
    
    with tab3:
        if 'customer_data' in datasets:
            st.subheader("📊 Customer Segmentation")
            customers = datasets['customer_data']
            
            segmenter = CustomerSegmenter(n_segments=5)
            try:
                results = segmenter.fit_segments(customers)
                
                for seg_id, profile in results['segment_profiles'].items():
                    with st.expander(f"{profile['name']} ({profile['count']} customers)"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Avg Contract Value", f"${profile['avg_contract_value']:,.0f}")
                            st.metric("Avg Tenure", f"{profile['avg_tenure']:.0f} months")
                        with col2:
                            st.metric("Total Revenue", f"${profile['total_revenue']:,.0f}")
                            st.write("**Characteristics:**", ", ".join(profile['characteristics']))
            except Exception as e:
                st.error(f"Error in segmentation: {e}")


def render_demand_forecasting(datasets):
    """Render demand forecasting view"""
    st.title("📈 Demand Forecasting & Resource Planning")
    
    if 'regional_demand' not in datasets:
        st.warning("Regional demand data not available")
        return
    
    df = datasets['regional_demand']
    
    st.subheader("Historical Demand Trends")
    df['date'] = pd.to_datetime(df['date'])
    daily_demand = df.groupby('date')['shipment_volume'].sum().reset_index()
    fig = px.line(daily_demand, x='date', y='shipment_volume', title="Daily Shipment Volume")
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Demand by Region")
    region_demand = df.groupby('region')['shipment_volume'].mean().reset_index()
    fig = px.bar(region_demand, x='region', y='shipment_volume', color='shipment_volume')
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("🔮 Forecast Generation")
    if st.button("Generate 30-Day Forecast"):
        with st.spinner("Training model and generating forecast..."):
            forecaster = DemandForecaster()
            try:
                results = forecaster.train_demand_model(df, 'shipment_volume')
                st.success(f"Model trained! MAPE: {results['metrics']['mape']:.2f}%")
                
                st.write("**Top Features:**")
                for feat, imp in list(results['feature_importance'].items())[:5]:
                    st.write(f"- {feat}: {imp:.4f}")
            except Exception as e:
                st.error(f"Error in forecasting: {e}")


def render_ai_insights(datasets, analyzer):
    """Render AI insights view"""
    st.title("🤖 AI-Powered Insights")
    
    generator = InsightGenerator()
    
    st.subheader("📊 Performance Analysis")
    if st.button("Generate Performance Insights"):
        with st.spinner("Analyzing performance data..."):
            kpis = analyzer.calculate_overall_kpis()
            insight = generator.generate_performance_insight(kpis)
            st.markdown(insight)
    
    st.markdown("---")
    
    st.subheader("💬 Ask a Question")
    question = st.text_input("Enter your question about the data:")
    if question:
        with st.spinner("Generating answer..."):
            kpis = analyzer.calculate_overall_kpis()
            answer = generator.answer_question(question, kpis)
            st.markdown(answer)


def main():
    """Main application entry point"""
    datasets = load_data(use_dummy=True)
    
    if not datasets:
        st.error("No data available. Please run `python -m src.data_generator` first.")
        return
    
    analyzer = get_analyzer(datasets)
    page, date_range, regions = render_sidebar()
    
    if page == "📊 Executive Dashboard":
        render_executive_dashboard(datasets, analyzer)
    elif page == "🚛 Fleet Operations":
        render_fleet_operations(datasets)
    elif page == "🏭 Warehouse Analytics":
        render_warehouse_analytics(datasets)
    elif page == "👥 Customer Intelligence":
        render_customer_intelligence(datasets)
    elif page == "📈 Demand Forecasting":
        render_demand_forecasting(datasets)
    elif page == "🤖 AI Insights":
        render_ai_insights(datasets, analyzer)


if __name__ == "__main__":
    main()
