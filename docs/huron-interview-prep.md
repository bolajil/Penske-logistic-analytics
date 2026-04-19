# Huron Interview Prep: Senior Data Engineer, AI & Context Platform
## First Round - Recruiter Screen with Cassie Lundquist

---

## 🎯 ROLE SUMMARY

**Position**: Senior Data Engineer, AI & Context Platform - Healthcare Insights  
**Team**: Rev Cycle OR Clinical Team (2 Openings)  
**Type**: Remote, Full-time  
**Salary**: $140K-$190K base + bonus ($161K-$237.5K total)  
**Level**: Manager (IC, no direct reports initially)  

**What They're Building**:
- Enterprise AI data and context platform for healthcare
- RAG/retrieval systems, vector databases, semantic layers
- Agent-ready interfaces for healthcare knowledge work
- **"Trusted, reusable building blocks"** that accelerate AI product innovation

---

## 🏢 ABOUT HURON

**What Huron Does**:
- Management consulting firm focused on **healthcare transformation**
- Helps health systems, hospitals, clinics improve outcomes & reduce costs
- Focus areas: Clinical operations, Revenue Cycle, Digital transformation

**Mission Statement (from JD)**:
> *"We help healthcare organizations build innovation capabilities and accelerate key growth initiatives, enabling organizations to own the future, instead of being disrupted by it."*

**Why This Role Exists**:
- Strategic investment to embed AI across healthcare business
- Building foundational AI infrastructure (not just one-off projects)
- Goal: Turn structured AND unstructured healthcare data into "trusted, reusable building blocks"
- Create foundation for **deeper domain innovation** and **cross-domain collaboration**

**Key Insight**: This is a **greenfield AI platform build** — hands-on technical leader who builds AND leads through architecture + mentorship.

---

## 🔥 THE 5 KEY RESPONSIBILITIES (Memorize These)

### 1. Build and Own the AI Context Platform
| What They Want | Your Proof Point |
|----------------|------------------|
| Design end-to-end pipelines: ingestion → parsing/chunking → enrichment → embeddings → vector indexing → retrieval/serving | **NEXUS Platform**: Built 6-agent pipeline with ChromaDB RAG, embeddings, retrieval serving |
| Scalable patterns for incremental refresh, backfills, re-embeddings, deduplication, lineage | **Penske Analytics**: Data pipelines with incremental processing, lineage tracking |
| Improve retrieval quality (query strategies, hybrid search, metadata filtering, reranking) | **GLIH/Penske**: BM25 + Vector hybrid search (40/60 weighting), reranking implementation |

### 2. Deliver Semantic and Governed Data Products
| What They Want | Your Proof Point |
|----------------|------------------|
| Define semantic layers (metrics/entities) powering BI and agent reasoning | **Penske**: KPI definitions, service performance metrics, executive dashboards |
| Establish "context contracts" for AI inputs (schemas, metadata, freshness, citations) | **NEXUS**: Provenance chain with input/output schemas, confidence scores, citations |
| Datasets discoverable, documented, reusable | **All projects**: README documentation, API docs, Swagger specs |

### 3. Operational Excellence
| What They Want | Your Proof Point |
|----------------|------------------|
| Monitoring, alerting, SLAs/SLOs, runbooks, incident response | **Trading Platform**: 5-min cycle monitoring, error handling, auto-recovery |
| Optimize cost and latency across warehouse and vector infrastructure | **NEXUS**: Token usage tracking, latency optimization, cost modeling |

### 4. AI Safety, Governance, and Compliance
| What They Want | Your Proof Point |
|----------------|------------------|
| RBAC/ABAC patterns, PII redaction, retention, audit logging | **Rady GenAI**: HIPAA compliance, PHI guardrails, role-based access (Admin/Doctor/Patient) |
| Safe access pathways for agent tools | **NEXUS**: Tool permissions, provenance audit trail per agent |

### 5. Lead Through Influence
| What They Want | Your Proof Point |
|----------------|------------------|
| Drive technical direction with product/AI/application stakeholders | **NEXUS CEO Review**: Roadmap, architecture decisions, stakeholder docs |
| Set best practices for testing, CI/CD, evaluation | **All projects**: pytest suites, GitHub Actions, retrieval eval sets |
| Mentor via pairing, code reviews, enablement | **Agent Tool Selection Guide**: 90KB teaching document for engineers |

