"""
Utility functions for ID generation and other helpers
"""

import uuid
import time
import hashlib
from typing import Optional

def generate_ulid() -> str:
    """Generate a ULID (Universally Unique Lexicographically Sortable Identifier)"""
    # Simple ULID implementation
    timestamp = int(time.time() * 1000)
    random_part = uuid.uuid4().hex[:10]
    
    # Convert timestamp to base32
    timestamp_base32 = base32_encode(timestamp)
    
    # Pad timestamp to 10 characters
    timestamp_padded = timestamp_base32.zfill(10)
    
    return f"{timestamp_padded}{random_part}"

def base32_encode(num: int) -> str:
    """Encode number to base32"""
    alphabet = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
    result = ""
    
    while num > 0:
        result = alphabet[num % 32] + result
        num //= 32
    
    return result

def generate_doc_id() -> str:
    """Generate document ID"""
    return generate_ulid()

def generate_chunk_id(doc_id: str, page: int, chunk_index: int) -> str:
    """Generate chunk ID"""
    return f"{doc_id}:{page}:{chunk_index}"

def generate_file_hash(content: bytes) -> str:
    """Generate SHA256 hash of file content"""
    return hashlib.sha256(content).hexdigest()

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage"""
    # Remove or replace unsafe characters
    unsafe_chars = '<>:"/\\|?*'
    for char in unsafe_chars:
        filename = filename.replace(char, '_')
    
    # Limit length
    if len(filename) > 100:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:95] + ('.' + ext if ext else '')
    
    return filename
