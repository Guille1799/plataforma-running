#!/usr/bin/env python
"""Simple startup script for FastAPI backend"""
import subprocess
import sys
import time
import os

os.chdir(r"c:\Users\Guille\proyectos\plataforma-running\backend")

print("🚀 Starting FastAPI Backend Server...")
print("   Port: 8000")
print("   URL: http://localhost:8000")
print("   Swagger: http://localhost:8000/docs")
print()

try:
    subprocess.run([
        sys.executable, "-m", "uvicorn", 
        "app.main:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--reload"
    ], check=True)
except KeyboardInterrupt:
    print("\n✋ Server stopped by user")
except Exception as e:
    print(f"\n❌ Error: {e}")
    sys.exit(1)
