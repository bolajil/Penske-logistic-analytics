# Penske Interview Deep Dive
## Advanced Topics & Detailed Examples

---

# 1. GENAI AGENTS - DEEP DIVE

## Agent Memory Systems

### Short-Term Memory (Conversation)
```python
from langchain.memory import ConversationBufferWindowMemory

# Keep last 10 exchanges
memory = ConversationBufferWindowMemory(k=10)

# Or use token-based limit
from langchain.memory import ConversationTokenBufferMemory
memory = ConversationTokenBufferMemory(
    llm=llm,
    max_token_limit=2000
)
```

### Long-Term Memory (Persistent)
```python
from langchain.memory import VectorStoreRetrieverMemory

# Store important facts in vector DB
vectorstore = Chroma(embedding_function=embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

memory = VectorStoreRetrieverMemory(
    retriever=retriever,
    memory_key="history"
)

# Agent recalls relevant past interactions
memory.save_context(
    {"input": "Our main warehouse is in Chicago"},
    {"output": "I'll remember that your main warehouse is in Chicago."}
)
```

### Entity Memory (Track Facts)
```python
from langchain.memory import ConversationEntityMemory

memory = ConversationEntityMemory(llm=llm)

# Automatically extracts and tracks entities
# User: "John Smith handles Northeast shipments"
# Memory stores: {"John Smith": "handles Northeast shipments"}
```

## Multi-Agent Architectures

### Supervisor Pattern
```python
from langgraph.graph import StateGraph, END

# Define agent states
class AgentState(TypedDict):
    messages: list
    next_agent: str

# Supervisor decides which agent to call
def supervisor(state):
    response = supervisor_llm.invoke(
        f"Given this task: {state['messages'][-1]}, "
        f"which agent should handle it? Options: analyst, forecaster, reporter"
    )
    return {"next_agent": response.agent}

# Build graph
graph = StateGraph(AgentState)
graph.add_node("supervisor", supervisor)
graph.add_node("analyst", analyst_agent)
graph.add_node("forecaster", forecaster_agent)
graph.add_node("reporter", reporter_agent)

graph.add_conditional_edges(
    "supervisor",
    lambda x: x["next_agent"],
    {
        "analyst": "analyst",
        "forecaster": "forecaster",
        "reporter": "reporter",
        "done": END
    }
)
```

### Debate Pattern (Self-Verification)
```python
def debate_agents(query: str) -> str:
    # Agent 1 proposes answer
    proposal = agent_1.invoke(f"Answer this: {query}")
    
    # Agent 2 critiques
    critique = agent_2.invoke(
        f"Critique this answer for accuracy and completeness:\n"
        f"Question: {query}\n"
        f"Answer: {proposal}"
    )
    
    # Agent 1 refines based on critique
    refined = agent_1.invoke(
        f"Refine your answer based on this critique:\n"
        f"Original: {proposal}\n"
        f"Critique: {critique}"
    )
    
    return refined
```

## Tool Design Best Practices

### Tool Schema Design
```python
from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

class ShipmentQueryInput(BaseModel):
    """Input schema for shipment queries."""
    
    start_date: str = Field(
        description="Start date in YYYY-MM-DD format"
    )
    end_date: str = Field(
        description="End date in YYYY-MM-DD format"
    )
    region: Optional[str] = Field(
        default=None,
        description="Region filter: Northeast, Midwest, Southeast, West"
    )
    status: Optional[str] = Field(
        default=None,
        description="Shipment status: pending, in_transit, delivered, delayed"
    )
    limit: int = Field(
        default=100,
        description="Maximum number of results to return"
    )

def query_shipments(
    start_date: str,
    end_date: str,
    region: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100
) -> str:
    """Query shipment data from the database."""
    
    # Build query
    query = f"""
    SELECT shipment_id, origin, destination, status, ship_date
    FROM shipments
    WHERE ship_date BETWEEN '{start_date}' AND '{end_date}'
    """
    
    if region:
        query += f" AND region = '{region}'"
    if status:
        query += f" AND status = '{status}'"
    
    query += f" LIMIT {limit}"
    
    result = execute_query(query)
    return result.to_markdown()

shipment_tool = StructuredTool.from_function(
    func=query_shipments,
    name="query_shipments",
    description="Query shipment data by date range, region, and status",
    args_schema=ShipmentQueryInput
)
```

### Tool Error Handling
```python
from langchain.tools import Tool
from tenacity import retry, stop_after_attempt, wait_exponential

class RobustTool:
    """Tool with built-in error handling and retries."""
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def execute_with_retry(self, func, *args, **kwargs):
        return func(*args, **kwargs)
    
    def safe_execute(self, func, *args, **kwargs):
        try:
            return self.execute_with_retry(func, *args, **kwargs)
        except Exception as e:
            # Return structured error for LLM to handle
            return f"ERROR: {type(e).__name__}: {str(e)}. Please try a different approach."
```

---

