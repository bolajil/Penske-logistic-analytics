# Penske Interview Flashcards
## Quick Review for Senior Data Scientist Role

---

# GENAI AGENTS

## Card 1: What is a GenAI Agent?
**Q:** Define a GenAI agent and its core components.

**A:** An autonomous AI system that:
- **Perceives** - Understands user intent
- **Reasons** - Plans multi-step actions using LLM
- **Acts** - Executes tools and APIs
- **Learns** - Improves from feedback

Components: LLM brain, tools, memory, knowledge base (RAG)

---

## Card 2: Agent Frameworks
**Q:** Name 5 popular agent frameworks and their best use cases.

**A:**
| Framework | Best For |
|-----------|----------|
| **LangChain** | General purpose, tools, chains |
| **LangGraph** | Complex workflows, state machines |
| **AutoGen** | Multi-agent collaboration |
| **CrewAI** | Role-based task delegation |
| **Semantic Kernel** | Microsoft/Azure integration |

---

## Card 3: ReAct Pattern
**Q:** Explain the ReAct pattern for agents.

**A:** **Re**asoning + **Act**ing
```
Thought: I need to find shipment data for Chicago
Action: query_database(region="Chicago")
Observation: Found 145 shipments
Thought: Now I need to calculate delays
Action: calculate_metrics(shipments)
Observation: Average delay: 2.3 hours
Answer: Chicago has 145 shipments with 2.3hr avg delay
```

---

## Card 4: Production Agent Considerations
**Q:** What are key considerations for production agents?

**A:**
- **Reliability**: Retries, fallbacks, circuit breakers
- **Latency**: Streaming, async, caching
- **Cost**: Token optimization, model routing
- **Safety**: Input validation, output filtering, guardrails
- **Observability**: Logging, tracing, metrics

---

# MCP (MODEL CONTEXT PROTOCOL)

## Card 5: What is MCP?
**Q:** What is MCP and why is it important?

**A:** Anthropic's open standard for connecting AI to external data/tools.

**Key concepts:**
- **Resources** - Data the server exposes (files, DB records)
- **Tools** - Functions LLM can call
- **Prompts** - Pre-built templates
- **Sampling** - Server requests LLM completion

**Why it matters:** Standardized, secure enterprise integrations

---

## Card 6: MCP Architecture
**Q:** Draw the MCP architecture.

**A:**
```
Host (LLM)  ◀──JSON-RPC──▶  MCP Protocol  ◀──JSON-RPC──▶  Server (Tool)

Examples:                                    Examples:
- Claude Desktop                             - Database server
- VS Code Copilot                            - File system
- Custom agents                              - API integrations
```

---

## Card 7: MCP Server Example
**Q:** How do you build an MCP server?

**A:**
```python
from mcp.server import Server
import mcp.types as types

server = Server("logistics-mcp")

@server.list_tools()
async def list_tools():
    return [types.Tool(
        name="query_shipments",
        description="Query shipment data",
        inputSchema={...}
    )]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "query_shipments":
        result = await query_database(arguments)
        return [types.TextContent(type="text", text=str(result))]
```

---

# KNOWLEDGE BASES & RAG

## Card 8: RAG Pipeline
**Q:** Explain the RAG pipeline phases.

**A:**
```
INDEXING:  Documents → Chunk → Embed → Vector DB

RETRIEVAL: Query → Embed Query → Vector Search → Top-K docs

GENERATION: Query + Context → LLM → Response
```

---

## Card 9: Vector Databases
**Q:** Compare popular vector databases.

**A:**
| Database | Best For |
|----------|----------|
| **Pinecone** | Production scale, managed |
| **Weaviate** | Hybrid search, GraphQL |
| **Chroma** | Prototyping, embedded |
| **Azure AI Search** | Enterprise, Azure integration |
| **pgvector** | Postgres users, SQL |

---

## Card 10: Advanced RAG Techniques
**Q:** Name 3 advanced RAG techniques.

