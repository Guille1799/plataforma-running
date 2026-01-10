# ============================================================================
# Sistema de Monitoreo Robusto de Producción - RunCoach AI
# ============================================================================
# Monitorea el estado de Vercel y Render, detecta errores y genera reportes

param(
    [switch]$Continuous = $false,
    [int]$IntervalSeconds = 60,
    [switch]$CheckLogs = $false,
    [string]$LogFile = "monitoring-report-$(Get-Date -Format 'yyyyMMdd-HHmmss').txt"
)

$ErrorActionPreference = "Continue"

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

$FRONTEND_URL = "https://plataforma-running.vercel.app"
$BACKEND_URL = "https://plataforma-running.onrender.com"

$services = @(
    @{
        Name = "Frontend Vercel"
        Url = $FRONTEND_URL
        HealthEndpoint = $FRONTEND_URL
        Type = "Frontend"
    },
    @{
        Name = "Backend API Render"
        Url = $BACKEND_URL
        HealthEndpoint = "$BACKEND_URL/health"
        Type = "Backend"
    }
)

# ============================================================================
# FUNCIONES DE MONITOREO
# ============================================================================

function Test-ServiceHealth {
    param(
        [string]$Name,
        [string]$Url,
        [string]$HealthEndpoint
    )
    
    $result = @{
        Name = $Name
        Url = $Url
        HealthEndpoint = $HealthEndpoint
        Status = "unknown"
        StatusCode = $null
        ResponseTime = $null
        Error = $null
        Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        Details = $null
    }
    
    try {
        $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
        $response = Invoke-WebRequest -Uri $HealthEndpoint -Method Get -TimeoutSec 15 -UseBasicParsing -ErrorAction Stop
        $stopwatch.Stop()
        
        $result.StatusCode = $response.StatusCode
        $result.ResponseTime = [math]::Round($stopwatch.ElapsedMilliseconds, 2)
        
        if ($response.StatusCode -eq 200) {
            $result.Status = "healthy"
            try {
                $jsonResponse = $response.Content | ConvertFrom-Json
                $result.Details = $jsonResponse
            } catch {
                # No es JSON, está bien
            }
        } elseif ($response.StatusCode -ge 300 -and $response.StatusCode -lt 400) {
            $result.Status = "redirecting"
        } elseif ($response.StatusCode -eq 503) {
            $result.Status = "unavailable"
        } elseif ($response.StatusCode -ge 500) {
            $result.Status = "error"
            $result.Error = "HTTP $($response.StatusCode)"
        } else {
            $result.Status = "warning"
        }
    }
    catch {
        $errorMessage = $_.Exception.Message
        
        if ($_.Exception.Response) {
            $statusCode = [int]$_.Exception.Response.StatusCode
            $result.StatusCode = $statusCode
            $result.Status = if ($statusCode -eq 503) { "unavailable" } elseif ($statusCode -ge 500) { "error" } else { "warning" }
            $result.Error = "HTTP $statusCode - $errorMessage"
        }
        else {
            if ($errorMessage -like "*timeout*" -or $errorMessage -like "*timed out*") {
                $result.Status = "timeout"
                $result.Error = "Timeout después de 15 segundos"
            }
            elseif ($errorMessage -like "*connect*" -or $errorMessage -like "*unreachable*" -or $errorMessage -like "*resolve*") {
                $result.Status = "unreachable"
                $result.Error = "No se pudo conectar al servidor"
            }
            else {
                $result.Status = "error"
                $result.Error = $errorMessage
            }
        }
    }
    
    return $result
}

function Write-ServiceStatus {
    param($Result)
    
    $name = $Result.Name
    $status = $Result.Status
    $statusCode = $Result.StatusCode
    $responseTime = $Result.ResponseTime
    $error = $Result.Error
    
    # Seleccionar color según el estado
    switch ($status) {
        "healthy" {
            $color = "Green"
            $icon = "✅"
        }
        "redirecting" {
            $color = "Yellow"
            $icon = "⚠️"
        }
        { $_ -in "unreachable", "timeout", "unavailable", "error" } {
            $color = "Red"
            $icon = "❌"
        }
        default {
            $color = "Yellow"
            $icon = "⚠️"
        }
    }
    
    Write-Host ""
    Write-Host "$icon $name" -ForegroundColor $color
    Write-Host "  URL: $($Result.Url)" -ForegroundColor Gray
    Write-Host "  Health: $($Result.HealthEndpoint)" -ForegroundColor Gray
    
    if ($statusCode) {
        Write-Host "  Status Code: $statusCode" -ForegroundColor Gray
    }
    
    if ($responseTime) {
        $timeColor = if ($responseTime -lt 1000) { "Green" } elseif ($responseTime -lt 3000) { "Yellow" } else { "Red" }
        Write-Host "  Response Time: ${responseTime}ms" -ForegroundColor $timeColor
    }
    
    Write-Host "  Status: $($status.ToUpper())" -ForegroundColor $color
    
    if ($error) {
        Write-Host "  Error: $error" -ForegroundColor Red
    }
    
    if ($Result.Details) {
        Write-Host "  Details: $($Result.Details | ConvertTo-Json -Compress)" -ForegroundColor Gray
    }
}

