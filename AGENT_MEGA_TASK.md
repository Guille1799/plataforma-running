# 🏆 MEGA-TAREA: PLATAFORMA DE RUNNING MUNDIAL

**OBJETIVO**: Transformar la plataforma en el MEJOR sistema de entrenamiento personalizado del mundo.

**TIEMPO ESTIMADO**: 4-6 horas completas de trabajo
**COMPLEJIDAD**: MÁXIMA
**PRIORIDAD**: CRÍTICA

---

## 📋 TAREA 0: PRELIMINARES (Validación Inicial)

### 0.1 Estado Actual
- ✅ Backend FastAPI corriendo en :8000
- ✅ Frontend Next.js corriendo en :3000
- ✅ EventsService con 27 carreras españolas
- ✅ Fórmula Karvonen implementada
- ✅ Duración automática de planes (agent ya hizo esto)
- ✅ Formulario V2 con 6 pasos (agent ya hizo esto)

### 0.2 Validar Antes de Empezar
1. Verificar que NO hay errores en:
   - `backend/app/services/coach_service.py` (línea 1411 tiene logger indefinido)
   - `frontend/app/(dashboard)/dashboard/training-plan-form-v2.tsx` (compilación limpia)
2. Verificar endpoints disponibles:
   - POST `/api/v1/training-plans/duration/with-target-race`
   - GET `/api/v1/training-plans/duration-options/{goal_type}`
   - GET `/api/v1/events/races/search`
3. Verificar modelos de Base de Datos:
   - User tiene campos: max_heart_rate, power_zones (JSON), hr_zones (JSON)
   - Workout tiene campos: avg_heart_rate, distance_meters, start_time

---

## 🔧 TAREA 1: OPTIMIZACIONES BACKEND (Velocidad + Confiabilidad)

### 1.1 CACHÉ EN EVENTS SERVICE
**Archivo**: `backend/app/services/events_service.py`

Implementar:
```python
from functools import lru_cache
from datetime import datetime, timedelta

# En EventsService class:
- Método search_races() con @lru_cache(maxsize=128)
- TTL de 1 hora (usar wrapper personalizado)
- Normalizar query: lowercase, sin acentos duplicados
- Resultado: búsquedas repetidas < 1ms en lugar de 100ms+
```

### 1.2 LOGGING ROBUSTO EN COACH SERVICE
**Archivo**: `backend/app/services/coach_service.py`

Implementar:
```python
import logging

# Configurar logger
logger = logging.getLogger(__name__)

# Agregar logging en:
- calculate_hr_zones(): INFO entrada + DEBUG valores calculados
- identify_workout_zone(): DEBUG con zona detectada
- generate_personalized_training_plan(): INFO plan generado + ERROR si falla
- _calculate_power_zones(): DEBUG con cálculos

# Formato: timestamp | LEVEL | función | mensaje
# Ej: 2025-11-16 14:30:45 | INFO | calculate_hr_zones | Calculating zones for max_hr=190, resting_hr=60
```

**NOTA CRÍTICA**: Reemplazar línea 1411 que tiene `logger.error` sin definir logger

### 1.3 OPTIMIZAR N+1 QUERIES
**Archivos**: `backend/app/routers/coach.py`, `backend/app/routers/workouts.py`

Implementar:
```python
# En get recent workouts:
- Usar joinedload() para eager loading de relaciones
- Ej: query(Workout).options(joinedload(Workout.user)).filter(...)
- Agregar índices en User-Workout (user_id, start_time)
- Lazy load power_zones/hr_zones solo cuando se usen

# Resultado: queries 50-70% más rápidas
```

### 1.4 AGREGAR ÍNDICES EN BASE DE DATOS
**Archivo**: `backend/app/models.py` + migration

```python
# En Workout model:
__table_args__ = (
    Index('idx_user_start_time', 'user_id', 'start_time'),
    Index('idx_user_distance', 'user_id', 'distance_meters'),
    Index('idx_start_time', 'start_time'),
)

# Validar que SQLite supports indexes (sí)
```

### 1.5 VALIDACIONES ROBUSTAS EN SCHEMAS
**Archivo**: `backend/app/schemas.py`

Implementar:
- Validar que plan_duration_weeks >= 4 y <= 24
- Validar que target_race_date > hoy
- Validar que max_heart_rate > 100 y < 250 bpm
- Validar que training_days_per_week >= 3 y <= 7
- Mensajes de error descriptivos en español

---

## 📊 TAREA 2: DASHBOARD METRICS (Visualización Inteligente)

### 2.1 MOSTRAR ZONAS DE FC Y POTENCIA
**Archivo**: `frontend/app/(dashboard)/dashboard/page.tsx`

