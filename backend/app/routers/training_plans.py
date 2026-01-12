"""
Training Plans Router

Endpoints for AI-generated personalized training plans.
Supports multi-week plan generation, adaptation, and tracking.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel, Field

from app.database import get_db
from app.models import User, TrainingPlan
from app.services.training_plan_service import get_training_plan_service
from app.services.training_plan_tracking_service import get_tracking_service
from app.services.training_plan_matching_service import get_matching_service
from app.services.training_plan_export_service import get_export_service
from app import crud
from app.utils.rate_limiter import limiter
from app.dependencies.auth import get_current_user
from app import schemas
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/training-plans", tags=["training-plans"])

# Lazy loading wrapper
_training_plan_service = None

def _get_training_plan_service():
    global _training_plan_service
    if _training_plan_service is None:
        _training_plan_service = get_training_plan_service()
    return _training_plan_service


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
@limiter.limit("10/hour")
def generate_training_plan(
    request: Request,
    plan_request: GeneratePlanRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate a personalized AI training plan.
    """
    try:
        # Log validated request
        logger.debug(
            "Training plan generation request validated",
            extra={
                "user_id": current_user.id,
                "user_email": current_user.email,
                "goal_type": plan_request.goal_type,
                "goal_date": plan_request.goal_date.isoformat() if plan_request.goal_date else None,
                "current_weekly_km": plan_request.current_weekly_km,
                "weeks": plan_request.weeks,
            }
        )
        
        # Validate goal date is in the future
        # Handle both naive and aware datetime objects
        from datetime import timezone
        now = datetime.now(timezone.utc)
        goal_date = plan_request.goal_date
        
        # Convert naive datetime to aware if needed
        if goal_date.tzinfo is None:
            goal_date = goal_date.replace(tzinfo=timezone.utc)
        
        if goal_date <= now:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Goal date must be in the future"
            )
        
        # Validate weeks fit within goal date
        weeks_until_goal = (goal_date - now).days / 7
        weeks_until_goal_floor = int(weeks_until_goal)  # Use floor for validation (same as frontend)
        if plan_request.weeks > weeks_until_goal_floor:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot create {plan_request.weeks}-week plan for goal {weeks_until_goal_floor} weeks away (days_left: {(goal_date - now).days})"
            )
        
        # Generate plan
        goal = {
            "type": plan_request.goal_type,
            "date": plan_request.goal_date.isoformat(),  # Convert to ISO string for JSON serialization
            "current_weekly_km": plan_request.current_weekly_km,
            "notes": plan_request.notes
        }
        
        plan = _get_training_plan_service().generate_plan(
            db=db,
            user=current_user,
            goal=goal,
            weeks=plan_request.weeks
        )
        
        # Store plan in user preferences
        if not current_user.preferences:
            current_user.preferences = {}
        
        if "training_plans" not in current_user.preferences:
            current_user.preferences["training_plans"] = []
        
        # Add metadata - ensure all datetime objects are ISO strings
        plan["status"] = "active"
        plan["current_week"] = 1
        plan["start_date"] = datetime.now(timezone.utc).isoformat()  # Plan starts today
        
        logger.debug(
            "Storing training plan in database",
            extra={
                "user_id": current_user.id,
                "plan_id": plan.get("plan_id"),
                "plan_name": plan.get("plan_name"),
            }
        )
        
        current_user.preferences["training_plans"].append(plan)
        
        # CRITICAL: Tell SQLAlchemy that the JSON column has changed
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(current_user, "preferences")
        
        db.commit()
        
        # CRITICAL: Refresh the user object from database to see what was actually persisted
        db.refresh(current_user)
        
        logger.info(
            "Training plan stored successfully",
            extra={
                "user_id": current_user.id,
                "plan_id": plan.get("plan_id"),
                "total_plans": len(current_user.preferences.get("training_plans", [])),
            }
        )
        
        return PlanResponse(
            success=True,
            message=f"Training plan '{plan.get('plan_name', 'Training Plan')}' generated successfully",
            plan=plan
        )
        
    except HTTPException:
        # Re-raise HTTPExceptions as-is (they already have the correct status code)
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        error_msg = f"Failed to generate training plan: {str(e)}"
        logger.error(
            "Failed to generate training plan",
            extra={"user_id": current_user.id, "error": str(e)},
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg
        )


