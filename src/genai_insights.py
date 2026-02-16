"""
GenAI Insights Module for Penske Logistics Analytics
Generates natural language insights using LLM integration
"""

import os
from typing import Dict, List, Optional
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI package not installed. GenAI features will use mock responses.")

try:
    from session_manager import SessionManager, ServiceType
    SESSION_MANAGER_AVAILABLE = True
except ImportError:
    SESSION_MANAGER_AVAILABLE = False
    logger.info("SessionManager not available. Running without timeout/retry/fallback.")


class InsightGenerator:
    """Generate AI-powered insights for logistics operations"""
    
    def __init__(self, api_key: str = None, session_manager: SessionManager = None):
        """
        Initialize the insight generator
        
        Args:
            api_key: OpenAI API key. If not provided, uses OPENAI_API_KEY env var
            session_manager: Optional SessionManager for timeout/retry/fallback
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.client = None
        self.session_manager = session_manager
        
        if OPENAI_AVAILABLE and self.api_key:
            self.client = OpenAI(api_key=self.api_key)
            logger.info("OpenAI client initialized")
        else:
            logger.warning("Running in mock mode - no API calls will be made")
        
        if self.session_manager is None and SESSION_MANAGER_AVAILABLE:
            self.session_manager = SessionManager()
            logger.info("Default SessionManager initialized (30s timeout, 3 retries, model fallback)")
    
    def _call_llm(self, system_prompt: str, user_prompt: str, temperature: float = 0.7) -> str:
        """Make LLM API call with timeout, retry, and model fallback.
        
        Fallback chain: GPT-4 → GPT-3.5-turbo → mock response
        Each attempt has a 30s timeout with 3 retries and exponential backoff.
        """
        if not self.client:
            return self._mock_response(user_prompt)
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # Use SessionManager for timeout/retry/fallback if available
        if self.session_manager:
            result = self.session_manager.call_llm_with_fallback(
                client=self.client,
                messages=messages,
                primary_model="gpt-4",
                fallback_models=["gpt-3.5-turbo"],
                cached_response=self._mock_response(user_prompt),
                temperature=temperature,
                max_tokens=1000,
            )
            if result["model_used"] != "gpt-4":
                logger.warning(f"LLM fallback used: {result['model_used']}")
            return result["content"]
        
        # Fallback: direct call without session management
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=temperature,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM API error: {e}")
            return self._mock_response(user_prompt)
    
    def _mock_response(self, prompt: str) -> str:
        """Generate mock response for testing without API"""
        
        if 'performance' in prompt.lower():
            return """## Performance Analysis Summary

**Overall Assessment: Good with Improvement Areas**

### Key Findings:
1. **On-Time Delivery**: Currently at 88.5%, slightly below the 95% target. The Southwest region shows the most significant gaps.

2. **Fleet Utilization**: Strong at 82%, with opportunities to optimize in the Northeast corridor.

3. **Customer Satisfaction**: Averaging 7.5/10, with dedicated contract carriage scoring highest.

### Recommended Actions:
- Increase driver capacity in Southwest region by 15%
- Implement predictive routing for weather-impacted deliveries
- Launch customer feedback program for low-scoring accounts

### Projected Impact:
Implementing these recommendations could improve on-time delivery by 4-6% within 90 days."""
        
        elif 'resource' in prompt.lower():
            return """## Resource Allocation Recommendations

**Forecast Period: Next 30 Days**

### Fleet Requirements:
- **Northeast**: Add 12 vehicles to meet projected demand increase
- **Southeast**: Current capacity adequate
- **Midwest**: Consider 8 additional vehicles for seasonal peak

### Staffing Needs:
- Warehouse operations require 15% more labor hours in weeks 3-4
- Driver hiring should target 25 new CDL holders by month-end

### Cost Optimization:
- Consolidate underutilized routes in Northwest (-$45K/month potential)
- Shift maintenance scheduling to off-peak hours

### Risk Factors:
- Weather disruptions expected in Midwest (weeks 2-3)
- Fuel cost volatility may impact margins by 2-3%"""
        
        elif 'customer' in prompt.lower() or 'lead' in prompt.lower():
            return """## Customer Acquisition Insights

