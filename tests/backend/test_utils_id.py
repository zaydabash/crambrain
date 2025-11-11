"""
Unit tests for utility ID generation functions
"""

import pytest
from apps.api.src.utils.id import (
    generate_ulid,
    generate_doc_id,
    generate_chunk_id,
    generate_file_hash,
    sanitize_filename,
    base32_encode,
)


class TestULIDGeneration:
    """Tests for ULID generation"""
    
    def test_generate_ulid_returns_string(self):
        """Test that generate_ulid returns a string"""
        ulid = generate_ulid()
        assert isinstance(ulid, str)
        assert len(ulid) > 0
    
    def test_generate_ulid_unique(self):
        """Test that generate_ulid produces unique IDs"""
        ulid1 = generate_ulid()
        ulid2 = generate_ulid()
        assert ulid1 != ulid2
    
    def test_generate_doc_id_returns_string(self):
        """Test that generate_doc_id returns a string"""
        doc_id = generate_doc_id()
        assert isinstance(doc_id, str)
        assert len(doc_id) > 0


class TestChunkIDGeneration:
    """Tests for chunk ID generation"""
    
    def test_generate_chunk_id(self):
        """Test chunk ID generation"""
        doc_id = "test-doc-123"
        page = 5
        chunk_index = 10
        
        chunk_id = generate_chunk_id(doc_id, page, chunk_index)
        assert chunk_id == f"{doc_id}:{page}:{chunk_index}"
    
    def test_generate_chunk_id_unique(self):
        """Test that different inputs produce different chunk IDs"""
        doc_id = "test-doc-123"
        
        chunk_id1 = generate_chunk_id(doc_id, 1, 1)
        chunk_id2 = generate_chunk_id(doc_id, 1, 2)
        chunk_id3 = generate_chunk_id(doc_id, 2, 1)
        
        assert chunk_id1 != chunk_id2
        assert chunk_id1 != chunk_id3
        assert chunk_id2 != chunk_id3


class TestFileHash:
    """Tests for file hash generation"""
    
    def test_generate_file_hash(self):
        """Test file hash generation"""
        content = b"test file content"
        hash_value = generate_file_hash(content)
        
        assert isinstance(hash_value, str)
        assert len(hash_value) == 64  # SHA256 produces 64 hex characters
    
    def test_generate_file_hash_deterministic(self):
        """Test that same content produces same hash"""
        content = b"test file content"
        hash1 = generate_file_hash(content)
        hash2 = generate_file_hash(content)
        
        assert hash1 == hash2
    
    def test_generate_file_hash_different_content(self):
        """Test that different content produces different hashes"""
        content1 = b"test file content 1"
        content2 = b"test file content 2"
        
        hash1 = generate_file_hash(content1)
        hash2 = generate_file_hash(content2)
        
        assert hash1 != hash2


class TestFilenameSanitization:
    """Tests for filename sanitization"""
    
    def test_sanitize_filename_safe(self):
        """Test that safe filenames are unchanged"""
        filename = "test_file.pdf"
        sanitized = sanitize_filename(filename)
        assert sanitized == filename
    
    def test_sanitize_filename_unsafe_chars(self):
        """Test that unsafe characters are replaced"""
        filename = "test<>file:name|.pdf"
        sanitized = sanitize_filename(filename)
        
        assert "<" not in sanitized
        assert ">" not in sanitized
        assert ":" not in sanitized
        assert "|" not in sanitized
    
    def test_sanitize_filename_length_limit(self):
        """Test that long filenames are truncated"""
        long_name = "a" * 150 + ".pdf"
        sanitized = sanitize_filename(long_name)
        
        assert len(sanitized) <= 100
        assert sanitized.endswith(".pdf")
    
    def test_sanitize_filename_preserves_extension(self):
        """Test that file extension is preserved"""
        filename = "test_file.pdf"
        sanitized = sanitize_filename(filename)
        assert sanitized.endswith(".pdf")


class TestBase32Encode:
    """Tests for base32 encoding"""
    
    def test_base32_encode_zero(self):
        """Test encoding zero"""
        result = base32_encode(0)
        assert result == ""
    
    def test_base32_encode_small_number(self):
        """Test encoding small number"""
        result = base32_encode(10)
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_base32_encode_large_number(self):
        """Test encoding large number"""
        result = base32_encode(1000000)
        assert isinstance(result, str)
        assert len(result) > 0

