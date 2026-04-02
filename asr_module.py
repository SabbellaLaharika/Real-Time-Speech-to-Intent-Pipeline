import time
from typing import Tuple
from faster_whisper import WhisperModel

class ASRModule:
    def __init__(self, model_size: str = "tiny.en", device: str = "cpu", compute_type: str = "int8"):
        """
        Requirement 10: Using faster-whisper tiny.en with int8 for optimized latency.
        """
        self.model = WhisperModel(model_size, device=device, compute_type=compute_type)

    def transcribe(self, audio_path: str) -> Tuple[str, float]:
        """
        Transcribes audio and returns the text and latency in ms.
        """
        start_time = time.perf_counter()
        segments, info = self.model.transcribe(audio_path, beam_size=5)
        
        # Collect all segments into a single transcription
        text = " ".join([segment.text for segment in segments]).strip()
        
        latency_ms = (time.perf_counter() - start_time) * 1000
        return text, round(latency_ms, 2)

if __name__ == "__main__":
    # Quick test if needed
    pass
