"""
Enhanced Race Prediction API Router
Endpoints for race prediction with environmental factors
"""
from fastapi import APIRouter, Depends, Query, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.database import get_db
from app import models, crud
from app.security import verify_token
from app.core.config import settings
from app.services.race_prediction_enhanced_service import (
    RacePredictionEnhancedService,
    TerrainType,
    WeatherCondition,
)


router = APIRouter(prefix="/api/v1/race", tags=["race-predictions"])
race_service = RacePredictionEnhancedService()
security_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db)
) -> models.User:
    """Extract current user from JWT token."""
    token = credentials.credentials
    payload = verify_token(token, settings.secret_key, settings.algorithm)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    user_id = int(payload.get("sub"))
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user


@router.post("/predict-with-conditions")
async def predict_race_with_conditions(
    base_distance_km: float = Query(..., gt=0, le=50),
    base_time_minutes: float = Query(..., gt=0, le=600),
    target_distance_km: float = Query(..., gt=0, le=50),
    terrain: TerrainType = Query(TerrainType.ROLLING),
    altitude_m: int = Query(0, ge=0, le=5000),
    temperature_c: Optional[float] = Query(None, ge=-20, le=50),
    humidity_pct: Optional[float] = Query(None, ge=0, le=100),
    wind_kmh: Optional[float] = Query(None, ge=0, le=80),
    weather_condition: Optional[str] = Query(None),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """
    Predict race time with environmental adjustments.
    
    **Parameters:**
    - `base_distance_km`: Your recent race/test distance (3-42 km)
    - `base_time_minutes`: Time for base race
    - `target_distance_km`: Target race distance
    - `terrain`: Track type (flat/rolling/hilly/mountain)
    - `altitude_m`: Race altitude above sea level
    - `temperature_c`: Expected temperature at race
    - `humidity_pct`: Expected humidity percentage
    - `wind_kmh`: Expected wind speed (assume headwind)
    - `weather_condition`: Overall condition (ideal/good/fair/poor)
    
    **Response:**
    - Adjusted prediction with all environmental factors
    - Individual adjustment factor percentages
    - Confidence score (0-100)
    - Actionable race recommendations
    
    **Example:**
    ```
    GET /api/v1/race/predict-with-conditions?
        base_distance_km=10&
        base_time_minutes=45&
        target_distance_km=21.1&
        terrain=rolling&
        temperature_c=18&
        humidity_pct=55&
        wind_kmh=12
    
    Response:
    {
      "prediction": {
        "adjusted_prediction_minutes": 95.8,
        "formatted_time": "01:35:48",
        "formatted_pace": "04:33 /km"
      },
      "adjustments": {
        "weather_factor": 1.0180,
        "terrain_factor": 1.0000,
        "altitude_factor": 1.0000,
        "adjustment_percentage": 1.8
      },
      "confidence": {
        "score": 78.5,
        "level": "high"
      },
      "recommendations": [...]
    }
    ```
    """
    try:
        # Prepare weather data
        weather = {}
        if temperature_c is not None:
            weather["temp_c"] = temperature_c
        if humidity_pct is not None:
            weather["humidity_pct"] = humidity_pct
        if wind_kmh is not None:
            weather["wind_kmh"] = wind_kmh
        if weather_condition:
            weather["condition"] = weather_condition
        
        # Get prediction
        result = race_service.predict_with_conditions(
            db=db,
            user_id=current_user.id,
            base_time_minutes=base_time_minutes,
            base_distance_km=base_distance_km,
            target_distance_km=target_distance_km,
            weather=weather if weather else None,
            terrain=terrain,
            altitude_m=altitude_m,
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Prediction failed: {str(e)}"
        )


@router.get("/conditions-impact")
async def get_conditions_impact(
    current_user: models.User = Depends(get_current_user),
) -> dict:
    """
    Get information about how conditions impact race performance.
    
    **Response:**
    - Weather factors (temperature, humidity, wind)
    - Terrain difficulty multipliers
    - Altitude impact calculation
    - Confidence scoring methodology
    
    **Example Response:**
    ```json
    {
      "weather_factors": {
        "temperature": {
          "optimal_min": 10,
          "optimal_max": 15,
          "impact": "1% slower per 2°C below optimal, 2% per °C above"
        },
        "humidity": {
          "optimal_min": 40,
          "optimal_max": 60,
          "impact": "0.5% per 1% humidity above optimal"
        },
        "wind": {
          "threshold_kmh": 15,
          "impact": "1% slower per km/h above threshold (headwind assumed)"
        }
      },
      "terrain_multipliers": {
        "flat": 0.98,
        "rolling": 1.00,
        "hilly": 1.04,
        "mountain": 1.08
      },
      "altitude": {
        "threshold_m": 1500,
        "max_impact": 0.15,
        "calculation": "Linear above threshold"
      }
    }
    ```
    """
    return {
        "weather_factors": {
            "temperature": {
                "optimal_min_c": 10,
                "optimal_max_c": 15,
                "impact_formula": "1% slower per 2°C below, 2% per °C above optimal",
            },
            "humidity": {
                "optimal_min_pct": 40,
                "optimal_max_pct": 60,
                "impact_formula": "0.5% slower per 1% above optimal",
            },
            "wind": {
                "threshold_kmh": 15,
                "impact_formula": "1% slower per km/h above threshold (headwind)",
            },
        },
        "terrain_multipliers": {
            "flat": 0.98,  # 2% faster
            "rolling": 1.00,  # Baseline
            "hilly": 1.04,  # 4% slower
            "mountain": 1.08,  # 8% slower
        },
        "altitude": {
            "threshold_m": 1500,
            "impact_formula": "Linear increase above threshold",
            "max_impact_pct": 15,
        },
        "confidence_scoring": {
            "distance_match": "40 points - higher when base and target distances close",
            "conditions": "60 points - higher with favorable conditions",
            "levels": [
                {"score": 85, "level": "very_high"},
                {"score": 70, "level": "high"},
                {"score": 55, "level": "moderate"},
                {"score": 40, "level": "low"},
                {"score": 0, "level": "very_low"},
            ],
        },
    }


@router.get("/terrain-guide")
async def get_terrain_guide(
    current_user: models.User = Depends(get_current_user),
) -> dict:
    """
    Get detailed guidance on terrain types and training strategies.
    
    **Response:**
    - Terrain classification
    - Performance impact percentages
    - Training recommendations
    - Technique tips
    """
    return {
        "terrains": [
            {
                "type": "flat",
                "description": "Road races, track, flat courses",
                "performance_impact": -2,
                "training_focus": "Speed work, tempo runs",
                "tips": "Focus on running efficiency, avoid overstriding",
            },
            {
                "type": "rolling",
                "description": "Mix of flat and slight hills",
                "performance_impact": 0,
                "training_focus": "Balanced training",
                "tips": "Maintain steady effort, practice pacing",
            },
            {
                "type": "hilly",
                "description": "Significant hills, varied elevation",
                "performance_impact": 4,
                "training_focus": "Hill repeats, leg strength",
                "tips": "Reduce stride on uphills, lean on downhills",
            },
            {
                "type": "mountain",
                "description": "Major climbs, high elevation changes",
                "performance_impact": 8,
                "training_focus": "Power development, VO2max",
                "tips": "Walk steep sections, control descent, mental toughness",
            },
        ]
    }


@router.post("/scenario-comparison")
async def compare_race_scenarios(
    base_distance_km: float = Query(..., gt=0),
    base_time_minutes: float = Query(..., gt=0),
    target_distance_km: float = Query(..., gt=0),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """
    Compare predictions across different race conditions.
    
    **Response:**
    - Best case scenario (ideal conditions)
    - Worst case scenario (poor conditions)
    - Realistic scenario (average conditions)
    - Range of possible outcomes
    
    **Example:**
    ```
    Comparing Marathon predictions:
    Best case (cool, flat): 3:45:00
    Realistic (10°C, rolling): 3:52:15
    Worst case (25°C, hilly): 4:05:30
    Confidence: High (80%)
    ```
    """
    try:
        # Best case: ideal conditions
        best_case = race_service.predict_with_conditions(
            db=db,
            user_id=current_user.id,
            base_time_minutes=base_time_minutes,
            base_distance_km=base_distance_km,
            target_distance_km=target_distance_km,
            weather={
                "temp_c": 12,
                "humidity_pct": 50,
                "wind_kmh": 0,
                "condition": "ideal",
            },
            terrain=TerrainType.FLAT,
            altitude_m=0,
        )
        
        # Realistic case: typical conditions
        realistic_case = race_service.predict_with_conditions(
            db=db,
            user_id=current_user.id,
            base_time_minutes=base_time_minutes,
            base_distance_km=base_distance_km,
            target_distance_km=target_distance_km,
            weather={
                "temp_c": 15,
                "humidity_pct": 55,
                "wind_kmh": 10,
                "condition": "good",
            },
            terrain=TerrainType.ROLLING,
            altitude_m=0,
        )
        
        # Worst case: challenging conditions
        worst_case = race_service.predict_with_conditions(
            db=db,
            user_id=current_user.id,
            base_time_minutes=base_time_minutes,
            base_distance_km=base_distance_km,
            target_distance_km=target_distance_km,
            weather={
                "temp_c": 25,
                "humidity_pct": 80,
                "wind_kmh": 20,
                "condition": "poor",
            },
            terrain=TerrainType.HILLY,
            altitude_m=500,
        )
        
        return {
            "scenarios": {
                "best_case": {
                    "prediction_minutes": best_case["prediction"]["adjusted_prediction_minutes"],
                    "formatted_time": best_case["prediction"]["formatted_time"],
                    "conditions": best_case["conditions"],
                },
                "realistic_case": {
                    "prediction_minutes": realistic_case["prediction"]["adjusted_prediction_minutes"],
                    "formatted_time": realistic_case["prediction"]["formatted_time"],
                    "conditions": realistic_case["conditions"],
                },
                "worst_case": {
                    "prediction_minutes": worst_case["prediction"]["adjusted_prediction_minutes"],
                    "formatted_time": worst_case["prediction"]["formatted_time"],
                    "conditions": worst_case["conditions"],
                },
            },
            "range": {
                "min_minutes": best_case["prediction"]["adjusted_prediction_minutes"],
                "max_minutes": worst_case["prediction"]["adjusted_prediction_minutes"],
                "difference_minutes": worst_case["prediction"]["adjusted_prediction_minutes"] - best_case["prediction"]["adjusted_prediction_minutes"],
                "time_variance_percentage": round(
                    (worst_case["prediction"]["adjusted_prediction_minutes"] - best_case["prediction"]["adjusted_prediction_minutes"]) / 
                    realistic_case["prediction"]["adjusted_prediction_minutes"] * 100,
                    1
                ),
            },
            "average_confidence": (
                best_case["confidence"]["score"] + 
                realistic_case["confidence"]["score"] + 
                worst_case["confidence"]["score"]
            ) / 3,
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Scenario comparison failed: {str(e)}"
        )
