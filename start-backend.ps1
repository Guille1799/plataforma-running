#!/bin/bash
# start-all.ps1 - Start backend and frontend servers

Write-Host "================================" -ForegroundColor Cyan
Write-Host "RunCoach Platform - Development Environment" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

# Function to start backend
function Start-Backend {
    Write-Host "`n[1] Starting Backend Server..." -ForegroundColor Yellow
    cd "$PSScriptRoot\backend"
    
    Write-Host "    Installing dependencies (if needed)..." -ForegroundColor Gray
    & .\venv\Scripts\python.exe -m pip install -q --upgrade pip 2>&1 | Out-Null
    
    Write-Host "    Starting Uvicorn on http://127.0.0.1:8000..." -ForegroundColor Green
    & .\venv\Scripts\uvicorn.exe app.main:app --host 127.0.0.1 --port 8000 --reload
}

# Function to start frontend
function Start-Frontend {
    Write-Host "`n[2] Starting Frontend Server..." -ForegroundColor Yellow
    cd "$PSScriptRoot\frontend"
    
    Write-Host "    Installing dependencies (if needed)..." -ForegroundColor Gray
    npm install 2>&1 | Out-Null
    
    Write-Host "    Starting Next.js on http://localhost:3000..." -ForegroundColor Green
    Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
    npm run dev
}

# Clean up on exit
function Cleanup {
    Write-Host "`n`n[!] Shutting down servers..." -ForegroundColor Yellow
    Get-Process node, python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
    Write-Host "    [OK] All processes stopped" -ForegroundColor Green
}

trap { Cleanup }

# Display instructions
Write-Host "`nInstructions:" -ForegroundColor Cyan
Write-Host "  1. Backend will start in this terminal" -ForegroundColor Gray
Write-Host "  2. Open a new PowerShell terminal for Frontend" -ForegroundColor Gray
Write-Host "  3. Or run: Start-Process PowerShell -ArgumentList '-NoExit -Command &{cd '$PSScriptRoot\frontend'; npm run dev}'" -ForegroundColor Gray
Write-Host "`nURLs:" -ForegroundColor Cyan
Write-Host "  - Backend:  http://127.0.0.1:8000" -ForegroundColor Gray
Write-Host "  - Frontend: http://localhost:3000" -ForegroundColor Gray
Write-Host "  - Docs:     http://127.0.0.1:8000/docs" -ForegroundColor Gray
Write-Host "`nPress CTRL+C to stop all servers`n" -ForegroundColor Yellow

Start-Backend
