# 🧪 Test Plan - Opción C (Onboarding + Dashboard Fix)

## Prerequisitos
- ✅ Backend corriendo en http://127.0.0.1:8000
- ✅ Frontend corriendo en http://localhost:3000
- ✅ Base de datos migrada (8 columnas nuevas en users table)

## Test 1: Fix del Dashboard (Token Loading)

### Pasos:
1. Abre http://localhost:3000
2. Login con:
   - Email: `guillermomartindeoliva@gmail.com`
   - Password: `password123`
3. Deberías ser redirigido a `/onboarding` (porque onboarding_completed = false)

### Verificación:
- [ ] Página de login funciona
- [ ] Token se guarda en localStorage
- [ ] Redireccion automática a onboarding

---

## Test 2: Flujo de Onboarding (5 Pasos)

### Step 1: Device Selection
1. En `/onboarding`, ves 5 opciones de dispositivos:
   - Garmin ⌚
   - Xiaomi / Amazfit 📱
   - Apple Health ❤️
   - Strava ⚡
   - Manual Entry 🧠

2. Haz click en **Garmin**

### Verificación:
- [ ] Opción Garmin se resalta en azul
- [ ] Progress bar sube a ~20%
- [ ] Puedes ir back (botón back aparece después)

### Step 2: Use Case Selection
1. Ves 4 opciones:
   - Fitness Tracker
   - Training Coach
   - Race Prep
   - General Health

2. Selecciona **Training Coach**

### Verificación:
- [ ] Opción se resalta
- [ ] Progress bar sube a ~40%
- [ ] Botón back disponible

### Step 3: Coach Style
1. Ves 4 estilos:
   - 🏃 Motivator
   - 📊 Technical
   - ⚖️ Balanced
   - 🎯 Custom

2. Selecciona **Balanced**

### Verificación:
- [ ] Opción se resalta
- [ ] Progress bar sube a ~60%

### Step 4: Language & Notifications
1. Ves grid de idiomas (Español, English, Français, Deutsch)
2. Ves toggle para "Enable notifications"

3. Selecciona **Español** (ya está seleccionado por defecto)
4. Deja **Enable notifications ON** (por defecto)

### Verificación:
- [ ] Idioma seleccionado: Español
- [ ] Notifications toggle: ON
- [ ] Progress bar sube a ~80%

### Step 5: Confirmation
1. Ves resumen de settings:
   - Device: garmin
   - Goal: training_coach
   - Coach Style: balanced
   - Language: es

2. Haz click en **"Start Training! 🚀"**

### Verificación:
- [ ] Botón muestra "Setting up..." mientras se carga
- [ ] Redirección a `/dashboard` después de 2-3 segundos
- [ ] No hay errores en consola

---

## Test 3: Dashboard con Datos de Salud

### En `/dashboard`:
1. Deberías ver:
   - Welcome message con tu email
   - **Readiness Badge** con score (ej: 72/100)
   - Stats cards: Entrenamientos, Distancia, Pace
   - Métricas visuales (colores según rendimiento)

### Verificación - Readiness Badge:
- [ ] Badge visible (no dice "Sin datos de salud")
- [ ] Muestra score (72 es el valor para hoy)
- [ ] Muestra confianza (high/medium/low)
- [ ] Muestra trend (↑/→/↓)
- [ ] Es clickeable (lleva a /health)

### Verificación - Stats Cards:
- [ ] "Entrenamientos esta semana" muestra número > 0
- [ ] "Distancia Total este mes" muestra número > 0 km
- [ ] "Pace Promedio" muestra valor en formato min:sec/km

---

## Test 4: Verificación en Backend

### Endpoint 1: Check Onboarding Status
```
curl -X GET http://127.0.0.1:8000/api/v1/onboarding/status \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Expected response:
```json
{
  "id": 1,
  "onboarding_completed": true,
  "primary_device": "garmin",
  "use_case": "training_coach",
  "coach_style_preference": "balanced",
  "language": "es"
}
```

### Endpoint 2: Health Data
```
curl -X GET http://127.0.0.1:8000/api/v1/health/today \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Expected: JSON con health metrics para hoy

---

## Test 5: Logout y Login Again

1. En dashboard, busca logout button (usuально en navbar/profile)
2. Click logout
3. Deberías volver a `/login`
4. Login de nuevo con mismas credenciales
5. Deberías ir directamente a `/dashboard` (onboarding ya completado)

### Verificación:
- [ ] Token se borra de localStorage al logout
- [ ] Login nuevamente funciona
- [ ] No pide onboarding otra vez (porque ya está completado)
- [ ] Dashboard carga inmediatamente

---

## 🐛 Troubleshooting

### Si ves "Sin datos de salud" en badge:
1. Abre DevTools (F12)
2. Console tab - ves algún error?
3. Network tab - GET /api/v1/health/readiness retorna 200?
4. Si no retorna 200:
   - Revisa token (localStorage > auth_token)
   - Revisa backend logs

### Si onboarding no guarda datos:
1. Check Network tab - POST /api/v1/onboarding/complete qué status?
2. Si 400/500 - qué dice el error?
3. Backend debe retornar 200 con `{success: true}`

### Si dashboard no carga después onboarding:
1. Check Console - errores de JavaScript?
2. Check Network - hay requests fallando?
3. Token todavía existe en localStorage?

---

## 📝 Expected Results Summary

| Component | Expected Behavior |
|-----------|------------------|
| Login Page | Funciona, guarda token |
| Onboarding Page | 5 pasos visuales, progreso actualiza |
| Dashboard | Muestra metrics reales, Readiness badge con datos |
| Token Persistence | Surviva page refresh, page reload en dashboard |
| Routing | Login→Onboarding→Dashboard flujo correcto |
| Health Metrics | API retorna 30+ métricas, badge muestra score |

---

## ✅ Checklist Final

- [ ] Login funciona
- [ ] Redireccion a onboarding funciona
- [ ] Onboarding 5 pasos completos
- [ ] Confirmacion guarda en backend
- [ ] Dashboard carga con datos reales
- [ ] Readiness badge visible y funcional
- [ ] Stats cards con valores correctos
- [ ] Logout funciona
- [ ] Re-login va directo a dashboard
- [ ] Sin errores en consola o network

---

## 🎯 Si Todo Pasa:
¡Felicidades! El sistema está listo para:
1. Pruebas con múltiples usuarios
2. Personalizacion del coach según device/use_case
3. Implementación de adaptive dashboard layouts
4. Integración multi-device

