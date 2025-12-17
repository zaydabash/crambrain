# Security Documentation

## Overview

This document outlines security considerations, best practices, and implementation details for the CramBrain API.

## Authentication & Authorization

### Current State

⚠️ **Note:** The API currently does not implement user authentication or authorization. All endpoints are publicly accessible.

### Recommendations for Production

1. **API Key Authentication:**
   - Implement API key authentication for all endpoints
   - Store API keys in environment variables
   - Use middleware to validate API keys on each request

2. **JWT Tokens:**
   - Implement JWT-based authentication for user sessions
   - Use secure token storage (httpOnly cookies)
   - Implement token refresh mechanism

3. **Role-Based Access Control (RBAC):**
   - Implement user roles (admin, user, guest)
   - Restrict access to sensitive endpoints
   - Implement document-level access control

## Input Validation

### Pydantic Models

All API requests are validated using Pydantic models:

```python
from pydantic import BaseModel, Field, validator

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    top_k: int = Field(6, ge=1, le=20)
    doc_id: Optional[str] = Field(None, max_length=100)
```

### Validation Practices

1. **String Length Limits:**
   - Query strings: max 1000 characters
   - Filenames: max 100 characters (sanitized)
   - Document IDs: validated format

2. **File Upload Validation:**
   - File type validation (PDF only)
   - File size limits (50MB max)
   - Filename sanitization
   - Content-type verification

3. **Number Validation:**
   - Range validation for pagination
   - Positive integers for counts
   - Bounded values for top_k, num_questions

### Sanitization

1. **Filename Sanitization:**
   ```python
   def sanitize_filename(filename: str) -> str:
       # Remove unsafe characters
       unsafe_chars = '<>:"/\\|?*'
       for char in unsafe_chars:
           filename = filename.replace(char, '_')
       # Limit length
       if len(filename) > 100:
           name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
           filename = name[:95] + ('.' + ext if ext else '')
       return filename
   ```

2. **SQL Injection Prevention:**
   - Use parameterized queries (Chroma handles this)
   - No raw SQL queries
   - Input sanitization before database operations

3. **XSS Prevention:**
   - All user input is sanitized before storage
   - HTML escaping in responses
   - Content Security Policy headers

## CORS Configuration

### Current Configuration

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ Allows all origins
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Security Recommendations

1. **Restrict Origins:**
   ```python
   allow_origins=[
       "https://your-app.vercel.app",
       "https://your-custom-domain.com",
   ]
   ```

2. **Limit Methods:**
   ```python
   allow_methods=["GET", "POST"],  # Only needed methods
   ```

3. **Limit Headers:**
   ```python
   allow_headers=["Content-Type", "Authorization"],  # Only needed headers
   ```

## Rate Limiting

### Current Implementation

A simple in-memory rate limiter is implemented but not fully functional:

```python
class SimpleRateLimiter:
    async def check_rate_limit(self):
        # Currently does not track IP addresses
        pass
```

### Recommendations

1. **Implement IP-Based Rate Limiting:**
   - Track requests by IP address
   - Implement sliding window or token bucket algorithm
   - Use Redis for distributed rate limiting

2. **Rate Limit Configuration:**
   - Different limits for different endpoints
   - Stricter limits for expensive operations (ingest, quiz generation)
   - User-based rate limiting for authenticated users

3. **Rate Limit Headers:**
   - Include rate limit headers in responses
   - Inform clients of remaining requests
   - Return 429 status code when limit exceeded

## Environment Variables & Secrets

### Secure Storage

1. **Never commit secrets to git:**
   - Use `.env` files (gitignored)
   - Use environment variables in production
   - Use secret management services (AWS Secrets Manager, etc.)

2. **Secret Rotation:**
   - Rotate API keys regularly
   - Use different keys for different environments
   - Implement key versioning

3. **Secret Validation:**
   - Validate all required secrets on startup
   - Fail fast if secrets are missing
   - Use placeholder values in development

### Required Secrets

- `OPENAI_API_KEY` - OpenAI API key
- `S3_ACCESS_KEY` - S3 access key
- `S3_SECRET_KEY` - S3 secret key
- `S3_BUCKET` - S3 bucket name

