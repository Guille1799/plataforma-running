#!/usr/bin/env python
"""Simple startup script for FastAPI backend"""
import subprocess
import sys
import time
import os
from pathlib import Path

# Get the directory where this script is located
script_dir = Path(__file__).parent.resolve()
os.chdir(script_dir)

print("[START] Starting FastAPI Backend Server...")
print("   Port: 8000")
print("   URL: http://localhost:8000")
print("   Swagger: http://localhost:8000/docs")
print()

try:
    # Set environment variable to disable buffering for immediate log output
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    
    subprocess.run(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "app.main:app",
            "--host",
            "0.0.0.0",
            "--port",
            "8000",
            "--reload",
            "--log-level",
            "info",
            "--no-access-log",  # Reduce noise, only show application logs
        ],
        check=True,
        env=env,  # Pass environment with unbuffered output
    )
except KeyboardInterrupt:
    print("\n[STOP] Server stopped by user")
except Exception as e:
    print(f"\n[ERROR] Error: {e}")
    sys.exit(1)
