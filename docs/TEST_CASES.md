# 🧪 TEST CASES EXHAUSTIVOS - Plataforma de Running

## 📋 Estructura de Tests

```
CATEGORÍA
├─ TEST 1: Descripción
│  ├─ Precondiciones
│  ├─ Pasos
│  ├─ Resultado Esperado
│  └─ Notas
└─ TEST 2: ...
```

---

## 🔐 **AUTENTICACIÓN**

### TEST 1.1: Login con Credenciales Correctas
- **Precondiciones**: Usuario registrado (email: test@test.com, password: Test123!)
- **Pasos**: 
  1. Navega a /login
  2. Ingresa email y password correctos
  3. Haz clic en "Ingresar"
- **Resultado Esperado**: Redirige a /dashboard con sesión activa
- **Validar**: Cookie de sesión existe, JWT en localStorage

### TEST 1.2: Login con Email Incorrecto
- **Resultado Esperado**: Error "Email o contraseña incorrectos"

### TEST 1.3: Login con Password Incorrecto
- **Resultado Esperado**: Error "Email o contraseña incorrectos"

### TEST 1.4: Logout
- **Pasos**: 
  1. Login exitoso
  2. Click en "Perfil" → "Logout"
- **Resultado Esperado**: Redirige a /login, JWT removido del localStorage

### TEST 1.5: Sesión Expirada
- **Pasos**: 
  1. Login
  2. Esperar 1 hora o forzar JWT expirado
  3. Intentar navegar a /dashboard
- **Resultado Esperado**: Redirige a /login con mensaje "Sesión expirada"

---

## 👤 **PERFIL DE USUARIO**

### TEST 2.1: Completar Perfil Inicial
- **Precondiciones**: Usuario nuevo, en página de perfil
- **Pasos**:
  1. Ingresa altura: 180 cm
  2. Ingresa peso: 75 kg
  3. Ingresa FC máxima: 190 bpm
  4. Nivel: Intermedio
  5. Guardar
- **Resultado Esperado**: Perfil guardado, mensaje "Perfil actualizado"

### TEST 2.2: Validación de Altura/Peso
- **Pasos**: Intenta ingresar altura = -5 cm
- **Resultado Esperado**: Error "Altura debe ser entre 100 y 250 cm"

### TEST 2.3: Validación de FC Máxima
- **Pasos**: Intenta FC máxima = 50 bpm
- **Resultado Esperado**: Error "FC máxima debe ser entre 100 y 250 bpm"

### TEST 2.4: Guardar FTP (Potencia)
- **Pasos**: Ingresa FTP = 280 watts
- **Resultado Esperado**: FTP guardado, zonas de potencia calculadas

### TEST 2.5: Conectar Garmin
- **Pasos**: 
  1. Click "Conectar Garmin"
  2. Autentica con credenciales Garmin reales
- **Resultado Esperado**: Token guardado, opción muestra "Desconectar Garmin"

### TEST 2.6: Exportar Datos Personales
- **Pasos**: Click "Exportar mis datos"
- **Resultado Esperado**: Descarga JSON con todos los datos del usuario

### TEST 2.7: Solicitar Eliminación de Cuenta
- **Pasos**: 
  1. Click "Eliminar cuenta"
  2. Confirma "Estoy seguro"
- **Resultado Esperado**: Email de confirmación, 24 horas para cancelar

---

## 📅 **CREAR PLANES DE ENTRENAMIENTO**

### TEST 3.1: Crear Plan CON Carrera Objetivo (Happy Path)
- **Precondiciones**: Usuario con FC máxima definida, carrera "Media Maratón Dos Hermanas" existe
- **Pasos**:
  1. Click "Crear Plan"
  2. Paso 1: Selecciona "Sí, tengo carrera"
  3. Busca "Dos Hermanas" → selecciona "Media Maratón Dos Hermanas"
  4. Verifica: duración calculada automáticamente
  5. Paso 2: Ve que objetivo ya está establecido "Media Maratón" (no editable)
  6. Selecciona prioridad "Speed"
  7. Paso 3: Selecciona 5 días, sábado para tirada larga
  8. Paso 4: Sí a fuerza (gym), No a cross-training
  9. Paso 5: Método "heart_rate_based"
  10. Paso 6: Acepta duración sugerida, Recuperación "emphasis"
  11. Click "Crear Plan"
- **Resultado Esperado**: 
  - Plan creado exitosamente
  - Redirecciona a dashboard
  - Plan visible en sidebar
  - 14 semanas de entrenamientos generados
  - Cada semana tiene exactamente 5 entrenamientos (lunes-viernes + sábado)

