"""
hrv.py - Heart Rate Variability Analysis Endpoints

Advanced HRV analytics endpoints for detailed fatigue assessment.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app import models
from app.services.hrv_analysis_service import hrv_analysis_service
from app.dependencies.auth import get_current_user


router = APIRouter(prefix="/api/v1/hrv", tags=["hrv-analysis"])


@router.get("/analysis")
def analyze_hrv(
    days: int = Query(30, ge=7, le=90, description="Analysis period in days"),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive Heart Rate Variability (HRV) analysis.
    
    HRV measures variation between heartbeats (in milliseconds).
    Higher HRV = better parasympathetic recovery and autonomic balance.
    
    **Analysis Components:**
    
    1. **Current Status**
       - Recent HRV vs baseline
       - Recovery status (excellent/good/adequate/compromised/critical)
       - Fatigue score (0-100)
    
    2. **Statistics**
       - Min, max, mean HRV values
       - Standard deviation
       - Coefficient of variation (CV)
    
    3. **Trend Analysis**
       - Direction: up (improving), down (declining), stable
       - Strength: weak, moderate, strong
       - Interpretation of trends
    
    4. **Fatigue Indicators**
       - Fatigue score breakdown
       - HRV decline percentage
       - Recovery quality assessment
       - Sympathetic dominance indicator
    
    5. **Workout Correlation**
       - How workouts affect HRV
       - Recovery patterns after exercise
       - Intensity vs recovery relationship
    
    6. **Prediction**
       - 7-day HRV forecast
       - Trend projection
       - Fatigue trajectory
    
    **Query Parameters:**
    - `days`: Analysis period (default: 30, range: 7-90)
    
    **Response Example:**
    ```json
    {
      "status": "analyzed",
      "current_status": {
        "recent_hrv_ms": 35.2,
        "baseline_hrv_ms": 42.5,
        "vs_baseline_percentage": 82.8,
        "recovery_status": "good",
        "fatigue_score": 35
      },
      "trend_analysis": {
        "direction": "up",
        "strength": "moderate",
        "interpretation": "HRV improving - positive recovery trend"
      },
      "fatig ue_indicators": {
        "fatigue_score_0_100": 35,
        "hrv_decline_percent": 17.2,
        "recovery_quality": "Good - Balanced autonomic function",
        "sympathetic_dominance": "No"
      },
      "prediction": {
        "trend_direction": "improving",
        "prediction_next_7_days_ms": [36.5, 37.2, 38.1, 38.9, 39.5, 40.1, 40.6]
      },
      "recommendations": [
        "✅ HRV good - normal parasympathetic function",
        "📈 Improving HRV trend - recovery phase working well"
      ]
    }
    ```
    
    **Interpretation Guide:**
    
    | Status | Fatigue | Action |
    |--------|---------|--------|
    | Excellent (>95% baseline) | 0-20 | Full training capacity |
    | Good (85-95%) | 20-40 | Normal training |
    | Adequate (70-85%) | 40-60 | Moderate intensity only |
    | Compromised (50-70%) | 60-80 | Recovery day recommended |
    | Critical (<50%) | 80-100 | Rest or active recovery |
    
    **Key Metrics:**
    - **HRV**: Time between heartbeats (milliseconds)
    - **CV (Coefficient of Variation)**: Normalized HRV measure
    - **Recovery Quality**: Parasympathetic tone assessment
    
    **Requires authentication**
    """
    try:
        result = hrv_analysis_service.analyze_hrv_trends(
            user_id=current_user.id,
            db=db,
            analysis_days=days
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing HRV: {str(e)}"
        )


@router.get("/status")
def get_hrv_status(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get quick HRV status summary (simplified).
    
    Returns:
    - Current HRV vs baseline
    - Recovery status (one word)
    - Trend (up/down/stable)
    - Actionable status
    
    **Response:**
    ```json
    {
      "recovery_status": "good",
      "vs_baseline_percent": 87.5,
      "trend": "up",
      "action": "Ready for normal training",
      "fatigue_level": 1-10
    }
    ```
    
    **Requires authentication**
    """
    try:
        full_analysis = hrv_analysis_service.analyze_hrv_trends(
            user_id=current_user.id,
            db=db,
            analysis_days=14
        )
        
        if full_analysis.get("status") != "analyzed":
            raise ValueError("Insufficient HRV data available")
        
        recovery_status = full_analysis["current_status"]["recovery_status"]
        vs_baseline = full_analysis["current_status"]["vs_baseline_percentage"]
        trend = full_analysis["trend_analysis"]["direction"]
        fatigue_score = full_analysis["current_status"]["fatigue_score"]
        
        # Map fatigue score to 1-10 scale
        fatigue_level = max(1, min(10, int((fatigue_score / 100) * 10)))
        
        # Action recommendations
        actions = {
            "excellent": "✅ Ready for hard training",
            "good": "✅ Ready for normal training",
            "adequate": "⚠️ Moderate intensity only",
            "compromised": "⚠️ Recovery day recommended",
            "critical": "🛑 Rest or very light activity"
        }
        
        return {
            "recovery_status": recovery_status,
            "vs_baseline_percent": vs_baseline,
            "trend": trend,
            "fatigue_level": fatigue_level,  # 1-10
            "action": actions.get(recovery_status, "Consult full analysis"),
            "full_analysis_recommended": fatigue_level >= 7
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting HRV status: {str(e)}"
        )


@router.get("/workout-correlation")
def get_hrv_workout_correlation(
    days: int = Query(30, ge=7, le=90),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyze how workouts affect your HRV and recovery.
    
    Shows:
    - Average HRV drop on workout days
    - Recovery time (HRV bounce-back)
    - Workout intensity vs HRV impact
    - Optimal recovery windows
    
    **Requires authentication**
    """
    try:
        analysis = hrv_analysis_service.analyze_hrv_trends(
            user_id=current_user.id,
            db=db,
            analysis_days=days
        )
        
        if analysis.get("status") != "analyzed":
            raise ValueError("Insufficient data")
        
        correlation = analysis.get("workout_correlation", {})
        
        if correlation.get("status") == "no_workouts":
            return {
                "message": "No workouts found in this period",
                "recommendation": "Complete some workouts first to see HRV-workout correlation"
            }
        
        return correlation
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing workout correlation: {str(e)}"
        )


@router.get("/prediction")
def get_hrv_prediction(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get 7-day HRV and fatigue prediction.
    
    Uses linear regression on last 14 days to forecast recovery trajectory.
    
    Returns:
    - Predicted HRV values for next 7 days
    - Trend direction (improving/stable/declining)
    - When fatigue will resolve (estimate)
    
    **Requires authentication**
    """
    try:
        analysis = hrv_analysis_service.analyze_hrv_trends(
            user_id=current_user.id,
            db=db,
            analysis_days=14
        )
        
        if analysis.get("status") != "analyzed":
            raise ValueError("Insufficient data for prediction")
        
        prediction = analysis.get("prediction", {})
        
        return {
            **prediction,
            "analysis_based_on_days": 14
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating HRV prediction: {str(e)}"
        )