@router.post("/duration/with-target-race", response_model=dict, status_code=status.HTTP_200_OK)
def calculate_plan_duration_with_target_race(
    request: schemas.DurationCalculationRequest,
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
    if not request.target_race_date or not request.goal_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="target_race_date and goal_type are required"
        )
    
    try:
        # Convert string date to datetime if needed
        from datetime import datetime as dt_class
        if isinstance(request.target_race_date, str):
            target_race_dt = dt_class.strptime(request.target_race_date, "%Y-%m-%d")
        else:
            target_race_dt = request.target_race_date
        
        result = _get_training_plan_service().calculate_plan_duration_with_target_race(
            target_race_date=target_race_dt,
            goal_type=request.goal_type,
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
    try:
        if not current_user.preferences or "training_plans" not in current_user.preferences:
            return []
        
        plans = current_user.preferences["training_plans"]
        if not isinstance(plans, list):
            return []
        
        summaries = []
        for plan in plans:
            # Validate required fields exist
            if not isinstance(plan, dict) or "plan_id" not in plan:
                continue  # Skip invalid plans
            
            try:
                # Safe parsing with defaults
                goal_date = plan.get("goal_date")
                if isinstance(goal_date, str):
                    goal_date = datetime.fromisoformat(goal_date)
                elif not isinstance(goal_date, datetime):
                    continue  # Skip if invalid date
                
                created_at = plan.get("created_at")
                if isinstance(created_at, str):
                    created_at = datetime.fromisoformat(created_at)
                elif not isinstance(created_at, datetime):
                    created_at = datetime.now()  # Default to now if invalid
                
                summaries.append(PlanSummary(
                    plan_id=plan["plan_id"],
                    plan_name=plan.get("plan_name", "Unnamed Plan"),
                    goal_type=plan.get("goal_type", "fitness"),
                    goal_date=goal_date,
                    total_weeks=plan.get("total_weeks", 12),
                    current_week=plan.get("current_week", 1),
                    created_at=created_at,
                    status=plan.get("status", "active")
                ))
            except (ValueError, KeyError, TypeError) as e:
                # Log and skip malformed plan
                logger.warning(
                    "Skipping malformed training plan",
                    extra={"user_id": current_user.id, "error": str(e)},
                    exc_info=True
                )
                continue
        
        return summaries
    except Exception as e:
        logger.error(
            "Error listing training plans",
            extra={"user_id": current_user.id, "error": str(e)},
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail=f"Error listing training plans: {str(e)}"
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
        plan_index = next((i for i, p in enumerate(plans) if isinstance(p, dict) and p.get("plan_id") == plan_id), None)
        
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
        from sqlalchemy.orm import joinedload
        actual_workouts = db.query(Workout).filter(
            Workout.user_id == current_user.id,
            Workout.start_time >= plan_start
        ).options(joinedload(Workout.user)).order_by(Workout.start_time.desc()).all()
        
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
    plan = next((p for p in plans if isinstance(p, dict) and p.get("plan_id") == plan_id), None)
    
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


@router.get("/{plan_id}/progress", response_model=dict)
def get_plan_progress(
    plan_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive progress metrics for a training plan.
    
    Returns adherence, progress, deviations, and current week metrics.
    
    **Requires authentication**
    """
    # For now, get from user.preferences (legacy)
    # TODO: Migrate to TrainingPlan model
    if not current_user.preferences or "training_plans" not in current_user.preferences:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No training plans found"
        )
    
    plans = current_user.preferences["training_plans"]
    plan_dict = next((p for p in plans if isinstance(p, dict) and p.get("plan_id") == plan_id), None)
    
    if not plan_dict:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Training plan '{plan_id}' not found"
        )
    
    # Convert dict to TrainingPlan-like object for tracking service
    # This is a temporary solution until we migrate fully to TrainingPlan model
    class PlanWrapper:
        def __init__(self, data: dict, user_id: int):
            self.plan_data = data
            self.user_id = user_id
            self.current_week = data.get('current_week', 1)
            self.total_weeks = data.get('total_weeks', len(data.get('weeks', [])))
            start_date_str = data.get('start_date')
            if isinstance(start_date_str, str):
                self.start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
            else:
                self.start_date = start_date_str or datetime.utcnow()
    
    plan_wrapper = PlanWrapper(plan_dict, current_user.id)
    
    # Calculate metrics
    tracking_service = get_tracking_service()
    metrics = tracking_service.calculate_metrics(plan_wrapper, db)
    
    return metrics


@router.get("/{plan_id}/adherence", response_model=dict)
def get_plan_adherence(
    plan_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get adherence metrics for a training plan.
    
    Returns percentage of workouts completed and related metrics.
    
    **Requires authentication**
    """
    # Similar to get_plan_progress, get from user.preferences for now
    if not current_user.preferences or "training_plans" not in current_user.preferences:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No training plans found"
        )
    
    plans = current_user.preferences["training_plans"]
    plan_dict = next((p for p in plans if isinstance(p, dict) and p.get("plan_id") == plan_id), None)
    
    if not plan_dict:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Training plan '{plan_id}' not found"
        )
    
    class PlanWrapper:
        def __init__(self, data: dict, user_id: int):
            self.plan_data = data
            self.user_id = user_id
            self.current_week = data.get('current_week', 1)
            self.total_weeks = data.get('total_weeks', len(data.get('weeks', [])))
            start_date_str = data.get('start_date')
            if isinstance(start_date_str, str):
                self.start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
            else:
                self.start_date = start_date_str or datetime.utcnow()
    
    plan_wrapper = PlanWrapper(plan_dict, current_user.id)
    tracking_service = get_tracking_service()
    adherence = tracking_service.calculate_adherence(plan_wrapper, db)
    
    return adherence


@router.get("/{plan_id}/deviations", response_model=dict)
def get_plan_deviations(
    plan_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detected deviations from the training plan.
    
    Returns list of deviations with recommendations.
    
    **Requires authentication**
    """
    # Similar pattern to get_plan_progress
    if not current_user.preferences or "training_plans" not in current_user.preferences:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No training plans found"
        )
    
    plans = current_user.preferences["training_plans"]
    plan_dict = next((p for p in plans if isinstance(p, dict) and p.get("plan_id") == plan_id), None)
    
    if not plan_dict:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Training plan '{plan_id}' not found"
        )
    
    class PlanWrapper:
        def __init__(self, data: dict, user_id: int):
            self.plan_data = data
            self.user_id = user_id
            self.current_week = data.get('current_week', 1)
            self.total_weeks = data.get('total_weeks', len(data.get('weeks', [])))
            start_date_str = data.get('start_date')
            if isinstance(start_date_str, str):
                self.start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
            else:
                self.start_date = start_date_str or datetime.utcnow()
    
    plan_wrapper = PlanWrapper(plan_dict, current_user.id)
    tracking_service = get_tracking_service()
    deviations = tracking_service.detect_deviations(plan_wrapper, db)
    
    return {
        'deviations': deviations,
        'count': len(deviations),
        'has_deviations': len(deviations) > 0,
    }


@router.put("/{plan_id}/weeks/{week_num}/workouts/{workout_index}", response_model=dict)
def update_plan_workout(
    plan_id: str,
    week_num: int,
    workout_index: int,
    workout_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a specific workout in a training plan.
    
    **Requires authentication**
    """
    if not current_user.preferences or "training_plans" not in current_user.preferences:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No training plans found"
        )
    
    plans = current_user.preferences["training_plans"]
    plan_index = next((i for i, p in enumerate(plans) if isinstance(p, dict) and p.get("plan_id") == plan_id), None)
    
    if plan_index is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Training plan '{plan_id}' not found"
        )
    
    plan_dict = plans[plan_index]
    
    # Find the week
    week = next((w for w in plan_dict.get('weeks', []) if w.get('week') == week_num), None)
    if not week:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Week {week_num} not found in plan"
        )
    
    # Find the workout
    workouts = week.get('workouts', [])
    if workout_index < 0 or workout_index >= len(workouts):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workout at index {workout_index} not found"
        )
    
    # Update workout
    workouts[workout_index].update(workout_data)
    
    # Save changes
    plans[plan_index] = plan_dict
    current_user.preferences["training_plans"] = plans
    
    from sqlalchemy.orm.attributes import flag_modified
    flag_modified(current_user, "preferences")
    db.commit()
    
    return {
        'success': True,
        'message': 'Workout updated successfully',
        'workout': workouts[workout_index]
    }


