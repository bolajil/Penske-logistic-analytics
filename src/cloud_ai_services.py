"""
Cloud AI/ML Services Integration
Provides unified interface for AWS SageMaker, Azure OpenAI/ML, and GCP Vertex AI
"""

import os
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, field
from enum import Enum


class CloudProvider(Enum):
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"


@dataclass
class CloudConfig:
    provider: CloudProvider
    region: str
    credentials: Dict[str, str]


class AWSSageMakerService:
    """AWS SageMaker and Bedrock integration"""
    
    def __init__(self, region: str = "us-east-1"):
        self.region = region
        self.client = None
        self.bedrock_client = None
        
    def connect(self, access_key: str, secret_key: str) -> bool:
        """Connect to AWS services"""
        try:
            import boto3
            self.session = boto3.Session(
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=self.region
            )
            self.client = self.session.client('sagemaker')
            self.bedrock_client = self.session.client('bedrock-runtime')
            return True
        except Exception as e:
            print(f"AWS connection error: {e}")
            return False
    
    def invoke_bedrock(self, prompt: str, model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0") -> str:
        """Invoke Bedrock model for text generation"""
        if not self.bedrock_client:
            return "Not connected to AWS"
        
        try:
            import json
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4096,
                "messages": [{"role": "user", "content": prompt}]
            })
            
            response = self.bedrock_client.invoke_model(
                modelId=model_id,
                body=body
            )
            
            result = json.loads(response['body'].read())
            return result['content'][0]['text']
        except Exception as e:
            return f"Bedrock error: {e}"
    
    def list_endpoints(self) -> List[Dict]:
        """List SageMaker endpoints"""
        if not self.client:
            return []
        
        try:
            response = self.client.list_endpoints()
            return response.get('Endpoints', [])
        except Exception as e:
            print(f"List endpoints error: {e}")
            return []
    
    def invoke_endpoint(self, endpoint_name: str, payload: Dict) -> Dict:
        """Invoke SageMaker endpoint"""
        if not self.client:
            return {"error": "Not connected"}
        
        try:
            import json
            runtime = self.session.client('sagemaker-runtime')
            response = runtime.invoke_endpoint(
                EndpointName=endpoint_name,
                ContentType='application/json',
                Body=json.dumps(payload)
            )
            return json.loads(response['Body'].read())
        except Exception as e:
            return {"error": str(e)}


