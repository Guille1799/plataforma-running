# ✅ MANUAL VERIFICATION CHECKLIST - RUNCOACH DASHBOARD

**Objetivo**: Verificar visualmente en el dashboard que todos los features funcionan como esperado.

**Instrucciones**:
1. Lee cada sección paso a paso
2. Ejecuta las acciones indicadas
3. Marca ✅ o reporta ❌
4. Si hay problema, describe exactamente qué viste

---

## 🚀 SETUP INICIAL

### Paso 1: Arranca Backend y Frontend

**Terminal 1 - Backend:**
```powershell
cd c:\Users\guill\Desktop\plataforma-running\backend
.\venv\Scripts\uvicorn.exe app.main:app --port 8000
```
✅ Backend debe arrancar sin errores  
📍 URL: http://127.0.0.1:8000

**Terminal 2 - Frontend:**
```powershell
cd c:\Users\guill\Desktop\plataforma-running\frontend
npm run dev
```
✅ Frontend debe compilar sin errores  
📍 URL: http://localhost:3000

**Paso 1 Status**: [ ] OK / [ ] ERROR

---

## 📋 SECCIÓN 1: AUTENTICACIÓN

### Test 1.1: Register New User
**Paso a paso**:
1. Abre http://localhost:3000
2. Click en "Register" o "Sign Up"
3. Llena el formulario:
   - Email: `testuser-dashboard@example.com`
   - Password: `TestPass123!`
   - Name: `Test User`
4. Click "Create Account"

**Validar**:
- [ ] Formulario acepta datos
- [ ] No hay errores de validación
- [ ] Redirige a login o dashboard
- [ ] Mensaje de éxito aparece

**Si Falla**: [ ] Screenshot / [ ] Error message: ________________

---

### Test 1.2: Login with Credentials
**Paso a paso**:
1. En la pantalla de login (o si registraste nuevo user)
2. Email: `testuser-dashboard@example.com`
3. Password: `TestPass123!`
4. Click "Login"

**Validar**:
- [ ] Acepta credenciales
- [ ] Redirige a dashboard
- [ ] Token se guarda (revisar DevTools → Cookies/LocalStorage)
- [ ] No hay errores de red en Console

**Si Falla**: [ ] Screenshot / [ ] Error message: ________________

---

## 🏃 SECCIÓN 2: WORKOUTS

### Test 2.1: Ver Dashboard Home
**Paso a paso**:
1. Después de login, deberías ver el dashboard
2. Busca sección "Workouts" o "Recent Workouts"

**Validar**:
- [ ] Dashboard carga sin errores
- [ ] Hay una sección de workouts visible
- [ ] Muestra número de workouts (puede ser 0)
- [ ] Hay botón "New Workout" o similar

