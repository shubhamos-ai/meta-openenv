FROM python:3.10-slim

# Force unbuffered output for real-time logs on HF
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install build dependencies for C-extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Create logs directory with correct permissions
RUN mkdir -p /app/logs && chmod -R 777 /app/logs

# Copy requirements FIRST to leverage Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Ensure test scripts are executable
RUN chmod +x ./tests/e2e_runner.sh

# Meta OpenEnv Requirement: Install the package in editable mode
# This registers the [project.scripts] and installs openenv dependencies.
RUN pip install --no-cache-dir -e .

# HF Spaces use 7860 as the internal port
EXPOSE 7860

CMD ["server"]