Implementar nueva sección "Tus Zonas de Entrenamiento":
```tsx
// Card para HR Zones (si user.max_heart_rate)
- Mostrar 5 zonas en horizontal (mobile) o vertical (desktop)
- Cada zona: nombre, bpm range, color código
- Colores: Z1=azul (#3b82f6), Z2=verde (#10b981), Z3=amarillo (#f59e0b), 
           Z4=naranja (#f97316), Z5=rojo (#ef4444)
- Click en zona → mostrar tooltip con descripción

// Card para Power Zones (si user.power_zones)
- Similar a HR pero en Watts
- 7 zonas (Z1-Z7)
- Si no hay FTP, mostrar "Configura tu FTP en Perfil"
```

### 2.2 CREAR COMPONENTE: WORKOUTS BY ZONE
**Archivo**: `frontend/app/(dashboard)/dashboard/components/workouts-by-zone.tsx` (NUEVO)

Implementar:
```tsx
// Gráfico de pastel o barras (usar recharts)
- Últimas 4 semanas
- Mostrar: % de workouts por zona, total horas por zona
- Interactivo: hover muestra valores exactos
- Responsive: mobile=pastel, desktop=barras
- Si no hay datos, mostrar "Completa entrenamientos para ver análisis"
```

**Backend endpoint** (si no existe):
```python
# GET /api/v1/coach/stats/by-zone
- Retorna: {
    "zone_1": {"count": 5, "hours": 4.5, "percentage": 15},
    "zone_2": {"count": 15, "hours": 22, "percentage": 65},
    ...
  }
- Últimas 20 workouts (4 semanas aproximadamente)
```

### 2.3 CREAR COMPONENTE: PROGRESSION CHART
**Archivo**: `frontend/app/(dashboard)/dashboard/components/progression-chart.tsx` (NUEVO)

Implementar:
```tsx
// Gráfico de líneas (recharts)
- Eje X: últimas 8 semanas
- Eje Y: km totales por semana
- 3 líneas: actual, media, máximo
- Hover: muestra valores exactos + % cambio
- Tendencia: línea de tendencia polinomial (simple ML)
- Si tendencia sube: "↗️ Progresando bien"
- Si baja: "↘️ Volumen bajando"
```

### 2.4 CREAR COMPONENTE: WORKOUT INSIGHTS
**Archivo**: `frontend/app/(dashboard)/dashboard/components/workout-insights.tsx` (NUEVO)

Implementar sugerencias inteligentes:
```tsx
// Mostrar 3 insights:
1. "Tu volumen está en zona verde (30km/semana)" ✓
2. "Recomendamos descansar este fin de semana" (si HR elevado)
3. "¡Próxima carrera en 12 días! Aumenta velocidad" (si hay target_race)

// Basado en:
- Comparar volumen actual vs recomendado
- HR trends (detectar fatiga)
- Proximidad a carrera objetivo
```

### 2.5 INTEGRAR EN DASHBOARD LAYOUT
**Archivo**: `frontend/app/(dashboard)/dashboard/page.tsx`

```tsx
// Grid layout responsivo:
// Mobile (1 col): Zones → Workouts by Zone → Progression → Insights
// Tablet (2 cols): [Zones + Workouts by Zone] [Progression + Insights]
// Desktop (3 cols): [Zones] [Progression] [Workouts by Zone + Insights]

// Loading states: usar skeleton loaders
// Error states: mostrar mensajes claros
```

---

## 🎨 TAREA 3: UI POLISH (Experiencia Perfecta)

### 3.1 RESPONSIVE DESIGN FORMULARIO
**Archivo**: `frontend/app/(dashboard)/dashboard/training-plan-form-v2.tsx`

```tsx
// Mobile (< 640px):
- Padding aumentado: 16px (evita contenido cortado)
- Inputs/selects: min-height 48px (mejor para tocar)
- Botones: width 100%, apilados verticalmente
- Text: 16px mínimo en inputs (evita auto-zoom Safari)
- Step title: 24px, bold

// Tablet (640-1024px):
- Padding: 20px
- Inputs/selects: width 100%, algunos side-by-side si cabe
- Botones: grid 2 cols cuando hay opciones múltiples
- Step title: 28px

// Desktop (> 1024px):
- Layout actual (perfecto)
- Padding: 32px
- Step title: 32px

// Test en: 375px, 768px, 1024px, 1920px
```

### 3.2 ANIMACIONES SUAVES
**Archivo**: `frontend/app/(dashboard)/dashboard/training-plan-form-v2.tsx`

