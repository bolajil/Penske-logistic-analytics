# ML Decision Guide
## Choosing the Right Machine Learning Approach

> **Purpose**: Help you determine which ML paradigm, algorithm, and cloud service to use based on your problem
> **Usage**: Answer the questions below to get a recommended approach and ready-to-use configuration

---

## Table of Contents
1. [Quick Decision Flowchart](#1-quick-decision-flowchart)
2. [Problem Type Identification](#2-problem-type-identification)
3. [Learning Paradigm Selection](#3-learning-paradigm-selection)
4. [Algorithm Selection](#4-algorithm-selection)
5. [GenAI vs Traditional ML](#5-genai-vs-traditional-ml)
6. [Ready-to-Use Configurations](#6-ready-to-use-configurations)

---

## 1. Quick Decision Flowchart

```
START: What is your goal?
│
├─► "Predict a NUMBER (price, time, quantity)"
│   └─► REGRESSION → Go to Section 4.1
│
├─► "Predict a CATEGORY (yes/no, type A/B/C)"
│   └─► CLASSIFICATION → Go to Section 4.2
│
├─► "Find PATTERNS or GROUPS in data (no labels)"
│   └─► UNSUPERVISED LEARNING → Go to Section 3.2
│
├─► "Generate TEXT, images, or have conversations"
│   └─► GENERATIVE AI → Go to Section 5
│
├─► "Make SEQUENTIAL DECISIONS (games, robots, optimization)"
│   └─► REINFORCEMENT LEARNING → Go to Section 3.4
│
├─► "Have SOME labeled data but mostly unlabeled"
│   └─► SEMI-SUPERVISED LEARNING → Go to Section 3.3
│
└─► "Detect UNUSUAL events or fraud"
    └─► ANOMALY DETECTION → Go to Section 4.5
```

---

## 2. Problem Type Identification

### 2.1 Answer These Questions

| Question | Your Answer | Points To |
|----------|-------------|-----------|
| Do you have labeled data (known correct answers)? | Yes → Supervised | No → Unsupervised/GenAI |
| Is your target a number or category? | Number → Regression | Category → Classification |
| Do you need to generate new content? | Yes → GenAI | No → Traditional ML |
| Is the output a sequence of actions? | Yes → Reinforcement Learning | No → Standard ML |
| Do you need real-time predictions? | Yes → Online Learning | No → Batch Learning |

### 2.2 Problem Type Examples

| Problem Description | Type | Paradigm | Recommended Approach |
|---------------------|------|----------|---------------------|
| Predict delivery time in hours | Regression | Supervised | XGBoost, Neural Network |
| Classify customer churn (yes/no) | Binary Classification | Supervised | Random Forest, Logistic Regression |
| Categorize support tickets by department | Multi-class Classification | Supervised | BERT, Gradient Boosting |
| Segment customers into groups | Clustering | Unsupervised | K-Means, DBSCAN |
| Detect fraudulent transactions | Anomaly Detection | Unsupervised/Supervised | Isolation Forest, Autoencoders |
| Answer questions from documents | Question Answering | GenAI | RAG with LLM |
| Summarize long reports | Text Summarization | GenAI | LLM (Claude, GPT-4, Gemini) |
| Optimize warehouse robot paths | Sequential Decision | Reinforcement Learning | PPO, DQN |
| Recommend products to users | Recommendation | Collaborative Filtering | Matrix Factorization, Deep Learning |
| Predict next word/token | Language Modeling | Self-Supervised | Transformers (GPT, BERT) |

---

## 3. Learning Paradigm Selection

### 3.1 Supervised Learning
**Use when**: You have labeled data (input-output pairs)

```
┌─────────────────────────────────────────────────────────────────┐
│ SUPERVISED LEARNING                                              │
├─────────────────────────────────────────────────────────────────┤
│ ✅ Best for:                                                     │
│    • Predicting specific outcomes                                │
│    • When you have historical data with known results            │
│    • Classification and regression problems                      │
│                                                                  │
│ ❌ Not suitable when:                                            │
│    • You don't have labeled data                                 │
│    • Labels are expensive/impossible to obtain                   │
│    • You need to discover hidden patterns                        │
│                                                                  │
│ 📊 Data requirements:                                            │
│    • Minimum: 100-1000 samples per class                         │
│    • Ideal: 10,000+ samples                                      │
│    • Must have target/label column                               │
└─────────────────────────────────────────────────────────────────┘
```

**Config setting:**
```yaml
model:
  paradigm: "supervised"
  task: "regression"  # or "classification"
```

### 3.2 Unsupervised Learning
**Use when**: You want to discover patterns without predefined labels

```
┌─────────────────────────────────────────────────────────────────┐
│ UNSUPERVISED LEARNING                                            │
├─────────────────────────────────────────────────────────────────┤
│ ✅ Best for:                                                     │
│    • Customer segmentation                                       │
│    • Anomaly/fraud detection                                     │
│    • Dimensionality reduction                                    │
│    • Finding hidden patterns                                     │
│                                                                  │
│ ❌ Not suitable when:                                            │
│    • You need specific predictions                               │
│    • You know what categories exist                              │
│    • Accuracy metrics are critical                               │
│                                                                  │
│ 📊 Data requirements:                                            │
│    • No labels needed                                            │
│    • More data = better patterns                                 │
│    • Feature engineering is critical                             │
└─────────────────────────────────────────────────────────────────┘
```

**Types of Unsupervised Learning:**

| Type | Use Case | Algorithms | Cloud Service |
|------|----------|------------|---------------|
| **Clustering** | Group similar items | K-Means, DBSCAN, Hierarchical | SageMaker, Vertex AI |
| **Dimensionality Reduction** | Reduce features, visualization | PCA, t-SNE, UMAP | All clouds |
| **Anomaly Detection** | Find outliers, fraud | Isolation Forest, One-Class SVM | SageMaker (Random Cut Forest) |
| **Association** | Market basket analysis | Apriori, FP-Growth | Custom implementation |

**Config setting:**
```yaml
model:
  paradigm: "unsupervised"
  task: "clustering"  # or "anomaly_detection", "dimensionality_reduction"
  algorithm: "kmeans"
  hyperparameters:
    n_clusters: 5
```

### 3.3 Semi-Supervised Learning
**Use when**: You have some labeled data but mostly unlabeled

```
┌─────────────────────────────────────────────────────────────────┐
│ SEMI-SUPERVISED LEARNING                                         │
├─────────────────────────────────────────────────────────────────┤
│ ✅ Best for:                                                     │
│    • Expensive labeling (medical images, legal documents)        │
│    • Large unlabeled datasets with few labels                    │
│    • Improving model with additional unlabeled data              │
│                                                                  │
│ ❌ Not suitable when:                                            │
│    • You have plenty of labeled data                             │
│    • Unlabeled data is low quality                               │
│    • Problem is simple enough for supervised                     │
│                                                                  │
│ 📊 Data requirements:                                            │
│    • Small labeled set (100-1000 samples)                        │
│    • Large unlabeled set (10,000+ samples)                       │
│    • Same distribution for both sets                             │
└─────────────────────────────────────────────────────────────────┘
```

**Approaches:**

| Technique | Description | When to Use |
|-----------|-------------|-------------|
| **Self-Training** | Train on labeled, predict unlabeled, add confident predictions | Simple, good baseline |
| **Label Propagation** | Spread labels through similar samples | Graph-structured data |
| **Co-Training** | Multiple models teach each other | Multiple feature views |
| **Pseudo-Labeling** | Use model predictions as soft labels | Deep learning |

**Config setting:**
```yaml
model:
  paradigm: "semi_supervised"
  technique: "self_training"
  base_algorithm: "gradient_boosting"
  confidence_threshold: 0.95
```

### 3.4 Reinforcement Learning
**Use when**: Agent learns by interacting with environment

```
┌─────────────────────────────────────────────────────────────────┐
│ REINFORCEMENT LEARNING                                           │
├─────────────────────────────────────────────────────────────────┤
│ ✅ Best for:                                                     │
│    • Game playing, robotics                                      │
│    • Resource optimization                                       │
│    • Dynamic pricing                                             │
│    • Recommendation systems                                      │
│                                                                  │
│ ❌ Not suitable when:                                            │
│    • You have direct input-output mappings                       │
│    • Environment simulation is impossible                        │
│    • Quick training is required                                  │
│                                                                  │
│ 📊 Requirements:                                                 │
│    • Environment to interact with                                │
│    • Reward signal definition                                    │
│    • Many iterations (millions of steps)                         │
└─────────────────────────────────────────────────────────────────┘
```

**Config setting:**
```yaml
model:
  paradigm: "reinforcement_learning"
  algorithm: "ppo"  # or "dqn", "a3c", "sac"
  hyperparameters:
    learning_rate: 0.0003
    gamma: 0.99
    episodes: 10000
```

---

## 4. Algorithm Selection

### 4.1 Regression Algorithms

**Decision Tree for Regression:**

```
START: Regression Problem
│
├─► Data size < 10,000 rows?
│   ├─► Yes → Try Random Forest or Gradient Boosting
│   └─► No → Continue
│
├─► Need interpretability?
│   ├─► Yes → Linear Regression, Decision Tree, or SHAP with any model
│   └─► No → Continue
│
├─► Has complex non-linear patterns?
│   ├─► Yes → XGBoost, LightGBM, or Neural Network
│   └─► No → Start with Linear Regression
│
├─► Time series data?
│   ├─► Yes → ARIMA, Prophet, or LSTM
│   └─► No → Standard regression
│
└─► Tabular data with mixed features?
    └─► XGBoost or CatBoost (handles categorical well)
```

| Algorithm | Best For | Pros | Cons | Config |
|-----------|----------|------|------|--------|
| **Linear Regression** | Simple relationships, baseline | Fast, interpretable | Can't capture non-linear | `algorithm: "linear"` |
| **Random Forest** | Medium datasets, robustness | Handles outliers, no tuning | Memory intensive | `algorithm: "random_forest"` |
| **XGBoost** | Tabular data, competitions | High accuracy, handles missing | Overfitting risk | `algorithm: "xgboost"` |
| **LightGBM** | Large datasets, speed | Fastest, memory efficient | Less accurate on small data | `algorithm: "lightgbm"` |
| **Neural Network** | Complex patterns, images | Learns features, flexible | Needs lots of data | `algorithm: "neural_network"` |

### 4.2 Classification Algorithms

**Decision Tree for Classification:**

```
START: Classification Problem
│
├─► Binary (2 classes) or Multi-class?
│   ├─► Binary → Logistic Regression baseline, then XGBoost
│   └─► Multi-class (3+) → Random Forest, XGBoost, or Neural Net
│
├─► Text data?
│   ├─► Yes → BERT, DistilBERT, or fine-tuned LLM
│   └─► No → Continue
│
├─► Image data?
│   ├─► Yes → CNN (ResNet, EfficientNet) or Vision Transformer
│   └─► No → Continue
│
├─► Imbalanced classes?
│   ├─► Yes → Use SMOTE, class weights, or Focal Loss
│   └─► No → Standard approach
│
└─► Need probability scores?
    ├─► Yes → Ensure model supports predict_proba
    └─► No → Any classifier works
```

| Algorithm | Best For | Handles Imbalance | Interpretable | Config |
|-----------|----------|-------------------|---------------|--------|
| **Logistic Regression** | Binary, baseline | With weights | High | `algorithm: "logistic"` |
| **Random Forest** | General purpose | With weights | Medium | `algorithm: "random_forest"` |
| **XGBoost** | Tabular, accuracy | With scale_pos_weight | Low | `algorithm: "xgboost"` |
| **SVM** | High-dim, margins | Limited | Low | `algorithm: "svm"` |
| **Neural Network** | Complex, unstructured | With weights | Low | `algorithm: "neural_network"` |

### 4.3 Clustering Algorithms

| Algorithm | Best For | Cluster Shape | Needs K? | Config |
|-----------|----------|---------------|----------|--------|
| **K-Means** | Spherical clusters, fast | Spherical | Yes | `algorithm: "kmeans"` |
| **DBSCAN** | Arbitrary shapes, outliers | Any | No | `algorithm: "dbscan"` |
| **Hierarchical** | Dendrograms, small data | Any | No | `algorithm: "hierarchical"` |
| **Gaussian Mixture** | Soft clustering, elliptical | Elliptical | Yes | `algorithm: "gmm"` |

### 4.4 Dimensionality Reduction

| Algorithm | Best For | Preserves | Linear? | Config |
|-----------|----------|-----------|---------|--------|
| **PCA** | Feature reduction, speed | Variance | Yes | `algorithm: "pca"` |
| **t-SNE** | Visualization (2D/3D) | Local structure | No | `algorithm: "tsne"` |
| **UMAP** | Visualization + clustering | Global + local | No | `algorithm: "umap"` |
| **Autoencoders** | Complex reduction | Learned features | No | `algorithm: "autoencoder"` |

### 4.5 Anomaly Detection

| Algorithm | Best For | Supervision | Config |
|-----------|----------|-------------|--------|
| **Isolation Forest** | General anomalies | Unsupervised | `algorithm: "isolation_forest"` |
| **One-Class SVM** | Known normal class | Semi-supervised | `algorithm: "one_class_svm"` |
| **Autoencoder** | Complex patterns | Unsupervised | `algorithm: "autoencoder"` |
| **Random Cut Forest** | Streaming data (AWS) | Unsupervised | `algorithm: "rcf"` |

---

## 5. GenAI vs Traditional ML

### 5.1 Decision Framework

```
┌─────────────────────────────────────────────────────────────────┐
│ WHEN TO USE TRADITIONAL ML                                       │
├─────────────────────────────────────────────────────────────────┤
│ ✅ Use Traditional ML when:                                      │
│    • You have structured/tabular data                            │
│    • Predictions need to be numeric or categorical               │
│    • Speed and cost are critical (inference)                     │
│    • You need explainability for compliance                      │
│    • Data is sensitive and can't leave your environment          │
│                                                                  │
│ Examples:                                                        │
│    • Predict delivery time: 2.5 hours                            │
│    • Classify fraud: Yes/No                                      │
│    • Segment customers: Group A, B, C                            │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ WHEN TO USE GENERATIVE AI                                        │
├─────────────────────────────────────────────────────────────────┤
│ ✅ Use GenAI when:                                               │
│    • You need to generate text, code, or content                 │
│    • Task requires understanding/reasoning                       │
│    • Building conversational interfaces                          │
│    • Summarizing or extracting from documents                    │
│    • Few-shot or zero-shot learning (no training data)           │
│                                                                  │
│ Examples:                                                        │
│    • "Why was this delivery delayed?" → Explanation              │
│    • "Summarize this report" → Summary text                      │
│    • "Answer questions from our docs" → RAG                      │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 Comparison Table

| Criteria | Traditional ML | Generative AI |
|----------|----------------|---------------|
| **Output** | Numbers, categories | Text, images, code |
| **Training** | Requires your data | Pre-trained, fine-tune optional |
| **Cost** | Low inference cost | Higher per-request cost |
| **Latency** | Milliseconds | Seconds |
| **Explainability** | High (SHAP, LIME) | Lower (black box) |
| **Data needs** | 1000s of examples | Few/zero examples |
| **Best for** | Structured predictions | Unstructured generation |

### 5.3 Hybrid Approaches

Sometimes you need **both**:

```
┌─────────────────────────────────────────────────────────────────┐
│ HYBRID: ML + GenAI                                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  [User Query] → [Intent Classification (ML)] → [Route]          │
│                           │                        │             │
│                           ↓                        ↓             │
│                    Structured Query           Open-ended         │
│                           │                        │             │
│                           ↓                        ↓             │
│                    [ML Prediction]          [LLM Response]       │
│                           │                        │             │
│                           ↓                        ↓             │
│              "Delivery: 2.5 hours"    "Based on traffic..."     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Config for Hybrid:**
```yaml
model:
  primary: "ml"  # Main prediction
  enhancement: "genai"  # Explain results
  
  ml:
    paradigm: "supervised"
    task: "regression"
    algorithm: "xgboost"
  
  genai:
    use_for: "explanation"
    model: "claude-3-sonnet"
    prompt_template: "Explain why the prediction is {prediction} given {features}"
```

---

## 6. Ready-to-Use Configurations

### 6.1 Regression Configuration

**Use when**: Predicting continuous values (time, price, quantity)

```yaml
# config/regression_config.yaml
model:
  paradigm: "supervised"
  task: "regression"
  algorithm: "xgboost"  # Options: linear, random_forest, xgboost, lightgbm, neural_network
  
  hyperparameters:
    # XGBoost specific
    n_estimators: 100
    max_depth: 6
    learning_rate: 0.1
    subsample: 0.8
    colsample_bytree: 0.8
    
  # Metrics to track
  metrics:
    - rmse
    - mae
    - r2

data:
  target_column: "delivery_time_hours"  # ← CHANGE: Your target
  feature_columns:
    - "distance_miles"
    - "weight_kg"
    - "hour"
    - "day_of_week"
```

### 6.2 Binary Classification Configuration

**Use when**: Predicting yes/no, true/false, 0/1

```yaml
# config/binary_classification_config.yaml
model:
  paradigm: "supervised"
  task: "classification"
  classification_type: "binary"
  algorithm: "xgboost"
  
  hyperparameters:
    n_estimators: 100
    max_depth: 6
    learning_rate: 0.1
    scale_pos_weight: 1  # Increase if positive class is rare
    
  metrics:
    - accuracy
    - precision
    - recall
    - f1
    - auc_roc

data:
  target_column: "is_delayed"  # ← CHANGE: Your target (0 or 1)
  positive_class: 1
```

### 6.3 Multi-Class Classification Configuration

**Use when**: Predicting one of 3+ categories

```yaml
# config/multiclass_config.yaml
model:
  paradigm: "supervised"
  task: "classification"
  classification_type: "multiclass"
  algorithm: "random_forest"
  
  hyperparameters:
    n_estimators: 200
    max_depth: 10
    class_weight: "balanced"  # Handle imbalance
    
  metrics:
    - accuracy
    - f1_macro
    - confusion_matrix

data:
  target_column: "delay_reason"  # ← CHANGE: Categories like "traffic", "weather", "other"
  classes:
    - "traffic"
    - "weather"
    - "mechanical"
    - "other"
```

### 6.4 Clustering Configuration

**Use when**: Grouping similar items without predefined labels

```yaml
# config/clustering_config.yaml
model:
  paradigm: "unsupervised"
  task: "clustering"
  algorithm: "kmeans"  # Options: kmeans, dbscan, hierarchical, gmm
  
  hyperparameters:
    # K-Means
    n_clusters: 5  # Use elbow method to determine
    init: "k-means++"
    n_init: 10
    max_iter: 300
    
    # DBSCAN (if using)
    # eps: 0.5
    # min_samples: 5
    
  metrics:
    - silhouette_score
    - calinski_harabasz
    - davies_bouldin

data:
  feature_columns:
    - "order_frequency"
    - "avg_order_value"
    - "days_since_last_order"
  
  # No target column for unsupervised!
```

### 6.5 Anomaly Detection Configuration

**Use when**: Finding outliers, fraud, unusual patterns

```yaml
# config/anomaly_detection_config.yaml
model:
  paradigm: "unsupervised"  # or "semi_supervised" if you have labeled anomalies
  task: "anomaly_detection"
  algorithm: "isolation_forest"  # Options: isolation_forest, one_class_svm, autoencoder
  
  hyperparameters:
    contamination: 0.01  # Expected proportion of anomalies (1%)
    n_estimators: 100
    max_samples: "auto"
    
  metrics:
    - precision_at_k
    - recall_at_k
    - auc_roc  # If you have labeled anomalies for evaluation

data:
  feature_columns:
    - "transaction_amount"
    - "time_since_last_transaction"
    - "distance_from_usual_location"
  
  # Optional: labeled anomalies for evaluation
  anomaly_column: "is_fraud"  # Optional
```

### 6.6 Time Series Forecasting Configuration

**Use when**: Predicting future values based on historical patterns

```yaml
# config/time_series_config.yaml
model:
  paradigm: "supervised"
  task: "forecasting"
  algorithm: "prophet"  # Options: arima, prophet, lstm, transformer
  
  hyperparameters:
    # Prophet
    seasonality_mode: "multiplicative"
    yearly_seasonality: true
    weekly_seasonality: true
    daily_seasonality: false
    
    # LSTM (if using)
    # sequence_length: 30
    # hidden_units: 64
    # layers: 2
    
  forecast_horizon: 7  # Days ahead to predict
  
  metrics:
    - mape
    - rmse
    - mae

data:
  date_column: "date"
  target_column: "daily_deliveries"
  
  # Optional external regressors
  external_features:
    - "is_holiday"
    - "weather_score"
```

### 6.7 Generative AI Configuration

**Use when**: Generating text, answering questions, summarizing

```yaml
# config/genai_config.yaml
model:
  paradigm: "genai"
  task: "text_generation"  # Options: text_generation, qa, summarization, embedding
  
  provider: "aws"  # Options: aws, azure, gcp
  model_id: "anthropic.claude-3-sonnet-20240229-v1:0"
  
  # Model parameters
  max_tokens: 1024
  temperature: 0.7
  top_p: 0.9
  
  # System prompt
  system_prompt: |
    You are a logistics analytics assistant. 
    Provide clear, data-driven insights about delivery operations.
    Always cite specific metrics when available.

# RAG configuration (if using knowledge base)
rag:
  enabled: true
  knowledge_base_id: "your-kb-id"
  chunk_size: 512
  top_k: 5

# For embeddings
embeddings:
  model_id: "amazon.titan-embed-text-v1"
  dimensions: 1536
```

### 6.8 Semi-Supervised Configuration

**Use when**: You have few labels but lots of unlabeled data

```yaml
# config/semi_supervised_config.yaml
model:
  paradigm: "semi_supervised"
  task: "classification"
  technique: "self_training"  # Options: self_training, label_propagation, pseudo_labeling
  
  base_algorithm: "gradient_boosting"
  
  hyperparameters:
    # Self-training specific
    confidence_threshold: 0.95
    max_iterations: 10
    
    # Base model
    n_estimators: 100
    max_depth: 6

data:
  target_column: "category"
  labeled_ratio: 0.1  # 10% of data is labeled
  
  # Labeled samples have target values
  # Unlabeled samples have target = null or -1
```

### 6.9 Reinforcement Learning Configuration

**Use when**: Learning through trial and error with rewards

```yaml
# config/reinforcement_learning_config.yaml
model:
  paradigm: "reinforcement_learning"
  algorithm: "ppo"  # Options: ppo, dqn, a3c, sac, ddpg
  
  hyperparameters:
    learning_rate: 0.0003
    gamma: 0.99  # Discount factor
    gae_lambda: 0.95
    clip_range: 0.2
    n_epochs: 10
    batch_size: 64
    
  training:
    total_timesteps: 1000000
    eval_frequency: 10000
    save_frequency: 50000

environment:
  name: "warehouse_routing"  # Custom environment
  observation_space: "continuous"
  action_space: "discrete"
  reward_function: "minimize_distance"
```

---

## 7. Quick Reference Decision Matrix

| I want to... | Paradigm | Task | Algorithm | GenAI? |
|--------------|----------|------|-----------|--------|
| Predict a number | Supervised | Regression | XGBoost | No |
| Classify into categories | Supervised | Classification | Random Forest | No |
| Group similar items | Unsupervised | Clustering | K-Means | No |
| Find outliers/fraud | Unsupervised | Anomaly Detection | Isolation Forest | No |
| Predict future values | Supervised | Forecasting | Prophet/LSTM | No |
| Answer questions | GenAI | QA/RAG | Claude/GPT | Yes |
| Generate text/reports | GenAI | Generation | Claude/GPT | Yes |
| Summarize documents | GenAI | Summarization | Claude/GPT | Yes |
| Optimize decisions | RL | Sequential | PPO/DQN | No |
| Work with few labels | Semi-Supervised | Classification | Self-Training | No |

---

## 8. Cloud Service Mapping

| Task | AWS | Azure | GCP |
|------|-----|-------|-----|
| **AutoML (any)** | SageMaker Autopilot | Azure AutoML | Vertex AI AutoML |
| **XGBoost** | SageMaker Built-in | Azure ML | Vertex AI Custom |
| **Deep Learning** | SageMaker (PyTorch/TF) | Azure ML | Vertex AI |
| **Time Series** | SageMaker DeepAR | Azure AutoML | Vertex AI Forecasting |
| **Anomaly Detection** | SageMaker RCF | Azure Anomaly Detector | Vertex AI |
| **Text Generation** | Bedrock (Claude) | Azure OpenAI | Gemini |
| **Embeddings** | Bedrock Titan | Azure OpenAI | Vertex AI Embeddings |
| **RAG** | Bedrock Knowledge Base | Azure AI Search + OpenAI | Vertex AI Search |
| **Clustering** | SageMaker K-Means | Azure ML | BigQuery ML |

---

*Last Updated: January 2024*
*Author: Penske Logistics Analytics Team*
