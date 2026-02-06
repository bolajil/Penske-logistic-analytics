# Machine Learning Algorithms - Educational Reference Guide

A comprehensive guide to machine learning algorithms, covering both the algorithms used in this project and other commonly referenced algorithms in the field.

---

## Table of Contents

1. [Algorithms Used in This Project](#algorithms-used-in-this-project)
   - [XGBoost](#1-xgboost-extreme-gradient-boosting)
   - [Gradient Boosting](#2-gradient-boosting)
   - [Random Forest](#3-random-forest)
   - [K-Means Clustering](#4-k-means-clustering)
2. [Other Common ML Algorithms](#other-common-ml-algorithms)
   - [KNN](#5-knn-k-nearest-neighbors)
   - [Linear Regression](#6-linear-regression)
   - [Logistic Regression](#7-logistic-regression)
3. [Deep Learning Algorithms](#deep-learning-algorithms)
   - [CNN](#8-cnn-convolutional-neural-network)
   - [RNN](#9-rnn-recurrent-neural-network)
   - [LSTM](#10-lstm-long-short-term-memory)
   - [GRU](#11-gru-gated-recurrent-unit)
   - [Transformers](#12-transformers)
4. [Generative Models](#generative-models)
   - [GANs](#13-gans-generative-adversarial-networks)
   - [VAE](#14-vae-variational-autoencoder)
5. [Algorithm Selection Guide](#algorithm-selection-guide)
6. [Glossary of Terms](#glossary-of-terms)

---

## Algorithms Used in This Project

### 1. XGBoost (eXtreme Gradient Boosting)

**Full Name:** eXtreme Gradient Boosting

**Category:** Supervised Learning → Ensemble Method → Boosting

#### What It Is
- A highly optimized implementation of gradient boosting
- Builds multiple decision trees sequentially
- Each new tree corrects the errors made by previous trees
- Uses gradient descent optimization to minimize prediction errors

#### How It Works
1. **Initialize** with a simple prediction (e.g., mean of target values)
2. **Calculate residuals** (errors) between predictions and actual values
3. **Build a new tree** to predict these residuals
4. **Add the new tree** to the ensemble with a learning rate
5. **Repeat** until stopping criteria met (max trees or no improvement)

#### Key Parameters
- **n_estimators:** Number of trees to build (e.g., 100-500)
- **max_depth:** Maximum depth of each tree (e.g., 3-10)
- **learning_rate:** Step size for updates (e.g., 0.01-0.3)
- **subsample:** Fraction of data used per tree (e.g., 0.8)
- **colsample_bytree:** Fraction of features used per tree (e.g., 0.8)

#### Example Use Case in This Project
```python
# From src/resource_prediction.py - Demand Forecasting
model = xgb.XGBRegressor(
    n_estimators=200,      # Build 200 trees
    max_depth=6,           # Each tree has max 6 levels
    learning_rate=0.1,     # Conservative learning rate
    subsample=0.8,         # Use 80% of data per tree
    colsample_bytree=0.8,  # Use 80% of features per tree
    random_state=42        # For reproducibility
)
model.fit(X_train, y_train)
predictions = model.predict(X_test)
```

#### Strengths
- Excellent performance on tabular/structured data
- Handles missing values automatically
- Built-in regularization prevents overfitting
- Fast training with parallel processing
- Provides feature importance scores

#### Weaknesses
- Can overfit on small datasets
- Many hyperparameters to tune
- Not ideal for image or text data
- "Black box" - less interpretable than linear models

#### When to Use
- Structured/tabular data (spreadsheets, databases)
- Classification or regression problems
- When accuracy is priority over interpretability
- Kaggle competitions (frequently wins)

---

### 2. Gradient Boosting

**Full Name:** Gradient Boosting Machine (GBM)

**Category:** Supervised Learning → Ensemble Method → Boosting

#### What It Is
- An ensemble learning technique that combines weak learners (usually decision trees)
- "Gradient" refers to using gradient descent to minimize loss
- "Boosting" means trees are built sequentially, each improving on the last

#### How It Works
1. **Start** with initial prediction (often the mean)
2. **Compute gradient** of loss function (direction of steepest improvement)
3. **Fit a tree** to predict the negative gradient (pseudo-residuals)
4. **Update predictions** by adding the new tree's output × learning rate
5. **Iterate** until convergence or max iterations

#### Mathematical Concept
```
Prediction(i+1) = Prediction(i) + learning_rate × Tree(i)

Where Tree(i) is trained to predict: -∂Loss/∂Prediction
```

#### Example Use Case in This Project
```python
# From src/customer_acquisition.py - Churn Prediction
from sklearn.ensemble import GradientBoostingClassifier

model = GradientBoostingClassifier(
    n_estimators=100,     # 100 sequential trees
    max_depth=4,          # Shallow trees (less overfitting)
    learning_rate=0.1,    # Small steps for stability
    random_state=42
)
model.fit(X_train, y_train)
churn_probability = model.predict_proba(X_test)[:, 1]
```

#### Difference from XGBoost
| Aspect | Gradient Boosting (sklearn) | XGBoost |
|--------|----------------------------|---------|
| Speed | Slower | 10x faster |
| Regularization | Basic | Advanced (L1, L2) |
| Missing Values | Must handle manually | Automatic |
| Parallel | No | Yes |

#### Strengths
- Strong predictive accuracy
- Handles non-linear relationships
- Works with mixed data types
- Standard library (no extra install)

#### Weaknesses
- Slower than XGBoost
- Sequential training (can't parallelize)
- Sensitive to noisy data
- Prone to overfitting without tuning

---

### 3. Random Forest

**Full Name:** Random Forest

**Category:** Supervised Learning → Ensemble Method → Bagging

#### What It Is
- An ensemble of decision trees trained independently
- "Random" because each tree sees random data subsets and features
- "Forest" because it combines many trees (typically 100-500)
- Final prediction = average (regression) or majority vote (classification)

#### How It Works
1. **Bootstrap sampling:** Create N random samples from training data (with replacement)
2. **Random feature selection:** At each split, consider only random subset of features
3. **Build N trees:** Each tree trained on different bootstrap sample
4. **Aggregate predictions:**
   - Regression: Average all tree predictions
   - Classification: Majority vote across trees

#### Key Parameters
- **n_estimators:** Number of trees (100-500 typical)
- **max_depth:** Maximum depth per tree (None = unlimited)
- **min_samples_split:** Minimum samples required to split a node
- **max_features:** Number of features to consider at each split
- **n_jobs:** Number of CPU cores for parallel training (-1 = all)

#### Example Use Case in This Project
```python
# From src/resource_prediction.py - Alternative Demand Model
from sklearn.ensemble import RandomForestRegressor

model = RandomForestRegressor(
    n_estimators=200,      # 200 independent trees
    max_depth=10,          # Limit tree depth
    min_samples_split=5,   # Need 5 samples to split
    random_state=42,
    n_jobs=-1              # Use all CPU cores
)
model.fit(X_train, y_train)
predictions = model.predict(X_test)
```

#### Bagging vs. Boosting
| Bagging (Random Forest) | Boosting (XGBoost/GBM) |
|------------------------|----------------------|
| Trees built in **parallel** | Trees built **sequentially** |
| Each tree is **independent** | Each tree **corrects previous** |
| Reduces **variance** | Reduces **bias** |
| Less prone to overfitting | Can overfit if not tuned |

#### Strengths
- Robust to overfitting
- Handles high-dimensional data
- Provides feature importance
- Parallelizable (fast training)
- Works out-of-the-box with minimal tuning

#### Weaknesses
- Less accurate than boosting for many problems
- Large memory footprint (stores all trees)
- Slower inference than single model
- Can struggle with very sparse data

---

### 4. K-Means Clustering

**Full Name:** K-Means Clustering

**Category:** Unsupervised Learning → Clustering

#### What It Is
- Partitions data into K distinct, non-overlapping groups (clusters)
- "K" is the number of clusters (chosen by user)
- "Means" refers to cluster centers (centroids)
- Goal: Minimize distance between points and their cluster centroid

#### How It Works
1. **Initialize:** Randomly place K centroids in feature space
2. **Assign:** Assign each data point to nearest centroid
3. **Update:** Move each centroid to the mean of its assigned points
4. **Repeat:** Continue steps 2-3 until centroids stop moving

#### Visual Example
```
Step 1: Random centroids     Step 2: Assign points     Step 3: Update centroids
    ★                            ★                          ★
  • • •   •                    ●●●   ○                     ●●●   ○
    • •                          ●●                          ●●
         •  •                         ○  ○                        ○  ○
         ★                            ★                            ★
```

#### Key Parameters
- **n_clusters:** Number of clusters (K)
- **init:** Initialization method ('k-means++' recommended)
- **n_init:** Number of times to run with different seeds
- **max_iter:** Maximum iterations per run

#### Example Use Case in This Project
```python
# From src/customer_acquisition.py - Customer Segmentation
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Scale features (important for K-Means!)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(customer_features)

# Create segments
model = KMeans(
    n_clusters=5,         # Create 5 customer segments
    random_state=42,
    n_init=10             # Run 10 times, pick best
)
model.fit(X_scaled)
customer_segments = model.labels_  # 0, 1, 2, 3, or 4
```

#### Choosing K (Number of Clusters)
- **Elbow Method:** Plot inertia vs. K, look for "elbow"
- **Silhouette Score:** Measure how similar points are to own cluster vs. others
- **Business Logic:** Sometimes domain knowledge dictates K

#### Strengths
- Simple and intuitive
- Fast and scalable
- Works well with spherical clusters
- Easy to interpret results

#### Weaknesses
- Must specify K in advance
- Sensitive to initial centroid placement
- Assumes spherical clusters of similar size
- Affected by outliers
- Requires feature scaling

---

## Other Common ML Algorithms

### 5. KNN (K-Nearest Neighbors)

**Full Name:** K-Nearest Neighbors

**Category:** Supervised Learning → Instance-Based Learning

#### What It Is
- A "lazy learner" that doesn't build a model during training
- Makes predictions by finding K most similar training examples
- Classification: Majority vote of K neighbors
- Regression: Average of K neighbors

#### How It Works
1. **Store** all training data (no actual training)
2. **For each new point:**
   - Calculate distance to all training points
   - Find K closest neighbors
   - Aggregate their labels/values

#### Distance Metrics
- **Euclidean Distance:** √(Σ(x₁ - x₂)²) - straight line
- **Manhattan Distance:** Σ|x₁ - x₂| - city block
- **Minkowski Distance:** Generalization of above
- **Cosine Similarity:** For text/high-dimensional data

#### Example
```python
from sklearn.neighbors import KNeighborsClassifier

# Create and train KNN classifier
knn = KNeighborsClassifier(
    n_neighbors=5,           # Use 5 nearest neighbors
    weights='distance',      # Closer neighbors have more influence
    metric='euclidean'       # Distance calculation method
)
knn.fit(X_train, y_train)
predictions = knn.predict(X_test)
```

#### Strengths
- No training time (instant "learning")
- Naturally handles multi-class problems
- Non-parametric (no assumptions about data distribution)
- Can capture complex decision boundaries

#### Weaknesses
- Slow predictions (must scan all training data)
- Memory-intensive (stores all data)
- Sensitive to irrelevant features
- Requires feature scaling
- Curse of dimensionality in high dimensions

#### Why Not Used in This Project
- Large logistics datasets make prediction slow
- Tree-based models provide better accuracy
- Feature importance not available in KNN

---

### 6. Linear Regression

**Full Name:** Linear Regression (Ordinary Least Squares - OLS)

**Category:** Supervised Learning → Regression

#### What It Is
- Models relationship between features (X) and target (y) as a straight line
- Finds coefficients (weights) that minimize squared errors
- Simplest and most interpretable regression model

#### Mathematical Formula
```
y = β₀ + β₁x₁ + β₂x₂ + ... + βₙxₙ + ε

Where:
- y = predicted value
- β₀ = intercept (bias)
- β₁...βₙ = coefficients (weights)
- x₁...xₙ = features
- ε = error term
```

#### Example
```python
from sklearn.linear_model import LinearRegression

# Predict house price based on features
model = LinearRegression()
model.fit(X_train, y_train)

# Coefficients show feature importance
print(f"Intercept: {model.intercept_}")
print(f"Coefficients: {model.coef_}")

# Predict
predicted_price = model.predict([[3, 1500, 2]])  # bedrooms, sqft, baths
```

#### Variants
| Variant | Description |
|---------|-------------|
| **Ridge (L2)** | Adds penalty on large coefficients |
| **Lasso (L1)** | Can zero out irrelevant features |
| **Elastic Net** | Combines Ridge and Lasso |
| **Polynomial** | Captures non-linear relationships |

#### Strengths
- Highly interpretable (coefficients are meaningful)
- Fast training and prediction
- No hyperparameters to tune
- Baseline for comparison

#### Weaknesses
- Assumes linear relationship
- Sensitive to outliers
- Cannot capture complex patterns
- Assumes features are independent (multicollinearity issues)

---

### 7. Logistic Regression

**Full Name:** Logistic Regression

**Category:** Supervised Learning → Classification (despite the name!)

#### What It Is
- Classification algorithm (NOT regression despite the name)
- Predicts probability of belonging to a class
- Uses sigmoid function to map predictions to [0, 1]

#### Mathematical Formula
```
P(y=1) = 1 / (1 + e^(-(β₀ + β₁x₁ + β₂x₂ + ...)))

Sigmoid function: σ(z) = 1 / (1 + e^(-z))
```

#### Example
```python
from sklearn.linear_model import LogisticRegression

# Predict customer churn (yes/no)
model = LogisticRegression(
    penalty='l2',           # Regularization type
    C=1.0,                  # Regularization strength
    max_iter=1000
)
model.fit(X_train, y_train)

# Get probabilities
churn_probability = model.predict_proba(X_test)[:, 1]

# Get binary predictions
churn_prediction = model.predict(X_test)  # 0 or 1
```

#### Strengths
- Interpretable coefficients (log-odds)
- Outputs probabilities (not just class)
- Works well with linearly separable classes
- Fast and scalable

#### Weaknesses
- Assumes linear decision boundary
- Cannot capture complex relationships
- Requires feature engineering for non-linear patterns

---

## Deep Learning Algorithms

### 8. CNN (Convolutional Neural Network)

**Full Name:** Convolutional Neural Network

**Category:** Deep Learning → Computer Vision

#### What It Is
- Neural network designed for processing grid-like data (images)
- Uses convolution operations to detect patterns (edges, textures, shapes)
- Hierarchical: Early layers detect simple features, deeper layers detect complex ones

#### Key Components
- **Convolutional Layer:** Applies filters to detect features
- **Pooling Layer:** Reduces spatial dimensions (downsampling)
- **Activation (ReLU):** Introduces non-linearity: max(0, x)
- **Fully Connected Layer:** Final classification/regression
- **Dropout:** Regularization to prevent overfitting

#### Architecture Example
```
Input Image (224×224×3)
    ↓
Conv Layer (filters detect edges)
    ↓
MaxPooling (reduce size)
    ↓
Conv Layer (detect shapes)
    ↓
MaxPooling
    ↓
Flatten
    ↓
Dense Layer (512 neurons)
    ↓
Output (classification)
```

#### Example Code
```python
import tensorflow as tf

model = tf.keras.Sequential([
    # Convolutional layers
    tf.keras.layers.Conv2D(32, (3,3), activation='relu', input_shape=(224,224,3)),
    tf.keras.layers.MaxPooling2D((2,2)),
    tf.keras.layers.Conv2D(64, (3,3), activation='relu'),
    tf.keras.layers.MaxPooling2D((2,2)),
    tf.keras.layers.Conv2D(128, (3,3), activation='relu'),
    
    # Classification layers
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(512, activation='relu'),
    tf.keras.layers.Dropout(0.5),
    tf.keras.layers.Dense(10, activation='softmax')  # 10 classes
])
```

#### Use Cases
- Image classification (cats vs. dogs)
- Object detection (finding cars in photos)
- Medical imaging (tumor detection)
- Facial recognition

#### Why Not Used in This Project
- Our data is **tabular** (numbers in spreadsheets), not images
- CNNs are designed for spatial patterns in 2D/3D data

---

### 9. RNN (Recurrent Neural Network)

**Full Name:** Recurrent Neural Network

**Category:** Deep Learning → Sequence Processing

#### What It Is
- Neural network with "memory" - output depends on current input AND previous states
- Designed for sequential data where order matters
- Processes input one step at a time, maintaining hidden state

#### How It Works
```
h(t) = tanh(W_hh × h(t-1) + W_xh × x(t) + b)
y(t) = W_hy × h(t)

Where:
- h(t) = hidden state at time t
- x(t) = input at time t
- W = weight matrices
- b = bias
```

#### Visual Representation
```
    y₁        y₂        y₃        y₄
    ↑         ↑         ↑         ↑
   [h₁] →   [h₂] →   [h₃] →   [h₄]
    ↑         ↑         ↑         ↑
    x₁        x₂        x₃        x₄
  "The"    "cat"     "sat"     "down"
```

#### Example Code
```python
import tensorflow as tf

model = tf.keras.Sequential([
    tf.keras.layers.Embedding(vocab_size, 64),
    tf.keras.layers.SimpleRNN(128, return_sequences=True),
    tf.keras.layers.SimpleRNN(64),
    tf.keras.layers.Dense(1, activation='sigmoid')
])
```

#### Limitations
- **Vanishing Gradient Problem:** Gradients become tiny over long sequences
- Struggles to learn long-range dependencies
- Can't remember information from many steps ago

#### Use Cases
- Text generation
- Speech recognition
- Time series (short sequences)
- Language translation (basic)

---

### 10. LSTM (Long Short-Term Memory)

**Full Name:** Long Short-Term Memory

**Category:** Deep Learning → Sequence Processing

#### What It Is
- Advanced RNN architecture that solves the vanishing gradient problem
- Has special "gates" that control what information to remember or forget
- Can learn long-range dependencies in sequences

#### Key Components (Gates)
| Gate | Purpose | Function |
|------|---------|----------|
| **Forget Gate** | Decide what to discard | f(t) = σ(W_f · [h(t-1), x(t)] + b_f) |
| **Input Gate** | Decide what to add | i(t) = σ(W_i · [h(t-1), x(t)] + b_i) |
| **Output Gate** | Decide what to output | o(t) = σ(W_o · [h(t-1), x(t)] + b_o) |
| **Cell State** | Long-term memory | C(t) = f(t) × C(t-1) + i(t) × tanh(...) |

#### Visual Representation
```
         ┌─────────────────────────────────────┐
         │           Cell State (C)            │
         │    ×─────────+──────────────────────│→ C(t)
         │    ↑         ↑                      │
    ┌────│──(f)       (i)×(C̃)                 │
    │    │    │         │                      │
    │    └────│─────────│──────────────────────┘
    │         │         │              │
    │    ┌────┴─────────┴──────────────┴───────┐
    │    │      Forget    Input      Output    │
    │    │       Gate     Gate        Gate     │
    │    └─────────────────────────────────────┘
    │              ↑           ↑
    └──────────→ h(t-1)      x(t)
```

#### Example Code
```python
import tensorflow as tf

model = tf.keras.Sequential([
    tf.keras.layers.Embedding(vocab_size, 128),
    tf.keras.layers.LSTM(256, return_sequences=True),
    tf.keras.layers.LSTM(128),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dense(num_classes, activation='softmax')
])
```

#### Use Cases
- Machine translation
- Speech recognition
- Text generation
- Time series forecasting (complex patterns)
- Sentiment analysis

#### Why Not Used in This Project
- Overkill for our forecasting needs
- Requires large amounts of sequential data
- XGBoost with lag features achieves similar results with less complexity

---

### 11. GRU (Gated Recurrent Unit)

**Full Name:** Gated Recurrent Unit

**Category:** Deep Learning → Sequence Processing

#### What It Is
- Simplified version of LSTM
- Has fewer gates (2 vs. 3) → faster training
- Often performs similarly to LSTM with less computation

#### Key Differences from LSTM
| Aspect | LSTM | GRU |
|--------|------|-----|
| Gates | 3 (forget, input, output) | 2 (reset, update) |
| Cell State | Separate cell state | Combined with hidden state |
| Parameters | More | Fewer |
| Training Speed | Slower | Faster |

#### Gates in GRU
- **Reset Gate (r):** How much past information to forget
- **Update Gate (z):** How much past information to keep

#### Example Code
```python
import tensorflow as tf

model = tf.keras.Sequential([
    tf.keras.layers.Embedding(vocab_size, 128),
    tf.keras.layers.GRU(256, return_sequences=True),
    tf.keras.layers.GRU(128),
    tf.keras.layers.Dense(1, activation='sigmoid')
])
```

#### When to Choose GRU vs. LSTM
- **Use GRU when:** Faster training needed, smaller datasets, simpler sequences
- **Use LSTM when:** Very long sequences, more complex dependencies

---

### 12. Transformers

**Full Name:** Transformer Architecture

**Category:** Deep Learning → Attention-Based Models

#### What It Is
- Revolutionary architecture that replaced RNNs for many NLP tasks
- Uses "attention" mechanism instead of recurrence
- Processes entire sequence at once (parallelizable)
- Basis for GPT, BERT, and other large language models

#### Key Concept: Self-Attention
- Each word "attends" to all other words in the sequence
- Learns which words are relevant to each other
- No sequential processing → much faster training

#### Attention Formula
```
Attention(Q, K, V) = softmax(QK^T / √d_k) × V

Where:
- Q = Query matrix (what am I looking for?)
- K = Key matrix (what do I contain?)
- V = Value matrix (what do I offer?)
- d_k = dimension of keys (scaling factor)
```

#### Architecture Components
```
┌─────────────────────────────────────┐
│           Transformer               │
├──────────────────┬──────────────────┤
│     ENCODER      │     DECODER      │
├──────────────────┼──────────────────┤
│ Multi-Head       │ Masked Multi-    │
│ Self-Attention   │ Head Attention   │
│        ↓         │        ↓         │
│ Add & Normalize  │ Add & Normalize  │
│        ↓         │        ↓         │
│ Feed Forward     │ Cross-Attention  │
│        ↓         │        ↓         │
│ Add & Normalize  │ Feed Forward     │
│        ↓         │        ↓         │
│    (×N layers)   │    (×N layers)   │
└──────────────────┴──────────────────┘
```

#### Famous Transformer Models
| Model | Type | Use Case |
|-------|------|----------|
| **BERT** | Encoder only | Understanding text |
| **GPT** | Decoder only | Generating text |
| **T5** | Encoder-Decoder | Translation, summarization |
| **ViT** | Vision Transformer | Image classification |

#### Example (Using Hugging Face)
```python
from transformers import pipeline

# Sentiment analysis with pre-trained transformer
classifier = pipeline("sentiment-analysis")
result = classifier("I love this product!")
# Output: [{'label': 'POSITIVE', 'score': 0.9998}]

# Text generation with GPT-2
generator = pipeline("text-generation", model="gpt2")
result = generator("The future of AI is", max_length=50)
```

#### Why Not Used in This Project
- Designed for text/sequence data, not tabular logistics data
- Requires massive datasets and compute resources
- XGBoost is more appropriate for our structured data

---

## Generative Models

### 13. GANs (Generative Adversarial Networks)

**Full Name:** Generative Adversarial Network

**Category:** Deep Learning → Generative Models

#### What It Is
- Two neural networks competing against each other
- **Generator:** Creates fake data trying to fool the discriminator
- **Discriminator:** Tries to distinguish real data from fake
- Through competition, the generator learns to create realistic data

#### How It Works
```
Real Data ──────────────────────┐
                                ↓
                          [Discriminator] ─→ Real or Fake?
                                ↑
Random Noise → [Generator] ─────┘
                   ↑
              Feedback (improve to fool discriminator)
```

#### Training Process
1. **Train Discriminator:** Show real and fake data, learn to classify
2. **Train Generator:** Generate fake data, get feedback from discriminator
3. **Iterate:** Generator gets better at fooling, discriminator gets better at detecting
4. **Equilibrium:** Generator creates data indistinguishable from real

#### Example Applications
- Generating realistic faces (StyleGAN)
- Image-to-image translation (Pix2Pix)
- Creating artwork
- Data augmentation
- Super-resolution (enhancing image quality)

#### Example Code
```python
import tensorflow as tf

# Generator - creates fake images
generator = tf.keras.Sequential([
    tf.keras.layers.Dense(256, activation='relu', input_shape=(100,)),
    tf.keras.layers.Dense(512, activation='relu'),
    tf.keras.layers.Dense(28*28, activation='tanh'),
    tf.keras.layers.Reshape((28, 28, 1))
])

# Discriminator - classifies real vs fake
discriminator = tf.keras.Sequential([
    tf.keras.layers.Flatten(input_shape=(28, 28, 1)),
    tf.keras.layers.Dense(512, activation='relu'),
    tf.keras.layers.Dense(256, activation='relu'),
    tf.keras.layers.Dense(1, activation='sigmoid')
])
```

#### GAN Variants
| Variant | Purpose |
|---------|---------|
| **DCGAN** | Deep Convolutional GAN for images |
| **StyleGAN** | High-quality face generation |
| **CycleGAN** | Unpaired image translation |
| **Pix2Pix** | Paired image translation |
| **WGAN** | More stable training |

#### Why Not Used in This Project
- We need prediction, not generation
- Our task is forecasting and classification, not creating new data

---

### 14. VAE (Variational Autoencoder)

**Full Name:** Variational Autoencoder

**Category:** Deep Learning → Generative Models

#### What It Is
- Neural network that learns compressed representations of data
- Has encoder (compresses) and decoder (reconstructs)
- Can generate new data by sampling from learned distribution
- Combines autoencoders with probabilistic modeling

#### Key Components
- **Encoder:** Maps input to latent distribution (mean μ, variance σ)
- **Latent Space:** Compressed representation of data
- **Decoder:** Reconstructs data from latent space
- **Reparameterization Trick:** Enables backpropagation through sampling

#### Architecture
```
Input x ─→ [Encoder] ─→ μ, σ ─→ z = μ + σ×ε ─→ [Decoder] ─→ x̂ (reconstruction)
                                    ↑
                            ε ~ N(0,1) (random noise)
```

#### Loss Function
```
Loss = Reconstruction Loss + KL Divergence

- Reconstruction: How well decoder recreates input
- KL Divergence: Keeps latent space close to normal distribution
```

#### Example Code
```python
import tensorflow as tf

# Encoder
encoder_inputs = tf.keras.Input(shape=(28, 28, 1))
x = tf.keras.layers.Flatten()(encoder_inputs)
x = tf.keras.layers.Dense(256, activation='relu')(x)
z_mean = tf.keras.layers.Dense(latent_dim)(x)
z_log_var = tf.keras.layers.Dense(latent_dim)(x)

# Sampling layer
z = Sampling()([z_mean, z_log_var])

# Decoder
decoder_inputs = tf.keras.Input(shape=(latent_dim,))
x = tf.keras.layers.Dense(256, activation='relu')(decoder_inputs)
x = tf.keras.layers.Dense(28*28, activation='sigmoid')(x)
outputs = tf.keras.layers.Reshape((28, 28, 1))(x)
```

#### Use Cases
- Anomaly detection (unusual data has high reconstruction error)
- Data compression
- Generating variations of existing data
- Semi-supervised learning
- Image denoising

#### VAE vs. GAN
| Aspect | VAE | GAN |
|--------|-----|-----|
| Training | Stable | Can be unstable |
| Output Quality | Blurrier | Sharper |
| Latent Space | Structured, interpretable | Less structured |
| Mode Collapse | No | Possible |

#### Why Not Used in This Project
- We need prediction, not generation
- Anomaly detection could be useful, but simpler methods work for our data

---

## Algorithm Selection Guide

### Choosing the Right Algorithm

```
START: What type of problem?
       │
       ├─── Supervised (have labels)?
       │    ├─── Predict number? → REGRESSION
       │    │    ├─── Tabular data? → XGBoost, Random Forest, Gradient Boosting
       │    │    ├─── Time series? → LSTM, GRU, or XGBoost with lag features
       │    │    └─── Images? → CNN
       │    │
       │    └─── Predict category? → CLASSIFICATION
       │         ├─── Tabular data? → XGBoost, Random Forest, Logistic Regression
       │         ├─── Text? → Transformers (BERT), LSTM
       │         └─── Images? → CNN
       │
       ├─── Unsupervised (no labels)?
       │    ├─── Find groups? → K-Means, DBSCAN, Hierarchical
       │    ├─── Reduce dimensions? → PCA, t-SNE, UMAP
       │    └─── Detect anomalies? → Isolation Forest, VAE
       │
       └─── Generative (create new data)?
            ├─── Images? → GAN, VAE
            └─── Text? → GPT, Transformer Decoder
```

### Algorithm Comparison Matrix

| Algorithm | Data Type | Speed | Interpretability | Accuracy |
|-----------|-----------|-------|------------------|----------|
| XGBoost | Tabular | Fast | Medium | ⭐⭐⭐⭐⭐ |
| Random Forest | Tabular | Fast | Medium | ⭐⭐⭐⭐ |
| Gradient Boosting | Tabular | Medium | Medium | ⭐⭐⭐⭐⭐ |
| Linear/Logistic | Tabular | Very Fast | High | ⭐⭐⭐ |
| KNN | Tabular | Slow (predict) | High | ⭐⭐⭐ |
| K-Means | Tabular | Fast | High | N/A |
| CNN | Images | Slow | Low | ⭐⭐⭐⭐⭐ |
| LSTM/GRU | Sequences | Slow | Low | ⭐⭐⭐⭐ |
| Transformer | Text/Seq | Very Slow | Low | ⭐⭐⭐⭐⭐ |
| GAN | Images | Very Slow | Low | N/A |
| VAE | Any | Slow | Medium | N/A |

---

## Glossary of Terms

### General ML Terms

| Term | Full Form | Definition |
|------|-----------|------------|
| **ML** | Machine Learning | Algorithms that learn patterns from data |
| **DL** | Deep Learning | ML using neural networks with many layers |
| **AI** | Artificial Intelligence | Machines that simulate human intelligence |
| **NLP** | Natural Language Processing | ML for understanding human language |
| **CV** | Computer Vision | ML for understanding images/video |

### Training Terms

| Term | Full Form | Definition |
|------|-----------|------------|
| **SGD** | Stochastic Gradient Descent | Optimization algorithm using random samples |
| **Adam** | Adaptive Moment Estimation | Popular optimizer combining momentum + RMSprop |
| **RMSprop** | Root Mean Square Propagation | Optimizer with adaptive learning rates |
| **LR** | Learning Rate | Step size for weight updates |
| **Epoch** | - | One complete pass through training data |
| **Batch** | - | Subset of data processed together |

### Model Terms

| Term | Full Form | Definition |
|------|-----------|------------|
| **MLP** | Multi-Layer Perceptron | Basic fully-connected neural network |
| **FC** | Fully Connected | Layer where all neurons connect to all inputs |
| **ReLU** | Rectified Linear Unit | Activation function: max(0, x) |
| **Softmax** | - | Converts outputs to probabilities (sum to 1) |
| **Sigmoid** | - | Squashes output to range [0, 1] |
| **Tanh** | Hyperbolic Tangent | Squashes output to range [-1, 1] |

### Evaluation Metrics

| Term | Full Form | Definition |
|------|-----------|------------|
| **MAE** | Mean Absolute Error | Average of |actual - predicted| |
| **MSE** | Mean Squared Error | Average of (actual - predicted)² |
| **RMSE** | Root Mean Squared Error | √MSE |
| **MAPE** | Mean Absolute Percentage Error | Average of |error| / |actual| × 100 |
| **R²** | R-Squared | Proportion of variance explained |
| **AUC** | Area Under Curve | ROC curve area (classifier quality) |
| **ROC** | Receiver Operating Characteristic | Plot of TPR vs FPR at thresholds |
| **F1** | F1 Score | Harmonic mean of precision and recall |
| **TP** | True Positive | Correctly predicted positive |
| **TN** | True Negative | Correctly predicted negative |
| **FP** | False Positive | Incorrectly predicted positive (Type I) |
| **FN** | False Negative | Incorrectly predicted negative (Type II) |

### Neural Network Terms

| Term | Full Form | Definition |
|------|-----------|------------|
| **CNN** | Convolutional Neural Network | NN for spatial data (images) |
| **RNN** | Recurrent Neural Network | NN for sequential data |
| **LSTM** | Long Short-Term Memory | RNN variant with memory gates |
| **GRU** | Gated Recurrent Unit | Simplified LSTM |
| **GAN** | Generative Adversarial Network | Generator + Discriminator |
| **VAE** | Variational Autoencoder | Probabilistic autoencoder |
| **BERT** | Bidirectional Encoder Representations from Transformers | Pre-trained language model |
| **GPT** | Generative Pre-trained Transformer | Text generation model |

### Regularization Terms

| Term | Full Form | Definition |
|------|-----------|------------|
| **L1** | L1 Regularization (Lasso) | Penalty on |weights| |
| **L2** | L2 Regularization (Ridge) | Penalty on weights² |
| **Dropout** | - | Randomly disable neurons during training |
| **BN** | Batch Normalization | Normalize layer inputs |

### Data Terms

| Term | Full Form | Definition |
|------|-----------|------------|
| **OHE** | One-Hot Encoding | Convert categories to binary vectors |
| **PCA** | Principal Component Analysis | Dimensionality reduction technique |
| **SMOTE** | Synthetic Minority Oversampling Technique | Generate synthetic minority samples |
| **CV** | Cross-Validation | Evaluate model on multiple data splits |
| **k-fold** | k-Fold Cross-Validation | Split data into k parts for validation |

---

## Summary

### Algorithms Used in This Project

| Algorithm | Task | File |
|-----------|------|------|
| **XGBoost Regressor** | Demand forecasting | `resource_prediction.py` |
| **XGBoost Classifier** | Lead scoring | `customer_acquisition.py` |
| **Gradient Boosting Regressor** | Demand forecasting (fallback) | `resource_prediction.py` |
| **Gradient Boosting Classifier** | Lead scoring, Churn prediction | `customer_acquisition.py` |
| **Random Forest Regressor** | Demand forecasting (alternative) | `resource_prediction.py` |
| **K-Means Clustering** | Customer segmentation | `customer_acquisition.py` |

### Why These Algorithms?

1. **Tabular Data:** All our logistics data is structured (rows and columns)
2. **Proven Performance:** Tree-based ensembles dominate tabular data benchmarks
3. **Feature Importance:** Business stakeholders need to understand what drives predictions
4. **Speed:** Fast training and inference for production use
5. **Minimal Tuning:** Work well with default parameters

---

*Document created for Penske Logistics Analytics Project*
*Last updated: February 2025*
