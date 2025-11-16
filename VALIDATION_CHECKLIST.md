# 📋 CHECKLIST DE VALIDACIÓN - Plataforma de Running

## 🚀 ANTES DE PRODUCCIÓN

Usar este checklist para validar que TODO está perfecto.

---

## ✅ **COMPILACIÓN & SINTAXIS**

- [ ] `cd frontend && npm run build` sin errores
- [ ] `tsc --noEmit` en frontend sin errores TypeScript
- [ ] Backend imports correctos: `python -m py_compile app/**/*.py`
- [ ] No hay archivos con import circular
- [ ] Todos los archivos creados están en carpeta correcta

**Validación**: 
```bash
# Frontend
cd frontend && npm run build && tsc --noEmit

# Backend  
cd backend && pylint app/ --disable=all --enable=E --max-line-length=120
```

---

## 🧪 **TESTS**

- [ ] Backend tests: `pytest backend/` → All green
- [ ] Frontend tests: `npm test` → All green
- [ ] Coverage > 80% en funciones críticas
- [ ] E2E test: Crear plan completo sin errores

**Validación**:
```bash
# Backend
cd backend && pytest -v

# Frontend
cd frontend && npm test -- --coverage
```

---

## 📦 **DEPENDENCIAS**

### Backend
- [ ] FastAPI
- [ ] SQLAlchemy
- [ ] Pydantic
- [ ] Groq
- [ ] slowapi (rate limiting)
- [ ] python-logging configurado

**Validación**: `pip list | grep -E "fastapi|sqlalchemy|pydantic|groq|slowapi"`

### Frontend
- [ ] Next.js 16+
- [ ] React 18+
- [ ] TypeScript
- [ ] Tailwind CSS
- [ ] recharts (gráficos)
- [ ] axios

**Validación**: `npm list`

---

## 🎨 **UI/UX**

### Responsive Design
- [ ] 375px (iPhone SE): layout correcto, no scroll horizontal
- [ ] 768px (iPad): grid 2 cols donde cabe
- [ ] 1024px (tablet landscape): layout óptimo
- [ ] 1920px (desktop): padding/spacing perfecto
- [ ] Botones min 48px height (tocar fácil)
- [ ] Inputs 16px min font (no auto-zoom Safari)

### Dark Mode
- [ ] Texto claro en fondo oscuro: contrast ≥ 4.5:1
- [ ] Bordes visibles: no son demasiado oscuros
- [ ] Hover states claramente visibles
- [ ] Verifica: Dropdown, Cards, Buttons, Inputs
- [ ] WCAG AA compliance mínimo

**Validación**: https://webaim.org/resources/contrastchecker/

### Animaciones
- [ ] Transiciones entre pasos: fade in/out 300ms
- [ ] Loading spinners: visible pero no distractivo
- [ ] Hover effects: suaves, responden
- [ ] Sin motion sickness (no demasiadas animaciones)

### Accessibility
- [ ] Alt text en todas las imágenes
- [ ] Aria labels en botones sin texto
- [ ] Keyboard navigation funciona (Tab, Enter, Escape)
- [ ] Color no es el único indicador (usa iconos también)
- [ ] Focus visible en todos los inputs

---

## 🔧 **BACKEND**

### APIs
- [ ] Todos los endpoints documentados en Swagger
- [ ] Request/Response schemas correctos
- [ ] Error messages descriptivos en español
- [ ] HTTP status codes correctos (200, 400, 401, 404, 500)

**Validación**: 
```bash
curl http://localhost:8000/docs
```

### Database
- [ ] Índices creados: user_id, start_time en Workout
- [ ] No hay N+1 queries: queries < 200ms
- [ ] Relaciones con eager loading donde corresponde
- [ ] Migrations up-to-date

**Validación**: 
```python
from sqlalchemy import event, func
# Profile queries
```