```tsx
// Entre pasos:
- Fade in/out: duration 300ms, easing ease-in-out
- Usar Framer Motion o CSS transitions
- Loading spinner durante cálculo de duración (200ms delay para UX)

// Cards:
- Hover: shadow + scale(1.02)
- Click: ripple effect suave

// Notificaciones:
- Toast al cambiar paso: "Paso X de Y"
- Toast al crear plan: "Plan creado exitosamente"
```

### 3.3 DARK MODE CONSISTENCY
**Archivos**: Todos los componentes nuevos

```tsx
// WCAG AA mínimo (contraste 4.5:1)
// Verificar en cada componente:
- Texto claro en fondo oscuro: text-slate-100 sobre bg-slate-800
- Bordes visibles: border-slate-700 (no border-slate-800)
- Hover states: hover:bg-slate-700 (visible oscuro)
- Active states: bg-blue-600 (destacado)
- Disabled: opacity-50, cursor-not-allowed

// Si algo no cumple contraste, usar:
- Más luz: text-slate-50 o text-white
- Más oscuro: bg-slate-900 en lugar de slate-800
- Borders: slate-600 si slate-700 no es suficiente

// Validar con: https://webaim.org/resources/contrastchecker/
```

### 3.4 SKELETON LOADERS
**Archivo**: `frontend/components/ui/skeleton-loader.tsx` (crear si no existe)

```tsx
// Componentes:
- SkeletonCard: 300px height, pulse animation
- SkeletonChart: 400px height, pulse animation
- SkeletonField: 48px height, pulse animation
- SkeletonButton: 48px height, pulse animation

// Uso:
- Dashboard mientras carga datos: mostrar 3x SkeletonCard
- Búsqueda de carreras: SkeletonField mientras busca
- Gráficos: SkeletonChart mientras carga

// Animación: pulse 2s infinite, opacity 0.5-1.0
```

### 3.5 TOOLTIPS E INFORMACIÓN CONTEXTUAL
**Archivo**: `frontend/components/ui/tooltip.tsx` (usar o crear)

```tsx
// Agregar tooltips en:
1. Zonas de FC: "Z1 es recuperación activa..."
2. Zona de Potencia: "FTP es tu máxima potencia sostenible 1 hora..."
3. Carrera selector: "Distancia: 21km | Fecha: 20 Abril"
4. Duración opciones: "Recomendado para tu nivel"
5. Método de entrenamiento: "Basado en ritmo o FC"

// Trigger:
- Desktop: hover (200ms delay)
- Mobile: tap/click (dismissible)

// Estilo: bg-slate-900, text-white, 12px font, rounded
```

---

## 🚀 TAREA 4: ADVANCED FEATURES (Inteligencia + Predictiva)

### 4.1 DETECCIÓN DE SOBREENTRENAMIENTO
**Archivo**: `backend/app/services/coach_service.py`

Nuevo método `detect_overtraining()`:
```python
def detect_overtraining(self, user: User, recent_workouts: List[Workout]) -> Dict:
    """
    Detectar señales de sobreentrenamiento:
    - Aumento de HR en reposo (> 5 bpm arriba de baseline)
    - Volumen muy alto en poco tiempo (> 10% aumento semanal)
    - Falta de días de descanso (< 1 día rest por semana)
    - HR elevado en entrenamientos fáciles
    
    Retorna:
    {
        "overtraining_risk": "low|medium|high",
        "signals": ["HR elevado", "Volumen alto", ...],
        "recommendation": "Descansa 2-3 días"
    }
    """
```

Integrar en endpoint POST `/api/v1/coach/check-overtraining`

### 4.2 SUGERENCIAS AUTOMÁTICAS DE AJUSTE
**Archivo**: `backend/app/services/coach_service.py`

Nuevo método `suggest_plan_adjustments()`:
```python
def suggest_plan_adjustments(self, plan: Dict, recent_performance: Dict) -> Dict:
    """
    Sugerencias basadas en ejecución real:
    - "Aumentar velocidad work (completaste todos exitosamente)"
    - "Reducir volumen (solo completaste 70%)"
    - "Agregar descanso (HR elevado)"
    - "Cambiar a método HR-based (tienes muchos datos HR)"
    """
```

Endpoint: POST `/api/v1/training-plans/{plan_id}/adjust`

### 4.3 PREDICTIVAS: ML SIMPLE
**Archivo**: `backend/app/services/predictions_service.py` (CREAR)

