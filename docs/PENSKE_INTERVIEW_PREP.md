# Penske Senior Data Scientist Interview Preparation Guide
## GenAI Agent Development & Modern AI Engineering

---

# TABLE OF CONTENTS

1. [GenAI Agents - Core Concepts & Experience](#1-genai-agents)
2. [MCP (Model Context Protocol) & Tool Integrations](#2-mcp-model-context-protocol)
3. [Knowledge Bases & Vector Search](#3-knowledge-bases--vector-search)
4. [Vibe Coding for Rapid Prototyping](#4-vibe-coding)
5. [Cloud Expertise (Azure/AWS)](#5-cloud-expertise)
6. [SQL & Snowflake](#6-sql--snowflake)
7. [Databricks for ML Workflows](#7-databricks)
8. [Traditional ML](#8-traditional-ml)
9. [Evals, Guardrails & Safety](#9-evals-guardrails--safety)
10. [MLOps & LLM Observability](#10-mlops--llm-observability)
11. [Sample Interview Q&A](#11-sample-interview-qa)

---

# 1. GenAI Agents

## Key Concepts to Know

### What is a GenAI Agent?
An AI agent is an autonomous system that uses LLMs to:
- **Perceive** - Understand user intent and context
- **Reason** - Plan multi-step actions
- **Act** - Execute tools and APIs
- **Learn** - Improve from feedback

### Agent Architecture Patterns

```
┌─────────────────────────────────────────────────────────────┐
│                    AGENT ARCHITECTURE                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐              │
│  │  User    │───▶│  Agent   │───▶│  Tools   │              │
│  │  Input   │    │  (LLM)   │    │  & APIs  │              │
│  └──────────┘    └────┬─────┘    └──────────┘              │
│                       │                                      │
│                       ▼                                      │
│              ┌────────────────┐                             │
│              │   Memory &     │                             │
│              │   Context      │                             │
│              └────────────────┘                             │
│                       │                                      │
│                       ▼                                      │
│              ┌────────────────┐                             │
│              │  Knowledge     │                             │
│              │  Base (RAG)    │                             │
│              └────────────────┘                             │
└─────────────────────────────────────────────────────────────┘
```

### Popular Agent Frameworks

| Framework | Best For | Key Features |
|-----------|----------|--------------|
| **LangChain** | General purpose | Tools, chains, memory |
| **LangGraph** | Complex workflows | State machines, cycles |
| **AutoGen** | Multi-agent | Agent collaboration |
| **CrewAI** | Role-based agents | Task delegation |
| **Semantic Kernel** | Microsoft stack | Azure integration |

## Sample Interview Answer

**Q: "Tell me about your experience building GenAI agents in production."**

**A:** "I've built several production GenAI agents, including a logistics analytics assistant for demand forecasting. Here's my approach:

**Architecture:**
- Used LangChain with Azure OpenAI as the LLM backbone
- Implemented ReAct (Reasoning + Acting) pattern for multi-step reasoning
- Built custom tools for database queries, API calls, and calculations

**Production Considerations:**
- **Reliability**: Implemented retry logic, fallbacks, and circuit breakers
- **Latency**: Used streaming responses and async processing
- **Cost**: Token optimization, caching frequent queries
- **Safety**: Input validation, output filtering, rate limiting

**Example - Logistics Agent:**
```python
from langchain.agents import AgentExecutor, create_react_agent
from langchain_openai import AzureChatOpenAI

# Define tools
tools = [
    query_shipment_data,      # SQL query tool
    get_weather_forecast,     # External API
    calculate_demand_forecast, # ML model inference
    send_alert                # Notification system
]

# Create agent with memory
agent = create_react_agent(
    llm=AzureChatOpenAI(model="gpt-4"),
    tools=tools,
    prompt=logistics_prompt
)

executor = AgentExecutor(
    agent=agent,
    tools=tools,
    memory=ConversationBufferMemory(),
    max_iterations=5,
    handle_parsing_errors=True
)
```

**Results:** Reduced manual analysis time by 60%, improved forecast accuracy by 15%."

---

# 2. MCP (Model Context Protocol)

## What is MCP?

MCP (Model Context Protocol) is Anthropic's open standard for connecting AI assistants to external data sources and tools securely.

### MCP Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP ARCHITECTURE                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────┐         ┌──────────┐         ┌──────────┐    │
│  │   Host   │◀───────▶│   MCP    │◀───────▶│  Server  │    │
│  │  (LLM)   │  JSON   │ Protocol │   JSON  │  (Tool)  │    │
│  └──────────┘  RPC    └──────────┘   RPC   └──────────┘    │
│                                                              │
│  Examples:                          Examples:                │
│  - Claude Desktop                   - Database server        │
│  - VS Code Copilot                  - File system server     │
│  - Custom agents                    - API integrations       │
└─────────────────────────────────────────────────────────────┘
```

### MCP Core Concepts

| Concept | Description | Example |
|---------|-------------|---------|
| **Resources** | Data the server exposes | Files, DB records, API data |
| **Tools** | Functions the LLM can call | query_database(), send_email() |
| **Prompts** | Pre-built prompt templates | analysis_template, report_template |
| **Sampling** | Server requests LLM completion | Complex reasoning chains |

### Building an MCP Server

```python
# Example MCP Server for Penske Logistics
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

server = Server("penske-logistics-mcp")

@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="query_shipments",
            description="Query shipment data from Snowflake",
            inputSchema={
                "type": "object",
                "properties": {
                    "date_range": {"type": "string"},
                    "region": {"type": "string"}
                },
                "required": ["date_range"]
            }
        ),
        types.Tool(
            name="get_demand_forecast",
            description="Get ML-based demand forecast",
            inputSchema={
                "type": "object",
                "properties": {
                    "days_ahead": {"type": "integer"},
                    "region": {"type": "string"}
                }
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if name == "query_shipments":
        result = await query_snowflake(arguments)
        return [types.TextContent(type="text", text=str(result))]
    elif name == "get_demand_forecast":
        forecast = await run_ml_forecast(arguments)
        return [types.TextContent(type="text", text=str(forecast))]

async def main():
    async with mcp.server.stdio.stdio_server() as (read, write):
        await server.run(read, write, InitializationOptions())
```

## Sample Interview Answer

**Q: "What experience do you have with MCP and tool integrations?"**

**A:** "I've worked extensively with MCP for building secure, enterprise-grade agent integrations:

**MCP Server Development:**
- Built custom MCP servers for database access, internal APIs, and file systems
- Implemented proper authentication and authorization layers
- Created resource endpoints for real-time data access

**Key Implementation Details:**
1. **Security**: All MCP servers run in isolated containers with minimal permissions
2. **Schema Validation**: Strong input validation using JSON Schema
3. **Error Handling**: Graceful degradation when tools fail
4. **Logging**: Comprehensive audit trails for compliance

**Example Use Case - Logistics Data Access:**
```
User Query: "What were shipment delays in the Midwest last week?"
     │
     ▼
┌─────────────────┐
│   LLM Agent     │
└────────┬────────┘
         │ MCP call: query_shipments
         ▼
┌─────────────────┐
│  MCP Server     │──▶ Snowflake Query
└────────┬────────┘
         │ Structured response
         ▼
┌─────────────────┐
│   LLM Agent     │──▶ Natural language answer
└─────────────────┘
```

This approach ensures secure, auditable access to enterprise data while maintaining the flexibility of natural language interfaces."

---

# 3. Knowledge Bases & Vector Search

## RAG (Retrieval-Augmented Generation) Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    RAG PIPELINE                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  INDEXING PHASE:                                            │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐               │
│  │Documents │──▶│  Chunk   │──▶│  Embed   │──▶ Vector DB  │
│  │(PDF,etc) │   │  Split   │   │  Model   │               │
│  └──────────┘   └──────────┘   └──────────┘               │
│                                                              │
│  RETRIEVAL PHASE:                                           │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐               │
│  │  Query   │──▶│  Embed   │──▶│  Vector  │──▶ Top-K docs │
│  │          │   │  Query   │   │  Search  │               │
│  └──────────┘   └──────────┘   └──────────┘               │
│                                                              │
│  GENERATION PHASE:                                          │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐               │
│  │  Query + │──▶│   LLM    │──▶│ Response │               │
│  │  Context │   │          │   │          │               │
│  └──────────┘   └──────────┘   └──────────┘               │
└─────────────────────────────────────────────────────────────┘
```

## Vector Databases Comparison

| Database | Best For | Key Features |
|----------|----------|--------------|
| **Pinecone** | Production scale | Managed, fast, metadata filtering |
| **Weaviate** | Hybrid search | GraphQL, modules |
| **Chroma** | Prototyping | Simple, embedded |
| **Qdrant** | Performance | Rust-based, filtering |
| **Azure AI Search** | Enterprise | Integrated with Azure |
| **pgvector** | Postgres users | SQL integration |

## Advanced RAG Techniques

### 1. Chunking Strategies
```python
# Semantic chunking with overlap
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n\n", "\n", ".", " "]
)
```

### 2. Hybrid Search (Vector + Keyword)
```python
# Combine BM25 with vector search
from rank_bm25 import BM25Okapi

def hybrid_search(query, documents, alpha=0.5):
    # Vector search
    vector_scores = vector_db.similarity_search(query, k=20)
    
    # BM25 keyword search
    bm25 = BM25Okapi([doc.split() for doc in documents])
    bm25_scores = bm25.get_scores(query.split())
    
    # Combine scores
    final_scores = alpha * vector_scores + (1 - alpha) * bm25_scores
    return get_top_k(final_scores, k=5)
```

### 3. Re-ranking
```python
# Use cross-encoder for re-ranking
from sentence_transformers import CrossEncoder

reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

def rerank_results(query, documents):
    pairs = [[query, doc] for doc in documents]
    scores = reranker.predict(pairs)
    return sorted(zip(documents, scores), key=lambda x: x[1], reverse=True)
```

## Sample Interview Answer

**Q: "How would you design a knowledge base for Penske's internal documentation?"**

**A:** "I'd design a multi-tier knowledge system:

**Architecture:**
```
┌─────────────────────────────────────────────────────────────┐
│                 PENSKE KNOWLEDGE SYSTEM                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  DATA SOURCES:                                               │
│  ├── Operations manuals (PDF)                               │
│  ├── Safety procedures (Word/Confluence)                    │
│  ├── Maintenance logs (Structured DB)                       │
│  └── Training materials (Video transcripts)                 │
│                                                              │
│  PROCESSING:                                                 │
│  ├── Document parsing (Unstructured.io)                     │
│  ├── Semantic chunking (1000 tokens, 200 overlap)          │
│  ├── Metadata extraction (date, department, doc_type)       │
│  └── Embedding (text-embedding-3-large)                     │
│                                                              │
│  STORAGE:                                                    │
│  ├── Azure AI Search (primary vector store)                 │
│  ├── Snowflake (structured metadata)                        │
│  └── Blob Storage (original documents)                      │
│                                                              │
│  RETRIEVAL:                                                  │
│  ├── Hybrid search (vector + BM25)                          │
│  ├── Metadata filtering (department, date range)            │
│  └── Re-ranking (cross-encoder)                             │
└─────────────────────────────────────────────────────────────┘
```

**Key Design Decisions:**
1. **Chunking**: Use semantic chunking that respects document structure (sections, paragraphs)
2. **Metadata**: Rich metadata for filtering (department, document type, date, author)
3. **Freshness**: Incremental updates with change detection
4. **Access Control**: Role-based filtering at retrieval time

**Performance Targets:**
- Retrieval latency: <200ms
- Relevance (MRR@10): >0.85
- Coverage: 95% of queries answered from KB"

---

# 4. Vibe Coding

## What is Vibe Coding?

"Vibe coding" refers to rapid, iterative AI-assisted development where you:
- Use AI tools (Copilot, Cursor, Claude) to quickly prototype
- Focus on intent and direction rather than syntax
- Iterate rapidly with AI feedback
- Build working prototypes in hours, not days

## Vibe Coding Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                 VIBE CODING WORKFLOW                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. DESCRIBE ──▶ 2. GENERATE ──▶ 3. ITERATE ──▶ 4. REFINE  │
│                                                              │
│  "Build a       AI generates    Test & fix     Production   │
│   dashboard     initial code    with AI help   hardening    │
│   that shows                                                 │
│   shipment                                                   │
│   metrics"                                                   │
│                                                              │
│  TOOLS:                                                      │
│  ├── Cursor / Windsurf (IDE)                                │
│  ├── Claude / GPT-4 (reasoning)                             │
│  ├── Gradio / Streamlit (rapid UI)                          │
│  └── GitHub Copilot (inline completion)                     │
└─────────────────────────────────────────────────────────────┘
```

## Sample Interview Answer

**Q: "What is your experience with vibe coding for rapid prototyping?"**

**A:** "I use vibe coding extensively for GenAI prototyping. My typical workflow:

**Tools I Use:**
- **Cursor/Windsurf**: AI-native IDE for code generation
- **Claude**: Complex reasoning and architecture decisions
- **Gradio/Streamlit**: Rapid UI prototyping

**Example - Building a Logistics Agent in 2 Hours:**

1. **Hour 1 - Core Agent:**
   - Described the agent requirements to Claude
   - Generated tool definitions for shipment queries
   - Built basic ReAct agent with LangChain

2. **Hour 2 - UI & Integration:**
   - Created Gradio interface with charts
   - Added Snowflake connection
   - Implemented basic error handling

**Key Principles:**
- **Start with working code**: Get something running fast
- **Iterate in small steps**: Make incremental improvements
- **Use AI for boilerplate**: Focus your energy on business logic
- **Document intent, not implementation**: Comments explain 'why'

**Production Hardening (after prototype):**
- Add comprehensive error handling
- Implement proper logging and monitoring
- Add unit and integration tests
- Security review and access controls

This approach lets me validate ideas quickly before investing in full production implementation."

---

# 5. Cloud Expertise

## Azure AI Services (Primary)

### Azure OpenAI Service
```python
from openai import AzureOpenAI

client = AzureOpenAI(
    api_key=os.environ["AZURE_OPENAI_KEY"],
    api_version="2024-02-15-preview",
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"]
)

response = client.chat.completions.create(
    model="gpt-4-turbo",  # deployment name
    messages=[
        {"role": "system", "content": "You are a logistics analyst."},
        {"role": "user", "content": "Analyze shipment delays in Q4"}
    ],
    temperature=0.7,
    max_tokens=1000
)
```

### Azure AI Search (Vector Store)
```python
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery

search_client = SearchClient(
    endpoint=os.environ["AZURE_SEARCH_ENDPOINT"],
    index_name="logistics-knowledge",
    credential=AzureKeyCredential(os.environ["AZURE_SEARCH_KEY"])
)

# Hybrid search with vector
vector_query = VectorizedQuery(
    vector=embedding,
    k_nearest_neighbors=5,
    fields="content_vector"
)

results = search_client.search(
    search_text="shipment delay causes",
    vector_queries=[vector_query],
    select=["title", "content", "metadata"],
    top=10
)
```

### Azure Architecture for GenAI

```
┌─────────────────────────────────────────────────────────────┐
│              AZURE GENAI ARCHITECTURE                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │   Azure     │    │   Azure     │    │   Azure     │     │
│  │   OpenAI    │    │  AI Search  │    │   Cosmos    │     │
│  │   (LLM)     │    │  (Vector)   │    │   (Memory)  │     │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘     │
│         │                  │                  │             │
│         └──────────────────┼──────────────────┘             │
│                            │                                 │
│                     ┌──────┴──────┐                         │
│                     │   Azure     │                         │
│                     │  Functions  │                         │
│                     │  (Agent)    │                         │
│                     └──────┬──────┘                         │
│                            │                                 │
│         ┌──────────────────┼──────────────────┐             │
│         │                  │                  │             │
│  ┌──────┴──────┐    ┌──────┴──────┐    ┌──────┴──────┐     │
│  │  Snowflake  │    │  Databricks │    │   Blob      │     │
│  │   (Data)    │    │    (ML)     │    │  Storage    │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

## AWS Alternative

| Azure Service | AWS Equivalent |
|---------------|----------------|
| Azure OpenAI | Amazon Bedrock |
| Azure AI Search | Amazon OpenSearch |
| Azure Functions | AWS Lambda |
| Azure Cosmos | DynamoDB |
| Azure Blob | S3 |

## Sample Interview Answer

**Q: "Describe your cloud experience, particularly with Azure."**

**A:** "I have extensive experience with Azure's AI stack:

**Azure OpenAI:**
- Deployed GPT-4 and embedding models
- Implemented content filtering and rate limiting
- Managed token budgets across teams

**Azure AI Search:**
- Built hybrid search indexes (vector + keyword)
- Implemented semantic ranking
- Configured security trimming for RBAC

**Production Architecture:**
```
User Request
     │
     ▼
Azure Front Door (CDN + WAF)
     │
     ▼
Azure Container Apps (Agent Service)
     │
     ├──▶ Azure OpenAI (LLM calls)
     ├──▶ Azure AI Search (RAG retrieval)
     ├──▶ Snowflake (business data)
     └──▶ Azure Monitor (observability)
```

**Key Implementations:**
1. **Cost Optimization**: Implemented PTU (Provisioned Throughput Units) for predictable costs
2. **Security**: Private endpoints, managed identities, Key Vault integration
3. **Reliability**: Multi-region deployment with failover
4. **Monitoring**: Custom metrics for token usage, latency, error rates"

---

# 6. SQL & Snowflake

## Why Snowflake Matters for This Role

Snowflake is Penske's primary data warehouse. You'll use it to:
- Query logistics data for agent tools
- Store and search vector embeddings (Cortex)
- Build real-time features for ML models
- Log and analyze LLM usage

## Snowflake Core Concepts

### 1. Architecture (Know This Cold)

```
┌─────────────────────────────────────────────────────────────┐
│                 SNOWFLAKE ARCHITECTURE                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  LAYER 1: CLOUD SERVICES                                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  • Query parsing & optimization                      │   │
│  │  • Metadata management                               │   │
│  │  • Authentication & access control                   │   │
│  │  • Infrastructure management                         │   │
│  └─────────────────────────────────────────────────────┘   │
│                          │                                   │
│  LAYER 2: COMPUTE (Virtual Warehouses)                      │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  • Independently scalable compute clusters           │   │
│  │  • XS, S, M, L, XL, 2XL, 3XL, 4XL sizes             │   │
│  │  • Auto-suspend & auto-resume                        │   │
│  │  • Multi-cluster warehouses for concurrency          │   │
│  │                                                       │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐             │   │
│  │  │ QUERY   │  │  ETL    │  │   ML    │             │   │
│  │  │ WH (XS) │  │ WH (M)  │  │ WH (XL) │             │   │
│  │  └─────────┘  └─────────┘  └─────────┘             │   │
│  └─────────────────────────────────────────────────────┘   │
│                          │                                   │
│  LAYER 3: STORAGE                                           │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  • Columnar storage format                           │   │
│  │  • Automatic compression                             │   │
│  │  • Micro-partitions (50-500MB each)                  │   │
│  │  • Stored on cloud object storage (S3/Azure Blob)    │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘

KEY INSIGHT: Compute and storage are SEPARATE
- Scale compute without copying data
- Pay for storage and compute independently
- Multiple warehouses can query same data simultaneously
```

### 2. Key Snowflake Objects

| Object | Description | Example Use |
|--------|-------------|-------------|
| **Database** | Container for schemas | `PENSKE_ANALYTICS` |
| **Schema** | Container for tables/views | `LOGISTICS`, `ML_FEATURES` |
| **Table** | Stores data | `SHIPMENTS`, `CUSTOMERS` |
| **View** | Virtual table from query | `V_DAILY_METRICS` |
| **Stage** | Location for loading data | `@my_s3_stage` |
| **Warehouse** | Compute resource | `ANALYTICS_WH` |
| **Task** | Scheduled SQL | Nightly aggregations |
| **Stream** | Change data capture | Track new shipments |
| **Pipe** | Continuous data loading | Real-time ingestion |

### 3. Snowflake for GenAI - Cortex

Cortex is Snowflake's AI/ML layer:

```sql
-- CORTEX LLM FUNCTIONS (Built-in AI)
-- Text completion
SELECT SNOWFLAKE.CORTEX.COMPLETE(
    'mistral-large',
    'Summarize these shipment delays: ' || delay_notes
) as summary
FROM shipment_issues;

-- Sentiment analysis
SELECT 
    customer_feedback,
    SNOWFLAKE.CORTEX.SENTIMENT(customer_feedback) as sentiment_score
FROM customer_reviews;

-- Text embedding for RAG
SELECT 
    document_id,
    content,
    SNOWFLAKE.CORTEX.EMBED_TEXT_768('e5-base-v2', content) as embedding
FROM documents;

-- Vector similarity search
SELECT 
    document_id,
    content,
    VECTOR_COSINE_SIMILARITY(
        embedding, 
        SNOWFLAKE.CORTEX.EMBED_TEXT_768('e5-base-v2', 'shipment delay causes')
    ) as similarity
FROM documents
ORDER BY similarity DESC
LIMIT 10;
```

### 4. Snowpark (Python in Snowflake)

Run Python directly in Snowflake for ML:

```python
# Connect from Python
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col, avg, count

# Create session
session = Session.builder.configs({
    "account": "penske.us-east-1",
    "user": "ml_service",
    "password": "***",
    "warehouse": "ML_WH",
    "database": "ANALYTICS",
    "schema": "ML_FEATURES"
}).create()

# Query with Snowpark DataFrame API (runs in Snowflake!)
shipments = session.table("SHIPMENTS")

daily_metrics = (
    shipments
    .filter(col("ship_date") >= "2024-01-01")
    .group_by("region", "ship_date")
    .agg(
        count("*").alias("shipment_count"),
        avg("delay_minutes").alias("avg_delay")
    )
)

# Convert to Pandas for ML
df = daily_metrics.to_pandas()

# Or register as stored procedure
from snowflake.snowpark.functions import sproc

@sproc(packages=["scikit-learn", "xgboost"])
def train_demand_model(session: Session) -> str:
    import xgboost as xgb
    from sklearn.model_selection import train_test_split
    
    # Load data
    df = session.table("SHIPMENT_FEATURES").to_pandas()
    
    # Train
    X = df[['volume_lag_1', 'volume_lag_7', 'fuel_price', 'is_weekend']]
    y = df['next_day_volume']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    
    model = xgb.XGBRegressor(n_estimators=100, max_depth=6)
    model.fit(X_train, y_train)
    
    score = model.score(X_test, y_test)
    
    # Save model to stage
    import joblib
    joblib.dump(model, '/tmp/model.joblib')
    session.file.put('/tmp/model.joblib', '@models/demand/')
    
    return f"Model trained. R2 score: {score:.4f}"

# Call the procedure
session.call("train_demand_model")
```

### 5. Time Travel & Data Versioning

```sql
-- Query data as it was at a specific time
SELECT * FROM shipments
AT(TIMESTAMP => '2024-01-15 10:00:00'::TIMESTAMP);

-- Query data as it was before a specific query
SELECT * FROM shipments
BEFORE(STATEMENT => '8e5d0ca9-005e-44e6-b858-a8f5b37c5726');

-- Restore accidentally deleted data
CREATE TABLE shipments_restored CLONE shipments
AT(OFFSET => -3600);  -- 1 hour ago

-- Set retention period (default 1 day, up to 90 days)
ALTER TABLE shipments SET DATA_RETENTION_TIME_IN_DAYS = 30;
```

### 6. Dynamic Tables (Real-Time Features)

```sql
-- Dynamic tables automatically refresh as source data changes
CREATE OR REPLACE DYNAMIC TABLE customer_features
TARGET_LAG = '5 minutes'  -- Refresh within 5 minutes of source changes
WAREHOUSE = FEATURES_WH
AS
SELECT 
    customer_id,
    
    -- Recency
    DATEDIFF(day, MAX(order_date), CURRENT_DATE) as days_since_last_order,
    
    -- Frequency
    COUNT(*) as total_orders_90d,
    COUNT(DISTINCT DATE_TRUNC('week', order_date)) as active_weeks,
    
    -- Monetary
    SUM(order_value) as total_spend_90d,
    AVG(order_value) as avg_order_value,
    
    -- Behavior
    AVG(items_per_order) as avg_items,
    MODE(preferred_shipping) as preferred_shipping,
    
    -- Metadata
    CURRENT_TIMESTAMP() as feature_timestamp
    
FROM orders
WHERE order_date >= DATEADD(day, -90, CURRENT_DATE)
GROUP BY customer_id;

-- Check refresh status
SELECT * FROM TABLE(INFORMATION_SCHEMA.DYNAMIC_TABLE_REFRESH_HISTORY(
    TABLE_NAME => 'CUSTOMER_FEATURES'
));
```

### 7. Streams (Change Data Capture)

```sql
-- Create a stream to track changes
CREATE STREAM shipments_stream ON TABLE shipments;

-- Process new/changed records
CREATE TASK process_new_shipments
WAREHOUSE = ETL_WH
SCHEDULE = '1 MINUTE'
WHEN SYSTEM$STREAM_HAS_DATA('shipments_stream')
AS
INSERT INTO shipment_events
SELECT 
    shipment_id,
    METADATA$ACTION as action,  -- INSERT, DELETE, UPDATE
    METADATA$ISUPDATE as is_update,
    CURRENT_TIMESTAMP() as processed_at
FROM shipments_stream;
```

## Complex SQL Patterns for Interviews

### Pattern 1: Rolling Aggregates with Window Functions

```sql
-- Calculate 7-day rolling metrics by region
SELECT 
    ship_date,
    region,
    shipment_count,
    
    -- Rolling average (last 7 days)
    AVG(shipment_count) OVER (
        PARTITION BY region 
        ORDER BY ship_date 
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) as rolling_7d_avg,
    
    -- Rolling standard deviation
    STDDEV(shipment_count) OVER (
        PARTITION BY region 
        ORDER BY ship_date 
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) as rolling_7d_std,
    
    -- Percent change from last week
    (shipment_count - LAG(shipment_count, 7) OVER (
        PARTITION BY region ORDER BY ship_date
    )) * 100.0 / NULLIF(LAG(shipment_count, 7) OVER (
        PARTITION BY region ORDER BY ship_date
    ), 0) as week_over_week_pct
    
FROM daily_shipments
ORDER BY region, ship_date;
```

### Pattern 2: Sessionization (Grouping Events)

```sql
-- Group driver activities into sessions (gaps > 30 min = new session)
WITH activity_gaps AS (
    SELECT 
        driver_id,
        activity_time,
        activity_type,
        DATEDIFF('minute', 
            LAG(activity_time) OVER (PARTITION BY driver_id ORDER BY activity_time),
            activity_time
        ) as minutes_since_last
    FROM driver_activities
),
session_starts AS (
    SELECT 
        *,
        CASE WHEN minutes_since_last > 30 OR minutes_since_last IS NULL 
             THEN 1 ELSE 0 END as is_session_start
    FROM activity_gaps
),
sessions AS (
    SELECT 
        *,
        SUM(is_session_start) OVER (
            PARTITION BY driver_id 
            ORDER BY activity_time
        ) as session_id
    FROM session_starts
)
SELECT 
    driver_id,
    session_id,
    MIN(activity_time) as session_start,
    MAX(activity_time) as session_end,
    DATEDIFF('minute', MIN(activity_time), MAX(activity_time)) as session_duration_min,
    COUNT(*) as activity_count
FROM sessions
GROUP BY driver_id, session_id;
```

### Pattern 3: Funnel Analysis

```sql
-- Analyze shipment lifecycle funnel
WITH funnel AS (
    SELECT 
        shipment_id,
        MAX(CASE WHEN status = 'created' THEN 1 ELSE 0 END) as step_1_created,
        MAX(CASE WHEN status = 'picked_up' THEN 1 ELSE 0 END) as step_2_picked_up,
        MAX(CASE WHEN status = 'in_transit' THEN 1 ELSE 0 END) as step_3_in_transit,
        MAX(CASE WHEN status = 'delivered' THEN 1 ELSE 0 END) as step_4_delivered
    FROM shipment_events
    WHERE event_date >= DATEADD(day, -30, CURRENT_DATE)
    GROUP BY shipment_id
)
SELECT 
    SUM(step_1_created) as created,
    SUM(step_2_picked_up) as picked_up,
    SUM(step_3_in_transit) as in_transit,
    SUM(step_4_delivered) as delivered,
    
    -- Conversion rates
    ROUND(SUM(step_2_picked_up) * 100.0 / NULLIF(SUM(step_1_created), 0), 1) as pickup_rate,
    ROUND(SUM(step_4_delivered) * 100.0 / NULLIF(SUM(step_1_created), 0), 1) as delivery_rate
FROM funnel;
```

### Pattern 4: Feature Engineering for ML

```sql
-- Complete feature engineering query for demand forecasting
WITH base_data AS (
    SELECT 
        ship_date,
        region,
        COUNT(*) as shipment_volume,
        AVG(weight_lbs) as avg_weight,
        AVG(distance_miles) as avg_distance,
        SUM(CASE WHEN is_expedited THEN 1 ELSE 0 END) as expedited_count,
        SUM(CASE WHEN delay_minutes > 30 THEN 1 ELSE 0 END) as delayed_count
    FROM shipments
    WHERE ship_date >= DATEADD(day, -180, CURRENT_DATE)
    GROUP BY ship_date, region
),
with_lags AS (
    SELECT 
        *,
        -- Lag features
        LAG(shipment_volume, 1) OVER (PARTITION BY region ORDER BY ship_date) as vol_lag_1,
        LAG(shipment_volume, 7) OVER (PARTITION BY region ORDER BY ship_date) as vol_lag_7,
        LAG(shipment_volume, 14) OVER (PARTITION BY region ORDER BY ship_date) as vol_lag_14,
        LAG(shipment_volume, 30) OVER (PARTITION BY region ORDER BY ship_date) as vol_lag_30,
        
        -- Rolling statistics
        AVG(shipment_volume) OVER (
            PARTITION BY region ORDER BY ship_date 
            ROWS BETWEEN 7 PRECEDING AND 1 PRECEDING
        ) as vol_rolling_mean_7d,
        STDDEV(shipment_volume) OVER (
            PARTITION BY region ORDER BY ship_date 
            ROWS BETWEEN 7 PRECEDING AND 1 PRECEDING
        ) as vol_rolling_std_7d,
        
        -- Expanding statistics (all history)
        AVG(shipment_volume) OVER (
            PARTITION BY region ORDER BY ship_date 
            ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
        ) as vol_expanding_mean
        
    FROM base_data
),
with_calendar AS (
    SELECT 
        w.*,
        -- Calendar features
        DAYOFWEEK(w.ship_date) as day_of_week,
        DAYOFMONTH(w.ship_date) as day_of_month,
        WEEKOFYEAR(w.ship_date) as week_of_year,
        MONTH(w.ship_date) as month,
        CASE WHEN DAYOFWEEK(w.ship_date) IN (0, 6) THEN 1 ELSE 0 END as is_weekend,
        CASE WHEN h.holiday_date IS NOT NULL THEN 1 ELSE 0 END as is_holiday,
        
        -- External features
        f.fuel_price_per_gallon,
        wth.weather_severity_score
        
    FROM with_lags w
    LEFT JOIN holidays h ON w.ship_date = h.holiday_date
    LEFT JOIN fuel_prices f ON w.ship_date = f.price_date
    LEFT JOIN weather_daily wth ON w.ship_date = wth.weather_date AND w.region = wth.region
)
SELECT 
    ship_date,
    region,
    
    -- Target (for training, exclude for inference)
    shipment_volume as target,
    
    -- Features
    vol_lag_1,
    vol_lag_7,
    vol_lag_14,
    vol_lag_30,
    vol_rolling_mean_7d,
    vol_rolling_std_7d,
    vol_expanding_mean,
    avg_weight,
    avg_distance,
    expedited_count,
    delayed_count,
    day_of_week,
    day_of_month,
    week_of_year,
    month,
    is_weekend,
    is_holiday,
    fuel_price_per_gallon,
    weather_severity_score,
    
    -- Derived features
    vol_lag_1 - vol_lag_7 as vol_diff_1d_7d,
    (shipment_volume - vol_rolling_mean_7d) / NULLIF(vol_rolling_std_7d, 0) as vol_zscore

FROM with_calendar
WHERE vol_lag_30 IS NOT NULL  -- Ensure enough history
ORDER BY region, ship_date;
```

## Sample Interview Answer - Snowflake

**Q: "How would you use Snowflake to support GenAI applications?"**

**A:** "Snowflake is central to my GenAI data strategy for several reasons:

**1. Agent Tool Integration:**
```python
@tool
def query_logistics_data(question: str) -> str:
    '''Query Snowflake using natural language. Converts to SQL and executes.'''
    # LLM converts question to SQL
    sql = llm.generate_sql(question, schema=LOGISTICS_SCHEMA)
    
    # Execute safely
    if validate_sql(sql):  # No DROP, DELETE, etc.
        result = snowflake_conn.execute(sql)
        return result.to_markdown()
    return "Query blocked for safety"
```

**2. Vector Search with Cortex:**
- Store document embeddings directly in Snowflake
- Use `VECTOR_COSINE_SIMILARITY` for RAG retrieval
- Join semantic search with structured business data

**3. Real-Time Features with Dynamic Tables:**
- `TARGET_LAG = '5 minutes'` for near real-time ML features
- No separate feature store infrastructure needed
- Automatic refresh as source data changes

**4. LLM Observability:**
```sql
-- Log all LLM calls
CREATE TABLE llm_logs (
    request_id STRING,
    timestamp TIMESTAMP,
    model STRING,
    prompt_tokens INT,
    completion_tokens INT,
    latency_ms INT,
    cost_usd FLOAT
);

-- Analyze usage
SELECT 
    DATE_TRUNC('day', timestamp) as day,
    model,
    COUNT(*) as requests,
    SUM(prompt_tokens + completion_tokens) as total_tokens,
    SUM(cost_usd) as daily_cost
FROM llm_logs
GROUP BY 1, 2;
```

**5. Time Travel for Debugging:**
- Reproduce exact data state when an agent gave wrong answer
- Compare before/after for data quality issues"

---

# 7. Databricks

## Why Databricks Matters for This Role

Databricks is used for:
- Large-scale data processing (Spark)
- ML experiment tracking and model registry (MLflow)
- Feature engineering and serving (Feature Store)
- GenAI workloads (Vector Search, Model Serving, Foundation Models)

## Databricks Core Concepts

### 1. Lakehouse Architecture (Know This Cold)

```
┌─────────────────────────────────────────────────────────────┐
│                 DATABRICKS LAKEHOUSE                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  LAYER 1: UNITY CATALOG (Governance)                        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  • Centralized access control (GRANT/REVOKE)         │   │
│  │  • Data lineage tracking                             │   │
│  │  • Audit logging                                     │   │
│  │  • Cross-workspace data sharing                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                          │                                   │
│  LAYER 2: DATA INTELLIGENCE                                 │
│  ┌──────────┬──────────┬──────────┬──────────┐            │
│  │  Delta   │  MLflow  │  Feature │  Vector  │            │
│  │  Lake    │          │  Store   │  Search  │            │
│  └──────────┴──────────┴──────────┴──────────┘            │
│                          │                                   │
│  LAYER 3: COMPUTE                                           │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  • All-Purpose Clusters (interactive)               │   │
│  │  • Job Clusters (scheduled, ephemeral)              │   │
│  │  • SQL Warehouses (BI queries)                      │   │
│  │  • Model Serving Endpoints (inference)              │   │
│  └─────────────────────────────────────────────────────┘   │
│                          │                                   │
│  LAYER 4: CLOUD STORAGE                                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  • Azure: ADLS Gen2                                  │   │
│  │  • AWS: S3                                           │   │
│  │  • All data stored as Delta tables                   │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘

KEY INSIGHT: Lakehouse = Data Lake + Data Warehouse benefits
- Open formats (Parquet/Delta) - no vendor lock-in
- ACID transactions on data lake
- Schema enforcement + evolution
- Time travel and versioning
```

### 2. Delta Lake - The Foundation

Delta Lake adds reliability to data lakes:

```python
# DELTA LAKE FUNDAMENTALS

# Create Delta table
df.write.format("delta").saveAsTable("penske.logistics.shipments")

# Or with SQL
# CREATE TABLE penske.logistics.shipments
# USING DELTA
# AS SELECT * FROM parquet_data;

# ============================================
# ACID TRANSACTIONS
# ============================================
# Multiple writers can safely update same table
spark.sql("""
    MERGE INTO shipments target
    USING updates source
    ON target.shipment_id = source.shipment_id
    WHEN MATCHED THEN UPDATE SET *
    WHEN NOT MATCHED THEN INSERT *
""")

# ============================================
# TIME TRAVEL (Version History)
# ============================================
# Read previous version
df_yesterday = spark.read.format("delta") \
    .option("versionAsOf", 5) \
    .table("shipments")

# Or by timestamp
df_before = spark.read.format("delta") \
    .option("timestampAsOf", "2024-01-15 10:00:00") \
    .table("shipments")

# View history
spark.sql("DESCRIBE HISTORY shipments")

# Restore to previous version
spark.sql("RESTORE TABLE shipments TO VERSION AS OF 5")

# ============================================
# SCHEMA EVOLUTION
# ============================================
# Add new columns automatically
df_new.write.format("delta") \
    .mode("append") \
    .option("mergeSchema", "true") \
    .saveAsTable("shipments")

# ============================================
# OPTIMIZE & Z-ORDER (Performance)
# ============================================
# Compact small files
spark.sql("OPTIMIZE shipments")

# Co-locate data for faster queries
spark.sql("OPTIMIZE shipments ZORDER BY (region, ship_date)")

# Clean up old versions
spark.sql("VACUUM shipments RETAIN 168 HOURS")
```

### 3. Medallion Architecture (Bronze/Silver/Gold)

```python
# ============================================
# BRONZE LAYER - Raw Ingestion
# ============================================
# Ingest raw data as-is, minimal transformation

# Auto Loader for streaming ingestion
bronze_df = (
    spark.readStream
    .format("cloudFiles")
    .option("cloudFiles.format", "json")
    .option("cloudFiles.schemaLocation", "/schemas/shipments")
    .load("/raw/shipments/")
)

bronze_df.writeStream \
    .format("delta") \
    .option("checkpointLocation", "/checkpoints/bronze_shipments") \
    .trigger(availableNow=True) \
    .toTable("bronze.shipments")

# ============================================
# SILVER LAYER - Cleaned & Validated
# ============================================
# Data quality checks, standardization, deduplication

from pyspark.sql.functions import col, when, trim, upper

silver_df = (
    spark.table("bronze.shipments")
    # Remove duplicates
    .dropDuplicates(["shipment_id", "event_timestamp"])
    # Standardize
    .withColumn("region", upper(trim(col("region"))))
    # Data quality: null handling
    .withColumn("weight_lbs", 
        when(col("weight_lbs") < 0, None).otherwise(col("weight_lbs")))
    # Type casting
    .withColumn("ship_date", col("ship_date").cast("date"))
)

# Apply constraints
spark.sql("""
    ALTER TABLE silver.shipments 
    ADD CONSTRAINT valid_weight CHECK (weight_lbs > 0 OR weight_lbs IS NULL)
""")

silver_df.write.format("delta").mode("overwrite").saveAsTable("silver.shipments")

# ============================================
# GOLD LAYER - Business-Ready Aggregations
# ============================================
# Aggregated, feature-engineered, ready for analytics/ML

gold_daily = spark.sql("""
    SELECT 
        ship_date,
        region,
        COUNT(*) as shipment_count,
        AVG(weight_lbs) as avg_weight,
        SUM(CASE WHEN delay_minutes > 30 THEN 1 ELSE 0 END) as delayed_count,
        AVG(delay_minutes) as avg_delay_minutes,
        PERCENTILE(delay_minutes, 0.95) as p95_delay
    FROM silver.shipments
    GROUP BY ship_date, region
""")

gold_daily.write.format("delta").mode("overwrite").saveAsTable("gold.daily_shipment_metrics")
```

### 4. MLflow - Complete ML Lifecycle

```python
import mlflow
import mlflow.sklearn
from mlflow.tracking import MlflowClient
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import numpy as np

# ============================================
# EXPERIMENT TRACKING
# ============================================

# Set experiment (creates if doesn't exist)
mlflow.set_experiment("/Penske/demand-forecasting")

# Start a run
with mlflow.start_run(run_name="rf_demand_v2") as run:
    
    # Log parameters
    params = {
        "n_estimators": 200,
        "max_depth": 8,
        "min_samples_split": 5,
        "feature_set": "v2_with_weather"
    }
    mlflow.log_params(params)
    
    # Train model
    model = RandomForestRegressor(**{k: v for k, v in params.items() 
                                      if k != "feature_set"})
    model.fit(X_train, y_train)
    
    # Predict and evaluate
    y_pred_train = model.predict(X_train)
    y_pred_test = model.predict(X_test)
    
    # Log metrics
    metrics = {
        "train_rmse": np.sqrt(mean_squared_error(y_train, y_pred_train)),
        "test_rmse": np.sqrt(mean_squared_error(y_test, y_pred_test)),
        "test_mae": mean_absolute_error(y_test, y_pred_test),
        "test_r2": r2_score(y_test, y_pred_test),
        "test_mape": np.mean(np.abs((y_test - y_pred_test) / y_test)) * 100
    }
    mlflow.log_metrics(metrics)
    
    # Log feature importance as artifact
    import pandas as pd
    importance_df = pd.DataFrame({
        'feature': feature_names,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    importance_df.to_csv("/tmp/feature_importance.csv", index=False)
    mlflow.log_artifact("/tmp/feature_importance.csv")
    
    # Log the model with signature
    from mlflow.models import infer_signature
    signature = infer_signature(X_train, y_pred_train)
    
    mlflow.sklearn.log_model(
        model, 
        "demand_model",
        signature=signature,
        input_example=X_train.iloc[:5]
    )
    
    # Add tags for searchability
    mlflow.set_tags({
        "model_type": "RandomForest",
        "use_case": "demand_forecasting",
        "region": "all",
        "author": "data_science_team"
    })
    
    print(f"Run ID: {run.info.run_id}")

# ============================================
# MODEL REGISTRY
# ============================================

client = MlflowClient()

# Register model
model_uri = f"runs:/{run.info.run_id}/demand_model"
model_version = mlflow.register_model(model_uri, "penske-demand-forecaster")

# Add description
client.update_registered_model(
    name="penske-demand-forecaster",
    description="Demand forecasting model for shipment volume prediction"
)

client.update_model_version(
    name="penske-demand-forecaster",
    version=model_version.version,
    description="V2: Added weather features, improved RMSE by 12%"
)

# Transition stages: None → Staging → Production → Archived
client.transition_model_version_stage(
    name="penske-demand-forecaster",
    version=model_version.version,
    stage="Staging"
)

# After validation, promote to production
client.transition_model_version_stage(
    name="penske-demand-forecaster",
    version=model_version.version,
    stage="Production"
)

# ============================================
# LOAD AND USE REGISTERED MODEL
# ============================================

# Load latest production model
model = mlflow.sklearn.load_model("models:/penske-demand-forecaster/Production")
predictions = model.predict(new_data)

# Or load specific version
model_v2 = mlflow.sklearn.load_model("models:/penske-demand-forecaster/2")
```

### 5. Feature Store

```python
from databricks.feature_engineering import FeatureEngineeringClient, FeatureLookup
from databricks.feature_engineering import FeatureFunction
from pyspark.sql.functions import col, datediff, current_date

fe = FeatureEngineeringClient()

# ============================================
# CREATE FEATURE TABLE
# ============================================

# Compute features
customer_features = spark.sql("""
    SELECT 
        customer_id,
        
        -- Recency
        DATEDIFF(CURRENT_DATE, MAX(order_date)) as days_since_last_order,
        
        -- Frequency
        COUNT(*) as order_count_90d,
        COUNT(DISTINCT DATE_TRUNC('week', order_date)) as active_weeks,
        
        -- Monetary
        SUM(order_value) as total_spend_90d,
        AVG(order_value) as avg_order_value,
        
        -- Behavior
        AVG(items_per_order) as avg_items,
        SUM(CASE WHEN is_expedited THEN 1 ELSE 0 END) / COUNT(*) as expedited_rate,
        
        -- Timestamp for point-in-time lookups
        CURRENT_TIMESTAMP() as feature_timestamp
        
    FROM silver.orders
    WHERE order_date >= DATE_SUB(CURRENT_DATE, 90)
    GROUP BY customer_id
""")

# Create feature table in Unity Catalog
fe.create_table(
    name="penske.features.customer_features",
    primary_keys=["customer_id"],
    timestamp_keys=["feature_timestamp"],
    df=customer_features,
    description="Customer RFM features computed over 90-day window"
)

# ============================================
# POINT-IN-TIME FEATURE LOOKUP (Training)
# ============================================

# Labels with timestamps
training_labels = spark.sql("""
    SELECT 
        customer_id,
        order_date as label_timestamp,
        next_order_value as target
    FROM silver.training_data
""")

# Define feature lookups
feature_lookups = [
    FeatureLookup(
        table_name="penske.features.customer_features",
        lookup_key=["customer_id"],
        timestamp_lookup_key=["label_timestamp"],  # Point-in-time!
        feature_names=["days_since_last_order", "order_count_90d", 
                       "avg_order_value", "expedited_rate"]
    ),
    FeatureLookup(
        table_name="penske.features.shipment_features",
        lookup_key=["customer_id"],
        timestamp_lookup_key=["label_timestamp"],
        feature_names=["avg_shipment_weight", "preferred_carrier"]
    )
]

# Create training set with automatic point-in-time joins
training_set = fe.create_training_set(
    df=training_labels,
    feature_lookups=feature_lookups,
    label="target",
    exclude_columns=["label_timestamp"]  # Don't use as feature
)

# Get pandas DataFrame for training
training_df = training_set.load_df().toPandas()

# ============================================
# TRAIN MODEL WITH FEATURE STORE
# ============================================

from sklearn.ensemble import GradientBoostingRegressor

X = training_df.drop(columns=["target"])
y = training_df["target"]

model = GradientBoostingRegressor()
model.fit(X, y)

# Log model with feature store metadata (enables auto-lookup at inference)
fe.log_model(
    model=model,
    artifact_path="model",
    flavor=mlflow.sklearn,
    training_set=training_set,
    registered_model_name="penske-customer-ltv"
)

# ============================================
# BATCH INFERENCE (Auto Feature Lookup)
# ============================================

# Just provide entity keys - features looked up automatically!
customers_to_score = spark.sql("SELECT customer_id FROM silver.active_customers")

predictions = fe.score_batch(
    model_uri="models:/penske-customer-ltv/Production",
    df=customers_to_score
)

predictions.write.format("delta").mode("overwrite").saveAsTable("gold.customer_ltv_predictions")
```

### 6. Model Serving & Endpoints

```python
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import EndpointCoreConfigInput, ServedModelInput

w = WorkspaceClient()

# ============================================
# CREATE MODEL SERVING ENDPOINT
# ============================================

endpoint_config = EndpointCoreConfigInput(
    served_models=[
        ServedModelInput(
            model_name="penske-demand-forecaster",
            model_version="3",
            workload_size="Small",  # Small, Medium, Large
            scale_to_zero_enabled=True  # Save costs when idle
        )
    ],
    auto_capture_config={
        "catalog_name": "penske",
        "schema_name": "inference_logs",
        "table_name_prefix": "demand_forecast"
    }
)

w.serving_endpoints.create(
    name="demand-forecast-endpoint",
    config=endpoint_config
)

# ============================================
# CALL ENDPOINT (REST API)
# ============================================

import requests
import json

# Get token
token = dbutils.secrets.get(scope="ml", key="serving_token")

# Prepare data
data = {
    "dataframe_records": [
        {"vol_lag_1": 120, "vol_lag_7": 115, "is_weekend": 0, "fuel_price": 3.45},
        {"vol_lag_1": 130, "vol_lag_7": 125, "is_weekend": 1, "fuel_price": 3.50}
    ]
}

# Call endpoint
response = requests.post(
    url="https://your-workspace.databricks.com/serving-endpoints/demand-forecast-endpoint/invocations",
    headers={"Authorization": f"Bearer {token}"},
    json=data
)

predictions = response.json()["predictions"]

# ============================================
# USE IN GENAI AGENT AS TOOL
# ============================================

@tool
def predict_demand(region: str, days_ahead: int = 7) -> str:
    """Get demand forecast from ML model."""
    
    # Get recent features from Snowflake/Databricks
    features = get_latest_features(region)
    
    # Call model endpoint
    response = requests.post(
        endpoint_url,
        headers={"Authorization": f"Bearer {token}"},
        json={"dataframe_records": [features]}
    )
    
    prediction = response.json()["predictions"][0]
    
    return f"Predicted demand for {region}: {prediction:.0f} shipments/day"
```

### 7. Databricks for GenAI

```python
# ============================================
# VECTOR SEARCH FOR RAG
# ============================================

from databricks.vector_search.client import VectorSearchClient

vsc = VectorSearchClient()

# Create vector search index
vsc.create_delta_sync_index(
    endpoint_name="penske-vector-search",
    index_name="penske.genai.document_index",
    source_table_name="penske.genai.documents",
    pipeline_type="TRIGGERED",
    primary_key="doc_id",
    embedding_source_column="content",  # Auto-embed this column
    embedding_model_endpoint_name="databricks-bge-large-en"  # Built-in model
)

# Query vector search
results = vsc.get_index("penske.genai.document_index").similarity_search(
    query_text="shipment delay procedures",
    columns=["doc_id", "title", "content"],
    num_results=5
)

# ============================================
# FOUNDATION MODEL APIS
# ============================================

from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

# Use Databricks-hosted models (DBRX, Llama, etc.)
response = w.serving_endpoints.query(
    name="databricks-dbrx-instruct",
    messages=[
        {"role": "system", "content": "You are a logistics analyst."},
        {"role": "user", "content": "Summarize shipment delays in Chicago"}
    ],
    max_tokens=500
)

print(response.choices[0].message.content)

# ============================================
# FINE-TUNING ON CUSTOM DATA
# ============================================

from databricks.model_training import foundation_model as fm

# Prepare training data (Delta table with prompt/response pairs)
training_data = spark.table("penske.genai.fine_tuning_data")

# Fine-tune model
run = fm.create(
    model="meta-llama/Meta-Llama-3-8B-Instruct",
    train_data_path="penske.genai.fine_tuning_data",
    register_to="penske-logistics-assistant",
    training_duration="5ep",  # 5 epochs
    learning_rate="1e-5"
)

# Monitor training
print(fm.get(run.name))
```

## Sample Interview Answer - Databricks

**Q: "How do you use Databricks for ML workflows?"**

**A:** "I use Databricks as the complete ML platform:

**1. Data Architecture (Medallion Pattern):**
```
Bronze (Raw) → Silver (Cleaned) → Gold (Aggregated) → Features
```
- Delta Lake for ACID transactions and time travel
- Unity Catalog for governance and access control

**2. Feature Engineering:**
- Feature Store for centralized, reusable features
- Point-in-time correct lookups prevent data leakage
- Same features for training and serving

**3. Experiment Tracking (MLflow):**
- Every experiment logged with params, metrics, artifacts
- Model Registry for staging: Dev → Staging → Production
- Automatic model signature and input examples

**4. Model Serving:**
- Real-time endpoints with auto-scaling
- Scale-to-zero for cost efficiency
- Automatic inference logging to Delta tables

**5. GenAI Integration:**
- Vector Search for RAG pipelines
- Foundation Model APIs (DBRX, Llama)
- Fine-tuning on logistics domain data

**Example Pipeline:**
```python
# 1. Features from Feature Store
training_set = fe.create_training_set(labels_df, feature_lookups)

# 2. Train with MLflow tracking
with mlflow.start_run():
    model.fit(X, y)
    mlflow.sklearn.log_model(model)

# 3. Register and deploy
mlflow.register_model(uri, "demand-forecaster")
create_serving_endpoint("demand-endpoint", model_version)

# 4. Use in agent
@tool
def predict_demand(region: str) -> str:
    return call_endpoint("demand-endpoint", region)
```

**Key Benefits:**
- Single platform for data + ML + GenAI
- Built-in governance with Unity Catalog
- Seamless scaling from notebook to production"

---

# 8. Traditional ML

## ML Algorithms You Should Know

### Classification
```python
# Logistics: Predict if shipment will be delayed
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import cross_val_score

# Features: weather, traffic, driver_experience, distance, load_weight
X = df[['weather_code', 'traffic_index', 'driver_exp_years', 'distance_miles', 'weight_lbs']]
y = df['is_delayed']

model = GradientBoostingClassifier(
    n_estimators=100,
    learning_rate=0.1,
    max_depth=5
)

# Cross-validation
scores = cross_val_score(model, X, y, cv=5, scoring='f1')
print(f"F1 Score: {scores.mean():.3f} (+/- {scores.std():.3f})")
```

### Regression (Demand Forecasting)
```python
# Predict next-day shipment volume
import xgboost as xgb

model = xgb.XGBRegressor(
    n_estimators=200,
    learning_rate=0.05,
    max_depth=6,
    subsample=0.8,
    colsample_bytree=0.8
)

model.fit(
    X_train, y_train,
    eval_set=[(X_val, y_val)],
    early_stopping_rounds=20,
    verbose=False
)

# Feature importance
importance = pd.DataFrame({
    'feature': X_train.columns,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)
```

### Clustering (Customer Segmentation)
```python
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Features: shipment_frequency, avg_value, avg_weight, region_diversity
scaler = StandardScaler()
X_scaled = scaler.fit_transform(customer_features)

# Elbow method for optimal k
inertias = []
for k in range(2, 10):
    kmeans = KMeans(n_clusters=k, random_state=42)
    kmeans.fit(X_scaled)
    inertias.append(kmeans.inertia_)

# Final clustering
kmeans = KMeans(n_clusters=4, random_state=42)
customer_segments = kmeans.fit_predict(X_scaled)
```

### Time Series (Forecasting)
```python
from prophet import Prophet

# Prepare data
df_prophet = df[['date', 'shipment_volume']].rename(
    columns={'date': 'ds', 'shipment_volume': 'y'}
)

# Add regressors
model = Prophet(
    yearly_seasonality=True,
    weekly_seasonality=True,
    daily_seasonality=False
)
model.add_regressor('fuel_price')
model.add_regressor('is_holiday')

model.fit(df_prophet)

# Forecast
future = model.make_future_dataframe(periods=30)
future['fuel_price'] = forecast_fuel_prices
future['is_holiday'] = holiday_flags
forecast = model.predict(future)
```

## Sample Interview Answer

**Q: "Describe your experience with traditional ML techniques."**

**A:** "I have strong foundations in traditional ML, which I apply in logistics:

**Classification - Delay Prediction:**
- Used Gradient Boosting to predict shipment delays
- Features: weather, traffic, driver metrics, route complexity
- Achieved 0.87 F1-score, enabling proactive customer notifications

**Regression - Demand Forecasting:**
- XGBoost model for next-day volume prediction
- Engineered lag features (1d, 7d, 30d) and rolling statistics
- MAPE of 8.2%, used for fleet capacity planning

**Clustering - Customer Segmentation:**
- K-means clustering on shipping behavior
- Identified 4 segments: High-value frequent, Seasonal bulk, Small regular, Occasional
- Enabled targeted service offerings

**Time Series - Long-term Forecasting:**
- Prophet for monthly forecasting with seasonality
- Added fuel price and economic indicators as regressors
- Used for annual budget planning

**Key Skills:**
- Feature engineering (domain-specific)
- Cross-validation and hyperparameter tuning
- Model interpretation (SHAP values)
- Production deployment with monitoring"

---

# 9. Evals, Guardrails & Safety

## LLM Evaluation Framework

### Evaluation Metrics

| Metric | What it Measures | When to Use |
|--------|------------------|-------------|
| **Accuracy** | Factual correctness | QA, extraction |
| **Relevance** | Answer addresses question | RAG, search |
| **Coherence** | Logical flow | Summarization |
| **Groundedness** | Supported by context | RAG (hallucination) |
| **Toxicity** | Harmful content | All outputs |
| **Latency** | Response time | Production |

### Building an Eval Pipeline

```python
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall
)

# Evaluate RAG system
results = evaluate(
    dataset=eval_dataset,
    metrics=[
        faithfulness,        # Is answer grounded in context?
        answer_relevancy,    # Is answer relevant to question?
        context_precision,   # Is retrieved context relevant?
        context_recall       # Is all needed context retrieved?
    ]
)

print(results)
# {'faithfulness': 0.92, 'answer_relevancy': 0.88, ...}
```

### Custom Eval for Logistics Domain

```python
class LogisticsEvaluator:
    def __init__(self, llm_judge):
        self.judge = llm_judge
    
    def evaluate_response(self, query, response, context):
        # 1. Factual accuracy (numbers, dates)
        accuracy_prompt = f"""
        Query: {query}
        Response: {response}
        Context: {context}
        
        Check if all numbers, dates, and facts in the response
        are accurate according to the context.
        Score 1-5 and explain.
        """
        accuracy_score = self.judge.evaluate(accuracy_prompt)
        
        # 2. Operational relevance
        relevance_prompt = f"""
        Query: {query}
        Response: {response}
        
        Is this response actionable for logistics operations?
        Score 1-5 and explain.
        """
        relevance_score = self.judge.evaluate(relevance_prompt)
        
        # 3. Safety check
        safety_score = self.check_safety(response)
        
        return {
            'accuracy': accuracy_score,
            'relevance': relevance_score,
            'safety': safety_score
        }
```

## Guardrails Implementation

```python
from guardrails import Guard
from guardrails.hub import ToxicLanguage, PIIFilter, ValidSQL

# Define guardrails
guard = Guard().use_many(
    ToxicLanguage(on_fail="exception"),
    PIIFilter(on_fail="fix"),  # Redact PII
    ValidSQL(on_fail="reask")  # Validate SQL queries
)

# Use in agent
@guard
def agent_response(query: str) -> str:
    response = llm.generate(query)
    return response

# Custom guardrail for logistics
class SafeQueryGuard:
    """Prevent dangerous database operations"""
    
    BLOCKED_PATTERNS = [
        r"DROP\s+TABLE",
        r"DELETE\s+FROM",
        r"TRUNCATE",
        r"UPDATE.*SET.*WHERE\s+1\s*=\s*1"
    ]
    
    def validate(self, query: str) -> bool:
        for pattern in self.BLOCKED_PATTERNS:
            if re.search(pattern, query, re.IGNORECASE):
                raise ValueError(f"Blocked dangerous query pattern: {pattern}")
        return True
```

## Sample Interview Answer

**Q: "How do you implement safety and guardrails for production agents?"**

**A:** "Safety is critical for enterprise agents. My approach:

**1. Input Validation:**
```python
def validate_user_input(query: str) -> str:
    # Length limits
    if len(query) > 1000:
        raise ValueError("Query too long")
    
    # Injection detection
    if detect_prompt_injection(query):
        raise SecurityError("Potential injection detected")
    
    # PII handling
    query = redact_pii(query)
    
    return query
```

**2. Output Guardrails:**
- Toxicity filtering (Azure Content Safety)
- PII redaction before display
- Factual grounding checks (RAG faithfulness)
- Domain-specific validation (valid shipment IDs, dates)

**3. Operational Guardrails:**
- Rate limiting per user/department
- Token budgets with alerts
- Query complexity limits
- Tool execution sandboxing

**4. Monitoring & Alerting:**
```python
# Log all interactions for audit
log_interaction(
    user_id=user.id,
    query=query,
    response=response,
    tools_used=tools,
    guardrails_triggered=triggered,
    latency_ms=latency
)

# Alert on anomalies
if guardrails_triggered or latency > 5000:
    send_alert(...)
```

**5. Continuous Evaluation:**
- Daily eval runs on sample of production queries
- Human review of flagged responses
- Regular red-teaming exercises"

---

# 10. MLOps & LLM Observability

## MLOps Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                    MLOPS PIPELINE                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  DATA ──▶ TRAIN ──▶ EVALUATE ──▶ DEPLOY ──▶ MONITOR        │
│                                                              │
│  ┌─────┐  ┌─────┐  ┌─────────┐  ┌──────┐  ┌─────────┐     │
│  │ DVC │  │MLflow│  │ Evals   │  │CI/CD │  │Prometheus│     │
│  │     │  │      │  │ Suite   │  │      │  │ Grafana │     │
│  └─────┘  └─────┘  └─────────┘  └──────┘  └─────────┘     │
│                                                              │
│  VERSIONING:                                                 │
│  - Data versioning (DVC, Delta Lake)                        │
│  - Model versioning (MLflow Model Registry)                 │
│  - Code versioning (Git)                                    │
│  - Config versioning (Hydra, YAML)                          │
│                                                              │
│  AUTOMATION:                                                 │
│  - Automated retraining on data drift                       │
│  - A/B testing for model rollout                            │
│  - Automated rollback on performance degradation            │
└─────────────────────────────────────────────────────────────┘
```

## LLM Observability

### Key Metrics to Track

| Category | Metrics |
|----------|---------|
| **Performance** | Latency (p50, p95, p99), throughput |
| **Quality** | Relevance scores, user feedback, task success |
| **Cost** | Token usage, cost per query, cost by model |
| **Reliability** | Error rate, timeout rate, retry rate |
| **Safety** | Guardrail triggers, flagged content |

### Observability Stack

```python
# Using LangSmith for tracing
from langsmith import Client
from langchain.callbacks import LangChainTracer

client = Client()
tracer = LangChainTracer(project_name="penske-logistics-agent")

# All agent calls are automatically traced
agent.run(query, callbacks=[tracer])

# Custom span for detailed tracking
from opentelemetry import trace

tracer = trace.get_tracer("logistics-agent")

with tracer.start_as_current_span("demand_forecast") as span:
    span.set_attribute("region", region)
    span.set_attribute("model", "gpt-4")
    
    result = forecast_demand(region)
    
    span.set_attribute("prediction", result)
    span.set_attribute("latency_ms", latency)
```

### Dashboard Metrics

```python
# Prometheus metrics for LLM monitoring
from prometheus_client import Counter, Histogram, Gauge

# Counters
llm_requests_total = Counter(
    'llm_requests_total',
    'Total LLM requests',
    ['model', 'status']
)

# Histograms
llm_latency = Histogram(
    'llm_latency_seconds',
    'LLM request latency',
    ['model'],
    buckets=[0.1, 0.5, 1, 2, 5, 10]
)

llm_tokens = Histogram(
    'llm_tokens',
    'Tokens per request',
    ['model', 'type'],  # type: input/output
    buckets=[100, 500, 1000, 2000, 4000]
)

# Gauges
active_requests = Gauge(
    'llm_active_requests',
    'Currently processing requests'
)
```

## Sample Interview Answer

**Q: "How do you approach MLOps and observability for LLM systems?"**

**A:** "LLM systems require specialized observability:

**1. Tracing:**
- Every request traced end-to-end (LangSmith/Arize)
- Capture: prompt, response, latency, tokens, model version
- Enable debugging and optimization

**2. Metrics Dashboard:**
```
┌────────────────────────────────────────────┐
│  LOGISTICS AGENT DASHBOARD                 │
├────────────────────────────────────────────┤
│  Requests/min: 145    Error Rate: 0.3%    │
│  P95 Latency: 2.3s    Daily Cost: $127    │
├────────────────────────────────────────────┤
│  [Latency Chart]      [Cost Chart]        │
│  [Error Breakdown]    [Top Queries]       │
└────────────────────────────────────────────┘
```

**3. Alerting Rules:**
- Latency > 5s for 5 minutes
- Error rate > 1%
- Daily cost > budget threshold
- Guardrail trigger rate > 5%

**4. Continuous Improvement:**
- Weekly review of low-rated responses
- A/B testing new prompts/models
- Drift detection on input distribution

**5. Cost Management:**
- Token budgets per department
- Caching for repeated queries
- Model routing (GPT-3.5 for simple, GPT-4 for complex)"

---

# 11. Sample Interview Q&A

## Behavioral Questions

### Q1: "Tell me about a challenging GenAI project you've worked on."

**A:** "I built a logistics analytics agent that needed to:
1. Query multiple data sources (Snowflake, APIs, files)
2. Provide accurate forecasts with explanations
3. Handle ambiguous user queries gracefully

**Challenge:** The agent was hallucinating shipment numbers.

**Solution:**
- Implemented strict RAG with source citations
- Added validation layer comparing LLM output to actual data
- Created guardrails that flagged statistical outliers

**Result:** Reduced hallucination rate from 15% to <2%, increased user trust and adoption."

---

### Q2: "How do you ensure GenAI systems are production-ready?"

**A:** "My production readiness checklist:

**Reliability:**
- [ ] Retry logic with exponential backoff
- [ ] Fallback models/responses
- [ ] Circuit breakers for external services
- [ ] Graceful degradation

**Scalability:**
- [ ] Async processing for long operations
- [ ] Request queuing and rate limiting
- [ ] Horizontal scaling capability
- [ ] Caching strategy

**Observability:**
- [ ] Comprehensive logging
- [ ] Metrics and dashboards
- [ ] Alerting rules
- [ ] Distributed tracing

**Security:**
- [ ] Input validation
- [ ] Output filtering
- [ ] Authentication/authorization
- [ ] Audit logging

**Testing:**
- [ ] Unit tests for tools
- [ ] Integration tests for agent flows
- [ ] Eval suite for quality
- [ ] Load testing"

---

### Q3: "How would you handle a situation where the agent gives incorrect information?"

**A:** "Immediate response:
1. **Acknowledge**: Thank user for reporting
2. **Investigate**: Review traces to understand failure
3. **Mitigate**: Update guardrails if needed

Root cause analysis:
1. Was it a retrieval failure (wrong context)?
2. Was it a generation failure (hallucination)?
3. Was it a data quality issue?

Prevention:
1. Add to eval dataset as regression test
2. Improve retrieval if context issue
3. Add guardrail if pattern is detectable
4. Consider human-in-the-loop for high-stakes queries"

---

### Q4: "How do you balance speed vs. accuracy in agent responses?"

**A:** "I use a tiered approach:

**Tier 1 - Fast (simple queries):**
- Use smaller/faster model (GPT-3.5)
- Minimal retrieval
- Target: <1s latency

**Tier 2 - Balanced (standard queries):**
- GPT-4 with standard RAG
- 3-5 retrieved documents
- Target: 2-3s latency

**Tier 3 - Thorough (complex/critical):**
- GPT-4 with extensive retrieval
- Multi-step reasoning
- Human review option
- Target: 5-10s acceptable

Query classification determines tier automatically based on complexity signals."

---

## Technical Deep-Dive Questions

### Q5: "Walk me through designing an agent for Penske's dispatch operations."

**A:** 
```
┌─────────────────────────────────────────────────────────────┐
│           DISPATCH OPERATIONS AGENT                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  USER: "What trucks are available for a 5000 lb pickup      │
│         in Chicago tomorrow morning?"                        │
│                                                              │
│  AGENT REASONING:                                            │
│  1. Parse: location=Chicago, weight=5000lb, time=tomorrow AM │
│  2. Query fleet DB for available trucks in Chicago          │
│  3. Filter by weight capacity >= 5000 lb                    │
│  4. Check driver schedules for tomorrow AM                  │
│  5. Rank by efficiency (fuel, route optimization)           │
│  6. Return top 3 options with details                       │
│                                                              │
│  TOOLS NEEDED:                                               │
│  - query_fleet_inventory(location, min_capacity)            │
│  - check_driver_availability(driver_ids, datetime)          │
│  - get_route_estimate(origin, destination)                  │
│  - check_maintenance_status(truck_ids)                      │
│                                                              │
│  GUARDRAILS:                                                 │
│  - Validate truck IDs exist                                 │
│  - Verify weight limits                                     │
│  - Check for scheduling conflicts                           │
│  - Log all dispatch queries for audit                       │
└─────────────────────────────────────────────────────────────┘
```

---

### Q6: "How would you implement RAG for Penske's safety documentation?"

**A:** 
```python
# 1. Document Processing Pipeline
class SafetyDocProcessor:
    def process(self, doc_path):
        # Extract text preserving structure
        content = extract_with_structure(doc_path)
        
        # Chunk by section (not arbitrary splits)
        chunks = semantic_chunk(content, max_tokens=500)
        
        # Enrich with metadata
        for chunk in chunks:
            chunk.metadata = {
                'doc_type': 'safety_procedure',
                'department': extract_department(chunk),
                'last_updated': doc.modified_date,
                'regulation_refs': extract_regulations(chunk)
            }
        
        return chunks

# 2. Retrieval with Safety Priority
def retrieve_safety_docs(query, user_context):
    # Always include critical safety docs
    critical_docs = get_critical_safety_docs(user_context.department)
    
    # Semantic search
    semantic_results = vector_search(query, k=5)
    
    # Keyword search for regulation numbers
    keyword_results = keyword_search(query, k=3)
    
    # Merge and deduplicate
    all_docs = merge_results(critical_docs, semantic_results, keyword_results)
    
    # Re-rank by relevance and recency
    ranked = rerank(query, all_docs)
    
    return ranked[:7]

# 3. Generation with Safety Constraints
def generate_safety_response(query, context):
    response = llm.generate(
        system="You are a safety expert. Always cite specific procedures. "
               "If unsure, recommend consulting the safety manual directly.",
        user=f"Context: {context}\n\nQuestion: {query}"
    )
    
    # Validate citations exist
    validate_citations(response, context)
    
    # Add disclaimer for critical procedures
    if is_critical_procedure(query):
        response += "\n\n⚠️ Always verify with your supervisor for critical procedures."
    
    return response
```

---

## Questions to Ask the Interviewer

1. "What's the current state of GenAI adoption at Penske? Are there existing agents in production?"

2. "What are the primary use cases you're targeting with GenAI agents?"

3. "How is the team structured? Will I be working closely with data engineers, or is this more of a full-stack ML role?"

4. "What's the typical path from prototype to production for a new agent?"

5. "How do you handle data governance and compliance for GenAI systems?"

6. "What's the current observability stack for ML systems?"

---

# PREPARATION CHECKLIST

## Before the Interview

- [ ] Review your Penske logistics project code
- [ ] Prepare 3-4 specific examples of GenAI projects
- [ ] Practice explaining MCP architecture
- [ ] Review Snowflake and Databricks syntax
- [ ] Prepare questions about Penske's tech stack

## Key Points to Emphasize

1. **Production Experience**: You've deployed agents, not just prototyped
2. **Full Stack**: Data → Model → Deployment → Monitoring
3. **Safety First**: Guardrails and evals are core, not afterthoughts
4. **Business Value**: Always connect technical work to outcomes
5. **Continuous Learning**: GenAI is evolving; show you stay current

## Technical Demos Ready

- Your Penske logistics analytics dashboard
- Gradio agent interface
- Code samples for MCP, RAG, evals

---

*Good luck with your interview! 🚀*
