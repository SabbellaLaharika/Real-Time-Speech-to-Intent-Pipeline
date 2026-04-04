# Real-Time Speech-to-Intent Pipeline

A production-ready voice assistant pipeline built with FastAPI and containerized with Docker. Designed for sub-2-second latency on standard CPUs using high-performance local AI models.

## 🚀 Key Features
- **Local Transcription (ASR)**: `faster-whisper` (tiny.en, int8)
- **Local Intent Classification (NLU)**: Optimized keyword-based heuristic (8 intents)
- **Local Text-to-Speech (TTS)**: `Piper` (Standalone ONNX)
- **Latency Monitoring**: p50/p95/p99 tracking across all stages.
- **Production Infrastructure**: Multi-stage Docker build with zero-intervention startup.

## 🛠 Prerequisites
- Docker & Docker Compose
- Audio files in `.wav` format (for testing)

## 📦 Getting Started

### 1. Start the Pipeline
```bash
docker compose up --build -d
```
The first build will take a few minutes as it downloads the model weights (~150MB).

### 2. Verify Service Health
Wait about 60 seconds (for model warm-up) then check:
```bash
curl http://localhost:8000/health
```

### 3. Process Your First Request
```bash
curl -X POST -F "audio=@test_audio.wav" http://localhost:8000/process-intent
```

## 📊 Benchmarking
To verify the performance target (<2s p95) on your hardware:
```bash
python benchmark.py
```
This script will run multiple iterations and generate a detailed report in `results/latency_report.json`.

## 📂 Project Structure
- `main.py`: FastAPI server and API logic.
- `asr_module.py`: Speech-to-text with faster-whisper.
- `intent_module.py`: Request classification with 8 intents.
- `tts_module.py`: Audio generation with Piper.
- `benchmark.py`: Performance testing utility.
- `Dockerfile`: Multi-stage, optimized container build.

## ⚖️ Model Justification
See [MODEL_CHOICES.md](./MODEL_CHOICES.md) for a detailed breakdown of model rationales and performance targets.
