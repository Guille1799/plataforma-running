"""
schemas.py - Pydantic models para validación y serialización
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ============================================================================
# AUTH SCHEMAS
# ============================================================================

class UserCreate(BaseModel):
    """Schema para registro de nuevo usuario."""
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)


class UserOut(BaseModel):
    """Schema para retornar datos de usuario (sin contraseña)."""
    id: int
    name: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    """Schema para login request."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Schema para respuesta de tokens (register/login/refresh)."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserOut


class RefreshTokenRequest(BaseModel):
    """Schema para refresh token request."""
    refresh_token: str


# ============================================================================
# WORKOUT SCHEMAS
# ============================================================================

class WorkoutCreate(BaseModel):
    """Schema para crear nuevo workout (desde FIT file)."""
    sport_type: str = Field(..., min_length=1, max_length=50)
    start_time: datetime
    duration_seconds: int = Field(..., gt=0)
    distance_meters: float = Field(..., gt=0)
    avg_heart_rate: Optional[int] = Field(None, ge=0, le=300)
    max_heart_rate: Optional[int] = Field(None, ge=0, le=300)
    avg_pace: Optional[float] = Field(None, gt=0)  # seconds per km
    max_speed: Optional[float] = Field(None, ge=0)  # km/h
    calories: Optional[float] = Field(None, ge=0)
    elevation_gain: Optional[float] = Field(None, ge=0)
    avg_cadence: Optional[float] = Field(None, ge=0)  # steps per minute
    max_cadence: Optional[float] = Field(None, ge=0)
    avg_stance_time: Optional[float] = Field(None, ge=0)  # milliseconds
    avg_vertical_oscillation: Optional[float] = Field(None, ge=0)  # centimeters
    avg_leg_spring_stiffness: Optional[float] = Field(None, ge=0)
    left_right_balance: Optional[float] = Field(None, ge=0, le=100)  # percentage
    file_name: Optional[str] = None

    @validator('avg_heart_rate', 'max_heart_rate', pre=True)
    def validate_heart_rate(cls, v):
        """Asegurar que max_heart_rate no sea menor que avg_heart_rate."""
        return v if v is None or v > 0 else None


class WorkoutOut(BaseModel):
    """Schema para retornar datos de workout."""
    id: int
    user_id: int
    sport_type: str
    start_time: datetime
    duration_seconds: int
    distance_meters: float
    avg_heart_rate: Optional[int] = None
    max_heart_rate: Optional[int] = None
    avg_pace: Optional[float] = None
    max_speed: Optional[float] = None
    calories: Optional[float] = None
    elevation_gain: Optional[float] = None
    avg_cadence: Optional[float] = None
    max_cadence: Optional[float] = None
    avg_stance_time: Optional[float] = None
    avg_vertical_oscillation: Optional[float] = None
    avg_leg_spring_stiffness: Optional[float] = None
    left_right_balance: Optional[float] = None
    file_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class WorkoutStats(BaseModel):
    """Schema para estadísticas agregadas de workouts."""
    total_workouts: int
    total_distance_km: float
    total_duration_hours: float
    avg_pace_min_per_km: Optional[float] = None
    avg_heart_rate: Optional[int] = None
    total_calories: Optional[float] = None
    sports_breakdown: dict  # {"running": 10, "cycling": 5, ...}


# ============================================================================
# ATHLETE PROFILE SCHEMAS
# ============================================================================

class RunningLevel(str, Enum):
    """Enum para nivel de running."""
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"


class CoachingStyle(str, Enum):
    """Enum para estilo de coaching."""
    motivator = "motivator"  # Energético, positivo, enfocado en ánimos
    technical = "technical"  # Analítico, basado en datos, detallado
    balanced = "balanced"  # Mix de motivación y técnica
    custom = "custom"  # Usuario define su propio prompt


class GoalType(str, Enum):
    """Enum para tipo de objetivo."""
    race = "race"  # Competencia específica
    distance = "distance"  # Aumentar distancia
    pace = "pace"  # Mejorar pace
    frequency = "frequency"  # Aumentar frecuencia de entrenamientos
    health = "health"  # Objetivos de salud general


class Goal(BaseModel):
    """Schema para un objetivo de entrenamiento."""
    name: str = Field(..., min_length=1, max_length=200, description="Nombre del objetivo")
    goal_type: GoalType
    target_value: Optional[str] = Field(None, description="Valor objetivo (ej: '40:00', '10K', '4x/week')")
    deadline: Optional[datetime] = Field(None, description="Fecha límite para el objetivo")
    description: Optional[str] = Field(None, max_length=500, description="Descripción adicional")
    completed: bool = Field(default=False, description="Si el objetivo fue completado")
    completed_at: Optional[datetime] = Field(None, description="Fecha de completación")


