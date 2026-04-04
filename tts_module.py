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
        self._ensure_model_exists()

    def _ensure_model_exists(self):
        """
        Downloads the ONNX model and config at runtime if not present.
        This enables a much smaller Docker image footprint (~500MB).
        """
        if not os.path.exists(self.model_path):
            print(f"Downloading TTS model to {self.model_path}...")
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            url = "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx?download=true"
            response = requests.get(url, stream=True)
            response.raise_for_status()
            with open(self.model_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Same for config
            config_url = url + ".json"
            config_path = self.model_path + ".json"
            config_resp = requests.get(config_url)
            config_resp.raise_for_status()
            with open(config_path, "wb") as f:
                f.write(config_resp.content)
            print("TTS model download complete.")

    def text_to_speech(self, text: str) -> Tuple[str, float]:
        """
        Converts text to speech using the piper binary and returns base64 wav.
        """
        start_time = time.perf_counter()
        
        output_file = f"temp_response_{int(time.time())}.wav"
        try:
            # Command to run piper: 
            # echo "text" | piper --model voice.onnx --output_file out.wav
            process = subprocess.run(
                ["piper", "--model", self.model_path, "--output_file", output_file],
                input=text.encode('utf-8'),
                capture_output=True,
                check=True
            )
            
            with open(output_file, "rb") as f:
                audio_b64 = base64.b64encode(f.read()).decode("utf-8")
                
            latency_ms = (time.perf_counter() - start_time) * 1000
            return audio_b64, round(latency_ms, 2)

        except Exception as e:
            print(f"TTS Error: {e}")
            # Fallback to empty wav header if it fails
            wav_header = b"RIFF\x00\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x80>\x00\x00\x80>\x00\x00\x01\x00\x08\x00data\x00\x00\x00\x00"
            return base64.b64encode(wav_header).decode("utf-8"), 0.0
        finally:
            if os.path.exists(output_file):
                os.remove(output_file)

if __name__ == "__main__":
    # Quick test
    pass