# 2. MCP PROTOCOL - DEEP DIVE

## Complete MCP Server Implementation

```python
#!/usr/bin/env python3
"""
Penske Logistics MCP Server
Complete implementation with authentication, logging, and error handling.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("penske-mcp")

# Initialize server
server = Server("penske-logistics")

# Database connection (simplified)
class SnowflakeConnection:
    async def execute(self, query: str) -> dict:
        # Real implementation would use snowflake-connector-python
        logger.info(f"Executing query: {query[:100]}...")
        # Simulated response
        return {"status": "success", "rows": 100}

db = SnowflakeConnection()


# ============================================================================
# RESOURCES - Data exposed by the server
# ============================================================================

@server.list_resources()
async def list_resources() -> list[types.Resource]:
    """List available data resources."""
    return [
        types.Resource(
            uri="penske://shipments/today",
            name="Today's Shipments",
            description="Real-time shipment data for today",
            mimeType="application/json"
        ),
        types.Resource(
            uri="penske://metrics/kpis",
            name="KPI Dashboard",
            description="Current KPI metrics",
            mimeType="application/json"
        ),
        types.Resource(
            uri="penske://alerts/active",
            name="Active Alerts",
            description="Currently active operational alerts",
            mimeType="application/json"
        )
    ]

@server.read_resource()
async def read_resource(uri: str) -> str:
    """Read a specific resource."""
    logger.info(f"Reading resource: {uri}")
    
    if uri == "penske://shipments/today":
        result = await db.execute(
            "SELECT * FROM shipments WHERE ship_date = CURRENT_DATE"
        )
        return str(result)
    
    elif uri == "penske://metrics/kpis":
        return """{
            "on_time_rate": 94.7,
            "total_shipments": 1245,
            "avg_delay_hours": 1.8,
            "fleet_utilization": 87.3
        }"""
    
    elif uri == "penske://alerts/active":
        return """[
            {"level": "warning", "message": "Weather delay expected in Northeast"},
            {"level": "info", "message": "High volume period starting tomorrow"}
        ]"""
    
    raise ValueError(f"Unknown resource: {uri}")


# ============================================================================
# TOOLS - Functions the LLM can call
# ============================================================================

@server.list_tools()
async def list_tools() -> list[types.Tool]:
    """List available tools."""
    return [
        types.Tool(
            name="query_shipments",
            description="Query shipment data from the database. Returns shipment details including status, dates, and locations.",
            inputSchema={
                "type": "object",
                "properties": {
                    "date_range": {
                        "type": "string",
                        "description": "Date range in format 'YYYY-MM-DD to YYYY-MM-DD'"
                    },
                    "region": {
                        "type": "string",
                        "enum": ["Northeast", "Midwest", "Southeast", "West"],
                        "description": "Filter by region"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["pending", "in_transit", "delivered", "delayed"],
                        "description": "Filter by shipment status"
                    }
                },
                "required": ["date_range"]
            }
        ),
        types.Tool(
            name="get_demand_forecast",
            description="Get ML-based demand forecast for a region",
            inputSchema={
                "type": "object",
                "properties": {
                    "region": {
                        "type": "string",
                        "enum": ["Northeast", "Midwest", "Southeast", "West"]
                    },
                    "days_ahead": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 30,
                        "description": "Number of days to forecast"
                    }
                },
                "required": ["region", "days_ahead"]
            }
        ),
        types.Tool(
            name="calculate_route_efficiency",
            description="Calculate efficiency metrics for a specific route",
            inputSchema={
                "type": "object",
                "properties": {
                    "origin": {"type": "string"},
                    "destination": {"type": "string"},
                    "include_alternatives": {"type": "boolean", "default": False}
                },
                "required": ["origin", "destination"]
            }
        ),
        types.Tool(
            name="send_dispatch_alert",
            description="Send an alert to dispatch team. Use only for urgent operational matters.",
            inputSchema={
                "type": "object",
                "properties": {
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "critical"]
                    },
                    "message": {
                        "type": "string",
                        "maxLength": 500
                    },
                    "affected_shipments": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": ["priority", "message"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Execute a tool and return results."""
    logger.info(f"Tool called: {name} with args: {arguments}")
    
    try:
        if name == "query_shipments":
            result = await handle_query_shipments(arguments)
        elif name == "get_demand_forecast":
            result = await handle_demand_forecast(arguments)
        elif name == "calculate_route_efficiency":
            result = await handle_route_efficiency(arguments)
        elif name == "send_dispatch_alert":
            result = await handle_dispatch_alert(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
        
        return [types.TextContent(type="text", text=str(result))]
    
    except Exception as e:
        logger.error(f"Tool error: {e}")
        return [types.TextContent(
            type="text",
            text=f"Error executing {name}: {str(e)}"
        )]

async def handle_query_shipments(args: dict) -> dict:
    """Handle shipment query."""
    date_range = args["date_range"]
    region = args.get("region")
    status = args.get("status")
    
    # Parse date range
    start, end = date_range.split(" to ")
    
    query = f"""
    SELECT shipment_id, origin, destination, status, ship_date, 
           estimated_arrival, actual_arrival, delay_minutes
    FROM shipments
    WHERE ship_date BETWEEN '{start}' AND '{end}'
    """
    
    if region:
        query += f" AND region = '{region}'"
    if status:
        query += f" AND status = '{status}'"
    
    query += " ORDER BY ship_date DESC LIMIT 100"
    
    result = await db.execute(query)
    return result

async def handle_demand_forecast(args: dict) -> dict:
    """Handle demand forecast request."""
    region = args["region"]
    days = args["days_ahead"]
    
    # Call ML model endpoint
    forecast = {
        "region": region,
        "forecast_days": days,
        "predictions": [
            {"date": f"2024-01-{15+i}", "volume": 1200 + i*50, "confidence": 0.92}
            for i in range(days)
        ],
        "model_version": "demand_v2.3",
        "generated_at": datetime.now().isoformat()
    }
    
    return forecast

async def handle_route_efficiency(args: dict) -> dict:
    """Calculate route efficiency."""
    origin = args["origin"]
    destination = args["destination"]
    
    return {
        "route": f"{origin} → {destination}",
        "efficiency_score": 0.87,
        "avg_time_hours": 4.5,
        "fuel_cost_estimate": 125.50,
        "recommendation": "Optimal route via I-80"
    }

async def handle_dispatch_alert(args: dict) -> dict:
    """Send dispatch alert with validation."""
    priority = args["priority"]
    message = args["message"]
    
    # Validate: don't send critical alerts without affected shipments
    if priority == "critical" and not args.get("affected_shipments"):
        raise ValueError("Critical alerts must include affected shipments")
    
    # Log for audit
    logger.warning(f"DISPATCH ALERT [{priority}]: {message}")
    
    return {
        "status": "sent",
        "alert_id": "ALT-2024-001234",
        "timestamp": datetime.now().isoformat()
    }


# ============================================================================
# PROMPTS - Pre-built prompt templates
# ============================================================================

@server.list_prompts()
async def list_prompts() -> list[types.Prompt]:
    """List available prompt templates."""
    return [
        types.Prompt(
            name="daily_summary",
            description="Generate a daily operations summary",
            arguments=[
                types.PromptArgument(
                    name="date",
                    description="Date for summary (YYYY-MM-DD)",
                    required=False
                )
            ]
        ),
        types.Prompt(
            name="delay_analysis",
            description="Analyze delays for a specific region",
            arguments=[
                types.PromptArgument(
                    name="region",
                    description="Region to analyze",
                    required=True
                )
            ]
        )
    ]

@server.get_prompt()
async def get_prompt(name: str, arguments: dict) -> types.GetPromptResult:
    """Get a specific prompt template."""
    
    if name == "daily_summary":
        date = arguments.get("date", "today")
        return types.GetPromptResult(
            description="Daily operations summary prompt",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"""Generate a comprehensive daily operations summary for {date}.

Include:
1. Total shipments and on-time rate
2. Any delays or issues
3. Regional performance breakdown
4. Key alerts or concerns
5. Recommendations for tomorrow

Use the available tools to gather data before summarizing."""
                    )
                )
            ]
        )
    
    raise ValueError(f"Unknown prompt: {name}")


# ============================================================================
# MAIN
# ============================================================================

async def main():
    """Run the MCP server."""
    logger.info("Starting Penske Logistics MCP Server...")
    
    async with mcp.server.stdio.stdio_server() as (read, write):
        await server.run(
            read,
            write,
            InitializationOptions(
                server_name="penske-logistics",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())
```

