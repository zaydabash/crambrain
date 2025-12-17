"""
CramBrain API - Simple Working Version
"""

import os
import uuid
import logging
from datetime import datetime
from typing import Optional
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Simple models
class PresignRequest(BaseModel):
    filename: str

class PresignResponse(BaseModel):
    upload_url: str
    file_url: str
    file_id: str

class IngestRequest(BaseModel):
    file_url: str
    original_name: str

class IngestResponse(BaseModel):
    doc_id: str
    pages: int
    chunks: int
    status: str

class QueryRequest(BaseModel):
    query: str
    top_k: int = 6
    doc_id: Optional[str] = None

class QueryResponse(BaseModel):
    answer: str
    citations: list
    retrieval: list

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="CramBrain API",
    description="AI-powered study assistant with PDF processing and Q&A",
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
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "api": "ok"
        }
    }

# Presign endpoint
@app.post("/v1/presign", response_model=PresignResponse)
async def create_presigned_upload(request: PresignRequest):
    """Generate presigned URL for S3 upload"""
    try:
        # Generate unique file key
        file_id = str(uuid.uuid4())
        file_key = f"docs/{file_id}.pdf"
        
        # For now, return mock URLs (you'll need to implement actual S3 presigning)
        upload_url = f"https://mock-s3.com/upload/{file_key}"
        file_url = f"https://mock-s3.com/file/{file_key}"
        
        return PresignResponse(
            upload_url=upload_url,
            file_url=file_url,
            file_id=file_id
        )
        
    except Exception as e:
        logger.error(f"Failed to generate presigned URL: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate presigned URL")

# Ingest endpoint
@app.post("/v1/ingest", response_model=IngestResponse)
async def ingest_document(request: IngestRequest):
    """Ingest document: download, parse, chunk, embed, and store"""
    try:
        logger.info(f"Starting ingestion for document: {request.file_url}")
        
        # For now, return mock response
        doc_id = str(uuid.uuid4())
        
        return IngestResponse(
            doc_id=doc_id,
            pages=5,  # Mock page count
            chunks=20,  # Mock chunk count
            status="ready"
        )
        
    except Exception as e:
        logger.error(f"Failed to ingest document: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to ingest document: {str(e)}")

# Ask endpoint
@app.post("/v1/ask", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    """Ask question with grounded answer and citations"""
    try:
        logger.info(f"Processing question: {request.query}")
        
        # Mock response for now
        answer = f"This is a mock answer for your question: '{request.query}'. The system is working but needs full implementation."
        
        return QueryResponse(
            answer=answer,
            citations=[],
            retrieval=[]
        )
        
    except Exception as e:
        logger.error(f"Failed to process question: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process question: {str(e)}")

# Quiz endpoint
@app.post("/v1/quiz")
async def generate_quiz(request: dict):
    """Generate quiz questions from documents"""
    try:
        logger.info("Generating quiz...")
        
        # Mock quiz response
        return {
            "questions": [
                {
                    "type": "short_answer",
                    "prompt": "What is the main topic of this document?",
                    "answer": "Mock answer",
                    "page": 1,
                    "quote": "Mock quote from page 1"
                }
            ],
            "doc_id": request.get("doc_id")
        }
        
    except Exception as e:
        logger.error(f"Failed to generate quiz: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate quiz: {str(e)}")

# Docs endpoint
@app.get("/v1/docs")
async def list_documents():
    """List all documents"""
    try:
        return {"documents": []}
        
    except Exception as e:
        logger.error(f"Failed to list documents: {e}")
        raise HTTPException(status_code=500, detail="Failed to list documents")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