```python
class PredictionService:
    def predict_race_time(self, user: User, race_distance: float) -> Dict:
        """
        Predecir tiempo de carrera basado en:
        - Workouts recientes (últimas 8 semanas)
        - Velocidades en zonas Z3, Z4, Z5
        - Distancias largas completadas
        
        Usar: simple linear regression o VVO2Max formula
        
        Retorna: {"predicted_time": "2:15:00", "confidence": 0.85}
        """
    
    def predict_next_milestone(self, user: User) -> Dict:
        """
        Predicción del próximo milestone alcanzable:
        "En 4 semanas podrías alcanzar sub-40 en 10K"
        """
```

---

## 🔒 TAREA 5: SEGURIDAD & COMPLIANCE

### 5.1 RATE LIMITING
**Archivo**: `backend/app/main.py`

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# Aplicar a endpoints sensibles:
- POST /api/v1/training-plans/duration/with-target-race: 100/hora
- GET /api/v1/events/races/search: 200/hora
- POST /api/v1/coach/generate: 10/hora (muy costoso)
- POST /api/v1/coach/plan: 5/hora
```

### 5.2 VALIDACIÓN DE DATOS ESTRICTA
**Archivo**: `backend/app/schemas.py`

```python
# Agregar @validator en todos los schemas:
- TrainingPlanRequest: validar ranges, tipos, dependencias
- DurationCalculationRequest: validar dates, goal_type
- RaceSearchRequest: sanitizar strings (SQL injection)

# Validar:
- Ningún user_id manipulado (usar current_user siempre)
- Dates nunca en pasado
- Números siempre en rangos válidos
```

### 5.3 GDPR COMPLIANCE
**Archivo**: `backend/app/routers/profile.py` (nuevo endpoint)

```python
@router.post("/export-data")
def export_user_data(current_user):
    """Exporta TODOS los datos del usuario en JSON"""
    return {
        "user": {...},
        "workouts": [...],
        "plans": [...],
        "exported_at": datetime.now().isoformat()
    }

@router.post("/delete-account")
def delete_account(current_user):
    """Elimina TODOS los datos del usuario (irreversible)"""
    # Requiere confirmación por email
```

### 5.4 ENCRYPTION DE DATOS SENSIBLES
**Archivo**: `backend/app/core/security.py`

```python
# Encriptar:
- garmin_token (ya encriptado probablemente)
- strava_tokens
- Cualquier token de integración

# Usar: cryptography library, key from .env
```

---

## 📱 TAREA 6: NOTIFICACIONES & ALERTAS

### 6.1 SISTEMA DE NOTIFICACIONES
**Archivo**: `backend/app/services/notification_service.py` (CREAR)

```python
class NotificationService:
    def send_notification(self, user_id: int, type: str, message: str, data: Dict):
        """
        Tipos:
        - overtraining_alert
        - upcoming_race
        - plan_complete
        - achievement_unlocked
        - weekly_summary
        """
```

### 6.2 IN-APP NOTIFICATIONS
**Archivo**: `frontend/app/(dashboard)/dashboard/components/notification-center.tsx` (CREAR)

```tsx
// Toast notifications para:
- "⚠️ Alto riesgo de sobreentrenamiento"
- "🏁 Tu carrera es en 7 días"
- "🎉 ¡Completaste 4 semanas de plan!"
- "📊 Resumen semanal listo"
```

---

## 📈 TAREA 7: DATA EXPORT & REPORTS

### 7.1 EXPORTAR PLAN A PDF
**Archivo**: `backend/app/routers/training_plans.py`

```python
@router.get("/export/{plan_id}/pdf")
def export_plan_pdf(plan_id: str, current_user):
    """Genera PDF con plan completo (todas las semanas y entrenamientos)"""
    # Usar: reportlab o WeasyPrint
    # Incluir: objetivo, duración, entrenamientos por semana, notas
```

### 7.2 REPORTE SEMANAL
**Archivo**: `backend/app/services/reports_service.py` (CREAR)

```python
def generate_weekly_report(user_id: int, week: int) -> Dict:
    """
    Reporte semanal con:
    - Entrenamientos completados vs planeados
    - Volumen total, promedio de HR, mejor workout
    - Cumplimiento de intensidades (% tiempo en cada zona)
    - Notas del coach AI
    """
```

Endpoint: GET `/api/v1/coach/reports/weekly/{week}`

### 7.3 EXPORTAR CSV
**Archivo**: `backend/app/routers/workouts.py`

```python
@router.get("/export/csv")
def export_workouts_csv(current_user):
    """CSV con todos los workouts para análisis externo"""
    # Columnas: date, type, distance, time, avg_hr, max_hr, pace, zones
