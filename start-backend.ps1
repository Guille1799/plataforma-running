# Start Backend Server
Write-Host "`n" -ForegroundColor Green
Write-Host "╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║        🚀 RunCoach AI - Backend Server (FastAPI)         ║" -ForegroundColor Cyan
Write-Host "║                   Port: 8000                             ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

$backend_path = "c:\Users\Guille\proyectos\plataforma-running\backend"
$conda_env = "C:\Users\Guille\miniconda3"

Write-Host "📂 Location: $backend_path" -ForegroundColor Yellow
Write-Host "🐍 Python: $conda_env" -ForegroundColor Yellow
Write-Host ""

Set-Location $backend_path

Write-Host "⏳ Starting Uvicorn..." -ForegroundColor Cyan
& "$conda_env\Scripts\conda.exe" run -p $conda_env `
    python -m uvicorn app.main:app `
    --host 0.0.0.0 --port 8000 --reload

Write-Host "`n✋ Server stopped" -ForegroundColor Yellow
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
