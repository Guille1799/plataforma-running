# Script para ejecutar backend y test en paralelo

$backendDir = "c:\Users\guill\Desktop\plataforma-running\backend"
$rootDir = "c:\Users\guill\Desktop\plataforma-running"

# Iniciar backend en background job
Write-Host "Starting backend..." -ForegroundColor Cyan
$backendJob = Start-Job -ScriptBlock {
    cd $using:backendDir
    & .\venv\Scripts\uvicorn.exe app.main:app --port 8000
}

Write-Host "Waiting for backend to start..." -ForegroundColor Cyan
Start-Sleep -Seconds 10

# Verificar que backend está listo
$attempt = 0
while ($attempt -lt 10) {
    try {
        $response = Invoke-WebRequest -Uri http://127.0.0.1:8000/docs -TimeoutSec 2
        Write-Host "Backend is ready!" -ForegroundColor Green
        break
    } catch {
        Write-Host "Waiting... ($attempt/10)"
        Start-Sleep -Seconds 2
        $attempt++
    }
}

# Ejecutar test
Write-Host "Running test..." -ForegroundColor Green
cd $backendDir
& .\venv\Scripts\python.exe "$rootDir\e2e_test_package_2.py"

# Limpiar
Write-Host "Stopping backend..." -ForegroundColor Cyan
Stop-Job -Job $backendJob
Remove-Job -Job $backendJob
