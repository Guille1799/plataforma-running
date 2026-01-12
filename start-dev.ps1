# Script PowerShell para iniciar backend (Docker) y frontend (local)
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "🚀 INICIANDO PLATAFORMA RUNNING" -ForegroundColor Green
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""

# Verificar Docker
Write-Host "[1/4] Verificando Docker..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [OK] Docker encontrado: $dockerVersion" -ForegroundColor Green
    } else {
        Write-Host "  [ERROR] Docker no está instalado o no está corriendo" -ForegroundColor Red
        Write-Host "  Por favor, instala Docker Desktop y asegúrate de que esté corriendo" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "  [ERROR] Docker no está instalado o no está corriendo" -ForegroundColor Red
    Write-Host "  Por favor, instala Docker Desktop y asegúrate de que esté corriendo" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Limpiar frontend antes de iniciar
Write-Host "[2/4] Limpiando frontend..." -ForegroundColor Yellow
$nodeProcesses = Get-Process -Name node -ErrorAction SilentlyContinue
if ($nodeProcesses) {
    Write-Host "  Deteniendo procesos de Node existentes..." -ForegroundColor Yellow
    $nodeProcesses | Stop-Process -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 1
}

$lockPath = Join-Path $PSScriptRoot ".next\dev\lock"
if (Test-Path $lockPath) {
    Remove-Item $lockPath -Force -ErrorAction SilentlyContinue
    Write-Host "  [OK] Lock file eliminado" -ForegroundColor Green
}

Write-Host ""

# Iniciar backend con Docker
Write-Host "[3/4] Iniciando Backend (Docker)..." -ForegroundColor Yellow
Write-Host "  Esto puede tardar unos segundos..." -ForegroundColor Gray
Write-Host ""

try {
    docker-compose -f docker-compose.dev.yml up -d
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [OK] Backend iniciado" -ForegroundColor Green
        
        # Esperar a que el backend esté listo
        Write-Host "  Esperando a que el backend esté listo..." -ForegroundColor Gray
        $maxAttempts = 30
        $attempt = 0
        $backendReady = $false
        
        while ($attempt -lt $maxAttempts -and -not $backendReady) {
            Start-Sleep -Seconds 2
            try {
                $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
                if ($response.StatusCode -eq 200) {
                    $backendReady = $true
                    Write-Host "  [OK] Backend listo!" -ForegroundColor Green
                }
            } catch {
                $attempt++
                Write-Host "  Intentando conectar... ($attempt/$maxAttempts)" -ForegroundColor Gray
            }
        }
        
        if (-not $backendReady) {
            Write-Host "  [WARNING] Backend no respondió en el tiempo esperado" -ForegroundColor Yellow
            Write-Host "  Puede que aún esté iniciando. Verifica con: docker-compose -f docker-compose.dev.yml ps" -ForegroundColor Gray
        }
    } else {
        Write-Host "  [ERROR] Error al iniciar Docker" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "  [ERROR] Error al iniciar Docker: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Iniciar frontend
Write-Host "[4/4] Iniciando Frontend (Next.js)..." -ForegroundColor Yellow
Write-Host "  Se abrirá en una nueva ventana" -ForegroundColor Gray
Write-Host ""

try {
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; npm run dev"
    Write-Host "  [OK] Frontend iniciando en nueva ventana" -ForegroundColor Green
} catch {
    Write-Host "  [ERROR] Error al iniciar frontend: $_" -ForegroundColor Red
    Write-Host "  Intenta ejecutar manualmente: npm run dev" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "✅ TODO LISTO!" -ForegroundColor Green
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "👉 Backend API: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "👉 Frontend:    http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Para detener todo, ejecuta: .\stop-dev.ps1" -ForegroundColor Yellow
Write-Host ""
