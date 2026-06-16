import time
import base64
import os
import subprocess
import json
import struct
from typing import Tuple

class TTSModule:
    def __init__(self, model_path: str = "/app/models/en_US-lessac-medium.onnx"):
        """
        Requirement 9: Using piper-tts (ONNX) for sub-second latency.
        Optimized to use a persistent subprocess and process audio completely in-memory.
        """
        self.model_path = model_path
        self.binary_path = "piper"
        self.process = None
        
        if not os.path.exists(self.model_path):
            print(f"Warning: TTS model not found at {self.model_path}. Please ensure it is baked into the Docker image.")
        else:
            self._start_process()

    def _start_process(self):
        try:
            # We start piper in json-input mode outputting directly to stdout (-)
            self.process = subprocess.Popen(
                ["piper", "--model", self.model_path, "--json-input", "--output_file", "-"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL
            )
        except Exception as e:
            print(f"TTS Process Start Error: {e}")
            self.process = None

    def text_to_speech(self, text: str) -> Tuple[str, float]:
        """
        Converts text to speech using the persistent piper binary and returns base64 wav.
        Processes output completely in-memory via stdin/stdout pipe.
        """
        start_time = time.perf_counter()
        
        try:
            # Check if process is running, restart if needed
            if self.process is None or self.process.poll() is not None:
                self._start_process()
                
            if self.process is None:
                raise Exception("Failed to start/restart piper process")

            # Send synthesis request via JSON input bytes
            payload = {"text": text}
            self.process.stdin.write((json.dumps(payload) + "\n").encode('utf-8'))
            self.process.stdin.flush()
            
            # Read first 8 bytes of the WAV file from stdout
            riff = self.process.stdout.read(4)
            if riff != b"RIFF":
                raise Exception(f"Expected RIFF header, got {riff}")
                
            size_bytes = self.process.stdout.read(4)
            if len(size_bytes) < 4:
                raise Exception("Failed to read WAV size bytes")
                
            wav_size = struct.unpack("<I", size_bytes)[0]
            
            # Read the rest of the WAV file
            wav_data = self.process.stdout.read(wav_size)
            if len(wav_data) < wav_size:
                raise Exception("Incomplete WAV data read from stdout")
                
            full_wav = riff + size_bytes + wav_data
            audio_b64 = base64.b64encode(full_wav).decode("utf-8")
                
            latency_ms = (time.perf_counter() - start_time) * 1000
            return audio_b64, round(latency_ms, 2)

        except Exception as e:
            print(f"TTS Error: {e}")
            # Fallback to empty wav header if it fails
            wav_header = b"RIFF\x00\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x80>\x00\x00\x80>\x00\x00\x01\x00\x08\x00data\x00\x00\x00\x00"
            return base64.b64encode(wav_header).decode("utf-8"), 0.0

    def __del__(self):
        if hasattr(self, 'process') and self.process is not None:
            try:
                self.process.stdin.close()
                self.process.terminate()
                self.process.wait(timeout=1)
            except Exception:
                pass

if __name__ == "__main__":
    # Quick test
    pass
