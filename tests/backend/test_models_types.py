"""
Unit tests for Pydantic models
"""

import pytest
from datetime import datetime
from apps.api.src.models.types import (
    PresignRequest,
    PresignResponse,
    IngestRequest,
    IngestResponse,
    QueryRequest,
    QueryResponse,
    QuizRequest,
    QuizResponse,
    QuizQuestion,
    QuestionType,
)


class TestPresignModels:
    """Tests for presign request/response models"""
    
    def test_presign_request_valid(self):
        """Test valid presign request"""
        request = PresignRequest(filename="test.pdf")
        assert request.filename == "test.pdf"
    
    def test_presign_request_missing_filename(self):
        """Test presign request without filename fails"""
        with pytest.raises(Exception):
            PresignRequest()
    
    def test_presign_response_valid(self):
        """Test valid presign response"""
        response = PresignResponse(
            upload_url="https://s3.example.com/upload",
            file_url="https://s3.example.com/file",
            file_id="test-file-id"
        )
        assert response.upload_url == "https://s3.example.com/upload"
        assert response.file_url == "https://s3.example.com/file"
        assert response.file_id == "test-file-id"


class TestIngestModels:
    """Tests for ingest request/response models"""
    
    def test_ingest_request_valid(self):
        """Test valid ingest request"""
        request = IngestRequest(
            file_url="https://s3.example.com/file.pdf",
            original_name="test.pdf"
        )
        assert request.file_url == "https://s3.example.com/file.pdf"
        assert request.original_name == "test.pdf"
    
    def test_ingest_response_valid(self):
        """Test valid ingest response"""
        response = IngestResponse(
            doc_id="test-doc-id",
            pages=10,
            chunks=50,
            status="ready"
        )
        assert response.doc_id == "test-doc-id"
        assert response.pages == 10
        assert response.chunks == 50
        assert response.status == "ready"


class TestQueryModels:
    """Tests for query request/response models"""
    
    def test_query_request_valid(self):
        """Test valid query request"""
        request = QueryRequest(
            query="What is the main topic?",
            top_k=5,
            doc_id="test-doc-id"
        )
        assert request.query == "What is the main topic?"
        assert request.top_k == 5
        assert request.doc_id == "test-doc-id"
    
    def test_query_request_defaults(self):
        """Test query request with defaults"""
        request = QueryRequest(query="Test query")
        assert request.query == "Test query"
        assert request.top_k == 6  # Default value
        assert request.doc_id is None
    
    def test_query_response_valid(self):
        """Test valid query response"""
        response = QueryResponse(
            answer="Test answer",
            citations=[],
            retrieval=[],
            grounding_score=0.95
        )
        assert response.answer == "Test answer"
        assert response.citations == []
        assert response.retrieval == []
        assert response.grounding_score == 0.95


class TestQuizModels:
    """Tests for quiz request/response models"""
    
    def test_quiz_request_valid(self):
        """Test valid quiz request"""
        request = QuizRequest(
            doc_id="test-doc-id",
            topic="Test topic",
            question_types=["short_answer", "multiple_choice"],
            num_questions=10,
            difficulty="medium"
        )
        assert request.doc_id == "test-doc-id"
        assert request.topic == "Test topic"
        assert request.num_questions == 10
        assert request.difficulty == "medium"
    
    def test_quiz_request_defaults(self):
        """Test quiz request with defaults"""
        request = QuizRequest(doc_id="test-doc-id")
        assert request.doc_id == "test-doc-id"
        assert request.num_questions == 5  # Default value
        assert request.difficulty == "medium"
        assert "short_answer" in request.question_types
    
    def test_quiz_question_valid(self):
        """Test valid quiz question"""
        question = QuizQuestion(
            type=QuestionType.SHORT_ANSWER,
            prompt="What is the main topic?",
            answer="Test answer",
            page=1,
            quote="Test quote"
        )
        assert question.type == QuestionType.SHORT_ANSWER
        assert question.prompt == "What is the main topic?"
        assert question.answer == "Test answer"
        assert question.page == 1
    
    def test_quiz_response_valid(self):
        """Test valid quiz response"""
        questions = [
            QuizQuestion(
                type=QuestionType.SHORT_ANSWER,
                prompt="Test question",
                answer="Test answer",
                page=1,
                quote="Test quote"
            )
        ]
        response = QuizResponse(
            questions=questions,
            doc_id="test-doc-id",
            generated_at=datetime.utcnow().isoformat(),
            estimated_time=10
        )
        assert len(response.questions) == 1
        assert response.doc_id == "test-doc-id"
        assert response.estimated_time == 10