### Logging
- [ ] Logger importado en coach_service.py
- [ ] Logs en: calculate_hr_zones, generate_personalized_training_plan, etc.
- [ ] Formato: timestamp | LEVEL | función | mensaje
- [ ] Visible en: `docker logs` o stderr

### Caching
- [ ] EventsService.search_races() con @lru_cache
- [ ] TTL de 1 hora implementado
- [ ] Búsquedas repetidas < 10ms

### Security
- [ ] Rate limiting: GET /races 200/hora, POST /plan 5/hora
- [ ] Validación de inputs en todos los schemas
- [ ] Tokens JWT con expiración correcta
- [ ] No hay datos sensibles en logs
- [ ] SQL injection prevenido (usar ORM)

### Performance
- [ ] Dashboard query < 200ms
- [ ] Búsqueda de carreras < 500ms (first time), < 10ms (caché)
- [ ] Crear plan < 5 segundos
- [ ] No hay timeout en ningún endpoint

---

## 🎯 **FRONTEND**

### Performance
- [ ] Initial load < 3 segundos
- [ ] Bundle size < 500KB (gzipped)
- [ ] LCP (Largest Contentful Paint) < 2.5s
- [ ] FID (First Input Delay) < 100ms
- [ ] CLS (Cumulative Layout Shift) < 0.1

**Validación**: 
```bash
npm run build
# Check .next/static files size
```

### API Integration
- [ ] API client con todos los endpoints
- [ ] Error handling: retry logic, timeouts
- [ ] Loading states en todos los async calls
- [ ] Datos cacheados donde corresponde (React Query)

### State Management
- [ ] FormData persiste correctamente
- [ ] No hay state contradictorio (loading + error simultáneos)
- [ ] Reset de estado cuando corresponde

### Componentes
- [ ] Todos los componentes tienen TypeScript types
- [ ] Props validadas con PropTypes o Zod
- [ ] Children typed correctamente
- [ ] Event handlers tipados

---

## 🔐 **INTEGRACIONES**

### Garmin
- [ ] Token refresh automático cuando expira
- [ ] Sincronización de workouts funciona
- [ ] Permisos solicitados correctamente

### Strava
- [ ] OAuth flow completo
- [ ] Token guardado encriptado
- [ ] Sync funciona

### Groq AI
- [ ] API key en .env (no en código)
- [ ] Modelo llama-3.3-70b disponible
- [ ] Rate limit respetado (100 requests/minuto)
- [ ] Timeout adecuado (30 segundos)

---

## 📊 **FEATURES**

### Búsqueda de Carreras
- [ ] Accent-insensitive: "león" encuentra "León"
- [ ] Case-insensitive
- [ ] Partial match: "mad" encuentra "Madrid"
- [ ] 27+ carreras españolas disponibles
- [ ] Caché funciona (búsqueda repetida rápida)

### Duración de Planes
- [ ] Con carrera: calcula automáticamente
  - 5K: 8-12 semanas (default 10)
  - 10K: 10-14 semanas (default 12)
  - Media Maratón: 12-16 semanas (default 14)
  - Maratón: 16-20 semanas (default 18)
- [ ] Sin carrera: muestra opciones
- [ ] Validación: error si no hay tiempo suficiente

### Zonas de FC
- [ ] Usa Karvonen formula (no simple % max HR)
- [ ] Input: max_hr, resting_hr
- [ ] Output: 5 zonas con rangos en bpm
- [ ] Colores correctos: azul, verde, amarillo, naranja, rojo

### Zonas de Potencia
- [ ] Input: FTP en watts
- [ ] Output: 7 zonas con rangos en watts
- [ ] Z1 <55%, Z2 55-75%, ..., Z7 >150%

### Dashboard Metrics
- [ ] Zonas de FC mostradas con rangos
- [ ] Zonas de Potencia mostradas con rangos
- [ ] Gráfico Workouts by Zone (últimas 4 semanas)
- [ ] Gráfico Progression Chart (últimas 8 semanas)
- [ ] Sugerencias inteligentes (mínimo 3)

