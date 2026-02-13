# Penske Senior Data Scientist — Round 2 Final Prep

> **Interview Format:**
> - **First Half (~1 hour):** Technical questions about your AI background
> - **Second Half (remaining):** Use case system design — no coding, walk through your approach
> - **Goal:** Understand your thought process

---

# BEFORE THE INTERVIEW

## Penske Company Research (Use This to Impress)

### What Penske Is Doing RIGHT NOW with AI

**Agentic AI with Augment (January 2026):**
- Penske is implementing Augment's agentic AI platform after a successful 6-month pilot
- The AI "teammate" validates the status of **~600,000 loads**
- Expects **30-40% productivity gains** by eliminating routine manual follow-ups
- The AI reaches out to carrier dispatchers via **phone, email, or text** when shipment updates aren't available
- Adapts to each carrier's preferred escalation path
- Uses human intervention for exceptions
- Quote from Jeff Jackson (President): *"AI at this scale is about giving customers more convenience, certainty and clarity in an increasingly complex and dynamic operating environment."*

**Catalyst AI (Penske Truck Leasing):**
- Fleet management platform with AI-powered diagnostics
- Includes a "Fantasy Fleet" tool to optimize rolling stock performance

**Key Insight for YOUR Interview:**
> Penske is moving from **AI experimentation to execution**. They want people who can build production systems, not just prototypes. Their focus is on **agentic AI that takes action** — not just analytics that surfaces insights. This is exactly what the job description asks for.

### How to Reference This in Answers

| When They Ask... | Drop This Knowledge... |
|-----------------|----------------------|
| "Why Penske?" | "I've been following your Augment partnership — the shift from AI experimentation to execution resonates with me. I want to build agents that take action, not just generate reports." |
| "Tell me about agents" | "What Penske is doing with Augment is a great example — an AI teammate that reaches out to carriers via their preferred channel. I'd build similar agentic systems for internal operations." |
| "How would you approach..." | "Given Penske's Azure + Snowflake + Databricks stack and the 600K+ loads you're managing, I'd design this to..." |

---

## Your Sound Bites (Memorize These)

### "Tell me about yourself." (2-3 sentences)

> "I'm a Senior Data Scientist with [X] years of experience building production AI systems. Most recently, I've focused on GenAI agent development — building agents that query databases, search knowledge bases, and take actions through tool integrations. I'm excited about Penske because you're moving from AI experimentation to execution, and that's exactly the kind of hands-on, production-grade work I thrive in."

### "Tell me about your career."

> "My career has progressed from traditional ML — building classification and prediction models — to modern AI engineering with GenAI agents and RAG systems. What makes me effective is that I bridge the gap between data science and engineering: I don't just build models, I deploy them. I've worked across cloud platforms including Azure, with data tools like Snowflake and Databricks, and I've built end-to-end pipelines from data ingestion through model serving. I want this role because it combines everything I'm passionate about — agents, production ML, and real business impact in logistics."

### "What are your strengths?"

> "Three key strengths:
> 1. **Production mindset** — I design for failure from day one: retry logic, fallback models, guardrails, and monitoring. I've deployed agents that handle thousands of requests daily with <2% error rates.
> 2. **Full-stack AI** — I'm equally comfortable writing complex SQL in Snowflake, training XGBoost models in Databricks, and building LangChain agents with Azure OpenAI.
> 3. **Clear communication** — I can explain a RAG architecture to an executive and debug a vector search pipeline with an engineer. I translate business problems into technical solutions and back."

---

# FIRST HALF: Technical AI Questions (~1 Hour)

## How This Section Works

They'll ask open-ended questions about your AI experience. **No coding.** They want to hear you think out loud. Use the structure:

```
1. Answer the question directly (10 seconds)
2. Explain the concept clearly (30 seconds)
3. Give a concrete example from your experience (30-60 seconds)
4. Connect it to Penske if possible (10 seconds)
```

---

## Topic 1: GenAI Agents

### "What is a GenAI agent and how does it differ from a chatbot?"

