# Stage 1: Builder
FROM python:3.11-slim AS builder

WORKDIR /build

ENV PIP_NO_CACHE_DIR=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create venv
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .

# Install dependencies (clean way)
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --prefer-binary -r requirements.txt

# Install Piper
RUN mkdir -p /opt/piper && \
    curl -L https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_amd64.tar.gz \
    | tar -xzC /opt/piper --strip-components=1

# Download ML Models
RUN mkdir -p /opt/models && \
    python -c "from faster_whisper import WhisperModel; WhisperModel('tiny.en', device='cpu', compute_type='int8', download_root='/opt/models')" && \
    curl -L -o /opt/models/en_US-lessac-medium.onnx "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx?download=true" && \
    curl -L -o /opt/models/en_US-lessac-medium.onnx.json "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json?download=true"


# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

ENV PATH="/opt/venv/bin:/opt/piper:$PATH" \
    LD_LIBRARY_PATH="/opt/piper:$LD_LIBRARY_PATH" \
    PYTHONUNBUFFERED=1

# Minimal runtime deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy only necessary runtime files
COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /opt/piper /opt/piper
COPY --from=builder /opt/models /app/models

# Copy app files (models and logs are ignored via .dockerignore)
COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]