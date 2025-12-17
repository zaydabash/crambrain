"""
Pytest configuration and fixtures for CramBrain tests
"""

import pytest
import os
from typing import Generator
from unittest.mock import Mock, MagicMock, AsyncMock

# Set test environment variables
os.environ["TESTING"] = "true"
os.environ["CHROMA_PERSIST_DIR"] = "/tmp/test_chroma"
os.environ["OPENAI_API_KEY"] = "test-key"
os.environ["S3_ENDPOINT_URL"] = "https://s3.test.example.com"
os.environ["S3_REGION"] = "us-west-004"
os.environ["S3_BUCKET"] = "test-bucket"
os.environ["S3_ACCESS_KEY"] = "test-access-key"
os.environ["S3_SECRET_KEY"] = "test-secret-key"

@pytest.fixture
def mock_settings():
    """Mock settings for testing"""
    settings = Mock()
    settings.openai_api_key = "test-key"
    settings.chroma_persist_dir = "/tmp/test_chroma"
    settings.chroma_collection = "test_collection"
    settings.s3_endpoint_url = "https://s3.test.example.com"
    settings.s3_region = "us-west-004"
    settings.s3_bucket = "test-bucket"
    settings.s3_access_key = "test-access-key"
    settings.s3_secret_key = "test-secret-key"
    settings.api_key = None
    settings.allowed_origins = ["*"]
    settings.rate_limit_requests = 100
    settings.rate_limit_window = 3600
    return settings

@pytest.fixture
def mock_s3_service():
    """Mock S3 service for testing"""
    service = Mock()
    service.upload_file = AsyncMock(return_value="https://test.example.com/file.pdf")
    service.download_file = AsyncMock(return_value=b"test file content")
    service.generate_presigned_upload_url = AsyncMock(
        return_value="https://s3.test.example.com/presigned-url"
    )
    service.get_public_url = Mock(return_value="https://test.example.com/file.pdf")
    return service

@pytest.fixture
def mock_embedding_service():
    """Mock embedding service for testing"""
    service = Mock()
    service.embed_text = AsyncMock(return_value=[0.1] * 384)  # Mock embedding vector
    service.embed_texts = AsyncMock(return_value=[[0.1] * 384] * 5)
    return service

@pytest.fixture
def mock_chroma_store():
    """Mock Chroma store for testing"""
    store = Mock()
    store.initialize = AsyncMock()
    store.store_chunks = AsyncMock()
    store.search = AsyncMock(return_value=[])
    store.get_document = AsyncMock(return_value=None)
    store.list_documents = AsyncMock(return_value=[])
    return store

@pytest.fixture
def sample_pdf_content():
    """Sample PDF content for testing"""
    return b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\nxref\n0 1\ntrailer\n<<\n/Root 1 0 R\n>>\n%%EOF"

@pytest.fixture
def sample_chunk_data():
    """Sample chunk data for testing"""
    return {
        "chunk_id": "test-chunk-1",
        "text": "This is a test chunk of text.",
        "page": 1,
        "chunk_type": "text",
        "embedding": [0.1] * 384,
    }