**Pipeline Health: Strong**

### High-Priority Leads (Score 75+):
1. **TechCorp Industries** - 89% conversion probability
   - Decision maker engaged, budget confirmed
   - Interested in: Dedicated Contract Carriage, Supply Chain Solutions
   - Recommended action: Schedule executive presentation

2. **Global Retail Co** - 82% conversion probability  
   - Large enterprise, multi-region needs
   - Interested in: Distribution Center Management
   - Recommended action: Site visit and capability demo

### Churn Risk Alert:
- 12 accounts showing elevated churn signals
- Total revenue at risk: $2.4M annually
- Priority intervention needed for: Manufacturing Plus, Food Distributors Inc

### Segment Opportunities:
- Growth Accounts segment shows 40% upsell potential
- Cross-sell Transportation Management to existing DC customers"""
        
        else:
            return """## Logistics Analytics Insight

Based on the data analysis, here are the key observations and recommendations:

### Observations:
- Operations are performing within expected parameters
- Some regional variations require attention
- Seasonal patterns are consistent with historical trends

### Recommendations:
1. Continue monitoring key performance indicators
2. Address identified gaps proactively
3. Leverage data-driven insights for decision making

### Next Steps:
- Review detailed metrics in the dashboard
- Schedule planning session with operations team
- Update forecasts based on latest data"""
    
    def generate_performance_insight(self, metrics: Dict) -> str:
        """Generate insights from performance metrics"""
        
        system_prompt = """You are an expert logistics analyst for Penske Logistics. 
        Analyze the provided performance metrics and generate actionable insights.
        Focus on identifying issues, opportunities, and specific recommendations.
        Be concise but thorough. Use markdown formatting."""
        
        user_prompt = f"""Analyze these Penske Logistics performance metrics and provide insights:

{json.dumps(metrics, indent=2, default=str)}

Provide:
1. Overall assessment
2. Key findings (positive and negative)
3. Specific recommendations with expected impact
4. Priority actions for the next 30 days"""
        
        return self._call_llm(system_prompt, user_prompt)
    
    def generate_resource_recommendation(self, resource_plan: Dict, forecast: Dict = None) -> str:
        """Generate resource allocation recommendations"""
        
        system_prompt = """You are a logistics resource planning expert for Penske Logistics.
        Based on demand forecasts and current capacity, provide specific resource allocation recommendations.
        Include fleet, staffing, and facility recommendations.
        Quantify recommendations where possible."""
        
        user_prompt = f"""Based on this resource analysis, provide allocation recommendations:

CURRENT RESOURCE PLAN:
{json.dumps(resource_plan, indent=2, default=str)}

{"DEMAND FORECAST:" + json.dumps(forecast, indent=2, default=str) if forecast else ""}

Provide:
1. Fleet allocation recommendations by region
2. Staffing adjustments needed
3. Cost optimization opportunities
4. Risk factors to monitor"""
        
        return self._call_llm(system_prompt, user_prompt)
    
    def generate_customer_insight(self, customer_data: Dict, lead_scores: Dict = None) -> str:
        """Generate customer acquisition and retention insights"""
        
        system_prompt = """You are a customer success expert for Penske Logistics.
        Analyze customer data to identify acquisition opportunities and retention risks.
        Provide specific, actionable recommendations for the sales and account management teams."""
        
        user_prompt = f"""Analyze this customer data and provide strategic recommendations:

CUSTOMER ANALYSIS:
{json.dumps(customer_data, indent=2, default=str)}

{"LEAD SCORES:" + json.dumps(lead_scores, indent=2, default=str) if lead_scores else ""}

Provide:
1. Top acquisition opportunities with recommended approach
2. Churn risk assessment and intervention strategies
3. Upsell/cross-sell opportunities
4. Customer segment strategies"""
        
        return self._call_llm(system_prompt, user_prompt)
    
    def explain_anomaly(self, anomaly_data: Dict) -> str:
        """Explain detected anomalies in operations"""
        
        system_prompt = """You are a logistics operations analyst for Penske Logistics.
        Explain anomalies detected in operational data.
        Identify likely root causes and recommend corrective actions."""
        
        user_prompt = f"""Explain this operational anomaly:

{json.dumps(anomaly_data, indent=2, default=str)}

Provide:
1. Likely root causes (ranked by probability)
2. Immediate actions needed
3. Preventive measures for the future
4. Impact assessment"""
        
        return self._call_llm(system_prompt, user_prompt, temperature=0.5)
    
    def answer_question(self, question: str, context: Dict) -> str:
        """Answer natural language questions about the data"""
        
        system_prompt = """You are an AI assistant for Penske Logistics analytics.
        Answer questions about logistics operations based on the provided data context.
        Be precise and reference specific data points when available.
        If you're uncertain, say so."""
        
        user_prompt = f"""Question: {question}

Context Data:
{json.dumps(context, indent=2, default=str)}

Provide a clear, data-driven answer."""
        
        return self._call_llm(system_prompt, user_prompt, temperature=0.3)
    
    def generate_executive_summary(self, all_metrics: Dict) -> str:
        """Generate executive summary for leadership"""
        
        system_prompt = """You are preparing an executive briefing for Penske Logistics leadership.
        Summarize the key operational metrics, risks, and opportunities.
        Focus on strategic implications and business impact.
        Use clear, executive-friendly language."""
        
        user_prompt = f"""Generate an executive summary from this operational data:

{json.dumps(all_metrics, indent=2, default=str)}

Format as:
1. Executive Overview (2-3 sentences)
2. Key Performance Highlights
3. Areas Requiring Attention
4. Strategic Recommendations
5. 90-Day Outlook"""
        
        return self._call_llm(system_prompt, user_prompt)


class ReportGenerator:
    """Generate formatted reports with AI insights"""
    
    def __init__(self, insight_generator: InsightGenerator = None):
        self.insight_gen = insight_generator or InsightGenerator()
    
    def generate_weekly_report(
        self,
        performance_metrics: Dict,
        resource_status: Dict,
        customer_metrics: Dict
    ) -> str:
        """Generate comprehensive weekly report"""
        
        report_date = datetime.now().strftime("%B %d, %Y")
        
        report = f"""# Penske Logistics Weekly Operations Report
**Generated: {report_date}**

---

## Performance Summary

{self.insight_gen.generate_performance_insight(performance_metrics)}

---

## Resource Allocation

{self.insight_gen.generate_resource_recommendation(resource_status)}

---

## Customer Intelligence

{self.insight_gen.generate_customer_insight(customer_metrics)}

---

*Report generated by Penske Logistics Analytics Platform*
"""
        return report
    
    def generate_alert_notification(self, alert_type: str, alert_data: Dict) -> str:
        """Generate formatted alert notification"""
        
        severity_emoji = {
            'critical': '🔴',
            'high': '🟠', 
            'medium': '🟡',
            'low': '🟢'
        }
        
        severity = alert_data.get('severity', 'medium')
        emoji = severity_emoji.get(severity, '⚪')
        
        notification = f"""{emoji} **{alert_type.upper()} ALERT**

**Time:** {datetime.now().strftime("%Y-%m-%d %H:%M")}
**Severity:** {severity.upper()}
**Region:** {alert_data.get('region', 'All')}

**Details:**
{alert_data.get('description', 'No description provided')}

**Recommended Action:**
{alert_data.get('action', 'Review in dashboard')}
"""
        return notification


if __name__ == '__main__':
    generator = InsightGenerator()
    
    test_metrics = {
        'on_time_delivery_rate': 88.5,
        'fleet_utilization': 82.3,
        'customer_satisfaction': 7.5,
        'revenue_growth': 5.2,
        'cost_per_shipment': 45.20,
        'regional_performance': {
            'Northeast': {'on_time': 91.2, 'utilization': 85.1},
            'Southwest': {'on_time': 82.1, 'utilization': 78.4},
            'Midwest': {'on_time': 89.5, 'utilization': 84.2}
        }
    }
    
    print("=== Performance Insight ===")
    insight = generator.generate_performance_insight(test_metrics)
    print(insight)
    
    print("\n=== Natural Language Query ===")
    answer = generator.answer_question(
        "Which region has the lowest on-time delivery rate?",
        test_metrics
    )
    print(answer)
