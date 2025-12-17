"""
Enhanced Pydantic models for CramBrain API with advanced features
"""

from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class QuestionType(str, Enum):
    """Question types for quiz generation"""
    SHORT_ANSWER = "short_answer"
    MULTIPLE_CHOICE = "multiple_choice"
    CLOZE = "cloze"

# Enhanced Citation with page anchors and visual references
class Citation(BaseModel):
    """Citation with page anchor, metadata, and visual references"""
    doc_id: str = Field(..., description="Document ID")
    page: int = Field(..., description="Page number")
    text: str = Field(..., description="Cited text snippet")
    score: float = Field(..., description="Relevance score")
    chunk_id: str = Field(..., description="Chunk ID")
    bbox_id: Optional[str] = Field(None, description="Bounding box ID")
    bbox: Optional[tuple] = Field(None, description="Bounding box coordinates")
    chunk_type: str = Field("text", description="Type of chunk (text/image/table)")
    preview_url: str = Field(..., description="Page preview URL")
    source_url: str = Field(..., description="Source URL")
    quote: str = Field(..., description="Source quote")
    thumbnail_url: Optional[str] = Field(None, description="Thumbnail image URL")

# Enhanced RetrievalResult with multimodal support
class RetrievalResult(BaseModel):
    """Retrieval result with enhanced metadata"""
    doc_id: str = Field(..., description="Document ID")
    page: int = Field(..., description="Page number")
    text: str = Field(..., description="Retrieved text")
    score: float = Field(..., description="Relevance score")
    chunk_id: str = Field(..., description="Chunk ID")
    chunk_type: str = Field("text", description="Type of chunk")
    bbox_id: Optional[str] = Field(None, description="Bounding box ID")
    preview_url: str = Field(..., description="Page preview URL")
    source_url: str = Field(..., description="Source URL")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class AnswerResult(BaseModel):
    """Answer with citations and grounding validation"""
    answer: str = Field(..., description="Generated answer")
    citations: List[Citation] = Field(..., description="Source citations")
    grounding_score: float = Field(..., description="Answer grounding confidence")
    retrieval_quality: str = Field(..., description="Quality of retrieval")

# Enhanced QuizQuestion with multiple types and explanations
class QuizQuestion(BaseModel):
    """Quiz question with enhanced features"""
    type: QuestionType = Field(..., description="Question type")
    prompt: str = Field(..., description="Question prompt")
    answer: str = Field(..., description="Correct answer")
    page: int = Field(..., description="Source page")
    quote: str = Field(..., description="Source quote")
    options: Optional[List[str]] = Field(None, description="Multiple choice options")
    explanation: Optional[str] = Field(None, description="Answer explanation")
    difficulty: str = Field("medium", description="Difficulty level")
    time_limit: Optional[int] = Field(None, description="Time limit in seconds")
    hints: Optional[List[str]] = Field(None, description="Progressive hints")

class QuizResult(BaseModel):
    """Generated quiz with metadata"""
    questions: List[QuizQuestion] = Field(..., description="Generated questions")
    doc_id: Optional[str] = Field(None, description="Document ID")
    generated_at: str = Field(..., description="Generation timestamp")
    estimated_time: int = Field(..., description="Estimated completion time in minutes")

# Request/Response Models
class PresignRequest(BaseModel):
    """Request for presigned upload URL"""
    filename: str = Field(..., description="Original filename")

class PresignResponse(BaseModel):
    """Response with presigned upload URL"""
    upload_url: str = Field(..., description="Presigned upload URL")
    file_url: str = Field(..., description="Public file URL")
    file_id: str = Field(..., description="Unique file identifier")

class IngestRequest(BaseModel):
    """Request to ingest document"""
    file_url: str = Field(..., description="S3 file URL")
    original_name: str = Field(..., description="Original filename")

class IngestResponse(BaseModel):
    """Response after document ingestion"""
    doc_id: str = Field(..., description="Document ID")
    pages: int = Field(..., description="Number of pages processed")
    chunks: int = Field(..., description="Number of chunks created")
    status: str = Field(..., description="Processing status")

