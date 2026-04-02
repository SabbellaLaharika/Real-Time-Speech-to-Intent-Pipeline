import time
import base64
import io
from typing import Dict, Any

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI(title="Speech-to-Intent Pipeline")

class LatencyReport(BaseModel):
    asr: float
    intent: float
    tts: float
    total: float

class SuccessResponse(BaseModel):
    transcribed_text: str
    intent: str
    confidence: float
    response_audio_b64: str
    latencies_ms: LatencyReport

@app.get("/health")
async def health_check():
    """Requirement 1: Functional health check."""
    return {"status": "ok"}

@app.post("/process-intent", response_model=SuccessResponse)
async def process_intent(audio: UploadFile = File(...)):
    """
    Requirement 3: POST /process-intent (multipart/form-data)
    Requirement 4: Returns JSON with specific schema.
    Requirement 5: Handle invalid input gracefully.
    """
    start_time = time.perf_counter()
    
    # Requirement 5: Validate audio file extension (.wav)
    if not audio.filename.endswith('.wav'):
        raise HTTPException(status_code=400, detail="Invalid file type. Only .wav is allowed.")

    try:
        # Placeholder for ASR (Speech-to-Text)
        asr_start = time.perf_counter()
        time.sleep(0.1)  # Simulating processing
        transcribed_text = "turn on the kitchen light"
        asr_end = time.perf_counter()

        # Placeholder for Intent Classification (NLU)
        intent_start = time.perf_counter()
        time.sleep(0.05)  # Simulating processing
        intent = "TurnOn"
        confidence = 0.95
        intent_end = time.perf_counter()

        # Placeholder for Text-to-Speech (TTS)
        tts_start = time.perf_counter()
        time.sleep(0.2)  # Simulating processing
        # Mocking a small wav file in base64
        response_audio_b64 = base64.b64encode(b"RIFF\x00\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x80>\x00\x00\x80>\x00\x00\x01\x00\x08\x00data\x00\x00\x00\x00").decode("utf-8")
        tts_end = time.perf_counter()

        # Latency calculations in ms
        latencies = {
            "asr": round((asr_end - asr_start) * 1000, 2),
            "intent": round((intent_end - intent_start) * 1000, 2),
            "tts": round((tts_end - tts_start) * 1000, 2),
            "total": round((time.perf_counter() - start_time) * 1000, 2)
        }

        return SuccessResponse(
            transcribed_text=transcribed_text,
            intent=intent,
            confidence=confidence,
            response_audio_b64=response_audio_b64,
            latencies_ms=LatencyReport(**latencies)
        )

    except Exception as e:
        # Robust error handling
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