---

## 🧠 THE 9 BEHAVIORAL ATTRIBUTES (They Will Test These)

| Attribute | What It Means | Your Example |
|-----------|---------------|--------------|
| **Business-curious** | Learn domain (terminology, KPIs), speak credibly with SMEs | *"At Penske, I learned logistics KPIs — OTD, fleet utilization, cost-per-mile — to build meaningful analytics"* |
| **Stakeholder-first** | Clarify goals early, communicate risks, set realistic expectations | *"I create architecture docs and roadmaps BEFORE coding — alignment first"* |
| **Consultative problem-solver** | Diagnose before prescribe, propose options, durable solutions | *"I built the Agent Tool Selection Guide to help engineers choose the RIGHT tool, not just any tool"* |
| **Influence without authority** | Lead through expertise and trust, unblock teams | *"I mentor through documentation, code reviews, and enablement — no direct reports needed"* |
| **High ownership** | Reliability, documentation, operational readiness as part of work | *"Every project has README, deployment docs, monitoring dashboards — production-ready"* |
| **Clear communicator** | Go deep with engineers, explain plainly to non-technical | *"My interview prep docs and CEO reviews show I can translate technical to business"* |
| **Pragmatic builder** | Ship in iterations, validate with users, balance innovation with maintainability | *"I ship MVPs, get feedback, iterate — not 6-month waterfall projects"* |
| **Comfortable with ambiguity** | Thrive in early-stage, turn unclear goals into actionable plans | *"NEXUS was a greenfield build — I turned 'build an engineering AI' into a 6-agent architecture"* |
| **Integrity and stewardship** | Handle sensitive data responsibly, secure-by-design | *"Rady GenAI: HIPAA-compliant from day 1, PHI guardrails, audit logging"* |

---

## 🎤 YOUR 2-MINUTE INTRO (Practice This!)

```
"Hi Cassie, thanks for reaching out. I'm excited about this role because 
I've actually built exactly what Huron is looking for.

I built Rady GenAI - a HIPAA-compliant AI platform for Rady Children's Hospital. 
What makes it special is I didn't just build AI — I integrated it into 
real clinical workflows:

- A Nurse Station with clinical tools: AI-powered SBAR shift handoffs, 
  age-appropriate pain assessments, blood transfusion safety checklists
- Nurse-to-doctor note system with urgency levels and care coordination
- LangChain agent with RAG for pediatric healthcare queries
- PHI guardrails, HIPAA compliance, role-based access control
- Full observability: Jaeger tracing, Prometheus, Grafana, LangFuse

The system understands pediatric clinical context — like auto-selecting 
FLACC pain scales for infants vs. Wong-Baker FACES for older kids.

I also built NEXUS — a 6-agent LangGraph pipeline with audit-grade 
provenance, and GLIH — showing I can apply these patterns across domains.

I want a hands-on technical role with architectural influence — which 
matches this position perfectly."
```

---

## 📋 KEY REQUIREMENTS → YOUR EXPERIENCE MAPPING

### Required Qualifications (Must Have)

| Requirement | Your Evidence | Talking Point |
|-------------|---------------|---------------|
| **6-10+ years data engineering** | [Your years] across multiple roles | *"I've progressed from data engineering to architecting full AI platforms"* |
| **Expert SQL + strong Python** | FastAPI backends, pandas, numpy, all projects | *"Python is my primary language — FastAPI, LangChain, data pipelines"* |
| **Cloud data pipelines at scale** | AWS deployments, Docker, production systems | *"Rady GenAI deployed to AWS with full observability stack"* |
| **Unstructured data processing** | Document parsing, chunking, embeddings | *"I built chunking strategies for medical docs, logistics SOPs, engineering papers"* |
| **Search/retrieval concepts** | RAG systems, vector search, hybrid search | *"Implemented BM25 + vector hybrid search with tunable weights"* |
| **Strong communication + cross-functional** | Architecture docs, CEO reviews, teaching guides | *"I create documentation that bridges technical and business audiences"* |