**Nota**: Si no ves UI completa, revisa:
- [ ] Console no tiene errores de React
- [ ] Network tab: requests al backend OK
- [ ] Backend respondiendo (http://127.0.0.1:8000/docs)

**Si Falla**: [ ] Screenshot / [ ] Error message: ________________

---

### Test 2.2: Create New Workout
**Paso a paso**:
1. Click botón "New Workout" o "Create Workout"
2. Llena el formulario:
   - Start Time: `Today, 14:00` (hace 1 hora)
   - Duration: `45 minutes`
   - Distance: `10 km`
   - Average Pace: `4:30 /km`
   - Heart Rate: `155 bpm`
   - Type: `Running`
3. Click "Save" o "Create"

**Validar**:
- [ ] Formulario valida campos requeridos
- [ ] Muestra error si campos inválidos
- [ ] Guarda correctamente
- [ ] Redirige a lista de workouts o muestra confirmación
- [ ] El nuevo workout aparece en la lista

**Si Falla**: [ ] Screenshot / [ ] Error message: ________________

---

### Test 2.3: Ver Detalle del Workout
**Paso a paso**:
1. Haz click en el workout que creaste (en la lista)
2. Debería abrir pantalla de detalle

**Validar**:
- [ ] Se abre la pantalla de detalle
- [ ] Muestra todos los datos (distancia, pace, HR, etc)
- [ ] Los valores son correctos (lo que ingresaste)
- [ ] Hay opción de editar o analizar
- [ ] No hay errores de layout/styling

**Detalle esperado**:
```
Workout: Running
Date: [fecha]
Duration: 45 minutes
Distance: 10 km
Pace: 4:30 /km
HR: 155 bpm
```

**Si Falla**: [ ] Screenshot / [ ] Error message: ________________

---

### Test 2.4: Ver Lista de Workouts
**Paso a paso**:
1. Navega a "Workouts" o "Training Log" en la sidebar
2. Debería ver lista de todos tus workouts

**Validar**:
- [ ] Lista carga correctamente
- [ ] Muestra múltiples workouts (al menos el que creaste)
- [ ] Cada item muestra: fecha, distancia, duración, HR
- [ ] Puedes hacer click en cada uno
- [ ] Hay paginación o scroll (si hay muchos)

**Si Falla**: [ ] Screenshot / [ ] Error message: ________________

---

## 🧠 SECCIÓN 3: AI FEATURES

### Test 3.1: Analizar Workout con AI
**Paso a paso**:
1. Abre un workout (Test 2.3)
2. Busca botón "Analyze" o "Get AI Analysis"
3. Click en él

**Validar**:
- [ ] Aparece loading spinner (puede tardar 2-5 segundos)
- [ ] Análisis carga correctamente
- [ ] Muestra insights sobre el workout:
  - Ritmo cardíaco (zones)
  - Pace analysis
  - Recomendaciones
  - Performance score
- [ ] No hay errores

**Ejemplo de análisis esperado**:
```
Análisis de Rendimiento:
- HR Zone: Z3-Z4 (aeróbico)
- Pace promedio: consistente
- Performance: 8.5/10
- Consejo: Aumentar volumen en Z2
```

**Si Falla**: [ ] Screenshot / [ ] Error message: ________________

---

### Test 3.2: Training Plan Generation
**Paso a paso**:
1. En dashboard, busca "Training Plans" o "Generate Plan"
2. Click en el botón
3. Debería aparecer formulario:
   - Goal: `5K Marathon Prep, etc`
   - Duration: `12 weeks`
   - Level: `Intermediate`
4. Click "Generate"

**Validar**:
- [ ] Formulario acepta inputs
- [ ] Loading spinner aparece (puede tardar 3-10 seg, AI)
- [ ] Plan se genera correctamente
- [ ] Muestra:
  - 12 semanas de entrenamientos
  - Distribución de workouts
  - Progresión de intensidad
- [ ] Plan es descargable o printable

**Si Falla**: [ ] Screenshot / [ ] Error message: ________________

---

### Test 3.3: Chat con Coach (si implementado)
**Paso a paso**:
1. Busca sección "Coach" o "Chat" en sidebar
2. Si existe, click en ella
3. Busca input de chat o botón "Start Chat"

**Validar**:
- [ ] Chat interface carga
- [ ] Puedes escribir un mensaje
- [ ] Mensaje se envía al backend
- [ ] Coach responde (puede tardar)
- [ ] Respuesta muestra en la UI

**Mensaje de prueba**: `"How can I improve my 5K time?"`

**Si NO existe**: [ ] SKIP (no implementado aún) / [ ] ERROR

**Si Falla**: [ ] Screenshot / [ ] Error message: ________________

---

## 👤 SECCIÓN 4: PERFIL & SETTINGS

### Test 4.1: Ver Perfil
**Paso a paso**:
1. Click en avatar/nombre en esquina superior derecha
2. Click "Profile" o "Settings"
3. Debería ver pantalla de perfil

**Validar**:
- [ ] Perfil carga correctamente
- [ ] Muestra datos:
  - Email correcto
  - Nombre correcto
  - Running level/preferences
- [ ] No hay errores

**Si Falla**: [ ] Screenshot / [ ] Error message: ________________

---

### Test 4.2: Editar Perfil
**Paso a paso**:
1. En perfil, busca botón "Edit" o campos editables
2. Cambia algún campo (ej: running level a "Advanced")
3. Click "Save"

**Validar**:
- [ ] Campos son editables
- [ ] Guarda cambios correctamente
- [ ] Muestra confirmación
- [ ] Al recargar, cambios persisten

**Si NO editable**: [ ] SKIP (lectura apenas)

**Si Falla**: [ ] Screenshot / [ ] Error message: ________________

---

## 📊 SECCIÓN 5: STATISTICS & INSIGHTS

### Test 5.1: Ver Estadísticas
**Paso a paso**:
1. Busca sección "Stats", "Analytics" o "Dashboard Home"
2. Debería mostrar resumen general

**Validar**:
- [ ] Muestra stats principales:
  - Total distance (todos los workouts)
  - Total time
  - Average pace
  - Workouts count
- [ ] Gráficos (si implementados):
  - Weekly view
  - Monthly view
  - Progress chart
- [ ] Stats son correctos (revisa con cálculos manuales)

**Cálculo manual**:
```
Si creaste 1 workout de 10km en 45 min:
- Total distance: 10 km ✅
- Total time: 45 min ✅
- Average pace: 4:30 /km ✅
```

**Si Falla**: [ ] Screenshot / [ ] Error message: ________________

---

## 🔐 SECCIÓN 6: SECURITY & ERROR HANDLING

### Test 6.1: Logout
**Paso a paso**:
1. Click avatar/nombre
2. Click "Logout"

**Validar**:
- [ ] Cierra sesión correctamente
- [ ] Redirige a login page
- [ ] Token se borra (revisar DevTools)
- [ ] No puedes acceder a dashboard sin login

**Si Falla**: [ ] Screenshot / [ ] Error message: ________________

---

### Test 6.2: Try Unauthorized Access
**Paso a paso**:
1. Cierra sesión (Test 6.1)
2. Intenta acceder directamente a: `http://localhost:3000/dashboard`

**Validar**:
- [ ] Redirige a login
- [ ] No ves datos privados

**Si Falla**: [ ] Screenshot / [ ] Error message: ________________

---

### Test 6.3: Invalid Input Handling
**Paso a paso**:
1. Login nuevamente
2. Intenta crear workout con datos inválidos:
   - Distance: `-10` (negativo)
   - Pace: `999999` (extremo)
3. Click "Save"

**Validar**:
- [ ] Formulario rechaza valores inválidos
- [ ] Muestra mensaje de error claro
- [ ] No permite guardar
- [ ] Error message es user-friendly

**Si Falla**: [ ] Screenshot / [ ] Error message: ________________

---

## 📱 SECCIÓN 7: RESPONSIVE DESIGN

### Test 7.1: Desktop View (1920x1080)
**Paso a paso**:
1. Abre dashboard en desktop completo
2. Navega por varias páginas

**Validar**:
- [ ] Sidebar visible y funcional
- [ ] Contenido bien distribuido
- [ ] Sin scroll horizontal innecesario
- [ ] Botones accesibles
- [ ] Texto legible

**Si Falla**: [ ] Screenshot / [ ] Issue: ________________

---

### Test 7.2: Tablet View (768px ancho)
**Paso a paso**:
1. DevTools: F12 → Toggle device toolbar
2. Select "iPad" o tablet de 768px
3. Navega por aplicación

**Validar**:
- [ ] Sidebar colapsable o responsive
- [ ] Contenido se adapta
- [ ] Buttons clickeables
- [ ] No hay texto cortado

**Si Falla**: [ ] Screenshot / [ ] Issue: ________________

---

### Test 7.3: Mobile View (375px ancho)
**Paso a paso**:
1. DevTools: Toggle device → "iPhone 12"
2. Navega por app

**Validar**:
- [ ] Sidebar oculto con hamburger menu
- [ ] Contenido full-width
- [ ] Botones grandes y clickeables
- [ ] Formularios adaptados

**Si Falla**: [ ] Screenshot / [ ] Issue: ________________

---

## 🎨 SECCIÓN 8: UI/UX QUALITY

### Test 8.1: Dark Theme
**Validar**:
- [ ] Tema dark aplicado correctamente
- [ ] Texto legible en fondo oscuro
- [ ] Contraste suficiente (WCAG AA)
- [ ] Iconos visibles
- [ ] Buttons con buen contraste

**Si Falla**: [ ] Screenshot / [ ] Issue: ________________

---

### Test 8.2: Loading States
**Paso a paso**:
1. Crea un workout (Test 2.2)
2. Mientras carga, revisa UI

**Validar**:
- [ ] Aparece skeleton loader o spinner
- [ ] UI no se "congela"
- [ ] User feedback claro

**Si Falla**: [ ] Screenshot / [ ] Issue: ________________

---

### Test 8.3: Error Messages
**Paso a paso**:
1. Intenta login con contraseña incorrecta
2. Revisa cómo se muestra el error

**Validar**:
- [ ] Error message aparece
- [ ] Es claro y específico
- [ ] No es técnico/confuso para usuario
- [ ] Color rojo o ícono de error visible

**Si Falla**: [ ] Screenshot / [ ] Issue: ________________

---

## 📋 RESUMEN FINAL

### Completa esta tabla:

| Sección | Tests | ✅ Passed | ❌ Failed | Notes |
|---------|-------|----------|----------|-------|
| 1. Autenticación | 2 | [ ] | [ ] | |
| 2. Workouts | 4 | [ ] | [ ] | |
| 3. AI Features | 3 | [ ] | [ ] | |
| 4. Perfil | 2 | [ ] | [ ] | |
| 5. Stats | 1 | [ ] | [ ] | |
| 6. Security | 3 | [ ] | [ ] | |
| 7. Responsive | 3 | [ ] | [ ] | |
| 8. UI/UX | 3 | [ ] | [ ] | |

---

## 🎯 RESULTADO FINAL

**Total Manual Tests**: 21  
**Passed**: __ / 21  
**Failed**: __ / 21  
**Success Rate**: __%

### Estado General:
- [ ] ✅ LISTO PARA PRODUCCIÓN
- [ ] ⚠️ NECESITA FIXES MENORES
- [ ] ❌ BLOQUEANTE - NO LISTO

---

## 📝 NOTAS GENERALES

```
Problemas encontrados:
1. 
2. 
3. 

Cosas que funcionan bien:
1. 
2. 
3. 

Sugerencias de mejora:
1. 
2. 
3. 
```

---

**¡Cuando termines, reporta los resultados paso a paso!**
