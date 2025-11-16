"""
Onboarding Router
Endpoints for initial setup and personalization
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime

from .. import models, schemas, crud
from ..database import get_db
from ..security import verify_token
from ..core.config import settings

router = APIRouter(prefix="/api/v1/onboarding", tags=["onboarding"])
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


@router.get("/status", response_model=schemas.UserProfileOut)
async def get_onboarding_status(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current onboarding status.
    
    Returns user profile with onboarding completion state.
    """
    return current_user


@router.post("/complete", response_model=schemas.OnboardingCompleteResponse)
async def complete_onboarding(
    data: schemas.OnboardingCompleteRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Complete onboarding flow.
    
    Persists user's device preferences, use case, and personalization choices.
    """
    # Validate primary device
    valid_devices = ["garmin", "xiaomi", "strava", "manual", "apple"]
    if data.primary_device not in valid_devices:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid primary_device. Must be one of: {', '.join(valid_devices)}"
        )
    
    # Validate use case
    valid_use_cases = ["fitness_tracker", "training_coach", "race_prep", "general_health"]
    if data.use_case not in valid_use_cases:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid use_case. Must be one of: {', '.join(valid_use_cases)}"
        )
    
    # Validate coach style
    valid_styles = ["motivator", "technical", "balanced", "custom"]
    if data.coach_style_preference not in valid_styles:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid coach_style_preference. Must be one of: {', '.join(valid_styles)}"
        )
    
    # Validate language
    valid_languages = ["es", "en", "fr", "de", "it", "pt"]
    if data.language not in valid_languages:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid language. Must be one of: {', '.join(valid_languages)}"
        )
    
    # Validate integration sources
    valid_sources = ["garmin", "strava", "google_fit", "apple_health"]
    for source in data.integration_sources:
        if source not in valid_sources:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid integration source: {source}"
            )
    
    # Update user
    current_user.onboarding_completed = True
    current_user.primary_device = data.primary_device
    current_user.use_case = data.use_case
    current_user.coach_style_preference = data.coach_style_preference
    current_user.language = data.language
    current_user.enable_notifications = data.enable_notifications
    current_user.integration_sources = data.integration_sources
    current_user.onboarding_completed_at = datetime.utcnow()
    
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    
    return schemas.OnboardingCompleteResponse(
        success=True,
        user_id=current_user.id,
        message="Onboarding completed successfully!",
        onboarding_completed=True,
        redirectUrl="/dashboard"
    )
