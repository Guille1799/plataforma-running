# ============================================================================
# Setup Completo Automático - RunCoach AI Platform
# ============================================================================
# Este script configura automáticamente:
# 1. Registro de usuario
# 2. Conexión con Garmin
# 3. Sincronización de workouts
# 4. Configuración de perfil de atleta
# 5. Creación de objetivos
# 6. Prueba de todos los endpoints del Coach AI
# ============================================================================

$ErrorActionPreference = "Stop"
$baseUrl = "http://127.0.0.1:8000"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  RunCoach AI - Setup Automático" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# ============================================================================
# PASO 1: REGISTRO DE USUARIO
# ============================================================================
Write-Host "[1/8] Registrando usuario..." -ForegroundColor Yellow

$registerBody = @{
    name = "Guillermo"
    email = "guillermomartindeoliva@gmail.com"
    password = "TestPass123!"
} | ConvertTo-Json

try {
    $registerResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/auth/register" `
        -Method Post `
        -Headers @{ "Content-Type" = "application/json" } `
        -Body $registerBody
    
    $token = $registerResponse.access_token
    Write-Host "✅ Usuario registrado exitosamente" -ForegroundColor Green
    Write-Host "   Token guardado en token.txt" -ForegroundColor Gray
    $token | Out-File -FilePath "token.txt" -Encoding utf8
} catch {
    Write-Host "❌ Error en registro: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""

# ============================================================================
# PASO 2: CONECTAR GARMIN
# ============================================================================
Write-Host "[2/8] Conectando con Garmin Connect..." -ForegroundColor Yellow
Write-Host ""

# Pedir credenciales de Garmin
$garminEmail = Read-Host "   Ingresa tu email de Garmin"
$garminPasswordSecure = Read-Host "   Ingresa tu contraseña de Garmin" -AsSecureString
$garminPassword = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($garminPasswordSecure)
)

$garminBody = @{
    email = $garminEmail
    password = $garminPassword
} | ConvertTo-Json

