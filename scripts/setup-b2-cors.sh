#!/bin/bash
# Script to set up CORS rules for Backblaze B2 to allow direct PUT uploads
# Requires: b2 CLI tool (install: pip install b2)
# Usage: ./setup-b2-cors.sh <bucket-name>

BUCKET_NAME=${1:-crambrain}
ORIGIN="https://nextjs-boilerplate-alpha-rust-98.vercel.app"

echo "Setting up CORS rules for bucket: $BUCKET_NAME"
echo "Origin: $ORIGIN"
echo ""

# Create CORS rules JSON
cat > /tmp/cors-rules.json << EOF
[
  {
    "corsRuleName": "allow-s3-compatible-upload",
    "allowedOrigins": ["$ORIGIN"],
    "allowedOperations": ["s3_put"],
    "allowedHeaders": ["*"],
    "exposeHeaders": ["ETag"],
    "maxAgeSeconds": 3600
  }
]
EOF

echo "CORS Rules JSON:"
cat /tmp/cors-rules.json
echo ""
echo "To apply these rules, use the B2 CLI:"
echo "  b2 update-bucket --corsRules /tmp/cors-rules.json $BUCKET_NAME allPublic"
echo ""
echo "Or use the B2 web interface and select 'Custom rules' option."

