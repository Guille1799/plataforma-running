"""
profile.py - Endpoints para gestión de perfil de atleta y objetivos
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List
import json

from app import models, schemas, security
from app.database import get_db
from app.core.config import settings

router = APIRouter(prefix="/api/v1/profile", tags=["Athlete Profile"])
security_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db),
) -> models.User:
    """Get current authenticated user."""
    token = credentials.credentials
    payload = security.verify_token(token, settings.secret_key, settings.algorithm)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    user_id = int(payload.get("sub"))
    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return user


# ============================================================================
# ATHLETE PROFILE ENDPOINTS
# ============================================================================


@router.get("/", response_model=schemas.AthleteProfileOut)
def get_athlete_profile(current_user: models.User = Depends(get_current_user)):
    """Get current user's athlete profile."""
    return schemas.AthleteProfileOut(
        running_level=current_user.running_level,
        max_heart_rate=current_user.max_heart_rate,
        resting_heart_rate=current_user.resting_heart_rate,
        coaching_style=current_user.coaching_style,
        goals=current_user.goals if current_user.goals else [],
        injuries=current_user.injuries if current_user.injuries else [],
        preferences=current_user.preferences if current_user.preferences else {},
        height_cm=current_user.height_cm,
        weight_kg=current_user.weight_kg,
        vo2_max=current_user.vo2_max,
        birth_date=current_user.birth_date,
        gender=current_user.gender,
    )


@router.patch("/", response_model=schemas.AthleteProfileOut)
def update_athlete_profile(
    profile_update: schemas.AthleteProfileUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update athlete profile."""
    if profile_update.running_level:
        current_user.running_level = profile_update.running_level.value

    if profile_update.max_heart_rate:
        current_user.max_heart_rate = profile_update.max_heart_rate

    if profile_update.coaching_style:
        current_user.coaching_style = profile_update.coaching_style.value

    if profile_update.goals is not None:
        current_user.goals = [goal.model_dump() for goal in profile_update.goals]

    if profile_update.injuries is not None:
        current_user.injuries = [
            injury.model_dump() for injury in profile_update.injuries
        ]

    if profile_update.preferences is not None:
        current_user.preferences = profile_update.preferences.model_dump()

    db.commit()
    db.refresh(current_user)

    return schemas.AthleteProfileOut(
        running_level=current_user.running_level,
        max_heart_rate=current_user.max_heart_rate,
        coaching_style=current_user.coaching_style,
        goals=current_user.goals if current_user.goals else [],
        injuries=current_user.injuries if current_user.injuries else [],
        preferences=current_user.preferences if current_user.preferences else {},
    )


# ============================================================================
# GOALS CRUD ENDPOINTS
# ============================================================================


@router.get("/goals", response_model=List[schemas.Goal])
def get_goals(current_user: models.User = Depends(get_current_user)):
    """Get all user goals."""
    if not current_user.goals:
        return []

    return [schemas.Goal(**goal) for goal in current_user.goals]


@router.post("/goals", response_model=schemas.Goal, status_code=status.HTTP_201_CREATED)
def create_goal(
    goal: schemas.GoalCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new training goal."""
    # Prepare goal data
    new_goal = {
        "name": goal.name,
        "goal_type": goal.goal_type.value,
        "target_value": goal.target_value,
        "deadline": goal.deadline.isoformat() if goal.deadline else None,
        "description": goal.description,
        "completed": False,
        "completed_at": None,
    }

    # Get current goals or initialize empty list
    goals = current_user.goals if current_user.goals else []
    goals.append(new_goal)

    # Update user
    current_user.goals = goals
    db.commit()
    db.refresh(current_user)

    return schemas.Goal(**new_goal)


@router.patch("/goals/{goal_index}", response_model=schemas.Goal)
def update_goal(
    goal_index: int,
    goal_update: schemas.GoalUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a specific goal by index."""
    if not current_user.goals or goal_index >= len(current_user.goals):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found"
        )

    # Get current goal
    goals = current_user.goals
    goal = goals[goal_index]

    # Update fields
    if goal_update.name is not None:
        goal["name"] = goal_update.name

    if goal_update.goal_type is not None:
        goal["goal_type"] = goal_update.goal_type.value

    if goal_update.target_value is not None:
        goal["target_value"] = goal_update.target_value

    if goal_update.deadline is not None:
        goal["deadline"] = goal_update.deadline.isoformat()

    if goal_update.description is not None:
        goal["description"] = goal_update.description

    if goal_update.completed is not None:
        goal["completed"] = goal_update.completed
        if goal_update.completed and not goal.get("completed_at"):
            from datetime import datetime

            goal["completed_at"] = datetime.utcnow().isoformat()

    # Update in DB
    goals[goal_index] = goal
    current_user.goals = goals
    db.commit()
    db.refresh(current_user)

    return schemas.Goal(**goal)


@router.delete("/goals/{goal_index}", status_code=status.HTTP_204_NO_CONTENT)
def delete_goal(
    goal_index: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a specific goal by index."""
    if not current_user.goals or goal_index >= len(current_user.goals):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found"
        )

    # Remove goal
    goals = current_user.goals
    goals.pop(goal_index)

    # Update in DB
    current_user.goals = goals
    db.commit()

    return None
