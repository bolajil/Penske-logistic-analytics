# AI-102 Azure AI Engineer Associate — Exam Flashcards
## Updated: December 2025 (Latest Microsoft Exam Topics)

---

# DOMAIN 1: PLAN & MANAGE AZURE AI SOLUTION (20-25%)

## Card 1: Azure AI Services Overview
**Q:** What are the main categories of Azure AI Services?

**A:**
| Category | Services |
|----------|----------|
| **Vision** | Computer Vision, Custom Vision, Face API |
| **Speech** | Speech-to-Text, Text-to-Speech, Translation |
| **Language** | Text Analytics, Translator, QnA Maker, LUIS |
| **Decision** | Content Moderator, Personalizer |
| **Generative** | Azure OpenAI Service |
| **Search** | Azure AI Search (Cognitive Search) |

---

## Card 2: Azure AI Foundry (formerly Azure AI Studio)
**Q:** What is Azure AI Foundry and its key components?

**A:** Unified platform for building AI solutions.

**Components:**
- **Hub** — Shared resources (compute, storage, connections)
- **Project** — Workspace for a specific AI solution
- **Foundry Models** — Model catalog (OpenAI, Meta, Mistral, etc.)
- **Foundry Tools** — Vision, Speech, Language, Document Intelligence

---

## Card 3: Responsible AI Principles
**Q:** List Microsoft's 6 Responsible AI principles.

**A:**
1. **Fairness** — AI should treat all people fairly
2. **Reliability & Safety** — AI should perform reliably and safely
3. **Privacy & Security** — AI should be secure and respect privacy
4. **Inclusiveness** — AI should empower everyone
5. **Transparency** — AI should be understandable
6. **Accountability** — People should be accountable for AI systems

---

## Card 4: Content Safety & Filters
**Q:** What content filtering options are available in Azure OpenAI?

**A:**
- **Content filters** — Block harmful content (hate, violence, sexual, self-harm)
- **Blocklists** — Custom word/phrase blocking
- **Prompt shields** — Detect jailbreak/injection attempts
- **Groundedness detection** — Detect hallucinations
- **Protected material detection** — Copyrighted content

**Severity levels:** Low, Medium, High (configurable per category)

---

## Card 5: Authentication Methods
**Q:** What authentication methods are available for Azure AI Services?

**A:**
| Method | Use Case |
|--------|----------|
| **API Key** | Simple apps, testing |
| **Azure AD (Entra ID)** | Enterprise, RBAC |
| **Managed Identity** | Azure resources (no credentials in code) |
| **Service Principal** | CI/CD pipelines |

**Best practice:** Use Managed Identity for production

---

## Card 6: Deployment Options
**Q:** What are the deployment options for Azure AI models?

**A:**
- **Standard** — Shared infrastructure, pay-per-token
- **Provisioned Throughput (PTU)** — Reserved capacity, predictable latency
- **Global** — Optimized routing across regions
- **Data Zone** — Data residency compliance
- **Connected Container** — On-premises with Azure billing

---

# DOMAIN 2: GENERATIVE AI SOLUTIONS (15-20%)

## Card 7: Azure OpenAI Models
**Q:** List the main Azure OpenAI model families and their uses.

**A:**
| Model | Best For |
|-------|----------|
| **GPT-4o** | Multimodal (text + images), reasoning |
| **GPT-4 Turbo** | Complex tasks, 128K context |
| **GPT-3.5 Turbo** | Fast, cost-effective chat |
| **DALL-E 3** | Image generation |
| **Whisper** | Speech-to-text transcription |
| **Text Embedding** | Vector search, semantic similarity |

---

## Card 8: RAG Pattern
**Q:** What is RAG and how does it work?

**A:** **Retrieval-Augmented Generation**

```
1. User Query → 
2. Convert to embedding vector →
3. Search vector database →
4. Retrieve relevant documents →
5. Add to prompt as context →
6. LLM generates grounded response
```