@router.post("/{plan_id}/weeks/{week_num}/workouts", response_model=dict)
def add_plan_workout(
    plan_id: str,
    week_num: int,
    workout_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a new workout to a specific week in a training plan.
    
    **Requires authentication**
    """
    if not current_user.preferences or "training_plans" not in current_user.preferences:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No training plans found"
        )
    
    plans = current_user.preferences["training_plans"]
    plan_index = next((i for i, p in enumerate(plans) if isinstance(p, dict) and p.get("plan_id") == plan_id), None)
    
    if plan_index is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Training plan '{plan_id}' not found"
        )
    
    plan_dict = plans[plan_index]
    
    # Find the week
    week = next((w for w in plan_dict.get('weeks', []) if w.get('week') == week_num), None)
    if not week:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Week {week_num} not found in plan"
        )
    
    # Add workout
    if 'workouts' not in week:
        week['workouts'] = []
    
    week['workouts'].append(workout_data)
    
    # Update week total_km if distance_km is provided
    if workout_data.get('distance_km'):
        week['total_km'] = week.get('total_km', 0) + workout_data['distance_km']
    
    # Save changes
    plans[plan_index] = plan_dict
    current_user.preferences["training_plans"] = plans
    
    from sqlalchemy.orm.attributes import flag_modified
    flag_modified(current_user, "preferences")
    db.commit()
    
    return {
        'success': True,
        'message': 'Workout added successfully',
        'workout': workout_data
    }


@router.delete("/{plan_id}/weeks/{week_num}/workouts/{workout_index}", response_model=dict)
def delete_plan_workout(
    plan_id: str,
    week_num: int,
    workout_index: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a workout from a training plan.
    
    **Requires authentication**
    """
    if not current_user.preferences or "training_plans" not in current_user.preferences:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No training plans found"
        )
    
    plans = current_user.preferences["training_plans"]
    plan_index = next((i for i, p in enumerate(plans) if isinstance(p, dict) and p.get("plan_id") == plan_id), None)
    
    if plan_index is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Training plan '{plan_id}' not found"
        )
    
    plan_dict = plans[plan_index]
    
    # Find the week
    week = next((w for w in plan_dict.get('weeks', []) if w.get('week') == week_num), None)
    if not week:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Week {week_num} not found in plan"
        )
    
    # Find the workout
    workouts = week.get('workouts', [])
    if workout_index < 0 or workout_index >= len(workouts):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workout at index {workout_index} not found"
        )
    
    # Remove workout and update week total_km
    removed_workout = workouts.pop(workout_index)
    if removed_workout.get('distance_km'):
        week['total_km'] = max(0, week.get('total_km', 0) - removed_workout['distance_km'])
    
    # Save changes
    plans[plan_index] = plan_dict
    current_user.preferences["training_plans"] = plans
    
    from sqlalchemy.orm.attributes import flag_modified
    flag_modified(current_user, "preferences")
    db.commit()
    
    return {
        'success': True,
        'message': 'Workout deleted successfully'
    }


