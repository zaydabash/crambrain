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
                    "chunk_type": chunk.chunk_type,
                    "page": chunk.page,
                    "headings": ",".join(chunk.headings or []),
                    "file_url": metadata.get("file_url", ""),
                    "preview_urls": ",".join(metadata.get("preview_urls", [])),
                    **chunk.metadata
                }
                # Chroma rejects None metadata values, so only include
                # optional fields when they're actually set.
                if chunk.bbox_id is not None:
                    chunk_metadata["bbox_id"] = chunk.bbox_id
                if chunk.char_start is not None:
                    chunk_metadata["char_start"] = chunk.char_start
                if chunk.char_end is not None:
                    chunk_metadata["char_end"] = chunk.char_end
                metadatas.append(chunk_metadata)

            # Add document metadata. "chunk_type" marks this record as
            # document-level metadata so it can be filtered out of chunk
            # queries with a simple $eq match (chromadb has no $exists op).
            doc_metadata = {
                "doc_id": doc_id,
                "chunk_type": "document_metadata",
                "original_name": metadata.get("original_name", ""),
                "file_url": metadata.get("file_url", ""),
                "preview_urls": ",".join(metadata.get("preview_urls", [])),
                "pages": metadata.get("pages", 0),
                "chunks": metadata.get("chunks", len(chunks)),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }

            # Store chunks
            if embeddings:
                self.collection.add(
                    embeddings=embeddings,
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )

            # Store document metadata separately. Fall back to the
            # all-MiniLM-L6-v2 dimension when there are no real chunks
            # (e.g. an empty document) to keep this dummy embedding's
            # dimension consistent with the rest of the collection.
            embedding_dim = len(embeddings[0]) if embeddings else 384
            self.collection.add(
                embeddings=[[0.0] * embedding_dim],  # Dummy embedding
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

            # Format results, skipping the dummy document-metadata records
            formatted_results = []
            for i in range(len(results["ids"][0])):
                metadata = results["metadatas"][0][i]
                if metadata.get("chunk_type") == "document_metadata":
                    continue
                result = {
                    "id": results["ids"][0][i],
                    "text": results["documents"][0][i],
                    "metadata": metadata,
                    "score": 1 - results["distances"][0][i]  # Convert distance to similarity
                }
                formatted_results.append(result)

            return formatted_results
            
        except Exception as e:
            logger.error(f"Failed to search Chroma: {e}")
            raise
    
    async def get_all_chunks(self, doc_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all stored chunks (excluding document-metadata records), optionally filtered by doc_id"""
        try:
            if not self.collection:
                raise RuntimeError("Chroma collection not initialized")

            where_clause = {"doc_id": doc_id} if doc_id else None
            results = self.collection.get(
                where=where_clause,
                include=["documents", "metadatas"]
            )

            chunks = []
            for i, chunk_id in enumerate(results["ids"]):
                metadata = results["metadatas"][i]
                if metadata.get("chunk_type") == "document_metadata":
                    continue
                chunks.append({
                    "id": chunk_id,
                    "text": results["documents"][i],
                    "metadata": metadata,
                })

            return chunks

        except Exception as e:
            logger.error(f"Failed to get all chunks: {e}")
            raise

    async def list_documents(self) -> List[DocumentMetadata]:
        """List all documents"""
        try:
            if not self.collection:
                raise RuntimeError("Chroma collection not initialized")
            
            # Get all document-metadata records (chromadb has no $exists
            # operator, so document metadata is tagged with chunk_type
            # and matched with a plain equality filter).
            results = self.collection.get(
                where={"chunk_type": "document_metadata"},
                include=["metadatas"]
            )

            documents = []
            for metadata in results["metadatas"]:
                doc = DocumentMetadata(
                    doc_id=metadata["doc_id"],
                    original_name=metadata["original_name"],
                    file_url=metadata["file_url"],
                    preview_urls=metadata["preview_urls"].split(",") if metadata["preview_urls"] else [],
                    pages=metadata["pages"],
                    chunks=metadata.get("chunks", 0),
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
                where={"$and": [{"doc_id": doc_id}, {"chunk_type": "document_metadata"}]},
                include=["metadatas"]
            )

            for metadata in results["metadatas"]:
                return DocumentMetadata(
                    doc_id=metadata["doc_id"],
                    original_name=metadata["original_name"],
                    file_url=metadata["file_url"],
                    preview_urls=metadata["preview_urls"].split(",") if metadata["preview_urls"] else [],
                    pages=metadata["pages"],
                    chunks=metadata.get("chunks", 0),
                    created_at=datetime.fromisoformat(metadata["created_at"]),
                    updated_at=datetime.fromisoformat(metadata["updated_at"])
                )

            return None
            
        except Exception as e:
            logger.error(f"Failed to get document: {e}")
            raise