### Preferred Qualifications (Differentiators)

| Preferred | Your Evidence | Talking Point |
|-----------|---------------|---------------|
| **Vector search hands-on** (pgvector/Pinecone/Weaviate/OpenSearch/Elastic) | ChromaDB, FAISS in production | *"I've used ChromaDB and FAISS for production RAG — understand trade-offs"* |
| **Retrieval patterns** (semantic, hybrid, reranking) | BM25+Vector hybrid, metadata filtering | *"I implemented hybrid search with 40% BM25, 60% vector weighting in GLIH"* |
| **LLM applications** (RAG, agent tools, eval/observability) | NEXUS 6-agent pipeline, Langfuse, provenance | *"Built multi-agent LangGraph systems with full Langfuse observability"* |
| **Knowledge graphs/semantic modeling** | Semantic layers in Penske, metrics definitions | *"Defined semantic layers for logistics KPIs that power both BI and AI"* |
| **Regulated environments** | HIPAA-compliant Rady GenAI, PHI guardrails | *"Built HIPAA-compliant healthcare AI — I understand the governance stakes"* |

---

## 📊 SUCCESS MEASURES → Your Proof Points

**They will measure you on these outcomes. Prepare examples!**

| Success Measure | What They Mean | Your Example |
|-----------------|----------------|--------------|
| **Higher retrieval precision/recall** | Better search results | *"I improved retrieval by adding hybrid search — precision went from ~70% to ~85%"* |
| **Better citation coverage** | AI responses cite sources | *"NEXUS provenance chain traces every output to its source document"* |
| **Fewer 'missing context' failures** | AI doesn't say "I don't know" | *"RAG grounds responses in knowledge base — reduces hallucination"* |
| **Reduced latency/cost per retrieval** | Efficient infrastructure | *"Token usage tracking in NEXUS — optimized prompt sizes"* |
| **Platform reliability (SLO attainment)** | System stays up | *"Trading platform runs 24/7 with 5-min cycles, auto-recovery on failures"* |
| **Broad adoption of semantic definitions** | Teams use your standards | *"Penske KPIs used across dashboards, reports, and AI insights"* |
| **Accelerated delivery via standards** | Others ship faster | *"Agent Tool Selection Guide enables engineers to pick right tools quickly"* |

---

## ❓ LIKELY RECRUITER QUESTIONS

### 1. "Tell me about yourself"
→ Use your 2-minute intro above

### 2. "Why are you interested in this role?"
```
"Three reasons:

1. **The technical challenge**: Building an AI context platform from the ground 
   up - embeddings, retrieval, semantic layers - is exactly what I love doing. 
   I've built similar systems and want to do it at enterprise scale.

2. **Healthcare impact**: Healthcare has massive amounts of unstructured data 
   that's underutilized. The opportunity to make clinicians more efficient 
   and improve patient outcomes through AI is meaningful work.

3. **The role structure**: Hands-on technical work plus architectural 
   leadership without people management overhead. That's my sweet spot."
```

### 3. "Why Huron specifically?"
```
"Huron has deep healthcare domain expertise - you're not just a tech company 
bolting AI onto healthcare. You understand revenue cycle, clinical operations, 
the regulatory landscape. 

Building AI platforms in healthcare requires that domain context embedded in 
the architecture - you can't just throw GPT at HIPAA-protected data. Huron 
gets that, and that's why this platform will succeed where others fail."
```

### 4. "Walk me through your experience with [X technology]"

**Vector Search/Embeddings**:
```
"In my GLIH project, I built a RAG system using:
- OpenAI embeddings for document vectorization
- ChromaDB for vector storage and similarity search
- Hybrid retrieval combining semantic search with metadata filtering
- Custom chunking strategies for logistics documents

I also implemented reranking to improve retrieval precision and built 
evaluation pipelines to measure recall/precision on test queries."
```

**Data Pipelines**:
```
"I've built end-to-end pipelines that handle:
- Ingestion from APIs, databases, file uploads
- Parsing/transformation (PDFs, structured data)
- Incremental processing with change detection
- Data quality validation and lineage tracking
- Serving through APIs and analytics layers"
```

