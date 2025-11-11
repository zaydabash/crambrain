#!/bin/bash

# CramBrain Smoke Tests
# This script tests the basic functionality of the deployed API

set -e

# Configuration
API_BASE_URL=${API_BASE_URL:-"http://localhost:8000"}
VERBOSE=${VERBOSE:-false}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# Test functions
test_health() {
    log_info "Testing health endpoint..."
    
    response=$(curl -s -w "%{http_code}" -o /tmp/health_response.json "$API_BASE_URL/v1/health")
    
    if [ "$response" = "200" ]; then
        log_info "✓ Health check passed"
        if [ "$VERBOSE" = "true" ]; then
            cat /tmp/health_response.json | jq .
        fi
    else
        log_error "✗ Health check failed with status $response"
        return 1
    fi
}

test_presign() {
    log_info "Testing presign endpoint..."
    
    response=$(curl -s -w "%{http_code}" -o /tmp/presign_response.json \
        -X POST \
        -H "Content-Type: application/json" \
        -d '{"filename": "test.pdf"}' \
        "$API_BASE_URL/v1/presign")
    
    if [ "$response" = "200" ]; then
        log_info "✓ Presign endpoint working"
        if [ "$VERBOSE" = "true" ]; then
            cat /tmp/presign_response.json | jq .
        fi
    else
        log_error "✗ Presign endpoint failed with status $response"
        return 1
    fi
}

test_docs_list() {
    log_info "Testing docs list endpoint..."
    
    response=$(curl -s -w "%{http_code}" -o /tmp/docs_response.json \
        "$API_BASE_URL/v1/docs")
    
    if [ "$response" = "200" ]; then
        log_info "✓ Docs list endpoint working"
        if [ "$VERBOSE" = "true" ]; then
            cat /tmp/docs_response.json | jq .
        fi
    else
        log_error "✗ Docs list endpoint failed with status $response"
        return 1
    fi
}

test_search() {
    log_info "Testing search endpoint..."
    
    response=$(curl -s -w "%{http_code}" -o /tmp/search_response.json \
        "$API_BASE_URL/v1/search?q=test")
    
    if [ "$response" = "200" ]; then
        log_info "✓ Search endpoint working"
        if [ "$VERBOSE" = "true" ]; then
            cat /tmp/search_response.json | jq .
        fi
    else
        log_error "✗ Search endpoint failed with status $response"
        return 1
    fi
}

# Main execution
main() {
    log_info "Starting CramBrain smoke tests..."
    log_info "API Base URL: $API_BASE_URL"
    
    # Check if jq is available for pretty printing
    if ! command -v jq &> /dev/null; then
        log_warn "jq not found. Install jq for better output formatting."
    fi
    
    # Run tests
    tests_passed=0
    tests_total=0
    
    for test in test_health test_presign test_docs_list test_search; do
        tests_total=$((tests_total + 1))
        if $test; then
            tests_passed=$((tests_passed + 1))
        fi
    done
    
    # Summary
    echo ""
    log_info "Test Summary: $tests_passed/$tests_total tests passed"
    
    if [ $tests_passed -eq $tests_total ]; then
        log_info "🎉 All tests passed! API is working correctly."
        exit 0
    else
        log_error "❌ Some tests failed. Check the logs above."
        exit 1
    fi
}

# Run main function
main "$@"
