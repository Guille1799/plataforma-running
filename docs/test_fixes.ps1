#!/usr/bin/env pwsh

# 🚀 TESTING SCRIPT - Validar que los 3 bugs están solucionados

Write-Host "╔════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     VALIDATION: Training Plan Form Fixes - 3 Critical Bugs          ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Credentials
$email = "test@example.com"
$password = "password123"

Write-Host "📋 TEST CREDENTIALS:" -ForegroundColor Yellow
Write-Host "   Email: $email"
Write-Host "   Password: $password"
Write-Host ""

Write-Host "🎯 FIXES A VALIDAR:" -ForegroundColor Green
Write-Host ""
Write-Host "1️⃣  RACE SEARCH (Buscador mostraba solo Málaga)" -ForegroundColor Blue
Write-Host "   ✅ FIXED: Added cache-busting with timestamp + headers"
Write-Host "   📍 VERIFICATION:"
Write-Host "      - Go to Training Plans"
Write-Host "      - Search: 'marat'"
Write-Host "      - EXPECT: 30+ marathons (Barcelona, Madrid, Málaga, Valencia, etc.)"
Write-Host "      - DevTools → Network → check '_t' parameter changes each search"
Write-Host ""

Write-Host "2️⃣  PASO 6 DURATION (Opciones de duración no cargaban)" -ForegroundColor Blue
Write-Host "   ✅ FIXED: Moved useEffect to component top level (Rules of Hooks)"
Write-Host "   📍 VERIFICATION:"
Write-Host "      - Paso 1: Select 'No race, just train'"
Write-Host "      - Paso 2: Select goal + priority"
Write-Host "      - Paso 6: Should see duration options (4, 8, 12, 16 weeks)"
Write-Host "      - Console: Should show '📋 Loading duration options...'"
Write-Host ""

Write-Host "3️⃣  PASO 2 VALIDATION (Podías avanzar sin prioridad)" -ForegroundColor Blue
Write-Host "   ✅ FIXED: Updated isStepValid() to require BOTH goal AND priority"
Write-Host "   📍 VERIFICATION:"
Write-Host "      - Paso 2: Select only goal → Button should be GRAY"
Write-Host "      - Paso 2: Select only priority → Button should be GRAY"
Write-Host "      - Paso 2: Select BOTH → Button should be BLUE (enabled)"
Write-Host ""

Write-Host "════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "📝 STEP-BY-STEP TEST:" -ForegroundColor Yellow
Write-Host "════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

Write-Host "SCENARIO 1: With Race Target (Quick Test)" -ForegroundColor Magenta
Write-Host "1. Login with $email"
Write-Host "2. Go to 'Training Plans' tab"
Write-Host "3. Click 'New Training Plan'"
Write-Host "4. Paso 1: Search 'Marató' → Select 'Marató de Barcelona 2025-03-09'"
Write-Host "   ✅ Should auto-populate duration (e.g., 16 semanas)"
Write-Host "5. Paso 2: Click 'Siguiente' without selecting anything"
Write-Host "   ✅ Button should be GRAY (disabled)"
Write-Host "6. Select Marathon + Speed"
Write-Host "   ✅ Button turns BLUE (enabled)"
Write-Host "7. Follow through to Paso 6"
Write-Host "   ✅ Duration already set from race calculation"
Write-Host "8. Click 'Crear Plan' → Should succeed"
Write-Host ""

Write-Host "SCENARIO 2: Without Race Target (Full Validation)" -ForegroundColor Magenta
Write-Host "1. Start new training plan"
Write-Host "2. Paso 1: Select 'No, I want to train in general'"
Write-Host "3. Paso 2:"
Write-Host "   - Try clicking 'Siguiente' → GRAY (no selections)"
Write-Host "   - Select only 'Marathon' → GRAY (missing priority)"
Write-Host "   - Select only 'Speed' → GRAY (missing goal)"
Write-Host "   - Select BOTH → BLUE (enabled) ✅"
Write-Host "4. Continue through Paso 3, 4, 5"
Write-Host "5. Paso 6:"
Write-Host "   - Options should load (4, 8, 12, 16 semanas) ✅"
Write-Host "   - Button GRAY until you select duration ✅"
Write-Host "   - Select 12 semanas → Button BLUE"
Write-Host "6. Click 'Crear Plan' → Should succeed"
Write-Host ""

Write-Host "SCENARIO 3: Race Search Deep Dive" -ForegroundColor Magenta
Write-Host "1. Open DevTools (F12)"
Write-Host "2. Go to Network tab"
Write-Host "3. Filter: 'search?q='"
Write-Host "4. Search 'marat' in form"
Write-Host "   - First request: shows _t=1234567890"
Write-Host "5. Clear search, type 'marat' again"
Write-Host "   - Second request: _t=1234567999 (DIFFERENT timestamp)"
Write-Host "   - Response should show 30+ races ✅"
Write-Host ""

Write-Host "════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "🔍 BROWSER CONSOLE LOGS TO WATCH FOR:" -ForegroundColor Yellow
Write-Host "════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "🔍 Buscando carreras con query: marat"
Write-Host "📍 Respuesta del API: {success: true, count: 30, races: [...]}"
Write-Host "🏃 Carreras encontradas: 30"
Write-Host ""
Write-Host "📋 Loading duration options for goal: marathon"
Write-Host ""

Write-Host "════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "✅ SUCCESS INDICATORS:" -ForegroundColor Green
Write-Host "════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ Race search shows 30+ results for 'marat' (not just 1)"
Write-Host "✅ All 'Siguiente' buttons are disabled until valid selections"
Write-Host "✅ Paso 2 requires BOTH objective AND priority"
Write-Host "✅ Paso 6 duration options load automatically"
Write-Host "✅ Duration options appear when entering Paso 6 without race"
Write-Host "✅ 'Crear Plan' button only enabled when all fields valid"
Write-Host ""

Write-Host "════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "🛠 IF SOMETHING DOESN'T WORK:" -ForegroundColor Red
Write-Host "════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Hard refresh (Ctrl+Shift+R in browser)"
Write-Host "2. Clear browser cache"
Write-Host "3. Check backend is running: http://127.0.0.1:8000/docs"
Write-Host "4. Check frontend is running: http://localhost:3000"
Write-Host "5. Check browser console for errors (F12)"
Write-Host "6. Check Network tab for API responses"
Write-Host ""

Write-Host "🚀 START TESTING NOW!" -ForegroundColor Green