> "A chatbot is a single prompt-in, response-out system. An agent is fundamentally different — it has a **reasoning loop**. It receives a task, **thinks** about what to do, **calls tools** (databases, APIs, search), **observes** the result, and decides whether it's done or needs another step.
>
> The key components are: an LLM for reasoning, tools for taking actions, memory for context, and an orchestrator that manages the loop.
>
> For example, if a dispatcher asks 'Why is shipment X late?', a chatbot would generate a generic response. An agent would: query the shipment database → check the weather API → look up the route history → and synthesize a specific answer: 'Shipment X is 90 minutes behind due to winter weather in Oklahoma. Based on historical patterns for this route, the delay is likely to extend to 2 hours.'
>
> This is exactly what Penske is doing with the Augment platform — agentic AI that actively reaches out and takes action rather than passively waiting."

### "What agent architectures have you worked with?"

> "I've used three main patterns:
>
> **ReAct (Reason + Act):** The agent alternates between reasoning and action. Best for open-ended investigation — like 'analyze why Zone 5 delays increased.' The agent decides at each step what to investigate next.
>
> **Plan-and-Execute:** The agent creates a full plan upfront, then executes step by step. Best for well-defined multi-step tasks — like generating a weekly logistics report. More predictable, easier to audit.
>
> **Router + Specialists:** A lightweight router classifies the request and dispatches to a specialist agent. I'd use this at Penske — a router sending shipment tracking queries to one agent, route optimization to another, and knowledge questions to a RAG agent.
>
> The choice depends on the task. For Penske's operations, I'd combine them: router for classification, ReAct for investigation, and Plan-and-Execute for reporting."

### "How do you decide which LLM to use for an agent?"

> "Five factors:
>
> **1. Task complexity:** Simple lookups → GPT-3.5. Complex reasoning → GPT-4. Long document analysis → Claude (200K context).
>
> **2. Enterprise requirements:** Penske is on Azure, so Azure OpenAI is the natural choice — private endpoints, SLAs, data stays in your VNet.
>
> **3. Cost:** I tier models. Route 70% of simple queries to GPT-3.5 (~$0.50/1M tokens) and 30% of complex queries to GPT-4 (~$30/1M tokens). That cuts costs by 60%.
>
> **4. Latency:** If real-time response is needed, smaller models or cached responses. For batch processing, quality over speed.
>
> **5. Function calling support:** OpenAI models have the best native function calling, which is critical for agents. Claude is catching up with MCP."

### "How do you handle agent failures in production?"

> "Defense in depth:
>
> **Retry with backoff** for transient failures — API timeouts, rate limits. Max 3 retries.
>
> **Fallback models** — if GPT-4 is slow, fall back to GPT-3.5 for simple tasks.
>
> **Graceful degradation** — if the agent can't complete fully, return what it has: 'I found the shipment data but couldn't calculate the optimized route. Here's the current status.'
>
> **Circuit breaker** — if error rate exceeds 10% in 5 minutes, stop sending requests, alert the team.
>
> **Human escalation** — for critical operations, two failures routes to a human with full context of what the agent tried.
>
> At Penske, this matters because dispatchers rely on these systems for time-sensitive decisions. The system needs to be reliable even when individual components fail."

### "How do you prevent hallucination in a production agent?"

> "Five layers:
>
> **1. Grounding:** Agent only answers from retrieved context, never from general knowledge. System prompt: 'Only use the provided documents. If the answer isn't there, say I don't know.'
>
> **2. Temperature zero** for all factual tasks.
>
> **3. Source attribution:** Every answer must cite which document or database record it used. If the agent can't cite a source, it flags uncertainty.
>
> **4. Post-generation verification:** Extract claims from the response and verify against the database. If the agent says 'Shipment arrives at 3pm,' check that against the actual ETA.
>
> **5. Evaluation pipeline:** Automated test suite of 200+ questions with known answers. Runs weekly, catches regression."

---

## Topic 2: MCP (Model Context Protocol)

### "What is MCP and why does it matter?"

> "MCP is Anthropic's open protocol for connecting AI models to external data sources and tools. I describe it as **USB-C for AI** — one standard interface for any data source.
>
> Before MCP, every agent-to-data connection was custom. If you had 5 data sources and 3 AI tools, that's 15 custom integrations. With MCP, each data source implements one MCP server, and any MCP client can connect.
>
> **Architecture:**
> ```
> AI App ←→ MCP Client ←→ MCP Server ←→ Data Source
> ```
>
> At Penske, I'd build MCP servers for Snowflake (shipment data), fleet management systems, and the document knowledge base. Any AI tool — Claude, internal agents, developer tools — can then access all of these through the standard MCP protocol.
>
> The three key MCP primitives are **Tools** (functions the model can call), **Resources** (read-only data access), and **Prompts** (reusable prompt templates)."