class AzureOpenAIService:
    """Azure OpenAI and Azure ML integration"""
    
    def __init__(self, endpoint: str = "", api_key: str = ""):
        self.endpoint = endpoint
        self.api_key = api_key
        self.client = None
        self.ml_client = None
        
    def connect(self, endpoint: str, api_key: str) -> bool:
        """Connect to Azure OpenAI"""
        try:
            from openai import AzureOpenAI
            self.endpoint = endpoint
            self.api_key = api_key
            self.client = AzureOpenAI(
                api_key=api_key,
                api_version="2024-02-15-preview",
                azure_endpoint=endpoint
            )
            return True
        except Exception as e:
            print(f"Azure connection error: {e}")
            return False
    
    def connect_ml(self, subscription_id: str, resource_group: str, workspace: str) -> bool:
        """Connect to Azure ML workspace"""
        try:
            from azure.ai.ml import MLClient
            from azure.identity import DefaultAzureCredential
            
            self.ml_client = MLClient(
                DefaultAzureCredential(),
                subscription_id=subscription_id,
                resource_group_name=resource_group,
                workspace_name=workspace
            )
            return True
        except Exception as e:
            print(f"Azure ML connection error: {e}")
            return False
    
    def generate_text(self, prompt: str, deployment: str = "gpt-4") -> str:
        """Generate text using Azure OpenAI"""
        if not self.client:
            return "Not connected to Azure OpenAI"
        
        try:
            response = self.client.chat.completions.create(
                model=deployment,
                messages=[
                    {"role": "system", "content": "You are a logistics analytics expert."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=4096,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Azure OpenAI error: {e}"
    
    def generate_embeddings(self, text: str, deployment: str = "text-embedding-ada-002") -> List[float]:
        """Generate embeddings"""
        if not self.client:
            return []
        
        try:
            response = self.client.embeddings.create(
                model=deployment,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Embeddings error: {e}")
            return []
    
    def list_ml_endpoints(self) -> List[Dict]:
        """List Azure ML endpoints"""
        if not self.ml_client:
            return []
        
        try:
            endpoints = self.ml_client.online_endpoints.list()
            return [{"name": e.name, "state": e.provisioning_state} for e in endpoints]
        except Exception as e:
            print(f"List ML endpoints error: {e}")
            return []


class VertexAIService:
    """Google Cloud Vertex AI integration"""
    
    def __init__(self, project_id: str = "", location: str = "us-central1"):
        self.project_id = project_id
        self.location = location
        self.model = None
        self.embedding_model = None
        
    def connect(self, project_id: str, location: str = "us-central1") -> bool:
        """Connect to Vertex AI"""
        try:
            import vertexai
            from vertexai.generative_models import GenerativeModel
            from vertexai.language_models import TextEmbeddingModel
            
            self.project_id = project_id
            self.location = location
            vertexai.init(project=project_id, location=location)
            self.model = GenerativeModel("gemini-1.5-pro")
            self.embedding_model = TextEmbeddingModel.from_pretrained("text-embedding-004")
            return True
        except Exception as e:
            print(f"Vertex AI connection error: {e}")
            return False
    
    def generate_text(self, prompt: str) -> str:
        """Generate text using Gemini"""
        if not self.model:
            return "Not connected to Vertex AI"
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "max_output_tokens": 4096,
                    "temperature": 0.7,
                    "top_p": 0.95,
                }
            )
            return response.text
        except Exception as e:
            return f"Vertex AI error: {e}"
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings"""
        if not self.embedding_model:
            return []
        
        try:
            embeddings = self.embedding_model.get_embeddings(texts)
            return [e.values for e in embeddings]
        except Exception as e:
            print(f"Embeddings error: {e}")
            return []
    
    def list_endpoints(self) -> List[Dict]:
        """List Vertex AI endpoints"""
        try:
            from google.cloud import aiplatform
            aiplatform.init(project=self.project_id, location=self.location)
            endpoints = aiplatform.Endpoint.list()
            return [{"name": e.display_name, "resource_name": e.resource_name} for e in endpoints]
        except Exception as e:
            print(f"List endpoints error: {e}")
            return []


class HybridSearchService:
    """Hybrid search combining BM25 (keyword) + Vector (semantic) search via LangChain.
    
    BM25 excels at exact-match queries (shipment IDs, regulation numbers).
    Vector search excels at semantic queries ("how do I handle damaged freight?").
    Combined, they cover both use cases with weighted score fusion.
    
    Usage:
        service = HybridSearchService()
        service.connect_azure_openai(endpoint="...", api_key="...")
        service.add_documents(["doc1", "doc2", ...], metadatas=[{...}, ...])
        results = service.search("DOT regulation 49-CFR-395", k=5)
    """
    
    def __init__(
        self,
        bm25_weight: float = 0.4,
        vector_weight: float = 0.6,
        vector_store_type: str = "faiss",
        embedding_model: str = "text-embedding-ada-002"
    ):
        self.bm25_weight = bm25_weight
        self.vector_weight = vector_weight
        self.vector_store_type = vector_store_type
        self.embedding_model = embedding_model
        self.embeddings = None
        self.bm25_retriever = None
        self.vector_retriever = None
        self.hybrid_retriever = None
        self.vector_store = None
        self._documents: List[str] = []
    
    def connect_azure_openai(self, endpoint: str, api_key: str) -> bool:
        """Initialize Azure OpenAI embeddings for vector search."""
        try:
            from langchain_openai import AzureOpenAIEmbeddings
            self.embeddings = AzureOpenAIEmbeddings(
                model=self.embedding_model,
                azure_endpoint=endpoint,
                api_key=api_key
            )
            return True
        except Exception as e:
            print(f"Azure OpenAI embeddings connection error: {e}")
            return False
    
    def connect_openai(self, api_key: str) -> bool:
        """Initialize OpenAI embeddings for vector search."""
        try:
            from langchain_openai import OpenAIEmbeddings
            self.embeddings = OpenAIEmbeddings(
                model=self.embedding_model,
                api_key=api_key
            )
            return True
        except Exception as e:
            print(f"OpenAI embeddings connection error: {e}")
            return False
    
    def add_documents(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """Add documents to both BM25 and vector indexes.
        
        Args:
            texts: List of document strings to index
            metadatas: Optional metadata dicts for each document
            
        Returns:
            True if both indexes built successfully
        """
        if not self.embeddings:
            print("Error: Connect to an embedding provider first.")
            return False
        
        try:
            from langchain_community.retrievers import BM25Retriever
            from langchain.retrievers import EnsembleRetriever
            from langchain_core.documents import Document
            
            self._documents = texts
            docs = [
                Document(page_content=t, metadata=metadatas[i] if metadatas else {})
                for i, t in enumerate(texts)
            ]
            
            # BM25 retriever (keyword search)
            self.bm25_retriever = BM25Retriever.from_documents(docs)
            self.bm25_retriever.k = 5
            
            # Vector retriever (semantic search)
            if self.vector_store_type == "faiss":
                from langchain_community.vectorstores import FAISS
                self.vector_store = FAISS.from_documents(docs, self.embeddings)
            elif self.vector_store_type == "chroma":
                from langchain_community.vectorstores import Chroma
                self.vector_store = Chroma.from_documents(docs, self.embeddings)
            else:
                print(f"Unsupported vector store type: {self.vector_store_type}")
                return False
            
            self.vector_retriever = self.vector_store.as_retriever(
                search_kwargs={"k": 5}
            )
            
            # Combine into hybrid retriever
            self.hybrid_retriever = EnsembleRetriever(
                retrievers=[self.bm25_retriever, self.vector_retriever],
                weights=[self.bm25_weight, self.vector_weight]
            )
            
            print(f"Indexed {len(texts)} documents (BM25 + {self.vector_store_type.upper()} vector store)")
            return True
        except Exception as e:
            print(f"Error building indexes: {e}")
            return False
    
    def connect_azure_search(
        self,
        search_endpoint: str,
        search_key: str,
        index_name: str,
        openai_endpoint: str,
        openai_key: str
    ) -> bool:
        """Connect to Azure AI Search with built-in hybrid search.
        
        Azure AI Search handles BM25 + vector natively, no EnsembleRetriever needed.
        """
        try:
            from langchain_openai import AzureOpenAIEmbeddings
            from langchain_community.vectorstores import AzureSearch
            
            self.embeddings = AzureOpenAIEmbeddings(
                model=self.embedding_model,
                azure_endpoint=openai_endpoint,
                api_key=openai_key
            )
            
            self.vector_store = AzureSearch(
                azure_search_endpoint=search_endpoint,
                azure_search_key=search_key,
                index_name=index_name,
                embedding_function=self.embeddings.embed_query,
                search_type="hybrid"
            )
            
            self.hybrid_retriever = self.vector_store.as_retriever(
                search_type="hybrid",
                search_kwargs={"k": 5}
            )
            
            print(f"Connected to Azure AI Search index: {index_name} (hybrid mode)")
            return True
        except Exception as e:
            print(f"Azure AI Search connection error: {e}")
            return False
    
    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Run hybrid search and return ranked results.
        
        Args:
            query: Search query string
            k: Number of results to return
            
        Returns:
            List of dicts with 'content', 'metadata', and 'rank' keys
        """
        if not self.hybrid_retriever:
            print("Error: Add documents or connect to Azure Search first.")
            return []
        
        try:
            results = self.hybrid_retriever.invoke(query)
            return [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "rank": i + 1
                }
                for i, doc in enumerate(results[:k])
            ]
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    def search_with_scores(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Run vector search with similarity scores (vector store only).
        
        Note: BM25 scores are not directly comparable to vector scores,
        so this uses vector search only for score-aware retrieval.
        """
        if not self.vector_store:
            print("Error: Vector store not initialized.")
            return []
        
        try:
            results = self.vector_store.similarity_search_with_score(query, k=k)
            return [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": float(score),
                    "rank": i + 1
                }
                for i, (doc, score) in enumerate(results)
            ]
        except Exception as e:
            print(f"Scored search error: {e}")
            return []
    
    def update_weights(self, bm25_weight: float, vector_weight: float) -> None:
        """Adjust the BM25 vs vector weight balance.
        
        Higher BM25 weight → better for exact-match queries (IDs, codes).
        Higher vector weight → better for semantic queries (natural language).
        """
        self.bm25_weight = bm25_weight
        self.vector_weight = vector_weight
        if self.hybrid_retriever and hasattr(self.hybrid_retriever, 'weights'):
            self.hybrid_retriever.weights = [bm25_weight, vector_weight]
            print(f"Updated weights: BM25={bm25_weight}, Vector={vector_weight}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Return current index statistics."""
        return {
            "total_documents": len(self._documents),
            "vector_store_type": self.vector_store_type,
            "embedding_model": self.embedding_model,
            "bm25_weight": self.bm25_weight,
            "vector_weight": self.vector_weight,
            "hybrid_ready": self.hybrid_retriever is not None
        }


# Demo mode responses for when credentials are not configured
DEMO_RESPONSES = {
    "route_optimization": """## Route Optimization Analysis

Based on the logistics data provided:

**Current Route:** Chicago → Indianapolis → Louisville → Nashville
- Total Distance: 478 miles
- Average Delivery Time: 8.5 hours
- Fuel Consumption: 65 gallons

### Recommendations:

1. **Optimized Route:** Chicago → Louisville → Nashville → Indianapolis (return)
   - Estimated savings: 45 miles, 0.8 hours
   - Fuel reduction: ~6 gallons

2. **Time Window Optimization:**
   - Depart Chicago at 5:00 AM to avoid I-65 morning traffic
   - Schedule Louisville delivery for 10:30 AM

3. **Fuel Efficiency Tips:**
   - Maintain consistent speed of 62 mph for optimal MPG
   - Use truck stops at mile markers 156 and 298 for refueling

**Projected Savings:** $127/trip, $3,175/month""",
    
    "demand_forecast": """## Demand Forecast Analysis

### 30-Day Outlook:

| Week | Predicted Volume | Confidence |
|------|-----------------|------------|
| Week 1 | 12,450 units | 94% |
| Week 2 | 13,200 units | 91% |
| Week 3 | 14,800 units | 87% |
| Week 4 | 15,100 units | 85% |

### Key Drivers:
- **Seasonal uptick:** +12% due to Q4 retail demand
- **New customer onboarding:** +850 units/week from Acme Corp
- **Regional shift:** Southwest region showing 18% growth

### Resource Recommendations:
- Add 3 trucks to Midwest fleet by Week 3
- Increase warehouse staffing by 15% for Weeks 3-4
- Pre-position inventory at Louisville hub""",

    "general": """## Logistics Analytics Insight

Based on the available data, here are the key findings:

### Performance Summary:
- **On-Time Delivery Rate:** 94.2% (target: 95%)
- **Fleet Utilization:** 87.3% (above target)
- **Cost per Mile:** $2.14 (3% improvement YoY)

### Recommendations:
1. Focus on Northeast region to improve OTD by 2%
2. Consider route consolidation for low-volume lanes
3. Implement predictive maintenance for aging fleet vehicles

### Alerts:
⚠️ 3 vehicles due for maintenance this week
⚠️ Capacity constraints expected in Southeast hub
"""
}


def get_demo_response(query_type: str = "general") -> str:
    """Get demo response for UI testing without credentials"""
    return DEMO_RESPONSES.get(query_type, DEMO_RESPONSES["general"])
