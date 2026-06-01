import time
import base64
import os
import subprocess
import requests
from typing import Tuple

class TTSModule:
    def __init__(self, model_path: str = "/app/models/voice.onnx"):
        """
        Requirement 9: Using piper-tts (ONNX) for sub-second latency.
        Using the standalone binary for robustness in Docker.
        """
        self.model_path = model_path
        self.binary_path = "piper"
        if not os.path.exists(self.model_path):
            print(f"Warning: TTS model not found at {self.model_path}. Please ensure it is baked into the Docker image.")

    def text_to_speech(self, text: str) -> Tuple[str, float]:
        """
        Converts text to speech using the piper binary and returns base64 wav.
        """
        start_time = time.perf_counter()
        try:
            # Command to run piper: 
            # echo "text" | piper --model voice.onnx --output_file -
            process = subprocess.run(
                ["piper", "--model", self.model_path, "--output_file", "-"],
                input=text.encode('utf-8'),
                capture_output=True,
                check=True
            )
            
            audio_b64 = base64.b64encode(process.stdout).decode("utf-8")
                
            latency_ms = (time.perf_counter() - start_time) * 1000
            return audio_b64, round(latency_ms, 2)

        except Exception as e:
            print(f"TTS Error: {e}")
            # Fallback to empty wav header if it fails
            wav_header = b"RIFF\x00\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x80>\x00\x00\x80>\x00\x00\x01\x00\x08\x00data\x00\x00\x00\x00"
            return base64.b64encode(wav_header).decode("utf-8"), 0.0

if __name__ == "__main__":
    # Quick test
    pass
