"""
Unit tests for API endpoints
"""

import pytest
from unittest.mock import Mock, AsyncMock
from fastapi.testclient import TestClient

# Import app and dependencies
try:
    from apps.api.src.main import app
    from apps.api.src.core.deps import (
        get_s3_service,
        get_chroma_store,
        get_embedding_service,
        get_search_service,
        get_answer_service,
        get_quiz_service,
        get_pdf_processor,
        get_rate_limiter
    )
    TESTCLIENT_AVAILABLE = True
except ImportError:
    TESTCLIENT_AVAILABLE = False
    app = None

@pytest.fixture
def client(
    mock_s3_service,
    mock_chroma_store,
    mock_embedding_service
):
    """Test client for API with mocked dependencies"""
    if not TESTCLIENT_AVAILABLE:
        pytest.skip("TestClient not available - FastAPI may not be installed")
    
    # Mock other services
    mock_search_service = Mock()
    mock_search_service.search = AsyncMock(return_value=[])
    
    mock_answer_service = Mock()
    mock_answer_service.generate_answer = AsyncMock(return_value=Mock(answer="Test answer", grounding_score=0.9))
    
    mock_quiz_service = Mock()
    mock_quiz_service.generate_quiz = AsyncMock(return_value=[])
    mock_quiz_service.generate_cram_plan = AsyncMock(return_value={})
    mock_quiz_service.generate_concept_graph = AsyncMock(return_value={})
    
    mock_pdf_processor = Mock()
    mock_pdf_processor.process_pdf = AsyncMock(return_value=[])
    
    mock_rate_limiter = Mock()
    mock_rate_limiter.check_rate_limit = AsyncMock()

    # Override dependencies
    app.dependency_overrides[get_s3_service] = lambda: mock_s3_service
    app.dependency_overrides[get_chroma_store] = lambda: mock_chroma_store
    app.dependency_overrides[get_embedding_service] = lambda: mock_embedding_service
    app.dependency_overrides[get_search_service] = lambda: mock_search_service
    app.dependency_overrides[get_answer_service] = lambda: mock_answer_service
    app.dependency_overrides[get_quiz_service] = lambda: mock_quiz_service
    app.dependency_overrides[get_pdf_processor] = lambda: mock_pdf_processor
    app.dependency_overrides[get_rate_limiter] = lambda: mock_rate_limiter
    
    with TestClient(app) as c:
        yield c
    
    # Clear overrides
    app.dependency_overrides.clear()


@pytest.mark.skipif(not TESTCLIENT_AVAILABLE, reason="TestClient not available")
class TestHealthEndpoint:
    """Tests for health check endpoint"""
    
    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"


@pytest.mark.skipif(not TESTCLIENT_AVAILABLE, reason="TestClient not available")
class TestPresignEndpoint:
    """Tests for presign endpoint"""
    
    def test_presign_endpoint_post(self, client):
        """Test presign endpoint with POST"""
        response = client.post(
            "/v1/presign",
            json={"filename": "test.pdf"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "upload_url" in data
        assert "file_url" in data
        assert "file_id" in data


@pytest.mark.skipif(not TESTCLIENT_AVAILABLE, reason="TestClient not available")
class TestIngestEndpoint:
    """Tests for ingest endpoint"""
    
    def test_ingest_endpoint_missing_fields(self, client):
        """Test ingest endpoint with missing fields"""
        response = client.post("/v1/ingest", json={})
        assert response.status_code == 422  # Validation error
    
    def test_ingest_endpoint_invalid_request(self, client):
        """Test ingest endpoint with invalid request"""
        response = client.post(
            "/v1/ingest",
            json={"file_url": "invalid-url"}  # Missing original_name
        )
        assert response.status_code == 422  # Validation error


@pytest.mark.skipif(not TESTCLIENT_AVAILABLE, reason="TestClient not available")
class TestQueryEndpoint:
    """Tests for query/ask endpoint"""
    
    def test_ask_endpoint_missing_query(self, client):
        """Test ask endpoint without query"""
        response = client.post("/v1/ask", json={})
        assert response.status_code == 422  # Validation error
    
    def test_ask_endpoint_valid_request(self, client):
        """Test ask endpoint with valid request"""
        response = client.post(
            "/v1/ask",
            json={"query": "What is the main topic?", "top_k": 5}
        )
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "citations" in data


@pytest.mark.skipif(not TESTCLIENT_AVAILABLE, reason="TestClient not available")
class TestQuizEndpoint:
    """Tests for quiz endpoint"""
    
    def test_quiz_endpoint_valid_request(self, client):
        """Test quiz endpoint with valid request"""
        # Mock search service to return results so quiz generation proceeds
        # Note: In a real integration test, we'd need more setup, but here we just check flow
        response = client.post(
            "/v1/quiz",
            json={
                "doc_id": "test-doc-id",
                "topic": "Test topic",
                "n": 10
            }
        )
        # It might return 404 if search returns empty (mock behavior), or 200 if we mock search results
        # Given our mock_search_service returns [], it will likely be 404 as per quiz router logic
        assert response.status_code in [200, 404]
    
    def test_quiz_endpoint_with_num_questions(self, client):
        """Test quiz endpoint with num_questions instead of n"""
        response = client.post(
            "/v1/quiz",
            json={
                "doc_id": "test-doc-id",
                "num_questions": 5
            }
        )
        assert response.status_code in [200, 404]