## File Upload Security

### Validation

1. **File Type Validation:**
   - Only allow PDF files
   - Verify MIME type
   - Check file extension

2. **File Size Limits:**
   - Maximum file size: 50MB
   - Validate before processing
   - Return clear error messages

3. **Content Validation:**
   - Validate PDF structure
   - Check for malicious content
   - Limit processing time

### Storage Security

1. **S3 Bucket Configuration:**
   - Use private buckets
   - Implement bucket policies
   - Enable versioning
   - Enable logging

2. **Presigned URLs:**
   - Short expiration times (1 hour)
   - Limit to specific operations (PUT only)
   - Validate signatures

3. **Access Control:**
   - Implement document-level access control
   - Use signed URLs for private documents
   - Restrict public access

## API Security

### HTTPS Only

⚠️ **Important:** Always use HTTPS in production. Never use HTTP for API endpoints.

### Headers

1. **Security Headers:**
   ```python
   @app.middleware("http")
   async def add_security_headers(request, call_next):
       response = await call_next(request)
       response.headers["X-Content-Type-Options"] = "nosniff"
       response.headers["X-Frame-Options"] = "DENY"
       response.headers["X-XSS-Protection"] = "1; mode=block"
       response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
       return response
   ```

2. **CORS Headers:**
   - Limit to specific origins
   - Don't allow credentials with wildcard origins
   - Use proper CORS preflight handling

### Error Handling

1. **Don't Leak Information:**
   - Don't expose stack traces in production
   - Don't expose internal error messages
   - Use generic error messages for users

2. **Logging:**
   - Log all errors securely
   - Don't log sensitive information
   - Use structured logging
   - Implement log rotation

## Database Security

### Chroma Vector Database

1. **Access Control:**
   - Restrict database access
   - Use authentication if available
   - Implement backup encryption

2. **Data Privacy:**
   - Encrypt sensitive data
   - Implement data retention policies
   - Comply with GDPR/CCPA

3. **Query Security:**
   - Validate all queries
   - Use parameterized queries
   - Limit query complexity

## Third-Party Services

### OpenAI API

1. **API Key Security:**
   - Store keys securely
   - Rotate keys regularly
   - Monitor API usage

2. **Rate Limiting:**
   - Implement client-side rate limiting
   - Handle API errors gracefully
   - Monitor API costs

### S3 Storage

1. **Bucket Security:**
   - Use private buckets
   - Implement bucket policies
   - Enable logging and monitoring

2. **Access Keys:**
   - Use IAM roles when possible
   - Rotate keys regularly
   - Limit key permissions

## Monitoring & Logging

### Security Monitoring

1. **Log All Requests:**
   - Log all API requests
   - Log authentication attempts
   - Log file uploads
   - Log errors

2. **Alert on Suspicious Activity:**
   - Multiple failed requests
   - Unusual traffic patterns
   - Large file uploads
   - Unauthorized access attempts

3. **Audit Logs:**
   - Maintain audit logs
   - Implement log retention
   - Secure log storage

## Compliance

### GDPR/CCPA

1. **Data Privacy:**
   - Implement data deletion
   - Provide data export
   - Honor user privacy requests

2. **Data Minimization:**
   - Only collect necessary data
   - Delete unused data
   - Implement data retention policies

## Security Checklist

- [ ] Implement API key authentication
- [ ] Restrict CORS origins
- [ ] Implement IP-based rate limiting
- [ ] Add security headers
- [ ] Encrypt sensitive data
- [ ] Implement input validation
- [ ] Sanitize all user input
- [ ] Use HTTPS only
- [ ] Rotate secrets regularly
- [ ] Monitor for suspicious activity
- [ ] Implement audit logging
- [ ] Regular security audits
- [ ] Dependency vulnerability scanning
- [ ] Penetration testing

## Reporting Security Issues

If you discover a security vulnerability, please report it to: security@crambrain.com

**Do not** create a public GitHub issue for security vulnerabilities.

## Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [Python Security](https://python.readthedocs.io/en/stable/library/security.html)
- [API Security Best Practices](https://cheatsheetseries.owasp.org/cheatsheets/API_Security_Cheat_Sheet.html)

