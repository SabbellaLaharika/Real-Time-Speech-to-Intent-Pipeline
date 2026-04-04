import time
import base64
import os
import shutil
import uuid
from typing import Dict, Any

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Import our custom modules
from asr_module import ASRModule
from intent_module import IntentModule
from tts_module import TTSModule
from wake_word_module import WakeWordModule

# Requirement 4: Define Response Schemas
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

app = FastAPI(title="Speech-to-Intent Pipeline")

# Initialize modules (Requirement 10: Optimizing for latency)
# Lazy loading is used to ensure the container starts quickly, 
# but we trigger a pre-warm load for the health check.
asr = None
nlu = None
tts = None
wakeword = None

def get_asr():
    global asr
    if asr is None:
        asr = ASRModule(model_size=os.getenv("ASR_MODEL", "tiny.en"))
    return asr

def get_nlu():
    global nlu
    if nlu is None:
        nlu = IntentModule()
    return nlu

def get_tts():
    global tts
    if tts is None:
        tts = TTSModule()
    return tts

def get_wakeword():
    global wakeword
    if wakeword is None:
        wakeword = WakeWordModule()
    return wakeword

@app.on_event("startup")
async def warmup():
    """Requirement 10: Pre-warm models on startup."""
    try:
        get_asr()
        get_nlu()
        get_tts()
        get_wakeword()
    except Exception as e:
        print(f"Warmup failed: {e}")

@app.get("/health")
async def health_check():
    """Requirement 1: Functional health check."""
    if asr is None or nlu is None or tts is None or wakeword is None:
        return JSONResponse(status_code=503, content={"status": "loading"})
    return {"status": "ok"}

@app.post("/process-intent", response_model=SuccessResponse)
async def process_intent(audio: UploadFile = File(...)):
    """
    Requirement 3: POST /process-intent (multipart/form-data)
    Requirement 4: Returns JSON with specific schema.
    Requirement 5: Handle invalid input gracefully.
    """
    overall_start = time.perf_counter()
    
    # Requirement 5: Request made without a file or with a non-audio file
    if audio is None:
        raise HTTPException(status_code=400, detail="Audio file must be provided.")
    
    if not audio.filename or not audio.filename.endswith('.wav'):
        raise HTTPException(status_code=400, detail="Invalid file type. Only .wav is allowed.")

    # Save temporary file for processing - use UUID for safety
    temp_filename = f"temp_{uuid.uuid4()}.wav"
    try:
        with open(temp_filename, "wb") as buffer:
            shutil.copyfileobj(audio.file, buffer)

        # Requirement 1: Wake Word Detection (always-on trigger)
        # Assuming the trigger is part of the initial streaming stream
        triggered, ww_ms = get_wakeword().detect(temp_filename)
        
        # 1. ASR (Speech-to-Text) - Requirement 4
        transcribed_text, asr_ms = get_asr().transcribe(temp_filename)

        # 2. Intent Classification (NLU) - Requirement 6 (8 allowed values)
        intent, confidence, intent_ms = get_nlu().predict(transcribed_text)

        # 3. Text-to-Speech (TTS) - Requirement 4 & 9 (Sub-2s p95)
        response_audio_b64, tts_ms = get_tts().text_to_speech(f"Okay, performing {intent}")

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
