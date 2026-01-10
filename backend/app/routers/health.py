"""
Health Metrics Router
Endpoints for syncing and managing health/wellness data
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime, timedelta
from pydantic import BaseModel, Field

from .. import models, crud
from ..database import get_db
from ..services.garmin_health_service import garmin_health_service
from ..services.google_fit_service import google_fit_service
from ..services.apple_health_service import apple_health_service
from ..services.coach_service import get_coach_service
from ..dependencies.auth import get_current_user


router = APIRouter(prefix="/api/v1/health", tags=["health"])


# ========================================================================
# REQUEST/RESPONSE SCHEMAS
# ========================================================================

class ManualHealthMetricCreate(BaseModel):
    """Manual entry of health metrics."""
    date: date
    energy_level: Optional[int] = Field(None, ge=1, le=5, description="1=Very Low, 5=Excellent")
    soreness_level: Optional[int] = Field(None, ge=1, le=5, description="1=No Soreness, 5=Very Sore")
    mood: Optional[int] = Field(None, ge=1, le=5, description="1=Poor, 5=Excellent")
    motivation: Optional[int] = Field(None, ge=1, le=5, description="1=None, 5=Very High")
    sleep_duration_minutes: Optional[int] = Field(None, ge=0)
    resting_hr_bpm: Optional[int] = Field(None, ge=30, le=200)
    notes: Optional[str] = None


class HealthMetricResponse(BaseModel):
    """Health metric response."""
    id: int
    user_id: int
    date: date
    hrv_ms: Optional[float]
    resting_hr_bpm: Optional[int]
    sleep_duration_minutes: Optional[int]
    sleep_score: Optional[int]
    body_battery: Optional[int]
    readiness_score: Optional[int]
    stress_level: Optional[int]
    steps: Optional[int]
    energy_level: Optional[int]
    soreness_level: Optional[int]
    source: str
    data_quality: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class ReadinessResponse(BaseModel):
    """Readiness score and recommendation."""
    readiness_score: int
    confidence: str
    factors: List[dict]
    recommendation: str
    should_train_hard: Optional[bool]


class WorkoutRecommendationResponse(BaseModel):
    """Complete workout recommendation with health context."""
    readiness: ReadinessResponse
    ai_recommendation: str
    health_metrics: Optional[dict]


# ========================================================================
# HEALTH METRICS ENDPOINTS
# ========================================================================

@router.get("/today", response_model=Optional[HealthMetricResponse])
async def get_today_health(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get today's health metrics.
    
    Returns the most recent health metric for today across all sources.
    """
    health = db.query(models.HealthMetric).filter(
        models.HealthMetric.user_id == current_user.id,
        models.HealthMetric.date == date.today()
    ).first()
    
    return health