## MCP Security Best Practices

```python
# 1. Input Validation
from pydantic import BaseModel, validator

class ToolInput(BaseModel):
    query: str
    
    @validator('query')
    def validate_query(cls, v):
        # Prevent SQL injection
        dangerous = ['DROP', 'DELETE', 'TRUNCATE', 'UPDATE', '--', ';']
        for word in dangerous:
            if word.upper() in v.upper():
                raise ValueError(f"Dangerous pattern detected: {word}")
        return v

# 2. Authentication Middleware
class AuthenticatedServer(Server):
    def __init__(self, name: str, api_key_validator):
        super().__init__(name)
        self.validate_key = api_key_validator
    
    async def handle_request(self, request):
        api_key = request.headers.get("X-API-Key")
        if not self.validate_key(api_key):
            raise PermissionError("Invalid API key")
        return await super().handle_request(request)

# 3. Rate Limiting
from collections import defaultdict
import time

class RateLimiter:
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window = window_seconds
        self.requests = defaultdict(list)
    
    def check(self, client_id: str) -> bool:
        now = time.time()
        # Clean old requests
        self.requests[client_id] = [
            t for t in self.requests[client_id]
            if now - t < self.window
        ]
        # Check limit
        if len(self.requests[client_id]) >= self.max_requests:
            return False
        self.requests[client_id].append(now)
        return True

rate_limiter = RateLimiter(max_requests=100, window_seconds=60)

# 4. Audit Logging
import json
from datetime import datetime

def audit_log(tool_name: str, args: dict, result: Any, user_id: str):
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "user_id": user_id,
        "tool": tool_name,
        "arguments": args,
        "result_summary": str(result)[:500],
        "success": "error" not in str(result).lower()
    }
    # Write to audit log (file, database, or logging service)
    logger.info(f"AUDIT: {json.dumps(log_entry)}")
```

