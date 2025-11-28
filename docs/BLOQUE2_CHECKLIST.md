# 🏃 BLOQUE 2: Login + ReadinessBadge Verification

**Estado**: ✅ Backend + Frontend listos
**Credenciales**: 
- Email: `guillermomartindeoliva@gmail.com`
- Password: `password123`

---

## 📋 Checklist Detallado

### Paso 1: Acceder al Frontend
**URL**: http://localhost:3000

**Qué deberías ver**:
- ✅ Página de login con formulario
- ✅ 2 campos: Email y Password
- ✅ Botón "Ingresar"
- ✅ Link "Crear cuenta" si no tienes

**Si ves error 500 en `/health`**:
- Normal, lo arreglamos después
- Intenta ir directamente a http://localhost:3000/login

---

### Paso 2: Login
**Acción**: 
1. Ingresa: `guillermomartindeoliva@gmail.com`
2. Ingresa: `password123`
3. Click en "Ingresar"

**Qué pasará**:
- Frontend hace POST a `/auth/login`
- Backend valida credenciales
- Si OK → retorna `access_token`
- Frontend guarda en `localStorage` como `auth_token`
- Redirecciona a `/dashboard`

**Errores posibles**:
| Error | Causa | Solución |
|-------|-------|----------|
| "User not found" | Email no existe | Verifica ortografía |
| "Invalid password" | Contraseña incorrecta | La correcta es `password123` |
| "Network error" | Backend no responde | Verifica que `uvicorn` corre en terminal 1 |
| Redirección a `/login` | Token no se guardó | Abre DevTools → Application → localStorage → busca `auth_token` |

---

### Paso 3: Verificar Dashboard
**URL destino**: http://localhost:3000/dashboard

**Qué deberías ver**:

#### 3.1 ReadinessBadge (Arriba a la izquierda)
```
┌─────────────────┐
│  Readiness      │
│    ┌─────┐      │
│    │  72 │      │  ← Número entre 0-100
│    └─────┘      │
│   "Ready"       │  ← Label según score
└─────────────────┘
```

- Circular badge con score (0-100)
- Color: Verde si >70, Amarillo si 50-70, Rojo si <50
- Label debajo: "Excellent" / "Ready" / "Caution" / "Not Ready"
- Si haces click → va a `/health`

**¿No ves el badge?**
- Abre DevTools (F12)
- Ve a Console
- Busca errores
- Reporta exactamente qué dice

#### 3.2 Workout Stats (Debajo o al lado)
```
Entrenamientos: 60
Distancia: 450.5 km
Tiempo: 3,240 min
```

- Si ves estos números → la API está funcionando
- Si ves 0 o "loading..." → espera 2 segundos
- Si sigue sin cargar → reporta error en console

#### 3.3 Daily Check-In Widget
```
┌──────────────────────┐
│ Today's Check-In     │
│ ─────────────────── │
│ Energy: [=====>] 7  │
│ Soreness: [===>] 3  │
│ Mood: [========] 9  │
│ Motivation: [...] 5 │
│ Sleep: [  ] hours   │
│            [Submit] │
└──────────────────────┘
```

- Sliders para energía, molestias, ánimo, motivación
- Campo para horas de sueño
- Botón Submit

---

### Paso 4: Click en ReadinessBadge
**Acción**: Click en el circular badge

**Qué debería pasar**:
- Navega a http://localhost:3000/health
- Carga page completa de Health Dashboard

**Qué verías en `/health`** (si funciona):
- ReadinessBadge más grande
- Gráfico circular de descomposición:
  - 40% Body Battery
  - 30% Sleep Quality
  - 20% HRV Balance
  - 10% Rest Heart Rate
  - 10% Stress Recovery
- Tarjetas con métricas:
  - HRV: `XX ms`
  - Resting HR: `XX bpm`
  - Sleep: `X h`
  - Body Battery: `X%`
  - Stress: `X%`

---

### Paso 5: Reporta Resultados

**Copia esto en tu respuesta** y completa con lo que viste:

```
✅ BLOQUE 2 RESULTADOS:

1. Login: [OK / FALLO]
   - Si FALLO, error exacto: ________________

2. Dashboard visible: [SÍ / NO]

3. ReadinessBadge visible: [SÍ / NO]
   - Score mostrado: _____ (número 0-100)
   - Color: _____ (verde/amarillo/rojo)
   - Label: _____ (Excellent/Ready/Caution/Not Ready)

4. Workout stats visible: [SÍ / NO]
   - Entrenamientos: ____
   - Distancia: ____ km
   - Tiempo: ____ min

5. Daily Check-In widget visible: [SÍ / NO]

6. Click en badge → /health: [OK / FALLO]
   - Si FALLO, error: ________________

7. Errores en console (F12): [NINGUNO / Listar abajo]
   ________________________
   ________________________

8. Observaciones adicionales:
   ________________________
```

---

## 🔧 Si algo no funciona

### "Module not found" errors en console
```
→ Los componentes Progress/Badge se acaban de crear
→ Recarga la página (Ctrl+Shift+R o Cmd+Shift+R)
→ Si persiste, reinicia Next.js y espera 5 segundos
```

### ReadinessBadge no se ve (pero no hay error)
```
→ Busca en la page.tsx si está importado
→ Ve a DevTools → Elements → busca "readiness"
→ Si existe pero no se ve → CSS issue, reporta
```

### Workouts siempre en "loading"
```
→ Backend puede estar lento
→ Abre http://127.0.0.1:8000/docs
→ Ve a GET /workouts → Try it out → Execute
→ ¿Retorna JSON? → Sí → problema frontend
→ ¿Retorna error? → Backend issue
```

### "Cannot read property 'email' of undefined"
```
→ Auth context no se inicializó correctamente
→ Limpia localStorage: F12 → Application → clear all
→ Logout y vuelve a login
```

---

## 🎯 Próximos Pasos (Bloque 3)

Una vez que verifiques Bloque 2:
1. Rellenarás el Daily Check-In con datos reales
2. Verificarás que el score de readiness cambia
3. Comprobaremos los gráficos de histórico

Espera instrucciones para Bloque 3 una vez confirmes Bloque 2 ✅
