# Stage 1: Builder
FROM python:3.11-slim AS builder

WORKDIR /build

ENV PIP_NO_CACHE_DIR=1 \
    PYTHONUNBUFFERED=1

# Install only what's needed for building
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create and populate virtual environment in one layer for maximum size savings
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .

RUN pip install --upgrade pip setuptools wheel && \
    pip install --prefer-binary -r requirements.txt && \
    # 🚨 AGGRESSIVE PRUNING: This saves ~500MB+ of unused metadata/docs
    find /opt/venv -type d -name "__pycache__" -exec rm -rf {} + && \
    find /opt/venv -type f -name "*.pyc" -delete && \
    find /opt/venv -type d -name "tests" -exec rm -rf {} + && \
    find /opt/venv -type d -name "*.dist-info" -exec rm -rf {} + && \
    find /opt/venv -type d -name "include" -exec rm -rf {} + && \
    find /opt/venv -type d -name "share" -exec rm -rf {} +

# Install Piper Binary (standalone)
RUN mkdir -p /opt/piper && \
    curl -L https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_amd64.tar.gz \
    | tar -xzC /opt/piper --strip-components=1

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

ENV PIP_NO_CACHE_DIR=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:/opt/piper:$PATH" \
    LD_LIBRARY_PATH="/opt/piper:$LD_LIBRARY_PATH"

# Minimal runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy artifacts from builder
COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /opt/piper /opt/piper

# Copy application files (models and logs are ignored via .dockerignore)
COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]