---

# 3. ADVANCED RAG TECHNIQUES

## Contextual Compression

```python
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor

# Base retriever
base_retriever = vectorstore.as_retriever(search_kwargs={"k": 10})

# Compressor extracts only relevant parts
compressor = LLMChainExtractor.from_llm(llm)

compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=base_retriever
)

# Returns only the relevant sentences/paragraphs from each document
docs = compression_retriever.get_relevant_documents(
    "What are the safety procedures for hazmat shipments?"
)
```

## Parent Document Retrieval

```python
from langchain.retrievers import ParentDocumentRetriever
from langchain.storage import InMemoryStore

# Store full documents
docstore = InMemoryStore()

# Small chunks for precise retrieval, but return full parent document
child_splitter = RecursiveCharacterTextSplitter(chunk_size=400)
parent_splitter = RecursiveCharacterTextSplitter(chunk_size=2000)

retriever = ParentDocumentRetriever(
    vectorstore=vectorstore,
    docstore=docstore,
    child_splitter=child_splitter,
    parent_splitter=parent_splitter
)

# Search finds small chunk, but returns larger context
docs = retriever.get_relevant_documents("hazmat procedures")
```

## Multi-Query Retrieval

```python
from langchain.retrievers.multi_query import MultiQueryRetriever

# LLM generates multiple query variations
retriever = MultiQueryRetriever.from_llm(
    retriever=vectorstore.as_retriever(),
    llm=llm
)

# User: "shipment delays"
# Generated queries:
# 1. "What causes shipment delays?"
# 2. "How to reduce delivery delays?"
# 3. "Delay statistics and trends"
# Results merged and deduplicated
```

## Self-Query Retrieval (Structured Filters)

```python
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.chains.query_constructor.base import AttributeInfo

metadata_field_info = [
    AttributeInfo(
        name="department",
        description="The department: operations, safety, maintenance",
        type="string"
    ),
    AttributeInfo(
        name="doc_type",
        description="Type: procedure, policy, training, report",
        type="string"
    ),
    AttributeInfo(
        name="last_updated",
        description="When the document was last updated",
        type="date"
    )
]

retriever = SelfQueryRetriever.from_llm(
    llm=llm,
    vectorstore=vectorstore,
    document_contents="Penske logistics documentation",
    metadata_field_info=metadata_field_info
)

# User: "safety procedures updated in 2024"
# Automatically creates filter: doc_type='procedure' AND department='safety' AND last_updated >= 2024-01-01
```

## Ensemble Retrieval

```python
from langchain.retrievers import EnsembleRetriever
from langchain.retrievers import BM25Retriever

# Vector retriever
vector_retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

# BM25 keyword retriever
bm25_retriever = BM25Retriever.from_documents(documents)
bm25_retriever.k = 5

# Combine with weights
ensemble_retriever = EnsembleRetriever(
    retrievers=[vector_retriever, bm25_retriever],
    weights=[0.6, 0.4]  # 60% vector, 40% keyword
)
```

---

# 4. PRODUCTION EVALUATION SYSTEM

## Comprehensive Eval Pipeline

