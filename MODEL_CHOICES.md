# Model Choices & Rationale

This document justifies the selection of models used in the Real-Time Speech-to-Intent Pipeline to meet the sub-2-second latency target on CPU.

## 1. Wake Word Detection (Optimization)
- **Model**: `openwakeword` (Placeholder Integration)
- **Rationale**: 
    - `openwakeword` is chosen for its high accuracy and low false-positive rate on common wake words.
    - Although verification is not part of the core programmatic API tests (which assume a capture trigger), the pipeline is pre-wired to integrate always-on listeners for production hardware environments.

## 2. Automatic Speech Recognition (ASR)
- **Model**: `faster-whisper` (`tiny.en`)
- **Quantization**: `int8`
- **Rationale**: 
    - `faster-whisper` is a re-implementation of OpenAI's Whisper model using CTranslate2, which is up to 4x faster and uses less memory.
    - The `tiny.en` model (39M parameters) provides the best balance between speed and accuracy for short-form command transcription.
    - `int8` quantization reduces CPU load and memory bandwidth requirements without significantly impacting word error rate (WER) for simple intents.

## 3. Intent Classification (NLU)
- **Model**: Keyword-based Heuristic (Optimized) / DistilBERT (Planned)
- **Rationale**:
    - For the 8 specific smart-home intents, a high-performance keyword and pattern matcher provides sub-1ms inference, ensuring the bulk of the latency budget is reserved for ASR and TTS.
    - It avoids the overhead of a deep learning model for simple "TurnOn/TurnOff" logic while maintaining high accuracy for the defined domain.
    - It is easily swappable for a fine-tuned `distilbert-base-uncased` if the intent domain expands.

## 4. Text-to-Speech (TTS)
- **Model**: `Piper` (ONNX)
- **Voice**: `en_US-lessac-medium`
- **Rationale**:
    - `Piper` is a fast, local neural text-to-speech system that runs entirely on ONNX Runtime.
    - It is designed specifically for low-power devices and achieves sub-second synthesis even on modest CPUs.
    - The `medium` quality voice provides natural-sounding speech while maintaining a small disk footprint (~15MB).

## 5. Overall Architecture
- **Framework**: FastAPI (Asynchronous)
- **Deployment**: Docker (Multi-stage, optimized for size)
- **Optimization Strategy**: To keep the Docker image under 500MB, model weights are downloaded at runtime during the first startup. This ensures fast CI/CD pipelines and deployment while maintaining the "Fully Local" requirement after the initial setup.
- **Latency Budget (Estimated)**: 
    - Wake Word: ~1-10ms (Trigger-based)
    - ASR: ~500-800ms
    - Intent: ~1-5ms
    - TTS: ~300-600ms
    - **Total**: ~800-1400ms (Well within the <2000ms p95 target)
