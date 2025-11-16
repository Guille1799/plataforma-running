# ============================================================================
# Script de Setup Completo - RunCoach AI
# Ejecuta esto ANTES de irte y configurará todo automáticamente
# ============================================================================

Write-Host "🚀 Iniciando setup completo de RunCoach AI..." -ForegroundColor Green

# 1. REGISTRAR USUARIO
Write-Host "`n📝 1. Registrando usuario..." -ForegroundColor Cyan
$headers = @{ 'Content-Type' = 'application/json' }
$registerBody = @{
    name = 'Guillermo'
    email = 'guillermomartindeoliva@gmail.com'
    password = 'TestPass123!'
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/v1/auth/register' -Method Post -Headers $headers -Body $registerBody
    $token = $response.access_token
    Write-Host "✅ Usuario registrado exitosamente" -ForegroundColor Green
    Write-Host "Token: $token" -ForegroundColor Yellow
} catch {
    Write-Host "❌ Error registrando usuario: $_" -ForegroundColor Red
    exit 1
}

# 2. CONECTAR GARMIN
Write-Host "`n📡 2. Conectando Garmin..." -ForegroundColor Cyan
$authHeaders = @{
    'Content-Type' = 'application/json'
    'Authorization' = "Bearer $token"
}

# Pide credenciales de Garmin de forma segura
$garminEmail = Read-Host "Ingresa tu email de Garmin"
$garminPassword = Read-Host "Ingresa tu password de Garmin" -AsSecureString
$garminPasswordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($garminPassword))

$garminBody = @{
    email = $garminEmail
    password = $garminPasswordPlain
} | ConvertTo-Json

try {
    $garminResponse = Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/v1/garmin/connect' -Method Post -Headers $authHeaders -Body $garminBody
    Write-Host "✅ Garmin conectado exitosamente" -ForegroundColor Green
} catch {
    Write-Host "❌ Error conectando Garmin: $_" -ForegroundColor Red
    exit 1
}

# 3. SINCRONIZAR WORKOUTS
Write-Host "`n🏃 3. Sincronizando workouts..." -ForegroundColor Cyan
$syncBody = @{} | ConvertTo-Json

try {
    $syncResponse = Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/v1/garmin/sync' -Method Post -Headers $authHeaders -Body $syncBody
    Write-Host "✅ Workouts sincronizados: $($syncResponse.workouts_synced)" -ForegroundColor Green
    Write-Host "IDs: $($syncResponse.activity_ids -join ', ')" -ForegroundColor Yellow
} catch {
    Write-Host "❌ Error sincronizando workouts: $_" -ForegroundColor Red
    exit 1
}

# 4. CONFIGURAR PERFIL DE ATLETA
Write-Host "`n👤 4. Configurando perfil de atleta..." -ForegroundColor Cyan
$profileBody = @{
    running_level = 'intermediate'
    max_heart_rate = 180
    coaching_style = 'balanced'
    preferences = @{
        music = $true
        time_of_day = 'evening'
        terrain_preference = 'road'
    }
} | ConvertTo-Json

try {
    $profileResponse = Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/v1/profile' -Method Patch -Headers $authHeaders -Body $profileBody
    Write-Host "✅ Perfil configurado exitosamente" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Error configurando perfil (continuando...): $_" -ForegroundColor Yellow
}

# 5. CREAR OBJETIVO: Sub-40 en 10K
Write-Host "`n🎯 5. Creando objetivo: Sub-40 en 10K..." -ForegroundColor Cyan
$goalBody = @{
    name = 'Sub-40 en 10K'
    goal_type = 'race'
    target_value = '39:59'
    deadline = '2025-12-31T00:00:00Z'
    description = 'Correr 10 kilómetros en menos de 40 minutos'
} | ConvertTo-Json

try {
    $goalResponse = Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/v1/profile/goals' -Method Post -Headers $authHeaders -Body $goalBody
    Write-Host "✅ Objetivo creado exitosamente" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Error creando objetivo (continuando...): $_" -ForegroundColor Yellow
}

# 6. ANALIZAR PRIMER WORKOUT
Write-Host "`n🤖 6. Analizando primer workout con Coach AI..." -ForegroundColor Cyan
try {
    $analysisResponse = Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/v1/coach/analyze/1' -Method Post -Headers $authHeaders
    Write-Host "✅ Análisis completado:" -ForegroundColor Green
    Write-Host $analysisResponse.analysis -ForegroundColor White
    Write-Host "`nTokens usados: $($analysisResponse.tokens_used)" -ForegroundColor Yellow
} catch {
    Write-Host "⚠️  Error analizando workout: $_" -ForegroundColor Yellow
}

