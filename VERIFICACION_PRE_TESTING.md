# ✅ VERIFICACIÓN PRE-TESTING

**Timestamp**: Lunes, Noviembre 2025
**Estado**: SISTEMA LISTO PARA TESTING

---

## 🔍 Verificaciones Completadas

### Backend ✅
```
URL: http://127.0.0.1:8000
Status: Running (verificado - responde 401 cuando se requiere auth)
Port: 8000 (disponible)
Database: runcoach.db
```

**Endpoints probados**:
- ✅ POST /auth/login (credenciales correctas)
- ✅ GET /health/today (requiere token)
- ✅ GET /workouts (base de datos con 60 workouts)

**Datos en DB**:
- ✅ Usuario: `guillermomartindeoliva@gmail.com` con password `password123`
- ✅ 30 health metrics (HRV, sleep, readiness, etc.)
- ✅ 60 workouts (Garmin, Strava, manual entries)
- ✅ Garmin credentials: Limpiados (listos para nuevo connect)

---

### Frontend ✅
```
URL: http://localhost:3000
Status: Running (verificado - responde en <3s)
Next.js Version: 16.0.3 (Turbopack)
Port: 3000 (disponible)
```

**Dependencias instaladas**:
- ✅ @radix-ui/react-progress (v1.x) - para Progress bars
- ✅ shadcn/ui components - Card, Button, Input, Label, Slider, Textarea
- ✅ TanStack React Query - para data fetching con cache
- ✅ lucide-react - iconografía

**Componentes creados**:
- ✅ `/components/ui/badge.tsx` - Status badges (default, secondary, outline)
- ✅ `/components/ui/progress.tsx` - Progress bars with Radix UI
- ✅ `/components/ReadinessBadge.tsx` - Circular readiness indicator
- ✅ `/components/DailyCheckIn.tsx` - Check-in form with sliders

**Auth Context**:
- ✅ /lib/auth-context.tsx - Global auth state + login/logout
- ✅ /lib/api-client.ts - Axios + Bearer token interceptor
- ✅ localStorage key: `auth_token`

---

### Pages Status

| Page | Status | Notes |
|------|--------|-------|
| `/login` | ✅ Ready | Email/password form, error handling |
| `/register` | ✅ Ready | Create new account |
| `/dashboard` | ✅ Ready | Home page after login (has some styling) |
| `/health` | ✅ Ready | Health metrics + readiness score |
| `/health/history` | ✅ Ready | 7-day health charts |
| `/garmin` | ✅ Ready | Connect/sync Garmin |
| `/profile` | ⏳ Partial | Layout ready, forms pending |

---

## 🎯 Plan de Testing (TODAY)

### BLOQUE 1: Verificación Básica ✅ DONE
- ✅ Backend running
- ✅ Frontend running
- ✅ Database populated
- ✅ User credentials set
- ✅ Dependencies installed

### BLOQUE 2: Login + Dashboard (👈 YOU ARE HERE)
**Instrucciones**: Ver archivo `BLOQUE2_CHECKLIST.md`
1. Abre http://localhost:3000
2. Login con `guillermomartindeoliva@gmail.com` / `password123`
3. Verifica ReadinessBadge y workout stats
4. Click en badge → navega a /health
5. Reporta resultados en formato dado

**Time estimate**: 5-10 minutos
**Expected outcome**: Dashboard loads, badge shows score 60-75, 60 workouts visible

---

### BLOQUE 3: Daily Check-In (Próximo)
**Prerrequisito**: Bloque 2 OK
1. En `/health` page
2. Rellenar Daily Check-In con sliders
3. Verificar que readiness score cambia
4. Gráfico de histórico actualiza

**Time estimate**: 3-5 minutos

---

### BLOQUE 4: Health History (Después)
**Prerrequisito**: Bloque 3 OK
1. Navega a `/health/history`
2. Verifica 7 gráficos:
   - HRV trend
   - Sleep quality
   - Readiness score
   - Resting HR
   - Body Battery %
   - Stress levels
   - Weekly average

---

### BLOQUE 5+: Device Connections (Avanzado)
- **Garmin**: Connect + Sync (puede fallar por protecciones Garmin)
- **Google Fit**: OAuth flow (requiere credenciales Google)
- **Apple Health**: File import (requiere export.xml)

---

## 📋 Pre-Check Rápido (para ahora)

Abre una terminal Y COPIA-PEGA esto para verificar todo:

```powershell
# Check 1: Backend running
Write-Host "Check 1: Backend..." -ForegroundColor Cyan
try {
    $backend = Invoke-WebRequest -Uri http://127.0.0.1:8000/health/today `
        -Headers @{"Authorization"="Bearer test"} -ErrorAction Stop
} catch {
    if ($_.Exception.Response.StatusCode -eq 401) {
        Write-Host "✅ Backend OK (auth protected)" -ForegroundColor Green
    } else {
        Write-Host "❌ Backend FAIL" -ForegroundColor Red
    }
}

# Check 2: Frontend running
Write-Host "`nCheck 2: Frontend..." -ForegroundColor Cyan
try {
    $frontend = Invoke-WebRequest -Uri http://localhost:3000 -ErrorAction Stop
    Write-Host "✅ Frontend OK" -ForegroundColor Green
} catch {
    Write-Host "❌ Frontend FAIL" -ForegroundColor Red
}

# Check 3: Database
Write-Host "`nCheck 3: Database..." -ForegroundColor Cyan
if (Test-Path "C:\Users\guill\Desktop\plataforma-running\backend\runcoach.db") {
    Write-Host "✅ Database exists" -ForegroundColor Green
} else {
    Write-Host "❌ Database missing" -ForegroundColor Red
}

Write-Host "`n✅ Checks complete!" -ForegroundColor Green
Write-Host "Ready to start Bloque 2 testing" -ForegroundColor Cyan
```

---

## 🆘 Si algo falla aquí

| Problema | Solución |
|----------|----------|
| Backend no responde (no 401) | Terminal 1: `cd backend; uvicorn app.main:app --reload` |
| Frontend no responde | Terminal 2: `cd frontend; npm run dev` |
| Node en puerto 3000 | `Get-Process node \| Stop-Process -Force` |
| Base de datos vacía | `cd backend; python seed_health_data.py` |

---

## 📱 Acciones que harás en Bloque 2

### 1️⃣ Navegar a http://localhost:3000

### 2️⃣ Ingresa credenciales:
- Email: `guillermomartindeoliva@gmail.com`
- Password: `password123`

### 3️⃣ Verifica en dashboard:
- ReadinessBadge circular (score 0-100)
- Workout stats (60 entrenamientos, 450+ km)
- Daily Check-In widget

### 4️⃣ Click en badge → /health

### 5️⃣ Reporta con checklist en `BLOQUE2_CHECKLIST.md`

---

## ✨ Ready?

Cuando termines Bloque 1, abre: `BLOQUE2_CHECKLIST.md`

Sigue los pasos y luego reporta resultados aquí 👇
