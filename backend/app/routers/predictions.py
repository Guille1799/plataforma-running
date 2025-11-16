"""
Race Predictions Router

Endpoints for predicting race times using VDOT and Riegel formulas.
Also provides training pace zones based on current fitness.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel, Field

from app.database import get_db
from app.models import User
from app.security import verify_token
from app.core.config import settings
from app.services.race_predictor_service import RacePredictorService

router = APIRouter(prefix="/api/v1/predictions", tags=["predictions"])
race_predictor_service = RacePredictorService()
security_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Extract current user from JWT token."""
    token = credentials.credentials
    payload = verify_token(token, settings.secret_key, settings.algorithm)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    user_id = int(payload.get("sub"))
    from app import crud
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user


# ==================== Schemas ====================

class PredictRacesRequest(BaseModel):
    """Request schema for race time predictions."""
    
    base_distance_km: Optional[float] = Field(
        None,
        ge=1.0,
        le=100.0,
        description="Base distance in km (if not provided, uses best recent performance)"
    )
    base_time_minutes: Optional[float] = Field(
        None,
        ge=1.0,
        le=600.0,
        description="Base time in minutes (required if base_distance_km provided)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "base_distance_km": 10.0,
                "base_time_minutes": 48.5
            }
        }


class RacePrediction(BaseModel):
    """Single race distance prediction."""
    
    predicted_time_minutes: float
    predicted_time_formatted: str  # "3:45:30"
    predicted_pace: str  # "5:21/km"
    confidence: str  # high, medium, low


class TrainingPaces(BaseModel):
    """Training pace zones based on VDOT."""
    
    easy: str  # "6:00-6:30/km"
    marathon: str  # "5:21/km"
    threshold: str  # "4:50/km"
    interval: str  # "4:30/km"
    repetition: str  # "4:15/km"


class BasePerformance(BaseModel):
    """Base performance used for predictions."""
    
    distance_km: float
    time_minutes: float
    pace: str
    date: str


class PredictionsResponse(BaseModel):
    """Complete race predictions response."""
    
    success: bool
    message: str
    predictions: dict[str, RacePrediction]
    vdot: float
    base_performance: BasePerformance
    training_paces: TrainingPaces
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Race times predicted successfully",
                "predictions": {
                    "5K": {
                        "predicted_time_minutes": 22.5,
                        "predicted_time_formatted": "22:30",
                        "predicted_pace": "4:30/km",
                        "confidence": "high"
                    },
                    "Marathon": {
                        "predicted_time_minutes": 225.6,
                        "predicted_time_formatted": "3:45:36",
                        "predicted_pace": "5:21/km",
                        "confidence": "low"
                    }
                },
                "vdot": 52.3,
                "base_performance": {
                    "distance_km": 10.0,
                    "time_minutes": 48.0,
                    "pace": "4:48/km",
                    "date": "2025-11-01"
                },
                "training_paces": {
                    "easy": "6:00-6:30/km",
                    "marathon": "5:21/km",
                    "threshold": "4:50/km",
                    "interval": "4:30/km",
                    "repetition": "4:15/km"
                }
            }
        }


class VDOTResponse(BaseModel):
    """VDOT calculation response."""
    
    success: bool
    vdot: float
    vo2max_equivalent: float
    fitness_level: str  # beginner, intermediate, advanced, competitive, elite


class VDOTCalculateRequest(BaseModel):
    """Request schema for VDOT calculation via POST."""
    
    distance: float = Field(..., ge=1.0, le=100000.0, description="Distance in meters")
    time_seconds: float = Field(..., ge=1.0, le=36000.0, description="Time in seconds")


# ==================== Endpoints ====================

