# ── Base image ────────────────────────────────────────────────────────────────
FROM python:3.11-slim

# ── Metadata ──────────────────────────────────────────────────────────────────
LABEL maintainer="Shubhamos Team"
LABEL description="SHUBHAMOS: AI Email Operations & Triage Environment (OpenEnv)"
LABEL version="1.0.0"

# ── System deps ───────────────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ── Working directory ─────────────────────────────────────────────────────────
WORKDIR /app

# ── Install Python dependencies (cached layer) ────────────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Copy project files ────────────────────────────────────────────────────────
COPY models.py .
COPY environment.py .
COPY reward.py .
COPY server.py .
COPY inference.py .
COPY openenv.yaml .
COPY tasks/ ./tasks/
COPY graders/ ./graders/
COPY dashboard/ ./dashboard/

# ── Health check ──────────────────────────────────────────────────────────────
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:7860/health || exit 1

# ── Runtime env vars ──────────────────────────────────────────────────────────
ENV PORT=7860
ENV API_BASE_URL=https://router.huggingface.co/v1
ENV MODEL_NAME=Qwen/Qwen2.5-72B-Instruct
# HF_TOKEN must be injected at runtime — never bake tokens into images

# ── Expose port (Hugging Face Spaces default) ─────────────────────────────────
EXPOSE 7860

# ── Start server ──────────────────────────────────────────────────────────────
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "7860"]