### "How would you build an MCP server for Penske's Snowflake data?"

> "The MCP server would expose Penske's Snowflake data safely:
>
> **Tools I'd expose:**
> - `get_shipment_status(shipment_id)` — lookup a specific shipment
> - `query_route_performance(route_id, date_range)` — route KPIs
> - `search_shipments(filters)` — flexible search with safety constraints
>
> **Resources I'd expose:**
> - Route definitions and metadata
> - KPI dashboards (read-only)
> - Standard report templates
>
> **Security:** The MCP server sits between the AI and Snowflake. It enforces role-based access — a customer-facing agent only calls `get_shipment_status`, while an internal analytics agent gets broader access. All queries are parameterized (no raw SQL injection). Write operations are blocked.
>
> This is safer than giving the agent direct Snowflake access because the MCP server validates every request before it reaches the database."

---

## Topic 3: Knowledge Bases & RAG

### "How do you design a knowledge base for enterprise use?"

> "Four-step approach:
>
> **1. Ingest:** Gather documents from SharePoint, Confluence, PDFs, manuals. Parse and preserve structure (headings, tables, sections).
>
> **2. Chunk:** Split documents into 300-500 token chunks with overlap. I use semantic chunking — respect paragraph and section boundaries rather than cutting mid-sentence. Each chunk gets metadata: document title, section, last updated, access level.
>
> **3. Index:** Generate embeddings (Azure OpenAI ada-002) and store in Azure AI Search. I use **hybrid search** — vector similarity for semantic queries plus BM25 keyword search for exact terms like shipment IDs or policy numbers.
>
> **4. Retrieve + Generate:** For each query, hybrid search retrieves top 20 candidates, a cross-encoder reranks to top 5, then the LLM generates an answer with citations.
>
> At Penske, the knowledge base would cover SOPs, safety manuals, compliance documents, and training materials. The key differentiator is hybrid search — you need both 'what's the process for handling damaged freight?' (semantic) and 'find DOT regulation 49 CFR 395' (keyword exact match)."

### "What's the difference between naive RAG and production RAG?"

> "Huge gap:
>
> | Aspect | Naive RAG | Production RAG |
> |--------|-----------|----------------|
> | **Chunking** | Fixed 500 tokens | Semantic, respects document structure |
> | **Search** | Vector only | Hybrid (vector + BM25) + reranking |
> | **Grounding** | Hope the LLM stays on topic | Verify claims against sources |
> | **Freshness** | Static index | Incremental updates, change detection |
> | **Access control** | None | Role-based, document-level permissions |
> | **Evaluation** | Manual spot checks | Automated test suite, regression testing |
> | **Monitoring** | None | Relevance scores, hallucination rate, latency |
>
> Production RAG at Penske would also need: document versioning (SOPs change), multi-language support if operating internationally, and handling of tables and structured data in documents."

---

## Topic 4: Cloud, Snowflake & Databricks

### "How do you work across Azure, Snowflake, and Databricks?"

> "Each serves a distinct purpose in the data stack:
>
> **Snowflake** is the analytical data warehouse. It's where all structured business data lives — shipments, routes, customers, KPIs. It powers BI dashboards, SQL analytics, and serves as the source of truth. Snowflake Cortex also brings AI functions directly into SQL.
>
> **Databricks** is the ML and data engineering platform. Feature engineering with Spark, model training with MLflow, Delta Lake for data pipelines. The Feature Store ensures consistent features across models.
>
> **Azure** provides the infrastructure and AI services — Azure OpenAI for LLMs, Azure AI Search for vector search, Event Hubs for streaming, Key Vault for secrets, VNet for security.
>
> **How they connect:** Data flows from sources through Databricks (ETL, Medallion Architecture) into Snowflake (analytics). Databricks also reads from Snowflake for ML feature engineering, trains models, and serves predictions. Azure OpenAI powers the agent layer on top.
>
> At Penske with 600K+ loads, the data volume justifies all three: Snowflake for fast SQL queries, Databricks for heavy ML processing, and Azure for the AI and infrastructure layer."

### "Explain the Medallion Architecture."