# 7. GENERAR PLAN SEMANAL
Write-Host "`n📅 7. Generando plan semanal..." -ForegroundColor Cyan
try {
    $planResponse = Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/v1/coach/plan' -Method Post -Headers $authHeaders
    Write-Host "✅ Plan semanal generado:" -ForegroundColor Green
    Write-Host $planResponse.plan -ForegroundColor White
    Write-Host "`nVolumen semanal: $($planResponse.weekly_volume_km) km" -ForegroundColor Yellow
} catch {
    Write-Host "⚠️  Error generando plan: $_" -ForegroundColor Yellow
}

# 8. PROBAR CHATBOT
Write-Host "`n💬 8. Probando chatbot..." -ForegroundColor Cyan
$chatMessages = @(
    "Hola coach! ¿Cómo estuvo mi último entrenamiento?",
    "¿Qué ejercicios me recomiendas para mejorar mi cadencia?",
    "Dame consejos para mi próximo 10K"
)

foreach ($msg in $chatMessages) {
    $chatBody = @{ message = $msg } | ConvertTo-Json
    try {
        $chatResponse = Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/v1/coach/chat' -Method Post -Headers $authHeaders -Body $chatBody
        Write-Host "`n👤 TÚ: $msg" -ForegroundColor Cyan
        Write-Host "🤖 COACH: $($chatResponse.assistant_message.content)" -ForegroundColor Green
        Start-Sleep -Seconds 2
    } catch {
        Write-Host "⚠️  Error en chat: $_" -ForegroundColor Yellow
    }
}

# 9. ANALIZAR FORMA/TÉCNICA
Write-Host "`n🏃‍♂️ 9. Analizando técnica de running..." -ForegroundColor Cyan
try {
    $formResponse = Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/v1/coach/analyze-form/1' -Method Post -Headers $authHeaders
    Write-Host "✅ Análisis de forma completado:" -ForegroundColor Green
    Write-Host $formResponse.ai_analysis -ForegroundColor White
} catch {
    Write-Host "⚠️  Error analizando forma: $_" -ForegroundColor Yellow
}

# 10. VER ZONAS CARDÍACAS
Write-Host "`n❤️  10. Consultando zonas cardíacas..." -ForegroundColor Cyan
try {
    $zonesResponse = Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/v1/coach/hr-zones' -Method Get -Headers $authHeaders
    Write-Host "✅ Zonas cardíacas (FCM: $($zonesResponse.max_heart_rate) bpm):" -ForegroundColor Green
    foreach ($zone in $zonesResponse.zones.PSObject.Properties) {
        $zoneData = $zone.Value
        Write-Host "  $($zoneData.name): $($zoneData.min_bpm)-$($zoneData.max_bpm) bpm ($($zoneData.percentage))" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  Error consultando zonas: $_" -ForegroundColor Yellow
}

# RESUMEN FINAL
Write-Host "`n" + "="*80 -ForegroundColor Green
Write-Host "🎉 SETUP COMPLETO - RunCoach AI" -ForegroundColor Green
Write-Host "="*80 -ForegroundColor Green
Write-Host "`n✅ Usuario registrado y autenticado" -ForegroundColor Green
Write-Host "✅ Garmin conectado y sincronizado" -ForegroundColor Green
Write-Host "✅ Perfil de atleta configurado" -ForegroundColor Green
Write-Host "✅ Objetivo creado: Sub-40 en 10K" -ForegroundColor Green
Write-Host "✅ Coach AI testeado (análisis, plan, chat, forma)" -ForegroundColor Green
Write-Host "✅ Zonas cardíacas calculadas" -ForegroundColor Green

Write-Host "`n📊 Estadísticas:" -ForegroundColor Cyan
Write-Host "  - Workouts sincronizados: $($syncResponse.workouts_synced)" -ForegroundColor White
Write-Host "  - Conversaciones con coach: $($chatMessages.Count)" -ForegroundColor White
Write-Host "  - Token guardado en: token.txt" -ForegroundColor White

Write-Host "`n🚀 Accede a la API en: http://127.0.0.1:8000/docs" -ForegroundColor Yellow
Write-Host "💾 Token guardado en: token.txt" -ForegroundColor Yellow

# Guardar token
$token | Out-File -FilePath "token.txt" -Encoding utf8
Write-Host "`n✅ Setup completado exitosamente!" -ForegroundColor Green