**Benefits:**
- Reduces hallucinations
- Uses your own data
- No model retraining needed

---

## Card 9: Prompt Engineering Techniques
**Q:** List 5 key prompt engineering techniques.

**A:**
1. **Zero-shot** — Direct question, no examples
2. **Few-shot** — Provide examples in prompt
3. **Chain-of-Thought** — "Let's think step by step"
4. **System prompts** — Set persona and rules
5. **Structured output** — Request JSON/XML format

**Temperature:** 0 = deterministic, 1 = creative

---

## Card 10: Prompt Flow
**Q:** What is Prompt Flow in Azure AI Foundry?

**A:** Visual tool for building LLM workflows.

**Node types:**
- **LLM** — Call language models
- **Python** — Custom code
- **Prompt** — Template management
- **Tools** — External integrations

**Benefits:** Version control, testing, evaluation, deployment

---

## Card 11: Fine-Tuning vs RAG
**Q:** When to use fine-tuning vs RAG?

**A:**
| Aspect | Fine-Tuning | RAG |
|--------|-------------|-----|
| **Use case** | Change model behavior/style | Add knowledge |
| **Data needed** | Training examples | Documents |
| **Cost** | Higher (training + hosting) | Lower |
| **Updates** | Retrain model | Update index |
| **Best for** | Tone, format, domain adaptation | Current facts, your data |

---

## Card 12: Model Parameters
**Q:** Explain key Azure OpenAI parameters.

**A:**
| Parameter | Effect |
|-----------|--------|
| **temperature** | 0=focused, 1=creative |
| **top_p** | Nucleus sampling (0.1=narrow, 1=broad) |
| **max_tokens** | Output length limit |
| **frequency_penalty** | Reduce repetition |
| **presence_penalty** | Encourage new topics |
| **stop** | Sequences to stop generation |

---

# DOMAIN 3: AGENTIC SOLUTIONS (5-10%) — NEW!

## Card 13: What is an AI Agent?
**Q:** Define an AI agent and its components.

**A:** Autonomous AI system that can perceive, reason, and act.

**Components:**
- **LLM Brain** — Reasoning and planning
- **Tools** — APIs, functions, actions
- **Memory** — Short-term (conversation) + Long-term (vector DB)
- **Knowledge** — RAG for domain expertise

---

## Card 14: Microsoft Agent Framework
**Q:** What is the Microsoft Agent Framework?

**A:** SDK for building complex agents in Azure.

**Key features:**
- **Function calling** — LLM invokes tools
- **Multi-agent** — Orchestrate multiple specialized agents
- **Semantic Kernel** — .NET/Python integration
- **Autonomous mode** — Agent decides actions

**Code pattern:**
```python
agent = Agent(model="gpt-4o", tools=[search, calculator])
response = agent.run("What's the weather in Seattle?")
```

---

## Card 15: Agent Orchestration
**Q:** What are common agent orchestration patterns?

**A:**
1. **Sequential** — Agent A → Agent B → Agent C
2. **Parallel** — Run multiple agents simultaneously
3. **Router** — Central agent delegates to specialists
4. **Hierarchical** — Manager agent coordinates workers

**Use case:** Customer support with routing, research, and response agents

---

# DOMAIN 4: COMPUTER VISION (10-15%)

## Card 16: Computer Vision Capabilities
**Q:** What can Azure Computer Vision analyze?

**A:**
- **Image Analysis** — Tags, objects, faces, text (OCR)
- **Spatial Analysis** — People counting, zone monitoring
- **Image captioning** — Generate descriptions
- **Dense captioning** — Multiple region descriptions
- **Object detection** — Bounding boxes + labels
- **Brand detection** — Logo recognition

---

## Card 17: Custom Vision
**Q:** What are the two Custom Vision model types?

**A:**
| Type | Output | Use Case |
|------|--------|----------|
| **Classification** | Tags/labels for whole image | "Is this a dog or cat?" |
| **Object Detection** | Bounding boxes + labels | "Where are the defects?" |