### 5. "What's your experience with healthcare data?"
**YOU BUILT A PRODUCTION HEALTHCARE AI SYSTEM - This is your strongest answer!**
```
"I built Rady GenAI - a HIPAA-compliant AI agent for Rady Children's Hospital.
It's a full production system, not a prototype:

Technical Stack:
- LangChain agent with GPT-4 for medical reasoning
- FAISS vector database with OpenAI embeddings for RAG
- FastAPI backend, Next.js frontend
- Published on DockerHub, deployed to AWS

Healthcare-Specific Features:
- PHI guardrails that detect and handle protected health information
- HIPAA compliance dashboard with audit logging
- Role-based access: Admin, Doctor, Patient - different data visibility
- EHR lookups, medication database, appointment scheduling
- All PHI access tracked with timestamps and severity classification

Observability (critical for healthcare):
- Jaeger for distributed tracing
- Prometheus + Grafana for metrics
- LangFuse for LLM-specific monitoring - tokens, costs, prompts

I understand healthcare AI deeply: HIPAA requirements, PHI sensitivity,
audit trails, clinician workflow integration, and the importance of
explainability in medical AI systems."
```

### 6. "Describe a challenging project" — STAR Stories

**STAR Story 1: Building the AI Context Platform (NEXUS)**
```
SITUATION: "I needed to build an AI platform that could autonomously 
process engineering briefs and produce full technical reports with 
CAD geometry — from scratch, no existing codebase."

TASK: "Turn an ambiguous goal ('build an engineering AI') into a 
production system with multiple specialized agents, each handling 
different parts of the workflow."

ACTION: "I designed a 6-agent LangGraph architecture:
- RequirementsAgent parses natural language into structured specs
- ResearchAgent queries ChromaDB for relevant engineering knowledge
- DesignAgent applies physics equations (not black-box LLM)
- SimulationAgent runs NumPy/SciPy solvers
- OptimizationAgent does multi-objective Pareto sweeps
- ReportAgent compiles everything with full provenance

I built a provenance chain that traces every calculation to its source,
implemented SSE streaming for real-time updates, and added Langfuse
for LLM observability."

RESULT: "Shipped a production system that takes English briefs and 
produces engineering reports + CAD files in minutes instead of days. 
The provenance chain became the key differentiator — audit-grade 
traceability that enterprises require."
```

**STAR Story 2: Healthcare AI with Clinical Workflow Integration (Rady GenAI)**
```
SITUATION: "Healthcare organizations need AI that integrates into 
clinical workflows, not just chatbots. Nurses need tools that fit 
how they actually work — shift handoffs, pain assessments, care coordination."

TASK: "Build a production AI platform for Rady Children's Hospital that 
handles PHI safely AND integrates into real clinical workflows."

ACTION: "I built beyond just compliance — I built clinical utility:
- Nurse Station with AI-powered SBAR shift handoff generation
- Age-appropriate pain assessment: FLACC for infants, Wong-Baker for kids
- Blood transfusion safety checklists with monitoring schedules
- Nurse-to-doctor notes with urgency levels (routine/urgent/critical)
- Doctor's orders visible to nurses with priority coding
- Patient context linking all tool outputs to specific patients
- PHI guardrails, RBAC, full audit logging, observability stack"

RESULT: "Delivered a system where AI augments clinical judgment — nurses 
get SBAR reports generated, pain assessments with recommendations, safety 
checklists for procedures. This is exactly the 'agent-ready interfaces 
for healthcare knowledge work' that Huron is building."
```

**STAR Story 3: Hybrid Search Optimization (Penske/GLIH)**
```
SITUATION: "Our RAG system was returning irrelevant results — users 
were complaining that the AI 'didn't understand their questions.'"

TASK: "Improve retrieval precision without retraining embeddings or 
increasing infrastructure costs."

ACTION: "I diagnosed the problem: pure semantic search missed keyword 
matches that users expected. I implemented hybrid search:
- BM25 for keyword matching (40% weight)
- Vector similarity for semantic matching (60% weight)
- Metadata filtering to narrow results by domain
- Tested with retrieval eval sets to measure precision/recall"

RESULT: "Retrieval precision improved from ~70% to ~85%. Users reported 
the AI 'finally understands what I'm asking.' This pattern is now 
standard across all my RAG implementations."
```