**A:**
1. **Hybrid Search**: Combine vector + BM25 keyword search
2. **Re-ranking**: Use cross-encoder to re-score results
3. **Semantic Chunking**: Chunk by meaning, not arbitrary splits

```python
# Hybrid search
final_score = alpha * vector_score + (1-alpha) * bm25_score
```

---

## Card 11: Chunking Strategy
**Q:** What's a good chunking strategy for enterprise docs?

**A:**
```python
RecursiveCharacterTextSplitter(
    chunk_size=1000,      # tokens
    chunk_overlap=200,    # context continuity
    separators=["\n\n", "\n", ".", " "]  # respect structure
)
```

**Key:** Preserve document structure (sections, paragraphs)

---

# AZURE CLOUD

## Card 12: Azure OpenAI Setup
**Q:** How do you configure Azure OpenAI?

**A:**
```python
from openai import AzureOpenAI

client = AzureOpenAI(
    api_key=os.environ["AZURE_OPENAI_KEY"],
    api_version="2024-02-15-preview",
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"]
)

response = client.chat.completions.create(
    model="gpt-4-turbo",  # deployment name
    messages=[...],
    temperature=0.7
)
```

---

## Card 13: Azure AI Search Vector Query
**Q:** How do you perform vector search in Azure AI Search?

**A:**
```python
from azure.search.documents.models import VectorizedQuery

vector_query = VectorizedQuery(
    vector=embedding,
    k_nearest_neighbors=5,
    fields="content_vector"
)

results = search_client.search(
    search_text="query",
    vector_queries=[vector_query],
    top=10
)
```

---

## Card 14: Azure vs AWS Services
**Q:** Map Azure to AWS equivalents.

**A:**
| Azure | AWS |
|-------|-----|
| Azure OpenAI | Amazon Bedrock |
| Azure AI Search | OpenSearch |
| Azure Functions | Lambda |
| Azure Cosmos | DynamoDB |
| Azure Blob | S3 |

---

# SNOWFLAKE

## Card 15: Snowflake Architecture
**Q:** Describe Snowflake's 3-layer architecture.

**A:**
```
1. CLOUD SERVICES - Query optimization, metadata, access control
         ↓
2. COMPUTE LAYER - Virtual warehouses (scale independently)
         ↓
3. STORAGE LAYER - Columnar, compressed, micro-partitions
```

**Key benefit:** Compute and storage scale independently

---

## Card 16: Snowflake for AI
**Q:** How do you use Snowflake for AI/ML?

**A:**
1. **Cortex** - Vector similarity search
2. **Snowpark** - Python/ML in Snowflake
3. **Dynamic Tables** - Real-time feature computation
4. **Time Travel** - Data versioning

```sql
-- Vector search
SELECT VECTOR_COSINE_SIMILARITY(embedding, :query) as sim
FROM documents ORDER BY sim DESC LIMIT 10;
```

---

## Card 17: Snowpark ML Example
**Q:** How do you train ML models in Snowpark?

**A:**
```sql
CREATE PROCEDURE train_model()
LANGUAGE PYTHON
PACKAGES = ('snowflake-snowpark-python', 'xgboost')
AS
$$
def train_model(session):
    df = session.table("SHIPMENTS").to_pandas()
    model = xgb.XGBRegressor()
    model.fit(X, y)
    return "Model trained"
$$;
```

---

# DATABRICKS

## Card 18: Databricks Lakehouse
**Q:** What are the key Databricks components?

**A:**
- **Delta Lake** - ACID transactions on data lake
- **Unity Catalog** - Governance, lineage, access control
- **MLflow** - Experiment tracking, model registry
- **Feature Store** - Centralized feature management
- **Model Serving** - Deploy endpoints

---

## Card 19: MLflow Tracking
**Q:** How do you track experiments in MLflow?

**A:**
```python
import mlflow

with mlflow.start_run(run_name="demand_v1"):
    mlflow.log_params({"n_estimators": 100})
    
    model.fit(X_train, y_train)
    
    mlflow.log_metrics({"rmse": 0.15, "r2": 0.92})
    mlflow.sklearn.log_model(model, "model")
    
    mlflow.register_model(
        f"runs:/{run_id}/model",
        "demand-forecaster"
    )
```