function Write-MonitoringReport {
    param($Results, $LogFile)
    
    $report = @"
================================================================================
MONITOREO DE PRODUCCIÓN - RunCoach AI
================================================================================
Fecha: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
Servicios Monitoreados: $($Results.Count)

"@
    
    foreach ($result in $Results) {
        $report += @"
SERVICIO: $($result.Name)
URL: $($result.Url)
Health Endpoint: $($result.HealthEndpoint)
Estado: $($result.Status)
Status Code: $($result.StatusCode)
Response Time: $($result.ResponseTime)ms
Error: $($result.Error)
Timestamp: $($result.Timestamp)

"@
    }
    
    $healthyCount = ($Results | Where-Object { $_.Status -eq "healthy" }).Count
    $totalCount = $Results.Count
    
    $report += @"
================================================================================
RESUMEN
================================================================================
Servicios Operativos: $healthyCount/$totalCount

"@
    
    if ($healthyCount -eq $totalCount) {
        $report += "✅ Todos los servicios están operativos`n"
    } else {
        $failed = $Results | Where-Object { $_.Status -ne "healthy" }
        $report += "⚠️ Servicios con problemas:`n"
        foreach ($service in $failed) {
            $report += "  - $($service.Name): $($service.Status) - $($service.Error)`n"
        }
    }
    
    $report += "`n================================================================================`n"
    
    # Guardar en archivo
    $report | Out-File -FilePath $LogFile -Encoding UTF8
    
    Write-Host "`n📄 Reporte guardado en: $LogFile" -ForegroundColor Cyan
}

# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

function Start-Monitoring {
    Write-Host "🔍 Sistema de Monitoreo de Producción - RunCoach AI" -ForegroundColor Cyan
    Write-Host "Timestamp: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
    Write-Host ("=" * 80) -ForegroundColor Gray
    Write-Host ""
    
    $allResults = @()
    
    foreach ($service in $services) {
        $result = Test-ServiceHealth -Name $service.Name -Url $service.Url -HealthEndpoint $service.HealthEndpoint
        $allResults += $result
        Write-ServiceStatus -Result $result
    }
    
    # Resumen
    Write-Host ""
    Write-Host ("=" * 80) -ForegroundColor Gray
    Write-Host "📊 Resumen" -ForegroundColor Cyan
    Write-Host ""
    
    $healthyCount = ($allResults | Where-Object { $_.Status -eq "healthy" }).Count
    $totalCount = $allResults.Count
    
    if ($healthyCount -eq $totalCount) {
        Write-Host "✅ Todos los servicios están operativos ($healthyCount/$totalCount)" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Algunos servicios tienen problemas ($healthyCount/$totalCount operativos)" -ForegroundColor Yellow
        
        $failed = $allResults | Where-Object { $_.Status -ne "healthy" }
        foreach ($service in $failed) {
            Write-Host "  - $($service.Name): $($service.Status)" -ForegroundColor Red
            if ($service.Error) {
                Write-Host "    Error: $($service.Error)" -ForegroundColor Red
            }
        }
    }
    
    # Generar reporte
    Write-MonitoringReport -Results $allResults -LogFile $LogFile
    
    return $allResults
}

# ============================================================================
# EJECUCIÓN
# ============================================================================

if ($Continuous) {
    Write-Host "🔄 Modo continuo activado (intervalo: $IntervalSeconds segundos)" -ForegroundColor Yellow
    Write-Host "Presiona Ctrl+C para detener`n" -ForegroundColor Gray
    
    while ($true) {
        $results = Start-Monitoring
        Write-Host "`n⏳ Esperando $IntervalSeconds segundos antes del siguiente check...`n" -ForegroundColor Gray
        Start-Sleep -Seconds $IntervalSeconds
    }
} else {
    $results = Start-Monitoring
    
    # Exit code basado en resultados
    $healthyCount = ($results | Where-Object { $_.Status -eq "healthy" }).Count
    $totalCount = $results.Count
    
    if ($healthyCount -eq $totalCount) {
        exit 0
    } else {
        exit 1
    }
}