### 7. "What are your salary expectations?"
```
"The posted range of $140K-$190K base aligns with my expectations. 
I'm flexible within that range depending on the total compensation 
package and growth opportunities. What does the typical structure 
look like for this role?"
```

### 8. "What questions do you have for me?"
(See section below)

---

## 🔑 TECHNICAL CONCEPTS TO KNOW (Deep Dive)

### RAG (Retrieval-Augmented Generation)
- **What**: Combining LLMs with external knowledge retrieval
- **Why**: Reduces hallucinations, grounds responses in facts
- **Components**: Embeddings → Vector DB → Retrieval → LLM → Response
- **Your implementation**: NEXUS ResearchAgent queries ChromaDB, returns grounded findings

### Vector Databases — Know the Trade-offs
| Database | Best For | Limitations | Your Experience |
|----------|----------|-------------|-----------------|
| **ChromaDB** | Prototyping, Python-native | Not for massive scale | ✅ NEXUS, Penske |
| **FAISS** | In-memory speed, local | No persistence OOTB | ✅ Rady GenAI |
| **Pinecone** | Managed, enterprise scale | Cost at scale | Know it, haven't used |
| **pgvector** | Postgres ecosystem | Slower than dedicated | Know it |
| **Weaviate** | Hybrid search built-in | Operational overhead | Know it |

**Key concepts to mention**: HNSW index, ANN (Approximate Nearest Neighbor), cosine similarity, embedding dimensions (1536 for OpenAI)

### Hybrid Search — Your Specialty
```
PURE SEMANTIC: "What's the hospital's cancellation policy?"
  → Matches: "appointment rescheduling guidelines" (semantically similar)
  → Misses: Document titled "Cancellation Policy" (exact match)

PURE BM25: Exact keyword match
  → Matches: "Cancellation Policy" document
  → Misses: Semantically related content

HYBRID (Your approach):
  BM25 Score × 0.4 + Vector Score × 0.6 = Final Score
  → Gets BOTH exact matches AND semantic matches
```

### Semantic Layers — Critical for Huron
- **What**: Abstraction layer defining business metrics/entities consistently
- **Tools**: dbt metrics, Cube.js, LookML, custom implementations
- **Why important for Huron**: 
  - Same KPI definition for BI dashboards AND AI agents
  - "Revenue per patient" means the SAME thing everywhere
  - Prevents AI from hallucinating different metric definitions
- **Your experience**: Penske KPIs (OTD, fleet utilization) defined once, used across dashboards and AI insights

### Context Contracts (Their Term — Learn This!)
- **What**: Defined schemas, metadata requirements, freshness SLAs for AI inputs
- **Like**: Data contracts but specifically for AI context/retrieval
- **Components**:
  - **Schema**: What fields must exist (title, domain, timestamp, source)
  - **Metadata requirements**: Must have author, version, classification
  - **Freshness**: "This document must be refreshed within 24 hours"
  - **Citation expectations**: "AI must cite source document ID"
- **Your experience**: NEXUS provenance chain = context contract in action

### Healthcare-Specific Terms (Memorize These!)
| Term | What It Means | Why It Matters |
|------|---------------|----------------|
| **HIPAA** | Health Insurance Portability & Accountability Act | Federal law protecting patient data |
| **PHI** | Protected Health Information | Names, DOB, SSN, medical records — MUST be protected |
| **PII** | Personally Identifiable Information | Broader than PHI — any identifying info |
| **Revenue Cycle** | Billing workflow: Patient visit → Coding → Claims → Payment | One of Huron's focus areas |
| **Clinical Data** | EHR notes, lab results, imaging, diagnoses | The unstructured data they want to unlock |
| **EHR/EMR** | Electronic Health/Medical Records | Epic, Cerner, Meditech systems |
| **ICD-10** | Diagnosis codes | Structured data from clinical encounters |
| **CPT** | Procedure codes | What treatments/services were provided |
| **Claims Denial** | Insurance rejects payment | Revenue cycle pain point |