@router.post("/{plan_id}/sync-workouts", response_model=dict)
def sync_plan_workouts(
    plan_id: str,
    auto_complete: bool = True,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Synchronize plan workouts with actual completed workouts.
    
    Matches actual workouts with planned workouts and optionally marks them as completed.
    
    **Requires authentication**
    """
    if not current_user.preferences or "training_plans" not in current_user.preferences:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No training plans found"
        )
    
    plans = current_user.preferences["training_plans"]
    plan_index = next((i for i, p in enumerate(plans) if isinstance(p, dict) and p.get("plan_id") == plan_id), None)
    
    if plan_index is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Training plan '{plan_id}' not found"
        )
    
    plan_dict = plans[plan_index]
    
    # Get start date
    start_date_str = plan_dict.get('start_date')
    if isinstance(start_date_str, str):
        start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00')).date()
    else:
        start_date = start_date_str.date() if isinstance(start_date_str, datetime) else datetime.utcnow().date()
    
    # Sync workouts
    matching_service = get_matching_service()
    sync_result = matching_service.sync_workouts(
        plan_dict,
        current_user.id,
        db,
        start_date,
        auto_complete=auto_complete
    )
    
    # Update plan in preferences
    plans[plan_index] = plan_dict
    current_user.preferences["training_plans"] = plans
    
    from sqlalchemy.orm.attributes import flag_modified
    flag_modified(current_user, "preferences")
    db.commit()
    
    return {
        'success': True,
        'message': f"Sincronización completada: {sync_result['workouts_completed']} entrenamientos marcados como completados",
        **sync_result
    }


@router.get("/{plan_id}/export/{format}")
def export_training_plan(
    plan_id: str,
    format: str,  # json, csv, ical, pdf
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Export a training plan to various formats.
    
    Supported formats: json, csv, ical, pdf
    
    **Requires authentication**
    """
    if format not in ['json', 'csv', 'ical', 'pdf']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported format: {format}. Supported: json, csv, ical, pdf"
        )
    
    if not current_user.preferences or "training_plans" not in current_user.preferences:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No training plans found"
        )
    
    plans = current_user.preferences["training_plans"]
    plan_dict = next((p for p in plans if isinstance(p, dict) and p.get("plan_id") == plan_id), None)
    
    if not plan_dict:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Training plan '{plan_id}' not found"
        )
    
    export_service = get_export_service()
    
    # Get start date
    start_date_str = plan_dict.get('start_date')
    if isinstance(start_date_str, str):
        start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
    else:
        start_date = start_date_str if isinstance(start_date_str, datetime) else datetime.utcnow()
    
    # Export based on format
    if format == 'json':
        content = export_service.export_to_json(plan_dict)
        media_type = 'application/json'
        filename = f"{plan_id}.json"
    elif format == 'csv':
        content = export_service.export_to_csv(plan_dict)
        media_type = 'text/csv'
        filename = f"{plan_id}.csv"
    elif format == 'ical':
        content = export_service.export_to_ical(plan_dict, start_date)
        media_type = 'text/calendar'
        filename = f"{plan_id}.ics"
    elif format == 'pdf':
        content = export_service.export_to_pdf(plan_dict)
        media_type = 'application/pdf'
        filename = f"{plan_id}.pdf"
    
    return Response(
        content=content,
        media_type=media_type,
        headers={
            'Content-Disposition': f'attachment; filename="{filename}"'
        }
    )


