"""
overtraining.py - Overtraining Detection Endpoints

Exposes the overtraining detection algorithms through REST API.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app import models
from app.services.overtraining_detector_service import overtraining_detector
from app.dependencies.auth import get_current_user


router = APIRouter(prefix="/api/v1/overtraining", tags=["overtraining"])


@router.get("/risk-assessment")
def get_overtraining_risk(
    days: int = Query(30, ge=7, le=90, description="Days to analyze (7-90)"),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive overtraining risk assessment.
    
    Analyzes multiple factors:
    - **Resting HR Trend**: Is HR elevated? (indicates fatigue)
    - **HRV Decline**: Is HRV dropping? (insufficient parasympathetic recovery)
    - **Recovery Patterns**: How well does HR recover? (autonomic function)
    - **Intensity Distribution**: Too many hard days? (polarized training)
    - **Readiness Score**: Consistently low? (accumulated fatigue)
    - **Sleep Quality**: Poor sleep? (overtraining marker)
    
    Returns risk score 0-100 and status: healthy/caution/warning/critical
    
    **Query Parameters:**
    - `days`: Analysis period (default: 30 days)
    
    **Response:**
    - `risk_score`: 0-100 (higher = more overtraining risk)
    - `status`: One of: healthy, caution, warning, critical
    - `factors`: Detailed breakdown of each contributing factor
    - `recommendations`: Actionable advice based on findings
    - `immediate_action_required`: Boolean flag for urgent situations
    
    **Example Response:**
    ```json
    {
      "risk_score": 62.5,
      "status": "warning",
      "risk_percentage": "62%",
      "factors": {
        "resting_heart_rate": {
          "baseline_bpm": 58.0,
          "recent_bpm": 64.2,
          "increase_percentage": 10.7,
          "risk_factor": 50
        },
        "heart_rate_variability": {
          "baseline_ms": 42.5,
          "recent_ms": 28.3,
          "decline_percentage": 33.4,
          "risk_factor": 75
        },
        "intensity_distribution": {
          "high_intensity_percentage": 28.5,
          "max_consecutive_intense_days": 4,
          "risk_factor": 60
        }
      },
      "recommendations": [
        "⚠️ WARNING: Reduce training volume by 40-50% and add extra recovery days",
        "🚨 Elevated resting HR detected - reduce training intensity for 3-5 days",
        "🚨 HRV significantly declined - prioritize sleep and recovery days"
      ],
      "immediate_action_required": true,
      "suggested_action": "Take a complete rest day or easy recovery run"
    }
    ```
    
    **Interpretation Guide:**
    - **Healthy (0-30%)**: Normal training load, continue as planned
    - **Caution (30-60%)**: Monitor trends, reduce intensity slightly
    - **Warning (60-80%)**: Significant fatigue, reduce training volume 40-50%
    - **Critical (80-100%)**: Overtraining likely, take 3-7 days rest
    
    **Requires authentication**
    """
    try:
        result = overtraining_detector.detect_overtraining_risk(
            user_id=current_user.id,
            db=db,
            analysis_days=days
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing overtraining risk: {str(e)}"
        )


@router.get("/recovery-status")
def get_recovery_status(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get quick recovery status summary.
    
    Simplified version of risk assessment for quick checks.
    
    Returns:
    - Current fatigue level (1-10)
    - Can train hard today? (yes/maybe/no)
    - Days until full recovery (estimate)
    
    **Requires authentication**
    """
    try:
        full_assessment = overtraining_detector.detect_overtraining_risk(
            user_id=current_user.id,
            db=db,
            analysis_days=14  # Shorter window for daily checks
        )
        
        risk_score = full_assessment["risk_score"]
        
        # Map risk score to fatigue level (1-10)
        fatigue_level = int((risk_score / 100) * 10)
        fatigue_level = max(1, min(10, fatigue_level))  # Clamp 1-10
        
        # Can train hard?
        if risk_score < 40:
            can_train_hard = "yes"
            recovery_estimate = 0
        elif risk_score < 60:
            can_train_hard = "maybe"
            recovery_estimate = 1
        elif risk_score < 80:
            can_train_hard = "no"
            recovery_estimate = 3
        else:
            can_train_hard = "no"
            recovery_estimate = 7
        
        return {
            "fatigue_level": fatigue_level,  # 1-10
            "can_train_hard": can_train_hard,  # yes/maybe/no
            "estimated_recovery_days": recovery_estimate,
            "detailed_assessment": {
                "risk_score": full_assessment["risk_score"],
                "status": full_assessment["status"],
                "recommendation": full_assessment["recommendations"][0] if full_assessment["recommendations"] else "No recommendation"
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting recovery status: {str(e)}"
        )


@router.get("/daily-alert")
def get_daily_alert(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get daily overtraining alert (if any).
    
    Returns alert only if overtraining risk is elevated (warning or critical).
    Useful for push notifications or dashboard alerts.
    
    Returns:
    - `should_alert`: Boolean - whether to show alert
    - `alert_type`: "warning" or "critical"
    - `message`: Human-readable alert message
    
    **Requires authentication**
    """
    try:
        assessment = overtraining_detector.detect_overtraining_risk(
            user_id=current_user.id,
            db=db,
            analysis_days=14
        )
        
        status_val = assessment["status"]
        
        # Only alert on warning or critical
        if status_val not in ["warning", "critical"]:
            return {
                "should_alert": False,
                "alert_type": None,
                "message": None
            }
        
        return {
            "should_alert": True,
            "alert_type": "critical" if status_val == "critical" else "warning",
            "message": assessment["recommended_action"],
            "risk_score": assessment["risk_score"],
            "main_concern": assessment["factors"]["resting_heart_rate"].get("interpretation", "")
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting daily alert: {str(e)}"
        )
