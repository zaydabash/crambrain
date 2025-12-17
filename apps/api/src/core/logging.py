"""
Logging configuration
"""

import logging
import sys
from datetime import datetime
from typing import Dict, Any

def setup_logging():
    """Setup structured logging"""
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Add handler to root logger
    root_logger.addHandler(console_handler)
    
    # Set specific loggers
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    logging.getLogger("chromadb").setLevel(logging.WARNING)
    logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
    logging.getLogger("transformers").setLevel(logging.WARNING)
    logging.getLogger("torch").setLevel(logging.WARNING)

def log_request(request_id: str, method: str, path: str, **kwargs):
    """Log request details"""
    logger = logging.getLogger(__name__)
    logger.info(f"Request {request_id}: {method} {path}", extra={
        "request_id": request_id,
        "method": method,
        "path": path,
        **kwargs
    })

def log_response(request_id: str, status_code: int, duration_ms: float, **kwargs):
    """Log response details"""
    logger = logging.getLogger(__name__)
    logger.info(f"Response {request_id}: {status_code} ({duration_ms}ms)", extra={
        "request_id": request_id,
        "status_code": status_code,
        "duration_ms": duration_ms,
        **kwargs
    })

def log_error(request_id: str, error: Exception, **kwargs):
    """Log error details"""
    logger = logging.getLogger(__name__)
    logger.error(f"Error {request_id}: {str(error)}", extra={
        "request_id": request_id,
        "error": str(error),
        "error_type": type(error).__name__,
        **kwargs
    })