from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Query, Body
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import logging

from core.deps import get_s3_service, get_pdf_processor, get_chroma_store, get_embedding_service
from utils.id import generate_doc_id
from models.types import PresignRequest, PresignResponse, IngestResponse, IngestRequest

router = APIRouter()
logger = logging.getLogger(__name__)

# Presign endpoint - support both GET and POST
async def _generate_presigned_url(file_name: str, s3_service) -> PresignResponse:
    """Internal helper to generate presigned URL"""
    if not file_name:
        raise HTTPException(status_code=400, detail="filename is required")
    
    # Generate unique file key
    file_id = generate_doc_id()
    file_key = f"docs/{file_id}.pdf"
    
    # Generate presigned URL
    upload_url = await s3_service.generate_presigned_upload_url(file_key, file_name)
    file_url = s3_service.get_public_url(file_key)
    
    logger.info(f"Generated presigned URL for {file_key}")
    
    return PresignResponse(
        upload_url=upload_url,
        file_url=file_url,
        file_id=file_id
    )

@router.get("/presign", response_model=PresignResponse)
async def create_presigned_upload_get(
    filename: str = Query(..., description="Filename for the upload"),
    s3_service = Depends(get_s3_service)
):
    """Generate presigned URL for S3 upload (GET)"""
    try:
        return await _generate_presigned_url(filename, s3_service)
    except Exception as e:
        logger.error(f"Failed to generate presigned URL: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate presigned URL: {str(e)}")

@router.post("/presign", response_model=PresignResponse)
async def create_presigned_upload_post(
    request: PresignRequest,
    s3_service = Depends(get_s3_service)
):
    """Generate presigned URL for S3 upload (POST)"""
    try:
        return await _generate_presigned_url(request.filename, s3_service)
    except Exception as e:
        logger.error(f"Failed to generate presigned URL: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate presigned URL: {str(e)}")

@router.post("/upload", response_model=IngestResponse)
async def upload_and_ingest_document(
    file: UploadFile = File(..., description="PDF file to upload"),
    s3_service = Depends(get_s3_service),
    pdf_processor = Depends(get_pdf_processor),
    chroma_store = Depends(get_chroma_store),
    embedding_service = Depends(get_embedding_service)
):
    """Upload file directly to backend, then to B2, then ingest - avoids CORS issues"""
    try:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        logger.info(f"Starting direct upload for file: {file.filename}")
        
        # Read file content
        file_content = await file.read()
        if len(file_content) == 0:
            raise HTTPException(status_code=400, detail="File is empty")
        
        # Generate unique file key
        file_id = generate_doc_id()
        file_key = f"docs/{file_id}.pdf"
        
        # Upload to B2
        file_url = await s3_service.upload_file(file_content, file_key, 'application/pdf')
        logger.info(f"Uploaded file to B2: {file_url}")
        
        # Process PDF with strict page boundaries
        pages_data = await pdf_processor.process_pdf(file_content, file.filename or "uploaded.pdf")
        
        # Generate embeddings for each chunk
        all_chunks = []
        for page_data in pages_data:
            for chunk in page_data.chunks:
                chunk.embedding = await embedding_service.embed_text(chunk.text)
                all_chunks.append(chunk)
        
        # Store in Chroma with metadata
        doc_id = generate_doc_id()
        await chroma_store.store_chunks(doc_id, all_chunks, {
            "original_name": file.filename or "uploaded.pdf",
            "file_url": file_url,
            "pages": len(pages_data),
            "chunks": len(all_chunks),
            "created_at": datetime.utcnow().isoformat()
        })
        
        logger.info(f"Successfully uploaded and ingested document {doc_id}: {len(pages_data)} pages, {len(all_chunks)} chunks")
        
        return IngestResponse(
            doc_id=doc_id,
            pages=len(pages_data),
            chunks=len(all_chunks),
            status="ready"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to upload and ingest document: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to upload and ingest document: {str(e)}")

@router.post("/ingest", response_model=IngestResponse)
async def ingest_document(
    request: IngestRequest,
    s3_service = Depends(get_s3_service),
    pdf_processor = Depends(get_pdf_processor),
    chroma_store = Depends(get_chroma_store),
    embedding_service = Depends(get_embedding_service)
):
    """Ingest document: download, parse, chunk, embed, and store with strict grounding"""
    try:
        logger.info(f"Starting ingestion for document: {request.file_url}")
        
        # Download PDF from S3
        pdf_content = await s3_service.download_file(request.file_url)
        
        # Process PDF with strict page boundaries
        pages_data = await pdf_processor.process_pdf(pdf_content, request.original_name)
        
        # Generate embeddings for each chunk
        all_chunks = []
        for page_data in pages_data:
            for chunk in page_data.chunks:
                chunk.embedding = await embedding_service.embed_text(chunk.text)
                all_chunks.append(chunk)
        
        # Store in Chroma with metadata
        doc_id = generate_doc_id()
        await chroma_store.store_chunks(doc_id, all_chunks, {
            "original_name": request.original_name,
            "file_url": request.file_url,
            "pages": len(pages_data),
            "chunks": len(all_chunks),
            "created_at": datetime.utcnow().isoformat()
        })
        
        logger.info(f"Successfully ingested document {doc_id}: {len(pages_data)} pages, {len(all_chunks)} chunks")
        
        return IngestResponse(
            doc_id=doc_id,
            pages=len(pages_data),
            chunks=len(all_chunks),
            status="ready"
        )
        
    except Exception as e:
        logger.error(f"Failed to ingest document: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to ingest document: {str(e)}")