"""
Simple test para verificar que Paquete 2 puede ejecutarse
Será ejecutado como subprocess
"""
import subprocess
import sys
import time

# Primero, arranca backend
print("=" * 60)
print("Starting backend...")
print("=" * 60)

backend_proc = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "app.main:app", "--port", "8000"],
    cwd=r"c:\Users\guill\Desktop\plataforma-running\backend",
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True
)

# Espera a que arranque
print("Waiting 8 seconds for backend to start...")
time.sleep(8)

# Verifica que el proceso siga corriendo
if backend_proc.poll() is not None:
    print("ERROR: Backend terminated unexpectedly!")
    print(backend_proc.stdout.read())
    sys.exit(1)

print("Backend started successfully (PID: {})".format(backend_proc.pid))

# Ahora ejecuta el test
print("\n" + "=" * 60)
print("Running test...")
print("=" * 60 + "\n")

test_proc = subprocess.run(
    [sys.executable, r"c:\Users\guill\Desktop\plataforma-running\e2e_test_package_2.py"],
    cwd=r"c:\Users\guill\Desktop\plataforma-running\backend"
)

# Detener backend
print("\n" + "=" * 60)
print("Stopping backend...")
print("=" * 60)

backend_proc.terminate()
try:
    backend_proc.wait(timeout=5)
except subprocess.TimeoutExpired:
    backend_proc.kill()

print("Done!")
sys.exit(test_proc.returncode)