**Training:** Upload images → Label → Train → Publish → Consume

**Minimum:** 5 images per tag (50+ recommended)

---

## Card 18: Azure AI Video Indexer
**Q:** What insights can Video Indexer extract?

**A:**
- **Visual:** Faces, objects, scenes, OCR, thumbnails
- **Audio:** Transcription, speaker identification, translation
- **Content:** Topics, keywords, sentiments, brands
- **Moderation:** Adult content detection

**Output:** JSON timeline with timestamps

---

# DOMAIN 5: NATURAL LANGUAGE PROCESSING (15-20%)

## Card 19: Text Analytics Capabilities
**Q:** What can Azure AI Language analyze?

**A:**
| Feature | Output |
|---------|--------|
| **Sentiment** | Positive/Negative/Neutral + confidence |
| **Key phrases** | Important terms |
| **Named entities** | Person, Location, Organization, Date |
| **PII detection** | SSN, credit card, phone, email |
| **Language detection** | ISO language code |
| **Linked entities** | Wikipedia links |

---

## Card 20: Conversational Language Understanding (CLU)
**Q:** What replaced LUIS? Explain CLU components.

**A:** **Conversational Language Understanding** in Azure AI Language.

**Components:**
- **Intents** — What user wants to do (BookFlight, CheckWeather)
- **Entities** — Key data (destination, date, time)
- **Utterances** — Example user phrases

**Example:**
```
Utterance: "Book a flight to Paris on Friday"
Intent: BookFlight
Entities: destination=Paris, date=Friday
```

---

## Card 21: Custom Question Answering
**Q:** How does Custom Question Answering work?

**A:**
1. Create project in Language Studio
2. Add sources (FAQ pages, documents, manual Q&A)
3. System extracts Q&A pairs automatically
4. Add alternate phrasings
5. Test and publish
6. Query via REST API

**Multi-turn:** Follow-up prompts for clarification

---

## Card 22: Azure Speech Services
**Q:** List Azure Speech service capabilities.

**A:**
| Service | Function |
|---------|----------|
| **Speech-to-Text** | Transcription, real-time + batch |
| **Text-to-Speech** | Neural voices, SSML customization |
| **Speech Translation** | Real-time speech translation |
| **Speaker Recognition** | Identify/verify speakers |
| **Custom Speech** | Train on your audio data |
| **Custom Neural Voice** | Create branded voice |

---

## Card 23: SSML (Speech Synthesis Markup Language)
**Q:** What is SSML and give an example?

**A:** XML markup for controlling speech output.

```xml
<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis">
  <voice name="en-US-JennyNeural">
    <prosody rate="slow" pitch="+10%">
      Welcome to Azure!
    </prosody>
    <break time="500ms"/>
    <emphasis level="strong">Let's get started.</emphasis>
  </voice>
</speak>
```

**Controls:** Rate, pitch, volume, pauses, emphasis, pronunciation

---

# DOMAIN 6: KNOWLEDGE MINING & EXTRACTION (15-20%)

## Card 24: Azure AI Search Architecture
**Q:** Explain Azure AI Search components.

**A:**
```
Data Source → Indexer → Skillset → Index → Query
     ↓           ↓          ↓         ↓        ↓
  Blob/SQL   Scheduler   AI Skills  Schema   REST API
```

**Key concepts:**
- **Index** — Searchable data structure
- **Indexer** — Automated data import
- **Skillset** — AI enrichment pipeline
- **Knowledge Store** — Enriched data projections

---

## Card 25: Built-in Skills
**Q:** List common Azure AI Search built-in skills.

**A:**
| Category | Skills |
|----------|--------|
| **Vision** | OCR, Image Analysis, Face Detection |
| **Language** | Key Phrases, Entity Recognition, Sentiment |
| **Text** | Split, Merge, Language Detection |
| **Utility** | Shaper, Conditional |

