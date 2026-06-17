"""
Custom embeddings class using TCS GenAI API
"""
import httpx
import sys
from typing import List
from langchain.embeddings.base import Embeddings
from config import Config


class TCSGenAIEmbeddings(Embeddings):
    """Custom embedding class that uses TCS GenAI API for generating embeddings"""
    
    def __init__(self):
        """Initialize TCS GenAI embeddings with API configuration"""
        self.base_url = Config.GENAI_BASE_URL
        self.api_key = Config.GENAI_API_KEY
        # Use TCS GenAI embedding model
        self.model = "azure/genailab-maas-text-embedding-3-large"
        
        print(f"TCSGenAIEmbeddings initialized with base_url: {self.base_url}, model: {self.model}", flush=True)
        sys.stdout.flush()
        
        # Create HTTP client with SSL verification disabled
        self.client = httpx.Client(
            verify=False,
            timeout=30.0
        )
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Embed a list of documents using TCS GenAI API
        
        Args:
            texts: List of text documents to embed
            
        Returns:
            List of embeddings (each embedding is a list of floats)
        """
        print(f"embed_documents called with {len(texts)} texts", flush=True)
        sys.stdout.flush()
        
        embeddings = []
        
        # Process texts in batches to avoid API limits
        batch_size = 10
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_embeddings = self._get_embeddings(batch)
            embeddings.extend(batch_embeddings)
        
        print(f"embed_documents returning {len(embeddings)} embeddings", flush=True)
        sys.stdout.flush()
        return embeddings
    
    def embed_query(self, text: str) -> List[float]:
        """
        Embed a single query text using TCS GenAI API
        
        Args:
            text: Query text to embed
            
        Returns:
            Single embedding as a list of floats
        """
        print(f"embed_query called with text length: {len(text)}", flush=True)
        sys.stdout.flush()
        
        embeddings = self._get_embeddings([text])
        result = embeddings[0] if embeddings else []
        
        print(f"embed_query returning embedding of length: {len(result)}", flush=True)
        sys.stdout.flush()
        return result
    
    def _get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Internal method to call TCS GenAI API for embeddings
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embeddings
        """
        try:
            # TCS GenAI API endpoint for embeddings (OpenAI compatible)
            url = f"{self.base_url}/embeddings"
            
            print(f"Calling TCS GenAI embedding API: {url}", flush=True)
            sys.stdout.flush()
            
            headers = {
                "Authorization": f"Bearer {self.api_key[:10]}...",  # Don't log full key
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "input": texts
            }
            
            print(f"Payload: model={self.model}, input_count={len(texts)}", flush=True)
            sys.stdout.flush()
            
            response = self.client.post(url, json=payload, headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"})
            
            print(f"Response status: {response.status_code}", flush=True)
            sys.stdout.flush()
            
            response.raise_for_status()
            
            data = response.json()
            
            # Extract embeddings from response
            # OpenAI-compatible API returns: {"data": [{"embedding": [...]}, ...]}
            embeddings = [item["embedding"] for item in data["data"]]
            
            print(f"Successfully got {len(embeddings)} embeddings", flush=True)
            sys.stdout.flush()
            
            return embeddings
            
        except httpx.HTTPStatusError as e:
            print(f"HTTP error getting embeddings: {e.response.status_code}", flush=True)
            print(f"Response: {e.response.text[:500]}", flush=True)
            sys.stdout.flush()
            # Return zero vectors as fallback
            return [[0.0] * 1536 for _ in texts]  # 1536 is typical embedding dimension
            
        except Exception as e:
            print(f"Error getting embeddings from TCS GenAI: {type(e).__name__}: {str(e)}", flush=True)
            import traceback
            traceback.print_exc()
            sys.stdout.flush()
            # Return zero vectors as fallback
            return [[0.0] * 1536 for _ in texts]
    
    def __del__(self):
        """Cleanup HTTP client when object is destroyed"""
        if hasattr(self, 'client'):
            self.client.close()