```python
import pandas as pd
from datetime import datetime
from typing import List, Dict
import json

class ProductionEvaluator:
    """
    Complete evaluation system for production LLM agents.
    """
    
    def __init__(self, llm_judge, metrics_client):
        self.judge = llm_judge
        self.metrics = metrics_client
        
    def evaluate_response(
        self,
        query: str,
        response: str,
        context: List[str],
        ground_truth: str = None
    ) -> Dict:
        """Run all evaluations on a single response."""
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "response_length": len(response)
        }
        
        # 1. Relevance - Does response answer the question?
        results["relevance"] = self._eval_relevance(query, response)
        
        # 2. Faithfulness - Is response grounded in context?
        results["faithfulness"] = self._eval_faithfulness(response, context)
        
        # 3. Coherence - Is response well-structured?
        results["coherence"] = self._eval_coherence(response)
        
        # 4. Accuracy - Compare to ground truth if available
        if ground_truth:
            results["accuracy"] = self._eval_accuracy(response, ground_truth)
        
        # 5. Safety - Check for harmful content
        results["safety"] = self._eval_safety(response)
        
        # 6. Domain-specific checks
        results["domain_validity"] = self._eval_domain(query, response)
        
        # Calculate overall score
        weights = {
            "relevance": 0.25,
            "faithfulness": 0.25,
            "coherence": 0.15,
            "accuracy": 0.20,
            "safety": 0.10,
            "domain_validity": 0.05
        }
        
        results["overall_score"] = sum(
            results.get(k, 0) * v 
            for k, v in weights.items()
            if k in results
        ) / sum(v for k, v in weights.items() if k in results)
        
        # Log metrics
        self.metrics.log(results)
        
        return results
    
    def _eval_relevance(self, query: str, response: str) -> float:
        """Evaluate if response answers the question."""
        prompt = f"""
        Rate how well this response answers the question.
        Score 0.0 to 1.0 where 1.0 = perfectly answers.
        
        Question: {query}
        Response: {response}
        
        Return only a number.
        """
        score = float(self.judge.invoke(prompt).strip())
        return min(max(score, 0), 1)  # Clamp to [0,1]
    
    def _eval_faithfulness(self, response: str, context: List[str]) -> float:
        """Check if response is grounded in provided context."""
        context_text = "\n\n".join(context)
        prompt = f"""
        Check if ALL claims in the response are supported by the context.
        Score 0.0 to 1.0 where 1.0 = fully supported, 0.0 = hallucinated.
        
        Context:
        {context_text}
        
        Response:
        {response}
        
        Return only a number.
        """
        return float(self.judge.invoke(prompt).strip())
    
    def _eval_coherence(self, response: str) -> float:
        """Evaluate logical flow and structure."""
        prompt = f"""
        Rate the coherence of this response.
        Consider: logical flow, clear structure, no contradictions.
        Score 0.0 to 1.0.
        
        Response: {response}
        
        Return only a number.
        """
        return float(self.judge.invoke(prompt).strip())
    
    def _eval_accuracy(self, response: str, ground_truth: str) -> float:
        """Compare response to known correct answer."""
        prompt = f"""
        Compare the response to the ground truth.
        Score 0.0 to 1.0 based on factual agreement.
        
        Ground Truth: {ground_truth}
        Response: {response}
        
        Return only a number.
        """
        return float(self.judge.invoke(prompt).strip())
    
    def _eval_safety(self, response: str) -> float:
        """Check for harmful, biased, or inappropriate content."""
        # Use Azure Content Safety or similar
        # Returns 1.0 if safe, lower if issues detected
        checks = [
            "harmful content",
            "PII exposure",
            "bias",
            "misinformation"
        ]
        
        prompt = f"""
        Check this response for:
        - Harmful content
        - PII/sensitive data exposure
        - Bias or discrimination
        - Dangerous misinformation
        
        Response: {response}
        
        If ALL clear, return 1.0. Otherwise return lower score.
        Return only a number.
        """
        return float(self.judge.invoke(prompt).strip())
    
    def _eval_domain(self, query: str, response: str) -> float:
        """Domain-specific validation for logistics."""
        prompt = f"""
        As a logistics domain expert, check this response for:
        - Valid shipment ID formats (if mentioned)
        - Realistic delivery times
        - Correct terminology
        - Sensible operational recommendations
        
        Query: {query}
        Response: {response}
        
        Score 0.0 to 1.0 for domain accuracy.
        Return only a number.
        """
        return float(self.judge.invoke(prompt).strip())
    
    def run_eval_suite(
        self,
        test_cases: List[Dict],
        output_path: str = "eval_results.json"
    ) -> pd.DataFrame:
        """Run evaluation on a test suite."""
        
        results = []
        for case in test_cases:
            result = self.evaluate_response(
                query=case["query"],
                response=case["response"],
                context=case.get("context", []),
                ground_truth=case.get("ground_truth")
            )
            result["test_id"] = case.get("id")
            results.append(result)
        
        df = pd.DataFrame(results)
        
        # Summary statistics
        summary = {
            "total_cases": len(results),
            "avg_overall": df["overall_score"].mean(),
            "avg_relevance": df["relevance"].mean(),
            "avg_faithfulness": df["faithfulness"].mean(),
            "avg_safety": df["safety"].mean(),
            "failing_cases": len(df[df["overall_score"] < 0.7])
        }
        
        # Save results
        with open(output_path, 'w') as f:
            json.dump({
                "summary": summary,
                "results": results
            }, f, indent=2)
        
        return df


# Usage
evaluator = ProductionEvaluator(judge_llm, metrics_client)

# Single evaluation
result = evaluator.evaluate_response(
    query="What are shipment delays in Chicago?",
    response="Chicago has 15 delayed shipments...",
    context=["Retrieved context here..."]
)

# Batch evaluation
test_suite = [
    {
        "id": "TC001",
        "query": "What is the on-time rate?",
        "response": "The on-time rate is 94.7%",
        "ground_truth": "94.7%",
        "context": ["KPI data..."]
    },
    # More test cases...
]

results_df = evaluator.run_eval_suite(test_suite)
```

---

# 5. MLOPS FOR LLM SYSTEMS

## Complete Observability Setup

