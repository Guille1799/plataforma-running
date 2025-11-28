# 📘 DOCUMENTACIÓN TÉCNICA COMPLETA - PLATAFORMA RUNNING TIER 2
## PARTE 4: API REST & INTEGRACIÓN COMPLETA

**Continuación de documentación exhaustiva**  
**Fecha:** 17 de Noviembre, 2025

---

## ÍNDICE PARTE 4

1. [Arquitectura REST API](#arquitectura-rest-api)
2. [Autenticación & Security](#autenticación--security)
3. [17 Endpoints Detallados](#17-endpoints-detallados)
4. [Ejemplos de Request/Response](#ejemplos-de-requestresponse)
5. [Error Handling](#error-handling)
6. [Integration Patterns](#integration-patterns)

---

## ARQUITECTURA REST API

### Base Configuration

```python
# FastAPI Setup (main.py)
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.authentication import AuthenticationMiddleware
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Running Platform API",
    description="TIER 2 Complete AI Running Coach API",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",      # Development frontend
        "http://localhost:3001",       # Testing frontend
        "https://running-app.com"      # Production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["x-total-count"],  # Para paginación
)

# GROQ API Key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY no configurada en .env")

# Base URLs
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
```

### Estructura de Respuesta Estándar

```python
from dataclasses import dataclass
from typing import Generic, TypeVar, Optional, List
from datetime import datetime

T = TypeVar('T')

@dataclass
class ApiResponse(Generic[T]):
    """Respuesta estándar para TODOS los endpoints"""
    
    success: bool
    data: Optional[T]
    error: Optional[str]
    timestamp: datetime
    path: str
    duration_ms: float
    
    @classmethod
    def success_response(cls, data: T, path: str, duration_ms: float):
        return {
            "success": True,
            "data": data,
            "error": None,
            "timestamp": datetime.now().isoformat(),
            "path": path,
            "duration_ms": duration_ms
        }
    
    @classmethod
    def error_response(cls, error: str, path: str, duration_ms: float, status_code: int = 400):
        return {
            "success": False,
            "data": None,
            "error": error,
            "timestamp": datetime.now().isoformat(),
            "path": path,
            "duration_ms": duration_ms,
            "status_code": status_code
        }
```

---

## AUTENTICACIÓN & SECURITY

### JWT Token Management

```python
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional

# Configuración
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-prod")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_tokens(user_id: int) -> dict:
    """Crea access token + refresh token"""
    
    # ACCESS TOKEN (corta duración: 30 min)
    access_payload = {
        "sub": str(user_id),
        "type": "access",
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        "iat": datetime.utcnow()
    }
    access_token = jwt.encode(access_payload, SECRET_KEY, algorithm=ALGORITHM)
    
    # REFRESH TOKEN (larga duración: 7 días)
    refresh_payload = {
        "sub": str(user_id),
        "type": "refresh",
        "exp": datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        "iat": datetime.utcnow()
    }
    refresh_token = jwt.encode(refresh_payload, SECRET_KEY, algorithm=ALGORITHM)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60  # segundos
    }

def verify_token(token: str) -> Optional[int]:
    """Verifica JWT y retorna user_id"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if user_id is None or token_type != "access":
            return None
        
        return int(user_id)
    
    except JWTError:
        return None

def get_current_user(
    authorization: Optional[str] = Header(None)
) -> int:
    """Dependency injection para rutas protegidas"""
    
    if not authorization:
        raise HTTPException(status_code=401, detail="No authorization header")
    
    # Formato: "Bearer <token>"
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    
    user_id = verify_token(token)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return user_id
```

### Validación de Entrada con Pydantic

```python
from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional, List
from datetime import datetime

# AUTH
class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    name: str = Field(..., min_length=2, max_length=100)
    age: int = Field(..., ge=13, le=120)
    max_heart_rate: Optional[int] = Field(None, ge=100, le=220)
    
    @validator('password')
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password debe tener al menos una mayúscula')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password debe tener al menos un dígito')
        return v

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

# RACE PREDICTION
class RacePredictionRequest(BaseModel):
    distance_km: float = Field(..., ge=1, le=100)
    
    conditions: dict = Field(default_factory=dict)
    # Conditions incluye: temperature_c, humidity_percent, wind_speed_kmh, etc.
    
    class Config:
        schema_extra = {
            "example": {
                "distance_km": 21.1,
                "conditions": {
                    "temperature_c": 15,
                    "humidity_percent": 60,
                    "wind_speed_kmh": 5
                }
            }
        }

# TRAINING PLAN
class TrainingPlanRequest(BaseModel):
    goal: str = Field(..., description="RACE_5K, RACE_10K, RACE_HALF, RACE_FULL, GENERAL_FITNESS")
    weeks_to_prepare: int = Field(..., ge=4, le=52)
    current_weekly_volume_km: float = Field(..., ge=5, le=200)
    injury_history: Optional[List[str]] = None
    availability_hours_per_week: float = Field(..., ge=3, le=30)
    
    @validator('weeks_to_prepare')
    def validate_preparation_time(cls, v, values):
        if v < 4:
            raise ValueError('Mínimo 4 semanas de preparación')
        return v
```

---

## 17 ENDPOINTS DETALLADOS

### GRUPO 1: AUTENTICACIÓN (3 endpoints)

#### Endpoint 1.1: Register

```python
@app.post("/api/v1/auth/register", tags=["Authentication"])
async def register(
    data: UserRegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Registra nuevo usuario
    
    VALIDACIONES:
    - Email único (sino, error 409 Conflict)
    - Password min 8 chars, 1 mayúscula, 1 número
    - Age 13-120 años
    - Nombre 2-100 caracteres
    
    RETORNA:
    - User object con tokens
    - access_token: expires en 30 min
    - refresh_token: expires en 7 días
    
    EJEMPLOS DE ERROR:
    - 409: Email ya existe
    - 422: Datos inválidos
    """
    
    # Verificar email único
    existing = await db.execute(
        select(User).where(User.email == data.email)
    )
    if existing.scalar():
        raise HTTPException(status_code=409, detail="Email ya registrado")
    
    # Crear usuario
    user = User(
        email=data.email,
        password_hash=pwd_context.hash(data.password),
        name=data.name,
        age=data.age,
        max_heart_rate=data.max_heart_rate or estimate_max_hr(data.age)
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    tokens = create_tokens(user.id)
    
    return ApiResponse.success_response({
        "id": user.id,
        "email": user.email,
        "name": user.name,
        **tokens
    }, "/api/v1/auth/register", 15.5)
```

#### Endpoint 1.2: Login

```python
@app.post("/api/v1/auth/login", tags=["Authentication"])
async def login(
    credentials: UserLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Autentica usuario y genera tokens
    
    VALIDACIONES:
    - Email debe existir
    - Password debe coincidir
    
    RETORNA:
    - access_token + refresh_token
    - User profile básico
    
    EJEMPLOS DE ERROR:
    - 401: Credenciales inválidas
    - 404: User no existe
    """
    
    user_query = await db.execute(
        select(User).where(User.email == credentials.email)
    )
    user = user_query.scalar()
    
    if not user or not pwd_context.verify(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    
    tokens = create_tokens(user.id)
    
    return ApiResponse.success_response({
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "created_at": user.created_at,
        **tokens
    }, "/api/v1/auth/login", 22.3)
```

#### Endpoint 1.3: Refresh Token

```python
@app.post("/api/v1/auth/refresh", tags=["Authentication"])
async def refresh_access_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Genera nuevo access token usando refresh token
    
    VALIDACIONES:
    - Refresh token debe ser válido
    - Refresh token no debe haber expirado
    
    RETORNA:
    - Nuevo access_token (30 min de validez)
    
    EJEMPLOS DE ERROR:
    - 401: Refresh token inválido/expirado
    """
    
    user_id = verify_refresh_token(refresh_token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Refresh token inválido")
    
    tokens = create_tokens(user_id)
    
    return {
        "access_token": tokens["access_token"],
        "token_type": "Bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }
```

---

### GRUPO 2: OVERTRAINING DETECTION (3 endpoints)

#### Endpoint 2.1: Risk Assessment

```python
@app.get(
    "/api/v1/overtraining/risk-assessment",
    tags=["Overtraining Detection"],
    dependencies=[Depends(get_current_user)]
)
async def get_overtraining_risk(
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Calcula Stress Accumulation Index (SAI)
    
    ALGORITMO:
    SAI = (Volume × Intensity × Stress) ÷ (HRV × Recovery)
    
    RETORNA:
    - SAI value (0-100+)
    - Categorización: GREEN/YELLOW/ORANGE/RED
    - Desglose de factores
    - Recomendaciones
    
    EJEMPLO:
    {
        "sai": 65.3,
        "category": "ORANGE",
        "interpretation": "Fatigado - considera día fácil",
        "factors": {
            "volume": 45,      # km última semana
            "intensity": 1.2,   # multiplicador
            "stress": 0.95,     # factor de estrés
            "hrv": 42,          # ms
            "recovery": 0.85    # factor
        },
        "breakdown": {
            "volume_contribution": 30,  # 30% del SAI total
            "intensity_contribution": 25,
            "stress_contribution": 15,
            ...
        },
        "recommendations": [
            "Descansa hoy o entrena muy fácil",
            "Aumenta horas de sueño (tienes 6.5h promedio)",
            "Considera sesión de masaje"
        ]
    }
    """
    
    # Get user's recent workouts
    last_week = datetime.now() - timedelta(days=7)
    workouts = await get_user_workouts(user_id, db, since=last_week)
    
    # Calculate SAI
    service = OvertreainingDetectorService()
    sai_result = service.calculate_sai(user_id, workouts, db)
    
    return ApiResponse.success_response(sai_result, "/api/v1/overtraining/risk-assessment", 45.2)
```

#### Endpoint 2.2: Recovery Status

```python
@app.get(
    "/api/v1/overtraining/recovery-status",
    tags=["Overtraining Detection"]
)
async def get_recovery_status(
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Calcula Recovery Score (0-100)
    
    FACTORES:
    - Sleep quality (25%)
    - HRV (25%)
    - Fatigue perception (20%)
    - Stress level (15%)
    - Nutrition/Hydration (15%)
    
    RETORNA:
    - Score total
    - Desglose por factor
    - Trend últimos 7 días
    - Recomendaciones específicas
    
    EJEMPLO:
    {
        "recovery_score": 72,
        "status": "GOOD",
        "factors": {
            "sleep": {"score": 65, "hours": 6.5, "trend": "↓"},
            "hrv": {"score": 82, "value": 45, "trend": "↑"},
            "fatigue": {"score": 75, "rating": 6.2, "trend": "→"},
            "stress": {"score": 68, "level": 6, "trend": "↑"},
            "nutrition": {"score": 70, "data": "incomplete", "trend": "→"}
        },
        "trend_7_days": [72, 71, 70, 72, 73, 71, 72],
        "priority_improvements": [
            "Aumenta a 8h de sueño (actualmente 6.5h)",
            "Estrés subiendo, prueba meditación",
            "HRV excelente, mantén ritmo"
        ]
    }
    """
    
    service = OvertreainingDetectorService()
    recovery = service.calculate_recovery_status(user_id, db)
    
    return ApiResponse.success_response(recovery, "/api/v1/overtraining/recovery-status", 35.8)
```

#### Endpoint 2.3: Daily Alert

```python
@app.get(
    "/api/v1/overtraining/daily-alert",
    tags=["Overtraining Detection"]
)
async def get_daily_alert(
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Alerta diaria con recomendación de entrenamiento
    
    NIVELES:
    - CRITICAL: Descansa absolutamente
    - WARNING: Entrena muy fácil
    - INFO: Día normal pero con precaución
    - GOOD: Día ideal para entrenar duro
    
    RETORNA:
    - Alert level + mensaje
    - Workout recommendation
    - Expected duration
    - Intensity guidance
    
    EJEMPLO:
    {
        "date": "2025-11-17",
        "alert_level": "WARNING",
        "message": "Tu cuerpo está fatigado. Recomendamos entreno muy ligero.",
        "recommendation": {
            "type": "EASY_RUN",
            "distance_km": 6,
            "pace": "6:30-7:00 min/km",
            "intensity_zone": "Z1",
            "duration_minutes": 45,
            "notes": "Mantén conversación. Si te sientes mal, para."
        },
        "metrics_triggering_alert": [
            "HRV bajo (38ms vs baseline 45ms)",
            "Dormir poco anoche (5.5h)",
            "Volumen alto últimos 2 días"
        ],
        "alternative_activities": [
            "Yoga (30 min)",
            "Natación fácil (40 min)",
            "Caminar (60 min)",
            "Descanso completo"
        ]
    }
    """
    
    service = OvertreainingDetectorService()
    alert = service.generate_daily_alert(user_id, db)
    
    return ApiResponse.success_response(alert, "/api/v1/overtraining/daily-alert", 28.5)
```

---

### GRUPO 3: HRV ANALYSIS (4 endpoints)

#### Endpoint 3.1: Complete HRV Analysis

```python
@app.get(
    "/api/v1/hrv/analysis",
    tags=["HRV Analysis"]
)
async def get_hrv_analysis(
    user_id: int = Depends(get_current_user),
    days: int = Query(7, ge=1, le=90),
    db: AsyncSession = Depends(get_db)
):
    """
    Análisis completo de HRV últimos N días
    
    MÉTRICAS CALCULADAS:
    - SDNN: Standard Deviation of NN intervals
    - RMSSD: Root Mean Square of Successive Differences (MEJOR MÉTRICA)
    - pNN50: % de cambios > 50ms
    - LF/HF: Low freq / High freq ratio
    
    RETORNA:
    - Valores actuales
    - Histórico y trend
    - Comparativas con baseline
    - Interpretación
    
    EJEMPLO:
    {
        "period_days": 7,
        "metrics": {
            "sdnn": {
                "current": 48,
                "average_7days": 46,
                "baseline": 45,
                "trend": "↑ mejorando",
                "interpretation": "Buena variabilidad"
            },
            "rmssd": {
                "current": 42,
                "average_7days": 40,
                "baseline": 40,
                "trend": "↑ mejorando",
                "interpretation": "BUENO - Alta capacidad de recuperación"
            },
            "pnn50": {
                "current": 22,
                "average_7days": 20,
                "baseline": 19
            },
            "lf_hf_ratio": {
                "current": 1.8,
                "average_7days": 1.9,
                "baseline": 2.0,
                "interpretation": "Parasimpático activo - buena recuperación"
            }
        },
        "trend_graph": [35, 38, 40, 42, 44, 45, 42],
        "recovery_readiness": "85%",
        "recommendations": [
            "Excelente estado de recuperación",
            "Ideal para sesión dura hoy",
            "Mantén rutina de sueño actual"
        ]
    }
    """
    
    service = HRVAnalysisService()
    analysis = service.calculate_complete_analysis(user_id, db, days)
    
    return ApiResponse.success_response(analysis, "/api/v1/hrv/analysis", 52.3)
```

#### Endpoint 3.2: HRV Status Classification

```python
@app.get("/api/v1/hrv/status", tags=["HRV Analysis"])
async def get_hrv_status(
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Estado actual de HRV con clasificación
    
    CATEGORÍAS:
    - EXCELLENT (RMSSD > 60ms): 100% readiness
    - GOOD (RMSSD 45-60ms): 85% readiness
    - FAIR (RMSSD 35-45ms): 65% readiness
    - POOR (RMSSD 25-35ms): 40% readiness
    - VERY_POOR (RMSSD < 25ms): 10% readiness
    
    RETORNA:
    - Status actual
    - Readiness %
    - Cambio vs ayer
    - Cambio vs promedio
    
    EJEMPLO:
    {
        "timestamp": "2025-11-17T09:30:00",
        "rmssd": 48,
        "status": "GOOD",
        "readiness_percent": 85,
        "vs_yesterday": "+2",
        "vs_7day_average": "+3",
        "trend": "stable",
        "training_recommendation": "Ready for hard workout"
    }
    """
    
    service = HRVAnalysisService()
    status = service.get_current_status(user_id, db)
    
    return ApiResponse.success_response(status, "/api/v1/hrv/status", 18.7)
```

#### Endpoint 3.3: Workout Correlation

```python
@app.get("/api/v1/hrv/workout-correlation", tags=["HRV Analysis"])
async def get_workout_correlation(
    user_id: int = Depends(get_current_user),
    days: int = Query(30, ge=7, le=180),
    db: AsyncSession = Depends(get_db)
):
    """
    Correlación entre HRV anterior y performance en workout
    
    CÁLCULO:
    - Pearson correlation entre HRV day N y performance day N+1
    - Valores: -1 a +1 (1 = perfecta correlación)
    
    RETORNA:
    - Correlation coefficient
    - Interpretación
    - Sugerencias de pacing
    
    EJEMPLO:
    {
        "correlation": 0.78,
        "interpretation": "Fuerte correlación - tu HRV predice bien tu performance",
        "analysis": {
            "high_hrv_workouts": {
                "avg_pace": "5:05 min/km",
                "avg_power": 280,
                "count": 8
            },
            "low_hrv_workouts": {
                "avg_pace": "5:45 min/km",
                "avg_power": 250,
                "count": 6
            },
            "difference": "8% más rápido cuando HRV es alto"
        },
        "actionable": "Cuando HRV > 45ms, planifica workouts de calidad"
    }
    """
    
    service = HRVAnalysisService()
    correlation = service.calculate_workout_correlation(user_id, db, days)
    
    return ApiResponse.success_response(correlation, "/api/v1/hrv/workout-correlation", 68.5)
```

#### Endpoint 3.4: HRV Prediction

```python
@app.get("/api/v1/hrv/prediction", tags=["HRV Analysis"])
async def get_hrv_prediction(
    days_ahead: int = Query(7, ge=1, le=30),
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Predicción de HRV para próximos N días
    
    MÉTODO:
    - Moving average de últimos 7 días
    - Trend análisis
    - Seasonal patterns si hay datos > 30 días
    
    RETORNA:
    - Forecast día por día
    - Confidence intervals
    - Recomendaciones
    
    EJEMPLO:
    {
        "forecast_days": 7,
        "predictions": [
            {"day": "2025-11-18", "rmssd": 44, "status": "GOOD", "confidence": 85},
            {"day": "2025-11-19", "rmssd": 43, "status": "GOOD", "confidence": 82},
            {"day": "2025-11-20", "rmssd": 41, "status": "FAIR", "confidence": 78},
            ...
        ],
        "trend": "slight_decline",
        "recommendation": "Descansa en día 3-4 para recuperar"
    }
    """
    
    service = HRVAnalysisService()
    prediction = service.predict_hrv_trend(user_id, db, days_ahead)
    
    return ApiResponse.success_response(prediction, "/api/v1/hrv/prediction", 35.2)
```

---

### GRUPO 4: RACE PREDICTION (4 endpoints)

#### Endpoint 4.1: Predict with Conditions

```python
@app.post(
    "/api/v1/race/predict-with-conditions",
    tags=["Race Prediction"]
)
async def predict_race_time(
    request: RacePredictionRequest,
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Predice tiempo de carrera con condiciones ambientales
    
    CÁLCULO MULTIPASOS:
    1. VDOT de carrera reciente
    2. Tiempo base con fórmula Riegel
    3. Ajustes por temperatura, humedad, viento
    4. Ajustes por terreno y altitud
    5. Confidence score
    
    RETORNA:
    - Tiempo predicho
    - Rango ± minutos
    - Confidence %
    - Desglose de factores
    - Contexto IA
    
    EJEMPLO:
    {
        "distance_km": 21.1,
        "predicted_time_minutes": 105.4,
        "formatted": "1:45:24",
        "pace_min_km": 5.0,
        "confidence": 82,
        "margin_minutes": 2.5,
        "range": {
            "optimistic": "1:42:54",
            "pessimistic": "1:47:54"
        },
        "factors": {
            "temperature_impact": -1.2,
            "humidity_impact": -0.8,
            "wind_impact": -1.5,
            "terrain_impact": -2.1,
            "altitude_impact": 0
        },
        "ai_context": "Tu ritmo es sostenible. Pega fuerte en km 15-18."
    }
    """
    
    service = RacePredictionEnhancedService()
    prediction = service.predict_with_conditions(user_id, request, db)
    
    return ApiResponse.success_response(prediction, "/api/v1/race/predict-with-conditions", 85.3)
```

---

**[CONTINÚA EN PARTE 5]**

*Documento de 4,500+ líneas.*
*Parte 4 completada.*
*Contiene: Arquitectura API, JWT Security, 9 de 17 endpoints detallados con ejemplos.*
