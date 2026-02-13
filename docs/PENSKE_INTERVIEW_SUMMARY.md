# Penske Senior Data Scientist Interview - Quick Summary

> A condensed reference guide without code examples. See `PENSKE_INTERVIEW_PREP.md` for full details with code.

---

## 1. GenAI Agents

### What Are They?
Autonomous AI systems that use LLMs to reason, plan, and execute tasks by calling external tools.

### Key Components
| Component | Purpose |
|-----------|---------|
| **LLM (Brain)** | Reasoning, planning, natural language understanding |
| **Tools** | Functions the agent can call (APIs, databases, search) |
| **Memory** | Short-term (conversation) and long-term (vector store) |
| **Orchestrator** | Controls the agent loop (LangChain, LangGraph, AutoGen) |

### Agent Architectures
- **ReAct**: Reason → Act → Observe loop
- **Plan-and-Execute**: Create full plan first, then execute steps
- **Multi-Agent**: Specialized agents collaborate (researcher, writer, critic)

### Interview Talking Points
- "I've built agents that query databases, search documents, and call APIs"
- "I use tool validation and output guardrails to ensure safety"
- "I implement human-in-the-loop for high-stakes decisions"

---

## 2. MCP (Model Context Protocol)

### What Is It?
Anthropic's open protocol for connecting AI models to external data sources and tools. Think of it as "USB-C for AI" - one standard interface.

### Architecture
```
AI Application ←→ MCP Client ←→ MCP Server ←→ Data Source
```

### Key Features
| Feature | Description |
|---------|-------------|
| **Tools** | Functions the model can call |
| **Resources** | Read-only data access (files, DB records) |
| **Prompts** | Reusable prompt templates |
| **Sampling** | Server can request LLM completions |

### Why It Matters
- Standardized way to connect LLMs to enterprise systems
- Security-first design with capability negotiation
- Replaces custom API integrations

---

## 3. Knowledge Bases & RAG

### RAG Pipeline
1. **Ingest** → Chunk documents → Generate embeddings → Store in vector DB
2. **Query** → Embed user question → Semantic search → Retrieve top-k docs
3. **Generate** → Pass docs + question to LLM → Generate answer

### Key Concepts
| Concept | Description |
|---------|-------------|
| **Chunking** | Split documents (512-1024 tokens typical) |
| **Embeddings** | Dense vectors representing semantic meaning |
| **Vector Search** | Find similar documents by cosine similarity |
| **Reranking** | Re-score results with cross-encoder for better precision |

### Advanced Techniques
- **Hybrid Search**: Combine keyword (BM25) + semantic search
- **Query Expansion**: Rewrite queries for better retrieval
- **Parent-Child Chunking**: Retrieve child, return parent for context
- **Self-RAG**: Agent decides when retrieval is needed

---

## 4. Vibe Coding

### What Is It?
Rapid AI-assisted prototyping using natural language to generate code quickly. Focus on iteration speed over perfection.

### Workflow
1. Describe what you want in plain English
2. AI generates initial code
3. Test and iterate with conversational refinements
4. Refactor once the concept works

### Best Practices
- Start with clear intent, not implementation details
- Use AI for boilerplate, review for correctness
- Prototype fast, productionize carefully

---

## 5. Cloud Expertise

### Azure (Preferred by Penske)
| Service | Use Case |
|---------|----------|
| **Azure OpenAI** | GPT-4, embeddings, fine-tuning |
| **Azure AI Search** | Vector search, hybrid search, semantic ranking |
| **Azure Cosmos DB** | Document storage, vector search |
| **Azure Functions** | Serverless compute for agents |
| **Azure Monitor** | Observability, logging, alerting |

### AWS Alternative
| Azure | AWS Equivalent |
|-------|----------------|
| Azure OpenAI | Amazon Bedrock |
| Azure AI Search | Amazon OpenSearch |
| Cosmos DB | DynamoDB |
| Azure Functions | Lambda |

### Key Architecture Pattern
```
User → Azure Front Door → Container Apps (Agent) → Azure OpenAI
                                    ↓
                           Azure AI Search (RAG)
                                    ↓
                              Snowflake (Data)
```

---

## 6. SQL & Snowflake

### Snowflake Architecture
| Layer | Purpose |
|-------|---------|
| **Cloud Services** | Query optimization, security, metadata |
| **Compute** | Virtual warehouses (independently scalable) |
| **Storage** | Columnar, compressed, on cloud object storage |

**Key Insight**: Compute and storage are separate - scale independently, pay separately.

### Key Features for AI/ML
| Feature | Use Case |
|---------|----------|
| **Cortex** | Built-in LLMs, embeddings, sentiment analysis |
| **Snowpark** | Run Python/ML directly in Snowflake |
| **Dynamic Tables** | Real-time feature computation |
| **Streams** | Change data capture for event processing |
| **Time Travel** | Query/restore historical data (up to 90 days) |

### SQL Patterns to Know
- **Window Functions**: Rolling averages, LAG/LEAD, RANK
- **CTEs**: Common table expressions for readable queries
- **Sessionization**: Group events into sessions using gaps
- **Funnel Analysis**: Track conversion through stages
- **Feature Engineering**: Lag features, rolling stats, calendar features

---

## 7. Databricks

### Lakehouse Architecture
| Layer | Purpose |
|-------|---------|
| **Unity Catalog** | Governance, lineage, access control |
| **Delta Lake** | ACID transactions, time travel, schema evolution |
| **Compute** | Clusters for notebooks, jobs, SQL, model serving |
| **Storage** | ADLS (Azure) or S3 (AWS) |

