FROM python:3.10-slim

WORKDIR /app

# Final trigger to ensure logs start streaming
RUN echo "Starting build for SHUBHAMOS meta-pytorch-hackathon"

# Install absolute bare minimum first
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose port (default 7860)
EXPOSE 7860

# Simple startup
CMD ["sh", "-c", "uvicorn server:app --host 0.0.0.0 --port ${PORT:-7860}"]