@router.get("/history", response_model=List[HealthMetricResponse])
async def get_health_history(
    days: int = 30,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get health metrics history.
    
    Args:
        days: Number of days to retrieve (default 30)
    """
    cutoff_date = date.today() - timedelta(days=days)
    
    metrics = db.query(models.HealthMetric).filter(
        models.HealthMetric.user_id == current_user.id,
        models.HealthMetric.date >= cutoff_date
    ).order_by(models.HealthMetric.date.desc()).all()
    
    return metrics


@router.post("/manual", response_model=HealthMetricResponse)
async def create_manual_health_metric(
    data: ManualHealthMetricCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Manually enter health metrics.
    
    Allows users to log how they feel, sleep, etc. when automatic sync is not available.
    """
    # Check if entry already exists for this date
    existing = db.query(models.HealthMetric).filter(
        models.HealthMetric.user_id == current_user.id,
        models.HealthMetric.date == data.date,
        models.HealthMetric.source == "manual"
    ).first()
    
    if existing:
        # Update existing
        for key, value in data.dict(exclude_unset=True).items():
            if key != "date":
                setattr(existing, key, value)
        db.commit()
        db.refresh(existing)
        return existing
    
    # Create new
    metric = models.HealthMetric(
        user_id=current_user.id,
        source="manual",
        data_quality="basic",
        **data.dict()
    )
    
    db.add(metric)
    db.commit()
    db.refresh(metric)
    
    return metric


@router.get("/readiness", response_model=ReadinessResponse)
async def get_readiness_score(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get today's readiness score.
    
    Calculates a 0-100 score based on HRV, sleep, stress, and other health metrics.
    """
    # Get today's health metrics
    health = db.query(models.HealthMetric).filter(
        models.HealthMetric.user_id == current_user.id,
        models.HealthMetric.date == date.today()
    ).first()
    
    # Calculate readiness
    coach_service = get_coach_service()
    readiness = coach_service.calculate_readiness_score(health, current_user)
    
    return readiness


@router.get("/recommendation", response_model=WorkoutRecommendationResponse)
async def get_workout_recommendation(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get AI-powered workout recommendation based on health state.
    
    Considers readiness score, recent training, goals, and health metrics.
    """
    coach_service = get_coach_service()
    recommendation = coach_service.generate_health_aware_recommendation(
        db, 
        current_user
    )
    
    return recommendation


# ========================================================================
# GARMIN SYNC
# ========================================================================

@router.post("/sync/garmin")
async def sync_garmin_health(
    days: int = 7,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Sync health metrics from Garmin Connect.
    
    Args:
        days: Number of days to sync (default 7)
    
    Requires Garmin to be connected via /garmin/connect endpoint.
    """
    if not current_user.garmin_token:
        raise HTTPException(400, "Garmin not connected. Connect via /garmin/connect first.")
    
    try:
        metrics = garmin_health_service.sync_health_metrics(db, current_user.id, days)
        
        return {
            "success": True,
            "synced_days": len(metrics),
            "latest_date": metrics[0].date.isoformat() if metrics else None,
            "message": f"Synced {len(metrics)} days of health metrics from Garmin"
        }
    except Exception as e:
        raise HTTPException(500, f"Error syncing Garmin health data: {str(e)}")


# ========================================================================
# GOOGLE FIT SYNC
# ========================================================================

@router.get("/connect/google-fit")
async def connect_google_fit(
    current_user: models.User = Depends(get_current_user)
):
    """
    Get Google Fit authorization URL.
    
    Returns URL for user to authorize access to Google Fit data.
    """
    import secrets
    state = secrets.token_urlsafe(32)
    
    auth_url = google_fit_service.get_authorization_url(state)
    
    return {
        "auth_url": auth_url,
        "state": state
    }


@router.post("/callback/google-fit")
async def google_fit_callback(
    code: str,
    state: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Handle Google Fit OAuth callback.
    
    Exchanges authorization code for access tokens and stores them.
    """
    try:
        # Exchange code for token
        token_data = google_fit_service.exchange_code_for_token(code)
        
        # Update user tokens
        current_user.google_fit_token = token_data["access_token"]
        current_user.google_fit_refresh_token = token_data["refresh_token"]
        current_user.google_fit_token_expires_at = datetime.utcnow() + timedelta(seconds=token_data["expires_in"])
        current_user.google_fit_connected_at = datetime.utcnow()
        
        db.commit()
        
        return {
            "success": True,
            "message": "Google Fit connected successfully"
        }
    except Exception as e:
        raise HTTPException(400, f"Error connecting Google Fit: {str(e)}")


@router.post("/sync/google-fit")
async def sync_google_fit_health(
    days: int = 7,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Sync health metrics from Google Fit.
    
    Args:
        days: Number of days to sync (default 7)
    """
    if not current_user.google_fit_token:
        raise HTTPException(400, "Google Fit not connected. Connect via /health/connect/google-fit first.")
    
    try:
        metrics = google_fit_service.sync_health_metrics(db, current_user.id, days)
        
        return {
            "success": True,
            "synced_days": len(metrics),
            "latest_date": metrics[0].date.isoformat() if metrics else None,
            "message": f"Synced {len(metrics)} days of health metrics from Google Fit"
        }
    except Exception as e:
        raise HTTPException(500, f"Error syncing Google Fit data: {str(e)}")


# ========================================================================
# APPLE HEALTH IMPORT
# ========================================================================

@router.post("/import/apple-health")
async def import_apple_health(
    file: UploadFile = File(...),
    max_days: int = 30,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Import health metrics from Apple Health export.xml file.
    
    Args:
        file: Apple Health export.xml file
        max_days: Maximum days to import (default 30)
    
    Users can export their data from iPhone Health app:
    1. Open Health app
    2. Tap profile icon
    3. Export All Health Data
    4. Extract zip and upload export.xml
    """
    if file.content_type not in ["text/xml", "application/xml"]:
        raise HTTPException(400, "File must be XML format (export.xml from Apple Health)")
    
    try:
        # Read file content
        xml_content = await file.read()
        xml_str = xml_content.decode("utf-8")
        
        # Import metrics
        metrics = apple_health_service.import_health_metrics(
            db,
            current_user.id,
            xml_str,
            max_days
        )
        
        return {
            "success": True,
            "imported_days": len(metrics),
            "message": f"Imported {len(metrics)} days from Apple Health"
        }
    except Exception as e:
        raise HTTPException(500, f"Error importing Apple Health data: {str(e)}")


# ========================================================================
# HEALTH INSIGHTS
# ========================================================================

@router.get("/insights/trends")
async def get_health_trends(
    days: int = 30,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get health trends and insights.
    
    Analyzes patterns in HRV, sleep, resting HR over time.
    """
    cutoff_date = date.today() - timedelta(days=days)
    
    metrics = db.query(models.HealthMetric).filter(
        models.HealthMetric.user_id == current_user.id,
        models.HealthMetric.date >= cutoff_date
    ).order_by(models.HealthMetric.date.asc()).all()
    
    if not metrics:
        return {
            "message": "No health data available for analysis",
            "trends": {}
        }
    
    # Calculate trends
    hrv_values = [m.hrv_ms for m in metrics if m.hrv_ms]
    rhr_values = [m.resting_hr_bpm for m in metrics if m.resting_hr_bpm]
    sleep_values = [m.sleep_duration_minutes / 60 for m in metrics if m.sleep_duration_minutes]
    
    trends = {}
    
    if hrv_values:
        trends["hrv"] = {
            "average": round(sum(hrv_values) / len(hrv_values), 1),
            "min": min(hrv_values),
            "max": max(hrv_values),
            "recent_average": round(sum(hrv_values[-7:]) / len(hrv_values[-7:]), 1) if len(hrv_values) >= 7 else None
        }
    
    if rhr_values:
        trends["resting_hr"] = {
            "average": round(sum(rhr_values) / len(rhr_values)),
            "min": min(rhr_values),
            "max": max(rhr_values),
            "recent_average": round(sum(rhr_values[-7:]) / len(rhr_values[-7:])) if len(rhr_values) >= 7 else None
        }
    
    if sleep_values:
        trends["sleep"] = {
            "average_hours": round(sum(sleep_values) / len(sleep_values), 1),
            "min_hours": round(min(sleep_values), 1),
            "max_hours": round(max(sleep_values), 1),
            "recent_average_hours": round(sum(sleep_values[-7:]) / len(sleep_values[-7:]), 1) if len(sleep_values) >= 7 else None
        }
    
    return {
        "period_days": days,
        "data_points": len(metrics),
        "trends": trends
    }
