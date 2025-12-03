# 📚 REPASO EXHAUSTIVO - RunCoach AI Platform
## Para Developer Junior (o cualquiera que NO entienda nada del proyecto)

**Última actualización**: Diciembre 2025  
**Duración estimada de lectura**: 45-60 minutos  
**Nivel**: Principiante (pero completo y técnico)

---

# ÍNDICE COMPLETO

1. [¿Qué es RunCoach AI?](#1-qué-es-runcoach-ai)
2. [Problema & Solución](#2-problema--solución)
3. [Stack Tecnológico (Explicado Simple)](#3-stack-tecnológico-explicado-simple)
4. [Arquitectura del Sistema](#4-arquitectura-del-sistema)
5. [Base de Datos: Tablas y Relaciones](#5-base-de-datos-tablas-y-relaciones)
6. [Backend: Cómo Funciona](#6-backend-cómo-funciona)
7. [Frontend: Cómo Funciona](#7-frontend-cómo-funciona)
8. [Flujos Completos Paso a Paso](#8-flujos-completos-paso-a-paso)
9. [Sistemas Complejos Explicados](#9-sistemas-complejos-explicados)
10. [Estado Real del Proyecto](#10-estado-real-del-proyecto)

---

# 1️⃣ ¿QUÉ ES RUNCOACH AI?

## Definición Ultra Simple

**RunCoach AI** es una **aplicación web para corredores** que funciona como tu "entrenador personal de running" usando IA.

### Lo que HACE:
- ✅ **Crea planes de entrenamiento** automáticos basados en tus objetivos
- ✅ **Sincroniza tus entrenamientos** desde Garmin, Strava, etc. (sin copiar/pegar)
- ✅ **Analiza tus métricas** (ritmo, frecuencia cardíaca, distancia)
- ✅ **Da recomendaciones** personalizadas usando IA (Llama 3.3)
- ✅ **Detecta sobreentrenamiento** analizando patrones de fatiga
- ✅ **Mantiene un historial** de todos tus entrenamientos

### Lo que NO HACE:
- ❌ No es un rastreador GPS (eso lo hace tu reloj)
- ❌ No reemplaza a un entrenador humano (es complementario)
- ❌ No funciona sin internet
- ❌ No tiene app móvil nativa (aún)

### ¿A quién le sirve?
- Corredores principiantes que no saben cómo entrenar
- Corredores competitivos preparando una carrera
- Cualquiera que tenga Garmin, Strava u otro dispositivo
- Gente que quiere análisis y recomendaciones personalizadas

---

# 2️⃣ PROBLEMA & SOLUCIÓN

## El Problema Real

Imagina que eres corredor. Cada día enfrentas estos problemas:

```
PROBLEMA 1: Sin estructura
├─ ¿A qué ritmo debo correr hoy?
├─ ¿Cuántos km debo hacer?
├─ ¿Estoy entrenando bien para mi maratón?
└─ Sin plan = entrenamiento caótico

PROBLEMA 2: Datos dispersos
├─ Entrenamientos en Garmin
├─ Otros en Strava
├─ Histórico en Apple Watch
└─ Todo en diferentes apps, sin coherencia

PROBLEMA 3: Datos que no entienden
├─ "Hice 10km en 50 minutos"
├─ "¿Eso está bien?"
├─ ¿Cómo compare con mis entrenamientos pasados?
└─ Sin análisis = sin insight

PROBLEMA 4: Sin feedback personalizado
├─ Un plan genérico de internet no es mío
├─ No considero mis lesiones, fatiga, disponibilidad
└─ Necesito coaching personalizado (pero cuesta $$$)

PROBLEMA 5: Sobreentrenamiento silencioso
├─ Aumento frecuencia cardíaca en reposo = fatiga
├─ Bajo HRV (variabilidad) = mala recuperación
├─ Pero no lo noto hasta que es tarde
└─ Necesito alertas de sobreentrenamiento
```

## La Solución: RunCoach AI

```
SOLUCIÓN 1: Plan personalizado
├─ IA genera plan específico para TI
├─ Basado en tus objetivos, historial, disponibilidad
└─ Se adapta conforme entrenas

SOLUCIÓN 2: Sincronización automática
├─ Conectas Garmin/Strava UNA VEZ
├─ Luego TODO se sincroniza automáticamente
├─ Todos tus datos en UN solo lugar
└─ Coherencia garantizada

SOLUCIÓN 3: Análisis inteligente
├─ Sistema analiza cada entrenamiento
├─ Compara con tu historial
├─ Proporciona insights accionables
└─ "Hiciste buen trabajo, pero necesitas más descanso"

SOLUCIÓN 4: Coaching IA 24/7
├─ Chat con "entrenador" basado en Llama 3.3
├─ Responde tus preguntas sobre entrenamiento
├─ Genera recomendaciones personalizadas
└─ Sin costo de entrenador humano

SOLUCIÓN 5: Detección de sobreentrenamiento
├─ Monitorea HR en reposo, HRV, patrones
├─ Te ALERTA antes de quemarte
├─ Sugiere reducir intensidad si es necesario
└─ Previene lesiones por fatiga
```

---

# 3️⃣ STACK TECNOLÓGICO (EXPLICADO SIMPLE)

## ¿Qué es el "Stack"?

"Stack" = Las tecnologías que usamos. Como los ingredientes de una receta.

```
RECETA DE RUNCOACH AI:

INGREDIENTE 1: Frontend (Lo que ves en pantalla)
├─ Next.js 16 (marco para construir páginas)
├─ React 19 (componentes reutilizables)
├─ TypeScript (JavaScript más seguro)
├─ Tailwind CSS (estilos bonitos)
└─ Shadcn UI (componentes pre-diseñados)
   RESULTADO: Interfaz moderna, rápida, responsive

INGREDIENTE 2: Backend (El "cerebro" que procesa)
├─ FastAPI (framework web Python)
├─ Python 3.13 (lenguaje de programación)
├─ SQLAlchemy (para hablar con la BD)
├─ Pydantic (valida que los datos sean correctos)
└─ JWT (seguridad: tokens)
   RESULTADO: API rápida, segura, con auto-documentación

INGREDIENTE 3: Base de datos (Donde guardamos todo)
├─ SQLite (desarrollo local)
└─ PostgreSQL (producción en la nube)
   RESULTADO: Datos persistentes, seguros, estructurados

INGREDIENTE 4: IA (El coach inteligente)
├─ Groq API (servicio en la nube)
└─ Llama 3.3 70B (modelo de lenguaje)
   RESULTADO: Análisis y recomendaciones personalizadas

INGREDIENTE 5: Deployment (Publicar en internet)
├─ Vercel (frontend en producción)
└─ Render (backend en producción)
   RESULTADO: App accesible 24/7 desde cualquier parte
```

## ¿Por Qué Estas Tecnologías?

### Frontend: Next.js + React
```
ALTERNATIVAS posibles:
- Vue.js (más simple, menos popular)
- Angular (muy complejo para esto)
- Svelte (muy nuevo)

¿POR QUÉ NEXT.JS?
✅ Combina React (componentes) + Node (backend)
✅ Server-Side Rendering (SSR) = mejor SEO
✅ Turbopack = muy rápido
✅ Deployment fácil en Vercel
✅ Comunidad gigante
✅ Production-ready
```

### Backend: FastAPI + Python
```
ALTERNATIVAS:
- Node.js/Express (JavaScript todo)
- Django (Python, más lento, overengineering)
- Go (muy diferente, menos popular para startups)
- Java (pesado, overkill)

¿POR QUÉ FASTAPI?
✅ Muy rápido (benchmarks vs Django, Flask)
✅ Auto-documentación (/docs - Swagger)
✅ Validación built-in (Pydantic)
✅ Async/await (operaciones lentas no bloquean)
✅ Python = ciencia de datos / IA fácil
✅ Fácil de aprender
```

### BD: SQLite + PostgreSQL
```
ESTRATEGIA:
- DESARROLLO: SQLite (local, archivo, sin servidor)
- PRODUCCIÓN: PostgreSQL (profesional, escalable)

¿POR QUÉ?
✅ SQLite: Rápido para desarrollar, file-based
✅ PostgreSQL: Estándar industria, confiable, open-source
✅ Fácil migración: mismo SQL
```

### IA: Groq API + Llama 3.3
```
OPCIONES:
- OpenAI (ChatGPT): caro, lento, overkill
- Anthropic (Claude): caro
- Google Gemini: mediano precio
- Meta Llama via Groq: RÁPIDO, BARATO, OPEN

¿POR QUÉ GROQ?
✅ Llama 3.3 70B = muy bueno, open-source
✅ Groq = optimizado para VELOCIDAD
✅ Precio: 10x más barato que OpenAI
✅ Latencia ultra baja (perfecto para streaming)
```

---

# 4️⃣ ARQUITECTURA DEL SISTEMA

## Diagrama General

```
┌─────────────────────────────────────────────────────────────┐
│                    USUARIO EN NAVEGADOR                      │
│                  http://localhost:3001                       │
└─────────────────────────────────────────────────────────────┘
                              │
                   Frontend (Next.js/React)
                              │
                    ┌─────────┴─────────┐
                    │                   │
           HTTP Requests        WebSocket Streaming
           (REST API)           (AI Coach en vivo)
                    │                   │
                    ↓                   ↓
┌─────────────────────────────────────────────────────────────┐
│             BACKEND API (FastAPI, puerto 3000)              │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Routers (endpoints)                                    │ │
│  ├─ /auth (registro, login)                              │ │
│  ├─ /workouts (entrenamientos)                           │ │
│  ├─ /training-plans (planes de entrenamiento)            │ │
│  ├─ /garmin (sincronizar Garmin)                         │ │
│  ├─ /strava (sincronizar Strava)                         │ │
│  ├─ /coach (análisis IA)                                 │ │
│  ├─ /hrv (análisis HRV)                                  │ │
│  ├─ /overtraining (detección sobreentrenamiento)         │ │
│  └─ ... (más endpoints)                                  │ │
│  └────────────────────────────────────────────────────────┘ │
│           │                          │                       │
│           ↓                          ↓                       │
│  ┌────────────────────┐   ┌──────────────────────────────┐ │
│  │ Services (lógica)  │   │ External APIs                │ │
│  ├─ coach_service    │   ├─ Groq API (IA)               │ │
│  ├─ training_plan... │   ├─ Garmin Connect              │ │
│  ├─ hrv_analysis...  │   ├─ Strava API                  │ │
│  ├─ overtraining...  │   └─ Google Fit, Apple Health    │ │
│  └─ garmin_service   │                                   │ │
│  └────────────────────┘   └──────────────────────────────┘ │
│           │                                                 │
│           ↓                                                 │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ SQLAlchemy ORM + Pydantic Schemas                      │ │
│  │ (Interfaz con base de datos)                          │ │
│  └────────────────────────────────────────────────────────┘ │
│           │                                                 │
│           ↓                                                 │
└─────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
              DESARROLLO         PRODUCCIÓN
                    │                   │
            ┌───────↓────────┐  ┌──────↓──────────┐
            │ SQLite         │  │ PostgreSQL      │
            │ (archivo local)│  │ (Render.com)    │
            └────────────────┘  └─────────────────┘
```

## Flujo de una Request (Paso a Paso)

### Ejemplo: Usuario crea un plan de entrenamiento

```
PASO 1: Usuario abre navegador
   URL: http://localhost:3001
   ↓

PASO 2: El frontend (Next.js) carga y muestra la página
   ├─ HTML + CSS + JavaScript
   ├─ React componentes se cargan
   └─ Estado = esperando acciones del usuario
   ↓

PASO 3: Usuario hace click en "Crear Plan"
   ├─ Event: onClick del botón
   ├─ JavaScript ejecuta función handleCreatePlan()
   └─ Se abre modal/formulario
   ↓

PASO 4: Usuario completa el formulario
   ├─ Objetivo: Maratón
   ├─ Fecha objetivo: 15 de Mayo 2025
   ├─ Duración: 16 semanas
   └─ Click en "Generar"
   ↓

PASO 5: Frontend prepara datos y los ENVÍA
   ├─ Método: POST
   ├─ URL: http://localhost:3000/api/v1/training-plans/generate
   ├─ Datos enviados (JSON):
   │  {
   │    "goal_type": "marathon",
   │    "goal_date": "2025-05-15T00:00:00Z",
   │    "current_weekly_km": 40,
   │    "weeks": 16,
   │    "notes": "Tengo rodilla sensible"
   │  }
   ├─ Headers incluyen: Authorization: Bearer <JWT_TOKEN>
   └─ Frontend muestra: "Generando plan..."
   ↓

PASO 6: Backend RECIBE la request
   ├─ FastAPI router @app.post("/training-plans/generate")
   ├─ Pydantic valida los datos
   │  └─ ¿goal_date es válido? ✓
   │  └─ ¿weeks entre 4-24? ✓
   │  └─ ¿current_weekly_km >= 0? ✓
   ├─ Extrae user_id del JWT token
   └─ ✓ TODO validado, continuamos
   ↓

PASO 7: Backend ejecuta lógica de negocio
   ├─ Busca al usuario en la BD: SELECT * FROM users WHERE id = 5
   ├─ Obtiene histórico de entrenamientos: SELECT * FROM workouts WHERE user_id = 5
   ├─ Calcula fitness actual (distancia, ritmo, etc.)
   ├─ Calcula zonas cardíacas usando Karvonen formula
   │  ├─ FC Máxima = 220 - edad = 220 - 35 = 185
   │  ├─ FC Reposo = 60 (del perfil)
   │  ├─ FC Reserva = 185 - 60 = 125
   │  ├─ Zona 2: 60 + (125 × 0.65) = 141 bpm
   │  └─ (calcula todas 7 zonas)
   └─ Construye el contexto para IA
   ↓

PASO 8: Backend LLAMA a IA (Groq/Llama 3.3)
   ├─ Groq API endpoint: https://api.groq.com/openai/v1/chat/completions
   ├─ Prompt enviado:
   │  "Genera plan de 16 semanas para maratón
   │   Usuario: 35 años, 75kg, nivel intermedio
   │   Histórico: 40 km/semana en últimas 4 semanas
   │   Objetivo: Terminar maratón
   │   Limitaciones: Rodilla sensible
   │   
   │   Formato JSON con semanas, entrenamientos, ritmos, etc."
   ├─ Groq procesa (típicamente 2-5 segundos)
   └─ Devuelve plan en JSON
   ↓

PASO 9: Backend procesa respuesta de IA
   ├─ Valida que JSON sea válido
   ├─ Extrae semanas, entrenamientos, etc.
   ├─ Calcula "compatibilidad" con perfil del usuario
   └─ ✓ Listo para guardar
   ↓

PASO 10: Backend GUARDA en base de datos
   ├─ Prepara: INSERT INTO training_plans ...
   ├─ Datos guardados:
   │  ├─ user_id = 5
   │  ├─ plan_type = "marathon"
   │  ├─ target_date = 2025-05-15
   │  ├─ duration_weeks = 16
   │  ├─ plan_content = {JSON completo del plan}
   │  ├─ created_at = now()
   │  └─ status = "active"
   ├─ Ejecuta query
   ├─ Base de datos confirma: ✓ Insertado con ID = 42
   └─ Backend recupera el plan (para devolver al cliente)
   ↓

PASO 11: Backend ENVÍA respuesta al frontend
   ├─ Status code: 200 OK
   ├─ Response JSON:
   │  {
   │    "id": 42,
   │    "plan_type": "marathon",
   │    "target_date": "2025-05-15",
   │    "duration_weeks": 16,
   │    "status": "active",
   │    "weeks": [
   │      {
   │        "week": 1,
   │        "focus": "Base aeróbica",
   │        "total_km": 35,
   │        "workouts": [...]
   │      },
   │      ...
   │    ]
   │  }
   └─ Toma ~500ms total
   ↓

PASO 12: Frontend RECIBE respuesta
   ├─ JavaScript recibe JSON
   ├─ React actualiza el estado (useState)
   ├─ Componentes se re-renderizan
   └─ "Generando plan..." desaparece
   ↓

PASO 13: Frontend MUESTRA el plan al usuario
   ├─ Renderiza tabla con semanas
   ├─ Cada semana con sus entrenamientos
   ├─ Colores, gráficos, ritmos
   ├─ Botones: "Guardar", "Descargar", "Editar"
   └─ ✅ ÉXITO: Usuario ve su plan personalizado

TIEMPO TOTAL: ~2-6 segundos (dependiendo de latencia IA)
```

---

# 5️⃣ BASE DE DATOS: TABLAS Y RELACIONES

## Estructura de Tablas

### Tabla: USERS (Usuarios)

```sql
CREATE TABLE users (
  -- Identificación
  id INTEGER PRIMARY KEY,
  name STRING,
  email STRING UNIQUE,
  hashed_password STRING,
  created_at DATETIME,
  
  -- Perfil del atleta
  height_cm FLOAT,
  weight_kg FLOAT,
  running_level STRING,  -- "beginner", "intermediate", "advanced"
  max_heart_rate INTEGER,
  
  -- Configuración
  onboarding_completed BOOLEAN,
  primary_device STRING,  -- "garmin", "strava", "apple", etc
  use_case STRING,        -- "fitness_tracker", "training_coach", "race_prep"
  language STRING,        -- "es", "en", "fr"
  enable_notifications BOOLEAN,
  
  -- Garmin Connect integración
  garmin_email STRING,
  garmin_token STRING,  -- encrypted
  last_garmin_sync DATETIME,
  
  -- Strava integración
  strava_athlete_id INTEGER,
  strava_access_token STRING,
  strava_refresh_token STRING,
  last_strava_sync DATETIME,
  
  -- Datos en JSON (flexible)
  hr_zones JSON,  -- [{"zone": 1, "min": 100, "max": 130}, ...]
  power_zones JSON,
  goals JSON,     -- [{"name": "sub-40 10K", "deadline": "2025-12-31"}, ...]
  preferences JSON,  -- {"music": true, "time_of_day": "evening"}
  injuries JSON,
  device_sync_config JSON
);

EJEMPLO DE FILA:
{
  id: 5,
  name: "Juan García",
  email: "juan@example.com",
  hashed_password: "$2b$12$...",
  created_at: 2025-01-15,
  height_cm: 180,
  weight_kg: 75,
  running_level: "intermediate",
  max_heart_rate: 185,
  onboarding_completed: true,
  primary_device: "garmin",
  hr_zones: [
    {"zone": 1, "min": 100, "max": 130},
    {"zone": 2, "min": 130, "max": 155},
    ...
  ],
  goals: [
    {"name": "Maratón Madrid", "deadline": "2025-05-15", "type": "race"}
  ]
}
```

### Tabla: WORKOUTS (Entrenamientos)

```sql
CREATE TABLE workouts (
  -- Identificación
  id INTEGER PRIMARY KEY,
  user_id INTEGER FOREIGN KEY,  -- ¿De quién es este entrenamiento?
  
  -- Datos básicos
  sport_type STRING,  -- "running", "cycling"
  start_time DATETIME,
  duration_seconds INTEGER,
  distance_meters FLOAT,
  
  -- Métricas cardíacas
  avg_heart_rate INTEGER,
  max_heart_rate INTEGER,
  
  -- Rendimiento
  avg_pace FLOAT,  -- min/km
  max_speed FLOAT,  -- km/h
  calories FLOAT,
  elevation_gain FLOAT,
  
  -- Métrica de running (análisis de forma)
  avg_cadence FLOAT,      -- pasos por minuto
  avg_stance_time FLOAT,  -- ms (tiempo apoyado en tierra)
  avg_vertical_oscillation FLOAT,  -- cm (cuánto rebotas)
  avg_leg_spring_stiffness FLOAT,
  left_right_balance FLOAT,  -- % (50 = perfectamente balanceado)
  
  -- Metadatos
  source_type STRING,  -- "garmin_fit", "strava", "gpx_upload", "tcx_upload"
  data_quality STRING,  -- "high", "medium", "basic"
  file_name STRING,
  created_at DATETIME
);

EJEMPLO DE FILA (entrenamiento real):
{
  id: 1042,
  user_id: 5,
  sport_type: "running",
  start_time: 2025-12-03 07:15:00,
  duration_seconds: 3600,  -- 1 hora
  distance_meters: 10000,  -- 10km
  avg_heart_rate: 155,
  max_heart_rate: 172,
  avg_pace: 6.0,  -- 6 min/km
  max_speed: 12.5,  -- km/h
  calories: 650,
  elevation_gain: 45,
  avg_cadence: 175,
  source_type: "garmin_fit",
  data_quality: "high",
  created_at: 2025-12-03 08:30:00
}
```

### Tabla: HEALTH_METRICS (Métricas de Salud Diarias)

```sql
CREATE TABLE health_metrics (
  -- Identificación
  id INTEGER PRIMARY KEY,
  user_id INTEGER FOREIGN KEY,
  date DATE,  -- Una métrica por usuario por día
  
  -- Métricas de recuperación
  hrv_ms FLOAT,              -- Heart Rate Variability en ms (alto = bueno)
  resting_hr_bpm INTEGER,    -- FC en reposo (bajo = bueno)
  hrv_baseline_ms FLOAT,     -- Media de últimos 7 días
  resting_hr_baseline_bpm INTEGER,
  
  -- Sueño
  sleep_hours FLOAT,
  sleep_quality STRING,  -- "poor", "fair", "good", "excellent"
  
  -- Estrés y recuperación
  stress_level INTEGER,  -- 1-10
  readiness_score INTEGER,  -- 1-100 (100 = perfectamente recuperado)
  
  -- Síntomas
  muscle_soreness INTEGER,  -- 1-10
  fatigue_level INTEGER,  -- 1-10
  
  -- Datos opcionales de dispositivo
  body_battery INTEGER,  -- Garmin metric (0-100)
  sp02 FLOAT,  -- Saturación de oxígeno %
  
  created_at DATETIME
);

EJEMPLO (día típico):
{
  id: 9234,
  user_id: 5,
  date: 2025-12-03,
  hrv_ms: 45,  -- Normal
  resting_hr_bpm: 58,
  hrv_baseline_ms: 55,
  resting_hr_baseline_bpm: 58,
  sleep_hours: 7.5,
  sleep_quality: "good",
  stress_level: 3,
  readiness_score: 78,
  muscle_soreness: 2,
  fatigue_level: 2,
  body_battery: 82
}
```

### Tabla: TRAINING_PLANS (Planes de Entrenamiento)

```sql
CREATE TABLE training_plans (
  -- Identificación
  id INTEGER PRIMARY KEY,
  user_id INTEGER FOREIGN KEY,
  
  -- Definición del plan
  plan_type STRING,  -- "marathon", "10k", "5k", "fitness", "base_building"
  target_date DATE,
  duration_weeks INTEGER,
  status STRING,  -- "draft", "active", "completed", "abandoned"
  
  -- Contenido del plan (JSON porque es flexible)
  plan_content JSON,  -- {weeks: [{week: 1, focus: "...", workouts: [...]}]}
  
  -- Adaptaciones
  adaptations JSON,  -- Cambios que el usuario ha hecho
  user_feedback JSON,  -- Cómo le ha ido al usuario
  
  -- Meta info
  created_at DATETIME,
  last_modified DATETIME,
  completion_percentage FLOAT  -- 0-100%
);

EJEMPLO (contenido simplificado):
{
  id: 42,
  user_id: 5,
  plan_type: "marathon",
  target_date: 2025-05-15,
  duration_weeks: 16,
  status: "active",
  plan_content: {
    "weeks": [
      {
        "week": 1,
        "focus": "Base aeróbica",
        "total_km": 35,
        "workouts": [
          {
            "day": "Monday",
            "type": "easy",
            "distance_km": 8,
            "duration_min": 55,
            "pace_min_per_km": "6:00-6:30",
            "heart_rate_zone": "Zone 2"
          },
          ...
        ]
      },
      ...
    ]
  }
}
```

### Tabla: CHAT_MESSAGES (Historial de Chat con IA)

```sql
CREATE TABLE chat_messages (
  id INTEGER PRIMARY KEY,
  user_id INTEGER FOREIGN KEY,
  role STRING,  -- "user" o "assistant"
  content STRING,  -- El mensaje
  tokens_used INTEGER,  -- Cuántos tokens costó (solo para assistant)
  created_at DATETIME
);

EJEMPLO:
{
  id: 5321,
  user_id: 5,
  role: "user",
  content: "¿Por qué mi FC en reposo sube cada día?",
  created_at: 2025-12-03 20:15:00
},
{
  id: 5322,
  user_id: 5,
  role: "assistant",
  content: "Tu FC en reposo está subiendo porque posiblemente estés acumulando fatiga. 
            He analizado tus últimos 7 entrenamientos y veo que:
            - 3 fueron de alta intensidad (Zona 4-5)
            - Dormiste menos de 7h durante 4 noches
            - Tu HRV bajó 18% comparado a hace una semana
            
            RECOMENDACIÓN: Haz entrenamiento ligero (Zona 1-2) en los próximos 3 días.",
  tokens_used: 145,
  created_at: 2025-12-03 20:15:05
}
```

## Relaciones Entre Tablas

```
USERS (1) ────→ (N) WORKOUTS
  id                 user_id
  
  Un usuario puede tener muchos entrenamientos
  Ejemplo: Juan tiene 245 entrenamientos guardados

USERS (1) ────→ (N) HEALTH_METRICS
  id                 user_id
  
  Un usuario tiene una métrica de salud por día
  Ejemplo: Juan tiene datos de 90 días

USERS (1) ────→ (N) TRAINING_PLANS
  id                 user_id
  
  Un usuario puede tener muchos planes
  Ejemplo: Juan tiene 5 planes (activos, completados, abandonados)

USERS (1) ────→ (N) CHAT_MESSAGES
  id                 user_id
  
  Historial de chats del usuario
  Ejemplo: Juan ha tenido 342 mensajes con el coach IA
```

---

# 6️⃣ BACKEND: CÓMO FUNCIONA

## Estructura de Carpetas

```
backend/
├─ app/
│  ├─ main.py                    ← PUNTO DE ENTRADA (FastAPI app)
│  ├─ database.py                ← CONEXIÓN A BD
│  ├─ models.py                  ← DEFINICIONES DE TABLAS (SQLAlchemy)
│  ├─ schemas.py                 ← VALIDACIÓN DE DATOS (Pydantic)
│  ├─ crud.py                    ← OPERACIONES BD (Create, Read, Update, Delete)
│  ├─ security.py                ← CONTRASEÑAS, JWT, TOKENS
│  │
│  ├─ core/
│  │  └─ config.py               ← VARIABLES DE ENTORNO
│  │
│  ├─ routers/                   ← ENDPOINTS (API routes)
│  │  ├─ auth.py                 (registro, login)
│  │  ├─ workouts.py             (CRUD entrenamientos)
│  │  ├─ training_plans.py       (crear/editar planes)
│  │  ├─ coach.py                (análisis y chat IA)
│  │  ├─ garmin.py               (sincronizar Garmin)
│  │  ├─ strava.py               (sincronizar Strava)
│  │  ├─ hrv.py                  (análisis HRV)
│  │  ├─ overtraining.py         (detectar sobreentrenamiento)
│  │  ├─ profile.py              (perfil del usuario)
│  │  ├─ health.py               (métricas salud)
│  │  ├─ onboarding.py           (onboarding wizard)
│  │  ├─ events.py               (carreras, eventos)
│  │  └─ ... (más routers)
│  │
│  └─ services/                  ← LÓGICA COMPLEJA
│     ├─ coach_service.py        (coaching con IA)
│     ├─ training_plan_service.py (generación de planes)
│     ├─ garmin_service.py       (parseo FIT, descarga)
│     ├─ strava_service.py       (auth Strava, descarga)
│     ├─ hrv_analysis_service.py (análisis HRV)
│     ├─ overtraining_detector_service.py (detector)
│     ├─ file_upload_service.py  (parseo GPX/TCX)
│     ├─ hr_zones_calculator.py  (cálculo zonas HR)
│     └─ ... (más services)
│
├─ requirements.txt              ← DEPENDENCIAS PYTHON
└─ Dockerfile                    ← CONTAINER CONFIG
```

## Cómo FastAPI Procesa una Request

```
REQUEST entra al servidor
        │
        ↓
┌────────────────────────────────────────┐
│ 1. MIDDLEWARE (procesamiento previo)   │
│    - Logging de requests               │
│    - CORS (¿permitir acceso?)          │
│    - Rate limiting (¿muchos requests?) │
└────────────────────────────────────────┘
        │
        ↓
┌────────────────────────────────────────┐
│ 2. ROUTING (¿A qué endpoint va?)       │
│    FastAPI mira la URL y método        │
│    POST /api/v1/training-plans/generate│
│    → training_plans.py router          │
│    → @router.post("/generate")         │
└────────────────────────────────────────┘
        │
        ↓
┌────────────────────────────────────────┐
│ 3. DEPENDENCY INJECTION                │
│    - get_db(): conecta a BD            │
│    - get_current_user(): verifica JWT  │
│    - Inyecta automáticamente en función│
└────────────────────────────────────────┘
        │
        ↓
┌────────────────────────────────────────┐
│ 4. VALIDATION (Pydantic)               │
│    - Valida tipos de datos             │
│    - Valida rangos (@Field constraints)│
│    - Retorna 422 si hay errores        │
└────────────────────────────────────────┘
        │
        ↓
┌────────────────────────────────────────┐
│ 5. HANDLER FUNCTION (Tu código)        │
│    async def generate_plan(...)        │
│    Lógica de negocio aquí              │
└────────────────────────────────────────┘
        │
        ↓
┌────────────────────────────────────────┐
│ 6. RESPONSE                            │
│    - Serializa resultado a JSON        │
│    - Status code 200                   │
│    - Headers (Content-Type, etc)       │
└────────────────────────────────────────┘
        │
        ↓
RESPONSE va al cliente (frontend)
```

## Ejemplo Real: Endpoint de Autenticación

### Archivo: `backend/app/routers/auth.py`

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import timedelta

from app.database import get_db
from app import crud, security, schemas
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=schemas.TokenResponse)
async def register(
    user_data: schemas.UserCreate,  # ← Pydantic valida automáticamente
    db: Session = Depends(get_db)   # ← FastAPI inyecta sesión BD
):
    """
    REGISTRO DE USUARIO
    
    1. Valida que email no exista
    2. Hashea contraseña
    3. Crea usuario en BD
    4. Genera JWT tokens
    5. Devuelve tokens al cliente
    """
    
    # PASO 1: ¿Ya existe el email?
    existing_user = crud.get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # PASO 2: Crear usuario en BD
    db_user = crud.create_user(db, {
        "email": user_data.email,
        "name": user_data.name,
        "password": user_data.password  # ← security.hash_password hace el hashing
    })
    
    # PASO 3: Generar tokens JWT
    access_token = security.create_access_token(
        data={"sub": str(db_user.id)},
        expire_minutes=settings.access_token_expire_minutes  # 30 minutos
    )
    refresh_token = security.create_refresh_token(
        data={"sub": str(db_user.id)},
        # Expires in 7 days
    )
    
    # PASO 4: Devolver respuesta
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": db_user.id,
            "name": db_user.name,
            "email": db_user.email
        }
    }


@router.post("/login", response_model=schemas.TokenResponse)
async def login(
    credentials: schemas.LoginRequest,
    db: Session = Depends(get_db)
):
    """
    LOGIN
    
    1. Busca usuario por email
    2. Verifica contraseña
    3. Genera JWT tokens
    4. Devuelve tokens
    """
    
    # PASO 1: Buscar usuario
    user = crud.get_user_by_email(db, credentials.email)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # PASO 2: Verificar contraseña
    if not security.verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # PASO 3: Generar tokens
    access_token = security.create_access_token(
        data={"sub": str(user.id)}
    )
    refresh_token = security.create_refresh_token(
        data={"sub": str(user.id)}
    )
    
    # PASO 4: Devolver
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {"id": user.id, "name": user.name, "email": user.email}
    }
```

### Cómo funciona en la práctica:

```
USUARIO hace POST /auth/register
{
  "name": "Juan García",
  "email": "juan@example.com",
  "password": "MiContraseña123!"
}

        ↓ FastAPI recibe

┌─────────────────────────────────────────┐
│ 1. Pydantic valida:                     │
│    ✓ name es string (1-100 caracteres) │
│    ✓ email es válido                   │
│    ✓ password es string (8+ caracteres)│
└─────────────────────────────────────────┘

        ↓ Si hay error, devuelve 422

┌─────────────────────────────────────────┐
│ 2. Inyecta dependencias:                │
│    ✓ db: Sesión de BD abierta          │
└─────────────────────────────────────────┘

        ↓ Ejecuta función

┌─────────────────────────────────────────┐
│ 3. La función hace:                     │
│    a) SELECT * FROM users WHERE email  │
│    b) Si existe → error 400             │
│    c) Si NO existe:                     │
│       - Hashea: MiContraseña123!        │
│         → $2b$12$xH8Z...               │
│       - INSERT INTO users               │
│       - Genera JWT: eyJhbG...          │
│       - Devuelve respuesta              │
└─────────────────────────────────────────┘

        ↓ Serializa a JSON

{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1In0...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1In0...",
  "token_type": "bearer",
  "user": {
    "id": 5,
    "name": "Juan García",
    "email": "juan@example.com"
  }
}

        ↓ Frontend recibe 200 OK

Frontend guarda access_token en localStorage
Próximas requests incluyen: Authorization: Bearer <token>
```

---

*(Documento continúa en la siguiente parte - es muy largo para caber en un mensaje)*
