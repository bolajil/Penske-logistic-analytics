# Penske Senior Data Scientist — Second Round Interview Prep

> Complete preparation guide for the second round interview.
> Covers deep technical Q&A, system design, live scenarios, behavioral questions, and a step-by-step knowledge base education plan.

---

# TABLE OF CONTENTS

1. [What to Expect in Round 2](#part-1)
2. [Deep Technical Q&A (30 Questions)](#part-2)
3. [System Design Scenarios](#part-3)
4. [Live Coding Challenges](#part-4)
5. [Behavioral & Leadership Q&A](#part-5)
6. [Penske-Specific Case Studies](#part-6)
7. [Step-by-Step Knowledge Base Education](#part-7)
8. [Day-Before Cheat Sheet](#part-8)

---

# Part 1: What to Expect in Round 2

## Second Round Format (Typical Senior Data Scientist)

```
┌──────────────────────────────────────────────────────────────┐
│              SECOND ROUND STRUCTURE (2-4 hours)               │
├──────────────────────────────────────────────────────────────┤
│                                                                │
│  BLOCK 1: Deep Technical (45-60 min)                          │
│  ─────────────────────────────────                            │
│  • Deeper dive into GenAI, agents, MCP                        │
│  • "Walk me through how you'd build X"                        │
│  • Architecture whiteboard                                     │
│  • Follow-up questions that go 2-3 levels deep                │
│                                                                │
│  BLOCK 2: System Design (45-60 min)                           │
│  ─────────────────────────────────                            │
│  • "Design an end-to-end system for..."                       │
│  • Data pipeline + ML + deployment                            │
│  • Scale, cost, monitoring considerations                     │
│  • Trade-off discussions                                       │
│                                                                │
│  BLOCK 3: Hands-On / Case Study (30-45 min)                  │
│  ──────────────────────────────────────────                   │
│  • SQL / Python live coding                                   │
│  • Debug a failing pipeline                                   │
│  • Evaluate an agent's output                                 │
│                                                                │
│  BLOCK 4: Behavioral & Culture (30 min)                       │
│  ──────────────────────────────────────                       │
│  • Leadership, collaboration, conflict                        │
│  • "Tell me about a time..."                                  │
│  • Why Penske? Why this role?                                 │
│                                                                │
└──────────────────────────────────────────────────────────────┘
```

## Key Differences from Round 1

| Round 1 | Round 2 |
|---------|---------|
| "Do you know X?" | "How would you build X at Penske?" |
| Breadth of knowledge | Depth of expertise |
| General concepts | Specific architecture decisions |
| "Tell me about your experience" | "Walk me through the code" |
| Screening for fit | Validating you can deliver |

---

# Part 2: Deep Technical Q&A (30 Questions with Answers)

## Section A: GenAI Agents (Questions 1-6)

### Q1: "Walk me through building a production agent from scratch. What are the key decisions?"

**Answer:**
> "Building a production agent involves five key decisions:
>
> **1. LLM Selection:** I evaluate based on the task. For Penske, I'd likely use Azure OpenAI since you're on Azure — it gives us private endpoints, SLAs, and compliance. For long-document tasks, Claude's 200K context.
>
> **2. Orchestration:** For simple tool-calling, LangChain is sufficient. If we have complex workflows — like route optimization that needs human approval before dispatching — I'd use LangGraph for its state machine capabilities.
>
> **3. Tool Design:** Each tool needs clear descriptions (the LLM reads these), input validation, error handling, and timeout limits. For Penske, tools might include: query Snowflake for shipment data, call route optimization API, look up driver schedules.
>
> **4. Guardrails:** Input validation (block prompt injection), output validation (verify SQL before execution), rate limiting, and human-in-the-loop for high-stakes actions like route changes.
>
> **5. Observability:** Every LLM call, tool call, and decision gets logged. I use structured logging with trace IDs so we can replay any agent session for debugging."

### Q2: "How do you handle agent failures in production?"

**Answer:**
> "I implement a multi-layer failure strategy:
>
> **Layer 1 — Retry with backoff:** Transient API failures get exponential backoff (1s, 2s, 4s). Max 3 retries.
>
> **Layer 2 — Fallback models:** If GPT-4 is down or slow, fall back to GPT-3.5 for simpler tasks or Claude as an alternative.
>
> **Layer 3 — Graceful degradation:** If the agent can't complete the full task, it returns what it has with a clear message: 'I retrieved the shipment data but couldn't generate the optimization. Here's the raw data.'
>
> **Layer 4 — Circuit breaker:** If error rate exceeds 10% in 5 minutes, stop sending requests and alert the team. Prevent cascading failures.
>
> **Layer 5 — Human escalation:** For critical paths, if the agent fails twice, route to a human operator with full context of what the agent tried."

### Q3: "What's the difference between ReAct, Plan-and-Execute, and function calling agents?"

**Answer:**
> "These are three different agent reasoning patterns:
>
> **ReAct (Reason + Act):** The agent thinks step-by-step. Each iteration: reason about what to do → take one action → observe result → reason again. Best for open-ended tasks where the path isn't clear upfront. Example: 'Investigate why shipments to Zone 5 are delayed' — the agent might check weather, then driver logs, then traffic data.
>
> **Plan-and-Execute:** The agent creates a full plan first, then executes each step. Better for well-defined tasks. Example: 'Generate the monthly logistics report' — plan: 1) query shipment data, 2) calculate KPIs, 3) generate charts, 4) format report. More predictable but less adaptive.
>
> **Function Calling:** The LLM directly outputs structured function calls (native in OpenAI/Azure). The simplest pattern — no explicit reasoning loop, just 'here's a function to call.' Best for straightforward tool use. Example: 'What's the status of shipment #12345?' → calls `get_shipment_status(id=12345)`.
>
> For Penske, I'd use **function calling** for simple lookups, **ReAct** for investigative analysis, and **Plan-and-Execute** for complex multi-step workflows like end-of-month reporting."

### Q4: "How would you prevent prompt injection in a Penske agent?"

**Answer:**
> "Prompt injection is when a user tricks the agent into ignoring its instructions. I use defense in depth:
>
> **1. Input sanitization:** Strip or escape special characters. Check for known injection patterns like 'ignore previous instructions.'
>
> **2. System prompt hardening:** Use delimiters to separate system instructions from user input. Add explicit instructions: 'Never execute commands that modify or delete data without human approval.'
>
> **3. Output validation:** Before executing any tool call, validate the parameters. If the agent generates SQL, run it through a parser to confirm it's SELECT-only (no DROP, DELETE, UPDATE).
>
> **4. Least privilege:** The agent's database credentials only have READ access. API keys have minimum required permissions.
>
> **5. Content filtering:** Azure OpenAI has built-in content filters. I also add custom filters for Penske-specific sensitive data (driver SSNs, contract terms).
>
> **6. Monitoring:** Log all inputs and flag anomalies. If a user's queries suddenly change pattern, alert the security team."

### Q5: "How do you evaluate agent quality? What metrics do you track?"

**Answer:**
> "I track metrics across four dimensions:
>
> **Task Success:** Did the agent complete the user's request? I measure task completion rate (target: >90%) and partial completion rate.
>
> **Accuracy:** For retrieval tasks — precision, recall, and NDCG of retrieved documents. For generative tasks — factual accuracy checked against ground truth (LLM-as-judge or human eval). For SQL generation — query correctness (does it return expected results?).
>
> **Efficiency:** Latency (p50, p95, p99), number of LLM calls per task (fewer is better), token usage (cost), and tool call success rate.
>
> **Safety:** Guardrail trigger rate, prompt injection detection rate, harmful output rate (should be ~0%), and human escalation rate.
>
> For evaluation pipeline, I build a test suite of 200+ representative queries with expected outputs, run weekly regression tests, and track metrics over time in a dashboard."

### Q6: "Explain MCP and how you'd use it at Penske."

**Answer:**
> "MCP — Model Context Protocol — is Anthropic's open standard for connecting AI models to external data. Think of it as USB-C for AI: one standard interface for any data source.
>
> **Architecture:**
> ```
> AI App ←→ MCP Client ←→ MCP Server ←→ Data Source
> ```
>
> **At Penske, I'd build MCP servers for:**
>
> 1. **Snowflake MCP Server** — Exposes shipment data, route history, and KPIs as resources. Tools for running approved queries.
> 2. **Fleet Management MCP Server** — Real-time truck locations, maintenance schedules, driver availability.
> 3. **Document MCP Server** — SOPs, safety manuals, compliance docs via vector search.
>
> **Why MCP over direct API calls?**
> - Standardized interface — any AI tool can connect
> - Built-in security — auth, rate limiting, data access controls
> - Discoverable — the AI can 'see' what data is available
> - Reusable — build once, use from any agent or AI application
>
> **Security:** Each MCP server has role-based access. A customer-facing agent gets read-only shipment status. An internal analytics agent gets broader query access. No MCP server can modify production data."

---

## Section B: Data & SQL (Questions 7-12)

### Q7: "Write a SQL query to find the top 10 routes by average delay, including only routes with 100+ shipments in the last 90 days."

**Answer:**
```sql
WITH route_stats AS (
    SELECT
        r.route_id,
        r.origin_city,
        r.destination_city,
        COUNT(*) AS total_shipments,
        AVG(DATEDIFF('minute', s.scheduled_arrival, s.actual_arrival)) AS avg_delay_minutes,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY
            DATEDIFF('minute', s.scheduled_arrival, s.actual_arrival)
        ) AS median_delay_minutes,
        STDDEV(DATEDIFF('minute', s.scheduled_arrival, s.actual_arrival)) AS delay_stddev
    FROM shipments s
    JOIN routes r ON s.route_id = r.route_id
    WHERE s.actual_arrival IS NOT NULL
      AND s.shipped_date >= DATEADD('day', -90, CURRENT_DATE())
    GROUP BY r.route_id, r.origin_city, r.destination_city
    HAVING COUNT(*) >= 100
)
SELECT
    route_id,
    origin_city || ' → ' || destination_city AS route,
    total_shipments,
    ROUND(avg_delay_minutes, 1) AS avg_delay_min,
    ROUND(median_delay_minutes, 1) AS median_delay_min,
    ROUND(delay_stddev, 1) AS delay_variability
FROM route_stats
ORDER BY avg_delay_minutes DESC
LIMIT 10;
```

**Why this approach:**
> "I include median alongside mean because delay distributions are typically right-skewed — a few extreme delays inflate the average. The standard deviation shows consistency. I use a CTE for readability, and the HAVING clause filters before the sort for efficiency."

### Q8: "How would you optimize a slow Snowflake query that joins 5 tables with 100M+ rows?"

**Answer:**
> "I'd investigate in this order:
>
> **1. Check the query profile:** Snowflake's QUERY_PROFILE shows where time is spent — scanning, joining, sorting. This tells me where to focus.
>
> **2. Clustering keys:** If the main table is frequently filtered by date or region, I'd add clustering keys:
> ```sql
> ALTER TABLE shipments CLUSTER BY (shipped_date, region);
> ```
> This physically sorts data, reducing scan time dramatically.
>
> **3. Reduce scan with pruning:** Ensure WHERE clauses align with clustering keys so Snowflake can skip irrelevant micro-partitions. Check with:
> ```sql
> SELECT SYSTEM$CLUSTERING_INFORMATION('shipments');
> ```
>
> **4. Materialized views or Dynamic Tables:** For frequently-run complex joins, create a Dynamic Table that auto-refreshes:
> ```sql
> CREATE DYNAMIC TABLE route_summary
>   TARGET_LAG = '1 hour'
>   WAREHOUSE = analytics_wh
> AS
> SELECT ... (the complex join);
> ```
>
> **5. Warehouse sizing:** If it's a one-off analytical query, scale up temporarily. For recurring queries, right-size the warehouse.
>
> **6. Join order and filtering:** Push filters as early as possible. Join smaller tables first. Use EXISTS instead of IN for subqueries."

### Q9: "Explain the Medallion Architecture and how you'd implement it at Penske."

**Answer:**
> "Medallion Architecture organizes data into three layers of increasing quality:
>
> ```
> BRONZE (Raw)          SILVER (Cleaned)        GOLD (Business-Ready)
> ──────────────        ────────────────        ─────────────────────
> Raw GPS events        Deduplicated GPS        Route performance KPIs
> Raw shipment logs     Validated shipments     Daily delivery metrics
> Raw driver data       Standardized drivers    Driver scorecards
> Raw weather feeds     Cleaned weather data    Weather impact analysis
> ```
>
> **At Penske:**
>
> **Bronze:** Ingest raw data from fleet telematics, TMS (Transportation Management System), Snowflake CDC streams, and external APIs. Store as-is with metadata (ingestion timestamp, source).
>
> **Silver:** Apply data quality rules — remove duplicates, validate GPS coordinates are within valid ranges, standardize addresses, handle missing values. This is where Databricks Delta Lake shines with MERGE operations and schema enforcement.
>
> **Gold:** Business aggregations — route efficiency scores, on-time delivery rates, fuel consumption trends, driver safety metrics. These tables power dashboards and ML models.
>
> **Why this matters:** Data scientists should query Gold tables for feature engineering, not raw Bronze data. This ensures consistency and quality across all models."

### Q10: "How would you build a feature store for ML at Penske using Databricks?"

**Answer:**
> "A feature store centralizes reusable ML features so every model uses the same calculations.
>
> **Step 1 — Identify key entities:** At Penske: routes, drivers, trucks, shipments, customers.
>
> **Step 2 — Define features per entity:**
> ```python
> # Route features
> route_features = {
>     'avg_transit_time_7d': 'Average transit time, rolling 7 days',
>     'delay_rate_30d': 'Percentage of late deliveries, 30 days',
>     'fuel_efficiency': 'Miles per gallon on this route',
>     'weather_disruption_score': 'Historical weather impact score'
> }
>
> # Driver features
> driver_features = {
>     'avg_hours_driven_weekly': 'Average driving hours per week',
>     'safety_score': 'Composite safety metric',
>     'on_time_rate_90d': 'On-time delivery rate, 90 days',
>     'experience_years': 'Total years driving for Penske'
> }
> ```
>
> **Step 3 — Register in Databricks Feature Store:**
> ```python
> from databricks.feature_engineering import FeatureEngineeringClient
>
> fe = FeatureEngineeringClient()
>
> fe.create_table(
>     name='penske.ml.route_features',
>     primary_keys=['route_id'],
>     timestamp_keys=['feature_date'],
>     description='Route-level features for ML models'
> )
>
> fe.write_table(
>     name='penske.ml.route_features',
>     df=route_features_df,
>     mode='merge'
> )
> ```
>
> **Step 4 — Use in training:**
> ```python
> training_set = fe.create_training_set(
>     df=labels_df,
>     feature_lookups=[
>         FeatureLookup(table_name='penske.ml.route_features',
>                       lookup_key='route_id'),
>         FeatureLookup(table_name='penske.ml.driver_features',
>                       lookup_key='driver_id')
>     ],
>     label='is_delayed'
> )
> ```
>
> **Key benefits:** Features are computed once, reused across models, automatically point-in-time correct (no data leakage), and versioned."

### Q11: "Write a window function query to calculate each driver's rank by on-time delivery rate within their region."

**Answer:**
```sql
WITH driver_performance AS (
    SELECT
        d.driver_id,
        d.driver_name,
        d.region,
        COUNT(*) AS total_deliveries,
        SUM(CASE WHEN s.actual_arrival <= s.scheduled_arrival THEN 1 ELSE 0 END) AS on_time_count,
        ROUND(100.0 * SUM(CASE WHEN s.actual_arrival <= s.scheduled_arrival THEN 1 ELSE 0 END)
              / COUNT(*), 1) AS on_time_pct
    FROM drivers d
    JOIN shipments s ON d.driver_id = s.driver_id
    WHERE s.shipped_date >= DATEADD('month', -3, CURRENT_DATE())
      AND s.actual_arrival IS NOT NULL
    GROUP BY d.driver_id, d.driver_name, d.region
    HAVING COUNT(*) >= 20  -- Minimum deliveries for statistical significance
)
SELECT
    driver_id,
    driver_name,
    region,
    total_deliveries,
    on_time_pct,
    RANK() OVER (PARTITION BY region ORDER BY on_time_pct DESC) AS region_rank,
    DENSE_RANK() OVER (ORDER BY on_time_pct DESC) AS overall_rank,
    NTILE(4) OVER (PARTITION BY region ORDER BY on_time_pct DESC) AS performance_quartile
FROM driver_performance
ORDER BY region, region_rank;
```

### Q12: "What's the difference between Snowflake and Databricks? When would you use each?"

**Answer:**
> "They serve different primary purposes but increasingly overlap:
>
> | Factor | Snowflake | Databricks |
> |--------|-----------|------------|
> | **Core Strength** | SQL analytics, data warehousing | ML/AI, data engineering |
> | **Language** | SQL-first | Python/Spark-first |
> | **Best For** | BI dashboards, ad-hoc queries, structured data | ML training, feature engineering, unstructured data |
> | **ML Support** | Snowpark ML, Cortex (newer) | MLflow, Feature Store, Model Serving (mature) |
> | **Streaming** | Snowpipe (micro-batch) | Structured Streaming (true real-time) |
> | **Cost Model** | Compute + storage separate | DBUs (Databricks Units) |
>
> **At Penske, I'd use both:**
> - **Snowflake:** Data warehouse for all structured business data — shipments, routes, financials, KPIs. Powers dashboards and SQL analytics. Source of truth.
> - **Databricks:** ML platform — feature engineering, model training, model serving. Reads from Snowflake (via connector), writes predictions back.
>
> **The flow:**
> ```
> Sources → Databricks (ETL/Bronze/Silver) → Snowflake (Gold/Analytics)
>                    ↓
>            Databricks (ML Training)
>                    ↓
>            Model Serving → Predictions back to Snowflake
> ```"

---

## Section C: ML & Modeling (Questions 13-18)

### Q13: "You're building a model to predict shipment delays. Walk me through your approach end-to-end."

**Answer:**
> "I'd follow a structured approach:
>
> **1. Problem Definition:**
> - Binary classification: Will this shipment be delayed (>30 min late)?
> - Business impact: Each delayed shipment costs Penske an estimated $X in penalties and customer satisfaction
> - Success metric: Precision-Recall AUC (we care more about catching delays than minimizing false positives)
>
> **2. Data Collection & EDA:**
> - Historical shipments from Snowflake (2+ years)
> - Features: route distance, driver experience, truck age, weather forecast, day of week, time of day, traffic patterns, cargo type, seasonal indicators
> - Check class balance (delays might be 15-20% — imbalanced)
> - Look for data leakage (no features that are only available AFTER the shipment starts)
>
> **3. Feature Engineering (Databricks):**
> ```python
> features = [
>     'route_avg_delay_30d',        # Historical route performance
>     'driver_on_time_rate_90d',    # Driver track record
>     'truck_miles_since_service',  # Vehicle condition
>     'weather_severity_score',     # Forecast weather impact
>     'day_of_week',                # Temporal patterns
>     'is_peak_season',             # Holiday/peak indicators
>     'cargo_weight_pct_capacity',  # Load factor
>     'origin_congestion_score',    # Traffic at origin
> ]
> ```
>
> **4. Model Selection:**
> - Start with **XGBoost** (fast, handles mixed features, good baselines)
> - Compare with **LightGBM** (faster for large datasets)
> - If interpretability needed: **Logistic Regression** as baseline
> - Feature importance analysis with SHAP values
>
> **5. Training & Validation:**
> - Time-based split (train on months 1-18, validate on 19-21, test on 22-24) — never random split for time series
> - Cross-validation with TimeSeriesSplit
> - Hyperparameter tuning with Optuna
> - Track experiments in MLflow
>
> **6. Evaluation:**
> - PR-AUC, F1, precision@k (top 100 most likely delays)
> - Calibration plot (are predicted probabilities meaningful?)
> - Fairness check across regions and driver demographics
>
> **7. Deployment:**
> - Register model in MLflow Model Registry
> - Serve via Databricks Model Serving endpoint
> - Batch predictions nightly for next-day shipments
> - Real-time predictions for dynamic re-routing
>
> **8. Monitoring:**
> - Feature drift detection (data distribution changes)
> - Prediction drift (model output distribution changes)
> - Retrain trigger: when AUC drops >5% from baseline"

### Q14: "How do you handle class imbalance? Your delay dataset is 85% on-time, 15% delayed."

**Answer:**
> "I address imbalance at multiple levels:
>
> **Data Level:**
> - **SMOTE** (Synthetic Minority Oversampling) — generate synthetic delay examples
> - **Undersampling** majority class — random or Tomek links
> - I prefer SMOTE + slight undersampling combined
>
> **Algorithm Level:**
> - **Class weights:** `scale_pos_weight = 85/15 ≈ 5.67` in XGBoost
> - This tells the model that missing a delay is 5.67x worse than a false alarm
>
> **Threshold Level:**
> - Don't use default 0.5 threshold
> - Plot precision-recall curve, choose threshold based on business need
> - If catching delays is critical: lower threshold (more alerts, some false positives)
> - If alert fatigue is a concern: higher threshold (fewer but more confident alerts)
>
> **Evaluation Level:**
> - Never use accuracy (85% by predicting 'on-time' for everything)
> - Use: PR-AUC, F1-score, precision@recall=80%
>
> For Penske, I'd probably use **class weights in XGBoost + threshold tuning** — it's simple, effective, and doesn't create synthetic data artifacts."

### Q15: "Explain SHAP values and how you'd use them at Penske."

**Answer:**
> "SHAP (SHapley Additive exPlanations) explains individual predictions by calculating each feature's contribution.
>
> **How it works:** For each prediction, SHAP assigns a value to each feature showing how much it pushed the prediction up or down from the average.
>
> **At Penske — Shipment Delay Prediction:**
> ```
> Prediction: 78% chance of delay
> Base rate: 15%
>
> SHAP Contributions:
>   weather_severity = +25%    ← Snowstorm forecast
>   route_avg_delay  = +18%    ← This route is historically slow
>   truck_age        = +12%    ← Truck is 8 years old
>   driver_experience = -8%    ← Experienced driver (reduces risk)
>   day_of_week      = +5%     ← Friday (higher traffic)
>   cargo_weight     = +11%    ← Near max capacity
> ```
>
> **Business value:**
> 1. **Operations:** Dispatcher sees WHY the model flagged a delay → can take specific action (reroute due to weather, assign different truck)
> 2. **Trust:** Stakeholders trust the model because they can see the reasoning
> 3. **Debugging:** If SHAP shows a feature contributing unexpectedly, it might indicate data leakage or a bug
> 4. **Feature engineering:** SHAP summary plots show which features matter most globally → focus engineering effort there"

### Q16: "What's the difference between batch and real-time ML inference? When would you use each at Penske?"

**Answer:**
> | Factor | Batch | Real-Time |
> |--------|-------|-----------|
> | **Latency** | Minutes to hours | Milliseconds to seconds |
> | **Frequency** | Scheduled (daily, hourly) | On-demand per request |
> | **Cost** | Lower (bulk processing) | Higher (always-on endpoint) |
> | **Complexity** | Simpler | More complex (scaling, caching) |
>
> **Batch at Penske:**
> - Nightly delay predictions for all next-day shipments
> - Weekly driver risk scoring
> - Monthly route optimization recommendations
> - Demand forecasting for fleet capacity planning
>
> **Real-Time at Penske:**
> - Dynamic re-routing when weather changes mid-transit
> - Agent answering 'What's the ETA for shipment X?' (needs fresh prediction)
> - Anomaly detection on live telematics data
> - Customer-facing shipment delay alerts
>
> **Hybrid approach:** Pre-compute batch predictions, cache them, and use real-time only when conditions change significantly from the batch prediction's assumptions."

### Q17: "How do you detect and handle data drift in production models?"

**Answer:**
> "Data drift means the input data distribution changes from what the model was trained on.
>
> **Detection methods:**
> 1. **Statistical tests:** KS-test, PSI (Population Stability Index) for each feature
> 2. **Distribution monitoring:** Track mean, std, min, max, percentiles of each feature daily
> 3. **Prediction distribution:** If model output distribution shifts, something changed
>
> **Implementation:**
> ```python
> from evidently import ColumnDriftMetric
>
> # Compare current week vs training data
> drift_report = Report(metrics=[
>     ColumnDriftMetric(column_name='weather_severity'),
>     ColumnDriftMetric(column_name='route_avg_delay'),
>     DataDriftTable()
> ])
> drift_report.run(reference_data=train_df, current_data=current_week_df)
> ```
>
> **Response strategy:**
> - **Minor drift (PSI < 0.1):** Log and monitor, no action
> - **Moderate drift (0.1 < PSI < 0.25):** Alert team, evaluate model performance
> - **Major drift (PSI > 0.25):** Trigger retraining pipeline
>
> **Penske example:** COVID caused massive drift in shipment patterns. Models trained on 2019 data failed in 2020. The fix: retrain with recent data, add a 'regime' feature (normal vs disrupted), and implement faster retraining cycles."

### Q18: "How would you A/B test a new ML model at Penske?"

**Answer:**
> "For a shipment delay model upgrade:
>
> **1. Shadow mode first (1-2 weeks):**
> - New model runs in parallel, predictions logged but not used
> - Compare predictions vs old model vs actual outcomes
> - Check for anomalies or edge cases
>
> **2. Canary deployment (1-2 weeks):**
> - Route 5% of predictions to new model
> - Monitor key metrics: accuracy, latency, error rate
> - Quick rollback if issues
>
> **3. A/B test (2-4 weeks):**
> - 50/50 split by region (not random — to avoid confusion)
> - Region A uses old model, Region B uses new model
> - Measure: on-time improvement, false alert rate, dispatcher satisfaction
>
> **4. Statistical significance:**
> - Sample size calculation upfront (need enough shipments per group)
> - Use two-proportion z-test for binary outcomes
> - p < 0.05 and practical significance (>2% improvement)
>
> **5. Full rollout:**
> - If new model wins, gradual rollout: 50% → 75% → 100%
> - Keep old model as fallback for 30 days"

---

## Section D: Cloud & Architecture (Questions 19-24)

### Q19: "How would you architect a data pipeline on Azure for Penske's logistics data?"

**Answer:**
> ```
> DATA SOURCES                  INGESTION              PROCESSING
> ────────────                  ─────────              ──────────
> Fleet GPS (IoT Hub)    ──→  Event Hubs    ──→   Databricks
> TMS API (REST)         ──→  Data Factory  ──→   Spark Streaming
> Partner EDI files      ──→  Blob Storage  ──→   Delta Lake
> Weather API            ──→  Functions     ──→   (Bronze/Silver/Gold)
>
>        STORAGE                SERVING                 CONSUMPTION
>        ───────                ───────                 ───────────
>        ADLS Gen2       ──→   Snowflake          ──→  Power BI
>        (Data Lake)            (Warehouse)             Dashboards
>                               Databricks          ──→ ML Models
>                               (ML Serving)            AI Agents
>                               Azure OpenAI        ──→ Chat Interface
> ```
>
> **Key Azure services and why:**
> - **Event Hubs:** High-throughput streaming for GPS data (~millions of events/day)
> - **Data Factory:** Orchestrate batch ETL from TMS and partner systems
> - **ADLS Gen2:** Cost-effective data lake storage
> - **Databricks on Azure:** Unified analytics and ML platform
> - **Snowflake on Azure:** SQL analytics, BI serving layer
> - **Azure OpenAI:** Private LLM endpoints for agents
> - **Azure AI Search:** Vector search for knowledge base RAG"

### Q20: "What's the difference between Azure Functions, Azure Databricks, and Azure Data Factory? When do you use each?"

**Answer:**
> | Service | Purpose | Use At Penske |
> |---------|---------|---------------|
> | **Azure Functions** | Serverless event-driven code | Trigger on new GPS data, webhook handlers, lightweight API endpoints |
> | **Azure Data Factory** | ETL orchestration, data movement | Schedule daily loads from TMS, copy data between systems, orchestrate pipelines |
> | **Azure Databricks** | Large-scale data processing + ML | Feature engineering, model training, streaming processing, Delta Lake |
>
> **Rule of thumb:**
> - Need to **move data** on a schedule → Data Factory
> - Need to **process data** at scale → Databricks
> - Need to **react to an event** quickly → Functions
>
> In a pipeline, they work together: Data Factory triggers → Databricks notebook runs → results stored → Function sends notification."

### Q21: "How do you secure sensitive data in a cloud ML pipeline?"

**Answer:**
> "Security at every layer:
>
> **Data at rest:** Encryption (AES-256) on ADLS, Snowflake (default), Databricks (customer-managed keys option).
>
> **Data in transit:** TLS 1.2+ for all connections. VNet integration so data never traverses public internet.
>
> **Access control:**
> - Azure AD for authentication
> - RBAC (Role-Based Access Control) — data scientists get read access to Silver/Gold, not Bronze
> - Snowflake row-level security — analysts see only their region's data
> - Column-level masking for PII (driver names, SSNs)
>
> **Secrets management:** Azure Key Vault for all API keys, connection strings, certificates. Never hardcoded.
>
> **ML-specific:**
> - Training data anonymized (hash driver IDs)
> - Model artifacts stored in private registry
> - Inference endpoints behind API gateway with auth
> - Audit logging on all model predictions
>
> **Compliance:** SOC 2, GDPR (if international), DOT regulations for transportation data."

### Q22: "How would you design a knowledge base system for Penske's internal documents?"

**Answer:**
> "A RAG-based knowledge system:
>
> **Architecture:**
> ```
> Documents (SOPs, manuals, policies)
>       ↓
> Document Processor (chunk + embed)
>       ↓
> Azure AI Search (vector + keyword index)
>       ↓
> Retrieval Pipeline (hybrid search + reranking)
>       ↓
> Azure OpenAI (generate answer with citations)
>       ↓
> Chat Interface (Teams bot or web app)
> ```
>
> **Step 1 — Ingestion:**
> - Sources: SharePoint, Confluence, PDF manuals, training materials
> - Chunk documents: 512 tokens with 50 token overlap
> - Use semantic chunking (respect paragraph/section boundaries)
> - Generate embeddings with Azure OpenAI text-embedding-ada-002
>
> **Step 2 — Indexing:**
> - Store in Azure AI Search with both vector and keyword fields
> - Add metadata: document type, department, last updated, access level
>
> **Step 3 — Retrieval:**
> - Hybrid search: vector similarity (semantic) + BM25 (keyword)
> - Rerank top 20 results with a cross-encoder to get top 5
> - This catches both 'what is the PTO policy' (semantic) and 'form DOT-1234' (keyword)
>
> **Step 4 — Generation:**
> - Pass top 5 chunks + user query to Azure OpenAI
> - System prompt: 'Answer based only on the provided context. Cite sources. Say I don't know if the answer isn't in the context.'
>
> **Step 5 — Evaluation:**
> - Track: answer relevance, source attribution accuracy, user satisfaction
> - Weekly review of 'I don't know' responses to identify knowledge gaps"

### Q23: "Explain Snowflake Cortex and how it enables AI at Penske."

**Answer:**
> "Snowflake Cortex brings AI/ML directly into Snowflake — no data movement needed.
>
> **Key Cortex Functions:**
>
> | Function | What It Does | Penske Use Case |
> |----------|-------------|-----------------|
> | `COMPLETE()` | LLM text generation | Summarize shipment incident reports |
> | `EXTRACT_ANSWER()` | Question answering over text | 'What caused the delay?' from notes |
> | `SENTIMENT()` | Sentiment analysis | Analyze customer feedback |
> | `TRANSLATE()` | Language translation | Translate driver reports (multilingual) |
> | `EMBED_TEXT()` | Generate embeddings | Build search over shipment notes |
> | `CLASSIFY_TEXT()` | Text classification | Categorize support tickets |
>
> **Example — Summarize delay reasons:**
> ```sql
> SELECT
>     shipment_id,
>     SNOWFLAKE.CORTEX.COMPLETE(
>         'mistral-large',
>         'Summarize the delay reason in one sentence: ' || delay_notes
>     ) AS delay_summary
> FROM shipments
> WHERE is_delayed = TRUE
>   AND shipped_date >= DATEADD('day', -7, CURRENT_DATE());
> ```
>
> **Why this matters:** Data stays in Snowflake (no external API calls), governed by existing access controls, and SQL analysts can use AI without Python."

### Q24: "How would you implement MLOps at Penske?"

**Answer:**
> "MLOps ensures models are reliably developed, deployed, and maintained.
>
> **The MLOps Lifecycle:**
> ```
> DEVELOP → TEST → DEPLOY → MONITOR → RETRAIN
>    ↑                                    │
>    └────────────────────────────────────┘
> ```
>
> **1. Development (Databricks):**
> - Notebooks for experimentation
> - MLflow for experiment tracking (parameters, metrics, artifacts)
> - Feature Store for consistent features
>
> **2. Testing:**
> - Unit tests for feature engineering code
> - Data validation tests (Great Expectations)
> - Model validation: performance on holdout set meets threshold
> - A/B test framework for comparing models
>
> **3. Deployment:**
> - MLflow Model Registry: Staging → Production promotion
> - CI/CD pipeline (Azure DevOps or GitHub Actions):
>   - PR triggers: lint, test, validate
>   - Merge to main: deploy to staging
>   - Approval gate: promote to production
> - Databricks Model Serving for real-time endpoints
> - Batch scoring via Databricks Jobs
>
> **4. Monitoring:**
> - Data drift (Evidently or custom)
> - Model performance decay
> - Prediction latency and error rates
> - Feature freshness (are features being updated?)
> - Alerting to Slack/Teams when thresholds breached
>
> **5. Retraining:**
> - Scheduled: Monthly full retrain
> - Triggered: When drift exceeds threshold
> - Automated pipeline: pull latest data → compute features → train → evaluate → if better → deploy"

---

## Section E: Evals, Guardrails & LLM Observability (Questions 25-30)

### Q25: "How do you build an evaluation framework for an LLM-powered agent?"

**Answer:**
> "I build evals at three levels:
>
> **Level 1 — Unit Evals (per component):**
> - Retrieval: Does the search return relevant documents? Measure recall@k, precision@k, MRR
> - Generation: Is the answer faithful to retrieved context? Measure faithfulness, relevance
> - Tool calling: Does the agent call the right tool with correct parameters?
>
> **Level 2 — End-to-End Evals (full pipeline):**
> - Create a test suite of 200+ (query, expected_answer) pairs
> - Run weekly, compare against baseline
> - Categories: easy (factual lookup), medium (multi-step reasoning), hard (ambiguous queries)
>
> **Level 3 — LLM-as-Judge:**
> - Use a stronger model (GPT-4) to evaluate a weaker model's output
> - Criteria: accuracy, completeness, tone, safety
> - Calibrate the judge against human ratings first
>
> ```python
> # Example eval pipeline
> eval_results = []
> for test_case in test_suite:
>     agent_answer = agent.run(test_case.query)
>     
>     # Automated metrics
>     relevance = compute_relevance(agent_answer, test_case.expected)
>     faithfulness = check_faithfulness(agent_answer, retrieved_docs)
>     
>     # LLM judge
>     judge_score = llm_judge.evaluate(
>         query=test_case.query,
>         answer=agent_answer,
>         reference=test_case.expected,
>         criteria=['accuracy', 'completeness', 'safety']
>     )
>     
>     eval_results.append({
>         'query': test_case.query,
>         'relevance': relevance,
>         'faithfulness': faithfulness,
>         'judge_score': judge_score
>     })
> ```
>
> **Key insight:** Evals must run automatically in CI/CD. Every PR that changes prompts or retrieval logic triggers the eval suite. If scores drop below threshold, the PR is blocked."

### Q26: "What guardrails would you put on a customer-facing agent at Penske?"

**Answer:**
> "Defense in depth with five guardrail layers:
>
> **Layer 1 — Input Guards:**
> - Content filter: Block profanity, threats, PII in queries
> - Topic filter: Reject off-topic queries ('write me a poem')
> - Length limit: Max 500 tokens input
> - Rate limit: Max 10 queries/minute per user
>
> **Layer 2 — Retrieval Guards:**
> - Access control: Only retrieve documents the user is authorized to see
> - Relevance threshold: If no document scores above 0.7 similarity, say 'I don't have information on that'
> - Source validation: Only use approved document sources
>
> **Layer 3 — Generation Guards:**
> - Grounding check: Verify the answer is supported by retrieved context (no hallucination)
> - PII filter: Scan output for SSNs, phone numbers, internal employee data
> - Competitor filter: Don't mention competitor pricing or capabilities
> - Legal filter: Don't make promises about delivery guarantees or liability
>
> **Layer 4 — Action Guards:**
> - Tool allowlist: Customer-facing agent can only call read-only tools
> - Parameter validation: SQL queries must be SELECT-only, no modification
> - Human approval: Any action affecting shipments requires human confirmation
>
> **Layer 5 — Output Guards:**
> - Toxicity check: Azure Content Safety API
> - Format validation: Ensure structured outputs match expected schema
> - Confidence threshold: If model uncertainty is high, escalate to human
>
> ```
> User Input → [Input Guards] → Agent → [Retrieval Guards] → Search
>     → [Generation Guards] → LLM → [Output Guards] → User
> ```"

### Q27: "How do you implement LLM observability? What do you log and monitor?"

**Answer:**
> "Observability for LLM systems requires logging more than traditional software:
>
> **What to log (every request):**
> ```
> {
>   'trace_id': 'abc-123',           // Unique request ID
>   'timestamp': '2026-02-10T12:00', 
>   'user_id': 'user_456',
>   'input_query': 'Where is shipment X?',
>   'input_tokens': 45,
>   
>   // Retrieval step
>   'retrieved_docs': [...],          // Document IDs and scores
>   'retrieval_latency_ms': 120,
>   
>   // LLM step  
>   'model': 'gpt-4',
>   'prompt_tokens': 1200,
>   'completion_tokens': 350,
>   'llm_latency_ms': 800,
>   'temperature': 0,
>   
>   // Tool calls
>   'tool_calls': [
>     {'name': 'get_shipment', 'args': {'id': 'X'}, 'latency_ms': 50}
>   ],
>   
>   // Output
>   'response': 'Shipment X is currently...',
>   'guardrail_flags': [],
>   'total_latency_ms': 1200,
>   'estimated_cost': 0.02
> }
> ```
>
> **Dashboards I'd build:**
>
> | Dashboard | Metrics | Alert Threshold |
> |-----------|---------|-----------------|
> | **Latency** | p50, p95, p99 response time | p95 > 5s |
> | **Cost** | Daily spend, cost per query | Daily > budget |
> | **Quality** | Relevance score, hallucination rate | Hallucination > 5% |
> | **Usage** | Queries/hour, unique users, peak times | Unusual spike |
> | **Errors** | Tool failures, LLM errors, timeout rate | Error rate > 2% |
> | **Safety** | Guardrail triggers, blocked queries | Any safety breach |
>
> **Tools:** LangSmith for trace visualization, Prometheus + Grafana for metrics, Azure Application Insights for infrastructure."

### Q28: "An agent keeps hallucinating shipment details that don't exist. How do you debug and fix it?"

**Answer:**
> "Systematic debugging approach:
>
> **Step 1 — Reproduce:** Find 10+ examples of hallucinations. Categorize them:
> - Fabricated shipment IDs?
> - Wrong dates/locations?
> - Mixing up different shipments?
>
> **Step 2 — Trace the pipeline:**
> - Check retrieval: Are the right documents being retrieved? If retrieval returns wrong docs → fix search
> - Check context: Is the relevant info in the context window? If context is correct but answer is wrong → fix prompt
> - Check the prompt: Is the system prompt clear about only using provided context?
>
> **Step 3 — Root cause fixes:**
>
> | Root Cause | Fix |
> |------------|-----|
> | Retrieval returns irrelevant docs | Improve chunking, add metadata filters, tune embedding model |
> | Context too large (LLM loses focus) | Reduce context window, use reranking to keep only top 3-5 chunks |
> | Prompt doesn't enforce grounding | Add: 'Only answer based on the provided context. If the answer isn't in the context, say I don't know.' |
> | LLM temperature too high | Set temperature=0 for factual tasks |
> | No source attribution | Require citations: 'Always cite the source document and section' |
>
> **Step 4 — Guardrail:**
> - Add a post-generation check: extract any shipment IDs from the response, verify they exist in the database
> - If verification fails → 'I found some relevant information but couldn't verify the details. Let me connect you with a specialist.'
>
> **Step 5 — Eval regression test:**
> - Add the hallucination examples to the test suite
> - Ensure they pass after the fix
> - Run in CI/CD to prevent regression"

### Q29: "How do you balance cost vs quality in a production LLM system?"

**Answer:**
> "Cost optimization strategy:
>
> **1. Model tiering:**
> ```
> Simple queries (70%)  → GPT-3.5-turbo   ($0.50/1M tokens)
> Complex queries (25%) → GPT-4-turbo     ($10/1M tokens)
> Critical tasks (5%)   → GPT-4           ($30/1M tokens)
> ```
> Use a lightweight classifier to route queries to the right model.
>
> **2. Caching:**
> - Exact match cache: Same question → same answer (Redis, TTL 1 hour)
> - Semantic cache: Similar questions → cached answer (embedding similarity > 0.95)
> - Saves 20-40% of API calls in practice
>
> **3. Prompt optimization:**
> - Shorter system prompts (every token costs money)
> - Use few-shot examples only when needed
> - Compress retrieved context (summarize before injecting)
>
> **4. Batch where possible:**
> - Nightly batch summaries instead of real-time generation
> - Pre-compute common answers during off-peak hours
>
> **5. Monitor and budget:**
> - Daily cost dashboard
> - Per-user and per-feature cost tracking
> - Alerting when daily spend exceeds budget
>
> At Penske scale, these optimizations can reduce LLM costs by 50-70% while maintaining quality."

### Q30: "What's the difference between LLM evaluation metrics: BLEU, ROUGE, BERTScore, and LLM-as-Judge?"

**Answer:**
> | Metric | How It Works | Best For | Weakness |
> |--------|-------------|----------|----------|
> | **BLEU** | N-gram overlap with reference | Translation | Poor for open-ended generation |
> | **ROUGE** | Recall of n-grams from reference | Summarization | Misses semantic similarity |
> | **BERTScore** | Embedding similarity to reference | General text quality | Still needs a reference answer |
> | **LLM-as-Judge** | Another LLM rates the output | Open-ended, no reference needed | Expensive, judge bias |
>
> **For Penske agents, I'd use:**
> - **BERTScore** for automated regression testing (fast, reasonable quality)
> - **LLM-as-Judge** for weekly quality audits (thorough, handles nuance)
> - **Custom metrics** for specific tasks: SQL correctness (does query run?), factual accuracy (verifiable against DB)
> - **Human evaluation** monthly for calibration (gold standard)"

---

# Part 3: System Design Scenarios

## Scenario 1: "Design an AI-powered shipment tracking and delay prediction system for Penske."

### Step-by-Step Solution

**Step 1 — Clarify Requirements (Always Ask First):**
> "Before I design, let me clarify a few things:
> - How many shipments per day? (assume 50,000)
> - What latency is acceptable for predictions? (assume <2 seconds)
> - Do we need real-time re-prediction when conditions change?
> - Who are the users? (dispatchers, customers, management)"

**Step 2 — High-Level Architecture:**
```
┌────────────────────────────────────────────────────────────────────┐
│              SHIPMENT DELAY PREDICTION SYSTEM                       │
├────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  DATA LAYER                                                          │
│  ══════════                                                          │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐       │
│  │ Fleet GPS │  │ Weather   │  │ Traffic   │  │ Historical│       │
│  │ (real-time)│  │ API       │  │ API       │  │ Shipments │       │
│  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘       │
│        │              │              │              │               │
│        ▼              ▼              ▼              ▼               │
│  ┌─────────────────────────────────────────────────────────┐       │
│  │         Azure Event Hubs / Kafka (Streaming)            │       │
│  └────────────────────────┬────────────────────────────────┘       │
│                           ▼                                         │
│  PROCESSING LAYER                                                    │
│  ════════════════                                                    │
│  ┌────────────────────────────────────────────────────┐             │
│  │  Databricks (Spark Structured Streaming)            │             │
│  │  • Bronze: Raw events                               │             │
│  │  • Silver: Cleaned, enriched (join GPS + weather)   │             │
│  │  • Gold: Feature tables for ML                      │             │
│  └────────────────────────┬───────────────────────────┘             │
│                           ▼                                         │
│  ML LAYER                                                            │
│  ════════                                                            │
│  ┌──────────────────────┐  ┌──────────────────────┐                │
│  │  Batch Predictions   │  │  Real-Time Endpoint  │                │
│  │  (Nightly for next   │  │  (On-demand for      │                │
│  │   day's shipments)   │  │   condition changes)  │                │
│  └──────────┬───────────┘  └──────────┬───────────┘                │
│             ▼                          ▼                             │
│  SERVING LAYER                                                       │
│  ═════════════                                                       │
│  ┌────────────────────────────────────────────────────┐             │
│  │  Snowflake (predictions + analytics)                │             │
│  │  API Gateway (real-time queries)                    │             │
│  │  AI Agent (natural language interface)               │             │
│  └────────────────────────┬───────────────────────────┘             │
│                           ▼                                         │
│  CONSUMER LAYER                                                      │
│  ══════════════                                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │Dispatcher│  │ Customer │  │Management│  │ AI Agent │           │
│  │Dashboard │  │  Portal  │  │ Reports  │  │ Chat     │           │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘           │
│                                                                      │
└────────────────────────────────────────────────────────────────────┘
```

**Step 3 — Key Design Decisions & Trade-offs:**

| Decision | Choice | Alternative | Why |
|----------|--------|-------------|-----|
| Streaming platform | Event Hubs | Kafka | Already on Azure, simpler ops |
| Processing | Databricks Streaming | Azure Stream Analytics | Need ML feature engineering |
| ML Model | XGBoost (batch) + lightweight model (real-time) | Deep learning | Interpretable, fast, good accuracy |
| Storage | Snowflake + Redis cache | Just Snowflake | Redis for <100ms real-time lookups |
| Agent framework | LangChain + Azure OpenAI | Custom | Fast development, good enough control |

**Step 4 — Discuss Scale & Cost:**
> "For 50K daily shipments, the batch pipeline runs on a Medium Databricks cluster (~$50/day). The real-time endpoint costs ~$200/month on Databricks Model Serving. The Agent uses Azure OpenAI at roughly $500/month for typical query volume. Total: ~$2,500/month — a fraction of the value from preventing even one delayed shipment."

---

## Scenario 2: "Design a multi-agent system for Penske's operations center."

### Step-by-Step Solution

**Architecture:**
```
┌─────────────────────────────────────────────────────────────┐
│              PENSKE OPERATIONS AI SYSTEM                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌───────────────────┐                                        │
│  │  ROUTER AGENT     │  Classifies incoming requests          │
│  │  (GPT-3.5-turbo)  │  Routes to specialist agent            │
│  └─────────┬─────────┘                                        │
│            │                                                   │
│    ┌───────┼───────┬──────────┬──────────┐                    │
│    ▼       ▼       ▼          ▼          ▼                    │
│  ┌─────┐ ┌─────┐ ┌─────┐  ┌─────┐  ┌─────────┐             │
│  │Track│ │Route│ │Fleet│  │Report│  │Knowledge│             │
│  │Agent│ │Agent│ │Agent│  │Agent │  │Agent    │             │
│  └──┬──┘ └──┬──┘ └──┬──┘  └──┬──┘  └────┬────┘             │
│     │       │       │        │           │                    │
│  TOOLS:   TOOLS:  TOOLS:   TOOLS:     TOOLS:                 │
│  -Shipment -Route  -Maint.  -Snowflake -Vector               │
│   DB API   Optim.  Schedule  Queries    Search                │
│  -GPS API  -Maps   -Fleet   -Chart     -Doc                  │
│  -ETA      -Traffic DB       Gen       Retrieval              │
│   Calc     API                                                │
│                                                               │
│  SHARED RESOURCES:                                            │
│  • Snowflake (data) • Azure AI Search (knowledge)             │
│  • MCP Servers (standardized access)                          │
│  • Guardrails (all agents share safety layer)                 │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

**Key Design Principles:**
> 1. **Router pattern** over monolithic agent — each specialist is simpler and more reliable
> 2. **Shared guardrails** — one safety layer, consistently applied
> 3. **MCP for data access** — all agents connect to data through MCP servers (standardized, secure)
> 4. **Cost tiering** — Router uses cheap GPT-3.5, specialists use GPT-4 only when needed
> 5. **Observability** — Centralized logging with trace IDs that span agent handoffs

---

# Part 4: Live Coding Challenges

## Challenge 1: Python — Build a Simple Agent Tool

**Prompt:** "Write a Python function that an agent could use to query shipment status and format the response."

```python
from typing import Optional
from datetime import datetime
import json

def get_shipment_status(shipment_id: str) -> dict:
    """
    Retrieve shipment status for an AI agent.
    Returns structured data the agent can use to answer user questions.
    
    Args:
        shipment_id: The shipment tracking number
        
    Returns:
        dict with shipment details or error message
    """
    # In production: query Snowflake or API
    # Simulated for interview
    shipments_db = {
        "PEN-2026-001": {
            "id": "PEN-2026-001",
            "origin": "Chicago, IL",
            "destination": "Dallas, TX", 
            "status": "In Transit",
            "carrier": "Penske Logistics",
            "scheduled_arrival": "2026-02-11 14:00",
            "estimated_arrival": "2026-02-11 15:30",
            "delay_minutes": 90,
            "delay_reason": "Winter weather in Oklahoma",
            "last_location": "Oklahoma City, OK",
            "last_update": "2026-02-10 10:00"
        }
    }
    
    shipment = shipments_db.get(shipment_id)
    
    if not shipment:
        return {
            "error": f"Shipment {shipment_id} not found",
            "suggestion": "Please verify the tracking number"
        }
    
    # Add computed fields
    shipment["is_delayed"] = shipment["delay_minutes"] > 0
    shipment["delay_severity"] = (
        "none" if shipment["delay_minutes"] == 0
        else "minor" if shipment["delay_minutes"] < 60
        else "moderate" if shipment["delay_minutes"] < 180
        else "severe"
    )
    
    return shipment
```

## Challenge 2: SQL — Window Functions for Driver Analytics

**Prompt:** "Write a query showing each driver's monthly performance trend with running averages."

```sql
WITH monthly_stats AS (
    SELECT
        d.driver_id,
        d.driver_name,
        d.region,
        DATE_TRUNC('month', s.delivery_date) AS month,
        COUNT(*) AS deliveries,
        ROUND(100.0 * SUM(CASE WHEN s.on_time THEN 1 ELSE 0 END) 
              / COUNT(*), 1) AS on_time_pct,
        ROUND(AVG(s.fuel_efficiency), 2) AS avg_mpg
    FROM drivers d
    JOIN shipments s ON d.driver_id = s.driver_id
    WHERE s.delivery_date >= DATEADD('month', -12, CURRENT_DATE())
    GROUP BY d.driver_id, d.driver_name, d.region,
             DATE_TRUNC('month', s.delivery_date)
)
SELECT
    driver_id,
    driver_name,
    region,
    month,
    deliveries,
    on_time_pct,
    -- 3-month rolling average
    ROUND(AVG(on_time_pct) OVER (
        PARTITION BY driver_id 
        ORDER BY month 
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ), 1) AS rolling_3m_on_time,
    -- Month-over-month change
    on_time_pct - LAG(on_time_pct) OVER (
        PARTITION BY driver_id ORDER BY month
    ) AS mom_change,
    -- Trend direction
    CASE 
        WHEN on_time_pct > LAG(on_time_pct) OVER (
            PARTITION BY driver_id ORDER BY month) THEN 'improving'
        WHEN on_time_pct < LAG(on_time_pct) OVER (
            PARTITION BY driver_id ORDER BY month) THEN 'declining'
        ELSE 'stable'
    END AS trend
FROM monthly_stats
ORDER BY driver_id, month;
```

## Challenge 3: Debug This Agent Code

**Prompt:** "This agent is returning wrong answers. Find and fix the bugs."

```python
# BUGGY CODE — find 3 issues
def run_agent(query, tools, max_iterations=10):
    messages = [{"role": "system", "content": "You are a helpful assistant."}]
    messages.append({"role": "user", "content": query})
    
    for i in range(max_iterations):
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            tools=tools,
            temperature=0.9  # BUG 1: Too high for factual tasks
        )
        
        msg = response.choices[0].message
        # BUG 2: Not appending assistant message to history
        
        if msg.tool_calls:
            for tc in msg.tool_calls:
                result = execute_tool(tc.function.name, tc.function.arguments)
                messages.append({
                    "role": "tool",
                    "content": result  # BUG 3: result might not be string
                    # Missing: tool_call_id
                })
        else:
            return msg.content
    
    return "Max iterations reached"
```

**Fixes:**
```python
def run_agent(query, tools, max_iterations=10):
    messages = [{"role": "system", "content": "You are a helpful assistant."}]
    messages.append({"role": "user", "content": query})
    
    for i in range(max_iterations):
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            tools=tools,
            temperature=0          # FIX 1: Use 0 for factual/deterministic tasks
        )
        
        msg = response.choices[0].message
        messages.append(msg)       # FIX 2: Append assistant message to maintain history
        
        if msg.tool_calls:
            for tc in msg.tool_calls:
                result = execute_tool(tc.function.name, tc.function.arguments)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,              # FIX 3a: Include tool_call_id
                    "content": str(result)               # FIX 3b: Ensure string type
                })
        else:
            return msg.content
    
    return "Max iterations reached"
