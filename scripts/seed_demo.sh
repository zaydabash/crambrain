#!/bin/bash

# CramBrain Demo Seed Script
# This script uploads a sample PDF and tests the complete workflow

set -e

# Configuration
API_BASE_URL=${API_BASE_URL:-"http://localhost:8000"}
SAMPLE_PDF_URL="https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
VERBOSE=${VERBOSE:-false}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Test functions
download_sample_pdf() {
    log_step "Downloading sample PDF..."
    
    if [ ! -f "/tmp/sample.pdf" ]; then
        curl -s -o /tmp/sample.pdf "$SAMPLE_PDF_URL"
        log_info "✓ Sample PDF downloaded"
    else
        log_info "✓ Sample PDF already exists"
    fi
}

upload_and_ingest() {
    log_step "Uploading and ingesting sample PDF..."
    
    # Step 1: Get presigned URL
    log_info "Getting presigned upload URL..."
    presign_response=$(curl -s -X POST \
        -H "Content-Type: application/json" \
        -d '{"filename": "sample.pdf"}' \
        "$API_BASE_URL/v1/presign")
    
    if [ "$VERBOSE" = "true" ]; then
        echo "$presign_response" | jq .
    fi
    
    upload_url=$(echo "$presign_response" | jq -r '.upload_url')
    file_url=$(echo "$presign_response" | jq -r '.file_url')
    
    if [ "$upload_url" = "null" ] || [ "$file_url" = "null" ]; then
        log_error "Failed to get presigned URL"
        return 1
    fi
    
    log_info "✓ Got presigned URL"
    
    # Step 2: Upload file
    log_info "Uploading file to S3..."
    upload_response=$(curl -s -w "%{http_code}" -o /tmp/upload_response.txt \
        -X PUT \
        -H "Content-Type: application/pdf" \
        --data-binary @/tmp/sample.pdf \
        "$upload_url")
    
    if [ "$upload_response" = "200" ]; then
        log_info "✓ File uploaded successfully"
    else
        log_error "✗ File upload failed with status $upload_response"
        return 1
    fi
    
    # Step 3: Ingest document
    log_info "Ingesting document..."
    ingest_response=$(curl -s -X POST \
        -H "Content-Type: application/json" \
        -d "{\"file_url\": \"$file_url\", \"original_name\": \"sample.pdf\"}" \
        "$API_BASE_URL/v1/ingest")
    
    if [ "$VERBOSE" = "true" ]; then
        echo "$ingest_response" | jq .
    fi
    
    doc_id=$(echo "$ingest_response" | jq -r '.doc_id')
    
    if [ "$doc_id" = "null" ]; then
        log_error "Failed to ingest document"
        return 1
    fi
    
    log_info "✓ Document ingested with ID: $doc_id"
    echo "$doc_id" > /tmp/demo_doc_id.txt
}

test_ask_question() {
    log_step "Testing question answering..."
    
    if [ ! -f "/tmp/demo_doc_id.txt" ]; then
        log_error "No document ID found. Run upload_and_ingest first."
        return 1
    fi
    
    doc_id=$(cat /tmp/demo_doc_id.txt)
    
    log_info "Asking question about document $doc_id..."
    ask_response=$(curl -s -X POST \
        -H "Content-Type: application/json" \
        -d "{\"query\": \"What is this document about?\", \"doc_id\": \"$doc_id\", \"top_k\": 3}" \
        "$API_BASE_URL/v1/ask")
    
    if [ "$VERBOSE" = "true" ]; then
        echo "$ask_response" | jq .
    fi
    
    answer=$(echo "$ask_response" | jq -r '.answer')
    
    if [ "$answer" != "null" ] && [ "$answer" != "" ]; then
        log_info "✓ Question answered successfully"
        log_info "Answer: $answer"
        
        # Check for citations
        citations=$(echo "$ask_response" | jq -r '.citations | length')
        log_info "✓ Found $citations citations"
    else
        log_error "✗ Failed to get answer"
        return 1
    fi
}

test_quiz_generation() {
    log_step "Testing quiz generation..."
    
    if [ ! -f "/tmp/demo_doc_id.txt" ]; then
        log_error "No document ID found. Run upload_and_ingest first."
        return 1
    fi
    
    doc_id=$(cat /tmp/demo_doc_id.txt)
    
    log_info "Generating quiz for document $doc_id..."
    quiz_response=$(curl -s -X POST \
        -H "Content-Type: application/json" \
        -d "{\"doc_id\": \"$doc_id\", \"n\": 5}" \
        "$API_BASE_URL/v1/quiz")
    
    if [ "$VERBOSE" = "true" ]; then
        echo "$quiz_response" | jq .
    fi
    
    questions_count=$(echo "$quiz_response" | jq -r '.questions | length')
    
    if [ "$questions_count" -gt 0 ]; then
        log_info "✓ Quiz generated successfully with $questions_count questions"
        
        # Show first question as example
        first_question=$(echo "$quiz_response" | jq -r '.questions[0].prompt')
        log_info "Sample question: $first_question"
    else
        log_error "✗ Failed to generate quiz"
        return 1
    fi
}

test_document_listing() {
    log_step "Testing document listing..."
    
    log_info "Listing all documents..."
    docs_response=$(curl -s "$API_BASE_URL/v1/docs")
    
    if [ "$VERBOSE" = "true" ]; then
        echo "$docs_response" | jq .
    fi
    
    docs_count=$(echo "$docs_response" | jq -r '.documents | length')
    
    if [ "$docs_count" -gt 0 ]; then
        log_info "✓ Found $docs_count documents"
    else
        log_warn "No documents found"
    fi
}

# Main execution
main() {
    log_info "Starting CramBrain demo seed..."
    log_info "API Base URL: $API_BASE_URL"
    
    # Check if jq is available
    if ! command -v jq &> /dev/null; then
        log_error "jq is required but not installed. Please install jq first."
        exit 1
    fi
    
    # Check if curl is available
    if ! command -v curl &> /dev/null; then
        log_error "curl is required but not installed. Please install curl first."
        exit 1
    fi
    
    # Run demo steps
    steps_passed=0
    steps_total=0
    
    for step in download_sample_pdf upload_and_ingest test_ask_question test_quiz_generation test_document_listing; do
        steps_total=$((steps_total + 1))
        if $step; then
            steps_passed=$((steps_passed + 1))
        else
            log_error "Step failed: $step"
            break
        fi
    done
    
    # Summary
    echo ""
    log_info "Demo Summary: $steps_passed/$steps_total steps completed"
    
    if [ $steps_passed -eq $steps_total ]; then
        log_info "🎉 Demo completed successfully!"
        log_info "You can now:"
        log_info "  - Visit the web app and upload documents"
        log_info "  - Ask questions and get answers with citations"
        log_info "  - Generate quizzes from your documents"
        log_info "  - View documents with page-specific navigation"
    else
        log_error "❌ Demo failed. Check the logs above."
        exit 1
    fi
}

# Run main function
main "$@"
