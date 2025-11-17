"""
Training Recommendations API Router
Endpoints for AI-powered adaptive training plans
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
from app.services.training_recommendations_service import (
    TrainingRecommendationsService,
    TrainingPhase,
    IntensityZone,
)


router = APIRouter(prefix="/api/v1/training", tags=["training-recommendations"])
training_service = TrainingRecommendationsService()
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


@router.get("/weekly-plan")
async def get_weekly_plan(
    fatigue_score: float = Query(50, ge=0, le=100),
    readiness_score: float = Query(50, ge=0, le=100),
    phase: TrainingPhase = Query(TrainingPhase.BUILD),
    max_hr: int = Query(190, ge=100, le=250),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """
    Generate adaptive weekly training plan.
    
    **Parameters:**
    - `fatigue_score`: Current fatigue level (0=fresh, 100=exhausted) - typically from HRV analysis
    - `readiness_score`: Recovery readiness (0=not ready, 100=peak) - from sleep + recovery tracking
    - `phase`: Training phase (base/build/peak/taper/recovery)
    - `max_hr`: Your maximum heart rate (used for zone calculations)
    
    **Response:**
    - 7 daily workouts with intensity zones
    - Total weekly load in minutes/hours
    - Adaptive recommendations based on fatigue/readiness
    - Injury prevention strategies
    - Next week adjustments
    
    **Example:**
    ```
    GET /api/v1/training/weekly-plan?
        fatigue_score=45&
        readiness_score=75&
        phase=build&
        max_hr=190
    
    Response:
    {
      "week_plan": {
        "phase": "build",
        "total_load_minutes": 165,
        "daily_workouts": [
          {
            "day": 1,
            "day_name": "Monday",
            "type": "easy",
            "duration_minutes": 30,
            "primary_zone": "z2",
            "zone_range_bpm": {"min": 114, "max": 133},
            "description": "30 min easy-paced run...",
            "adaptive_notes": "Standard workout"
          },
          ...
        ]
      },
      "athlete_status": {
        "fatigue_score": 45.0,
        "status": "🟢 READY - Good to push"
      },
      "recommendations": [
        "🟢 Low fatigue (45%) - You can handle challenging workouts",
        "🟢 READY - Good to push",
        "🎯 Build phase: Mix of speed work and endurance..."
      ],
      "weekly_metrics": {
        "total_duration": 2.75,
        "sessions_per_week": 7,
        "intensity_distribution": {...}
      }
    }
    ```
    
    **Intensity Zones Explanation:**
    - **Z1 (Recovery)**: 50-60% max HR - very easy, conversational pace
    - **Z2 (Aerobic)**: 60-70% max HR - comfortable, buildaerobicbase
    - **Z3 (Tempo)**: 70-80% max HR - moderate hard, can speak few words
    - **Z4 (Threshold)**: 80-90% max HR - hard, near lactate threshold
    - **Z5 (Interval)**: 90-100% max HR - very hard, sprint efforts
    """
    try:
        result = training_service.generate_weekly_plan(
            db=db,
            user_id=current_user.id,
            fatigue_score=fatigue_score,
            readiness_score=readiness_score,
            phase=phase,
            max_hr=max_hr,
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Plan generation failed: {str(e)}"
        )


@router.get("/phases-guide")
async def get_training_phases_guide(
    current_user: models.User = Depends(get_current_user),
) -> dict:
    """
    Get comprehensive guide to training phases.
    
    **Response:**
    - Purpose of each phase
    - Duration recommendations
    - Zone distribution
    - Typical weekly load
    - Key workouts
    - Progression markers
    
    **Example Response:**
    ```json
    {
      "phases": [
        {
          "name": "Base",
          "duration_weeks": "8-12",
          "purpose": "Build aerobic foundation, injury prevention",
          "zone_distribution": {
            "z1": 20,
            "z2": 70,
            "z3": 10,
            "z4": 0,
            "z5": 0
          },
          "weekly_load_hours": "2-3",
          "key_workouts": [
            "Long slow distance (LSD) runs",
            "Easy recovery runs",
            "Tempo runs introduction",
            "Core strength training"
          ],
          "goal_markers": [
            "Improved aerobic efficiency",
            "Lower resting heart rate",
            "Better recovery between workouts",
            "Increased running volume tolerance"
          ]
        },
        ...
      ]
    }
    ```
    """
    return {
        "phases": [
            {
                "name": "Base",
                "duration_weeks": "8-12",
                "purpose": "Build aerobic foundation, improve running economy, prevent injury",
                "zone_distribution": {
                    "z1_recovery": 20,
                    "z2_aerobic": 70,
                    "z3_tempo": 10,
                    "z4_threshold": 0,
                    "z5_interval": 0,
                },
                "weekly_load_hours": "2-3",
                "key_workouts": [
                    "Long slow distance (LSD) - 1-2x per week",
                    "Easy runs - conversational pace",
                    "Recovery runs - focus on form",
                    "Strength training - 2x per week",
                ],
                "progression_markers": [
                    "Can run longer distances easily",
                    "Resting heart rate decreases",
                    "Better recovery between sessions",
                    "Improved running form consistency",
                ],
            },
            {
                "name": "Build",
                "duration_weeks": "6-10",
                "purpose": "Increase intensity, develop lactate threshold, improve VO2max",
                "zone_distribution": {
                    "z1_recovery": 15,
                    "z2_aerobic": 55,
                    "z3_tempo": 15,
                    "z4_threshold": 10,
                    "z5_interval": 5,
                },
                "weekly_load_hours": "2.5-3.5",
                "key_workouts": [
                    "Tempo runs - 20-30min at threshold",
                    "Interval training - 6-8x3-5min repeats",
                    "Fartlek training - unstructured speed play",
                    "Long runs with tempo portions",
                ],
                "progression_markers": [
                    "Can sustain higher intensities",
                    "Improved speed at aerobic pace",
                    "Better lactate clearance",
                    "Increased HRV stability",
                ],
            },
            {
                "name": "Peak",
                "duration_weeks": "3-4",
                "purpose": "Race-specific preparation, peak fitness, mental preparation",
                "zone_distribution": {
                    "z1_recovery": 10,
                    "z2_aerobic": 40,
                    "z3_tempo": 20,
                    "z4_threshold": 15,
                    "z5_interval": 15,
                },
                "weekly_load_hours": "3-4",
                "key_workouts": [
                    "Race-pace efforts - practice target pace",
                    "Interval workouts - maintain VO2max",
                    "Long runs - race simulation",
                    "Tempo runs - race-specific intensity",
                ],
                "progression_markers": [
                    "Feeling strong and confident",
                    "Target race pace feels sustainable",
                    "Mental readiness high",
                    "No fatigue accumulation",
                ],
            },
            {
                "name": "Taper",
                "duration_weeks": "2-3",
                "purpose": "Reduce volume, maintain fitness, maximize freshness for race",
                "zone_distribution": {
                    "z1_recovery": 40,
                    "z2_aerobic": 40,
                    "z3_tempo": 10,
                    "z4_threshold": 5,
                    "z5_interval": 5,
                },
                "weekly_load_hours": "1.5-2.5",
                "key_workouts": [
                    "Easy runs - recover and stay sharp",
                    "Short strides - maintain leg turnover",
                    "One race-pace effort - 10-15min",
                    "Complete rest days - focus on sleep",
                ],
                "progression_markers": [
                    "Feeling fresh and energetic",
                    "Mental anxiety rising (normal)",
                    "Improved sleep quality",
                    "Body feels light and reactive",
                ],
            },
            {
                "name": "Recovery",
                "duration_weeks": "1-2",
                "purpose": "Allow full physical and mental recovery, prepare for next cycle",
                "zone_distribution": {
                    "z1_recovery": 70,
                    "z2_aerobic": 30,
                    "z3_tempo": 0,
                    "z4_threshold": 0,
                    "z5_interval": 0,
                },
                "weekly_load_hours": "1-2",
                "key_workouts": [
                    "Easy recovery runs - 20-30min max",
                    "Walking - active recovery",
                    "Cross-training - swimming, cycling",
                    "Complete rest days - multiple per week",
                ],
                "progression_markers": [
                    "Fully recovered from previous race/cycle",
                    "Motivation returning",
                    "Ready to start next training block",
                    "HRV normalized to baseline",
                ],
            },
        ]
    }


@router.get("/intensity-zones")
async def get_intensity_zones_info(
    max_hr: int = Query(190, ge=100, le=250),
    current_user: models.User = Depends(get_current_user),
) -> dict:
    """
    Get detailed intensity zones information for given max HR.
    
    **Parameters:**
    - `max_hr`: Your maximum heart rate
    
    **Response:**
    - BPM ranges for each zone
    - Perceived exertion (RPE)
    - Breathing descriptions
    - Training adaptations
    - When to use each zone
    """
    zones_detail = []
    
    for zone, (min_pct, max_pct) in TrainingRecommendationsService.ZONE_RANGES.items():
        zones_detail.append({
            "zone": zone.value,
            "name": zone.name.replace("_", " "),
            "heart_rate_range": {
                "min_bpm": int(max_hr * min_pct),
                "max_bpm": int(max_hr * max_pct),
                "percentage_max": f"{int(min_pct*100)}-{int(max_pct*100)}%",
            },
            "perceived_exertion": {
                "z1": {"rpe": "1-2/10", "description": "Very easy, can sing"},
                "z2": {"rpe": "3-5/10", "description": "Easy, can talk"},
                "z3": {"rpe": "6-7/10", "description": "Moderate, speak few words"},
                "z4": {"rpe": "8-9/10", "description": "Hard, few words only"},
                "z5": {"rpe": "9-10/10", "description": "Maximum effort, can't speak"},
            }.get(zone.value),
            "breathing": {
                "z1": "Relaxed, normal breathing",
                "z2": "Comfortable breathing, rhythmic",
                "z3": "Elevated, steady breathing",
                "z4": "Heavy, labored breathing",
                "z5": "Maximum, gasping",
            }.get(zone.value),
            "training_benefit": {
                "z1": "Active recovery, reduces stress, promotes blood flow",
                "z2": "Aerobic fitness, fat burning, builds base",
                "z3": "Improves aerobic capacity, teaches race pace",
                "z4": "Increases lactate threshold, VO2max",
                "z5": "Develops speed, anaerobic capacity, sprint power",
            }.get(zone.value),
            "frequency_per_week": {
                "z1": "1-2 times",
                "z2": "3-4 times",
                "z3": "1-2 times",
                "z4": "1 time",
                "z5": "1 time",
            }.get(zone.value),
        })
    
    return {
        "zones": zones_detail,
        "note": "RPE = Perceived Exertion (Rate of Perceived Exertion, 1-10 scale)",
        "zones_summary": {
            "total_zones": 5,
            "recommendation": "Most training (70-80%) should be in Z1-Z2 to build aerobic base",
            "key_insight": "Long, easy runs build more fitness with less injury risk than hard running",
        },
    }


@router.post("/adaptive-adjustment")
async def get_adaptive_adjustment(
    current_fatigue: float = Query(..., ge=0, le=100),
    previous_workout_stress: float = Query(50, ge=0, le=100),
    sleep_hours: float = Query(7, ge=0, le=16),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """
    Get adaptive training adjustment recommendation.
    
    **Parameters:**
    - `current_fatigue`: Your current fatigue level (0=fresh, 100=exhausted)
    - `previous_workout_stress`: Stress from previous workout (0-100)
    - `sleep_hours`: Hours of sleep last night
    
    **Response:**
    - Recommendation to increase/maintain/decrease training
    - Specific workout modifications
    - Recovery suggestions
    - Timeline for adjustment
    
    **Example:**
    ```
    POST /api/v1/training/adaptive-adjustment?
        current_fatigue=65&
        previous_workout_stress=75&
        sleep_hours=6.5
    
    Response:
    {
      "recommendation": "DECREASE",
      "reason": "High fatigue (65%) + Hard previous workout (75%) + Insufficient sleep (6.5hrs)",
      "adjustment": {
        "decrease_volume_by_percent": 20,
        "decrease_intensity_by_percent": 15,
        "add_recovery_days": 1
      },
      "suggested_workouts": [
        "Easy 30min run in Z2",
        "Complete rest day",
        "Cross-training: swimming or cycling"
      ],
      "recovery_focus": [
        "Get 8+ hours sleep tonight",
        "Focus on nutrition: carbs and protein",
        "Foam rolling and stretching"
      ]
    }
    ```
    """
    # Calculate adjustment recommendation
    stress_index = (current_fatigue * 0.5) + (previous_workout_stress * 0.3) + ((8 - sleep_hours) * 5)
    
    if stress_index > 70:
        recommendation = "DECREASE"
        intensity_adjustment = -15
        volume_adjustment = -20
        recovery_focus = "High priority recovery"
    elif stress_index > 50:
        recommendation = "MAINTAIN"
        intensity_adjustment = 0
        volume_adjustment = 0
        recovery_focus = "Standard recovery"
    else:
        recommendation = "INCREASE"
        intensity_adjustment = 10
        volume_adjustment = 10
        recovery_focus = "Minimal recovery needed"
    
    return {
        "recommendation": recommendation,
        "stress_index": round(stress_index, 1),
        "factors": {
            "current_fatigue": current_fatigue,
            "previous_stress": previous_workout_stress,
            "sleep_hours": sleep_hours,
            "sleep_deficit": max(0, 8 - sleep_hours),
        },
        "adjustment": {
            "intensity_change_percent": intensity_adjustment,
            "volume_change_percent": volume_adjustment,
            "recovery_priority": recovery_focus,
        },
        "suggested_actions": {
            "today": (
                "Take a complete rest day - prioritize recovery" if recommendation == "DECREASE"
                else "Easy run or cross-training" if recommendation == "MAINTAIN"
                else "Good day for a harder workout"
            ),
            "this_week": (
                "Reduce intensity, add extra recovery days" if recommendation == "DECREASE"
                else "Follow normal training plan" if recommendation == "MAINTAIN"
                else "Push intensity, take advantage of good form"
            ),
            "recovery_strategies": [
                "Aim for 8+ hours sleep (crucial for adaptation)",
                "Eat 1.2-1.6g protein per kg body weight",
                "Hydrate well (urine should be pale yellow)",
                "Do 10min foam rolling daily",
                "Consider compression garments",
            ] if recommendation == "DECREASE" else [
                "Maintain sleep schedule (7-9 hours)",
                "Balanced nutrition (carbs + protein)",
                "Standard hydration",
                "Light stretching",
            ],
        },
        "timeline": {
            "when_to_reassess": "After your next 2-3 workouts or tomorrow",
            "expected_recovery_days": (
                "3-5 days" if recommendation == "DECREASE"
                else "1-2 days" if recommendation == "MAINTAIN"
                else "0-1 days"
            ),
        },
    }


@router.get("/progress-tracking")
async def get_progress_tracking_guide(
    current_user: models.User = Depends(get_current_user),
) -> dict:
    """
    Get guide for tracking training progress and adaptation.
    
    **Response:**
    - Key metrics to track
    - How to measure improvement
    - What indicates good adaptation
    - Warning signs to watch for
    """
    return {
        "metrics_to_track": {
            "heart_rate": {
                "resting_hr": "Track morning HR before getting up - should decrease over training cycle",
                "hr_recovery": "HR drop 2 min after workout - faster recovery = better fitness",
                "hrv": "Higher HRV = better parasympathetic function = good recovery",
            },
            "performance": {
                "pace_at_z2": "Should be able to run faster at same Z2 heart rate",
                "workout_times": "Same workout distance should get faster each week",
                "vo2max": "Estimated through pace or VDOT calculations",
            },
            "subjective": {
                "perceived_effort": "Workouts should feel easier over time",
                "recovery_feeling": "Should feel recovered between sessions",
                "motivation": "Staying engaged and excited about training",
            },
            "body": {
                "weight": "Should stabilize with consistent training",
                "muscle_tone": "Legs should develop definition",
                "injury_markers": "No increased aches or pains",
            },
        },
        "good_adaptation_signs": [
            "✅ Resting heart rate decreasing by 1-2 BPM each week",
            "✅ Can maintain race pace at lower heart rate",
            "✅ Workouts feel easier (same effort, faster pace)",
            "✅ Recovery HR faster (heart rate drops quickly after workout)",
            "✅ HRV trending upward over weeks",
            "✅ Sleep quality improving",
            "✅ Motivation high, looking forward to workouts",
            "✅ No lingering soreness day after hard workouts",
        ],
        "warning_signs": [
            "⚠️ Resting HR suddenly elevated (+5+ BPM) - sign of fatigue/illness",
            "⚠️ Declining performance despite good effort - overtraining",
            "⚠️ HRV dropping - insufficient recovery",
            "⚠️ Persistent soreness - could indicate injury",
            "⚠️ Losing motivation - burnout or overtraining",
            "⚠️ Sleep quality poor - CNS fatigued",
            "⚠️ Prone to getting sick - immune system suppressed",
            "⚠️ Frequent aches or pains - injury developing",
        ],
        "progression_guidelines": [
            "Increase mileage no more than 10% per week",
            "Hard/easy principle: Follow hard workouts with easy runs",
            "One long run per week - increase by 5-10% every 2-3 weeks",
            "Vary workouts - alternating intensities prevents adaptation plateau",
            "Deload week every 3-4 weeks - reduce volume by 30-40%",
            "Strength training 2x per week - prevents injuries",
        ],
    }