@router.get("/{plan_id}/notifications", response_model=dict)
def get_plan_notifications(
    plan_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get notifications and reminders for a training plan.
    
    Returns upcoming workouts, reminders, and missed workouts.
    
    **Requires authentication**
    """
    if not current_user.preferences or "training_plans" not in current_user.preferences:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No training plans found"
        )
    
    plans = current_user.preferences["training_plans"]
    plan_dict = next((p for p in plans if isinstance(p, dict) and p.get("plan_id") == plan_id), None)
    
    if not plan_dict:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Training plan '{plan_id}' not found"
        )
    
    # Get start date and current week
    start_date_str = plan_dict.get('start_date')
    if isinstance(start_date_str, str):
        start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00')).date()
    else:
        start_date = start_date_str.date() if isinstance(start_date_str, datetime) else date.today()
    
    current_week = plan_dict.get('current_week', 1)
    
    # Generate notifications
    notification_service = get_notification_service()
    summary = notification_service.generate_notification_summary(
        plan_dict,
        start_date,
        current_week
    )
    
    return summary


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
    plan = next((p for p in plans if isinstance(p, dict) and p.get("plan_id") == plan_id), None)
    
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
    logger.info(
        f"DELETE training plan request: plan_id={plan_id}, user_id={current_user.id}",
        extra={
            "plan_id": plan_id,
            "user_id": current_user.id,
            "user_email": current_user.email,
        }
    )
    
    if not current_user.preferences or "training_plans" not in current_user.preferences:
        logger.warning(f"No training plans found for user {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No training plans found"
        )
    
    plans = current_user.preferences["training_plans"]
    logger.debug(f"Current plans count before delete: {len(plans)}")
    
    plan_index = next((i for i, p in enumerate(plans) if isinstance(p, dict) and p.get("plan_id") == plan_id), None)
    
    if plan_index is None:
        logger.warning(f"Plan {plan_id} not found in user {current_user.id}'s plans")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Training plan '{plan_id}' not found"
        )
    
    # Log the plan being deleted
    plan_to_delete = plans[plan_index]
    logger.info(
        f"Deleting plan: plan_id={plan_id}, plan_name={plan_to_delete.get('plan_name')}",
        extra={
            "plan_id": plan_id,
            "plan_name": plan_to_delete.get("plan_name"),
            "user_id": current_user.id,
        }
    )
    
    # Remove plan from list
    updated_plans = [p for i, p in enumerate(plans) if i != plan_index]
    
    # Use direct SQL UPDATE to ensure it works correctly with SQLite JSON
    # This is more reliable than relying on SQLAlchemy's JSON change detection
    from sqlalchemy import text
    from app.database import engine
    
    # Get current preferences as dict
    current_prefs = dict(current_user.preferences) if current_user.preferences else {}
    current_prefs["training_plans"] = updated_plans
    
    # Detect database type
    db_url = str(engine.url)
    is_postgres = 'postgresql' in db_url or 'postgres' in db_url
    
    try:
        # Update using raw SQL - this ensures the change is persisted correctly
        if is_postgres:
            # PostgreSQL: use JSONB cast
            db.execute(
                text("UPDATE users SET preferences = :prefs::jsonb WHERE id = :user_id"),
                {"prefs": json.dumps(current_prefs), "user_id": current_user.id}
            )
        else:
            # SQLite: JSON stored as text
            db.execute(
                text("UPDATE users SET preferences = :prefs WHERE id = :user_id"),
                {"prefs": json.dumps(current_prefs), "user_id": current_user.id}
            )
        
        db.commit()
        logger.info(f"Committed deletion of plan {plan_id} using direct SQL. Plans before: {len(plans)}, after: {len(updated_plans)}")
        
        # Also update the in-memory object for consistency
        current_user.preferences = current_prefs
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(current_user, "preferences")
        
    except Exception as e:
        logger.error(f"Failed to delete plan using direct SQL: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to persist deletion to database"
        )
    
    # Verify deletion by querying database directly
    result = db.execute(
        text("SELECT preferences FROM users WHERE id = :user_id"),
        {"user_id": current_user.id}
    )
    db_prefs = result.scalar_one()
    
    # Refresh the user object
    db.refresh(current_user)
    
    # Get plans after deletion from the database query result (not from session cache)
    if db_prefs and isinstance(db_prefs, dict) and "training_plans" in db_prefs:
        plans_after = db_prefs.get("training_plans", [])
    else:
        plans_after = []
    
    remaining_plan_ids = [p.get("plan_id") for p in plans_after if isinstance(p, dict) and p.get("plan_id")]
    
    logger.info(
        f"Plan deleted. Remaining plans count: {len(plans_after)}, remaining plan_ids: {remaining_plan_ids}",
        extra={
            "plan_id": plan_id,
            "user_id": current_user.id,
            "plans_before": len(plans),
            "plans_after": len(plans_after),
            "remaining_plan_ids": remaining_plan_ids,
        }
    )
    
    # Double-check the plan is gone
    if plan_id in remaining_plan_ids:
        logger.error(
            f"CRITICAL: Plan {plan_id} still exists after deletion!",
            extra={
                "plan_id": plan_id,
                "user_id": current_user.id,
                "remaining_plan_ids": remaining_plan_ids,
                "all_plans": plans_after,
            }
        )
        # Try one more time with direct database update using SQL
        from sqlalchemy import text
        from app.database import engine
        
        try:
            # Detect database type
            db_url = str(engine.url)
            is_postgres = 'postgresql' in db_url or 'postgres' in db_url
            
            # Get raw preferences JSON and update it
            result = db.execute(
                text("SELECT preferences FROM users WHERE id = :user_id"),
                {"user_id": current_user.id}
            )
            raw_prefs = result.scalar_one()
            
            if raw_prefs and isinstance(raw_prefs, dict) and "training_plans" in raw_prefs:
                # Filter out the deleted plan
                raw_prefs["training_plans"] = [
                    p for p in raw_prefs["training_plans"] 
                    if isinstance(p, dict) and p.get("plan_id") != plan_id
                ]
                
                # Update using raw SQL - handle both PostgreSQL (JSONB) and SQLite (JSON)
                if is_postgres:
                    # PostgreSQL: use JSONB cast
                    db.execute(
                        text("UPDATE users SET preferences = :prefs::jsonb WHERE id = :user_id"),
                        {"prefs": json.dumps(raw_prefs), "user_id": current_user.id}
                    )
                else:
                    # SQLite: just use JSON string
                    db.execute(
                        text("UPDATE users SET preferences = :prefs WHERE id = :user_id"),
                        {"prefs": json.dumps(raw_prefs), "user_id": current_user.id}
                    )
                
                db.commit()
                
                # Verify the update
                result_after = db.execute(
                    text("SELECT preferences FROM users WHERE id = :user_id"),
                    {"user_id": current_user.id}
                )
                prefs_after = result_after.scalar_one()
                plans_after_sql = prefs_after.get("training_plans", []) if prefs_after and isinstance(prefs_after, dict) else []
                remaining_ids = [p.get("plan_id") for p in plans_after_sql if isinstance(p, dict) and p.get("plan_id")]
                
                if plan_id not in remaining_ids:
                    logger.info(f"Successfully removed plan {plan_id} using direct SQL update. Remaining: {remaining_ids}")
                else:
                    logger.error(f"CRITICAL: Plan {plan_id} still exists after direct SQL update!")
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Failed to delete training plan even with direct SQL"
                    )
            else:
                logger.error(f"Invalid preferences format: {type(raw_prefs)}")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Direct SQL update also failed: {e}", exc_info=True)
            db.rollback()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete training plan"
        )
    
    return None  # 204 No Content


@router.get("/{plan_id}/workouts/{week_num}/{day_num}/export-tcx", status_code=status.HTTP_200_OK)
def export_workout_tcx(
    plan_id: str,
    week_num: int,
    day_num: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Export a specific workout as TCX file (Garmin format).
    
    Returns TCX file for import into Garmin devices/apps.
    
    **Requires authentication**
    """
    if not current_user.preferences or "training_plans" not in current_user.preferences:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No training plans found"
        )
    
    plans = current_user.preferences["training_plans"]
    plan = next((p for p in plans if isinstance(p, dict) and p.get("plan_id") == plan_id), None)
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Training plan '{plan_id}' not found"
        )
    
    weeks = plan.get("weeks", [])
    if week_num < 1 or week_num > len(weeks):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Week {week_num} not found in plan"
        )
    
    week = weeks[week_num - 1]
    workouts = week.get("workouts", [])
    
    # Find workout by day number
    workout = next((w for w in workouts if w.get("day") == day_num), None)
    if not workout:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Workout on day {day_num} not found in week {week_num}"
        )
    
    # Generate TCX
    tcx_content = _generate_tcx(plan, week_num, workout)
    
    return Response(
        content=tcx_content,
        media_type="application/xml",
        headers={
            "Content-Disposition": f"attachment; filename=workout_{plan_id}_w{week_num}_d{day_num}.tcx"
        }
    )