---

## Card 20: Feature Store
**Q:** Why use a Feature Store?

**A:**
- **Consistency**: Same features for training and serving
- **Reusability**: Share features across teams
- **Point-in-time**: Correct features for historical training
- **Lineage**: Track feature dependencies

```python
fs.create_training_set(
    df=labels,
    feature_lookups=[FeatureLookup(table="features", key="id")]
)
```

---

# TRADITIONAL ML

## Card 21: Classification Example
**Q:** How would you predict shipment delays?

**A:**
```python
from sklearn.ensemble import GradientBoostingClassifier

# Features: weather, traffic, driver_exp, distance, weight
X = df[['weather_code', 'traffic_index', 'driver_years', 
        'distance_miles', 'weight_lbs']]
y = df['is_delayed']

model = GradientBoostingClassifier(n_estimators=100)
model.fit(X_train, y_train)

# Evaluate
from sklearn.metrics import f1_score
print(f"F1: {f1_score(y_test, model.predict(X_test))}")
```

---

## Card 22: Time Series Features
**Q:** What lag features should you create for demand forecasting?

**A:**
```python
# Lag features
df['demand_lag_1'] = df['demand'].shift(1)   # yesterday
df['demand_lag_7'] = df['demand'].shift(7)   # last week
df['demand_lag_30'] = df['demand'].shift(30) # last month

# Rolling statistics
df['demand_rolling_7d'] = df['demand'].rolling(7).mean()
df['demand_rolling_std'] = df['demand'].rolling(7).std()

# Calendar features
df['day_of_week'] = df['date'].dt.dayofweek
df['is_weekend'] = df['day_of_week'].isin([5, 6])
```

---

## Card 23: Clustering
**Q:** How do you determine optimal number of clusters?

**A:**
**Elbow Method:**
```python
inertias = []
for k in range(2, 10):
    kmeans = KMeans(n_clusters=k)
    kmeans.fit(X_scaled)
    inertias.append(kmeans.inertia_)

# Plot inertias - look for "elbow"
```

**Silhouette Score:**
```python
from sklearn.metrics import silhouette_score
score = silhouette_score(X, labels)  # Higher is better
```

---

# EVALS & GUARDRAILS

## Card 24: RAG Evaluation Metrics
**Q:** What metrics evaluate RAG systems?

**A:**
| Metric | Measures |
|--------|----------|
| **Faithfulness** | Is answer grounded in context? |
| **Answer Relevancy** | Does answer address question? |
| **Context Precision** | Is retrieved context relevant? |
| **Context Recall** | Is all needed context retrieved? |

```python
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy
results = evaluate(dataset, metrics=[faithfulness, answer_relevancy])
```

---

## Card 25: Guardrails Implementation
**Q:** What guardrails should production agents have?

**A:**
**Input:**
- Length limits
- Prompt injection detection
- PII redaction

**Output:**
- Toxicity filtering
- Factual grounding checks
- Citation validation

**Operational:**
- Rate limiting
- Token budgets
- Query complexity limits

```python
if detect_prompt_injection(query):
    raise SecurityError("Blocked")
```

---

## Card 26: LLM-as-Judge
**Q:** How do you use LLM-as-Judge for evaluation?

**A:**
```python
eval_prompt = f"""
Rate this response 1-5 for:
- Accuracy: Are facts correct?
- Relevance: Does it answer the question?
- Actionability: Can user act on this?

Question: {question}
Response: {response}
Context: {context}

Return JSON: {{"accuracy": X, "relevance": X, "actionability": X}}
"""

scores = judge_llm.evaluate(eval_prompt)
```

---

# MLOPS & OBSERVABILITY

## Card 27: LLM Metrics to Track
**Q:** What metrics should you track for LLM systems?