class QueryRequest(BaseModel):
    """Query request with enhanced options"""
    query: str = Field(..., description="User question")
    top_k: int = Field(6, ge=1, le=20, description="Number of retrieval results")
    doc_id: Optional[str] = Field(None, description="Filter by document ID")
    mode: str = Field("answer", description="Query mode (answer/explain/example)")

class QueryResponse(BaseModel):
    """Query response with enhanced features"""
    answer: str = Field(..., description="Generated answer")
    citations: List[Citation] = Field(..., description="Source citations")
    retrieval: List[RetrievalResult] = Field(..., description="Retrieval results")
    grounding_score: float = Field(..., description="Answer grounding confidence")
    next_mode: Optional[str] = Field(None, description="Suggested next mode")

class QuizRequest(BaseModel):
    """Quiz generation request with enhanced options"""
    doc_id: Optional[str] = Field(None, description="Document ID")
    topic: Optional[str] = Field(None, description="Specific topic to focus on")
    question_types: List[str] = Field(["short_answer", "multiple_choice"], description="Question types")
    num_questions: int = Field(5, ge=1, le=20, description="Number of questions")
    difficulty: str = Field("medium", description="Difficulty level")
    time_limit: Optional[int] = Field(None, description="Time limit in minutes")

class QuizResponse(BaseModel):
    """Quiz generation response"""
    questions: List[QuizQuestion] = Field(..., description="Generated questions")
    doc_id: Optional[str] = Field(None, description="Document ID")
    generated_at: str = Field(..., description="Generation timestamp")
    estimated_time: int = Field(..., description="Estimated completion time")

class DocumentMetadata(BaseModel):
    """Document metadata with enhanced information"""
    doc_id: str = Field(..., description="Document ID")
    original_name: str = Field(..., description="Original filename")
    file_url: str = Field(..., description="File URL")
    preview_urls: List[str] = Field(..., description="Page preview URLs")
    pages: int = Field(..., description="Number of pages")
    chunks: int = Field(..., description="Number of chunks")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class DocumentResponse(BaseModel):
    """Document response"""
    doc_id: str = Field(..., description="Document ID")
    original_name: str = Field(..., description="Original filename")
    file_url: str = Field(..., description="File URL")
    preview_urls: List[str] = Field(..., description="Page preview URLs")
    pages: int = Field(..., description="Number of pages")
    chunks: int = Field(..., description="Number of chunks")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

class DocumentListResponse(BaseModel):
    """List of documents response"""
    documents: List[DocumentMetadata] = Field(..., description="List of documents")

class SearchResponse(BaseModel):
    """Search response"""
    query: str = Field(..., description="Search query")
    results: List[RetrievalResult] = Field(..., description="Search results")
    total: int = Field(..., description="Total number of results")

# Internal Models with Enhanced Features
class ImageDataModel(BaseModel):
    """Extracted image data with OCR"""
    page: int = Field(..., description="Page number")
    bbox: tuple = Field(..., description="Bounding box (x0, y0, x1, y1)")
    text: str = Field(default="", description="OCR extracted text")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="OCR confidence score")

class TableDataModel(BaseModel):
    """Extracted table data"""
    page: int = Field(..., description="Page number")
    bbox: tuple = Field(..., description="Bounding box (x0, y0, x1, y1)")
    data: List[List[str]] = Field(default_factory=list, description="Table data rows")
    headers: List[str] = Field(default_factory=list, description="Table headers")

class PageData(BaseModel):
    """Page data from PDF processing with multimodal content"""
    page_number: int = Field(..., description="Page number")
    text: str = Field(..., description="Page text content")
    chunks: List["ChunkData"] = Field(..., description="Text chunks")
    spans: List[Dict[str, Any]] = Field(default_factory=list, description="Text spans with bboxes")
    headings: List[str] = Field(default_factory=list, description="Extracted headings")
    slide_title_guess: Optional[str] = Field(None, description="Guessed slide title")
    preview_image: Optional[bytes] = Field(None, description="Page preview image")
    images: List[ImageDataModel] = Field(default_factory=list, description="Extracted images")
    tables: List[TableDataModel] = Field(default_factory=list, description="Extracted tables")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Page metadata")