```python
# config/observability.py
import os
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from prometheus_client import Counter, Histogram, Gauge, start_http_server

# ============================================================================
# TRACING SETUP
# ============================================================================

# Initialize OpenTelemetry
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer("logistics-agent")

# Export to observability backend (Jaeger, DataDog, etc.)
otlp_exporter = OTLPSpanExporter(endpoint=os.environ["OTLP_ENDPOINT"])
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(otlp_exporter)
)

# ============================================================================
# PROMETHEUS METRICS
# ============================================================================

# Counters
llm_requests = Counter(
    'llm_requests_total',
    'Total LLM API requests',
    ['model', 'endpoint', 'status']
)

tool_executions = Counter(
    'agent_tool_executions_total',
    'Total tool executions',
    ['tool_name', 'status']
)

guardrail_triggers = Counter(
    'guardrail_triggers_total',
    'Guardrail activations',
    ['guardrail_type', 'action']
)

# Histograms
llm_latency = Histogram(
    'llm_request_duration_seconds',
    'LLM request latency',
    ['model'],
    buckets=[0.1, 0.25, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0]
)

token_usage = Histogram(
    'llm_tokens_used',
    'Tokens per request',
    ['model', 'token_type'],
    buckets=[50, 100, 250, 500, 1000, 2000, 4000, 8000]
)

retrieval_latency = Histogram(
    'retrieval_duration_seconds',
    'RAG retrieval latency',
    buckets=[0.05, 0.1, 0.25, 0.5, 1.0, 2.0]
)

eval_scores = Histogram(
    'eval_score',
    'Evaluation scores',
    ['metric'],
    buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
)

# Gauges
active_sessions = Gauge(
    'active_agent_sessions',
    'Currently active agent sessions'
)

daily_cost = Gauge(
    'llm_daily_cost_dollars',
    'Estimated daily LLM cost'
)


# ============================================================================
# INSTRUMENTED LLM WRAPPER
# ============================================================================

class ObservedLLM:
    """LLM wrapper with full observability."""
    
    def __init__(self, llm, model_name: str):
        self.llm = llm
        self.model_name = model_name
        self.tracer = trace.get_tracer("llm-calls")
    
    def invoke(self, prompt: str, **kwargs) -> str:
        with self.tracer.start_as_current_span("llm_invoke") as span:
            span.set_attribute("model", self.model_name)
            span.set_attribute("prompt_length", len(prompt))
            
            start_time = time.time()
            
            try:
                response = self.llm.invoke(prompt, **kwargs)
                
                # Record metrics
                duration = time.time() - start_time
                llm_latency.labels(model=self.model_name).observe(duration)
                llm_requests.labels(
                    model=self.model_name,
                    endpoint="invoke",
                    status="success"
                ).inc()
                
                # Token counting (approximate)
                input_tokens = len(prompt.split()) * 1.3
                output_tokens = len(response.split()) * 1.3
                token_usage.labels(
                    model=self.model_name,
                    token_type="input"
                ).observe(input_tokens)
                token_usage.labels(
                    model=self.model_name,
                    token_type="output"
                ).observe(output_tokens)
                
                # Update span
                span.set_attribute("response_length", len(response))
                span.set_attribute("duration_ms", duration * 1000)
                span.set_attribute("status", "success")
                
                return response
                
            except Exception as e:
                llm_requests.labels(
                    model=self.model_name,
                    endpoint="invoke",
                    status="error"
                ).inc()
                span.set_attribute("status", "error")
                span.set_attribute("error", str(e))
                raise


# ============================================================================
# CUSTOM LOGGING
# ============================================================================

import structlog
from datetime import datetime

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
)

logger = structlog.get_logger()

def log_agent_interaction(
    session_id: str,
    user_id: str,
    query: str,
    response: str,
    tools_used: list,
    latency_ms: float,
    token_cost: float
):
    """Log complete agent interaction for analysis."""
    logger.info(
        "agent_interaction",
        session_id=session_id,
        user_id=user_id,
        query=query[:200],  # Truncate for logging
        response_preview=response[:200],
        tools_used=tools_used,
        latency_ms=latency_ms,
        token_cost=token_cost,
        timestamp=datetime.utcnow().isoformat()
    )


# ============================================================================
# ALERTING
# ============================================================================

from dataclasses import dataclass
from typing import Callable

@dataclass
class AlertRule:
    name: str
    condition: Callable[[], bool]
    message: str
    severity: str  # info, warning, critical
    cooldown_minutes: int = 15

class AlertManager:
    def __init__(self, notification_handler):
        self.rules = []
        self.last_fired = {}
        self.notify = notification_handler
    
    def add_rule(self, rule: AlertRule):
        self.rules.append(rule)
    
    def check_all(self):
        now = datetime.now()
        for rule in self.rules:
            # Check cooldown
            last = self.last_fired.get(rule.name)
            if last and (now - last).total_seconds() < rule.cooldown_minutes * 60:
                continue
            
            # Check condition
            if rule.condition():
                self.notify(rule)
                self.last_fired[rule.name] = now

# Define alert rules
alerts = AlertManager(send_slack_alert)

alerts.add_rule(AlertRule(
    name="high_latency",
    condition=lambda: get_p95_latency() > 5.0,
    message="Agent P95 latency > 5 seconds",
    severity="warning"
))

alerts.add_rule(AlertRule(
    name="error_spike",
    condition=lambda: get_error_rate() > 0.05,
    message="Error rate > 5%",
    severity="critical"
))

alerts.add_rule(AlertRule(
    name="cost_overrun",
    condition=lambda: get_daily_cost() > 500,
    message="Daily LLM cost exceeds $500",
    severity="warning"
))
```

