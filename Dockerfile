FROM python:3.10-slim

# Force unbuffered output for real-time logs on HF
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install build dependencies for C-extensions (like uvicorn/httpcore)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements FIRST to leverage Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# HF Spaces use 7860 as the internal port
EXPOSE 7860

# Start unified app (FastAPI + Gradio)
# Note: we use app.py as the entry point
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT:-7860}"]
