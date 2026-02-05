"""
RAG (Retrieval-Augmented Generation) Engine for Penske Logistics Analytics

Production-level implementation with:
- OpenAI embeddings (text-embedding-3-small)
- ChromaDB vector store (local, persistent)
- Document chunking and preprocessing
- Semantic search with metadata filtering
- Integration with existing InsightGenerator
"""

import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import hashlib
import json

import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Optional imports with fallbacks
try:
    from langchain_openai import OpenAIEmbeddings
    from langchain_community.vectorstores import Chroma
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.schema import Document
    HAS_LANGCHAIN = True
except ImportError:
    HAS_LANGCHAIN = False
    logger.warning("LangChain not installed. Run: pip install langchain langchain-openai chromadb")

try:
    import chromadb
    from chromadb.config import Settings
    HAS_CHROMADB = True
except ImportError:
    HAS_CHROMADB = False


class DocumentProcessor:
    """Preprocesses and chunks documents for embedding"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        if HAS_LANGCHAIN:
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                length_function=len,
                separators=["\n\n", "\n", ". ", " ", ""]
            )
    
    def process_text(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict]:
        """Split text into chunks with metadata"""
        if not HAS_LANGCHAIN:
            # Fallback: simple splitting
            chunks = [text[i:i+self.chunk_size] for i in range(0, len(text), self.chunk_size - self.chunk_overlap)]
            return [{"text": chunk, "metadata": metadata or {}} for chunk in chunks]
        
        chunks = self.text_splitter.split_text(text)
        return [
            {
                "text": chunk,
                "metadata": {
                    **(metadata or {}),
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "chunk_hash": hashlib.md5(chunk.encode()).hexdigest()[:8]
                }
            }
            for i, chunk in enumerate(chunks)
        ]
    
    def process_dataframe(self, df: pd.DataFrame, text_columns: List[str], 
                          id_column: str = None, category_column: str = None) -> List[Dict]:
        """Convert DataFrame rows to embeddable documents"""
        documents = []
        
        for idx, row in df.iterrows():
            # Combine text columns
            text_parts = []
            for col in text_columns:
                if col in row and pd.notna(row[col]):
                    text_parts.append(f"{col}: {row[col]}")
            
            text = "\n".join(text_parts)
            
            # Build metadata
            metadata = {
                "source": "dataframe",
                "row_index": idx,
                "created_at": datetime.now().isoformat()
            }
            
            if id_column and id_column in row:
                metadata["document_id"] = str(row[id_column])
            
            if category_column and category_column in row:
                metadata["category"] = str(row[category_column])
            
            # Add numeric fields as metadata for filtering
            for col in df.columns:
                if df[col].dtype in ['int64', 'float64'] and pd.notna(row[col]):
                    metadata[f"num_{col}"] = float(row[col])
            
            documents.append({"text": text, "metadata": metadata})
        
        return documents
    
    def process_kpi_report(self, kpis: Dict[str, Any], report_name: str = "KPI Report") -> List[Dict]:
        """Convert KPI dictionary to embeddable document"""
        # Create narrative text from KPIs
        lines = [f"# {report_name}", f"Generated: {datetime.now().isoformat()}", ""]
        
        for key, value in kpis.items():
            if isinstance(value, float):
                lines.append(f"- {key}: {value:.2f}")
            else:
                lines.append(f"- {key}: {value}")
        
        text = "\n".join(lines)
        
        return [{
            "text": text,
            "metadata": {
                "source": "kpi_report",
                "report_name": report_name,
                "created_at": datetime.now().isoformat(),
                **{f"kpi_{k}": v for k, v in kpis.items() if isinstance(v, (int, float))}
            }
        }]


class LogisticsRAGEngine:
    """
    Production-level RAG engine for Penske Logistics.
    
    Features:
    - Persistent vector storage with ChromaDB
    - OpenAI embeddings (text-embedding-3-small)
    - Semantic search with metadata filtering
    - Document versioning and deduplication
    - Batch processing for large datasets
    """
    
    def __init__(self, 
                 persist_directory: str = "./data/vectordb",
                 collection_name: str = "penske_logistics",
                 embedding_model: str = "text-embedding-3-small"):
        
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.embedding_model = embedding_model
        self.processor = DocumentProcessor()
        
        # Initialize components
        self.embeddings = None
        self.vectorstore = None
        self.client = None
        
        self._initialize()
    
    def _initialize(self):
        """Initialize embedding model and vector store"""
        if not HAS_LANGCHAIN or not HAS_CHROMADB:
            logger.warning("RAG engine running in mock mode. Install: pip install langchain langchain-openai chromadb")
            return
        
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key or api_key == "your-openai-api-key-here":
            logger.warning("OpenAI API key not set. RAG engine will use mock mode.")
            return
        
        try:
            # Initialize embeddings
            self.embeddings = OpenAIEmbeddings(
                model=self.embedding_model,
                openai_api_key=api_key
            )
            
            # Initialize ChromaDB client
            os.makedirs(self.persist_directory, exist_ok=True)
            
            self.client = chromadb.PersistentClient(path=self.persist_directory)
            
            # Initialize or load vector store
            self.vectorstore = Chroma(
                client=self.client,
                collection_name=self.collection_name,
                embedding_function=self.embeddings,
                persist_directory=self.persist_directory
            )
            
            logger.info(f"RAG engine initialized with collection: {self.collection_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG engine: {e}")
            self.embeddings = None
            self.vectorstore = None
    
    @property
    def is_active(self) -> bool:
        """Check if RAG engine is properly initialized"""
        return self.vectorstore is not None and self.embeddings is not None
    
    def add_documents(self, documents: List[Dict], batch_size: int = 100) -> Dict[str, Any]:
        """
        Add documents to vector store with batching.
        
        Args:
            documents: List of {"text": str, "metadata": dict}
            batch_size: Number of documents per batch
            
        Returns:
            Summary of ingestion results
        """
        if not self.is_active:
            return self._mock_add_documents(documents)
        
        results = {
            "total_documents": len(documents),
            "batches_processed": 0,
            "documents_added": 0,
            "errors": []
        }
        
        # Process in batches
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            
            try:
                texts = [doc["text"] for doc in batch]
                metadatas = [doc.get("metadata", {}) for doc in batch]
                
                # Generate unique IDs based on content hash
                ids = [
                    hashlib.md5(f"{text}{json.dumps(meta, sort_keys=True)}".encode()).hexdigest()
                    for text, meta in zip(texts, metadatas)
                ]
                
                self.vectorstore.add_texts(
                    texts=texts,
                    metadatas=metadatas,
                    ids=ids
                )
                
                results["documents_added"] += len(batch)
                results["batches_processed"] += 1
                
            except Exception as e:
                results["errors"].append(f"Batch {i//batch_size}: {str(e)}")
                logger.error(f"Error processing batch: {e}")
        
        logger.info(f"Added {results['documents_added']} documents to vector store")
        return results
    
    def _mock_add_documents(self, documents: List[Dict]) -> Dict[str, Any]:
        """Mock implementation when RAG is not available"""
        logger.info(f"[MOCK] Would add {len(documents)} documents to vector store")
        return {
            "total_documents": len(documents),
            "batches_processed": 1,
            "documents_added": len(documents),
            "mode": "mock",
            "errors": []
        }
    
    def search(self, query: str, k: int = 5, 
               filter_metadata: Dict[str, Any] = None,
               score_threshold: float = 0.0) -> List[Dict]:
        """
        Semantic search for relevant documents.
        
        Args:
            query: Search query
            k: Number of results to return
            filter_metadata: Metadata filters (e.g., {"category": "fleet"})
            score_threshold: Minimum similarity score (0-1)
            
        Returns:
            List of matching documents with scores
        """
        if not self.is_active:
            return self._mock_search(query, k)
        
        try:
            # Build filter if provided
            where_filter = None
            if filter_metadata:
                where_filter = {
                    "$and": [
                        {key: {"$eq": value}} 
                        for key, value in filter_metadata.items()
                    ]
                } if len(filter_metadata) > 1 else {
                    list(filter_metadata.keys())[0]: {"$eq": list(filter_metadata.values())[0]}
                }
            
            # Perform search
            results = self.vectorstore.similarity_search_with_relevance_scores(
                query=query,
                k=k,
                filter=where_filter
            )
            
            # Format results
            formatted = []
            for doc, score in results:
                if score >= score_threshold:
                    formatted.append({
                        "content": doc.page_content,
                        "metadata": doc.metadata,
                        "relevance_score": round(score, 4)
                    })
            
            logger.info(f"Search returned {len(formatted)} results for: {query[:50]}...")
            return formatted
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []
    
    def _mock_search(self, query: str, k: int) -> List[Dict]:
        """Mock search results"""
        return [
            {
                "content": f"[MOCK] Relevant document for query: {query}",
                "metadata": {"source": "mock", "created_at": datetime.now().isoformat()},
                "relevance_score": 0.85
            }
        ]
    
    def query_with_context(self, question: str, k: int = 5,
                           filter_metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Search and return formatted context for LLM.
        
        Args:
            question: User question
            k: Number of context documents
            filter_metadata: Optional metadata filters
            
        Returns:
            Dict with context and source documents
        """
        results = self.search(question, k=k, filter_metadata=filter_metadata)
        
        # Build context string
        context_parts = []
        for i, result in enumerate(results, 1):
            context_parts.append(f"[Source {i}] (Score: {result['relevance_score']:.2f})")
            context_parts.append(result["content"])
            context_parts.append("")
        
        context = "\n".join(context_parts)
        
        return {
            "question": question,
            "context": context,
            "num_sources": len(results),
            "sources": results
        }
    
    def ingest_fleet_data(self, fleet_df: pd.DataFrame) -> Dict[str, Any]:
        """Ingest fleet operations data"""
        logger.info("Ingesting fleet operations data...")
        
        docs = self.processor.process_dataframe(
            df=fleet_df,
            text_columns=['vehicle_id', 'region', 'service_type', 'driver_id'],
            id_column='vehicle_id',
            category_column='region'
        )
        
        # Add category metadata
        for doc in docs:
            doc["metadata"]["data_type"] = "fleet_operations"
        
        return self.add_documents(docs)
    
    def ingest_customer_data(self, customer_df: pd.DataFrame, 
                              anonymize: bool = True) -> Dict[str, Any]:
        """Ingest customer data with optional anonymization"""
        logger.info("Ingesting customer data...")
        
        if anonymize:
            # Anonymize before ingestion
            safe_df = customer_df.copy()
            if 'company_name' in safe_df.columns:
                safe_df['company_name'] = safe_df['company_name'].apply(
                    lambda x: f"Company_{hashlib.md5(str(x).encode()).hexdigest()[:6]}"
                )
            if 'customer_id' in safe_df.columns:
                safe_df['customer_id'] = safe_df['customer_id'].apply(
                    lambda x: f"ANON_{hashlib.md5(str(x).encode()).hexdigest()[:8]}"
                )
        else:
            safe_df = customer_df
        
        docs = self.processor.process_dataframe(
            df=safe_df,
            text_columns=['industry', 'region', 'services_used', 'shipment_frequency', 'growth_potential'],
            id_column='customer_id',
            category_column='industry'
        )
        
        for doc in docs:
            doc["metadata"]["data_type"] = "customer"
            doc["metadata"]["anonymized"] = anonymize
        
        return self.add_documents(docs)
    
    def ingest_kpi_snapshot(self, kpis: Dict[str, Any], 
                            snapshot_name: str = None) -> Dict[str, Any]:
        """Ingest KPI snapshot for historical comparison"""
        name = snapshot_name or f"KPI_Snapshot_{datetime.now().strftime('%Y%m%d_%H%M')}"
        logger.info(f"Ingesting KPI snapshot: {name}")
        
        docs = self.processor.process_kpi_report(kpis, report_name=name)
        
        for doc in docs:
            doc["metadata"]["data_type"] = "kpi_snapshot"
        
        return self.add_documents(docs)
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store"""
        if not self.is_active:
            return {"mode": "mock", "document_count": 0}
        
        try:
            collection = self.client.get_collection(self.collection_name)
            count = collection.count()
            
            return {
                "collection_name": self.collection_name,
                "document_count": count,
                "persist_directory": self.persist_directory,
                "embedding_model": self.embedding_model,
                "mode": "active"
            }
        except Exception as e:
            return {"error": str(e), "mode": "error"}
    
    def delete_collection(self) -> bool:
        """Delete the entire collection (use with caution)"""
        if not self.is_active:
            return False
        
        try:
            self.client.delete_collection(self.collection_name)
            logger.warning(f"Deleted collection: {self.collection_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete collection: {e}")
            return False


class RAGInsightGenerator:
    """
    Enhanced InsightGenerator that uses RAG for context-aware responses.
    Combines vector search with LLM generation.
    """
    
    def __init__(self, rag_engine: LogisticsRAGEngine = None):
        self.rag_engine = rag_engine or LogisticsRAGEngine()
        
        # Import existing InsightGenerator
        try:
            from src.genai_insights import InsightGenerator
            self.insight_gen = InsightGenerator()
        except ImportError:
            self.insight_gen = None
    
    def answer_with_context(self, question: str, 
                            additional_context: Dict[str, Any] = None,
                            k: int = 5) -> Dict[str, Any]:
        """
        Answer question using RAG context + LLM.
        
        Args:
            question: User question
            additional_context: Extra context (e.g., current KPIs)
            k: Number of documents to retrieve
            
        Returns:
            Dict with answer, sources, and metadata
        """
        # Step 1: Retrieve relevant context
        rag_result = self.rag_engine.query_with_context(question, k=k)
        
        # Step 2: Build enhanced prompt context
        full_context = {
            "retrieved_context": rag_result["context"],
            "num_sources": rag_result["num_sources"],
            **(additional_context or {})
        }
        
        # Step 3: Generate answer
        if self.insight_gen:
            answer = self.insight_gen.answer_question(question, full_context)
        else:
            answer = f"[MOCK] Based on {rag_result['num_sources']} sources: Answer to '{question}'"
        
        return {
            "question": question,
            "answer": answer,
            "sources": rag_result["sources"],
            "num_sources": rag_result["num_sources"],
            "rag_enabled": self.rag_engine.is_active
        }
    
    def compare_historical_kpis(self, current_kpis: Dict[str, Any]) -> Dict[str, Any]:
        """Compare current KPIs with historical snapshots"""
        # Search for historical KPI snapshots
        results = self.rag_engine.search(
            query="KPI performance metrics historical comparison",
            k=5,
            filter_metadata={"data_type": "kpi_snapshot"}
        )
        
        comparison_context = {
            "current_kpis": current_kpis,
            "historical_snapshots": [r["content"] for r in results]
        }
        
        question = "Compare current KPIs with historical performance and identify trends."
        
        if self.insight_gen:
            analysis = self.insight_gen.answer_question(question, comparison_context)
        else:
            analysis = "[MOCK] Historical comparison analysis"
        
        return {
            "current_kpis": current_kpis,
            "historical_sources": len(results),
            "analysis": analysis
        }


# Convenience function for quick setup
def create_rag_engine(persist_dir: str = "./data/vectordb") -> LogisticsRAGEngine:
    """Factory function to create RAG engine"""
    return LogisticsRAGEngine(persist_directory=persist_dir)
