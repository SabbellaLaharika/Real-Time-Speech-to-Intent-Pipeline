import time
import base64
import os
import shutil
from typing import Dict, Any

from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel

# Import our custom modules
from asr_module import ASRModule
from intent_module import IntentModule
from tts_module import TTSModule

app = FastAPI(title="Speech-to-Intent Pipeline")

# Initialize modules (Requirement 10: Optimizing for latency)
asr = ASRModule(model_size="tiny.en")
nlu = IntentModule()
tts = TTSModule()

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
    overall_start = time.perf_counter()
    
    # Requirement 5: Validate audio file extension (.wav)
    if not audio.filename.endswith('.wav'):
        raise HTTPException(status_code=400, detail="Invalid file type. Only .wav is allowed.")

    # Save temporary file for processing
    temp_filename = f"temp_{int(time.time())}.wav"
    try:
        with open(temp_filename, "wb") as buffer:
            shutil.copyfileobj(audio.file, buffer)

        # 1. ASR (Speech-to-Text) - Requirement 4
        transcribed_text, asr_ms = asr.transcribe(temp_filename)

        # 2. Intent Classification (NLU) - Requirement 6 (8 allowed values)
        intent, confidence, intent_ms = nlu.predict(transcribed_text)

        # 3. Text-to-Speech (TTS) - Requirement 4 & 9 (Sub-2s p95)
        response_audio_b64, tts_ms = tts.text_to_speech(f"Okay, performing {intent}")

        # Total Latency calculation
        total_ms = round((time.perf_counter() - overall_start) * 1000, 2)

        return SuccessResponse(
            transcribed_text=transcribed_text,
            intent=intent,
            confidence=confidence,
            response_audio_b64=response_audio_b64,
            latencies_ms=LatencyReport(
                asr=asr_ms,
                intent=intent_ms,
                tts=tts_ms,
                total=total_ms
            )
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Error: {str(e)}")
    finally:
        # Cleanup temporary audio file
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