class GoalCreate(BaseModel):
    """Schema para crear un nuevo objetivo."""
    name: str = Field(..., min_length=1, max_length=200)
    goal_type: GoalType
    target_value: Optional[str] = None
    deadline: Optional[datetime] = None
    description: Optional[str] = Field(None, max_length=500)


class GoalUpdate(BaseModel):
    """Schema para actualizar un objetivo existente."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    goal_type: Optional[GoalType] = None
    target_value: Optional[str] = None
    deadline: Optional[datetime] = None
    description: Optional[str] = Field(None, max_length=500)
    completed: Optional[bool] = None


class Injury(BaseModel):
    """Schema para historial de lesiones."""
    date: datetime
    injury_type: str = Field(..., min_length=1, max_length=100, description="Tipo de lesión")
    description: Optional[str] = Field(None, max_length=500)
    recovered: bool = Field(default=False)
    recovery_date: Optional[datetime] = None


class AthletePreferences(BaseModel):
    """Schema para preferencias de entrenamiento."""
    music: Optional[bool] = Field(None, description="Prefiere música durante entrenamientos")
    preferred_pace_range: Optional[List[float]] = Field(None, description="Rango de pace preferido [min, max] en min/km")
    time_of_day: Optional[str] = Field(None, description="Hora preferida del día (morning/afternoon/evening/night)")
    terrain_preference: Optional[str] = Field(None, description="Terreno preferido (road/trail/track/mixed)")
    weather_preference: Optional[str] = Field(None, description="Condiciones climáticas preferidas")
    training_days: Optional[List[str]] = Field(None, description="Días de la semana para entrenar")
    avoid_days: Optional[List[str]] = Field(None, description="Días a evitar")
    custom_prompt: Optional[str] = Field(None, max_length=1000, description="Prompt personalizado para coaching_style=custom")


class AthleteProfileUpdate(BaseModel):
    """Schema para actualizar perfil de atleta."""
    running_level: Optional[RunningLevel] = None
    max_heart_rate: Optional[int] = Field(None, ge=100, le=220, description="Frecuencia cardíaca máxima")
    coaching_style: Optional[CoachingStyle] = None
    goals: Optional[List[Goal]] = None
    injuries: Optional[List[Injury]] = None
    preferences: Optional[AthletePreferences] = None

    @validator('max_heart_rate')
    def validate_max_hr(cls, v):
        """Validar que max_heart_rate esté en rango razonable."""
        if v is not None and (v < 100 or v > 220):
            raise ValueError("Max heart rate debe estar entre 100 y 220 bpm")
        return v


class AthleteProfileOut(BaseModel):
    """Schema para retornar perfil completo de atleta."""
    running_level: Optional[str] = None
    max_heart_rate: Optional[int] = None
    coaching_style: Optional[str] = None
    goals: Optional[List[Dict[str, Any]]] = None
    injuries: Optional[List[Dict[str, Any]]] = None
    preferences: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


# ============================================================================
# CHAT SCHEMAS
# ============================================================================

class ChatMessageCreate(BaseModel):
    """Schema for creating a new chat message."""
    message: str = Field(..., min_length=1, max_length=2000, description="User message to coach")


class ChatMessageOut(BaseModel):
    """Schema for chat message output."""
    id: int
    role: str  # "user" or "assistant"
    content: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class ChatResponse(BaseModel):
    """Schema for chat response from coach."""
    user_message: ChatMessageOut
    assistant_message: ChatMessageOut
    tokens_used: int
    conversation_length: int  # Total messages in conversation


# ============================================================================
# ONBOARDING SCHEMAS
# ============================================================================

class OnboardingCompleteRequest(BaseModel):
    """Schema para completar el flujo de onboarding."""
    primary_device: str = Field(
        ..., 
        description="Primary device: garmin, xiaomi, strava, manual, apple"
    )
    use_case: str = Field(
        ...,
        description="Use case: fitness_tracker, training_coach, race_prep, general_health"
    )
    coach_style_preference: str = Field(
        default="balanced",
        description="Coach style: motivator, technical, balanced, custom"
    )
    language: str = Field(default="es", description="Language: es, en, fr, etc")
    enable_notifications: bool = Field(default=True, description="Enable notifications")
    integration_sources: List[str] = Field(
        default=[],
        description="Additional integration sources in priority order"
    )


class OnboardingCompleteResponse(BaseModel):
    """Response after onboarding completion."""
    success: bool
    user_id: int
    message: str
    onboarding_completed: bool
    redirectUrl: str = "/dashboard"

    class Config:
        from_attributes = True


class UserProfileOut(BaseModel):
    """Extended user profile with onboarding data."""
    id: int
    name: str
    email: str
    onboarding_completed: bool
    primary_device: Optional[str] = None
    use_case: Optional[str] = None
    coach_style_preference: Optional[str] = None
    language: str = "es"
    enable_notifications: bool = True
    integration_sources: Optional[List[str]] = None
    created_at: datetime
    onboarding_completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================================================
# DEVICE INTEGRATION SCHEMAS
# ============================================================================

class DeviceSyncConfig(BaseModel):
    """Configuration for a single device's sync settings."""
    sync_interval_hours: int = Field(ge=1, le=24, description="Sync interval in hours (1-24)")
    auto_sync_enabled: bool = True
    last_sync: Optional[datetime] = None
    next_sync: Optional[datetime] = None
    sync_error: Optional[str] = None


