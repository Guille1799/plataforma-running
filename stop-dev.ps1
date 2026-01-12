# Script PowerShell para detener backend (Docker) y frontend (Node)
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "🛑 DETENIENDO PLATAFORMA RUNNING" -ForegroundColor Red
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""

# Detener procesos de Node (Frontend)
Write-Host "[1/2] Deteniendo Frontend (Node)..." -ForegroundColor Yellow
$nodeProcesses = Get-Process -Name node -ErrorAction SilentlyContinue
if ($nodeProcesses) {
    foreach ($proc in $nodeProcesses) {
        Write-Host "  Deteniendo proceso PID: $($proc.Id)" -ForegroundColor Red
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
    }
    Write-Host "  [OK] Procesos de Node detenidos" -ForegroundColor Green
} else {
    Write-Host "  [OK] No hay procesos de Node corriendo" -ForegroundColor Gray
}

Write-Host ""

# Detener Docker
Write-Host "[2/2] Deteniendo Backend (Docker)..." -ForegroundColor Yellow
try {
    docker-compose -f docker-compose.dev.yml stop
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [OK] Contenedores de Docker detenidos" -ForegroundColor Green
    } else {
        Write-Host "  [WARNING] Error al detener Docker (puede que no esté corriendo)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  [WARNING] Error al detener Docker: $_" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "✅ Servidores detenidos correctamente" -ForegroundColor Green
Write-Host ""

# Opción para eliminar contenedores también
$removeContainers = Read-Host "¿Deseas eliminar los contenedores también? (s/N)"
if ($removeContainers -eq "s" -or $removeContainers -eq "S") {
    Write-Host ""
    Write-Host "Eliminando contenedores..." -ForegroundColor Yellow
    docker-compose -f docker-compose.dev.yml down
    Write-Host "  [OK] Contenedores eliminados" -ForegroundColor Green
}

Write-Host ""