### The Pipeline They're Building (Visualize This!)
```
┌─────────────────────────────────────────────────────────────────────┐
│                    HURON AI CONTEXT PLATFORM                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  INGESTION          PROCESSING         INDEXING         SERVING     │
│  ──────────         ──────────         ────────         ───────     │
│                                                                      │
│  ┌──────────┐      ┌──────────┐      ┌──────────┐    ┌──────────┐  │
│  │ Clinical │      │ Parsing  │      │ Vector   │    │ RAG      │  │
│  │ Notes    │ ──▶  │ Chunking │ ──▶  │ Index    │ ──▶│ Retrieval│  │
│  │ EHR Data │      │ Enriching│      │ (embed)  │    │          │  │
│  │ Claims   │      │          │      │          │    │          │  │
│  │ Policies │      │          │      │          │    │          │  │
│  └──────────┘      └──────────┘      └──────────┘    └──────────┘  │
│       │                 │                 │               │         │
│       ▼                 ▼                 ▼               ▼         │
│  ┌──────────┐      ┌──────────┐      ┌──────────┐    ┌──────────┐  │
│  │ Lineage  │      │ Semantic │      │ Metadata │    │ Agent    │  │
│  │ Tracking │      │ Layer    │      │ Filtering│    │ Tools    │  │
│  │          │      │ (metrics)│      │          │    │          │  │
│  └──────────┘      └──────────┘      └──────────┘    └──────────┘  │
│                                                                      │
│  GOVERNANCE: RBAC │ PII Redaction │ Audit Logging │ Retention       │
└─────────────────────────────────────────────────────────────────────┘
```

**This is what YOU would own.** Be ready to discuss any part of this pipeline.

---

## ❓ QUESTIONS TO ASK CASSIE (Strategic Questions)

### About the Platform (Shows Technical Depth)
1. "The JD mentions 'trusted, reusable building blocks' — what types of unstructured data are you primarily working with? Clinical notes? Claims documents? Policies?"

2. "You mention semantic layers powering both BI and agent reasoning. Is there an existing BI stack I'd integrate with, or is this greenfield?"

3. "What's the current state of the AI context platform? Am I building from scratch or inheriting existing infrastructure?"

### About the Team & Leadership
4. "The role is 'lead through influence without direct reports' — who would I be influencing? Product managers? AI engineers? Consultants?"

5. "How established is the AI team? Would I be one of the first platform engineers or joining an existing group?"

6. "Who would I report to, and what's their background?"

### About Success & Impact
7. "What would success look like in the first 90 days? First year?"

8. "The JD mentions 'measurable improvement in AI outcomes' — how do you currently measure retrieval quality and citation coverage?"

### About Huron & Healthcare
9. "How does this platform team interact with Huron's consulting engagements? Do we build internal tools, client-facing products, or both?"

10. "Which EHR systems does Huron typically work with — Epic, Cerner, Meditech?"

### About Process
11. "What does the interview process look like after this call?"

12. "Is there anything about my background I can clarify to help move forward?"

---

## ✅ PRE-INTERVIEW CHECKLIST

- [ ] Test audio/microphone (Teams audio-only call)
- [ ] Quiet environment, no distractions
- [ ] Have this document open for reference
- [ ] Water nearby
- [ ] Resume open in case they reference it
- [ ] Notepad for taking notes
- [ ] LinkedIn profile of Cassie reviewed
- [ ] Huron website reviewed (huron.com)
- [ ] Practice 2-minute intro OUT LOUD 3x
- [ ] Review the 5 Key Responsibilities
- [ ] Memorize the 9 Behavioral Attributes
- [ ] Know healthcare terms (HIPAA, PHI, Revenue Cycle, EHR)
- [ ] Have 3 STAR stories ready

---

## 🚨 RECRUITER SCREEN TIPS

1. **Be concise** - Recruiters screen many candidates; respect their time
2. **Show enthusiasm** - They're gauging culture fit and interest level
3. **Use their language** - "Context contracts", "semantic layers", "agent-ready interfaces"
4. **Healthcare curiosity** - Mention you understand the HIPAA stakes
5. **Don't oversell** - Be honest; your experience speaks for itself
6. **Remote work** - Mention you're effective working remotely if asked
7. **Ask strategic questions** - Shows you've read the JD carefully

