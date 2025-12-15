#!/usr/bin/env pwsh
# RunCoach AI - Local Development Server Launcher
# Esta es la forma SIMPLE de iniciar todo

param(
    [switch]$Backend,
    [switch]$Frontend,
    [switch]$Both,
    [switch]$Kill
)

$ErrorActionPreference = 'Continue'

function Show-Banner {
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║         🚀 RunCoach AI - Local Development Servers        ║" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
}

function Kill-Processes {
    Write-Host "🛑 Deteniendo procesos..." -ForegroundColor Yellow
    Get-Process -Name python -ErrorAction SilentlyContinue | Stop-Process -Force
    Get-Process -Name node -ErrorAction SilentlyContinue | Stop-Process -Force
    Start-Sleep -Seconds 2
    Write-Host "✅ Procesos detenidos" -ForegroundColor Green
}

function Start-Backend {
    Write-Host ""
    Write-Host "📍 Backend: FastAPI en http://localhost:8000" -ForegroundColor Green
    Write-Host "📄 Swagger Docs: http://localhost:8000/docs" -ForegroundColor Green
    Write-Host ""
    
    Push-Location "$PSScriptRoot\backend"
    
    $conda = "C:\Users\Guille\miniconda3"
    Write-Host "⏳ Iniciando..." -ForegroundColor Yellow
    
    & "$conda\Scripts\conda.exe" run -p $conda python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    
    Pop-Location
}

function Start-Frontend {
    Write-Host ""
    Write-Host "📍 Frontend: Next.js en http://localhost:3000" -ForegroundColor Green
    Write-Host ""
    
    Push-Location "$PSScriptRoot"
    
    Write-Host "⏳ Iniciando..." -ForegroundColor Yellow
    
    npm run dev
    
    Pop-Location
}

# Main logic
Show-Banner

if ($Kill) {
    Kill-Processes
    exit 0
}

if ($Both -or ($Backend -and $Frontend)) {
    Write-Host "⚠️  IMPORTANTE: Abre ESTA terminal en 2 ventanas SEPARADAS" -ForegroundColor Yellow
    Write-Host "   Terminal 1: .\run-servers.ps1 -Backend" -ForegroundColor Cyan
    Write-Host "   Terminal 2: .\run-servers.ps1 -Frontend" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "O usa: .\run-servers.ps1 -Kill  para detener todo" -ForegroundColor Yellow
    exit 1
}

if ($Backend) {
    Kill-Processes
    Start-Backend
}
elseif ($Frontend) {
    Kill-Processes
    Start-Frontend
}
else {
    Write-Host "USO:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  .\run-servers.ps1 -Backend    # Inicia solo backend (puerto 8000)" -ForegroundColor White
    Write-Host "  .\run-servers.ps1 -Frontend   # Inicia solo frontend (puerto 3000)" -ForegroundColor White
    Write-Host "  .\run-servers.ps1 -Kill       # Detiene todos los procesos" -ForegroundColor White
    Write-Host ""
    Write-Host "INSTRUCCIONES:" -ForegroundColor Yellow
    Write-Host "  1. Abre PowerShell Terminal 1" -ForegroundColor White
    Write-Host "  2. Ejecuta: .\run-servers.ps1 -Backend" -ForegroundColor Cyan
    Write-Host "  3. Espera hasta ver '✓ Started server process'" -ForegroundColor White
    Write-Host "  4. Abre PowerShell Terminal 2" -ForegroundColor White
    Write-Host "  5. Ejecuta: .\run-servers.ps1 -Frontend" -ForegroundColor Cyan
    Write-Host "  6. Abre navegador: http://localhost:3000" -ForegroundColor Green
    Write-Host ""
}