### Formulario 6 Pasos
- [ ] Paso 1: Carrera sí/no
- [ ] Paso 2: Objetivo y Prioridad
- [ ] Paso 3: Disponibilidad (días, tirada larga)
- [ ] Paso 4: Entrenamientos adicionales (fuerza, cross-training)
- [ ] Paso 5: Método de entrenamiento
- [ ] Paso 6: Recuperación y Duración

---

## 🚦 **END-TO-END WORKFLOW**

### Flujo Completo con Carrera
- [ ] Usuario nuevo
- [ ] Completa perfil (altura, peso, FC máx)
- [ ] Crea plan con carrera objetivo
- [ ] Plan se genera exitosamente
- [ ] Ve zonas de FC en dashboard
- [ ] Ve plan en sidebar

### Flujo Completo sin Carrera
- [ ] Usuario nuevo
- [ ] Completa perfil
- [ ] Crea plan sin carrera
- [ ] Ve opciones de duración
- [ ] Selecciona una
- [ ] Plan se genera exitosamente

---

## 📱 **RESPONSIVIDAD**

### Dispositivos Testeados
- [ ] iPhone SE (375px)
- [ ] iPad (768px)
- [ ] iPad Pro (1024px)
- [ ] Desktop (1920px)

### Por Dispositivo

**Mobile (< 640px)**
- [ ] No hay scroll horizontal
- [ ] Botones apilados
- [ ] Texto legible (16px mín)
- [ ] Inputs con padding (48px height)
- [ ] Selects funcionan

**Tablet (640-1024px)**
- [ ] Grid 2 columnas
- [ ] Botones side-by-side cuando cabe
- [ ] Spacing óptimo

**Desktop (> 1024px)**
- [ ] Layout completo
- [ ] Padding amplio
- [ ] Eficiente espacialmente

---

## 🧠 **INTELIGENCIA**

### Coach AI
- [ ] Responde preguntas correctamente
- [ ] Analiza workouts
- [ ] Sugiere mejoras
- [ ] Detecta sobreentrenamiento

### Predicciones
- [ ] Calcula duración correcta con fecha
- [ ] Detecta insuficiente tiempo
- [ ] Sugiere próximo milestone

---

## 📊 **MONITOREO & LOGS**

### Backend Logs
- [ ] Se crean en archivo o stdout
- [ ] Nivel adecuado: INFO para eventos, DEBUG para detalles
- [ ] Formato consistente
- [ ] Sin datos sensibles (contraseñas, tokens)

### Frontend Logs
- [ ] Console limpia (sin errors)
- [ ] Sin warnings de React
- [ ] No hay console.log en producción

**Validación**:
```bash
# Backend
docker logs <container> | grep ERROR

# Frontend (DevTools)
F12 → Console → no errors
```

---

## 🎯 **ANTES DE DEPLOY**

- [ ] Todas las secciones arriba ✅
- [ ] README actualizado
- [ ] Documentación de API completa
- [ ] Guía de usuario disponible
- [ ] Test cases documentados
- [ ] Backup de base de datos
- [ ] Variables de entorno configuradas
- [ ] Certificados SSL listos (si es HTTPS)
- [ ] Domain DNS apuntando correctamente
- [ ] CDN configurado (si es relevante)

---

## 🔄 **DESPUÉS DE DEPLOY**

- [ ] Monitorear errores en producción
- [ ] Revisar logs por primeras 24 horas
- [ ] Responder a feedback de usuarios
- [ ] Bug fixes si hay issues críticos
- [ ] Performance monitoring
- [ ] Security scanning periódico

---

## ✅ **FIRMA DE VALIDACIÓN**

```
Validado por: ________________  Fecha: ________

Plataforma Lista para: ☐ Alpha ☐ Beta ☐ Producción

Notas: _______________________________________
```

---

## 🚀 **ÉXITO!**

Si todo está checkeado ✅, la plataforma está **LISTA PARA LA EXCELENCIA** 🏆