```

---

# Part 5: Behavioral & Leadership Q&A

## The STAR Method

Every behavioral answer should follow:
```
S — Situation: Set the context (1-2 sentences)
T — Task: What was your specific responsibility?
A — Action: What did YOU do? (be specific, use "I")
R — Result: Quantifiable outcome
```

### Q1: "Tell me about a time you built something complex from scratch."

**Answer:**
> **S:** "At [previous company], we had customer support agents spending 4 hours daily searching through documentation to answer client questions.
>
> **T:** I was tasked with building an AI-powered knowledge assistant to reduce this time.
>
> **A:** I designed and built a RAG system: ingested 10,000+ documents, implemented hybrid search with Azure AI Search, built a LangChain agent with custom tools for querying our database and document store, and added guardrails to prevent hallucination.
>
> **R:** The system reduced average query resolution time from 15 minutes to 2 minutes, with 92% accuracy on factual questions. Support team satisfaction increased 40%."

### Q2: "Tell me about a time a model failed in production. What did you do?"

**Answer:**
> **S:** "Our shipment ETA model suddenly started predicting arrival times 2 hours early for an entire region.
>
> **T:** I was the on-call data scientist responsible for investigating and fixing production model issues.
>
> **A:** I checked our monitoring dashboard and saw a spike in prediction errors starting Tuesday. I traced it to a data pipeline change — a new field mapping caused the 'traffic_score' feature to be populated with 'weather_score' values. I rolled back the pipeline change immediately, then added a data validation step that checks feature distributions before they reach the model, and an automated alert when feature statistics deviate significantly.
>
> **R:** Root cause identified within 2 hours, fix deployed same day. We added 15 data validation tests that have since caught 3 similar issues before they reached production."

### Q3: "How do you handle disagreements with stakeholders about model performance?"

**Answer:**
> **S:** "A product manager wanted to launch a recommendation model with 72% accuracy, but I believed the error rate was too high for production.
>
> **T:** I needed to either convince them to wait or find a compromise.
>
> **A:** Instead of saying 'no,' I reframed the discussion around business impact. I calculated that at 72% accuracy, we'd send wrong recommendations to ~28,000 customers monthly — costing an estimated $140K in returns and support tickets. I proposed a phased launch: start with the top 10% most confident predictions (where accuracy was 95%), measure impact, then gradually expand.
>
> **R:** The phased approach launched successfully. At 95% confidence threshold, we served 8,000 customers with 97% accuracy. Over 3 months, we tuned the threshold down to serve 60% of customers while maintaining 90% accuracy."

### Q4: "Why Penske? Why this role?"

**Answer:**
> "Three reasons:
>
> **1. Real-world impact:** Penske moves critical goods for thousands of businesses. Building AI that optimizes this supply chain has tangible impact — fewer delayed shipments, more efficient routes, better driver experiences.
>
> **2. The technical challenge:** This role combines everything I'm passionate about — building GenAI agents, production ML systems, and working across a modern data stack (Snowflake, Databricks, Azure). It's not just chatbots — it's agents that interact with real systems and make real decisions.
>
> **3. The stage of AI adoption:** Penske is investing in AI seriously — this role is about building the foundation. I want to be the person who designs these systems from the ground up, not just maintain existing ones."

### Q5: "How do you stay current with rapidly changing AI technology?"

**Answer:**
> "I have a structured approach:
>
> **Weekly:** Read 2-3 papers from Arxiv (focus on agents, RAG, evaluation), follow key researchers on Twitter/X, and read the LangChain/LlamaIndex changelogs.
>
> **Monthly:** Build a small prototype with a new tool or technique. Last month I built an MCP server. This month I'm experimenting with LangGraph's new features.
>
> **Quarterly:** Take an online course or attend a virtual conference. Recently completed DeepLearning.ai's LLM agents course.
>
> **At work:** I run a bi-weekly 'AI Innovations' session where the team shares new papers, tools, and techniques. This keeps the whole team current, not just me."

---

# Part 6: Penske-Specific Case Studies

## Case Study 1: Route Optimization Agent

**Scenario:** Penske wants an AI agent that dispatchers can ask: "What's the best route for delivering 3 shipments from Chicago to Dallas, Houston, and San Antonio?"

**Your Solution:**

> **Architecture:**
> - Router agent receives the query
> - Calls Route Optimization tool (distance matrix API + custom optimization)
> - Checks weather conditions for each route
> - Queries historical performance data from Snowflake
> - Returns optimized route with explanation
>
> **Key Talking Points:**
> - "I'd use the Traveling Salesman Problem (TSP) heuristic for route ordering"
> - "Weather and traffic data provide dynamic route adjustments"
> - "The agent explains its reasoning: 'I routed through San Antonio first because of severe weather on the I-35 corridor to Dallas'"
> - "Human-in-the-loop: dispatcher confirms before dispatching"

## Case Study 2: Fleet Maintenance Predictor

**Scenario:** Predict which trucks will need maintenance in the next 30 days to prevent breakdowns.

**Your Solution:**

> **Approach:** Survival analysis + classification
> - Features: miles since last service, truck age, route difficulty score, sensor data (engine temp, oil pressure), driver behavior scores
> - Model: XGBoost for 30-day breakdown probability
> - Output: Priority list ranked by risk × cost of breakdown
>
> **Talking Points:**
> - "I use a time-to-event model (survival analysis) for the time horizon, combined with XGBoost for risk scoring"
> - "Feature importance shows 'miles since service' and 'engine temperature trend' are the top predictors"
> - "The model reduced unplanned breakdowns by 35% in similar logistics applications"
> - "Integration: predictions feed into a Databricks dashboard + the operations agent can query: 'Which trucks in the Midwest need service this week?'"

## Case Study 3: Customer Communication Agent

**Scenario:** Build an agent that automatically updates customers about their shipment status, including proactive delay notifications.

**Your Solution:**

> **Architecture:**
> ```
> Delay Prediction Model
>        ↓
> If delay > 30 min predicted
>        ↓
> Agent generates personalized message
>        ↓
> Human review (for first 2 weeks)
>        ↓
> Send via email/SMS
> ```
>
> **Key considerations:**
> - "Tone matters — professional but empathetic: 'Your shipment is experiencing a slight delay due to weather. New ETA: 3:30 PM.'"
> - "Never over-promise: use prediction confidence intervals"
> - "Guardrails: no internal details (driver names, route specifics), no liability language"
> - "Escalation: if customer responds with a complaint, route to human"

---

# Part 7: Step-by-Step Knowledge Base Education Plan

## Week 1: Foundations (Days 1-7)

### Day 1-2: GenAI Agent Fundamentals
```
□ Read: LangChain docs — Agents section
□ Build: Simple weather agent (raw API)
□ Build: Same agent with LangChain
□ Understand: ReAct loop, function calling
□ Review: AGENT_TOOL_SELECTION_GUIDE.md Parts 1-2
```

### Day 3-4: RAG & Knowledge Bases
```
□ Read: LlamaIndex documentation — basic RAG
□ Build: Simple RAG over 10 PDF documents
□ Learn: Chunking strategies, embedding models
□ Understand: Hybrid search (vector + keyword)
□ Build: Add reranking to your RAG pipeline
```

### Day 5-6: MCP & Tool Integration
```
□ Read: Anthropic MCP documentation
□ Build: Simple MCP server (file reader)
□ Build: MCP server connected to a database
□ Understand: Resources, Tools, Prompts in MCP
□ Review: PENSKE_INTERVIEW_PREP.md Section 2
```

### Day 7: Review & Practice
```
□ Review: All Q&A from this guide (Sections A-B)
□ Practice: Explain agent architecture out loud (5 min)
□ Practice: Draw system diagram on whiteboard
□ Flashcard review: INTERVIEW_FLASHCARDS.md
```

---

## Week 2: Data & ML Stack (Days 8-14)

### Day 8-9: SQL & Snowflake Deep Dive
```
□ Practice: 10 complex SQL queries (window functions, CTEs)
□ Learn: Snowflake-specific features (clustering, dynamic tables, Cortex)
□ Build: Query optimization exercise
□ Study: Medallion architecture
□ Review: Q&A Questions 7-12 in this guide
```

### Day 10-11: Databricks & MLOps
```
□ Read: Databricks Feature Store documentation
□ Read: MLflow model registry and serving
□ Understand: Databricks + Snowflake integration
□ Learn: Delta Lake (MERGE, time travel, optimization)
□ Build: End-to-end ML pipeline (train → register → serve)
```

### Day 12-13: Traditional ML Refresher
```
□ Review: XGBoost, LightGBM, Random Forest
□ Practice: Feature engineering for tabular data
□ Study: Class imbalance handling (SMOTE, class weights)
□ Study: SHAP values and model interpretability
□ Review: Q&A Questions 13-18 in this guide
```

### Day 14: Review & Practice
```
□ Review: All Q&A from Sections C-D
□ Practice: System design on whiteboard (30 min)
□ Practice: Explain Medallion architecture out loud
□ Practice: Write 3 complex SQL queries from memory
```

---

## Week 3: Production & Interview Skills (Days 15-21)

### Day 15-16: Evals, Guardrails & Safety
```
□ Learn: LLM evaluation metrics (BERTScore, LLM-as-judge)
□ Build: Simple eval pipeline for a RAG system
□ Study: Guardrail patterns (input/output validation)
□ Study: Prompt injection defenses
□ Review: Q&A Questions 25-30 in this guide
```

### Day 17-18: Cloud Architecture (Azure)
```
□ Study: Azure OpenAI, AI Search, Event Hubs, Data Factory
□ Learn: VNet, Key Vault, RBAC security patterns
□ Practice: Draw architecture diagrams for Penske scenarios
□ Review: Q&A Questions 19-24 in this guide
```

### Day 19-20: Behavioral & Case Studies
```
□ Write: 5 STAR stories from your experience
□ Practice: Tell each story in 2 minutes
□ Study: Penske case studies (Part 6 of this guide)
□ Prepare: "Why Penske?" and "Why this role?" answers
□ Research: Penske recent news, AI initiatives
```

### Day 21: Final Review
```
□ Full mock interview (ask a friend or use AI)
□ Review: Day-Before Cheat Sheet (Part 8)
□ Review: Weak areas identified during practice
□ Rest and prepare mentally
```

---

# Part 8: Day-Before Cheat Sheet

## Quick Reference — Key Numbers to Know

| Metric | Value |
|--------|-------|
| GPT-4 context window | 128K tokens |
| Claude context window | 200K tokens |
| Embedding dimension (ada-002) | 1536 |
| Good retrieval recall@5 | >85% |
| Acceptable hallucination rate | <5% |
| XGBoost typical AUC (tabular) | 0.85-0.95 |
| p-value threshold | <0.05 |

## Key Frameworks to Mention

| Need | Framework | One-Liner |
|------|-----------|-----------|
| Agent orchestration | LangChain | "Swiss army knife for LLM apps" |
| Complex workflows | LangGraph | "State machines for agents" |
| Document RAG | LlamaIndex | "Purpose-built for data retrieval" |
| Multi-agent | AutoGen | "Agents talking to agents" |
| ML tracking | MLflow | "Git for ML experiments" |
| Data quality | Great Expectations | "Unit tests for data" |
| Feature store | Databricks FS | "Reusable ML features" |

## Architecture Patterns to Draw

**1. RAG Pipeline:**
```
Query → Embed → Vector Search → Rerank → LLM + Context → Answer
```

**2. Agent Loop:**
```
User → LLM (reason) → Tool Call → Execute → LLM (reason) → ... → Response
```

**3. Medallion:**
```
Sources → Bronze (raw) → Silver (clean) → Gold (business) → Consumers
```

**4. MLOps:**
```
Develop → Test → Register → Deploy → Monitor → Retrain
```

## Power Phrases for the Interview

| Topic | Power Phrase |
|-------|-------------|
| **Agent design** | "I use defense in depth — input validation, output guardrails, and human-in-the-loop for high-stakes actions" |
| **Data quality** | "The model is only as good as the data. I invest 60% of project time in data understanding and feature engineering" |
| **Cost** | "I tier models by query complexity — GPT-3.5 for simple lookups, GPT-4 for reasoning tasks. This cut our LLM costs by 60%" |
| **Evaluation** | "I build automated eval suites that run in CI/CD. Every prompt change gets regression tested" |
| **Production** | "I design for failure — retry logic, fallback models, circuit breakers, and graceful degradation" |
| **MCP** | "MCP standardizes how agents access data — build once, connect from any AI application" |
| **Penske-specific** | "Logistics is perfect for AI — route optimization, delay prediction, fleet maintenance, and knowledge management all benefit from the agent + ML combination" |

## Questions to Ask THEM

1. "What does the current AI/ML stack look like at Penske? Are you already on Azure + Snowflake + Databricks?"
2. "What are the first 1-2 agent use cases you'd want me to tackle?"
3. "How does the data science team interact with engineering and operations?"
4. "What's the current state of MLOps maturity? Is there an existing model deployment pipeline?"
5. "How do you measure success for AI projects — what KPIs matter most?"

---

> **You've got this. You know the tech, you have the examples, and you can articulate your decisions. Go crush it.**
