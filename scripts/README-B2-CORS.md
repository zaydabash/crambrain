# Backblaze B2 CORS Configuration for Direct Uploads

## Problem
The Backblaze B2 web interface's simple CORS rules might not support PUT requests needed for S3-compatible presigned URL uploads.

## Solution Options

### Option 1: Use B2 CLI (Recommended)
Install B2 CLI: `pip install b2`

Then create and apply custom CORS rules:

```bash
# Create CORS rules file
cat > cors-rules.json << 'CORSJSON'
[
  {
    "corsRuleName": "allow-vercel-s3-put",
    "allowedOrigins": ["https://nextjs-boilerplate-alpha-rust-98.vercel.app"],
    "allowedOperations": ["s3_put"],
    "allowedHeaders": ["*"],
    "exposeHeaders": ["ETag"],
    "maxAgeSeconds": 3600
  }
]
CORSJSON

# Apply to your bucket
b2 update-bucket --corsRules cors-rules.json crambrain allPublic
```

### Option 2: Alternative - Use Backend Upload
If CORS setup is problematic, we can modify the upload flow to:
1. Upload file to your Render API backend
2. Backend uploads to B2 directly
3. No CORS issues since backend-to-B2 doesn't require CORS

### Option 3: Check B2 Web Interface Advanced Settings
Some B2 accounts have an "Advanced" or "Custom CORS Rules" option. Check if your bucket settings have this option.

## Verify CORS Configuration
After setting up CORS, test with:
```bash
curl -X OPTIONS 'https://s3.us-west-004.backblazeb2.com/crambrain/' \
  -H 'Origin: https://nextjs-boilerplate-alpha-rust-98.vercel.app' \
  -H 'Access-Control-Request-Method: PUT' \
  -H 'Access-Control-Request-Headers: content-type' \
  -v
```

You should see `Access-Control-Allow-Methods: PUT` in the response.
