import requests
import time
import json
import os
import numpy as np
from typing import List, Dict

# Configuration
API_URL = "http://localhost:8000/process-intent"
TEST_AUDIO_PATH = "test_audio.wav"
ITERATIONS = 20
RESULTS_DIR = "results"

def create_dummy_wav(path: str):
    """Creates a basic 1-second dummy WAV file for testing."""
    import wave
    import struct
    
    with wave.open(path, 'w') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(16000)
        # 1 second of silence
        for _ in range(16000):
            value = struct.pack('<h', 0)
            wav.writeframesraw(value)

def run_benchmark():
    print(f"Starting benchmark against {API_URL}...")
    
    if not os.path.exists(TEST_AUDIO_PATH):
        print("Creating dummy test audio...")
        create_dummy_wav(TEST_AUDIO_PATH)
        
    latencies: Dict[str, List[float]] = {
        "asr": [],
        "intent": [],
        "tts": [],
        "total": []
    }
    
    # Warmup
    print("Warming up...")
    try:
        with open(TEST_AUDIO_PATH, "rb") as f:
            requests.post(API_URL, files={"audio": f}, timeout=30)
    except Exception as e:
        print(f"Warmup failed: {e}. Is the server running?")
        return

    print(f"Running {ITERATIONS} iterations...")
    for i in range(ITERATIONS):
        try:
            with open(TEST_AUDIO_PATH, "rb") as f:
                start_time = time.perf_counter()
                response = requests.post(API_URL, files={"audio": f}, timeout=15)
                end_time = time.perf_counter()
                
                if response.status_code == 200:
                    data = response.json()
                    lats = data["latencies_ms"]
                    latencies["asr"].append(lats["asr"])
                    latencies["intent"].append(lats["intent"])
                    latencies["tts"].append(lats["tts"])
                    latencies["total"].append(lats["total"])
                    print(f"Iteration {i+1}: {lats['total']}ms")
                else:
                    print(f"Iteration {i+1} failed: {response.status_code}")
        except Exception as e:
            print(f"Iteration {i+1} error: {e}")

    # Calculate statistics
    report = {}
    
    for key, values in latencies.items():
        if not values: continue
        report[f"{key}_ms"] = {
            "p50": round(float(np.percentile(values, 50)), 2),
            "p95": round(float(np.percentile(values, 95)), 2),
            "p99": round(float(np.percentile(values, 99)), 2)
        }

    # Save report
    os.makedirs(RESULTS_DIR, exist_ok=True)
    with open(os.path.join(RESULTS_DIR, "latency_report.json"), "w") as f:
        json.dump(report, f, indent=4)
    
    print("\nBenchmark Results:")
    print(json.dumps(report, indent=4))
    
    # Target check
    target_met = report.get("total_ms", {}).get("p95", 9999) < 2000
    
    if target_met:
        print("\n✅ SUCCESS: P95 latency is under 2 seconds.")
    else:
        print("\n❌ FAILED: P95 latency exceeds 2 seconds.")

if __name__ == "__main__":
    run_benchmark()
