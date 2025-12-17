FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
 && rm -rf /var/lib/apt/lists/*

ENV PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1
COPY requirements.txt /app/requirements.txt
# CPU-only Torch
RUN pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu torch==2.1.1
# Rest of deps (now small/CPU-only)
RUN pip install --no-cache-dir -r /app/requirements.txt

# ——— Cache Hugging Face / sentence-transformers model at build time ———
ENV HF_HOME=/app/.cache/huggingface \
    TRANSFORMERS_CACHE=/app/.cache/huggingface \
    SENTENCE_TRANSFORMERS_HOME=/app/.cache/sentence-transformers \
    HF_HUB_DISABLE_TELEMETRY=1

# Pre-download the SBERT model so runtime is offline + fast
RUN python - <<'PY'
from sentence_transformers import SentenceTransformer
print("Downloading SBERT…")
SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
print("SBERT cached.")
PY

# Force offline use at runtime so it never tries to download on Render
ENV TRANSFORMERS_OFFLINE=1

COPY src /app/src
ENV PYTHONPATH=/app/src

EXPOSE 8000
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]