def _generate_tcx(plan: dict, week_num: int, workout: dict) -> str:
    """
    Generate TCX file content for a workout.
    
    TCX is Garmin's Training Center XML format.
    """
    distance_m = (workout.get("distance_km", 0) or 0) * 1000
    
    # Parse pace target (e.g., "5:30-6:00 min/km" -> average of 5:45 min/km)
    pace_str = workout.get("pace_target", "6:00")
    try:
        # Extract first pace value
        pace_parts = pace_str.split("-")[0].split(":")
        pace_min_per_km = int(pace_parts[0]) + int(pace_parts[1]) / 60
    except:
        pace_min_per_km = 6.0  # Default
    
    # Calculate total time (minutes -> seconds)
    total_time_seconds = int(distance_m / 1000 * pace_min_per_km * 60)
    
    # Start time (use plan's start_date if available, otherwise today)
    start_date_str = plan.get("start_date", datetime.now(timezone.utc).isoformat())
    start_date = datetime.fromisoformat(start_date_str.replace("Z", "+00:00"))
    
    # Adjust to actual workout date (week + day)
    # Assuming weeks start on Monday
    days_offset = (week_num - 1) * 7 + (workout.get("day", 1) - 1)
    workout_date = start_date + timedelta(days=days_offset)
    
    # Format as ISO 8601 for TCX
    date_iso = workout_date.isoformat().split("+")[0] + "Z"
    
    tcx = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<TrainingCenterDatabase xsi:schemaLocation="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2 http://apps.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd" xmlns:ns2="http://www.garmin.com/xmlschemas/ActivityExtension/v2" xmlns="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <Courses>
    <Course>
      <Name>{workout.get('name', 'Entrenamiento')}</Name>
      <Lap>
        <TotalTimeSeconds>{total_time_seconds}</TotalTimeSeconds>
        <DistanceMeters>{distance_m}</DistanceMeters>
        <BeginPosition>
          <LatitudeDegrees>40.4168</LatitudeDegrees>
          <LongitudeDegrees>-3.7038</LongitudeDegrees>
        </BeginPosition>
        <EndPosition>
          <LatitudeDegrees>40.4168</LatitudeDegrees>
          <LongitudeDegrees>-3.7038</LongitudeDegrees>
        </EndPosition>
        <AvgSpeed>{distance_m / total_time_seconds if total_time_seconds > 0 else 0}</AvgSpeed>
      </Lap>
    </Course>
  </Courses>
  <Workouts>
    <Workout Sport="Running">
      <Name>{workout.get('name', 'Entrenamiento')}</Name>
      <Description>{workout.get('notes', '')}</Description>
      <ScheduledOn>{date_iso}</ScheduledOn>
      <Workouts>
        <Workout Sport="Running">
          <ScheduledOn>{date_iso}</ScheduledOn>
          <Intensity>Active</Intensity>
          <CourseNameRef>{workout.get('name', 'Entrenamiento')}</CourseNameRef>
        </Workout>
      </Workouts>
    </Workout>
  </Workouts>
