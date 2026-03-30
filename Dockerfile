# Use Python 3.10-slim as base image for stability and smaller footprint
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory to /app
WORKDIR /app

# Install system dependencies if needed (none strictly required for this specific task)
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     curl \
#     && rm -rf /var/lib/apt/lists/*

# Copy requirements file first to leverage Docker cache
COPY requirements.txt .

# Upgrade pip and install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy all project files into the container
COPY . .

# Expose the port used by Hugging Face Spaces (and our FastAPI server)
EXPOSE 7860

# Run the FastAPI server using uvicorn (dynamic port for HF Spaces with 7860 fallback)
CMD ["sh", "-c", "uvicorn server:app --host 0.0.0.0 --port ${PORT:-7860}"]