**A:**
| Category | Metrics |
|----------|---------|
| **Performance** | Latency (p50, p95, p99), throughput |
| **Quality** | Relevance scores, user feedback |
| **Cost** | Tokens/query, cost/query, daily spend |
| **Reliability** | Error rate, timeout rate |
| **Safety** | Guardrail triggers, flagged content |

---

## Card 28: Tracing Setup
**Q:** How do you set up LLM tracing?

**A:**
```python
# LangSmith
from langsmith import Client
from langchain.callbacks import LangChainTracer

tracer = LangChainTracer(project_name="logistics-agent")
agent.run(query, callbacks=[tracer])

# OpenTelemetry
with tracer.start_as_current_span("forecast") as span:
    span.set_attribute("model", "gpt-4")
    result = forecast(region)
    span.set_attribute("latency_ms", latency)
```

---

## Card 29: Alerting Rules
**Q:** What alerts should you configure for LLM systems?

**A:**
```yaml
alerts:
  - name: high_latency
    condition: p95_latency > 5s for 5min
    
  - name: error_spike
    condition: error_rate > 1%
    
  - name: cost_overrun
    condition: daily_cost > $500
    
  - name: guardrail_triggers
    condition: trigger_rate > 5%
    
  - name: quality_degradation
    condition: avg_relevance_score < 0.7
```

---

# BEHAVIORAL QUESTIONS

## Card 30: Challenging Project
**Q:** "Tell me about a challenging GenAI project."

**A:** Structure: **Situation → Challenge → Action → Result**

"Built logistics analytics agent that queried multiple data sources.

**Challenge:** Agent was hallucinating shipment numbers (15% error rate).

**Actions:**
1. Implemented strict RAG with source citations
2. Added validation comparing LLM output to actual data
3. Created guardrails flagging statistical outliers

**Result:** Reduced hallucination to <2%, increased user adoption by 40%."

---

## Card 31: Production Readiness
**Q:** "How do you ensure GenAI systems are production-ready?"

**A:** Checklist approach:

**Reliability:** Retries, fallbacks, circuit breakers
**Scalability:** Async, queuing, caching
**Observability:** Logging, metrics, tracing, alerts
**Security:** Input validation, output filtering, audit logs
**Testing:** Unit tests, integration tests, eval suite, load tests

---

## Card 32: Handling Incorrect Information
**Q:** "How would you handle agent giving wrong information?"

**A:**
**Immediate:**
1. Acknowledge user report
2. Investigate via traces
3. Update guardrails if needed

**Root Cause:**
- Retrieval failure? (wrong context)
- Generation failure? (hallucination)
- Data quality issue?

**Prevention:**
- Add to eval dataset as regression test
- Improve retrieval or add guardrails
- Consider human-in-the-loop for high-stakes

---

# QUICK REFERENCE

## Card 33: Key Numbers to Remember
**Q:** What are good benchmark numbers?

**A:**
| Metric | Target |
|--------|--------|
| RAG Faithfulness | >0.90 |
| Retrieval MRR@10 | >0.85 |
| Agent Latency (p95) | <3s |
| Error Rate | <1% |
| Hallucination Rate | <2% |
| Vector Search Latency | <200ms |

---

## Card 34: Penske-Specific Context
**Q:** How does your project demonstrate these skills?

**A:** Your logistics project shows:

- **GenAI Agents**: Gradio app with AI assistant
- **RAG**: Knowledge base for logistics docs
- **Cloud**: Azure/AWS deployment guides
- **ML**: Demand forecasting models
- **MLOps**: Model training pipelines
- **SQL**: Complex analytics queries

**Demo ready at:** http://localhost:7860

---

## Card 35: Questions to Ask Them
**Q:** What questions should you ask the interviewer?

**A:**
1. "What's the current state of GenAI adoption at Penske?"
2. "What are the primary use cases you're targeting?"
3. "How is the team structured?"
4. "What's the path from prototype to production?"
5. "How do you handle data governance for GenAI?"
6. "What's the current observability stack?"

---

*Review these cards before your interview. Good luck! 🚀*
