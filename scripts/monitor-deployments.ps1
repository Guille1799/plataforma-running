# Script de monitoreo de deployments en Vercel y Render
# Verifica el estado de los servicios haciendo health checks HTTP

param(
    [string]$BackendUrl = ""
)

$ErrorActionPreference = "Continue"

Write-Host "🔍 Monitoreo de Deployments - RunCoach AI" -ForegroundColor Cyan
Write-Host "Timestamp: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
Write-Host ("=" * 60) -ForegroundColor Gray
Write-Host ""

# URLs de producción (configuración centralizada)
$FRONTEND_URL = "https://plataforma-running.vercel.app"
$BACKEND_URL = "https://plataforma-running.onrender.com"

# Servicios a monitorear
$services = @(
    @{
        Name = "Frontend Vercel"
        Url = $FRONTEND_URL
        HealthEndpoint = $FRONTEND_URL
    },
    @{
        Name = "Backend API Render"
        Url = $BACKEND_URL
        HealthEndpoint = "$BACKEND_URL/health"
    }
)

# Si se proporciona URL de backend como parámetro, sobreescribir
if ($BackendUrl) {
    $BACKEND_URL = $BackendUrl.TrimEnd('/')
    $services[1].Url = $BACKEND_URL
    $services[1].HealthEndpoint = "$BACKEND_URL/health"
}

$results = @()

foreach ($service in $services) {
    $name = $service.Name
    $url = $service.Url
    $healthUrl = $service.HealthEndpoint
    
    Write-Host "Verificando $name..." -ForegroundColor Yellow
    Write-Host "  URL: $url" -ForegroundColor Gray
    Write-Host "  Health Check: $healthUrl" -ForegroundColor Gray
    
    try {
        $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
        $response = Invoke-WebRequest -Uri $healthUrl -Method Get -TimeoutSec 10 -UseBasicParsing -ErrorAction Stop
        $stopwatch.Stop()
        
        $statusCode = $response.StatusCode
        $responseTime = [math]::Round($stopwatch.ElapsedMilliseconds, 2)
        
        if ($statusCode -eq 200) {
            $status = "healthy"
            $icon = "✅"
            $color = "Green"
        }
        elseif ($statusCode -ge 300 -and $statusCode -lt 400) {
            $status = "redirecting"
            $icon = "⚠️"
            $color = "Yellow"
        }
        elseif ($statusCode -eq 503) {
            $status = "unavailable"
            $icon = "❌"
            $color = "Red"
        }
        elseif ($statusCode -ge 500) {
            $status = "error"
            $icon = "❌"
            $color = "Red"
        }
        else {
            $status = "warning"
            $icon = "⚠️"
            $color = "Yellow"
        }
        
        Write-Host "  $icon $name" -ForegroundColor $color
        Write-Host "    Status Code: $statusCode" -ForegroundColor Gray
        Write-Host "    Response Time: ${responseTime}ms" -ForegroundColor Gray
        Write-Host "    Status: $($status.ToUpper())" -ForegroundColor $color
        
        $results += @{
            Name = $name
            Url = $url
            Status = $status
            StatusCode = $statusCode
            ResponseTime = $responseTime
            Error = $null
        }
    }
    catch {
        $errorMessage = $_.Exception.Message
        
        if ($_.Exception.Response) {
            $statusCode = [int]$_.Exception.Response.StatusCode
            $status = if ($statusCode -eq 503) { "unavailable" } elseif ($statusCode -ge 500) { "error" } else { "warning" }
        }
        else {
            $statusCode = $null
            if ($errorMessage -like "*timeout*" -or $errorMessage -like "*timed out*") {
                $status = "timeout"
            }
            elseif ($errorMessage -like "*connect*" -or $errorMessage -like "*unreachable*") {
                $status = "unreachable"
            }
            else {
                $status = "error"
            }
        }
        
        $icon = "❌"
        $color = "Red"
        
        Write-Host "  $icon $name" -ForegroundColor $color
        if ($statusCode) {
            Write-Host "    Status Code: $statusCode" -ForegroundColor Gray
        }
        Write-Host "    Status: $($status.ToUpper())" -ForegroundColor $color
        Write-Host "    Error: $errorMessage" -ForegroundColor Red
        
        $results += @{
            Name = $name
            Url = $url
            Status = $status
            StatusCode = $statusCode
            ResponseTime = $null
            Error = $errorMessage
        }
    }
    
    Write-Host ""
}

# Resumen
Write-Host ("=" * 60) -ForegroundColor Gray
Write-Host "📊 Resumen" -ForegroundColor Cyan
Write-Host ""

$healthyCount = ($results | Where-Object { $_.Status -eq "healthy" }).Count
$totalCount = $results.Count

if ($healthyCount -eq $totalCount) {
    Write-Host "✅ Todos los servicios están operativos ($healthyCount/$totalCount)" -ForegroundColor Green
    exit 0
}
else {
    Write-Host "⚠️  Algunos servicios tienen problemas ($healthyCount/$totalCount operativos)" -ForegroundColor Yellow
    
    $failed = $results | Where-Object { $_.Status -ne "healthy" }
    foreach ($service in $failed) {
        Write-Host "  - $($service.Name): $($service.Status)" -ForegroundColor Red
    }
    
    exit 1
}
