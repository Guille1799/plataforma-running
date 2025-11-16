"""
routers/workouts.py - Endpoints para gestionar entrenamientos y FIT files
"""
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
import fitparse
from io import BytesIO
from datetime import datetime

from .. import crud, schemas, models
from ..database import get_db
from ..security import verify_token
from ..core.config import settings

router = APIRouter(
    prefix="/api/v1/workouts",
    tags=["Workouts"],
)

security_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db)
) -> models.User:
    """Extraer usuario actual desde JWT token."""
    token = credentials.credentials
    payload = verify_token(token, settings.secret_key, settings.algorithm)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    user_id = int(payload.get("sub"))
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user


@router.post("/upload", response_model=schemas.WorkoutOut, status_code=status.HTTP_201_CREATED)
async def upload_fit_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> schemas.WorkoutOut:
    """
    Subir y parsear un archivo FIT de Garmin/Polar.
    
    - Parsea el archivo FIT
    - Extrae métricas: distancia, tiempo, ritmo, freq. cardíaca, etc
    - Guarda en base de datos
    - Retorna detalles del entrenamiento
    
    Args:
        file: Archivo .fit a subir
        db: Database session
        current_user: Usuario autenticado
        
    Returns:
        Workout data con todas las métricas extraídas
        
    Raises:
        HTTPException 400: Si el archivo no es válido FIT
        HTTPException 415: Si el tipo de archivo no es .fit
    """
    # Validar extensión
    if not file.filename.endswith(".fit"):
        raise HTTPException(
            status_code=415,
            detail="File must be a .fit file (Garmin/Polar format)"
        )
    
    # Leer archivo
    content = await file.read()
    
    try:
        # Parsear archivo FIT
        fit_file = fitparse.FitFile(BytesIO(content))
        workout_data = _extract_fit_data(fit_file, file.filename)
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to parse FIT file: {str(e)}"
        )
    
    # Crear workout en BD
    workout = crud.create_workout(
        db,
        current_user.id,
        workout_data,
    )
    
    return schemas.WorkoutOut.model_validate(workout)