</TrainingCenterDatabase>"""
    
    return tcx


# ============================================================================
# ADAPTIVE COACHING - Dynamic Workout Adjustments
# ============================================================================

class HealthMetricsRequest(BaseModel):
    """Health metrics for adaptive coaching."""
    readiness_score: Optional[float] = 0.5  # 0-1
    sleep_hours: Optional[float] = 7
    fatigue_level: Optional[float] = 0  # 0-1
    heart_rate_variability: Optional[float] = None


@router.post("/{plan_id}/workouts/{week_num}/{day_num}/adapt", status_code=status.HTTP_200_OK)
def get_adapted_workout(
    plan_id: str,
    week_num: int,
    day_num: int,
    metrics: HealthMetricsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get an adapted version of a workout based on current health metrics.
    
    Uses adaptive coaching to adjust intensity/volume based on:
    - Readiness score (0-1: 0=not ready, 1=fully ready)
    - Sleep hours
    - Fatigue level (0-1)
    - Heart rate variability
    
    Returns adjusted workout or suggests rest day if needed.
    
    **Requires authentication**
    """
    if not current_user.preferences or "training_plans" not in current_user.preferences:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No training plans found"
        )
    
    plans = current_user.preferences["training_plans"]
    plan = next((p for p in plans if isinstance(p, dict) and p.get("plan_id") == plan_id), None)
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Training plan '{plan_id}' not found"
        )
    
    weeks = plan.get("weeks", [])
    if week_num < 1 or week_num > len(weeks):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Week {week_num} not found in plan"
        )
    
    week = weeks[week_num - 1]
    workouts = week.get("workouts", [])
    
    # Find original workout
    original_workout = next((w for w in workouts if w.get("day") == day_num), None)
    if not original_workout:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Workout on day {day_num} not found in week {week_num}"
        )
    
    # Get adaptive coaching service
    from app.services.adaptive_coaching_service import AdaptiveCoachingService
    coaching_service = AdaptiveCoachingService()
    
    # Check if should skip
    health_data = {
        "readiness_score": metrics.readiness_score,
        "sleep_hours": metrics.sleep_hours,
        "fatigue_level": metrics.fatigue_level,
        "heart_rate_variability": metrics.heart_rate_variability,
    }
    
    if coaching_service.should_skip_workout(health_data):
        return {
            "original_workout": original_workout,
            "adapted_workout": {
                "type": "rest_day",
                "name": "Día de descanso (Recomendado por salud)",
                "distance_km": 0,
                "pace_target": "N/A",
                "notes": "Necesitas descanso. Recuperarte hoy es entrenar mañana."
            },
            "should_rest": True,
            "recommendation": coaching_service.get_recovery_recommendation(health_data)
        }
    
    # Get adapted workout
    adapted_workout = coaching_service.get_adjusted_workout(
        original_workout.copy(),
        health_data
    )
    
    return {
        "original_workout": original_workout,
        "adapted_workout": adapted_workout,
        "should_rest": False,
        "recommendation": coaching_service.get_recovery_recommendation(health_data),
        "metrics_received": {
            "readiness_score": metrics.readiness_score,
            "sleep_hours": metrics.sleep_hours,
            "fatigue_level": metrics.fatigue_level,
        }
    }