---

## 🎯 YOUR KILLER DIFFERENTIATORS

**When they ask "Why should we hire you?" — Hit these points:**

1. **Healthcare AI Experience**: "I built Rady GenAI — a HIPAA-compliant AI agent with PHI guardrails, audit logging, and role-based access. I understand the compliance stakes."

2. **Full RAG Pipeline Expertise**: "I've built end-to-end: ingestion → chunking → embeddings → vector indexing → hybrid retrieval → agent tools. That's exactly what you need."

3. **Provenance/Governance**: "My NEXUS platform has audit-grade provenance — every AI output traces to its source. That's the 'trusted building blocks' you mentioned."

4. **Semantic Layers**: "I've defined KPI semantic layers that power both dashboards AND AI agents — same definition everywhere."

5. **Lead Without Authority**: "I mentor through documentation and enablement, not titles. My 90KB Agent Tool Selection Guide is an example."

---

## 📊 YOUR PROJECT PORTFOLIO (Quick Reference)

| Project | Relevance to Huron | Key Talking Point |
|---------|-------------------|-------------------|
| **Rady GenAI** | Healthcare AI, HIPAA compliance | "Production HIPAA-compliant AI with PHI guardrails" |
| **NEXUS** | Multi-agent pipeline, provenance | "6-agent LangGraph with audit-grade traceability" |
| **Penske Analytics** | RAG, semantic layers, KPIs | "Hybrid search, semantic metrics for BI + AI" |
| **GLIH** | Logistics RAG, domain expertise | "Applied same patterns to different domain" |
| **Trading Platform** | Operational excellence, monitoring | "24/7 reliability, error handling, auto-recovery" |

---

## 🏥 RADY GENAI DEEP DIVE — YOUR HEALTHCARE AI DIFFERENTIATOR

**This is your STRONGEST talking point for Huron. You built EXACTLY what they want.**

### Architecture Overview
```
┌──────────────────────────────────────────────────────────────────┐
│                    RADY CHILDREN'S GENAI PLATFORM                 │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  FRONTEND (Next.js)           BACKEND (FastAPI)                  │
│  ─────────────────            ─────────────────                  │
│  ┌─────────────┐              ┌─────────────────┐                │
│  │ Patient EHR │              │ LangChain Agent │                │
│  │ Dashboard   │◀────────────▶│ (GPT-4o-mini)   │                │
│  └─────────────┘              └────────┬────────┘                │
│  ┌─────────────┐                       │                         │
│  │ Nurse       │              ┌────────▼────────┐                │
│  │ Station     │              │   AGENT TOOLS   │                │
│  └─────────────┘              ├─────────────────┤                │
│  ┌─────────────┐              │ • PatientInfo   │                │
│  │ Clinical    │              │ • MedicationDB  │                │
│  │ Tools       │              │ • RAG Search    │                │
│  └─────────────┘              └─────────────────┘                │
│                                                                   │
│  COMPLIANCE LAYER                                                │
│  ─────────────────                                               │
│  PHI Guardrails │ Audit Logging │ RBAC │ HIPAA Dashboard         │
└──────────────────────────────────────────────────────────────────┘
```

### Clinical Workflow Integration (Key Differentiator!)
**"I didn't just build AI — I integrated it into real clinical workflows."**

| Clinical Tool | What It Does | Why Huron Cares |
|---------------|--------------|-----------------|
| **Nurse Station** | Dashboard for nurse workflows — patient assignments, doctor notes, clinical tools | Shows you understand clinician UX |
| **Shift Handoff (SBAR)** | AI generates structured SBAR nursing handoff reports | Clinical documentation automation |
| **Pain Assessment** | Age-appropriate scales: FLACC (infants), Wong-Baker FACES (kids), Numeric (older) | Domain-specific clinical logic |
| **Blood Transfusion Safety** | Pre-transfusion checklist with verification steps, reaction monitoring | Patient safety + compliance |
| **Nurse-to-Doctor Notes** | Structured communication with urgency levels, categories | Care coordination workflow |
| **Doctor's Orders Display** | Priority-coded orders with monitoring instructions | Clinician decision support |

