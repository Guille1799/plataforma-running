# Script PowerShell para reiniciar el backend
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "🔄 REINICIANDO BACKEND" -ForegroundColor Yellow
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/3] Deteniendo procesos de Python en puerto 8000..." -ForegroundColor Yellow

# Obtener procesos en puerto 8000
$processes = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique

if ($processes) {
    foreach ($pid in $processes) {
        $proc = Get-Process -Id $pid -ErrorAction SilentlyContinue
        if ($proc -and $proc.ProcessName -like "*python*") {
            Write-Host "  Deteniendo proceso PID: $pid ($($proc.ProcessName))" -ForegroundColor Red
            Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
        }
    }
} else {
    Write-Host "  No hay procesos en el puerto 8000" -ForegroundColor Gray
}

Write-Host ""
Write-Host "[2/3] Esperando 2 segundos..." -ForegroundColor Yellow
Start-Sleep -Seconds 2

Write-Host ""
Write-Host "[3/3] Iniciando backend..." -ForegroundColor Yellow
Write-Host ""

Set-Location -Path "$PSScriptRoot\backend"
python run_server.py

Write-Host ""
Write-Host "Backend detenido." -ForegroundColor Red
Read-Host "Presiona Enter para salir"
