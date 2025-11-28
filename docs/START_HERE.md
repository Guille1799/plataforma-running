# 🚀 ESTADO DEL SISTEMA - BLOQUE 2 LISTO

## 📊 Estado Actual

```
┌─────────────────────────────────────────────────────┐
│  🔵 BACKEND      ✅ Running on :8000                │
│  🔵 FRONTEND     ✅ Running on :3000                │
│  🔵 DATABASE     ✅ 30 metrics, 60 workouts, 1 user│
│  🔵 COMPONENTS   ✅ Badge, Progress installed      │
│  🔵 DEPENDENCIES ✅ @radix-ui/react-progress added │
└─────────────────────────────────────────────────────┘
```

---

## 🎯 INSTRUCCIONES PARA BLOQUE 2

### ⚡ Quick Start (2 minutos)

**1. Abre navegador**
```
http://localhost:3000
```

**2. Ingresa**
```
Email:    guillermomartindeoliva@gmail.com
Password: password123
```

**3. Verifica**
- ✅ Dashboard carga
- ✅ ReadinessBadge visible (número 0-100)
- ✅ Workout stats visible (60 entrenamientos)
- ✅ Daily Check-In widget visible

**4. Click en ReadinessBadge**
- ✅ Navega a /health
- ✅ Muestra gráfico y métricas

**5. Reporta resultados**
```
Usa el template en BLOQUE2_CHECKLIST.md
```

---

## 📁 Archivos Importantes para Ti

1. **`BLOQUE2_CHECKLIST.md`** ← ABRE ESTO
   - Instrucciones paso a paso
   - Qué deberías ver en cada pantalla
   - Errores comunes y soluciones
   - Template para reportar resultados

2. **`VERIFICACION_PRE_TESTING.md`** 
   - Estado actual del sistema
   - Tests rápidos (pre-check)
   - Plan completo de testing (Bloques 2-7)

3. **Terminals en uso**
   - Terminal 1: Backend en `:8000`
   - Terminal 2: Frontend en `:3000`
   - Déjalas corriendo durante todo el testing

---

## 🔐 Credenciales

**Login**:
```
Email:    guillermomartindeoliva@gmail.com
Password: password123
```

**¿Olvidaste la contraseña?**
```powershell
cd C:\Users\guill\Desktop\plataforma-running\backend
python reset_password.py
```

---

## 🛠️ Si necesitas reiniciar

### Frontend (Turbopack - rápido)
```powershell
# En Terminal 2
# Ctrl+C para detener
# Luego: npm run dev
```

### Backend (FastAPI)
```powershell
# En Terminal 1
# Ctrl+C para detener
# Luego: uvicorn app.main:app --reload
```

### Reset completo de BD (si todo se rompe)
```powershell
cd backend
Remove-Item runcoach.db
# Backend recrea automáticamente
# Luego: python seed_health_data.py
```

---

## 📞 Status Commands

**Ver proceso Next.js:**
```powershell
Get-Process node | Where-Object {$_.Path -like "*node*"}
```

**Ver puerto 3000 en uso:**
```powershell
netstat -ano | findstr :3000
```

**Ver puerto 8000 en uso:**
```powershell
netstat -ano | findstr :8000
```

---

## ✅ Pre-Check Rápido

```powershell
# Backend OK?
Invoke-WebRequest -Uri http://127.0.0.1:8000/health/today -Headers @{"Authorization"="Bearer x"} -ErrorAction SilentlyContinue
# Resultado: 401 = ✅ OK (requiere auth)

# Frontend OK?
Invoke-WebRequest -Uri http://localhost:3000 -ErrorAction SilentlyContinue
# Resultado: 200 = ✅ OK

# DB OK?
Test-Path "C:\Users\guill\Desktop\plataforma-running\backend\runcoach.db"
# Resultado: True = ✅ OK
```

---

## 🎓 Qué Vamos a Probar

### Bloque 2: Hoy ✨
- ✅ Login flow
- ✅ Dashboard renderiza
- ✅ ReadinessBadge muestra score
- ✅ Workouts cargan desde DB
- ✅ Navigation a /health

### Bloque 3: Después
- Daily Check-In submission
- Score updates en tiempo real
- Histórico actualiza

### Bloque 4+: Después
- Health charts (7 gráficos)
- Device connections (Garmin, Google Fit)
- Training plans

---

## 📝 Próximo Paso

**→ Abre `BLOQUE2_CHECKLIST.md`**

Sigue todos los pasos y reporta los resultados en el template.

¡Listo para empezar! 🎉
