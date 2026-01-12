# Script PowerShell para iniciar el backend
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "🚀 INICIANDO BACKEND" -ForegroundColor Green
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""

Set-Location -Path "$PSScriptRoot\backend"
Write-Host "Iniciando Backend..." -ForegroundColor Yellow
Write-Host ""

python run_server.py

Write-Host ""
Write-Host "Backend detenido." -ForegroundColor Red
Read-Host "Presiona Enter para salir"
