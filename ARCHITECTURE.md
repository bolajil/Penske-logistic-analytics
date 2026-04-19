# Penske Logistics Analytics — LangGraph Agentic Architecture

## Overview

This project uses a **LangGraph-based multi-agent orchestration** pattern to power an intelligent logistics analytics platform. A central **Planner** routes user queries to specialized agents, each equipped with domain-specific tools. The system supports conditional logic, error handling, retry control, and optional human-in-the-loop review.

## Architecture Diagram

```
                         ┌──────────────┐
                         │  USER INPUT  │
                         └──────┬───────┘
                                │
                         ┌──────▼───────┐
                         │   Planner    │  (LLM classifies intent → routes)
                         └──┬───┬───┬───┘
                            │   │   │
              ┌─────────────┘   │   └─────────────┐
              │                 │                  │
     ┌────────▼────────┐ ┌─────▼──────┐ ┌─────────▼────────┐
     │ Performance     │ │ Forecast   │ │ Customer         │
     │ Agent           │ │ Agent      │ │ Agent            │
     └───────┬─────────┘ └─────┬──────┘ └────────┬─────────┘
             │                 │                  │
     ┌───────▼─────┐   ┌──────▼──────┐  ┌───────▼──────┐
     │ KPI Tool    │   │ Demand Tool │  │ Lead Scorer  │
     │ Anomaly Tool│   │ Fleet Tool  │  │ Churn Tool   │
     │ Trend Tool  │   │ Capacity    │  │ Segment Tool │
     └─────────────┘   └─────────────┘  └──────────────┘
              │                 │                  │
              └────────┬───────┘──────────┬───────┘
                       │                  │
                ┌──────▼──────┐    ┌──────▼──────┐
                │  RAG Agent  │    │ Condition   │
                │ (context)   │    │ Check       │
                └──────┬──────┘    └──────┬──────┘
                       │                  │
                ┌──────▼──────┐    ┌──────▼──────┐
                │ Human       │    │ Error       │
                │ Review      │    │ Handling    │
                │ (optional)  │    │ + Retry     │
                └──────┬──────┘    └─────────────┘
                       │
                ┌──────▼──────┐
                │ Final Output│
                │ (synthesis) │
                └─────────────┘
```

## Components

### 1. Planner Node
- Receives raw user query
- Uses LLM to classify intent into one or more categories:
  - `performance` — KPIs, delivery rates, fleet utilization, anomalies
  - `forecast` — Demand prediction, capacity planning, resource allocation
  - `customer` — Lead scoring, churn prediction, customer segmentation
  - `knowledge` — RAG-based document Q&A over logistics SOPs/policies
- Outputs a plan: list of agents to invoke, in order or parallel

### 2. Specialized Agents

| Agent | Module Wrapped | Tools |
|-------|---------------|-------|
| **PerformanceAgent** | `service_performance.py` | KPI calculation, anomaly detection, trend analysis, regional benchmarks |
| **ForecastAgent** | `resource_prediction.py` | Demand forecasting, fleet sizing, capacity optimization, staffing prediction |
| **CustomerAgent** | `customer_acquisition.py` | Lead scoring, churn prediction, customer segmentation, retention analysis |
| **RAGAgent** | `rag_engine.py` | Document search, context retrieval, policy Q&A |

### 3. Tools Layer
Each tool is a thin wrapper around existing module functions, decorated with `@tool` for LangChain/LangGraph compatibility:

- **kpi_tool** — `ServicePerformanceAnalyzer.calculate_overall_kpis()`
- **anomaly_tool** — `ServicePerformanceAnalyzer.detect_anomalies()`
- **trend_tool** — `ServicePerformanceAnalyzer.analyze_trends()`
- **demand_forecast_tool** — `DemandForecaster.predict()`
- **fleet_optimization_tool** — `FleetOptimizer.optimize()`
- **lead_score_tool** — `LeadScorer.score_leads()`
- **churn_prediction_tool** — `ChurnPredictor.predict()`
- **rag_search_tool** — `RAGEngine.query()`

### 4. State Graph (LangGraph)
```python
StateGraph:
  START → planner → route_agents
  route_agents →(conditional)→ performance_agent | forecast_agent | customer_agent | rag_agent
  *_agent → condition_check
  condition_check →(conditional)→ human_review | synthesize
  human_review → synthesize
  synthesize → END

  # Error handling: any node failure → error_handler → retry or fallback
```

### 5. Shared State Schema
```python
class PenskeState(TypedDict):
    query: str                          # Original user question
    plan: List[str]                     # Agents to invoke
    agent_outputs: Dict[str, Any]       # Results from each agent
    rag_context: str                    # Retrieved document context
    needs_review: bool                  # Flag for human-in-the-loop
    error: Optional[str]               # Error message if any
    retry_count: int                    # Current retry attempt
    final_answer: str                   # Synthesized response
```

### 6. Key Features
- **Multi-Agent Systems** — Parallel or sequential agent invocation based on query complexity
- **Conditional Logic** — Planner decides which agents to invoke; condition check gates human review
- **Human-in-the-Loop** — High-stakes recommendations (fleet purchases, staffing changes) flagged for review
- **Retry & Control** — Failed tool calls retry up to 3x with exponential backoff; falls back to mock responses
- **RAG Context** — Every agent response is enriched with relevant document context from ChromaDB

## File Structure
```
src/
├── agents/
│   ├── __init__.py
│   ├── state.py              # PenskeState schema
│   ├── orchestrator.py       # LangGraph StateGraph definition
│   ├── planner.py            # Intent classification + planning
│   ├── performance_agent.py  # Wraps service_performance.py
│   ├── forecast_agent.py     # Wraps resource_prediction.py
│   ├── customer_agent.py     # Wraps customer_acquisition.py
│   └── rag_agent.py          # Wraps rag_engine.py
├── tools/
│   ├── __init__.py
│   ├── performance_tools.py  # @tool wrappers for KPI, anomaly, trend
│   ├── forecast_tools.py     # @tool wrappers for demand, fleet, capacity
│   ├── customer_tools.py     # @tool wrappers for lead, churn, segment
│   └── rag_tools.py          # @tool wrapper for RAG search
```

## Dependencies
- `langgraph >= 0.2.0`
- `langchain >= 0.3.0`
- `langchain-openai >= 0.2.0`
- `chromadb >= 0.4.0`
- Existing: `scikit-learn`, `xgboost`, `pandas`, `numpy`