@router.post("/create", response_model=schemas.WorkoutOut, status_code=status.HTTP_201_CREATED)
def create_workout(
    workout_data: schemas.WorkoutCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> schemas.WorkoutOut:
    """
    Crear un nuevo entrenamiento manualmente (sin archivo FIT).
    
    Body:
        - start_time: datetime ISO string
        - duration_minutes: enteros
        - distance_meters: float
        - avg_pace: float (min/km)
        - avg_heart_rate: int (bpm)
        - workout_type: str (running, cycling, swimming, etc)
        - notes: str opcional
        
    Returns:
        Workout creado con ID
    """
    workout = crud.create_workout(
        db,
        current_user.id,
        workout_data,
    )
    
    return schemas.WorkoutOut.model_validate(workout)


@router.get("", response_model=List[schemas.WorkoutOut])
def get_workouts(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> List[schemas.WorkoutOut]:
    """
    Obtener listado de entrenamientos del usuario.
    
    Retorna:
        - Últimos entrenamientos (ordenados por fecha descendente)
        - Con paginación (skip/limit)
        - Solo entrenamientos del usuario actual
    
    Args:
        skip: Número de resultados a saltar (default 0)
        limit: Máximo de resultados (default 50, máx 100)
        db: Database session
        current_user: Usuario autenticado
        
    Returns:
        List de Workout objects
    """
    limit = min(limit, 100)  # Máximo 100 resultados
    
    workouts = crud.get_user_workouts(db, current_user.id, limit=limit, offset=skip)
    return [schemas.WorkoutOut.model_validate(w) for w in workouts]


@router.get("/stats", response_model=schemas.WorkoutStats)
def get_stats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> schemas.WorkoutStats:
    """
    Obtener estadísticas agregadas del usuario.
    
    Incluye:
        - Total entrenamientos
        - Distancia total (km)
        - Duración total (horas)
        - Ritmo promedio (min/km)
        - Frecuencia cardíaca promedio
        - Calorías totales
        - Desglose por deporte
    
    Args:
        db: Database session
        current_user: Usuario autenticado
        
    Returns:
        WorkoutStats object
    """
    return crud.get_user_workout_stats(db, current_user.id)


@router.get("/{workout_id}", response_model=schemas.WorkoutOut)
def get_workout(
    workout_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> schemas.WorkoutOut:
    """
    Obtener detalles de un entrenamiento específico.
    
    Args:
        workout_id: ID del entrenamiento
        db: Database session
        current_user: Usuario autenticado
        
    Returns:
        Workout data
        
    Raises:
        HTTPException 404: Si el entrenamiento no existe o no pertenece al usuario
    """
    workout = crud.get_workout_by_id(db, workout_id)
    
    if not workout or workout.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Workout not found")
    
    return schemas.WorkoutOut.model_validate(workout)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _extract_fit_data(fit_file: fitparse.FitFile, filename: str) -> schemas.WorkoutCreate:
    """
    Extraer datos de un archivo FIT parseado.
    
    Extrae:
        - Tipo de deporte
        - Tiempo inicio/duración
        - Distancia total
        - Métricas cardiácas (avg/max heart rate)
        - Ritmo promedio
        - Velocidad máxima
        - Calorías
        - Ganancia de elevación
    
    Args:
        fit_file: FitFile object parseado
        filename: Nombre original del archivo
        
    Returns:
        WorkoutCreate schema con datos extraídos
    """
    messages = fit_file.messages
    
    # Valores por defecto
    sport_type = "running"
    start_time = datetime.utcnow()
    duration_seconds = 0
    distance_meters = 0.0
    avg_heart_rate = None
    max_heart_rate = None
    avg_pace = None
    max_speed = 0.0
    calories = 0.0
    elevation_gain = 0.0
    
    heart_rates = []
    speeds = []
    
    # Procesar mensajes del archivo FIT
    for message in messages:
        if message.name == "file_id":
            for field in message.fields:
                if field.name == "type":
                    sport_map = {
                        "running": "running",
                        "cycling": "cycling",
                        "swimming": "swimming",
                        "walking": "walking",
                    }
                    sport_type = sport_map.get(str(field.value).lower(), "running")
        
        elif message.name == "session":
            for field in message.fields:
                if field.name == "start_time":
                    start_time = field.value
                elif field.name == "total_elapsed_time":
                    duration_seconds = int(field.value)
                elif field.name == "total_distance":
                    distance_meters = float(field.value)
                elif field.name == "avg_heart_rate":
                    avg_heart_rate = int(field.value)
                elif field.name == "max_heart_rate":
                    max_heart_rate = int(field.value)
                elif field.name == "calories":
                    calories = float(field.value)
                elif field.name == "total_ascent":
                    elevation_gain = float(field.value)
        
        elif message.name == "record":
            # Recopilar datos de cada record
            for field in message.fields:
                if field.name == "heart_rate" and field.value:
                    heart_rates.append(int(field.value))
                elif field.name == "speed" and field.value:
                    speeds.append(float(field.value))
    
    # Calcular promedios si no están en session
    if heart_rates and not avg_heart_rate:
        avg_heart_rate = int(sum(heart_rates) / len(heart_rates))
    if heart_rates and not max_heart_rate:
        max_heart_rate = max(heart_rates)
    if speeds:
        max_speed = max(speeds)
    
    # Calcular ritmo promedio (segundos por km)
    if duration_seconds > 0 and distance_meters > 0:
        avg_pace = (duration_seconds / (distance_meters / 1000))
    
    return schemas.WorkoutCreate(
        sport_type=sport_type,
        start_time=start_time,
        duration_seconds=duration_seconds,
        distance_meters=distance_meters,
        avg_heart_rate=avg_heart_rate,
        max_heart_rate=max_heart_rate,
        avg_pace=avg_pace,
        max_speed=max_speed,
        calories=calories if calories > 0 else None,
        elevation_gain=elevation_gain if elevation_gain > 0 else None,
        file_name=filename,
    )
