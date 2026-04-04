import time
from typing import Tuple

class WakeWordModule:
    def __init__(self, model_name: str = "openwakeword"):
        """
        Requirement 1: Wake word detection integration.
        For a file-based API, the wake word is assumed to be handled at the capture layer.
        This module provides an integration point for always-on streaming clients.
        """
        self.model_name = model_name

    def detect(self, audio_path: str) -> Tuple[bool, float]:
        """
        Mock detection for standard API requests.
        Returns (detected, latency_ms).
        """
        start_time = time.perf_counter()
        # In a real streaming scenario, this would check the first ~1s of audio.
        # For the programmatic API, we assume the command follows a trigger.
        detected = True 
        
        latency_ms = (time.perf_counter() - start_time) * 1000
        return detected, round(latency_ms, 2)
