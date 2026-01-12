# Script PowerShell para limpiar locks y procesos de Node colgados
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "🧹 LIMPIANDO FRONTEND" -ForegroundColor Yellow
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""

# Detener procesos de Node
Write-Host "[1/3] Deteniendo procesos de Node..." -ForegroundColor Yellow
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

# Limpiar lock files de Next.js
Write-Host "[2/3] Limpiando lock files de Next.js..." -ForegroundColor Yellow
$lockPath = Join-Path $PSScriptRoot ".next\dev\lock"
if (Test-Path $lockPath) {
    Remove-Item $lockPath -Force -ErrorAction SilentlyContinue
    Write-Host "  [OK] Lock file eliminado: $lockPath" -ForegroundColor Green
} else {
    Write-Host "  [OK] No hay lock file" -ForegroundColor Gray
}

# Limpiar otros archivos temporales de Next.js
$nextCache = Join-Path $PSScriptRoot ".next"
if (Test-Path $nextCache) {
    Write-Host "  [INFO] Cache de Next.js encontrado en: $nextCache" -ForegroundColor Gray
    Write-Host "  [INFO] Para limpiar completamente, ejecuta: Remove-Item -Recurse -Force .next" -ForegroundColor Gray
}

Write-Host ""

# Verificar puerto 3000
Write-Host "[3/3] Verificando puerto 3000..." -ForegroundColor Yellow
$port3000 = Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue
if ($port3000) {
    Write-Host "  [WARNING] Puerto 3000 aún en uso por proceso: $($port3000.OwningProcess)" -ForegroundColor Yellow
    Write-Host "  Ejecuta: Get-Process -Id $($port3000.OwningProcess) | Stop-Process -Force" -ForegroundColor Gray
} else {
    Write-Host "  [OK] Puerto 3000 libre" -ForegroundColor Green
}

Write-Host ""
Write-Host "✅ Limpieza completada!" -ForegroundColor Green
Write-Host ""
Write-Host "Ahora puedes ejecutar: npm run dev" -ForegroundColor Cyan
Write-Host ""
