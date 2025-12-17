"""
Embedding service using sentence-transformers
"""

import logging
from typing import List, Optional
import asyncio
from sentence_transformers import SentenceTransformer
import torch

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Embedding service using sentence-transformers"""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model: Optional[SentenceTransformer] = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
    
    async def initialize(self):
        """Initialize the embedding model with retry logic"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                logger.info(f"Loading embedding model: {self.model_name} (attempt {attempt + 1}/{max_retries})")
                
                # Load model in thread pool to avoid blocking
                loop = asyncio.get_event_loop()
                self.model = await loop.run_in_executor(
                    None,
                    lambda: SentenceTransformer(self.model_name, device=self.device)
                )
                
                logger.info(f"Embedding model loaded successfully on {self.device}")
                return
                
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.info(f"Retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"Failed to load embedding model after {max_retries} attempts: {e}")
                    raise
    
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for texts"""
        try:
            if not self.model:
                raise RuntimeError("Embedding model not initialized")
            
            # Generate embeddings in thread pool
            loop = asyncio.get_event_loop()
            embeddings = await loop.run_in_executor(
                None,
                lambda: self.model.encode(texts, convert_to_tensor=False)
            )
            
            # Convert to list of lists
            return embeddings.tolist()
            
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            raise
    
    async def embed_text(self, text: str) -> List[float]:
        """Generate embedding for single text"""
        embeddings = await self.embed_texts([text])
        return embeddings[0]