```

---

## 🌍 TAREA 8: INTEGRACIONES AVANZADAS

### 8.1 WEATHER INTEGRATION
**Archivo**: `backend/app/services/weather_service.py` (CREAR)

```python
class WeatherService:
    def get_weather_for_location(self, location: str, date: str) -> Dict:
        """
        API: Open-Meteo (free) o Weather.API
        Retorna: temp, humidity, wind, rain probability
        """
    
    def suggest_pace_adjustment(self, weather: Dict, planned_pace: float) -> float:
        """
        Ajusta pace sugerido basado en clima:
        - Calor: reducir 30-60 seg/km
        - Frío: reducir 15-30 seg/km
        - Viento fuerte: reducir 45-90 seg/km
        """
```

### 8.2 EQUIPAMIENTO SUGERENCIAS
**Archivo**: `backend/app/services/gear_service.py` (CREAR)

```python
def suggest_gear(weather: Dict, distance: float) -> List[str]:
    """
    Sugerencias de ropa/equipamiento:
    - Temperatura < 10°C: "Chaqueta, guantes, gorro"
    - Distancia > 20km: "Cinturón de hidratación"
    - Lluvia: "Reflectantes, chaqueta impermeable"
    """
```

Endpoint: GET `/api/v1/coach/gear-suggestions?location=&date=`

---

## ✅ TAREA 9: VALIDACIONES EXHAUSTIVAS

### 9.1 COMPILACIÓN LIMPIA
- ✅ `tsc --noEmit` sin errores en frontend
- ✅ `pylint backend/` sin warnings críticos
- ✅ Todos los imports usados
- ✅ Tipos TypeScript strict mode completo

### 9.2 TESTING
- ✅ Backend: `pytest` todos los tests verdes
- ✅ Frontend: `npm test` todos los tests verdes
- ✅ E2E: Formulario completo sin errores
- ✅ Performance: Cada página < 3s inicial load

### 9.3 RESPONSIVE TESTING
- ✅ Mobile 375px: layout correcto, toques funcionan
- ✅ Tablet 768px: grid layout perfecto
- ✅ Desktop 1920px: espaciado y tipografía óptimos
- ✅ Dark mode: contraste 4.5:1 minimum

### 9.4 FUNCIONALIDAD END-TO-END
1. ✅ Login → Dashboard
2. ✅ Crear plan CON carrera → duración automática
3. ✅ Crear plan SIN carrera → opciones de duración
4. ✅ Ver zonas de FC y potencia
5. ✅ Ver gráficos de progresión
6. ✅ Ver sugerencias inteligentes
7. ✅ Exportar plan a PDF
8. ✅ Detección de sobreentrenamiento
9. ✅ Predicción de tiempo en carrera

---

## 📝 RETORNO ESPERADO

Después de completar TODO, retorna:

```markdown
# ✅ MEGA-TAREA COMPLETADA

## Backend
- [ ] Archivo: Cambios realizados
- [ ] Archivo: Cambios realizados

## Frontend
- [ ] Archivo: Cambios realizados
- [ ] Archivo: Cambios realizados

## Validaciones
- [x] Compilación limpia
- [x] Tests pasados
- [x] E2E funciona
- [x] Responsive en 3 breakpoints

## Features Implementadas
- [x] Feature 1
- [x] Feature 2
- ...

## Problemas Encontrados y Resueltos
- Problema 1: Solución aplicada
- Problema 2: Solución aplicada

## Próximos Pasos Recomendados
1. ...
2. ...

## Performance Metrics
- Query time improvements: X%
- Frontend bundle size: X KB
- Initial load: X ms
```

---

## 🎯 PRIORIZACIÓN

Si no hay tiempo suficiente, completar en este orden:

**TIER 1 (CRÍTICO)**:
- Tarea 0 (Validaciones)
- Tarea 1 (Backend Optimizations)
- Tarea 2 (Dashboard Metrics)
- Tarea 3 (UI Polish)

**TIER 2 (IMPORTANTE)**:
- Tarea 4 (Advanced Features)
- Tarea 5 (Seguridad)

**TIER 3 (NICE-TO-HAVE)**:
- Tarea 6 (Notificaciones)
- Tarea 7 (Export/Reports)
- Tarea 8 (Integraciones)

---

## 🏆 FILOSOFÍA

Esta es una plataforma para buscar la **EXCELENCIA ABSOLUTA**. Cada detalle importa:
- Performance no debe sacrificarse por features
- UI/UX debe ser intuitiva sin excepciones
- Seguridad es non-negotiable
- Testing coverage mínimo 80%
- Documentación clara en cada función importante

**VAMOS A CREAR LA MEJOR PLATAFORMA DE RUNNING DEL MUNDO. 🚀**
