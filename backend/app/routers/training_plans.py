"""
Training Plans Router

Endpoints for AI-generated personalized training plans.
Supports multi-week plan generation, adaptation, and tracking.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field

from app.database import get_db
from app.models import User
from app.security import verify_token
from app.core.config import settings
from app.services.training_plan_service import get_training_plan_service
import json

router = APIRouter(prefix="/api/v1/training-plans", tags=["training-plans"])
security_scheme = HTTPBearer()

# Lazy loading wrapper
_training_plan_service = None

def _get_training_plan_service():
    global _training_plan_service
    if _training_plan_service is None:
        _training_plan_service = get_training_plan_service()
    return _training_plan_service


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

class GeneratePlanRequest(BaseModel):
    """Request schema for generating a new training plan."""
    
    goal_type: str = Field(
        ...,
        description="Type of goal: 5k, 10k, half_marathon, marathon, fitness, base_building"
    )
    goal_date: datetime = Field(
        ...,
        description="Target date for the goal (ISO format)"
    )
    current_weekly_km: float = Field(
        ...,
        ge=0,
        le=200,
        description="Current weekly volume in kilometers"
    )
    weeks: int = Field(
        default=12,
        ge=4,
        le=24,
        description="Number of weeks for the plan (4-24)"
    )
    notes: Optional[str] = Field(
        None,
        max_length=500,
        description="Additional context (injuries, preferences, etc.)"
    )


class AdaptPlanRequest(BaseModel):
    """Request schema for adapting an existing plan."""
    
    plan_id: str = Field(
        ...,
        description="ID of the plan to adapt"
    )
    feedback: Optional[str] = Field(
        None,
        max_length=500,
        description="Feedback about plan execution (fatigue, injuries, etc.)"
    )


class PlanResponse(BaseModel):
    """Response schema for training plans."""
    
    success: bool
    message: str
    plan: dict
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Training plan generated successfully",
                "plan": {
                    "plan_id": "plan_123abc",
                    "plan_name": "Preparación Media Maratón",
                    "goal_type": "half_marathon",
                    "goal_date": "2026-04-15",
                    "total_weeks": 12,
                    "weeks": []
                }
            }
        }


class PlanSummary(BaseModel):
    """Summary of a training plan."""
    
    plan_id: str
    plan_name: str
    goal_type: str
    goal_date: datetime
    total_weeks: int
    current_week: int
    created_at: datetime
    status: str  # active, completed, paused


# ==================== Endpoints ====================

@router.post("/generate", response_model=PlanResponse, status_code=status.HTTP_201_CREATED)
def generate_training_plan(
    request: GeneratePlanRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate a personalized AI training plan.
    
    Creates a multi-week training plan based on:
    - User's current fitness level and volume
    - Goal type and target date
    - Training history and preferences
    - Any injuries or limitations
    
    The plan includes:
    - Weekly structure with varied workouts
    - Target distances and paces
    - Heart rate zones
    - Progression strategy
    - Nutrition and recovery tips
    
    **Requires authentication**
    """
    try:
        # Validate goal date is in the future
        if request.goal_date <= datetime.now():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Goal date must be in the future"
            )
        
        # Validate weeks fit within goal date
        weeks_until_goal = (request.goal_date - datetime.now()).days / 7
        if request.weeks > weeks_until_goal:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot create {request.weeks}-week plan for goal {int(weeks_until_goal)} weeks away"
            )
        
        # Generate plan
        goal = {
            "type": request.goal_type,
            "date": request.goal_date.isoformat(),  # Convert to ISO string for JSON serialization
            "current_weekly_km": request.current_weekly_km,
            "notes": request.notes
        }
        
        plan = _get_training_plan_service().generate_plan(
            db=db,
            user=current_user,
            goal=goal,
            weeks=request.weeks
        )
        
        # Store plan in user preferences
        if not current_user.preferences:
            current_user.preferences = {}
        
        if "training_plans" not in current_user.preferences:
            current_user.preferences["training_plans"] = []
        
        # Add metadata - ensure all datetime objects are ISO strings
        plan["status"] = "active"
        plan["current_week"] = 1
        
        current_user.preferences["training_plans"].append(plan)
        db.commit()
        
        return PlanResponse(
            success=True,
            message=f"Training plan '{plan['plan_name']}' generated successfully",
            plan=plan
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate training plan: {str(e)}"
        )


@router.get("/", response_model=List[PlanSummary])
def list_training_plans(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all training plans for the current user.
    
    Returns summaries of all plans (active, completed, paused).
    
    **Requires authentication**
    """
    if not current_user.preferences or "training_plans" not in current_user.preferences:
        return []
    
    plans = current_user.preferences["training_plans"]
    
    summaries = []
    for plan in plans:
        summaries.append(PlanSummary(
            plan_id=plan["plan_id"],
            plan_name=plan["plan_name"],
            goal_type=plan["goal_type"],
            goal_date=datetime.fromisoformat(plan["goal_date"]) if isinstance(plan["goal_date"], str) else plan["goal_date"],
            total_weeks=plan["total_weeks"],
            current_week=plan.get("current_week", 1),
            created_at=datetime.fromisoformat(plan["created_at"]) if isinstance(plan["created_at"], str) else plan["created_at"],
            status=plan.get("status", "active")
        ))
    
    return summaries


@router.get("/{plan_id}", response_model=PlanResponse)
def get_training_plan(
    plan_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific training plan by ID.
    
    Returns the full plan with all weeks and workouts.
    
    **Requires authentication**
    """
    if not current_user.preferences or "training_plans" not in current_user.preferences:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No training plans found"
        )
    
    plans = current_user.preferences["training_plans"]
    plan = next((p for p in plans if p["plan_id"] == plan_id), None)
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Training plan '{plan_id}' not found"
        )
    
    return PlanResponse(
        success=True,
        message="Training plan retrieved successfully",
        plan=plan
    )