---

# 6. INTERVIEW SCENARIO WALKTHROUGHS

## Scenario 1: Design a Dispatch Optimization Agent

**Interviewer:** "Design an agent that helps dispatchers optimize truck assignments."

**Your Answer:**

```
REQUIREMENTS GATHERING:

1. What decisions does the agent help with?
   - Assign trucks to shipments
   - Optimize routes
   - Handle exceptions (delays, cancellations)

2. What data sources are needed?
   - Fleet inventory (truck locations, capacity, maintenance status)
   - Driver schedules and certifications
   - Shipment queue (pickup locations, weights, deadlines)
   - Real-time traffic and weather
   - Historical performance data

3. What are the constraints?
   - Driver hours regulations (HOS)
   - Truck weight limits
   - Delivery time windows
   - Fuel efficiency targets

ARCHITECTURE:

┌─────────────────────────────────────────────────────────────┐
│                 DISPATCH OPTIMIZATION AGENT                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  USER: "Assign trucks for tomorrow's Northeast shipments"   │
│                          │                                   │
│                          ▼                                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                    AGENT (GPT-4)                     │   │
│  │  • Understands dispatcher intent                     │   │
│  │  • Plans multi-step optimization                     │   │
│  │  • Explains recommendations                          │   │
│  └───────────────────────┬─────────────────────────────┘   │
│                          │                                   │
│         ┌────────────────┼────────────────┐                 │
│         ▼                ▼                ▼                 │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐           │
│  │ get_pending│  │ get_fleet  │  │ optimize   │           │
│  │ _shipments │  │ _status    │  │ _routes    │           │
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘           │
│        │               │               │                    │
│        ▼               ▼               ▼                    │
│  ┌──────────────────────────────────────────────────┐      │
│  │                   SNOWFLAKE                       │      │
│  │  shipments | fleet | drivers | routes             │      │
│  └──────────────────────────────────────────────────┘      │
│                                                              │
│  ┌──────────────────────────────────────────────────┐      │
│  │              OPTIMIZATION ENGINE                  │      │
│  │  (OR-Tools / Custom ML model)                     │      │
│  │  • Vehicle routing problem solver                 │      │
│  │  • Constraint satisfaction                        │      │
│  └──────────────────────────────────────────────────┘      │
│                                                              │
│  GUARDRAILS:                                                │
│  • Validate truck/driver assignments are legal              │
│  • Check HOS compliance                                     │
│  • Require human approval for exceptions                    │
└─────────────────────────────────────────────────────────────┘

TOOLS IMPLEMENTATION:

@tool
def get_pending_shipments(region: str, date: str) -> str:
    '''Get shipments awaiting assignment.'''
    query = f"""
    SELECT shipment_id, origin, destination, weight_lbs,
           pickup_window_start, delivery_deadline
    FROM shipments
    WHERE region = '{region}'
      AND scheduled_date = '{date}'
      AND status = 'pending_assignment'
    ORDER BY delivery_deadline
    """
    return execute_query(query)

@tool
def get_fleet_status(region: str) -> str:
    '''Get available trucks and drivers.'''
    query = f"""
    SELECT t.truck_id, t.capacity_lbs, t.current_location,
           d.driver_id, d.hours_remaining, d.certifications
    FROM trucks t
    JOIN drivers d ON t.assigned_driver = d.driver_id
    WHERE t.region = '{region}'
      AND t.status = 'available'
      AND d.hours_remaining > 2
    """
    return execute_query(query)

@tool
def optimize_routes(
    shipments: list,
    trucks: list,
    constraints: dict
) -> str:
    '''Run route optimization algorithm.'''
    # Call OR-Tools or custom solver
    solution = route_optimizer.solve(
        shipments=shipments,
        vehicles=trucks,
        constraints=constraints
    )
    return solution.to_json()

@tool
def create_assignment(
    truck_id: str,
    driver_id: str,
    shipment_ids: list
) -> str:
    '''Create truck-shipment assignment. Requires dispatcher approval.'''
    # Validate constraints
    validate_assignment(truck_id, driver_id, shipment_ids)
    
    # Create pending assignment
    assignment_id = create_pending_assignment(
        truck_id, driver_id, shipment_ids
    )
    
    return f"Assignment {assignment_id} created. Awaiting dispatcher approval."

EXAMPLE INTERACTION:

Dispatcher: "What's the most efficient way to handle tomorrow's 
             Chicago pickups?"

Agent thinking:
1. Get pending Chicago shipments for tomorrow
2. Get available fleet in Chicago area
3. Run route optimization
4. Present recommendations

Agent: "I found 23 pending shipments for Chicago tomorrow. 
        Based on current fleet availability and delivery windows,
        I recommend:
        
        Truck T-1042 (Driver: J. Smith)
        - 8 shipments, 4200 lbs total
        - Route: Loop through South Chicago
        - Est. completion: 3:30 PM
        
        Truck T-1089 (Driver: M. Garcia)
        - 9 shipments, 5100 lbs total
        - Route: North suburbs circuit
        - Est. completion: 4:15 PM
        
        Truck T-1056 (Driver: K. Johnson)
        - 6 shipments, 3800 lbs total
        - Route: West Chicago deliveries
        - Est. completion: 2:45 PM
        
        This optimizes for fuel efficiency while meeting all
        delivery windows. Total miles: 342 (18% less than 
        standard routing).
        
        Should I create these assignments for your approval?"
```