**Custom skills:** Call Azure Functions or external APIs

---

## Card 26: Vector Search
**Q:** How does vector search work in Azure AI Search?

**A:**
1. **Embed documents** → Convert to vectors using embedding model
2. **Store vectors** → Add to index with vector field
3. **Query** → Convert query to vector
4. **Search** → Find similar vectors (cosine similarity)

**Hybrid search:** Combine keyword + vector for best results

```json
{
  "search": "azure ai capabilities",
  "vectorQueries": [{
    "vector": [0.1, 0.2, ...],
    "k": 5,
    "fields": "contentVector"
  }]
}
```

---

## Card 27: Azure Document Intelligence
**Q:** What are the Document Intelligence model types?

**A:**
| Model | Use Case |
|-------|----------|
| **Prebuilt** | Invoice, Receipt, ID, Business Card, W-2 |
| **Layout** | Tables, structure, reading order |
| **Read** | OCR, handwriting |
| **Custom** | Your document types |
| **Composed** | Multiple custom models combined |

**Output:** JSON with fields, confidence scores, bounding boxes

---

## Card 28: Knowledge Store Projections
**Q:** What are the three Knowledge Store projection types?

**A:**
| Type | Storage | Use Case |
|------|---------|----------|
| **Table** | Azure Tables | Structured data for Power BI |
| **Object** | Blob (JSON) | Complex nested data |
| **File** | Blob (binary) | Normalized images |

**Purpose:** Persist AI enrichments for downstream analytics

---

# QUICK REFERENCE

## Card 29: SDK Code Patterns
**Q:** Show common Azure AI SDK patterns.

**A:**
```python
# Azure OpenAI
from openai import AzureOpenAI
client = AzureOpenAI(azure_endpoint="...", api_key="...")
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello"}]
)

# Computer Vision
from azure.ai.vision.imageanalysis import ImageAnalysisClient
client = ImageAnalysisClient(endpoint, credential)
result = client.analyze(image_url, visual_features=["Caption", "Tags"])

# Text Analytics
from azure.ai.textanalytics import TextAnalyticsClient
client = TextAnalyticsClient(endpoint, credential)
result = client.analyze_sentiment(documents)
```

---

## Card 30: Pricing Tiers & Limits
**Q:** What are common Azure AI service tiers?

**A:**
| Tier | Characteristics |
|------|-----------------|
| **Free (F0)** | Limited calls, testing only |
| **Standard (S0)** | Pay-per-use, production |
| **Provisioned (PTU)** | Reserved capacity, OpenAI only |

**Key limits:**
- OpenAI: Tokens per minute (TPM), Requests per minute (RPM)
- Vision: 20 requests/second
- Search: Replicas × Partitions = Scale units

---

# EXAM TIPS

## Card 31: Common Exam Scenarios
**Q:** What are frequent AI-102 scenario types?

**A:**
1. **"Which service..."** → Service selection based on requirements
2. **"How to configure..."** → SDK/portal configuration
3. **"What code..."** → Complete the code snippet
4. **"Troubleshoot..."** → Identify error cause
5. **"Best practice..."** → Security, performance, cost

**Focus areas:**
- Azure OpenAI configuration
- RAG implementation
- Content safety
- Custom models (Vision, Language)
- Search skillsets

---

## Card 32: Key APIs & Endpoints
**Q:** What are the main Azure AI API patterns?

**A:**
```
# Azure OpenAI
https://{resource}.openai.azure.com/openai/deployments/{model}/chat/completions

# Computer Vision
https://{resource}.cognitiveservices.azure.com/vision/v3.2/analyze

# Language
https://{resource}.cognitiveservices.azure.com/language/:analyze-text

# Document Intelligence
https://{resource}.cognitiveservices.azure.com/formrecognizer/documentModels/{model}:analyze

# Search
https://{service}.search.windows.net/indexes/{index}/docs/search
```

---

**Good luck on your AI-102 exam! 🎯**
