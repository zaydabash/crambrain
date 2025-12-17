"""
Simple API test without heavy dependencies
"""

import os
import logging
from datetime import datetime
from typing import Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Simple models for testing
class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str

class PresignRequest(BaseModel):
    filename: str

class PresignResponse(BaseModel):
    upload_url: str
    file_url: str
    file_id: str

# Create FastAPI app
app = FastAPI(
    title="CramBrain API",
    description="AI-powered study assistant with strict grounding and advanced RAG",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version="1.0.0"
    )

# Presign endpoint (mock)
@app.post("/v1/presign", response_model=PresignResponse)
async def create_presigned_upload(request: PresignRequest):
    """Generate presigned URL for S3 upload (mock)"""
    return PresignResponse(
        upload_url=f"https://mock-upload-url.com/{request.filename}",
        file_url=f"https://mock-file-url.com/{request.filename}",
        file_id=f"mock-file-id-{request.filename}"
    )

# Ingest endpoint (mock)
@app.post("/v1/ingest")
async def ingest_document(request: dict):
    """Ingest document (mock)"""
    return {
        "doc_id": "mock-doc-id",
        "pages": 5,
        "chunks": 25,
        "status": "ready"
    }

# Ask endpoint (mock)
@app.post("/v1/ask")
async def ask_question(request: dict):
    """Ask question (mock)"""
    return {
        "answer": f"Mock answer for: {request.get('query', 'No query provided')}",
        "citations": [
            {
                "page": 1,
                "text": "Mock citation text",
                "score": 0.95,
                "chunk_id": "mock-chunk-1",
                "chunk_type": "text",
                "preview_url": "https://mock-preview.com/page1",
                "source_url": "https://mock-source.com/page1",
                "quote": "Mock quote from page 1"
            }
        ],
        "retrieval": [],
        "grounding_score": 0.95,
        "next_mode": "example"
    }

# Quiz endpoint (mock)
@app.post("/v1/quiz")
async def generate_quiz(request: dict):
    """Generate quiz (mock)"""
    return {
        "questions": [
            {
                "type": "short_answer",
                "prompt": "What is the main topic discussed?",
                "answer": "Mock answer",
                "page": 1,
                "quote": "Mock quote",
                "explanation": "Mock explanation",
                "difficulty": "medium",
                "time_limit": 60
            }
        ],
        "doc_id": request.get("doc_id"),
        "generated_at": datetime.utcnow().isoformat(),
        "estimated_time": 5
    }

# Cram plan endpoint (mock)
@app.post("/v1/cram-plan")
async def generate_cram_plan(request: dict):
    """Generate a 20-minute cram plan (mock)"""
    return {
        "plan_id": "mock-plan-id",
        "doc_id": request.get("doc_id"),
        "time_minutes": request.get("time_minutes", 20),
        "sections": [
            {
                "title": "Quick Review",
                "time_minutes": 7,
                "pages": [1, 2, 3],
                "activities": ["skim", "highlight key points"],
                "priority": "high"
            },
            {
                "title": "Practice Questions",
                "time_minutes": 8,
                "pages": [4, 5, 6],
                "activities": ["quiz", "self-test"],
                "priority": "high"
            },
            {
                "title": "Final Review",
                "time_minutes": 5,
                "pages": [7, 8, 9, 10],
                "activities": ["summarize", "review mistakes"],
                "priority": "medium"
            }
        ],
        "generated_at": datetime.utcnow().isoformat()
    }

# Concept graph endpoint (mock)
@app.get("/v1/concept-graph/{doc_id}")
async def get_concept_graph(doc_id: str):
    """Get concept graph (mock)"""
    return {
        "graph_id": "mock-graph-id",
        "doc_id": doc_id,
        "nodes": [
            {
                "id": "concept_1",
                "label": "Main Concept",
                "pages": [1, 2, 3],
                "importance": 0.9,
                "type": "concept"
            }
        ],
        "edges": [],
        "generated_at": datetime.utcnow().isoformat()
    }

# Documents endpoint (mock)
@app.get("/v1/docs")
async def list_documents():
    """List all documents (mock)"""
    return {
        "documents": [
            {
                "doc_id": "mock-doc-1",
                "original_name": "sample.pdf",
                "file_url": "https://mock-file.com/sample.pdf",
                "preview_urls": ["https://mock-preview.com/page1"],
                "pages": 10,
                "chunks": 50,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
        ]
    }

# Document detail endpoint (mock)
@app.get("/v1/docs/{doc_id}")
async def get_document(doc_id: str):
    """Get document details (mock)"""
    return {
        "doc_id": doc_id,
        "original_name": "sample.pdf",
        "file_url": f"https://mock-file.com/{doc_id}.pdf",
        "preview_urls": [f"https://mock-preview.com/{doc_id}/page{i}" for i in range(1, 6)],
        "pages": 10,
        "chunks": 50,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }

# Search endpoint (mock)
@app.get("/v1/search")
async def search_documents(
    q: str = "sample query",
    doc_id: Optional[str] = None,
    top_k: int = 10
):
    """Search documents (mock)"""
    return {
        "query": q,
        "results": [
            {
                "doc_id": doc_id or "mock-doc",
                "page": 1,
                "text": f"Mock search result for: {q}",
                "score": 0.95,
                "chunk_id": "mock-chunk-1",
                "chunk_type": "text",
                "preview_url": "https://mock-preview.com/page1",
                "source_url": "https://mock-source.com/page1"
            }
        ],
        "total": 1
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