### Specific Talking Points for the Interview

**When they ask about clinical workflow integration:**
```
"I built a Nurse Station that integrates AI into real clinical workflows:

1. SHIFT HANDOFF: Nurses input patient status, events, concerns — 
   AI generates structured SBAR reports for handoff continuity.

2. PAIN ASSESSMENT: Age-appropriate scales automatically selected — 
   FLACC for infants, Wong-Baker FACES for children, Numeric for older kids.
   Provides clinical recommendations based on score.

3. BLOOD TRANSFUSION: Pre-transfusion safety checklists with 
   verification steps, vital sign monitoring schedules, reaction warnings.

4. NURSE-TO-DOCTOR NOTES: Structured communication with urgency levels 
   (routine/urgent/critical) and categories (vitals concern, medication issue, 
   behavior change) — visible in the patient EHR for care coordination.

This isn't just AI — it's AI integrated into how clinicians actually work."
```

**When they ask about unstructured data → structured output:**
```
"In the Nurse Station, I take unstructured clinical observations — 
'patient seems more agitated, refusing meds' — and structure them into:

- Category: 'behavior_change' or 'medication_issue'
- Urgency: 'routine', 'urgent', 'critical'  
- Status: 'pending', 'acknowledged', 'resolved'

This creates structured data for analytics and AI reasoning while 
preserving the clinical context. That's the 'semantic layer' Huron 
is building — turning unstructured clinical data into AI-ready context."
```

**When they ask about healthcare-specific AI challenges:**
```
"Three challenges I solved in Rady GenAI:

1. AGE-APPROPRIATE LOGIC: Pain scales differ by age — I built logic 
   that auto-selects FLACC for 0-3yo, Wong-Baker for 4-7yo, Numeric 
   for 8+. Same AI, different clinical pathways.

2. PATIENT CONTEXT: Every clinical tool requires patient context — 
   I built a patient selector that links all tool outputs to specific 
   patients with MRN, room, diagnosis visible.

3. CARE CONTINUITY: Doctor's orders and nurse notes need to flow 
   between roles — I built bidirectional note systems so doctors 
   see nurse concerns and nurses see care plans."
```

### Healthcare Terms You Can Now Use Credibly

| Term | Your Experience | How to Use It |
|------|-----------------|---------------|
| **SBAR** | Built AI-powered SBAR handoff generator | "I automated SBAR nursing handoffs" |
| **FLACC** | Implemented in pain assessment tool | "Age-appropriate pain scales for pediatrics" |
| **Wong-Baker FACES** | Implemented for 4-7yo patients | "Visual pain scale for children" |
| **Care Coordination** | Nurse-to-doctor notes system | "Structured communication between care team" |
| **Clinical Decision Support** | Pain recommendations, transfusion checklists | "AI augments clinical judgment, doesn't replace it" |
| **Pre-transfusion Verification** | Blood check safety checklist | "Patient safety protocols embedded in workflow" |

### Code You Can Reference (GitHub)
```
Repository: github.com/bolajil/Rady-Children-Hospital

Key Files:
- app/nurse/page.tsx — Nurse Station with clinical tools
- app/ehr/[id]/page.tsx — Patient EHR with doctor/nurse notes
- backend/app/agent.py — LangChain agent with medical tools
- backend/app/phi_guardrail.py — HIPAA-compliant PHI handling
```

---

## 📝 AFTER THE CALL

- Send thank-you email to Cassie within 24 hours
- Note any questions they asked you struggled with
- Research any topics that came up you weren't sure about
- Prepare deeper technical answers for next round
- Update this doc with new insights

---

## 🔥 FINAL CONFIDENCE BOOST

**You are not hoping to get this job. You are evaluating if HURON deserves YOU.**

✅ You've built HIPAA-compliant healthcare AI (Rady GenAI)  
✅ You've built multi-agent LangGraph pipelines (NEXUS)  
✅ You've implemented hybrid search and semantic layers (Penske)  
✅ You've shipped production systems with full observability  
✅ You lead through documentation and enablement  

**The JD describes what you've ALREADY DONE.**

Go get it. 🚀
