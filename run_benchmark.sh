#!/bin/bash
# run_benchmark.sh
set -e

echo "Starting Real-Time Speech-to-Intent Latency Benchmark..."

# Ensure dependencies are installed for the benchmark script
# (Assumes local python has requests and numpy)
pip install -q requests numpy

# Run the benchmark
python benchmark.py

echo "Benchmark complete. Results saved to results/latency_report.json"
