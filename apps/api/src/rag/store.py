"""
Chroma vector store implementation
"""

import uuid
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import chromadb
from chromadb.config import Settings as ChromaSettings
from models.types import ChunkData, DocumentMetadata

logger = logging.getLogger(__name__)

class ChromaStore:
    """Chroma vector store with persistence"""
    
    def __init__(self, settings):
        self.persist_directory = settings.chroma_persist_dir
        self.collection_name = settings.chroma_collection
        self.client: Optional[chromadb.ClientAPI] = None
        self.collection: Optional[chromadb.Collection] = None
    
    async def initialize(self):
        """Initialize Chroma client and collection"""
        try:
            # Create persistent client
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            
            logger.info(f"Chroma store initialized: {self.collection_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Chroma store: {e}")
            raise
    
    async def store_chunks(
        self,
        doc_id: str,
        chunks: List[ChunkData],
        embeddings: List[List[float]],
        metadata: Dict[str, Any]
    ):
        """Store document chunks in Chroma"""
        try:
            if not self.collection:
                raise RuntimeError("Chroma collection not initialized")
            
            # Prepare data for Chroma
            ids = []
            documents = []
            metadatas = []
            
            for i, chunk in enumerate(chunks):
                chunk_id = f"{doc_id}:{chunk.page}:{i}"
                ids.append(chunk_id)
                documents.append(chunk.text)
                
                chunk_metadata = {
                    "doc_id": doc_id,
                    "page": chunk.page,
                    "bbox_id": chunk.bbox_id,
                    "char_start": chunk.char_start,
                    "char_end": chunk.char_end,
                    "headings": ",".join(chunk.headings),
                    **chunk.metadata
                }
                metadatas.append(chunk_metadata)
            
            # Add document metadata
            doc_metadata = {
                "doc_id": doc_id,
                "original_name": metadata.get("original_name", ""),
                "file_url": metadata.get("file_url", ""),
                "preview_urls": ",".join(metadata.get("preview_urls", [])),
                "pages": metadata.get("pages", 0),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # Store chunks
            self.collection.add(
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            # Store document metadata separately
            self.collection.add(
                embeddings=[[0.0] * len(embeddings[0])],  # Dummy embedding
                documents=[f"DOCUMENT_METADATA:{doc_id}"],
                metadatas=[doc_metadata],
                ids=[f"doc_meta:{doc_id}"]
            )
            
            logger.info(f"Stored {len(chunks)} chunks for document {doc_id}")
            
        except Exception as e:
            logger.error(f"Failed to store chunks: {e}")
            raise
    
    async def search(
        self,
        query_embedding: List[float],
        doc_id: Optional[str] = None,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """Search for similar chunks"""
        try:
            if not self.collection:
                raise RuntimeError("Chroma collection not initialized")
            
            # Build where clause
            where_clause = {}
            if doc_id:
                where_clause["doc_id"] = doc_id
            
            # Search
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=where_clause
            )
            
            # Format results
            formatted_results = []
            for i in range(len(results["ids"][0])):
                result = {
                    "id": results["ids"][0][i],
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "score": 1 - results["distances"][0][i]  # Convert distance to similarity
                }
                formatted_results.append(result)
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Failed to search Chroma: {e}")
            raise
    
    async def list_documents(self) -> List[DocumentMetadata]:
        """List all documents"""
        try:
            if not self.collection:
                raise RuntimeError("Chroma collection not initialized")
            
            # Get all document metadata
            results = self.collection.get(
                where={"doc_id": {"$exists": True}},
                include=["metadatas"]
            )
            
            documents = []
            for metadata in results["metadatas"]:
                if metadata.get("original_name"):  # Skip chunk metadata
                    doc = DocumentMetadata(
                        doc_id=metadata["doc_id"],
                        original_name=metadata["original_name"],
                        file_url=metadata["file_url"],
                        preview_urls=metadata["preview_urls"].split(",") if metadata["preview_urls"] else [],
                        pages=metadata["pages"],
                        chunks=0,  # TODO: Count chunks
                        created_at=datetime.fromisoformat(metadata["created_at"]),
                        updated_at=datetime.fromisoformat(metadata["updated_at"])
                    )
                    documents.append(doc)
            
            return documents
            
        except Exception as e:
            logger.error(f"Failed to list documents: {e}")
            raise
    
    async def get_document(self, doc_id: str) -> Optional[DocumentMetadata]:
        """Get document metadata"""
        try:
            if not self.collection:
                raise RuntimeError("Chroma collection not initialized")
            
            results = self.collection.get(
                where={"doc_id": doc_id},
                include=["metadatas"]
            )
            
            for metadata in results["metadatas"]:
                if metadata.get("original_name"):  # Document metadata
                    return DocumentMetadata(
                        doc_id=metadata["doc_id"],
                        original_name=metadata["original_name"],
                        file_url=metadata["file_url"],
                        preview_urls=metadata["preview_urls"].split(",") if metadata["preview_urls"] else [],
                        pages=metadata["pages"],
                        chunks=0,  # TODO: Count chunks
                        created_at=datetime.fromisoformat(metadata["created_at"]),
                        updated_at=datetime.fromisoformat(metadata["updated_at"])
                    )
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get document: {e}")
            raise