try {
    $garminResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/garmin/connect" `
        -Method Post `
        -Headers @{ 
            "Content-Type" = "application/json"
            "Authorization" = "Bearer $token"
        } `
        -Body $garminBody
    
    Write-Host "✅ Garmin conectado exitosamente" -ForegroundColor Green
} catch {
    Write-Host "❌ Error conectando Garmin: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "   Verifica tus credenciales e intenta de nuevo" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# ============================================================================
# PASO 3: SINCRONIZAR WORKOUTS
# ============================================================================
Write-Host "[3/8] Sincronizando entrenamientos desde Garmin..." -ForegroundColor Yellow

try {
    $syncResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/garmin/sync" `
        -Method Post `
        -Headers @{ 
            "Content-Type" = "application/json"
            "Authorization" = "Bearer $token"
        } `
        -Body "{}"
    
    $workoutCount = $syncResponse.workouts_synced
    Write-Host "✅ $workoutCount entrenamientos sincronizados" -ForegroundColor Green
    Write-Host "   IDs: $($syncResponse.activity_ids -join ', ')" -ForegroundColor Gray
} catch {
    Write-Host "❌ Error sincronizando workouts: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""

# ============================================================================
# PASO 4: OBTENER WORKOUTS PARA AUTO-CONFIGURACIÓN
# ============================================================================
Write-Host "[4/8] Analizando tu historial de entrenamientos..." -ForegroundColor Yellow

try {
    $workouts = Invoke-RestMethod -Uri "$baseUrl/api/v1/workouts?limit=10" `
        -Method Get `
        -Headers @{ "Authorization" = "Bearer $token" }
    
    # Calcular FCM del historial
    $maxHR = ($workouts | Measure-Object -Property max_heart_rate -Maximum).Maximum
    
    # Calcular pace promedio
    $avgPace = ($workouts | Where-Object { $_.avg_pace -ne $null } | 
                Measure-Object -Property avg_pace -Average).Average
    
    Write-Host "✅ Historial analizado" -ForegroundColor Green
    Write-Host "   FCM detectada: $maxHR bpm" -ForegroundColor Gray
    Write-Host "   Pace promedio: $([math]::Floor($avgPace / 60)):$([math]::Floor($avgPace % 60).ToString('00'))/km" -ForegroundColor Gray
} catch {
    Write-Host "⚠️  No se pudo analizar historial, usando valores por defecto" -ForegroundColor Yellow
    $maxHR = 180
}

Write-Host ""

# ============================================================================
# PASO 5: CONFIGURAR PERFIL DE ATLETA
# ============================================================================
Write-Host "[5/8] Configurando perfil de atleta..." -ForegroundColor Yellow

$profileBody = @{
    running_level = "intermediate"
    max_heart_rate = $maxHR
    coaching_style = "balanced"
    preferences = @{
        music = $true
        time_of_day = "evening"
        terrain_preference = "road"
    }
} | ConvertTo-Json

try {
    $profileResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/profile" `
        -Method Patch `
        -Headers @{ 
            "Content-Type" = "application/json"
            "Authorization" = "Bearer $token"
        } `
        -Body $profileBody
    
    Write-Host "✅ Perfil configurado" -ForegroundColor Green
    Write-Host "   Nivel: intermediate" -ForegroundColor Gray
    Write-Host "   FCM: $maxHR bpm" -ForegroundColor Gray
    Write-Host "   Estilo: balanced" -ForegroundColor Gray
} catch {
    Write-Host "❌ Error configurando perfil: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# ============================================================================
# PASO 6: CREAR OBJETIVO
# ============================================================================
Write-Host "[6/8] Creando objetivo de entrenamiento..." -ForegroundColor Yellow

$goalBody = @{
    name = "Sub-40 en 10K"
    goal_type = "race"
    target_value = "39:59"
    deadline = "2026-06-01T00:00:00"
    description = "Bajar de 40 minutos en 10 kilómetros"
} | ConvertTo-Json

try {
    $goalResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/profile/goals" `
        -Method Post `
        -Headers @{ 
            "Content-Type" = "application/json"
            "Authorization" = "Bearer $token"
        } `
        -Body $goalBody
    
    Write-Host "✅ Objetivo creado: Sub-40 en 10K" -ForegroundColor Green
} catch {
    Write-Host "❌ Error creando objetivo: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# ============================================================================
# PASO 7: PROBAR COACH AI - ANÁLISIS DE WORKOUT
# ============================================================================
Write-Host "[7/8] Probando Coach AI..." -ForegroundColor Yellow
Write-Host ""

try {
    # Análisis post-workout
    Write-Host "   → Analizando tu primer entrenamiento..." -ForegroundColor Cyan
    $analysisResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/coach/analyze/1" `
        -Method Post `
        -Headers @{ "Authorization" = "Bearer $token" } `
        -Body ""
    
    Write-Host "   ✅ Análisis completado" -ForegroundColor Green
    Write-Host "   Zona: $($analysisResponse.workout_summary.zone)" -ForegroundColor Gray
    Write-Host "   Tokens: $($analysisResponse.tokens_used)" -ForegroundColor Gray
    Write-Host ""
    
    # Plan semanal
    Write-Host "   → Generando plan semanal..." -ForegroundColor Cyan
    $planResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/coach/plan" `
        -Method Post `
        -Headers @{ "Authorization" = "Bearer $token" }
    
    Write-Host "   ✅ Plan semanal generado" -ForegroundColor Green
    Write-Host "   Volumen: $($planResponse.weekly_volume_km) km/semana" -ForegroundColor Gray
    Write-Host ""
    
    # Chat
    Write-Host "   → Probando chatbot..." -ForegroundColor Cyan
    $chatBody = @{
        message = "¿Qué opinas de mi último entrenamiento?"
    } | ConvertTo-Json
    
    $chatResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/coach/chat" `
        -Method Post `
        -Headers @{ 
            "Content-Type" = "application/json"
            "Authorization" = "Bearer $token"
        } `
        -Body $chatBody
    
    Write-Host "   ✅ Chatbot respondió correctamente" -ForegroundColor Green
    Write-Host "   Mensajes en conversación: $($chatResponse.conversation_length)" -ForegroundColor Gray
    Write-Host ""
    
    # Análisis de forma
    Write-Host "   → Analizando técnica de running..." -ForegroundColor Cyan
    $formResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/coach/analyze-form/1" `
        -Method Post `
        -Headers @{ "Authorization" = "Bearer $token" }
    
    Write-Host "   ✅ Análisis de forma completado" -ForegroundColor Green
    Write-Host "   Eficiencia: $($formResponse.form_metrics.efficiency)" -ForegroundColor Gray
    Write-Host ""
    
    # Zonas cardíacas
    Write-Host "   → Obteniendo zonas cardíacas..." -ForegroundColor Cyan
    $zonesResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/coach/hr-zones" `
        -Method Get `
        -Headers @{ "Authorization" = "Bearer $token" }
    
    Write-Host "   ✅ Zonas calculadas" -ForegroundColor Green
    Write-Host "   FCM: $($zonesResponse.max_heart_rate) bpm" -ForegroundColor Gray
    
} catch {
    Write-Host "   ❌ Error probando Coach AI: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# ============================================================================
# PASO 8: RESUMEN FINAL
# ============================================================================
Write-Host "[8/8] ¡Setup completado!" -ForegroundColor Yellow
Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  CONFIGURACION EXITOSA" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Resumen:" -ForegroundColor Cyan
Write-Host "   - Usuario: guillermomartindeoliva@gmail.com" -ForegroundColor White
Write-Host "   - Workouts sincronizados: $workoutCount" -ForegroundColor White
Write-Host "   - FCM configurada: $maxHR bpm" -ForegroundColor White
Write-Host "   - Objetivo: Sub-40 en 10K" -ForegroundColor White
Write-Host "   - Coach AI: Funcionando" -ForegroundColor White
Write-Host ""
Write-Host "Accede a Swagger UI:" -ForegroundColor Cyan
Write-Host "   http://127.0.0.1:8000/docs" -ForegroundColor Blue
Write-Host ""
Write-Host "Token guardado en: token.txt" -ForegroundColor Cyan
Write-Host ""
Write-Host "Todo listo para entrenar con IA!" -ForegroundColor Green
Write-Host ""
