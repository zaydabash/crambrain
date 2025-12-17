# CramBrain API

FastAPI-based backend for CramBrain, providing RAG (Retrieval-Augmented Generation) capabilities for document processing, question answering, and quiz generation.

## Features

- 📄 PDF document processing and ingestion
- 🔍 Vector-based semantic search
- 💬 Question answering with citations
- 📝 Quiz generation
- 🔐 Rate limiting
- 📊 Health monitoring

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Configuration

Copy `env.example` to `.env` and configure:

```bash
cp env.example .env
# Edit .env with your configuration
```

### Run

```bash
uvicorn src.main:app --reload
```

## API Endpoints

### Health Check
- `GET /v1/health` - Health check endpoint

### Document Management
- `POST /v1/presign` - Generate presigned upload URL
- `POST /v1/upload` - Upload and ingest document
- `POST /v1/ingest` - Ingest document from URL
- `GET /v1/docs` - List documents
- `GET /v1/docs/{doc_id}` - Get document details

### Query & Search
- `POST /v1/ask` - Ask questions with citations
- `GET /v1/search` - Search documents

### Quiz Generation
- `POST /v1/quiz` - Generate quiz questions
- `POST /v1/cram-plan` - Generate cram plan

## Security

⚠️ **Important:** This API does not currently implement authentication. All endpoints are publicly accessible.

See [SECURITY.md](SECURITY.md) for security considerations and recommendations.

### Security Features

- Input validation with Pydantic
- File upload validation
- Rate limiting (basic)
- CORS configuration
- Filename sanitization

### Security Recommendations

1. **Implement API Key Authentication:**
   - Add API key validation middleware
   - Store keys securely
   - Rotate keys regularly

2. **Restrict CORS Origins:**
   - Update `CORS_ORIGINS` to specific domains
   - Don't use wildcard (`*`) in production

3. **Implement IP-Based Rate Limiting:**
   - Track requests by IP address
   - Use Redis for distributed rate limiting
   - Implement different limits per endpoint

4. **Add Security Headers:**
   - X-Content-Type-Options
   - X-Frame-Options
   - X-XSS-Protection
   - Strict-Transport-Security

## Input Validation

All API requests are validated using Pydantic models:

- **Query strings:** max 1000 characters
- **File uploads:** PDF only, max 50MB
- **File names:** sanitized, max 100 characters
- **Numbers:** bounded ranges (top_k: 1-20, etc.)

### Validation Examples

```python
class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    top_k: int = Field(6, ge=1, le=20)
    doc_id: Optional[str] = Field(None, max_length=100)
```

## Environment Variables

See `env.example` for all required environment variables.

### Required Variables

- `OPENAI_API_KEY` - OpenAI API key
- `S3_ENDPOINT_URL` - S3 endpoint URL
- `S3_ACCESS_KEY` - S3 access key
- `S3_SECRET_KEY` - S3 secret key
- `S3_BUCKET` - S3 bucket name

### Optional Variables

- `CORS_ORIGINS` - Allowed CORS origins (default: `*`)
- `RATE_LIMIT_REQUESTS` - Rate limit requests (default: 100)
- `RATE_LIMIT_WINDOW` - Rate limit window in seconds (default: 3600)
- `MAX_FILE_MB` - Maximum file size in MB (default: 50)
- `ENABLE_TESSERACT` - Enable OCR (default: false)

## Development

### Running Tests

```bash
pytest tests/backend
```

### Code Quality

```bash
# Linting
ruff check src/

# Type checking
mypy src/
```

## Deployment

See main [README.md](../README.md) for deployment instructions.

### Docker

```bash
docker build -t crambrain-api .
docker run -p 8000:8000 --env-file .env crambrain-api
```

### Render

See `render.yaml` for Render deployment configuration.

## Monitoring

### Health Check

```bash
curl https://your-api.onrender.com/v1/health
```

### Logs

```bash
# Render
render logs --service your-service-name

# Docker
docker logs crambrain-api
```

## Troubleshooting

### Common Issues

1. **Missing Environment Variables:**
   - Check all required variables are set
   - Verify `.env` file is loaded
   - Check Render environment variables

2. **S3 Connection Issues:**
   - Verify S3 credentials
   - Check bucket permissions
   - Verify endpoint URL

3. **Chroma Database Issues:**
   - Check persistent disk is mounted
   - Verify `CHROMA_PERSIST_DIR` is set
   - Check disk space

4. **OpenAI API Issues:**
   - Verify API key is valid
   - Check API quota
   - Monitor API usage

## Security Considerations

See [SECURITY.md](SECURITY.md) for detailed security documentation.

### Key Security Points

1. **No Authentication:** API is currently public
2. **CORS:** Configured to allow all origins (change in production)
3. **Rate Limiting:** Basic implementation (needs improvement)
4. **Input Validation:** All inputs are validated
5. **File Uploads:** Validated and sanitized

## License

MIT License - see [LICENSE](../LICENSE) file for details.