@router.post("/vdot", response_model=VDOTResponse)
def calculate_vdot_post(
    request: VDOTCalculateRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Calculate VDOT (VO2max equivalent) from a race performance via POST.
    
    VDOT is Jack Daniels' training intensity metric that accounts for:
    - VO2max (aerobic capacity)
    - Running economy (efficiency)
    
    ## VDOT Scale:
    - **30-40**: Beginner (recreational runner)
    - **40-50**: Intermediate (regular trainer)
    - **50-60**: Advanced (competitive runner)
    - **60-70**: Elite (sub-3:00 marathon)
    - **70+**: World-class
    
    **Requires authentication**
    """
    try:
        # Convert meters to km and seconds to minutes
        distance_km = request.distance / 1000.0
        time_minutes = request.time_seconds / 60.0
        
        vdot = race_predictor_service._calculate_vdot(
            distance_km=distance_km,
            time_minutes=time_minutes
        )
        
        # Determine fitness level
        if vdot < 35:
            fitness_level = "beginner"
        elif vdot < 45:
            fitness_level = "intermediate"
        elif vdot < 55:
            fitness_level = "advanced"
        elif vdot < 65:
            fitness_level = "competitive"
        else:
            fitness_level = "elite"
        
        # VO2max approximation (VDOT ≈ VO2max for most runners)
        vo2max = vdot * 1.05
        
        return VDOTResponse(
            success=True,
            vdot=round(vdot, 1),
            vo2max_equivalent=round(vo2max, 1),
            fitness_level=fitness_level
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate VDOT: {str(e)}"
        )


@router.get("/vdot", response_model=VDOTResponse)
def predict_race_times(
    request: PredictRacesRequest = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Predict race times for 5K, 10K, 15K, Half Marathon, and Marathon.
    
    Uses scientifically proven formulas:
    - **VDOT** (Jack Daniels): VO2max-based fitness indicator
    - **Riegel Formula**: Race time prediction with 1.06 fatigue factor
    
    ## Input Options:
    
    1. **Automatic** (no parameters):
       - Uses your best recent performance (last 60 days)
       - Ideal for regular runners with consistent training
    
    2. **Manual** (provide both parameters):
       - `base_distance_km`: Known race distance (e.g., 10.0 for 10K)
       - `base_time_minutes`: Your time for that distance (e.g., 48.5)
       - Use this for race-specific predictions
    
    ## Output:
    
    - Predicted times for 5 standard distances
    - Confidence levels (high/medium/low)
    - VDOT score
    - Training pace zones (Easy, Marathon, Threshold, Interval, Repetition)
    
    ## Confidence Levels:
    
    - **High**: Target distance ≤ 2x base distance (e.g., 10K → Half)
    - **Medium**: Target distance 2-4x base distance (e.g., 10K → Marathon)
    - **Low**: Large extrapolation (e.g., 5K → Marathon)
    
    **Requires authentication**
    """
    try:
        # Extract optional parameters
        base_distance = None
        base_time = None
        
        if request:
            base_distance = request.base_distance_km
            base_time = request.base_time_minutes
        
        # Validate: if one is provided, both must be provided
        if (base_distance is None) != (base_time is None):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Both base_distance_km and base_time_minutes must be provided together, or neither"
            )
        
        # Get predictions
        result = race_predictor_service.predict_race_times(
            user_id=current_user.id,
            base_distance_km=base_distance,
            base_time_minutes=base_time,
            db=db
        )
        
        return PredictionsResponse(
            success=True,
            message="Race times predicted successfully using " + 
                    ("provided base performance" if base_distance else "best recent performance"),
            predictions=result["predictions"],
            vdot=result["vdot"],
            base_performance=result["base_performance"],
            training_paces=result["training_paces"]
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to predict race times: {str(e)}"
        )