### TEST 3.2: Crear Plan SIN Carrera (Happy Path)
- **Pasos**:
  1. Click "Crear Plan"
  2. Paso 1: Selecciona "No, entreno sin carrera"
  3. Paso 2: Selecciona objetivo "10K"
  4. Paso 3: Selecciona 4 días, lunes para tirada larga (cambio extraño pero válido)
  5. Paso 4: Sí a fuerza (home), sí a cross-training (yoga, natación)
  6. Paso 5: Método "pace_based"
  7. Paso 6: Ve opciones de duración:
     - Opción Rápida: 10 semanas
     - ⭐ Opción Recomendada: 12 semanas
     - Opción Extendida: 14 semanas
  8. Selecciona "12 semanas"
  9. Click "Crear Plan"
- **Resultado Esperado**:
  - Plan de 12 semanas creado
  - Objetivo "10K" establecido
  - 4 días de running + cross-training intercalado

### TEST 3.3: Validación: No puede crear plan sin datos obligatorios
- **Pasos**: Intenta pasar paso 2 sin seleccionar objetivo
- **Resultado Esperado**: Alert "Por favor selecciona un objetivo general"

### TEST 3.4: Carrera con Fecha en Pasado
- **Pasos**: Intenta seleccionar carrera con fecha 2025-01-01
- **Resultado Esperado**: Error "La fecha de carrera debe ser en el futuro"

### TEST 3.5: Carrera sin Tiempo Suficiente
- **Pasos**: Carrera en 2 días, objetivo "Marathon"
- **Resultado Esperado**: Error "Necesitas mínimo 16 semanas para una Maratón"

### TEST 3.6: Duración Automática Calculada Correctamente
- **Precondiciones**: Hoy es 2025-11-16, carrera es 2025-12-20 (34 días = 4.9 semanas)
- **Pasos**: Selecciona carrera con esa fecha
- **Resultado Esperado**: Duración sugerida = 4-5 semanas (máximo disponible)

---

## 📊 **DASHBOARD METRICS**

### TEST 4.1: Mostrar Zonas de FC
- **Precondiciones**: Usuario con max_heart_rate = 190, resting_hr = 60
- **Pasos**: Navega a dashboard
- **Resultado Esperado**:
  - Sección "Tus Zonas de Entrenamiento" visible
  - 5 zonas mostradas con rangos correctos usando Karvonen:
    - Z1: 65-79 bpm (50-60% HRR)
    - Z2: 79-93 bpm (60-70%)
    - Z3: 93-107 bpm (70-80%)
    - Z4: 107-121 bpm (80-90%)
    - Z5: 121-190 bpm (90-100%)
  - Colores correctos: azul, verde, amarillo, naranja, rojo

### TEST 4.2: Mostrar Zonas de Potencia
- **Precondiciones**: Usuario con ftp_watts = 280
- **Pasos**: Navega a dashboard
- **Resultado Esperado**:
  - 7 zonas de potencia visibles:
    - Z1: 0-154 watts
    - Z2: 154-210 watts
    - Z3: 210-252 watts
    - Z4: 252-294 watts
    - Z5: 294-336 watts
    - Z6: 336-420 watts
    - Z7: >420 watts

### TEST 4.3: Gráfico Workouts by Zone
- **Precondiciones**: Usuario con 15+ workouts últimas 4 semanas
- **Pasos**: Navega a dashboard
- **Resultado Esperado**:
  - Gráfico de pastel/barras mostrando distribución
  - Z1: ~5%, Z2: ~65%, Z3: ~20%, Z4: ~8%, Z5: ~2%
  - Hover muestra valores exactos

### TEST 4.4: Gráfico Progression Chart
- **Precondiciones**: Usuario con workouts en últimas 8 semanas
- **Pasos**: Navega a dashboard
- **Resultado Esperado**:
  - Gráfico de líneas mostrando volumen semanal
  - 8 puntos (una por semana)
  - Línea de media y máximo visible
  - Tendencia mostrada (↗️ o ↘️)

### TEST 4.5: Workout Insights
- **Pasos**: Navega a dashboard
- **Resultado Esperado**:
  - Mínimo 3 insights visibles:
    - "Tu volumen está en zona verde (30km/semana)" ✓
    - "Próxima carrera en 12 días" (si existe)
    - Otros basados en datos reales

---

## 🎯 **FORMULARIO DE PLAN (6 PASOS)**

### TEST 5.1: Navegación Entre Pasos
- **Pasos**: 
  1. Paso 1: Click "Siguiente"
  2. Verifica: Paso 2 visible
  3. Click "Atrás"
  4. Verifica: Paso 1 visible
- **Resultado Esperado**: Navegación fluida, datos persisten

### TEST 5.2: Responsive en Mobile (375px)
- **Pasos**: 
  1. Abre DevTools (F12)
  2. Set viewport a 375x667 (iPhone SE)
  3. Crear plan
- **Resultado Esperado**:
  - Botones apilados (100% width)
  - Texto legible (16px mínimo)
  - Selects y inputs con padding amplio
  - No hay scroll horizontal

### TEST 5.3: Responsive en Tablet (768px)
- **Resultado Esperado**:
  - Grid 2 columnas donde cabe
  - Botones side-by-side
  - Layout optimizado