> "Three layers of increasing data quality:
>
> **Bronze (Raw):** Data lands as-is. GPS pings, TMS exports, carrier EDI files. Schema-on-read, append-only. Never modify Bronze — it's your audit trail.
>
> **Silver (Cleaned):** Apply quality rules — deduplicate, validate, standardize. GPS coordinates validated to reasonable ranges, addresses normalized, timestamps converted to UTC. This is where you handle nulls, outliers, and schema enforcement.
>
> **Gold (Business-Ready):** Aggregated for specific use cases — route performance scorecards, daily delivery KPIs, driver efficiency metrics. Gold tables power dashboards and feed ML models.
>
> At Penske: Bronze has raw GPS events and shipment logs. Silver has cleaned shipments with validated locations and standardized carrier info. Gold has the 'route_performance_daily' and 'driver_scorecard_monthly' tables that dispatchers and analysts query."

---

## Topic 5: Traditional ML

### "Walk me through building a classification model for predicting shipment delays."

> "End-to-end:
>
> **Define the problem:** Binary classification — will this shipment arrive >30 minutes late? Success metric: Precision-Recall AUC (delays are the minority class we care about catching).
>
> **Feature engineering:** Historical route delay rate, driver on-time percentage, truck age and maintenance status, weather severity forecast, day of week, cargo weight, origin/destination congestion scores. All from the Feature Store to ensure consistency.
>
> **Model choice:** XGBoost — handles mixed feature types, great with tabular data, fast to train, interpretable with SHAP. I'd compare against LightGBM as well.
>
> **Key details:**
> - Time-based split (not random) — train on older data, test on newer
> - Handle 85/15 class imbalance with class weights in XGBoost
> - SHAP values for explainability — dispatchers need to know WHY a delay is predicted
> - Calibrated probabilities so '80% likely delayed' actually means 80%
>
> **Deployment:** Register in MLflow, serve via Databricks endpoint for real-time, batch scoring nightly for next-day shipments. Monitor for data drift weekly."

### "How do you explain model decisions to non-technical stakeholders?"

> "SHAP values are my go-to. Instead of saying 'the model predicts 78% delay probability,' I show:
>
> 'This shipment has a high delay risk because:
> - Severe weather forecast on the route (+25%)
> - This route has been consistently slow recently (+18%)
> - The truck is due for maintenance (+12%)
> - However, the driver is very experienced (-8%)
>
> Recommended action: Consider rerouting via I-40 or scheduling maintenance before dispatch.'
>
> I also build simple dashboards showing the top contributing factors and validation metrics — 'of the last 100 shipments we flagged as high-risk, 82 were actually delayed.' This builds trust."

---

## Topic 6: Evals, Guardrails & MLOps

### "How do you evaluate an LLM-based agent?"

> "Three levels:
>
> **Component evals:** Test retrieval quality (recall@5), tool calling accuracy (right tool, right parameters), generation faithfulness (answer grounded in context).
>
> **End-to-end evals:** 200+ test cases with known correct answers. Run weekly. Automated scoring with BERTScore for similarity plus LLM-as-judge for nuance.
>
> **Production evals:** Real-time monitoring — latency, error rate, guardrail trigger rate, user satisfaction. Weekly human review of a random sample of responses.
>
> Every prompt change triggers the eval suite in CI/CD. If scores drop below threshold, the change is blocked."

### "What guardrails would you implement for a Penske agent?"