@router.get("/vdot", response_model=VDOTResponse)
def calculate_vdot(
    distance_km: float = Query(..., ge=1.0, le=100.0, description="Race distance in kilometers"),
    time_minutes: float = Query(..., ge=1.0, le=600.0, description="Race time in minutes"),
    current_user: User = Depends(get_current_user)
):
    """
    Calculate VDOT (VO2max equivalent) from a race performance.
    
    VDOT is Jack Daniels' training intensity metric that accounts for:
    - VO2max (aerobic capacity)
    - Running economy (efficiency)
    
    ## VDOT Scale:
    - **30-40**: Beginner (recreational runner)
    - **40-50**: Intermediate (regular trainer)
    - **50-60**: Advanced (competitive runner)
    - **60-70**: Elite (sub-3:00 marathon)
    - **70+**: World-class
    
    ## Examples:
    - 10K in 50 minutes → VDOT ~45 (intermediate)
    - 10K in 40 minutes → VDOT ~55 (advanced)
    - Marathon in 3:30 → VDOT ~50 (intermediate/advanced)
    
    **Requires authentication**
    """
    try:
        distance_meters = distance_km * 1000
        time_seconds = time_minutes * 60
        
        vdot = race_predictor_service._calculate_vdot(distance_meters, time_seconds)
        
        # Determine fitness level
        if vdot < 35:
            fitness_level = "beginner"
        elif vdot < 45:
            fitness_level = "intermediate"
        elif vdot < 55:
            fitness_level = "advanced"
        elif vdot < 65:
            fitness_level = "competitive"
        else:
            fitness_level = "elite"
        
        # VO2max approximation (VDOT ≈ VO2max for most runners)
        vo2max = vdot * 1.05  # Slight adjustment for typical running economy
        
        return VDOTResponse(
            success=True,
            vdot=round(vdot, 1),
            vo2max_equivalent=round(vo2max, 1),
            fitness_level=fitness_level
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate VDOT: {str(e)}"
        )


@router.get("/training-paces", response_model=TrainingPaces)
def get_training_paces(
    vdot: float = Query(..., ge=20.0, le=90.0, description="VDOT score (use /vdot endpoint to calculate)"),
    current_user: User = Depends(get_current_user)
):
    """
    Get training pace zones based on VDOT.
    
    Returns optimal paces for 5 training zones:
    
    1. **Easy**: 65-79% effort, conversational pace
       - Purpose: Aerobic base, recovery
       - Volume: 60-80% of weekly training
    
    2. **Marathon**: 80-89% effort, goal marathon pace
       - Purpose: Race-specific endurance
       - Volume: 10-20% of weekly training
    
    3. **Threshold**: 90-92% effort, comfortably hard
       - Purpose: Lactate threshold improvement
       - Volume: 8-10% of weekly training
    
    4. **Interval**: 95-100% effort, VO2max work
       - Purpose: Aerobic capacity
       - Volume: 5-8% of weekly training
    
    5. **Repetition**: 105-110% effort, speed work
       - Purpose: Running economy, neuromuscular
       - Volume: 2-5% of weekly training
    
    **Requires authentication**
    """
    try:
        paces = race_predictor_service.get_training_paces(vdot)
        
        return TrainingPaces(**paces)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate training paces: {str(e)}"
        )


@router.get("/distances")
def get_supported_distances(
    current_user: User = Depends(get_current_user)
):
    """
    Get list of supported race distances for predictions.
    
    Returns standard distances with common race names.
    
    **Requires authentication**
    """
    return {
        "success": True,
        "distances": [
            {
                "key": "5K",
                "distance_km": 5.0,
                "name": "5 Kilometers",
                "common_races": ["parkrun", "5K road race"]
            },
            {
                "key": "10K",
                "distance_km": 10.0,
                "name": "10 Kilometers",
                "common_races": ["10K road race", "10000m track"]
            },
            {
                "key": "15K",
                "distance_km": 15.0,
                "name": "15 Kilometers",
                "common_races": ["15K road race"]
            },
            {
                "key": "Half_Marathon",
                "distance_km": 21.0975,
                "name": "Half Marathon",
                "common_races": ["Half marathon", "21K"]
            },
            {
                "key": "Marathon",
                "distance_km": 42.195,
                "name": "Marathon",
                "common_races": ["Marathon", "42K"]
            }
        ]
    }