---

## Scenario 2: Debug a Hallucinating Agent

**Interviewer:** "Users report the agent sometimes gives wrong shipment counts. How do you debug this?"

**Your Answer:**

```
DEBUGGING METHODOLOGY:

1. REPRODUCE THE ISSUE
   - Collect specific examples from users
   - Identify patterns (time of day, query type, data conditions)
   
2. TRACE THE PIPELINE
   
   Query: "How many shipments were delayed yesterday?"
   
   ┌─────────────────────────────────────────────────────┐
   │ STEP 1: Query Understanding                         │
   │ Check: Did LLM correctly interpret the question?    │
   │ Log: parsed_intent, extracted_parameters            │
   └───────────────────────┬─────────────────────────────┘
                           │
                           ▼
   ┌─────────────────────────────────────────────────────┐
   │ STEP 2: Tool Selection                              │
   │ Check: Did agent choose correct tool?               │
   │ Log: selected_tool, tool_arguments                  │
   └───────────────────────┬─────────────────────────────┘
                           │
                           ▼
   ┌─────────────────────────────────────────────────────┐
   │ STEP 3: Tool Execution                              │
   │ Check: Did tool return correct data?                │
   │ Log: sql_query, raw_result, row_count               │
   └───────────────────────┬─────────────────────────────┘
                           │
                           ▼
   ┌─────────────────────────────────────────────────────┐
   │ STEP 4: Response Generation                         │
   │ Check: Did LLM correctly interpret results?         │
   │ Log: context_provided, generated_response           │
   └─────────────────────────────────────────────────────┘

3. COMMON CAUSES & FIXES

   CAUSE A: Tool returned wrong data
   - SQL query had wrong date filter
   - Fix: Add query validation and unit tests
   
   CAUSE B: LLM misinterpreted results
   - Result was "145 total, 12 delayed" but LLM said "145 delayed"
   - Fix: Structure tool output more clearly
   
   Before: "Query returned 145 rows with 12 having status=delayed"
   After:  "DELAYED_COUNT: 12\nTOTAL_COUNT: 145\nDELAY_RATE: 8.3%"
   
   CAUSE C: Context window overflow
   - Too much data, LLM lost track
   - Fix: Summarize large results, paginate
   
   CAUSE D: Outdated cached response
   - Agent returned stale data
   - Fix: Add cache invalidation, timestamp responses

4. IMPLEMENTATION OF FIXES

   # Add validation layer
   class ValidatedResponse:
       def __init__(self, query, response, tool_results):
           self.query = query
           self.response = response
           self.tool_results = tool_results
       
       def validate(self) -> bool:
           # Extract numbers from response
           response_numbers = extract_numbers(self.response)
           
           # Compare to actual tool results
           for num in response_numbers:
               if not self._number_exists_in_results(num):
                   logger.warning(
                       f"Potential hallucination: {num} not in results"
                   )
                   return False
           return True
       
       def _number_exists_in_results(self, num) -> bool:
           results_text = str(self.tool_results)
           return str(num) in results_text

   # Add regression test
   def test_delayed_shipment_count():
       # Seed known data
       insert_test_shipments(total=100, delayed=15)
       
       # Run agent
       response = agent.run("How many shipments were delayed yesterday?")
       
       # Verify
       assert "15" in response
       assert "delayed" in response.lower()

5. MONITORING GOING FORWARD

   # Add hallucination detection metric
   hallucination_detected = Counter(
       'hallucination_detected_total',
       'Detected potential hallucinations'
   )
   
   # Alert on spike
   if hallucination_rate > 0.05:
       send_alert("Hallucination rate > 5%")
```

---

*Study these deep dives for technical interview questions. Good luck! 🚀*
