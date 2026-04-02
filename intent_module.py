import time
from typing import List, Tuple
import numpy as np

class IntentModule:
    ALLOWED_INTENTS = [
        "TurnOn", "TurnOff", "SetBrightness", "GetTemperature", 
        "PlayMusic", "StopMusic", "SetTimer", "GetWeather"
    ]

    def __init__(self):
        """
        Requirement 6: Support at least 8 specific intents.
        Using a simple but effective keyword and pattern matcher for maximum speed (sub-10ms).
        In a real scenario, this would be a fine-tuned DistilBERT or similar.
        """
        self.intent_keywords = {
            "TurnOn": ["on", "switch on", "start"],
            "TurnOff": ["off", "switch off", "stop", "shut down"],
            "SetBrightness": ["brightness", "brighten", "dim", "light level"],
            "GetTemperature": ["temperature", "temp", "how hot", "how cold"],
            "PlayMusic": ["play", "music", "song", "tunes"],
            "StopMusic": ["stop music", "pause music", "quiet"],
            "SetTimer": ["timer", "set a timer", "remind me"],
            "GetWeather": ["weather", "forecast", "outside", "rain"]
        }

    def predict(self, text: str) -> Tuple[str, float, float]:
        """
        Predicts intent from text. Returns (intent, confidence, latency_ms).
        """
        start_time = time.perf_counter()
        text = text.lower()
        
        # Simple heuristic for intent classification (Requirement 6)
        # In production, we'd use a small Transformer (e.g. DistilBERT)
        best_intent = "TurnOn"  # Default
        max_score = 0.0

        for intent, keywords in self.intent_keywords.items():
            score = sum(1 for kw in keywords if kw in text)
            if score > max_score:
                max_score = score
                best_intent = intent
        
        # Normalize confidence (mocking a real model output)
        confidence = 0.85 if max_score > 0 else 0.4
        
        latency_ms = (time.perf_counter() - start_time) * 1000
        return best_intent, round(confidence, 2), round(latency_ms, 2)

if __name__ == "__main__":
    # Quick test
    nm = IntentModule()
    print(nm.predict("turn on the lights"))
