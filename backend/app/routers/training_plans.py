"""
Training Plans Router

Endpoints for AI-generated personalized training plans.
Supports multi-week plan generation, adaptation, and tracking.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel, Field

from app.database import get_db
from app.models import User
from app.security import verify_token
from app.core.config import settings
from app.services.training_plan_service import get_training_plan_service
from app import schemas
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
    """
    try:
        # Log validated request
        print(f"\n{'='*60}")
        print(f"DEBUG: Request VALIDATED by Pydantic:")
        print(f"  goal_type: {request.goal_type} (type: {type(request.goal_type).__name__})")
        print(f"  goal_date: {request.goal_date} (type: {type(request.goal_date).__name__}, tzinfo: {request.goal_date.tzinfo})")
        print(f"  current_weekly_km: {request.current_weekly_km} (type: {type(request.current_weekly_km).__name__})")
        print(f"  weeks: {request.weeks} (type: {type(request.weeks).__name__})")
        print(f"  notes: {request.notes}")
        print(f"  current_user: {current_user.email} (id: {current_user.id})")
        print(f"{'='*60}\n")
        
        # Validate goal date is in the future
        # Handle both naive and aware datetime objects
        from datetime import timezone
        now = datetime.now(timezone.utc)
        goal_date = request.goal_date
        
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
        if request.weeks > weeks_until_goal_floor:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot create {request.weeks}-week plan for goal {weeks_until_goal_floor} weeks away (days_left: {(goal_date - now).days})"
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
        plan["start_date"] = datetime.now(timezone.utc).isoformat()  # Plan starts today
        
        print(f"\n{'='*60}")
        print(f"💾 STORING PLAN IN DATABASE")
        print(f"Plan ID: {plan.get('plan_id')}")
        print(f"Plan Keys: {list(plan.keys())}")
        print(f"{'='*60}\n")
        
        print(f"Before append - Plan dict keys: {list(plan.keys())}")
        print(f"Before append - Plan ID value: {plan.get('plan_id')}")
        print(f"Before append - Plan ID type: {type(plan.get('plan_id'))}")
        
        current_user.preferences["training_plans"].append(plan)
        
        print(f"After append but before commit:")
        print(f"  - List length: {len(current_user.preferences['training_plans'])}")
        print(f"  - Last item keys: {list(current_user.preferences['training_plans'][-1].keys())}")
        print(f"  - Last item plan_id: {current_user.preferences['training_plans'][-1].get('plan_id')}")
        
        # CRITICAL: Tell SQLAlchemy that the JSON column has changed
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(current_user, "preferences")
        
        db.commit()
        
        # CRITICAL: Refresh the user object from database to see what was actually persisted
        db.refresh(current_user)
        
        print(f"\n{'='*60}")
        print(f"✅ PLAN STORED - Verifying...")
        print(f"Total plans in preferences: {len(current_user.preferences['training_plans'])}")
        if current_user.preferences['training_plans']:
            last_plan = current_user.preferences['training_plans'][-1]
            print(f"Last plan dict: {last_plan}")
            print(f"Last plan ID: {last_plan.get('plan_id')}")
            print(f"Last plan keys: {list(last_plan.keys())}")
        print(f"{'='*60}\n")
        
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
        import traceback
        error_msg = f"Failed to generate training plan: {str(e)}"
        traceback.print_exc()
        print(f"DEBUG: Error details: {error_msg}")
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
                print(f"⚠️ Skipping malformed plan: {str(e)}")
                continue
        
        return summaries
    except Exception as e:
        print(f"❌ Error in list_training_plans: {str(e)}")
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
    
    # Remove plan
    del plans[plan_index]
    current_user.preferences["training_plans"] = plans
    db.commit()
    
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