class DeviceIntegration(BaseModel):
    """Represents a configured device integration."""
    device_id: str = Field(description="Unique device identifier (e.g., 'garmin', 'xiaomi', 'strava')")
    device_type: str = Field(description="Type of device (garmin, xiaomi, strava, apple, manual)")
    device_name: str = Field(description="User-friendly name (e.g., 'My Garmin Watch')")
    sync_config: DeviceSyncConfig
    is_primary: bool = False
    connected_at: datetime
    
    class Config:
        from_attributes = True


class DeviceIntegrationCreate(BaseModel):
    """Request schema for adding a new device."""
    device_type: str = Field(description="Device type (garmin, xiaomi, strava, apple, manual)")
    device_name: str = Field(min_length=1, max_length=50)
    sync_interval_hours: int = Field(default=1, ge=1, le=24)
    auto_sync_enabled: bool = True


class DeviceIntegrationUpdate(BaseModel):
    """Request schema for updating device settings."""
    device_name: Optional[str] = Field(None, min_length=1, max_length=50)
    sync_interval_hours: Optional[int] = Field(None, ge=1, le=24)
    auto_sync_enabled: Optional[bool] = None


class DeviceIntegrationList(BaseModel):
    """Response schema with list of devices."""
    primary_device: str
    devices_enabled: bool
    devices: list[DeviceIntegration]
    
    class Config:
        from_attributes = True


class DeviceSyncStatus(BaseModel):
    """Device sync status response."""
    device_id: str
    last_sync: Optional[datetime]
    next_sync: Optional[datetime]
    sync_status: str = Field(description="Status: idle, syncing, success, error")
    message: Optional[str] = None


# ============================================================================
# TRAINING PLAN SCHEMAS
# ============================================================================

class TrainingGoal(BaseModel):
    """Schema para carrera objetivo."""
    race_name: str
    race_date: str
    distance_km: float
    target_time_minutes: float
    target_pace_min_per_km: Optional[float] = None


class TrainingPlanRequest(BaseModel):
    """Schema para solicitar un plan de entrenamiento personalizado."""
    general_goal: str = Field(..., description="marathon, half_marathon, 10k, 5k, improve_fitness, build_endurance")
    priority: str = Field(..., description="speed, endurance, recovery, balanced")
    has_target_race: bool = False
    target_race: Optional[TrainingGoal] = None
    training_days_per_week: int = Field(default=4, ge=3, le=7)
    preferred_long_run_day: str = Field(default="saturday", description="day of week for long run")
    plan_duration_weeks: int = Field(default=8, ge=2, le=52)
    include_strength_training: bool = True
    strength_location: str = Field(default="gym", description="gym or home")
    training_method: str = Field(default="automatic", description="automatic, pace_based or heart_rate_based")
    include_cross_training: bool = False
    cross_training_types: List[str] = Field(default=[], description="swimming, cycling, rowing, etc")
    recovery_focus: str = Field(default="moderate", description="minimal, moderate, high")
    injury_considerations: Optional[str] = None


class TrainingDay(BaseModel):
    """Schema para un día de entrenamiento."""
    day: str
    type: str  # Easy Run, Speed Work, Long Run, Recovery, Strength, etc.
    description: str
    distance_km: Optional[float] = None
    pace_min_per_km: Optional[float] = None
    heart_rate_zone: Optional[int] = None
    duration_minutes: Optional[int] = None


class TrainingWeek(BaseModel):
    """Schema para una semana de entrenamiento."""
    week_number: int
    days: List[TrainingDay]
    total_km: float


class TrainingPlanResponse(BaseModel):
    """Schema para la respuesta del plan de entrenamiento."""
    id: str
    name: str
    start_date: str
    end_date: str
    weeks: List[TrainingWeek]
    general_goal: str
    priority: str
    training_days_per_week: int
    plan_duration_weeks: int
    total_volume_km: float
    max_weekly_distance_km: float


