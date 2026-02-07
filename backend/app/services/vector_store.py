"""Vector store service for regulatory document retrieval using ChromaDB."""

import chromadb
from chromadb.config import Settings as ChromaSettings
from chromadb.utils import embedding_functions
from app.config import get_settings
from pathlib import Path
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)
settings = get_settings()


class VectorStore:
    """Manages vector database for regulatory documents."""
    
    def __init__(self):
        """Initialize ChromaDB client and collection."""
        
        # Create persist directory if it doesn't exist
        persist_path = Path(settings.chroma_persist_dir)
        persist_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.Client(
            ChromaSettings(
                persist_directory=str(persist_path),
                anonymized_telemetry=False
            )
        )
        
        # Set up Gemini embedding function
        try:
            import google.genai as genai
            genai.configure(api_key=settings.google_api_key)
            
            # Create custom embedding function for Gemini
            self.embedding_fn = self._create_gemini_embedder()
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini embeddings: {e}")
            # Fallback to default embeddings if Gemini fails
            self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection(
                name=settings.collection_name,
                embedding_function=self.embedding_fn
            )
            logger.info(f"Loaded existing collection: {settings.collection_name}")
        except:
            self.collection = self.client.create_collection(
                name=settings.collection_name,
                embedding_function=self.embedding_fn,
                metadata={"description": "PRA Rulebook and COREP knowledge base"}
            )
            logger.info(f"Created new collection: {settings.collection_name}")
    
    def _create_gemini_embedder(self):
        """Create custom embedding function using Gemini."""
        import google.genai as genai
        
        class GeminiEmbeddingFunction:
            def __call__(self, input: List[str]) -> List[List[float]]:
                embeddings = []
                for text in input:
                    result = genai.embed_content(
                        model=f"models/{settings.embedding_model}",
                        content=text,
                        task_type="retrieval_document"
                    )
                    embeddings.append(result['embedding'])
                return embeddings
        
        return GeminiEmbeddingFunction()
    
    def add_documents(
        self,
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        ids: List[str]
    ):
        """Add documents to the vector store."""
        
        try:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Added {len(documents)} documents to vector store")
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            raise
    
    def search(
        self,
        query: str,
        n_results: int = None,
        filter_metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Search for relevant documents.
        
        Args:
            query: Search query
            n_results: Number of results to return (default from settings)
            filter_metadata: Metadata filters (e.g., {'template_id': 'CA1'})
        
        Returns:
            Dictionary with documents, metadatas, and distances
        """
        
        if n_results is None:
            n_results = settings.top_k_results
        
        try:
            # Generate embedding for query
            import google.genai as genai
            genai.configure(api_key=settings.google_api_key)
            
            query_embedding = genai.embed_content(
                model=f"models/{settings.embedding_model}",
                content=query,
                task_type="retrieval_query"
            )
            
            # Search with query embedding
            results = self.collection.query(
                query_embeddings=[query_embedding['embedding']],
                n_results=n_results,
                where=filter_metadata
            )
            
            # Filter by relevance threshold (distance-based)
            filtered_results = self._filter_by_relevance(results)
            
            logger.info(f"Retrieved {len(filtered_results['documents'][0])} relevant documents")
            return filtered_results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            # Return empty results
            return {
                'documents': [[]],
                'metadatas': [[]],
                'distances': [[]]
            }
    
    def _filter_by_relevance(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Filter results by relevance threshold."""
        
        # ChromaDB returns distances (lower is better)
        # Convert to similarity scores and filter
        filtered = {
            'documents': [[]],
            'metadatas': [[]],
            'distances': [[]]
        }
        
        if not results['distances'] or not results['distances'][0]:
            return filtered
        
        for i, distance in enumerate(results['distances'][0]):
            # Simple threshold: keep if distance < inverse of threshold
            # This is a heuristic; adjust based on your data
            if distance < (1.0 / settings.relevance_threshold):
                filtered['documents'][0].append(results['documents'][0][i])
                filtered['metadatas'][0].append(results['metadatas'][0][i])
                filtered['distances'][0].append(distance)
        
        return filtered
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection."""
        
        try:
            count = self.collection.count()
            return {
                "collection_name": settings.collection_name,
                "document_count": count,
                "status": "ready" if count > 0 else "empty"
            }
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {"status": "error", "message": str(e)}