@router.post("/{plan_id}/health-check", status_code=status.HTTP_200_OK)
def check_training_readiness(
    plan_id: str,
    metrics: HealthMetricsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check if user is ready for training and get recovery recommendations.
    
    Returns detailed analysis of current state and suggestions.
    
    **Requires authentication**
    """
    from app.services.adaptive_coaching_service import AdaptiveCoachingService
    coaching_service = AdaptiveCoachingService()
    
    health_data = {
        "readiness_score": metrics.readiness_score,
        "sleep_hours": metrics.sleep_hours,
        "fatigue_level": metrics.fatigue_level,
        "heart_rate_variability": metrics.heart_rate_variability,
    }
    
    should_rest = coaching_service.should_skip_workout(health_data)
    recommendations = coaching_service.get_recovery_recommendation(health_data)
    adjustment_factor = coaching_service._calculate_adjustment_factor(health_data)
    
    return {
        "is_ready_for_training": not should_rest,
        "adjustment_factor": adjustment_factor,  # 0.7 = 30% intensity reduction
        "should_rest": should_rest,
        "recommendations": recommendations,
        "health_status": {
            "readiness": "Good" if metrics.readiness_score > 0.7 else "Fair" if metrics.readiness_score > 0.4 else "Poor",
            "sleep": "Good" if 7 <= metrics.sleep_hours <= 9 else "Poor",
            "fatigue": "Low" if metrics.fatigue_level < 0.3 else "Moderate" if metrics.fatigue_level < 0.7 else "High",
        }
    }