@router.post("/{plan_id}/adapt", response_model=PlanResponse)
def adapt_training_plan(
    plan_id: str,
    request: AdaptPlanRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Adapt a training plan based on actual performance and feedback.
    
    Analyzes:
    - Adherence to planned workouts
    - Performance vs targets
    - Fatigue indicators
    - User feedback
    
    Adjusts upcoming weeks accordingly:
    - Volume (increase/decrease/maintain)
    - Intensity distribution
    - Recovery time
    
    **Requires authentication**
    """
    try:
        # Find the plan
        if not current_user.preferences or "training_plans" not in current_user.preferences:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No training plans found"
            )
        
        plans = current_user.preferences["training_plans"]
        plan_index = next((i for i, p in enumerate(plans) if p["plan_id"] == plan_id), None)
        
        if plan_index is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Training plan '{plan_id}' not found"
            )
        
        original_plan = plans[plan_index]
        
        # Get actual workouts since plan start
        from sqlalchemy import select
        from app.models import Workout
        
        plan_start = datetime.fromisoformat(original_plan["created_at"]) if isinstance(original_plan["created_at"], str) else original_plan["created_at"]
        
        from app.models import Workout
        actual_workouts = db.query(Workout).filter(
            Workout.user_id == current_user.id,
            Workout.start_time >= plan_start
        ).order_by(Workout.start_time.desc()).all()
        
        # Adapt the plan
        adapted_plan = _get_training_plan_service().adapt_plan(
            user=current_user,
            plan_id=plan_id,
            actual_workouts=actual_workouts,
            feedback=request.feedback,
            db=db
        )
        
        # Update metadata
        adapted_plan["adapted_at"] = datetime.now().isoformat()
        adapted_plan["adaptation_count"] = original_plan.get("adaptation_count", 0) + 1
        
        # Replace in user preferences
        plans[plan_index] = adapted_plan
        current_user.preferences["training_plans"] = plans
        db.commit()
        
        return PlanResponse(
            success=True,
            message=f"Training plan adapted successfully (adaptation #{adapted_plan['adaptation_count']})",
            plan=adapted_plan
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to adapt training plan: {str(e)}"
        )


@router.put("/{plan_id}/status")
def update_plan_status(
    plan_id: str,
    status: str,  # active, completed, paused
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update the status of a training plan.
    
    Allowed statuses:
    - **active**: Currently following the plan
    - **paused**: Temporarily stopped (injury, vacation, etc.)
    - **completed**: Successfully finished the plan
    
    **Requires authentication**
    """
    if status not in ["active", "completed", "paused"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status must be one of: active, completed, paused"
        )
    
    if not current_user.preferences or "training_plans" not in current_user.preferences:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No training plans found"
        )
    
    plans = current_user.preferences["training_plans"]
    plan = next((p for p in plans if p["plan_id"] == plan_id), None)
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Training plan '{plan_id}' not found"
        )
    
    plan["status"] = status
    plan["status_updated_at"] = datetime.now().isoformat()
    
    db.commit()
    
    return {
        "success": True,
        "message": f"Plan status updated to '{status}'",
        "plan_id": plan_id,
        "status": status
    }


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_training_plan(
    plan_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a training plan.
    
    Permanently removes the plan from user's profile.
    This action cannot be undone.
    
    **Requires authentication**
    """
    if not current_user.preferences or "training_plans" not in current_user.preferences:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No training plans found"
        )
    
    plans = current_user.preferences["training_plans"]
    plan_index = next((i for i, p in enumerate(plans) if p["plan_id"] == plan_id), None)
    
    if plan_index is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Training plan '{plan_id}' not found"
        )
    
    # Remove plan
    del plans[plan_index]
    current_user.preferences["training_plans"] = plans
    db.commit()
    
    return None  # 204 No Content


@router.post("/duration/with-target-race", response_model=dict, status_code=status.HTTP_200_OK)
def calculate_plan_duration_with_target_race(
    target_race_date: datetime = None,
    goal_type: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Calculate optimal plan duration based on target race date.
    
    Uses sports science periodization principles to determine:
    - How many weeks from now until optimal race preparation
    - How many weeks for training vs taper
    - Realistic race date given current time
    
    **Requires authentication**
    """
    if not target_race_date or not goal_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="target_race_date and goal_type are required"
        )
    
    try:
        result = _get_training_plan_service().calculate_plan_duration_with_target_race(
            target_race_date=target_race_date,
            goal_type=goal_type,
            start_date=datetime.utcnow()
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
            detail=f"Error calculating duration: {str(e)}"
        )


@router.get("/duration-options/{goal_type}", response_model=dict, status_code=status.HTTP_200_OK)
def get_plan_duration_options(
    goal_type: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get recommended plan duration options for a given goal.
    
    Returns multiple duration options with:
    - Number of weeks
    - Difficulty/intensity
    - Recommended option marked
    - Description of each option
    
    Used when user doesn't have a specific target race date.
    
    **Requires authentication**
    """
    try:
        result = _get_training_plan_service().get_plan_duration_options(goal_type)
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting duration options: {str(e)}"
        )