### TEST 5.4: Dark Mode Consistency
- **Pasos**: 
  1. Abre formulario
  2. Verifica cada elemento
- **Resultado Esperado**:
  - Texto claro en fondo oscuro
  - Contraste mínimo 4.5:1 (WCAG AA)
  - Bordes visibles (slate-700)
  - Hover states claramente visibles

### TEST 5.5: Animaciones
- **Pasos**: 
  1. Crea plan
  2. Observa transiciones entre pasos
- **Resultado Esperado**:
  - Fade in/out suave (300ms)
  - No es distractivo
  - Loading spinner durante duración calculation

---

## 🔍 **BÚSQUEDA DE CARRERAS**

### TEST 6.1: Búsqueda Básica
- **Pasos**: 
  1. Paso 1: Click "Sí, tengo carrera"
  2. Escribe "madrid"
  3. Espera 500ms
- **Resultado Esperado**:
  - Se muestran carreras con "madrid" en nombre/ciudad
  - "Maratón de Madrid", "10K Madrid", etc.

### TEST 6.2: Búsqueda con Acentos
- **Pasos**: Escribe "león" (con acento)
- **Resultado Esperado**:
  - Encuentra carreras "León" sin problemas
  - Búsqueda accent-insensitive

### TEST 6.3: No hay Resultados
- **Pasos**: Escribe "xyzabc123"
- **Resultado Esperado**:
  - Mensaje: "❌ No se encontraron carreras"
  - No loop infinito de "Buscando..."

### TEST 6.4: Caché Funciona
- **Pasos**: 
  1. Busca "madrid" (tarda ~500ms)
  2. Busca otra cosa
  3. Busca "madrid" de nuevo
- **Resultado Esperado**:
  - Segunda búsqueda de "madrid" es instantánea (<10ms)

### TEST 6.5: Seleccionar Carrera
- **Pasos**: 
  1. Busca y selecciona "Media Maratón Dos Hermanas"
  2. Verifica que se muestra en resumen
- **Resultado Esperado**:
  - Carrera guardada en formData
  - Duración calculada automáticamente

---

## 🚀 **PERFORMANCE**

### TEST 7.1: Dashboard Carga Rápido
- **Pasos**: Abre dashboard, mide tiempo de carga completa
- **Resultado Esperado**: < 3 segundos hasta completamente renderizado

### TEST 7.2: Queries Optimizadas (No N+1)
- **Pasos**: 
  1. Abre DevTools Network
  2. Navega a dashboard
  3. Cuenta número de requests
- **Resultado Esperado**:
  - Máximo 5-6 requests API (no 20+)
  - Query time < 200ms cada una

### TEST 7.3: Búsqueda de Carreras Caché
- **Pasos**: 
  1. Medir primer "madrid"
  2. Medir segundo "madrid"
- **Resultado Esperado**: Segunda búsqueda < 10ms (vs 500ms primera)

---

## 🔒 **SEGURIDAD**

### TEST 8.1: SQL Injection en Búsqueda
- **Pasos**: Intenta buscar `" OR "1"="1`
- **Resultado Esperado**: Sin error SQL visible, búsqueda normal

### TEST 8.2: No se puede Manipular Duración
- **Pasos**: Console → setFormData({ plan_duration_weeks: 200 })
- **Resultado Esperado**: Backend valida, rechaza si > 24 semanas

### TEST 8.3: Rate Limiting en Búsqueda
- **Pasos**: 
  1. Envía 300 búsquedas en 1 minuto
- **Resultado Esperado**: Error 429 "Too Many Requests" después de ~100

### TEST 8.4: JWT Expira Correctamente
- **Pasos**: 
  1. Login
  2. Esperar a que JWT expire (ej: 1 hora)
  3. Intenta navegar
- **Resultado Esperado**: Redirige a login

---

## 📱 **CROSS-BROWSER**

### TEST 9.1: Chrome
- Crear plan completo
- Dashboard carga correctamente
- Responsive en mobile

### TEST 9.2: Firefox
- Mismo como TEST 9.1

### TEST 9.3: Safari
- Mismo como TEST 9.1
- Verificar: inputs tienen min-height 48px (evita zoom auto)

### TEST 9.4: Mobile Safari (iPhone)
- Crear plan en iPhone real o simulado
- Verificar: no hay zoom inesperado

---

## ✅ **RESUMEN DE VALIDACIÓN**

- [ ] Todos los tests 1-9 pasados
- [ ] No hay errores en consola
- [ ] No hay warnings en compilación
- [ ] Responsive en 375px, 768px, 1024px, 1920px
- [ ] Performance < 3s dashboard load
- [ ] Dark mode contraste OK
- [ ] Búsqueda caché funciona
- [ ] Plan se crea sin errores
- [ ] All 6 steps workflow completo

**PLATAFORMA LISTA PARA PRODUCCIÓN ✅**