class ChunkData(BaseModel):
    """Chunk data for vector storage with enhanced metadata"""
    chunk_id: str = Field(..., description="Unique chunk identifier")
    text: str = Field(..., description="Chunk text content")
    page: int = Field(..., description="Page number")
    chunk_type: str = Field("text", description="Type of chunk (text/image/table)")
    bbox_id: Optional[str] = Field(None, description="Bounding box ID")
    char_start: Optional[int] = Field(None, description="Character start position")
    char_end: Optional[int] = Field(None, description="Character end position")
    headings: Optional[List[str]] = Field(None, description="Associated headings")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Chunk metadata")
    embedding: Optional[List[float]] = Field(None, description="Text embedding vector")

# Advanced Feature Models

# Cram Plan Models
class CramPlan(BaseModel):
    """20-minute cram plan"""
    plan_id: str = Field(..., description="Plan ID")
    doc_id: str = Field(..., description="Document ID")
    time_minutes: int = Field(..., description="Total time in minutes")
    sections: List["CramSection"] = Field(..., description="Study sections")
    generated_at: str = Field(..., description="Generation timestamp")

class CramSection(BaseModel):
    """Study section in cram plan"""
    title: str = Field(..., description="Section title")
    time_minutes: int = Field(..., description="Time allocated")
    pages: List[int] = Field(..., description="Pages to study")
    activities: List[str] = Field(..., description="Study activities")
    priority: str = Field("medium", description="Priority level")

# Concept Graph Models
class ConceptGraph(BaseModel):
    """Concept graph showing topic connections"""
    graph_id: str = Field(..., description="Graph ID")
    doc_id: str = Field(..., description="Document ID")
    nodes: List["ConceptNode"] = Field(..., description="Concept nodes")
    edges: List["ConceptEdge"] = Field(..., description="Concept relationships")
    generated_at: str = Field(..., description="Generation timestamp")

class ConceptNode(BaseModel):
    """Concept node in graph"""
    id: str = Field(..., description="Node ID")
    label: str = Field(..., description="Concept label")
    pages: List[int] = Field(..., description="Pages where concept appears")
    importance: float = Field(..., description="Concept importance score")
    type: str = Field("concept", description="Node type")

class ConceptEdge(BaseModel):
    """Concept relationship edge"""
    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    relationship: str = Field(..., description="Relationship type")
    strength: float = Field(..., description="Relationship strength")

# Spaced Repetition Models
class StudySession(BaseModel):
    """Study session with spaced repetition"""
    session_id: str = Field(..., description="Session ID")
    user_id: str = Field(..., description="User ID")
    doc_id: str = Field(..., description="Document ID")
    questions: List["StudyQuestion"] = Field(..., description="Questions in session")
    started_at: str = Field(..., description="Session start time")
    completed_at: Optional[str] = Field(None, description="Session completion time")
    score: Optional[float] = Field(None, description="Session score")

class StudyQuestion(BaseModel):
    """Question in study session"""
    question_id: str = Field(..., description="Question ID")
    question: str = Field(..., description="Question text")
    answer: str = Field(..., description="Correct answer")
    user_answer: Optional[str] = Field(None, description="User's answer")
    is_correct: Optional[bool] = Field(None, description="Whether answer is correct")
    time_spent: Optional[int] = Field(None, description="Time spent in seconds")
    next_review: Optional[str] = Field(None, description="Next review date")

# Mode Switching Models
class LearningMode(BaseModel):
    """Learning mode configuration"""
    mode: str = Field(..., description="Mode type (explain/example/test)")
    doc_id: str = Field(..., description="Document ID")
    topic: str = Field(..., description="Topic to focus on")
    difficulty: str = Field("medium", description="Difficulty level")
    time_limit: Optional[int] = Field(None, description="Time limit in minutes")

class ModeResponse(BaseModel):
    """Response for mode switching"""
    mode: str = Field(..., description="Current mode")
    content: str = Field(..., description="Mode-specific content")
    next_mode: Optional[str] = Field(None, description="Suggested next mode")
    progress: float = Field(..., description="Learning progress")

# Update forward references
PageData.model_rebuild()
ChunkData.model_rebuild()
CramPlan.model_rebuild()
CramSection.model_rebuild()
ConceptGraph.model_rebuild()
ConceptNode.model_rebuild()
ConceptEdge.model_rebuild()
StudySession.model_rebuild()
StudyQuestion.model_rebuild()
