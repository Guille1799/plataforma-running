# 🏗️ RunCoach AI - Arquitectura del Sistema

## 📋 Índice

1. [Visión General](#visión-general)
2. [Stack Tecnológico](#stack-tecnológico)
3. [Arquitectura de Microservicios](#arquitectura-de-microservicios)
4. [Base de Datos](#base-de-datos)
5. [Sistema de Autenticación](#sistema-de-autenticación)
6. [Integraciones Externas](#integraciones-externas)
7. [Sistema de Tareas Asíncronas](#sistema-de-tareas-asíncronas)
8. [API REST](#api-rest)
9. [Frontend](#frontend)
10. [Despliegue](#despliegue)

---

## 🎯 Visión General

**RunCoach AI** es una plataforma de entrenamiento inteligente para corredores que:
- Analiza entrenamientos con IA (GPX/FIT)
- Sincroniza métricas de salud desde Garmin
- Genera planes de entrenamiento personalizados
- Adapta planes según progreso y fatiga
- Proporciona base de datos de carreras en España

### Arquitectura de Alto Nivel

```
┌─────────────────────────────────────────────────────────────────┐
│                        USUARIO (Navegador)                       │
└───────────────────────────┬─────────────────────────────────────┘
                            │ HTTPS
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                   FRONTEND (Next.js 15 + React)                  │
│  • Páginas: Login, Dashboard, Análisis, Planes, Configuración   │
│  • Componentes: shadcn/ui + Tailwind CSS                         │
│  • Estado: React Query + Zustand                                 │
│  • Gráficos: Recharts (VO2max, HRV, tendencias)                 │
└───────────────────────────┬─────────────────────────────────────┘
                            │ REST API (JSON)
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                   BACKEND (FastAPI + Python)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   API REST   │  │   Auth JWT   │  │  AI Service  │          │
│  │  (Routers)   │  │   (OAuth2)   │  │   (Groq)     │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                  │                  │                  │
│  ┌──────▼──────────────────▼──────────────────▼───────┐         │
│  │              Business Logic (Services)              │         │
│  │  • WorkoutService • PlanService • HealthService     │         │
│  │  • EventsService  • GarminService                   │         │
│  └──────┬──────────────────┬──────────────────┬────────┘        │
│         │                  │                  │                  │
│  ┌──────▼──────┐    ┌──────▼──────┐    ┌─────▼──────┐          │
│  │   SQLAlchemy │    │  Garth (OAuth)│  │  Groq API  │          │
│  │    (ORM)     │    │   Garmin      │  │  (Llama 3) │          │
│  └──────┬───────┘    └───────────────┘  └────────────┘          │
└─────────┼────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                  POSTGRESQL 15 (Base de Datos)                   │
│  • users, workouts, health_metrics, training_plans, events       │
│  • Extensions: unaccent, pg_trgm (búsqueda fuzzy)               │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│              CELERY + REDIS (Tareas Asíncronas)                  │
│  • Celery Worker: Ejecuta tareas en background                   │
│  • Celery Beat: Scheduler (sync Garmin 2x/día: 7 AM, 8 PM UTC)  │
│  • Redis: Message Broker + Result Backend                        │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                   SERVICIOS EXTERNOS (APIs)                      │
│  • Groq (IA): Análisis de entrenamientos, planes personalizados │
│  • Garmin Connect: OAuth + sincronización de métricas           │
│  • Strava (futuro): Importar actividades                         │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Stack Tecnológico

### Frontend
| Tecnología | Versión | Propósito |
|-----------|---------|-----------|
| **Next.js** | 15.1.3 | Framework React con SSR/SSG |
| **React** | 19.0.0 | Librería UI |
| **TypeScript** | 5.7.2 | Type safety |
| **Tailwind CSS** | 3.4.17 | Utilidades CSS |
| **shadcn/ui** | Latest | Componentes pre-diseñados |
| **Recharts** | 2.15.0 | Gráficos y visualizaciones |
| **React Query** | 5.62.7 | Data fetching y cache |
| **Zustand** | 5.0.2 | Estado global |
| **Lucide React** | 0.468.0 | Iconos |
| **React Hook Form** | 7.54.2 | Formularios |
| **Zod** | 3.24.1 | Validación de esquemas |

### Backend
| Tecnología | Versión | Propósito |
|-----------|---------|-----------|
| **Python** | 3.11 | Lenguaje base |
| **FastAPI** | 0.115.6 | Framework web asíncrono |
| **SQLAlchemy** | 2.0.36 | ORM para PostgreSQL |
| **Pydantic** | 2.10.4 | Validación de datos |
| **Celery** | 5.4.0 | Tareas asíncronas |
| **Redis** | Latest | Message broker |
| **PostgreSQL** | 15 | Base de datos principal |
| **Alembic** | 1.14.0 | Migraciones de DB |
| **python-jose** | 3.3.0 | JWT tokens |
| **bcrypt** | 4.2.1 | Hash de passwords |
| **garth** | 0.4.46 | Cliente Garmin Connect |
| **groq** | 0.13.0 | Cliente IA |
| **gpxpy** | 1.6.2 | Parser de archivos GPX |
| **fitparse** | 1.2.0 | Parser de archivos FIT |

### Infraestructura
| Tecnología | Propósito |
|-----------|-----------|
| **Docker** | Contenedores |
| **Docker Compose** | Orquestación local |
| **Nginx** | Reverse proxy (producción) |
| **Render** | Hosting (producción) |

---

## 🏛️ Arquitectura de Microservicios

### Servicios Docker

```yaml
# docker-compose.dev.yml
services:
  frontend:
    port: 3000
    volumes: ./frontend:/app
    hot reload: ✅
    
  backend:
    port: 8000
    volumes: 
      - ./backend:/app
      - garmin_tokens:/app/garmin_tokens
    depends_on: [db, redis]
    
  db:
    image: postgres:15
    port: 5432
    volumes: postgres_data:/var/lib/postgresql/data
    
  redis:
    image: redis:alpine
    port: 6379
    
  celery-worker:
    command: celery -A app.celery_app worker
    depends_on: [db, redis]
    
  celery-beat:
    command: celery -A app.celery_app beat
    depends_on: [redis]
```

### Comunicación entre Servicios

```
Frontend (3000) ──REST API──> Backend (8000)
                              │
                              ├──SQL──> PostgreSQL (5432)
                              │
                              ├──HTTP──> Groq API (externa)
                              │
                              └──AMQP──> Redis (6379) <──┐
                                         │                │
                                         ├──> Celery Worker
                                         │                │
                                         └──> Celery Beat ┘
```

---

## 🗄️ Base de Datos

### Esquema PostgreSQL

#### Tabla `users`
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    name VARCHAR,
    age INTEGER,
    weight_kg FLOAT,
    vo2max FLOAT,
    pace_threshold VARCHAR,  -- "5:00" formato MM:SS
    garmin_email VARCHAR,
    has_garmin_sync BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### Tabla `workouts`
```sql
CREATE TABLE workouts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR,
    file_name VARCHAR,
    file_type VARCHAR,  -- 'gpx' o 'fit'
    upload_date TIMESTAMP DEFAULT NOW(),
    date TIMESTAMP,
    distance_km FLOAT,
    duration_seconds INTEGER,
    avg_pace VARCHAR,       -- "5:30" formato MM:SS
    avg_heart_rate INTEGER,
    max_heart_rate INTEGER,
    elevation_gain_m INTEGER,
    elevation_loss_m INTEGER,
    calories INTEGER,
    avg_cadence INTEGER,
    max_cadence INTEGER,
    analysis TEXT,          -- Análisis de IA (JSON string)
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_workouts_user_id ON workouts(user_id);
CREATE INDEX idx_workouts_date ON workouts(date);
```

#### Tabla `health_metrics`
```sql
CREATE TABLE health_metrics (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    resting_heart_rate INTEGER,
    hrv_rmssd FLOAT,              -- HRV en ms
    stress_level INTEGER,         -- 0-100
    body_battery INTEGER,         -- 0-100 (Garmin)
    sleep_score INTEGER,          -- 0-100
    sleep_duration_hours FLOAT,
    deep_sleep_hours FLOAT,
    light_sleep_hours FLOAT,
    rem_sleep_hours FLOAT,
    awake_hours FLOAT,
    steps INTEGER,
    floors_climbed INTEGER,
    calories_burned INTEGER,
    source VARCHAR DEFAULT 'garmin',  -- 'garmin', 'manual', 'strava'
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, date, source)
);

CREATE INDEX idx_health_metrics_user_date ON health_metrics(user_id, date);
```

#### Tabla `training_plans`
```sql
CREATE TABLE training_plans (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR NOT NULL,
    goal VARCHAR,                  -- 'Marathon 42K', 'Half 21K', etc.
    target_race_id VARCHAR,        -- external_id de events
    target_date DATE,
    current_fitness_level VARCHAR, -- 'beginner', 'intermediate', 'advanced'
    weekly_volume_km INTEGER,
    created_by VARCHAR DEFAULT 'ai',  -- 'ai', 'manual', 'template'
    plan_data TEXT,                   -- JSON con semanas y entrenamientos
    status VARCHAR DEFAULT 'active',  -- 'active', 'completed', 'archived'
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_training_plans_user_id ON training_plans(user_id);
CREATE INDEX idx_training_plans_status ON training_plans(status);
```

#### Tabla `events` (Carreras)
```sql
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    external_id VARCHAR UNIQUE NOT NULL,  -- 'SVMM2026', 'RMM2026'
    name VARCHAR NOT NULL,                -- 'San Silvestre Vallecana'
    location VARCHAR NOT NULL,            -- 'Madrid'
    region VARCHAR,                       -- 'Comunidad de Madrid'
    country VARCHAR DEFAULT 'España',
    date DATE NOT NULL,
    distance_km FLOAT NOT NULL,           -- 42.195, 21.0975, 10.0, 5.0
    elevation_m INTEGER,                  -- Desnivel positivo
    participants_estimate INTEGER,        -- 40000
    registration_url VARCHAR,
    website_url VARCHAR,
    description TEXT,
    price_eur FLOAT,
    source VARCHAR DEFAULT 'official',    -- 'official', 'user', 'scraper'
    verified BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_events_date ON events(date);
CREATE INDEX idx_events_location ON events(location);
CREATE INDEX idx_events_distance ON events(distance_km);
CREATE INDEX idx_events_verified ON events(verified);
CREATE INDEX idx_events_name_trgm ON events USING gin(name gin_trgm_ops);
```

**Extensiones PostgreSQL:**
```sql
CREATE EXTENSION IF NOT EXISTS unaccent;  -- Búsqueda sin acentos
CREATE EXTENSION IF NOT EXISTS pg_trgm;   -- Búsqueda fuzzy (trigramas)
```

---

## 🔐 Sistema de Autenticación

### JWT (JSON Web Tokens)

#### Configuración
```python
# backend/app/core/security.py
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
```

#### Estructura de Tokens

**Access Token:**
```json
{
  "sub": "1",           // user_id
  "exp": 1736345678,    // expira en 30 minutos
  "type": "access"
}
```

**Refresh Token:**
```json
{
  "sub": "1",           // user_id
  "exp": 1736950478,    // expira en 7 días
  "type": "refresh"
}
```

### Flujo de Autenticación

```python
# backend/app/routers/auth.py

@router.post("/register")
async def register(user_data: UserCreate, db: Session):
    # 1. Validar email único
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(409, "Email already exists")
    
    # 2. Hash password con bcrypt
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt(12))
    
    # 3. Crear usuario
    user = User(email=email, hashed_password=hashed_password, name=name)
    db.add(user)
    db.commit()
    
    # 4. Generar tokens
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    
    return {"access_token": access_token, "refresh_token": refresh_token}

@router.post("/login")
async def login(credentials: OAuth2PasswordRequestForm, db: Session):
    # 1. Buscar usuario
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(401, "Invalid credentials")
    
    # 2. Verificar password
    if not bcrypt.checkpw(password.encode(), user.hashed_password.encode()):
        raise HTTPException(401, "Invalid credentials")
    
    # 3. Generar tokens
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    
    return {"access_token": access_token, "refresh_token": refresh_token}

@router.post("/refresh")
async def refresh(refresh_token: str, db: Session):
    # 1. Verificar refresh token
    payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
    
    # 2. Generar nuevos tokens
    access_token = create_access_token({"sub": payload["sub"]})
    new_refresh_token = create_refresh_token({"sub": payload["sub"]})
    
    return {"access_token": access_token, "refresh_token": new_refresh_token}
```

### Middleware de Autenticación

```python
# backend/app/core/deps.py

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(401, "Invalid token")
    except JWTError:
        raise HTTPException(401, "Invalid token")
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(401, "User not found")
    
    return user
```

**Uso en endpoints protegidos:**
```python
@router.get("/workouts")
async def get_workouts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # Requiere autenticación
):
    workouts = db.query(Workout).filter(Workout.user_id == current_user.id).all()
    return workouts
```

---

## 🔌 Integraciones Externas

### Groq (IA - Llama 3.3 70B)

**Configuración:**
```python
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
model = "llama-3.3-70b-versatile"
```

**Análisis de Entrenamientos:**
```python
# backend/app/services/workout_service.py

def analyze_workout_with_ai(workout_data: dict) -> dict:
    prompt = f"""
    Analiza este entrenamiento de running:
    
    Distancia: {workout_data['distance_km']} km
    Duración: {workout_data['duration_seconds'] // 60} minutos
    Ritmo promedio: {workout_data['avg_pace']} min/km
    Frecuencia cardíaca promedio: {workout_data['avg_heart_rate']} bpm
    Desnivel: +{workout_data['elevation_gain_m']}m
    
    Proporciona:
    1. Tipo de entrenamiento (recuperación, base, tempo, series, etc.)
    2. Intensidad (baja, media, alta)
    3. Calidad de ejecución (1-10)
    4. Recomendaciones para mejorar
    5. Riesgo de lesión (bajo, medio, alto) basado en FC y ritmo
    
    Responde en formato JSON.
    """
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=1000
    )
    
    return json.loads(response.choices[0].message.content)
```

**Generación de Planes:**
```python
# backend/app/services/plan_service.py

def generate_training_plan(user_profile: dict, goal: dict) -> dict:
    prompt = f"""
    Genera un plan de entrenamiento personalizado:
    
    Usuario:
    - Nivel: {user_profile['fitness_level']}
    - VO2max: {user_profile['vo2max']}
    - Volumen semanal actual: {user_profile['weekly_volume_km']} km
    - Ritmo umbral: {user_profile['pace_threshold']} min/km
    
    Objetivo:
    - Carrera: {goal['race_name']} ({goal['distance_km']} km)
    - Fecha: {goal['target_date']}
    - Semanas disponibles: {goal['weeks_to_race']}
    
    Genera plan con:
    1. Progresión de volumen semanal
    2. Días de entrenamiento por semana
    3. Tipos de entrenamientos (recuperación, base, tempo, series, largo)
    4. Ritmos objetivo para cada tipo
    5. Consejos de tapering (2 semanas antes)
    
    Formato JSON con estructura de semanas.
    """
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
        max_tokens=4000
    )
    
    return json.loads(response.choices[0].message.content)
```

### Garmin Connect (OAuth + Sincronización)

**Librería:** `garth` (wrapper OAuth no oficial)

**Flujo de Autenticación:**
```python
# backend/app/services/garmin_service.py
from garth.exc import GarthHTTPError

async def garmin_login(email: str, password: str):
    try:
        # 1. Autenticación OAuth
        garth.login(email, password)
        
        # 2. Guardar tokens en volumen persistente
        token_dir = "/app/garmin_tokens"
        os.makedirs(token_dir, exist_ok=True)
        garth.save(f"{token_dir}/{email}")
        
        return True
    except GarthHTTPError as e:
        raise HTTPException(401, f"Garmin auth failed: {str(e)}")
```

**Sincronización de Métricas:**
```python
async def sync_garmin_health_metrics(user: User, db: Session):
    try:
        # 1. Cargar tokens guardados
        garth.resume(f"/app/garmin_tokens/{user.garmin_email}")
        
        # 2. Fecha desde última sync (o últimos 30 días)
        last_sync = db.query(HealthMetric).filter(
            HealthMetric.user_id == user.id
        ).order_by(HealthMetric.date.desc()).first()
        
        start_date = last_sync.date if last_sync else date.today() - timedelta(days=30)
        
        # 3. Obtener métricas
        metrics = []
        for single_date in daterange(start_date, date.today()):
            daily_data = garth.connectapi(
                f"/usersummary-service/usersummary/daily/{user.garmin_email}",
                params={"calendarDate": single_date.isoformat()}
            )
            
            # 4. Parsear respuesta
            metric = HealthMetric(
                user_id=user.id,
                date=single_date,
                resting_heart_rate=daily_data.get("restingHeartRate"),
                hrv_rmssd=daily_data.get("hrvRmssd"),
                stress_level=daily_data.get("averageStressLevel"),
                body_battery=daily_data.get("bodyBattery", {}).get("charged"),
                sleep_score=daily_data.get("sleepScore"),
                sleep_duration_hours=daily_data.get("sleepDuration") / 3600,
                steps=daily_data.get("totalSteps"),
                calories_burned=daily_data.get("totalKilocalories"),
                source="garmin"
            )
            metrics.append(metric)
        
        # 5. Guardar en DB (upsert)
        for metric in metrics:
            existing = db.query(HealthMetric).filter(
                HealthMetric.user_id == user.id,
                HealthMetric.date == metric.date,
                HealthMetric.source == "garmin"
            ).first()
            
            if existing:
                for key, value in metric.__dict__.items():
                    if key != "_sa_instance_state" and value is not None:
                        setattr(existing, key, value)
            else:
                db.add(metric)
        
        db.commit()
        return len(metrics)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(500, f"Sync failed: {str(e)}")
```

---

## ⏰ Sistema de Tareas Asíncronas

### Celery Configuration

```python
# backend/app/celery_app.py
from celery import Celery
from celery.schedules import crontab

celery_app = Celery(
    "runcoach",
    broker=os.getenv("REDIS_URL", "redis://redis:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://redis:6379/0")
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    result_expires=3600  # Resultados expiran en 1 hora
)

# Celery Beat Schedule (tareas programadas)
celery_app.conf.beat_schedule = {
    "sync-garmin-morning": {
        "task": "app.tasks.sync_all_garmin_users",
        "schedule": crontab(hour=7, minute=0),  # 7 AM UTC diario
    },
    "sync-garmin-evening": {
        "task": "app.tasks.sync_all_garmin_users",
        "schedule": crontab(hour=20, minute=0),  # 8 PM UTC diario
    },
}
```

### Tareas Definidas

```python
# backend/app/tasks.py

@celery_app.task(name="app.tasks.sync_all_garmin_users")
def sync_all_garmin_users():
    """Sincroniza métricas de Garmin para todos los usuarios conectados"""
    db = SessionLocal()
    try:
        users = db.query(User).filter(User.has_garmin_sync == True).all()
        
        results = {
            "total_users": len(users),
            "successful": 0,
            "failed": 0,
            "errors": []
        }
        
        for user in users:
            try:
                metrics_count = sync_garmin_health_metrics(user, db)
                results["successful"] += 1
                logger.info(f"Synced {metrics_count} metrics for user {user.id}")
            except Exception as e:
                results["failed"] += 1
                results["errors"].append({
                    "user_id": user.id,
                    "error": str(e)
                })
                logger.error(f"Sync failed for user {user.id}: {str(e)}")
        
        return results
        
    finally:
        db.close()

@celery_app.task(name="app.tasks.analyze_workout_async")
def analyze_workout_async(workout_id: int):
    """Analiza un entrenamiento con IA en background"""
    db = SessionLocal()
    try:
        workout = db.query(Workout).filter(Workout.id == workout_id).first()
        if not workout:
            return {"error": "Workout not found"}
        
        # Preparar datos para IA
        workout_data = {
            "distance_km": workout.distance_km,
            "duration_seconds": workout.duration_seconds,
            "avg_pace": workout.avg_pace,
            "avg_heart_rate": workout.avg_heart_rate,
            "elevation_gain_m": workout.elevation_gain_m
        }
        
        # Llamar a Groq
        analysis = analyze_workout_with_ai(workout_data)
        
        # Guardar análisis
        workout.analysis = json.dumps(analysis)
        db.commit()
        
        return {"workout_id": workout_id, "status": "analyzed"}
        
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()

@celery_app.task(name="app.tasks.generate_plan_async")
def generate_plan_async(user_id: int, plan_id: int):
    """Genera un plan de entrenamiento con IA en background"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        plan = db.query(TrainingPlan).filter(TrainingPlan.id == plan_id).first()
        
        if not user or not plan:
            return {"error": "User or plan not found"}
        
        # Preparar perfil de usuario
        user_profile = {
            "fitness_level": plan.current_fitness_level,
            "vo2max": user.vo2max,
            "weekly_volume_km": plan.weekly_volume_km,
            "pace_threshold": user.pace_threshold
        }
        
        # Preparar objetivo
        goal = {
            "race_name": plan.name,
            "distance_km": 42.195 if "Marathon" in plan.goal else 21.0975,
            "target_date": plan.target_date.isoformat(),
            "weeks_to_race": (plan.target_date - date.today()).days // 7
        }
        
        # Generar plan con IA
        plan_data = generate_training_plan(user_profile, goal)
        
        # Guardar plan
        plan.plan_data = json.dumps(plan_data)
        plan.status = "active"
        db.commit()
        
        return {"plan_id": plan_id, "status": "generated"}
        
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()
```

### Monitoreo de Tareas

```bash
# Ver tareas activas
docker exec -it runcoach_celery_worker celery -A app.celery_app inspect active

# Ver tareas programadas
docker exec -it runcoach_celery_beat celery -A app.celery_app inspect scheduled

# Ver estadísticas
docker exec -it runcoach_celery_worker celery -A app.celery_app inspect stats
```

---

## 📡 API REST

### Endpoints Disponibles

#### **Autenticación** (`/api/v1/auth`)

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| POST | `/register` | Crear nueva cuenta | ❌ |
| POST | `/login` | Iniciar sesión | ❌ |
| POST | `/refresh` | Renovar access token | ❌ |
| GET | `/me` | Obtener perfil actual | ✅ |
| PUT | `/me` | Actualizar perfil | ✅ |

#### **Entrenamientos** (`/api/v1/workouts`)

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| GET | `/` | Listar entrenamientos | ✅ |
| POST | `/upload` | Subir GPX/FIT | ✅ |
| GET | `/{workout_id}` | Detalle de entrenamiento | ✅ |
| DELETE | `/{workout_id}` | Eliminar entrenamiento | ✅ |
| POST | `/{workout_id}/analyze` | Analizar con IA | ✅ |
| GET | `/statistics` | Estadísticas generales | ✅ |

#### **Métricas de Salud** (`/api/v1/health`)

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| GET | `/metrics` | Métricas por rango de fechas | ✅ |
| GET | `/trends` | Tendencias (HRV, FC, sueño) | ✅ |
| POST | `/sync-garmin` | Sincronizar Garmin manualmente | ✅ |
| GET | `/sync-status` | Estado de última sync | ✅ |

#### **Planes de Entrenamiento** (`/api/v1/plans`)

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| GET | `/` | Listar planes | ✅ |
| POST | `/generate` | Generar plan con IA | ✅ |
| GET | `/{plan_id}` | Detalle de plan | ✅ |
| PUT | `/{plan_id}` | Actualizar plan | ✅ |
| DELETE | `/{plan_id}` | Eliminar plan | ✅ |
| POST | `/{plan_id}/adapt` | Adaptar según progreso | ✅ |

#### **Carreras** (`/api/v1/races`)

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| GET | `/search` | Buscar carreras | ❌ |
| GET | `/upcoming` | Próximas carreras (N semanas) | ❌ |
| GET | `/{race_id}` | Detalle de carrera | ❌ |
| GET | `/by-distance/{distance_km}` | Carreras por distancia | ❌ |

#### **Admin - Carreras** (`/api/v1/admin/races`)

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| POST | `/` | Crear carrera | ✅ (TODO: admin) |
| GET | `/` | Listar todas (incluye pasadas) | ✅ (TODO: admin) |
| PUT | `/{race_id}` | Actualizar carrera | ✅ (TODO: admin) |
| DELETE | `/{race_id}` | Eliminar carrera | ✅ (TODO: admin) |
| GET | `/stats` | Estadísticas de BD | ✅ (TODO: admin) |

### Esquemas de Datos (Pydantic)

```python
# backend/app/schemas.py

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None

class UserOut(BaseModel):
    id: int
    email: str
    name: Optional[str]
    age: Optional[int]
    weight_kg: Optional[float]
    vo2max: Optional[float]
    pace_threshold: Optional[str]
    has_garmin_sync: bool
    created_at: datetime

class WorkoutOut(BaseModel):
    id: int
    user_id: int
    name: Optional[str]
    date: datetime
    distance_km: float
    duration_seconds: int
    avg_pace: str
    avg_heart_rate: Optional[int]
    elevation_gain_m: Optional[int]
    analysis: Optional[dict]  # JSON parseado
    created_at: datetime

class HealthMetricOut(BaseModel):
    id: int
    user_id: int
    date: date
    resting_heart_rate: Optional[int]
    hrv_rmssd: Optional[float]
    stress_level: Optional[int]
    body_battery: Optional[int]
    sleep_score: Optional[int]
    sleep_duration_hours: Optional[float]
    steps: Optional[int]
    source: str

class EventOut(BaseModel):
    id: int
    external_id: str
    name: str
    location: str
    date: date
    distance_km: float
    elevation_m: Optional[int]
    registration_url: Optional[str]
    website_url: Optional[str]
    verified: bool
```

---

## 🎨 Frontend

### Estructura de Componentes

```
frontend/app/
├── (auth)/
│   ├── login/page.tsx         # Página de login
│   └── register/page.tsx      # Página de registro
├── dashboard/
│   └── page.tsx               # Dashboard principal
├── workouts/
│   ├── page.tsx               # Lista de entrenamientos
│   └── [id]/page.tsx          # Detalle de entrenamiento
├── health/
│   └── page.tsx               # Métricas de salud
├── plans/
│   ├── page.tsx               # Lista de planes
│   ├── new/page.tsx           # Wizard crear plan
│   └── [id]/page.tsx          # Detalle de plan
├── settings/
│   └── page.tsx               # Configuración de usuario
└── layout.tsx                 # Layout principal

frontend/components/
├── ui/                        # shadcn/ui components
│   ├── button.tsx
│   ├── card.tsx
│   ├── input.tsx
│   ├── select.tsx
│   └── ...
├── charts/
│   ├── HRVChart.tsx           # Gráfico de HRV
│   ├── PaceChart.tsx          # Gráfico de ritmos
│   └── TrendsChart.tsx        # Tendencias generales
├── dashboard/
│   ├── DashboardHeader.tsx
│   ├── MetricCard.tsx
│   └── RecentWorkouts.tsx
├── workouts/
│   ├── WorkoutCard.tsx
│   ├── WorkoutUploadForm.tsx
│   └── WorkoutAnalysisPanel.tsx
└── plans/
    ├── PlanWizard.tsx
    ├── WeeklySchedule.tsx
    └── AdaptationPanel.tsx
```

### Estado Global (Zustand)

```typescript
// frontend/lib/store.ts
import { create } from 'zustand'

interface AuthState {
  user: User | null
  accessToken: string | null
  refreshToken: string | null
  login: (tokens: Tokens, user: User) => void
  logout: () => void
  updateUser: (user: Partial<User>) => void
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  accessToken: localStorage.getItem('access_token'),
  refreshToken: localStorage.getItem('refresh_token'),
  
  login: (tokens, user) => {
    localStorage.setItem('access_token', tokens.access_token)
    localStorage.setItem('refresh_token', tokens.refresh_token)
    set({ user, accessToken: tokens.access_token, refreshToken: tokens.refresh_token })
  },
  
  logout: () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    set({ user: null, accessToken: null, refreshToken: null })
  },
  
  updateUser: (updates) => set((state) => ({
    user: state.user ? { ...state.user, ...updates } : null
  }))
}))
```

### API Client (React Query)

```typescript
// frontend/lib/api.ts
import axios from 'axios'
import { useAuthStore } from './store'

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
})

// Interceptor: añadir token
api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().accessToken
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Interceptor: refresh token si 401
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      const refreshToken = useAuthStore.getState().refreshToken
      if (refreshToken) {
        try {
          const { data } = await axios.post('/auth/refresh', {
            refresh_token: refreshToken
          })
          useAuthStore.getState().login(data.tokens, data.user)
          // Reintentar request original
          return api(error.config)
        } catch {
          useAuthStore.getState().logout()
          window.location.href = '/login'
        }
      }
    }
    return Promise.reject(error)
  }
)

export default api
```

### Hooks de React Query

```typescript
// frontend/hooks/useWorkouts.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '@/lib/api'

export const useWorkouts = () => {
  return useQuery({
    queryKey: ['workouts'],
    queryFn: async () => {
      const { data } = await api.get('/workouts')
      return data
    }
  })
}

export const useUploadWorkout = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData()
      formData.append('file', file)
      const { data } = await api.post('/workouts/upload', formData)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workouts'] })
    }
  })
}
```

---

## 🚀 Despliegue

### Desarrollo Local

```bash
# 1. Clonar repositorio
git clone https://github.com/Guille1799/plataforma-running.git
cd plataforma-running

# 2. Crear .env
cp .env.example .env
# Editar .env con tus valores reales

# 3. Iniciar servicios
start-dev.bat  # Windows
# o
docker-compose -f docker-compose.dev.yml up -d

# 4. Acceder
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Producción (Render)

**Servicios creados:**

1. **Web Service (Backend)**
   - Tipo: Docker
   - Dockerfile: `backend/Dockerfile`
   - Port: 8000
   - Health Check: `/api/v1/health`
   - Variables de entorno: SECRET_KEY, GROQ_API_KEY, DATABASE_URL

2. **Web Service (Frontend)**
   - Tipo: Static Site
   - Build: `npm run build`
   - Publish: `out/`
   - Variables: NEXT_PUBLIC_API_URL

3. **PostgreSQL Database**
   - Versión: 15
   - Plan: Starter ($7/mes)
   - Backup automático diario

4. **Redis**
   - Plan: Free
   - Máx. 25 MB

**Deploy automático:**
- Push a `main` → Render auto-deploy
- Logs en tiempo real en dashboard
- Rollback con 1 click

---

**Última actualización:** 8 de enero de 2026  
**Versión:** 3.0