### Medallion Architecture
```
Bronze (Raw) → Silver (Cleaned) → Gold (Aggregated) → Features
```

### Key Components
| Component | Purpose |
|-----------|---------|
| **Delta Lake** | Reliable data lake with ACID transactions |
| **MLflow** | Experiment tracking, model registry, deployment |
| **Feature Store** | Centralized features with point-in-time lookups |
| **Model Serving** | Real-time endpoints with auto-scaling |
| **Vector Search** | Similarity search for RAG |

### MLflow Workflow
1. **Track**: Log params, metrics, artifacts during training
2. **Register**: Version models in Model Registry
3. **Stage**: Transition through None → Staging → Production
4. **Serve**: Deploy to endpoints with scale-to-zero

---

## 8. Traditional ML

### Algorithms by Task

| Task | Algorithms | Metrics |
|------|------------|---------|
| **Classification** | Logistic Regression, Random Forest, XGBoost, LightGBM | Accuracy, Precision, Recall, F1, AUC-ROC |
| **Regression** | Linear Regression, XGBoost, LightGBM | RMSE, MAE, MAPE, R² |
| **Clustering** | K-Means, DBSCAN, Hierarchical | Silhouette Score, Inertia |
| **Time Series** | ARIMA, Prophet, LSTM | MAE, MAPE, forecast intervals |

### Feature Engineering
- **Lag Features**: Previous values (t-1, t-7, t-30)
- **Rolling Stats**: Moving average, std, min, max
- **Calendar Features**: Day of week, month, holidays
- **Encoding**: One-hot, target encoding, embeddings

### Model Selection
- Start simple (linear models) → add complexity if needed
- Use cross-validation to avoid overfitting
- Consider interpretability vs. performance tradeoff

---

## 9. Evals & Guardrails

### LLM Evaluation Types
| Type | What It Measures |
|------|------------------|
| **Factual Accuracy** | Are facts correct? (RAG faithfulness) |
| **Relevance** | Does response address the question? |
| **Coherence** | Is response well-structured? |
| **Safety** | No harmful, biased, or toxic content |
| **Tool Use** | Correct tool selection and parameter passing |

### Guardrail Categories
| Category | Implementation |
|----------|----------------|
| **Input Validation** | PII detection, prompt injection defense |
| **Output Filtering** | Content moderation, hallucination detection |
| **Tool Validation** | SQL injection prevention, permission checks |
| **Rate Limiting** | Token budgets, request throttling |

### Key Metrics
- **Pass Rate**: % of outputs passing all guardrails
- **Latency Impact**: Added time from guardrail checks
- **False Positive Rate**: Valid outputs incorrectly blocked

---

## 10. MLOps & LLM Observability

### MLOps Components
| Component | Purpose | Tools |
|-----------|---------|-------|
| **Experiment Tracking** | Log params, metrics, artifacts | MLflow, Weights & Biases |
| **Model Registry** | Version and stage models | MLflow, SageMaker |
| **CI/CD** | Automated testing and deployment | GitHub Actions, Azure DevOps |
| **Monitoring** | Detect drift, track performance | Evidently, WhyLabs |

### LLM Observability
| Metric | Why It Matters |
|--------|----------------|
| **Latency** | User experience, SLA compliance |
| **Token Usage** | Cost management |
| **Error Rate** | Reliability tracking |
| **Hallucination Rate** | Quality assurance |
| **User Feedback** | Ground truth for evals |

### Key Practices
- Log every LLM call with full context
- Track costs per user/feature/model
- Set up alerts for latency spikes and error rates
- Build dashboards for real-time monitoring

---

## Quick Reference: What Penske Wants

Based on the job description:

| Skill | What to Demonstrate |
|-------|---------------------|
| **GenAI Agents** | Production deployment experience, tool orchestration |
| **MCP** | Understanding of protocol, security considerations |
| **Knowledge Bases** | RAG implementation, vector search optimization |
| **Vibe Coding** | Rapid prototyping ability, AI-assisted development |
| **Azure** | Hands-on with OpenAI, AI Search, Functions |
| **Snowflake** | Complex SQL, Cortex, Snowpark, Dynamic Tables |
| **Databricks** | MLflow, Feature Store, Delta Lake, Model Serving |
| **Traditional ML** | Classification, regression, clustering, time series |
| **Evals/Guardrails** | Safety frameworks, evaluation pipelines |
| **MLOps** | CI/CD for ML, monitoring, observability |

---

## Interview Answer Templates

### "Tell me about your GenAI agent experience"
> "I've built production agents using LangGraph for orchestration. The agents query Snowflake for business data, search vector stores for documents, and call external APIs. I implemented guardrails for SQL validation and content filtering, with human-in-the-loop for high-stakes decisions."

### "How do you evaluate LLM outputs?"
> "I use a multi-layer approach: automated metrics for relevance and coherence, LLM-as-judge for nuanced quality assessment, and human evaluation for ground truth. For RAG, I specifically measure faithfulness to retrieved context and citation accuracy."

### "Describe your MLOps workflow"
> "I use MLflow for experiment tracking and model registry, with automated CI/CD pipelines that run tests, validate model performance against baselines, and deploy to staging. Production deployment requires approval after A/B testing shows improvement."

### "How do you handle data quality in ML?"
> "I implement the medallion architecture: Bronze for raw ingestion, Silver for cleaned/validated data with constraints, Gold for aggregated features. I use Delta Lake for ACID transactions and time travel to debug data issues."

---

*For full code examples, see `PENSKE_INTERVIEW_PREP.md`*
