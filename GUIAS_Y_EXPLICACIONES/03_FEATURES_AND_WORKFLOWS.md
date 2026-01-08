# 🏃 RunCoach AI - Features y Workflows

## 📋 Índice

1. [Visión General de Features](#visión-general-de-features)
2. [Dashboard Principal](#dashboard-principal)
3. [Análisis de Entrenamientos](#análisis-de-entrenamientos)
4. [Métricas de Salud](#métricas-de-salud)
5. [Planes de Entrenamiento](#planes-de-entrenamiento)
6. [Base de Datos de Carreras](#base-de-datos-de-carreras)
7. [Configuración de Usuario](#configuración-de-usuario)
8. [Flujos de Usuario Completos](#flujos-de-usuario-completos)
9. [Arquitectura de Datos](#arquitectura-de-datos)

---

## 🎯 Visión General de Features

### Estado Actual (Enero 2026)

| Feature | Estado | Descripción |
|---------|--------|-------------|
| **Autenticación JWT** | ✅ Completo | Register, Login, Refresh tokens |
| **Dashboard** | ✅ Completo | Resumen de métricas, últimos workouts |
| **Upload GPX/FIT** | ✅ Completo | Parser de archivos, extracción de métricas |
| **Análisis IA** | ✅ Completo | Groq Llama 3.3 70B - análisis de entrenamientos |
| **Garmin Sync** | ✅ Completo | OAuth + sincronización 2x/día automática |
| **Métricas de Salud** | ✅ Completo | HRV, FC, sueño, estrés, Body Battery |
| **Base de Datos de Carreras** | ✅ Completo | 52 carreras España, búsqueda avanzada |
| **Generación de Planes IA** | ✅ Completo | Wizard + generación personalizada |
| **Adaptación de Planes** | 🚧 En Progreso | Adaptar según fatiga/progreso |
| **Admin Panel** | ⏳ Pendiente | Gestión de carreras, usuarios |
| **Strava Sync** | ⏳ Pendiente | Importar actividades de Strava |
| **Notificaciones** | ⏳ Pendiente | Email/Push para recordatorios |

### Usuarios Objetivo

1. **Corredores Principiantes:**
   - Necesitan guía y estructura
   - Quieren evitar lesiones
   - Buscan planes personalizados

2. **Corredores Intermedios:**
   - Entrenan para objetivos específicos (medio maratón, maratón)
   - Quieren mejorar tiempos
   - Necesitan feedback sobre entrenamientos

3. **Corredores Avanzados:**
   - Optimización fina de entrenamientos
   - Monitoreo avanzado de métricas (HRV, fatiga)
   - Ajuste dinámico de planes según rendimiento

---

## 📊 Dashboard Principal

### Vista General

**URL:** `/dashboard`

**Componentes:**

1. **Header con Estadísticas Rápidas:**
   ```
   ┌────────────────────────────────────────────────────────────┐
   │  👤 Bienvenido, Guillermo                  🔔 Notificaciones │
   ├────────────────────────────────────────────────────────────┤
   │  📊 Esta Semana:                                            │
   │     ├─ 45 km  (🎯 Objetivo: 50 km)                         │
   │     ├─ 4 entrenamientos                                     │
   │     └─ VO2max: 52.3 (+0.5 desde mes pasado)               │
   └────────────────────────────────────────────────────────────┘
   ```

2. **Gráficos de Tendencias:**
   - Volumen semanal (últimos 3 meses)
   - HRV trend (últimos 30 días)
   - Ritmo promedio por tipo de entrenamiento

3. **Últimos Entrenamientos:**
   - Cards con resumen de últimos 5 workouts
   - Distancia, ritmo, FC, análisis IA resumido

4. **Próximo Objetivo:**
   - Si tiene plan activo: próxima carrera y tiempo restante
   - Progreso del plan (% completado)

5. **Recomendaciones IA:**
   - Basadas en HRV: "Tu HRV es baja, considera día de recuperación"
   - Basadas en volumen: "Has aumentado 15% esta semana, cuidado con sobreentrenamiento"

### Datos Mostrados

```typescript
interface DashboardData {
  user: {
    name: string
    vo2max: number
    pace_threshold: string
  }
  
  weekly_stats: {
    total_km: number
    target_km: number
    workouts_count: number
    avg_pace: string
  }
  
  recent_workouts: WorkoutOut[]
  
  health_trends: {
    hrv_7day_avg: number
    hrv_30day_avg: number
    hrv_trend: 'up' | 'down' | 'stable'
    rhr_current: number
    sleep_score_avg: number
  }
  
  active_plan: {
    name: string
    target_date: string
    weeks_completed: number
    total_weeks: number
    next_workout: {
      type: string
      distance_km: number
      target_pace: string
    }
  } | null
  
  ai_recommendations: string[]
}
```

### API Endpoint

```python
# backend/app/routers/dashboard.py

@router.get("/dashboard")
async def get_dashboard_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> DashboardData:
    # Calcular stats semanales
    week_start = datetime.now() - timedelta(days=7)
    workouts = db.query(Workout).filter(
        Workout.user_id == current_user.id,
        Workout.date >= week_start
    ).all()
    
    total_km = sum(w.distance_km for w in workouts)
    
    # Métricas de salud (últimos 30 días)
    health_metrics = db.query(HealthMetric).filter(
        HealthMetric.user_id == current_user.id,
        HealthMetric.date >= date.today() - timedelta(days=30)
    ).all()
    
    hrv_values = [m.hrv_rmssd for m in health_metrics if m.hrv_rmssd]
    hrv_7day = statistics.mean(hrv_values[-7:]) if len(hrv_values) >= 7 else None
    hrv_30day = statistics.mean(hrv_values) if hrv_values else None
    
    # Plan activo
    active_plan = db.query(TrainingPlan).filter(
        TrainingPlan.user_id == current_user.id,
        TrainingPlan.status == "active"
    ).first()
    
    # Recomendaciones IA
    recommendations = generate_recommendations(current_user, health_metrics, workouts)
    
    return {
        "user": {...},
        "weekly_stats": {...},
        "recent_workouts": workouts[:5],
        "health_trends": {...},
        "active_plan": {...},
        "ai_recommendations": recommendations
    }
```

---

## 🏃 Análisis de Entrenamientos

### Upload y Procesamiento

**Flujo:**

```
Usuario → Selecciona GPX/FIT
          ↓
Frontend → POST /api/v1/workouts/upload (multipart/form-data)
          ↓
Backend → 1. Validar archivo (tipo, tamaño)
          2. Parsear con gpxpy/fitparse
          3. Extraer métricas:
             - Distancia total (km)
             - Duración (segundos)
             - Ritmo promedio (min/km)
             - FC promedio/máx
             - Elevación ganada/perdida
             - Cadencia promedio/máx
          4. Guardar en DB
          5. Encolar tarea Celery para análisis IA
          ↓
Celery → Llamar a Groq API con contexto
          ↓
Backend → Guardar análisis en workout.analysis
          ↓
Frontend → Mostrar workout con análisis completo
```

### Parser GPX

```python
# backend/app/services/workout_service.py

import gpxpy
from datetime import datetime

def parse_gpx(file_content: bytes) -> dict:
    gpx = gpxpy.parse(file_content.decode('utf-8'))
    
    # Extraer puntos
    points = []
    for track in gpx.tracks:
        for segment in track.segments:
            points.extend(segment.points)
    
    if not points:
        raise ValueError("No track points found in GPX")
    
    # Calcular métricas
    total_distance = 0.0
    elevation_gain = 0.0
    elevation_loss = 0.0
    heart_rates = []
    
    for i in range(1, len(points)):
        prev, curr = points[i-1], points[i]
        
        # Distancia (2D)
        distance_2d = gpxpy.geo.haversine_distance(
            prev.latitude, prev.longitude,
            curr.latitude, curr.longitude
        )
        
        # Elevación
        if prev.elevation and curr.elevation:
            elev_diff = curr.elevation - prev.elevation
            if elev_diff > 0:
                elevation_gain += elev_diff
            else:
                elevation_loss += abs(elev_diff)
        
        total_distance += distance_2d
        
        # FC (extensión Garmin)
        if hasattr(curr, 'extensions') and curr.extensions:
            hr = curr.extensions.get('hr') or curr.extensions.get('heartrate')
            if hr:
                heart_rates.append(int(hr))
    
    # Tiempo total
    start_time = points[0].time
    end_time = points[-1].time
    duration = (end_time - start_time).total_seconds()
    
    # Ritmo promedio
    pace_seconds_per_km = duration / (total_distance / 1000)
    avg_pace = format_pace(pace_seconds_per_km)
    
    return {
        "date": start_time,
        "distance_km": round(total_distance / 1000, 2),
        "duration_seconds": int(duration),
        "avg_pace": avg_pace,
        "avg_heart_rate": int(statistics.mean(heart_rates)) if heart_rates else None,
        "max_heart_rate": max(heart_rates) if heart_rates else None,
        "elevation_gain_m": int(elevation_gain),
        "elevation_loss_m": int(elevation_loss)
    }
```

### Parser FIT

```python
from fitparse import FitFile

def parse_fit(file_content: bytes) -> dict:
    fitfile = FitFile(io.BytesIO(file_content))
    
    records = []
    for record in fitfile.get_messages('record'):
        data = {}
        for field in record:
            data[field.name] = field.value
        if data:
            records.append(data)
    
    # Procesar registros (similar a GPX)
    total_distance = records[-1].get('distance', 0) / 1000  # metros → km
    duration = records[-1].get('timestamp') - records[0].get('timestamp')
    
    heart_rates = [r['heart_rate'] for r in records if 'heart_rate' in r]
    avg_hr = int(statistics.mean(heart_rates)) if heart_rates else None
    
    cadences = [r['cadence'] for r in records if 'cadence' in r]
    avg_cadence = int(statistics.mean(cadences)) if cadences else None
    
    return {
        "date": records[0]['timestamp'],
        "distance_km": round(total_distance, 2),
        "duration_seconds": int(duration.total_seconds()),
        "avg_pace": format_pace(duration.total_seconds() / total_distance),
        "avg_heart_rate": avg_hr,
        "max_heart_rate": max(heart_rates) if heart_rates else None,
        "avg_cadence": avg_cadence,
        "max_cadence": max(cadences) if cadences else None,
        "elevation_gain_m": int(records[-1].get('total_ascent', 0)),
        "elevation_loss_m": int(records[-1].get('total_descent', 0))
    }
```

### Análisis con IA

**Prompt Template:**

```python
def generate_analysis_prompt(workout: dict, user: User) -> str:
    return f"""
Eres un entrenador profesional de running. Analiza este entrenamiento:

DATOS DEL ENTRENAMIENTO:
- Distancia: {workout['distance_km']} km
- Duración: {workout['duration_seconds'] // 60} minutos
- Ritmo promedio: {workout['avg_pace']} min/km
- Frecuencia cardíaca promedio: {workout['avg_heart_rate']} bpm
- FC máxima: {workout['max_heart_rate']} bpm
- Desnivel positivo: {workout['elevation_gain_m']} m
- Cadencia promedio: {workout.get('avg_cadence', 'N/A')} spm

CONTEXTO DEL ATLETA:
- VO2max: {user.vo2max}
- Ritmo umbral: {user.pace_threshold} min/km
- FC máxima teórica: {220 - user.age} bpm (edad: {user.age} años)

ANÁLISIS REQUERIDO (JSON):
{{
  "workout_type": "recovery|base|tempo|intervals|long|race",
  "intensity": "low|moderate|high|very_high",
  "execution_quality": 1-10 (número),
  "aerobic_efficiency": "good|moderate|poor",
  "heart_rate_zones": {{
    "zone_1_pct": <porcentaje>,
    "zone_2_pct": <porcentaje>,
    "zone_3_pct": <porcentaje>,
    "zone_4_pct": <porcentaje>,
    "zone_5_pct": <porcentaje>
  }},
  "strengths": ["punto fuerte 1", "punto fuerte 2"],
  "areas_for_improvement": ["mejora 1", "mejora 2"],
  "injury_risk": "low|moderate|high",
  "injury_risk_factors": ["factor 1", "factor 2"],
  "recommendations": ["recomendación 1", "recomendación 2"],
  "next_workout_suggestion": "descripción del próximo entrenamiento ideal"
}}

Sé específico y práctico. Basa tus recomendaciones en fisiología del ejercicio.
"""
```

**Resultado del Análisis:**

```json
{
  "workout_type": "tempo",
  "intensity": "high",
  "execution_quality": 8,
  "aerobic_efficiency": "good",
  "heart_rate_zones": {
    "zone_1_pct": 10,
    "zone_2_pct": 25,
    "zone_3_pct": 40,
    "zone_4_pct": 20,
    "zone_5_pct": 5
  },
  "strengths": [
    "Ritmo constante durante todo el entrenamiento",
    "Cadencia óptima >180 spm"
  ],
  "areas_for_improvement": [
    "FC algo elevada para ritmo tempo, considerar reducir 10 seg/km",
    "Necesitas más trabajo en zona 2 para base aeróbica"
  ],
  "injury_risk": "moderate",
  "injury_risk_factors": [
    "Aumento de volumen 15% respecto a semana anterior",
    "FC promedio 88% de FCmax (alto para distancia)"
  ],
  "recommendations": [
    "Próximo entrenamiento debe ser recuperación activa (zona 1-2)",
    "Añadir 2 días de entrenamiento de fuerza para prevenir lesiones",
    "Monitorizar HRV mañana - si <40ms, considera día off"
  ],
  "next_workout_suggestion": "Recuperación de 6-8 km a ritmo muy cómodo (>6:00 min/km), manteniendo FC <140 bpm. Enfocarte en cadencia y técnica."
}
```

---

## 🫀 Métricas de Salud

### Sincronización con Garmin

**Configuración Inicial:**

```
Usuario → Settings → Connect Garmin
          ↓
Frontend → POST /api/v1/health/connect-garmin
          Body: { email, password }
          ↓
Backend → 1. Validar credenciales con Garmin Connect
          2. Obtener tokens OAuth
          3. Guardar tokens en volumen persistente
          4. Actualizar user.has_garmin_sync = true
          5. Trigger sync inmediata
          ↓
Celery → sync_garmin_health_metrics(user_id)
          ↓
Backend → Guardar métricas en health_metrics table
          ↓
Frontend → Mostrar confirmación + datos sincronizados
```

**Datos Sincronizados:**

1. **Métricas Diarias:**
   - Frecuencia cardíaca en reposo
   - HRV (RMSSD en ms)
   - Nivel de estrés (0-100)
   - Body Battery (0-100, exclusivo Garmin)
   - Pasos totales
   - Pisos subidos
   - Calorías quemadas

2. **Métricas de Sueño:**
   - Duración total (horas)
   - Sueño profundo (horas)
   - Sueño ligero (horas)
   - REM (horas)
   - Tiempo despierto (horas)
   - Sleep Score (0-100)

### Visualización de Tendencias

**Gráficos en Dashboard de Salud:**

```tsx
// components/charts/HRVChart.tsx

interface HRVChartProps {
  data: HealthMetricOut[]
}

export function HRVChart({ data }: HRVChartProps) {
  // Preparar datos para Recharts
  const chartData = data.map(m => ({
    date: format(new Date(m.date), 'dd/MM'),
    hrv: m.hrv_rmssd,
    rhr: m.resting_heart_rate
  }))
  
  // Calcular promedio móvil de 7 días
  const moving_avg_7 = calculateMovingAverage(chartData, 7)
  
  return (
    <Card>
      <CardHeader>
        <CardTitle>HRV Trend (últimos 30 días)</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis yAxisId="left" label={{ value: 'HRV (ms)', angle: -90 }} />
            <YAxis yAxisId="right" orientation="right" label={{ value: 'RHR (bpm)', angle: 90 }} />
            <Tooltip />
            <Legend />
            <Line 
              yAxisId="left"
              type="monotone" 
              dataKey="hrv" 
              stroke="#8884d8" 
              strokeWidth={2}
              name="HRV"
            />
            <Line 
              yAxisId="left"
              type="monotone" 
              dataKey="moving_avg_7" 
              stroke="#82ca9d" 
              strokeDasharray="5 5"
              name="HRV (7-day avg)"
            />
            <Line 
              yAxisId="right"
              type="monotone" 
              dataKey="rhr" 
              stroke="#ffc658" 
              strokeWidth={2}
              name="RHR"
            />
          </LineChart>
        </ResponsiveContainer>
        
        {/* Interpretación automática */}
        <div className="mt-4 p-4 bg-blue-50 rounded-md">
          <p className="text-sm">
            {interpretHRVTrend(chartData)}
          </p>
        </div>
      </CardContent>
    </Card>
  )
}

function interpretHRVTrend(data: any[]): string {
  const recent_7 = data.slice(-7)
  const previous_7 = data.slice(-14, -7)
  
  const recent_avg = mean(recent_7.map(d => d.hrv))
  const previous_avg = mean(previous_7.map(d => d.hrv))
  
  const change_pct = ((recent_avg - previous_avg) / previous_avg) * 100
  
  if (change_pct > 5) {
    return "✅ Tu HRV ha mejorado un " + change_pct.toFixed(1) + "% en la última semana. Esto indica buena recuperación y adaptación al entrenamiento."
  } else if (change_pct < -5) {
    return "⚠️ Tu HRV ha bajado un " + Math.abs(change_pct).toFixed(1) + "% en la última semana. Considera reducir volumen o intensidad, y priorizar el descanso."
  } else {
    return "📊 Tu HRV se mantiene estable. Continúa monitoreando para detectar cambios tempranos en fatiga."
  }
}
```

### Alertas Inteligentes

**Condiciones que Disparan Alertas:**

```python
# backend/app/services/health_service.py

def check_health_alerts(user: User, recent_metrics: List[HealthMetric]) -> List[str]:
    alerts = []
    
    # Alerta 1: HRV bajo persistente
    hrv_values = [m.hrv_rmssd for m in recent_metrics[-7:] if m.hrv_rmssd]
    if hrv_values:
        user_baseline = calculate_hrv_baseline(user)  # Promedio de 30 días
        recent_avg = statistics.mean(hrv_values)
        
        if recent_avg < user_baseline * 0.85:
            alerts.append({
                "type": "warning",
                "title": "HRV Bajo",
                "message": f"Tu HRV ({recent_avg:.1f} ms) está 15% por debajo de tu baseline ({user_baseline:.1f} ms). Considera un día de descanso.",
                "action": "Reducir volumen o intensidad"
            })
    
    # Alerta 2: Nivel de estrés elevado
    stress_values = [m.stress_level for m in recent_metrics[-3:] if m.stress_level]
    if stress_values and statistics.mean(stress_values) > 60:
        alerts.append({
            "type": "warning",
            "title": "Estrés Elevado",
            "message": "Tu nivel de estrés ha sido alto en los últimos 3 días.",
            "action": "Priorizar sueño y técnicas de relajación"
        })
    
    # Alerta 3: Sueño insuficiente
    sleep_values = [m.sleep_duration_hours for m in recent_metrics[-7:] if m.sleep_duration_hours]
    if sleep_values and statistics.mean(sleep_values) < 7:
        alerts.append({
            "type": "info",
            "title": "Sueño Insuficiente",
            "message": f"Promedio de sueño esta semana: {statistics.mean(sleep_values):.1f} horas. Objetivo: 7-9 horas.",
            "action": "Ajustar rutina de sueño"
        })
    
    # Alerta 4: Body Battery bajo (Garmin)
    bb_values = [m.body_battery for m in recent_metrics[-3:] if m.body_battery]
    if bb_values and all(bb < 30 for bb in bb_values):
        alerts.append({
            "type": "critical",
            "title": "Body Battery Crítico",
            "message": "Tu Body Battery ha estado <30 durante 3 días consecutivos.",
            "action": "DÍA DE DESCANSO OBLIGATORIO"
        })
    
    return alerts
```

---

## 🗓️ Planes de Entrenamiento

### Wizard de Creación

**Pasos del Wizard:**

```
PASO 1: Objetivo
  ├─ Tipo de carrera: [Marathon 42K] [Half Marathon 21K] [10K] [5K]
  ├─ Fecha objetivo: [Date Picker]
  └─ Carrera específica: [Buscar en DB de carreras] (opcional)

PASO 2: Nivel Actual
  ├─ Fitness level: [Beginner] [Intermediate] [Advanced]
  ├─ Volumen semanal actual: [slider 0-100 km]
  ├─ VO2max: [auto desde perfil] o [manual input]
  └─ Ritmo umbral: [auto desde últimos workouts] o [manual]

PASO 3: Disponibilidad
  ├─ Días por semana: [3] [4] [5] [6] [7]
  ├─ Día de descanso preferido: [Lunes] [Martes] ... [Domingo]
  └─ Restricciones: [checkboxes: gym access, pista, montaña]

PASO 4: Preferencias
  ├─ Enfoque: [Velocidad] [Resistencia] [Balanceado]
  ├─ Incluir entrenamiento cruzado: [Sí] [No]
  └─ Incluir trabajo de fuerza: [Sí] [No]

PASO 5: Revisión
  ├─ Resumen de inputs
  ├─ Vista previa de estructura (semanas)
  └─ [Generar Plan con IA] button
```

### Generación con IA

**Prompt para Groq:**

```python
def generate_plan_prompt(wizard_data: dict, user: User) -> str:
    weeks_to_race = (wizard_data['target_date'] - date.today()).days // 7
    
    return f"""
Genera un plan de entrenamiento personalizado para running:

OBJETIVO:
- Carrera: {wizard_data['race_type']} ({wizard_data['distance_km']} km)
- Fecha: {wizard_data['target_date'].strftime('%d/%m/%Y')} ({weeks_to_race} semanas)
- Nombre de carrera: {wizard_data.get('race_name', 'N/A')}

ATLETA:
- Nivel: {wizard_data['fitness_level']}
- Volumen semanal actual: {wizard_data['current_weekly_km']} km
- VO2max: {user.vo2max}
- Ritmo umbral: {user.pace_threshold} min/km
- Edad: {user.age} años

DISPONIBILIDAD:
- Días de entrenamiento: {wizard_data['days_per_week']} días/semana
- Día de descanso: {wizard_data['rest_day']}

PREFERENCIAS:
- Enfoque: {wizard_data['focus']}
- Entrenamiento cruzado: {wizard_data['cross_training']}
- Trabajo de fuerza: {wizard_data['strength_training']}

ESTRUCTURA REQUERIDA (JSON):
{{
  "plan_name": "<nombre descriptivo>",
  "total_weeks": {weeks_to_race},
  "phases": [
    {{
      "name": "Base Building",
      "weeks": [1, 2, 3, 4],
      "focus": "Aumentar volumen aeróbico"
    }},
    {{
      "name": "Build",
      "weeks": [5, 6, 7, 8, 9, 10],
      "focus": "Introducir trabajo de velocidad"
    }},
    {{
      "name": "Peak",
      "weeks": [11, 12],
      "focus": "Trabajo específico de carrera"
    }},
    {{
      "name": "Taper",
      "weeks": [13, 14],
      "focus": "Reducir volumen, mantener intensidad"
    }}
  ],
  "weeks": [
    {{
      "week_number": 1,
      "total_km": <número>,
      "intensity_distribution": {{
        "easy": <porcentaje>,
        "moderate": <porcentaje>,
        "hard": <porcentaje>
      }},
      "workouts": [
        {{
          "day": "Monday",
          "type": "rest",
          "description": "Día de descanso completo"
        }},
        {{
          "day": "Tuesday",
          "type": "easy",
          "distance_km": 8,
          "target_pace": "5:45-6:00",
          "duration_min": 50,
          "description": "Carrera fácil de recuperación. Zona 2 (60-70% FCmax). Enfocarse en sensaciones, no en ritmo.",
          "notes": ["Calentar 10 min caminando/trotando", "Estiramientos después"]
        }},
        {{
          "day": "Wednesday",
          "type": "intervals",
          "distance_km": 10,
          "target_pace": "4:30 en series, 6:00 en recuperación",
          "duration_min": 60,
          "description": "Intervalos 6x800m con 2min recuperación activa",
          "warmup": "2 km trote suave + drills",
          "main_set": "6x800m a ritmo 5K (4:30/km) con 2min trote suave",
          "cooldown": "2 km trote suave + estiramientos",
          "notes": ["Si FC no baja <120 en recuperación, alargar descanso", "Parar si aparece dolor"]
        }},
        ... (resto de días)
      ]
    }},
    ... (resto de semanas)
  ],
  "key_workouts": [
    {{
      "week": 6,
      "day": "Saturday",
      "name": "First Long Run >20K",
      "importance": "Alta - Test de resistencia"
    }},
    {{
      "week": 12,
      "day": "Sunday",
      "name": "Race Pace Long Run",
      "importance": "Crítica - Simulación de carrera"
    }}
  ],
  "nutrition_tips": [
    "Semanas 1-4: Mantener ingesta normal, añadir snack post-workout",
    "Semanas 5-10: Aumentar carbohidratos en días de workout duro",
    "Semanas 11-12: Testar estrategia de nutrición de carrera en largos",
    "Semanas 13-14: Carb-loading 3 días antes de carrera"
  ],
  "injury_prevention": [
    "Sesión de fuerza 2x/semana: core, glúteos, isquios",
    "Foam rolling después de workouts duros",
    "Si HRV baja >10% del baseline, considerar día off",
    "Monitorear dolores: >3/10 en escala → visitar fisio"
  ]
}}

IMPORTANTE:
- Progresión de volumen: máx 10% por semana
- Incluir semana de descarga cada 3-4 semanas
- Último workout duro: 10 días antes de carrera
- Taper: reducir volumen 40% primera semana, 70% última semana
- Ritmos específicos según VO2max y umbral
"""
```

### Adaptación Dinámica

**Lógica de Adaptación:**

```python
# backend/app/services/plan_service.py

def adapt_plan(plan: TrainingPlan, user: User, db: Session) -> dict:
    """
    Adapta el plan según:
    1. Métricas de salud (HRV, sueño, estrés)
    2. Cumplimiento de entrenamientos
    3. Progreso de fitness (VO2max, ritmos)
    """
    
    # 1. Analizar métricas de salud (últimos 7 días)
    recent_metrics = db.query(HealthMetric).filter(
        HealthMetric.user_id == user.id,
        HealthMetric.date >= date.today() - timedelta(days=7)
    ).all()
    
    hrv_baseline = calculate_hrv_baseline(user, db)
    hrv_recent = statistics.mean([m.hrv_rmssd for m in recent_metrics if m.hrv_rmssd])
    hrv_ratio = hrv_recent / hrv_baseline
    
    fatigue_score = calculate_fatigue_score(recent_metrics)
    
    # 2. Analizar cumplimiento
    plan_data = json.loads(plan.plan_data)
    current_week = get_current_week(plan)
    completed_workouts = get_completed_workouts(plan, user, db)
    completion_rate = len(completed_workouts) / len(plan_data['weeks'][current_week]['workouts'])
    
    # 3. Decisión de adaptación
    adaptations = []
    
    if hrv_ratio < 0.85:
        # HRV muy bajo → reducir intensidad
        adaptations.append({
            "type": "reduce_intensity",
            "reason": f"HRV bajo ({hrv_recent:.1f} vs baseline {hrv_baseline:.1f})",
            "action": "Convertir workout de intervalos a carrera fácil",
            "affected_days": ["Wednesday"]
        })
    
    if fatigue_score > 70:
        # Fatiga alta → día extra de descanso
        adaptations.append({
            "type": "add_rest_day",
            "reason": f"Fatiga acumulada alta ({fatigue_score}/100)",
            "action": "Reemplazar carrera fácil del lunes con descanso activo o cross-training",
            "affected_days": ["Monday"]
        })
    
    if completion_rate < 0.7:
        # Bajo cumplimiento → simplificar plan
        adaptations.append({
            "type": "simplify_workouts",
            "reason": f"Cumplimiento bajo esta semana ({completion_rate*100:.0f}%)",
            "action": "Reducir volumen de próxima semana en 20%",
            "affected_weeks": [current_week + 1]
        })
    
    # 4. Aplicar adaptaciones y regenerar semanas afectadas
    if adaptations:
        apply_adaptations(plan_data, adaptations)
        plan.plan_data = json.dumps(plan_data)
        plan.updated_at = datetime.utcnow()
        db.commit()
    
    return {
        "adapted": len(adaptations) > 0,
        "adaptations": adaptations,
        "updated_plan": plan_data
    }
```

---

## 🏆 Base de Datos de Carreras

### Búsqueda Avanzada

**Filtros Disponibles:**

```tsx
// app/races/page.tsx

interface RaceFilters {
  query?: string              // Búsqueda de texto (nombre o ubicación)
  location?: string           // Ciudad específica
  date_from?: string          // YYYY-MM-DD
  date_to?: string            // YYYY-MM-DD
  distance_km?: number        // Distancia exacta
  min_distance?: number       // Distancia mínima
  max_distance?: number       // Distancia máxima
  region?: string             // Comunidad Autónoma
  verified?: boolean          // Solo carreras verificadas
}

export default function RacesPage() {
  const [filters, setFilters] = useState<RaceFilters>({
    verified: true,
    date_from: new Date().toISOString().split('T')[0]
  })
  
  const { data: races, isLoading } = useQuery({
    queryKey: ['races', filters],
    queryFn: async () => {
      const params = new URLSearchParams(filters as any)
      const { data } = await api.get(`/races/search?${params}`)
      return data
    }
  })
  
  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">🏁 Buscar Carreras</h1>
      
      {/* Filtros */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <Input 
          placeholder="Buscar por nombre o ubicación..."
          value={filters.query || ''}
          onChange={(e) => setFilters({...filters, query: e.target.value})}
        />
        
        <Select 
          value={filters.distance_km?.toString() || 'all'}
          onValueChange={(v) => setFilters({...filters, distance_km: v === 'all' ? undefined : Number(v)})}
        >
          <SelectTrigger>
            <SelectValue placeholder="Distancia" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Todas las distancias</SelectItem>
            <SelectItem value="5">5K</SelectItem>
            <SelectItem value="10">10K</SelectItem>
            <SelectItem value="21.0975">Media Maratón</SelectItem>
            <SelectItem value="42.195">Maratón</SelectItem>
          </SelectContent>
        </Select>
        
        <Input 
          type="date"
          value={filters.date_from || ''}
          onChange={(e) => setFilters({...filters, date_from: e.target.value})}
        />
        
        <Input 
          type="date"
          value={filters.date_to || ''}
          onChange={(e) => setFilters({...filters, date_to: e.target.value})}
        />
      </div>
      
      {/* Resultados */}
      {isLoading ? (
        <div>Cargando...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {races?.map((race) => (
            <RaceCard key={race.id} race={race} />
          ))}
        </div>
      )}
    </div>
  )
}
```

### Backend - Búsqueda con PostgreSQL

```python
# backend/app/services/events_service.py

from sqlalchemy import and_, or_, func
from sqlalchemy.orm import Session
from app.models import Event

class EventsService:
    def __init__(self, db: Session):
        self.db = db
    
    def search_races(
        self,
        query: Optional[str] = None,
        location: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        min_distance: Optional[float] = None,
        max_distance: Optional[float] = None,
        region: Optional[str] = None,
        verified: bool = True,
        limit: int = 100
    ) -> List[Event]:
        
        filters = [Event.verified == verified]
        
        # Filtro de fecha: solo futuras por defecto
        if not date_from:
            date_from = date.today()
        filters.append(Event.date >= date_from)
        
        if date_to:
            filters.append(Event.date <= date_to)
        
        # Búsqueda de texto (nombre o ubicación) con unaccent
        if query:
            search_filter = or_(
                func.unaccent(Event.name).ilike(f"%{unaccent_string(query)}%"),
                func.unaccent(Event.location).ilike(f"%{unaccent_string(query)}%")
            )
            filters.append(search_filter)
        
        # Ubicación específica
        if location:
            filters.append(func.unaccent(Event.location).ilike(f"%{unaccent_string(location)}%"))
        
        # Región
        if region:
            filters.append(Event.region == region)
        
        # Distancia
        if min_distance:
            filters.append(Event.distance_km >= min_distance)
        if max_distance:
            filters.append(Event.distance_km <= max_distance)
        
        # Query
        events = self.db.query(Event).filter(and_(*filters)).order_by(Event.date).limit(limit).all()
        
        return events
```

**Función auxiliar para búsqueda sin acentos:**

```python
def unaccent_string(s: str) -> str:
    """Normalizar string para búsqueda sin acentos"""
    import unicodedata
    return ''.join(
        c for c in unicodedata.normalize('NFD', s)
        if unicodedata.category(c) != 'Mn'
    )
```

### Admin - Gestión de Carreras

**Endpoints de Admin:**

```python
# backend/app/routers/events.py

@router.post("/admin/races", response_model=EventOut)
async def create_race(
    event_data: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    # TODO: añadir dependency is_admin
):
    """Crear nueva carrera (solo admin)"""
    service = EventsService(db)
    
    # Verificar que external_id sea único
    existing = db.query(Event).filter(Event.external_id == event_data.external_id).first()
    if existing:
        raise HTTPException(409, "Race with this ID already exists")
    
    # Crear evento
    event = Event(**event_data.dict())
    db.add(event)
    db.commit()
    db.refresh(event)
    
    return event

@router.put("/admin/races/{race_id}", response_model=EventOut)
async def update_race(
    race_id: str,
    event_data: EventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Actualizar carrera existente"""
    event = db.query(Event).filter(Event.external_id == race_id).first()
    if not event:
        raise HTTPException(404, "Race not found")
    
    # Actualizar campos
    for field, value in event_data.dict(exclude_unset=True).items():
        setattr(event, field, value)
    
    event.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(event)
    
    return event

@router.delete("/admin/races/{race_id}")
async def delete_race(
    race_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Eliminar carrera"""
    event = db.query(Event).filter(Event.external_id == race_id).first()
    if not event:
        raise HTTPException(404, "Race not found")
    
    db.delete(event)
    db.commit()
    
    return {"message": "Race deleted successfully"}

@router.get("/admin/stats")
async def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Estadísticas de base de datos"""
    total = db.query(Event).count()
    verified = db.query(Event).filter(Event.verified == True).count()
    future = db.query(Event).filter(Event.date >= date.today()).count()
    
    by_distance = db.query(
        Event.distance_km,
        func.count(Event.id).label('count')
    ).group_by(Event.distance_km).all()
    
    return {
        "total_races": total,
        "verified_races": verified,
        "future_races": future,
        "by_distance": {str(d): c for d, c in by_distance}
    }
```

---

## 🔄 Flujos de Usuario Completos

### Flujo 1: Nuevo Usuario → Primera Carrera

```
1. REGISTRO
   Usuario → /register
          → Email, password, nombre
          → Backend crea user + tokens JWT
          → Frontend guarda tokens en localStorage
          → Redirect a /dashboard

2. ONBOARDING (Primera vez en dashboard)
   Dashboard → Detecta perfil incompleto
            → Modal: "Completa tu perfil"
            → Campos: edad, peso, VO2max estimado
            → POST /auth/me con datos

3. CONECTAR GARMIN (Opcional)
   Settings → "Connect Garmin"
           → Modal con email/password de Garmin
           → POST /health/connect-garmin
           → Backend autentica y guarda tokens
           → Celery task: sync inmediata
           → 731 métricas sincronizadas
           → Dashboard muestra gráficos de HRV/sueño

4. BUSCAR CARRERA OBJETIVO
   Menú → "Carreras"
       → Filtrar: "Maratón", "Madrid", "Abril 2026"
       → Resultados: Rock 'n' Roll Madrid Marathon
       → Click "Ver Detalles"
       → Modal con info completa
       → Button: "Crear Plan para esta Carrera"

5. WIZARD DE PLAN
   Step 1 → Objetivo ya pre-seleccionado (Marathon 42K, 26/04/2026)
   Step 2 → Nivel: Intermediate
          → Volumen actual: 40 km/semana
          → VO2max: 50 (auto desde perfil)
   Step 3 → 5 días/semana
          → Descanso: Lunes
   Step 4 → Enfoque: Balanceado
          → Cross-training: No
          → Fuerza: Sí
   Step 5 → Revisión
          → "Generar Plan con IA"
          → Loading (llamada a Groq, ~10 seg)
          → Plan creado con 16 semanas

6. VER PLAN GENERADO
   /plans/1 → Vista de plan completo
           → Estructura por fases
           → Semana 1 desplegada con 5 workouts
           → Botón "Iniciar Plan"

7. ENTRENAR Y ANALIZAR
   Semana 1, Martes → "Carrera fácil 8 km"
                   → Usuario sale a correr con Garmin
                   → Al volver: exportar GPX desde Garmin Connect
                   
   /workouts → "Upload Workout"
            → Seleccionar archivo .gpx
            → POST /workouts/upload
            → Backend parsea y guarda
            → Celery task: análisis IA
            → Loading 5 seg
            → Análisis completo visible
            → "Tipo: Easy Run, Calidad: 8/10"
            → Recomendaciones específicas

8. MONITOREO DE SALUD
   Cada mañana → Celery Beat sync Garmin (7 AM UTC)
              → Nuevas métricas en dashboard
              → Si HRV < baseline:
                 → Alerta en dashboard
                 → "Considera reducir intensidad hoy"

9. ADAPTACIÓN DE PLAN (Semana 5)
   /plans/1 → Button "Adaptar Plan"
           → Backend analiza:
              - HRV: estable
              - Cumplimiento: 90%
              - Progreso: VO2max +1
           → "Plan está óptimo, continuar como está"
           
   (Escenario alternativo: HRV baja)
           → "HRV bajo detectado"
           → Adaptaciones propuestas:
              - Reemplazar intervalos con fácil
              - Añadir día de descanso
           → Usuario acepta
           → Plan actualizado

10. CARRERA (26 de Abril)
    Día de carrera → Upload actividad después
                  → Análisis: "Race Performance"
                  → Comparar con tiempos objetivo
                  → Celebrar logro 🎉
                  → Sugerencia: "Plan de recuperación post-maratón"
```

### Flujo 2: Usuario Avanzado → Optimización

```
1. USUARIO CON HISTORIAL
   - 50 workouts en últimos 6 meses
   - Garmin conectado (2 años de datos)
   - VO2max: 58 (alto)
   - Ritmo umbral: 3:50 min/km

2. ANÁLISIS AUTOMÁTICO DE TENDENCIAS
   Dashboard → Sección "AI Insights"
            → "Tu VO2max ha mejorado +3 en 3 meses"
            → "HRV muestra buen equilibrio carga/recuperación"
            → "Volumen semanal estable: 70±5 km"
            → "Sugerencia: Incorporar más trabajo de velocidad (zona 5)"

3. CREAR PLAN AVANZADO
   Wizard → Objetivo: Ultra Trail 50K montaña
         → Nivel: Advanced
         → Volumen actual: 70 km/semana
         → Días: 6/semana
         → Enfoque: Resistencia + elevación
         → Plan generado: 20 semanas
            - Fase 1: Base aeróbica (4 sem)
            - Fase 2: Fuerza específica + vertical (8 sem)
            - Fase 3: Trabajo en terreno técnico (6 sem)
            - Fase 4: Taper (2 sem)

4. ANÁLISIS DETALLADO POST-WORKOUT
   Upload GPX de entrenamiento en montaña:
   - Distancia: 25 km
   - Desnivel: +1200m / -1200m
   - Duración: 3h 15min
   
   Análisis IA:
   - "Excelente gestión de ritmo en subidas"
   - "Distribución de esfuerzo: 70% Z2, 20% Z3, 10% Z4"
   - "Cadencia baja en bajadas (150 spm), trabajar técnica"
   - "FC recuperación post-subidas: buena (60 seg a Z2)"
   - "Riesgo lesión: BAJO - técnica sólida"

5. MONITOREO AVANZADO
   Health Dashboard → Correlaciones automáticas:
   - "HRV vs Volumen semanal" (gráfico scatter)
   - "Sleep Score vs Performance" (correlación 0.72)
   - "Stress Level predictivo de sobreentrenamiento"
   
   Alertas inteligentes:
   - "FC en reposo +5 bpm vs baseline → posible fatiga"
   - "Body Battery <50 durante 5 días → revisar carga"

6. EXPORT Y COMPARTIR
   /workouts/123 → "Export to PDF"
                → Descarga informe completo
                → Compartir con entrenador
                
   /plans/5 → "Share Plan"
           → Genera link público (read-only)
           → Otros usuarios pueden ver estructura
```

---

## 📐 Arquitectura de Datos

### Flujo de Datos Completo

```
┌─────────────────────────────────────────────────────────────────┐
│                         USUARIO (Browser)                        │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                    ┌───────┴───────┐
                    │               │
              [Interacción]    [Visualización]
                    │               │
          ┌─────────▼─────────┐    │
          │  Frontend (React) │    │
          │  ┌──────────────┐ │    │
          │  │ Zustand Store│ │    │
          │  │ (Auth State) │ │    │
          │  └──────────────┘ │    │
          │  ┌──────────────┐ │    │
          │  │ React Query  │ │    │
          │  │ (Data Cache) │ │    │
          │  └──────────────┘ │    │
          └─────────┬─────────┘    │
                    │               │
            [REST API Calls]        │
                    │               │
          ┌─────────▼─────────────────────────────┐
          │      Backend (FastAPI)                │
          │  ┌────────────────────────────────┐   │
          │  │ Routers (Endpoints)            │   │
          │  │ /auth, /workouts, /plans, etc. │   │
          │  └────────┬───────────────────────┘   │
          │           │                            │
          │  ┌────────▼───────────────────────┐   │
          │  │ Services (Business Logic)      │   │
          │  │ - WorkoutService               │   │
          │  │ - PlanService                  │   │
          │  │ - HealthService                │   │
          │  │ - EventsService                │   │
          │  │ - GarminService                │   │
          │  └────────┬───────────────────────┘   │
          │           │                            │
          │  ┌────────▼───────────────────────┐   │
          │  │ ORM (SQLAlchemy Models)        │   │
          │  └────────┬───────────────────────┘   │
          └───────────┼────────────────────────────┘
                      │
          ┌───────────▼───────────────────────────┐
          │    PostgreSQL (Database)              │
          │  ┌─────────────────────────────────┐  │
          │  │ users                           │  │
          │  ├─────────────────────────────────┤  │
          │  │ workouts                        │  │
          │  ├─────────────────────────────────┤  │
          │  │ health_metrics                  │  │
          │  ├─────────────────────────────────┤  │
          │  │ training_plans                  │  │
          │  ├─────────────────────────────────┤  │
          │  │ events (carreras)               │  │
          │  └─────────────────────────────────┘  │
          └───────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                 TAREAS ASÍNCRONAS (Celery)                       │
├─────────────────────────────────────────────────────────────────┤
│  Celery Beat (Scheduler)                                         │
│    ├─ 7:00 AM UTC: sync_all_garmin_users()                      │
│    └─ 8:00 PM UTC: sync_all_garmin_users()                      │
│                                                                  │
│  Celery Worker (Executor)                                        │
│    ├─ analyze_workout_async(workout_id)                         │
│    ├─ generate_plan_async(user_id, plan_id)                     │
│    └─ sync_garmin_health_metrics(user_id)                       │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    SERVICIOS EXTERNOS                            │
├─────────────────────────────────────────────────────────────────┤
│  Groq API (IA)                                                   │
│    ├─ Análisis de entrenamientos                                │
│    └─ Generación de planes                                      │
│                                                                  │
│  Garmin Connect (OAuth)                                          │
│    ├─ Autenticación                                             │
│    └─ Sincronización de métricas                                │
└─────────────────────────────────────────────────────────────────┘
```

---

**Última actualización:** 8 de enero de 2026  
**Versión:** 3.0