> "Five layers of defense:
>
> **Input:** Content filtering, topic restriction (stay on logistics), length limits, rate limiting.
>
> **Retrieval:** Access control (users only see authorized documents), relevance threshold (if no good match, say 'I don't know').
>
> **Generation:** Grounding check (answer supported by context?), PII filter (no driver SSNs in output), legal filter (no delivery guarantees).
>
> **Action:** Tool allowlist (read-only for customer-facing), parameter validation, human approval for high-impact actions.
>
> **Output:** Toxicity check, format validation, confidence threshold (low confidence → escalate to human).
>
> For Penske specifically: never expose internal routing details to customers, never make promises about specific delivery times (only ranges), and always route complaints to a human."

### "What's your MLOps approach?"

> "The lifecycle: Develop → Test → Register → Deploy → Monitor → Retrain.
>
> **Develop:** Experiments in Databricks notebooks, tracked in MLflow.
> **Test:** Unit tests for feature code, data validation with Great Expectations, model performance on holdout set.
> **Register:** MLflow Model Registry with Staging → Production promotion.
> **Deploy:** CI/CD via GitHub Actions — PR triggers tests, merge to main deploys to staging, manual approval promotes to production.
> **Monitor:** Feature drift (PSI), prediction drift, latency, error rates. Alerting when thresholds breached.
> **Retrain:** Monthly scheduled + triggered when drift exceeds threshold. Automated: pull data → compute features → train → evaluate → if better → deploy."

---

# SECOND HALF: Use Case System Design

## What They're Looking For

```
┌──────────────────────────────────────────────────────────────┐
│           SYSTEM DESIGN EVALUATION CRITERIA                   │
├──────────────────────────────────────────────────────────────┤
│                                                                │
│  1. CLARIFY (Do you ask the right questions first?)           │
│  2. STRUCTURE (Do you break the problem into components?)     │
│  3. TOOLS (Do you pick the right tools and explain why?)      │
│  4. TRADE-OFFS (Do you discuss alternatives and why not?)     │
│  5. PRODUCTION (Do you think about scale, cost, monitoring?)  │
│  6. COMMUNICATION (Can you explain clearly?)                  │
│                                                                │
└──────────────────────────────────────────────────────────────┘
```

## The Framework: How to Walk Through ANY Use Case

**Step 1 — Clarify (2 minutes):**
> "Before I design, let me understand the requirements..."
> - Who are the users?
> - What's the scale? (loads/day, users, latency needs)
> - What systems exist today?
> - What does success look like?

**Step 2 — High-Level Architecture (3 minutes):**
> Draw/describe the major components and data flow.
> Keep it simple: Data Sources → Processing → ML/AI → Serving → Users

**Step 3 — Deep Dive on Key Components (10-15 minutes):**
> Go deeper on 2-3 critical components. Explain HOW they work.
> This is where you show expertise.

**Step 4 — Tool Choices with Justification (5 minutes):**
> "I'd use X because [reason]. I considered Y but [trade-off]."

**Step 5 — Production Considerations (5 minutes):**
> Monitoring, failure handling, cost, security, scaling

**Step 6 — Iterate (ongoing):**
> "Does this align with what you had in mind? Should I go deeper on any part?"

---

## Practice Use Case 1: "Design an AI agent that helps dispatchers manage shipments"

### Step 1 — Clarify

> "A few questions:
> - How many dispatchers would use this? (Let's say 200)
> - How many shipments are they managing? (Given the 600K loads you process, let's say 3,000/dispatcher)
> - What systems do they use today? (I'll assume a TMS + Snowflake for analytics)
> - Are they asking questions or should the agent also take actions?"

### Step 2 — High-Level Architecture

> "I'd design this as a **multi-tool agent** with a natural language interface:
>
> ```
> Dispatcher (chat/Teams)
>       ↓
> Agent (Azure OpenAI + LangChain)
>       ↓
> ┌─────────────────────────────────────────┐
> │              TOOLS                        │
> ├────────────┬────────────┬────────────────┤
> │ Shipment   │ Route      │ Knowledge      │
> │ Tracker    │ Optimizer  │ Base           │
> │ (Snowflake)│ (API)      │ (AI Search)    │
> └────────────┴────────────┴────────────────┘
> ```
>
> The dispatcher asks natural language questions. The agent decides which tool to call, executes it, and returns a clear answer."

### Step 3 — Deep Dive

> **Tool 1 — Shipment Tracker:** Connects to Snowflake via MCP server. Handles queries like 'Where is shipment PEN-1234?' and 'Show me all delayed shipments in the Midwest.' The MCP server enforces read-only access and parameterized queries.
>
> **Tool 2 — Route Optimizer:** When the agent detects a delay, it can proactively suggest alternatives: 'Shipment X is delayed due to weather on I-35. Rerouting via I-40 would add 30 miles but avoid the storm, with an estimated 2-hour improvement.'
>
> **Tool 3 — Knowledge Base:** RAG over SOPs and procedures. When a dispatcher asks 'What's the process for re-routing a hazmat shipment?', the agent retrieves the relevant SOP and answers with citations.

### Step 4 — Tool Choices

> | Component | Choice | Why | Alternative Considered |
> |-----------|--------|-----|----------------------|
> | LLM | Azure OpenAI GPT-4 | Enterprise compliance, Penske is on Azure | Claude — great but Azure OpenAI integrates better |
> | Framework | LangChain | Good balance of control and speed | LangGraph — overkill for this, no complex branching |
> | Vector DB | Azure AI Search | Native Azure, hybrid search | Pinecone — managed but additional vendor |
> | Data Access | MCP Server on Snowflake | Standardized, secure, reusable | Direct Snowflake connector — less secure |
> | Interface | Microsoft Teams bot | Where dispatchers already work | Custom web app — adoption friction |

### Step 5 — Production Considerations

> **Monitoring:** Log every query, tool call, and response. Dashboard: latency (target p95 < 3s), accuracy (weekly eval), cost per query, usage patterns.
>
> **Guardrails:** Read-only tools for safety. Any action (like re-routing) requires dispatcher confirmation. PII filtering on outputs.
>
> **Cost:** ~$1,500/month for Azure OpenAI + $500/month for AI Search = ~$2,000/month. For 200 dispatchers, that's $10/dispatcher/month — easily justified if it saves each dispatcher even 30 minutes/day.
>
> **Scaling:** Start with 20 dispatchers in one region, measure impact, expand. Add tools incrementally (start with tracking, add routing later).

---

## Practice Use Case 2: "Design a knowledge base system for Penske's operational documents"

### Step 1 — Clarify

> "What types of documents? (SOPs, safety manuals, compliance, training)
> How many documents? (Let's say 5,000+)
> Who needs access? (Dispatchers, drivers, managers — different access levels)
> How often do documents change? (Monthly for SOPs, quarterly for compliance)"

### Step 2 — Architecture

> ```
> Documents (SharePoint, Confluence, PDFs)
>       ↓
> Ingestion Pipeline (Azure Functions + Document Intelligence)
>       ↓
> Chunking & Embedding (Azure OpenAI ada-002)
>       ↓
> Azure AI Search (hybrid index: vector + keyword)
>       ↓
> RAG Pipeline (retrieve → rerank → generate with citations)
>       ↓
> Interface (Teams bot, web portal)
> ```

### Step 3 — Deep Dive

> **Ingestion:** Azure Functions watches SharePoint for new/updated documents. Azure Document Intelligence extracts text from PDFs, preserving tables and structure. Each document tagged with metadata: department, document type, access level, effective date.
>
> **Chunking strategy:** Semantic chunking at section boundaries. Each chunk carries parent context (document title + section header). For tables: keep tables as single chunks to preserve structure.
>
> **Hybrid search:** Vector search catches 'What's the procedure for overnight parking?' while keyword search catches 'Form DOT-49-CFR-395.' Combine scores with reciprocal rank fusion, then rerank top 20 with a cross-encoder to get top 5.
>
> **Access control:** Document-level permissions synced from Azure AD. A driver sees safety manuals and general SOPs. A manager sees financial procedures too. Enforced at search time — unauthorized docs never appear in results.

### Step 4 — Production

> **Freshness:** Incremental re-indexing when documents change. Stale document detection — flag if a document hasn't been reviewed in 12 months.
>
> **Evaluation:** Monthly test suite of 100 questions across departments. Track answer accuracy, source relevance, and 'I don't know' rate (should be <15% for in-scope questions).
>
> **Cost:** Azure AI Search Standard ~$250/month. Azure OpenAI for embeddings + generation ~$500/month. Total ~$750/month for an enterprise knowledge system.

---

## Practice Use Case 3: "Design an evaluation and guardrail system for Penske's AI agents"

### Step 1 — Clarify

> "How many agents are we evaluating? What are the risk levels? (Customer-facing = high risk, internal analytics = lower) What's the current evaluation process?"

### Step 2 — Architecture

> ```
> ┌──────────────────────────────────────────┐
> │        AGENT EVALUATION SYSTEM            │
> ├──────────────────────────────────────────┤
> │                                            │
> │  OFFLINE EVALS (pre-deployment)            │
> │  ─────────────                             │
> │  • Test suite: 200+ queries per agent      │
> │  • Automated scoring: relevance, accuracy  │
> │  • LLM-as-judge for open-ended quality     │
> │  • Runs in CI/CD on every change           │
> │                                            │
> │  ONLINE GUARDRAILS (runtime)               │
> │  ────────────────────                      │
> │  • Input validation (injection, toxicity)  │
> │  • Output validation (PII, grounding)      │
> │  • Action gates (human-in-the-loop)        │
> │                                            │
> │  MONITORING (continuous)                    │
> │  ──────────                                │
> │  • Quality metrics dashboard               │
> │  • Drift detection                         │
> │  • Cost tracking                           │
> │  • Alerting                                │
> │                                            │
> └──────────────────────────────────────────┘
> ```

### Step 3 — Key Point

> "The eval system is the **immune system** of your AI. Offline evals catch problems before deployment. Runtime guardrails catch problems in real-time. Monitoring catches gradual degradation. All three are necessary — no single layer is sufficient."

---

# QUESTIONS TO ASK THE HIRING MANAGER

## Smart Questions (Shows You've Done Your Homework)

1. **"I read about the Augment partnership for agentic AI on 600K loads. How is that going, and what other areas are you looking to apply agentic AI internally?"**
   *Shows: You researched the company, you understand their AI strategy*

2. **"What does the current data stack look like? Are you fully on Azure + Snowflake + Databricks, or is there migration happening?"**
   *Shows: You're thinking about practical implementation*

3. **"What would the first 90 days look like for this role? Is there a specific agent or knowledge base project I'd start on?"**
   *Shows: You're ready to contribute immediately*

4. **"How does the data science team collaborate with operations and engineering? Is there an existing MLOps pipeline?"**
   *Shows: You care about production, not just experiments*

5. **"What are the biggest pain points today that you'd want AI to solve first?"**
   *Shows: You focus on business impact, not just cool technology*

## Questions NOT to Ask

- Salary, bonuses, benefits (wait until offer stage)
- Vacation time, remote work policy (too early)
- Office space or equipment
- When you'd hear back (they'll tell you)

---

# DAY-BEFORE CHECKLIST

```
LOGISTICS
□ Quiet room, blank wall behind you
□ Good lighting on your face
□ Camera at eye level
□ Strong internet connection (wired if possible)
□ Resume printed out in front of you
□ This prep guide on second screen or printed

PREP
□ Practice "Tell me about yourself" 3 times out loud
□ Practice one system design walkthrough (10 min)
□ Review Penske research facts (Augment, 600K loads, Jeff Jackson quote)
□ Review your 3-5 best technical stories
□ Prepare 3 questions for the hiring manager
□ Read through the technical Q&A one more time

MINDSET
□ They already liked you in Round 1 — you belong here
□ There's no coding — this is a conversation
□ They want to understand your THOUGHT PROCESS
□ It's okay to say "Let me think about that for a moment"
□ It's okay to ask clarifying questions
□ Connect everything back to: "At Penske, I'd..."
```

---

# QUICK REFERENCE: KEY NUMBERS

| What | Number |
|------|--------|
| Penske loads managed with AI | ~600,000 |
| Expected productivity gain | 30-40% |
| GPT-4 context window | 128K tokens |
| Claude context window | 200K tokens |
| Good retrieval recall@5 | >85% |
| Target hallucination rate | <5% |
| Embedding dimensions (ada-002) | 1,536 |
| Typical XGBoost AUC (tabular) | 0.85-0.95 |

# QUICK REFERENCE: TOOL CHOICES FOR PENSKE

| Need | Tool | One-Liner Why |
|------|------|---------------|
| LLM | Azure OpenAI | "Enterprise SLAs, data stays in Azure VNet" |
| Agent framework | LangChain | "Production-ready, good abstractions, huge ecosystem" |
| Complex workflows | LangGraph | "State machines with checkpoints and human-in-the-loop" |
| Vector search | Azure AI Search | "Native Azure, hybrid search, enterprise security" |
| Data warehouse | Snowflake | "SQL analytics, Cortex AI, source of truth" |
| ML platform | Databricks | "Feature Store, MLflow, model serving" |
| Data pipeline | Delta Lake | "ACID transactions, schema enforcement, time travel" |
| Monitoring | LangSmith + Azure Monitor | "Trace visualization + infrastructure metrics" |

---

> **Final reminder: They're testing your THOUGHT PROCESS, not your memory. Think out loud, ask clarifying questions, discuss trade-offs, and connect everything to Penske's logistics operations. You've got this.**
