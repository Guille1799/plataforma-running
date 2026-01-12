from sqlalchemy.orm import Session, joinedload
from . import models, security, schemas
from typing import List
from datetime import datetime


# ============================================================================
# USER CRUD OPERATIONS
# ============================================================================


def get_user_by_email(db: Session, email: str) -> models.User | None:
    """Get user by email address.

    Args:
        db: Database session
        email: Email address to search for

    Returns:
        User object if found, None otherwise
    """
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> models.User | None:
    """Get user by ID.

    Args:
        db: Database session
        user_id: User ID to search for

    Returns:
        User object if found, None otherwise
    """
    return db.query(models.User).filter(models.User.id == user_id).first()


def create_user(db: Session, user_data: dict) -> models.User:
    """Create a new user in the database.

    Args:
        db: Database session
        user_data: Dictionary containing user data (email, name, password)

    Returns:
        Created User object with ID assigned
    """
    hashed_password = security.hash_password(user_data["password"])

    db_user = models.User(
        email=user_data["email"],
        name=user_data["name"],
        hashed_password=hashed_password,
        role="user",  # New users default to 'user' role
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


# ============================================================================
# WORKOUT CRUD OPERATIONS
# ============================================================================


def create_workout(
    db: Session, user_id: int, workout_data: schemas.WorkoutCreate
) -> models.Workout:
    """Create a new workout record in the database.

    Args:
        db: Database session
        user_id: User ID who owns this workout
        workout_data: Pydantic schema with workout details

    Returns:
        Created Workout object with ID assigned
    """
    db_workout = models.Workout(
        user_id=user_id,
        sport_type=workout_data.sport_type,
        start_time=workout_data.start_time,
        duration_seconds=workout_data.duration_seconds,
        distance_meters=workout_data.distance_meters,
        avg_heart_rate=workout_data.avg_heart_rate,
        max_heart_rate=workout_data.max_heart_rate,
        avg_pace=workout_data.avg_pace,
        max_speed=workout_data.max_speed,
        calories=workout_data.calories,
        elevation_gain=workout_data.elevation_gain,
        file_name=workout_data.file_name,
        # Running Form Metrics
        avg_cadence=workout_data.avg_cadence,
        max_cadence=workout_data.max_cadence,
        avg_stance_time=workout_data.avg_stance_time,
        avg_vertical_oscillation=workout_data.avg_vertical_oscillation,
        avg_stride_length=workout_data.avg_stride_length,
        avg_leg_spring_stiffness=workout_data.avg_leg_spring_stiffness,
        left_right_balance=workout_data.left_right_balance,
    )

    db.add(db_workout)
    db.commit()
    db.refresh(db_workout)

    return db_workout


def get_workout_by_id(db: Session, workout_id: int) -> models.Workout | None:
    """Get workout by ID.

    Args:
        db: Database session
        workout_id: Workout ID to search for

    Returns:
        Workout object if found, None otherwise
    """
    return db.query(models.Workout).filter(models.Workout.id == workout_id).first()


def get_workout_by_start_time(
    db: Session, user_id: int, start_time: datetime
) -> models.Workout | None:
    """Get workout by start time and user ID to prevent duplicates.

    Args:
        db: Database session
        user_id: User ID
        start_time: Workout start time

    Returns:
        Workout object if found, None otherwise
    """
    return (
        db.query(models.Workout)
        .filter(
            models.Workout.user_id == user_id, models.Workout.start_time == start_time
        )
        .first()
    )


def get_user_workouts(
    db: Session,
    user_id: int,
    limit: int = 50,
    offset: int = 0,
) -> List[models.Workout]:
    """Get all workouts for a user with pagination.

    Args:
        db: Database session
        user_id: User ID to filter by
        limit: Maximum number of results (default 50)
        offset: Number of results to skip (default 0)

    Returns:
        List of Workout objects
    """
    return (
        db.query(models.Workout)
        .filter(models.Workout.user_id == user_id)
        .options(joinedload(models.Workout.user))  # Prevent N+1 query
        .order_by(models.Workout.start_time.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )


def get_user_workout_stats(db: Session, user_id: int) -> schemas.WorkoutStats:
    """Get aggregated statistics for a user's workouts.

    Args:
        db: Database session
        user_id: User ID to aggregate stats for

    Returns:
        WorkoutStats object with aggregated data
    """
    workouts = db.query(models.Workout).filter(
        models.Workout.user_id == user_id
    ).options(joinedload(models.Workout.user)).all()

    if not workouts:
        return schemas.WorkoutStats(
            total_workouts=0,
            total_distance_km=0.0,
            total_duration_hours=0.0,
            sports_breakdown={},
        )

    total_distance_km = sum(w.distance_meters for w in workouts) / 1000
    total_duration_hours = sum(w.duration_seconds for w in workouts) / 3600
    avg_heart_rate = (
        sum(w.avg_heart_rate for w in workouts if w.avg_heart_rate)
        / len([w for w in workouts if w.avg_heart_rate])
        if any(w.avg_heart_rate for w in workouts)
        else None
    )
    total_calories = sum(w.calories for w in workouts if w.calories)

    # Calculate average pace
    total_distance_km_for_pace = (
        sum(w.distance_meters for w in workouts if w.avg_pace) / 1000
    )
    avg_pace_sec_per_km = (
        sum(w.duration_seconds for w in workouts if w.avg_pace)
        / total_distance_km_for_pace
        if total_distance_km_for_pace > 0
        else None
    )

    # Sports breakdown
    sports_breakdown: dict = {}
    for workout in workouts:
        sports_breakdown[workout.sport_type] = (
            sports_breakdown.get(workout.sport_type, 0) + 1
        )

    return schemas.WorkoutStats(
        total_workouts=len(workouts),
        total_distance_km=round(total_distance_km, 2),
        total_duration_hours=round(total_duration_hours, 2),
        avg_pace_min_per_km=(
            round(avg_pace_sec_per_km / 60, 2) if avg_pace_sec_per_km else None
        ),
        avg_heart_rate=int(avg_heart_rate) if avg_heart_rate else None,
        total_calories=round(total_calories, 2) if total_calories else None,
        sports_breakdown=sports_breakdown,
    )


# ============================================================================
# TRAINING PLAN CRUD OPERATIONS
# ============================================================================


def create_training_plan(
    db: Session,
    user_id: int,
    plan_id: str,
    plan_name: str,
    goal_type: str,
    goal_date: datetime | None,
    start_date: datetime,
    end_date: datetime,
    total_weeks: int,
    plan_data: dict,
    metrics: dict | None = None,
    status: str = "active",
    current_week: int = 1,
) -> models.TrainingPlan:
    """Create a new training plan in the database.
    
    Args:
        db: Database session
        user_id: User ID who owns the plan
        plan_id: Unique plan identifier
        plan_name: Name of the training plan
        goal_type: Type of goal (5k, 10k, marathon, etc.)
        goal_date: Target race/event date (optional)
        start_date: When the plan starts
        end_date: When the plan ends
        total_weeks: Total number of weeks in the plan
        plan_data: Complete plan structure (JSON)
        metrics: Calculated metrics (JSON, optional)
        status: Plan status (active, completed, paused, archived)
        current_week: Current week being executed (1-based)
        
    Returns:
        Created TrainingPlan object
    """
    db_plan = models.TrainingPlan(
        user_id=user_id,
        plan_id=plan_id,
        plan_name=plan_name,
        goal_type=goal_type,
        goal_date=goal_date,
        start_date=start_date,
        end_date=end_date,
        total_weeks=total_weeks,
        current_week=current_week,
        status=status,
        plan_data=plan_data,
        metrics=metrics,
    )
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan


def get_training_plan_by_id(
    db: Session, plan_id: str, user_id: int | None = None
) -> models.TrainingPlan | None:
    """Get training plan by plan_id.
    
    Args:
        db: Database session
        plan_id: Unique plan identifier
        user_id: Optional user ID to filter by ownership
        
    Returns:
        TrainingPlan object if found, None otherwise
    """
    query = db.query(models.TrainingPlan).filter(models.TrainingPlan.plan_id == plan_id)
    if user_id is not None:
        query = query.filter(models.TrainingPlan.user_id == user_id)
    return query.first()


def get_training_plan_by_db_id(
    db: Session, id: int, user_id: int | None = None
) -> models.TrainingPlan | None:
    """Get training plan by database ID.
    
    Args:
        db: Database session
        id: Database primary key ID
        user_id: Optional user ID to filter by ownership
        
    Returns:
        TrainingPlan object if found, None otherwise
    """
    query = db.query(models.TrainingPlan).filter(models.TrainingPlan.id == id)
    if user_id is not None:
        query = query.filter(models.TrainingPlan.user_id == user_id)
    return query.first()


def get_user_training_plans(
    db: Session,
    user_id: int,
    status: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> List[models.TrainingPlan]:
    """Get all training plans for a user.
    
    Args:
        db: Database session
        user_id: User ID
        status: Optional status filter (active, completed, paused, archived)
        limit: Maximum number of plans to return
        offset: Number of plans to skip
        
    Returns:
        List of TrainingPlan objects
    """
    query = db.query(models.TrainingPlan).filter(models.TrainingPlan.user_id == user_id)
    if status is not None:
        query = query.filter(models.TrainingPlan.status == status)
    return (
        query.order_by(models.TrainingPlan.created_at.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )


def update_training_plan(
    db: Session,
    plan_id: str,
    user_id: int,
    updates: dict,
) -> models.TrainingPlan | None:
    """Update a training plan.
    
    Args:
        db: Database session
        plan_id: Unique plan identifier
        user_id: User ID (for ownership verification)
        updates: Dictionary of fields to update
        
    Returns:
        Updated TrainingPlan object, or None if not found
    """
    plan = get_training_plan_by_id(db, plan_id, user_id)
    if not plan:
        return None
    
    # Update allowed fields
    allowed_fields = [
        "plan_name",
        "status",
        "current_week",
        "plan_data",
        "metrics",
        "goal_date",
    ]
    for field in allowed_fields:
        if field in updates:
            setattr(plan, field, updates[field])
    
    plan.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(plan)
    return plan


def delete_training_plan(
    db: Session, plan_id: str, user_id: int
) -> bool:
    """Delete a training plan.
    
    Args:
        db: Database session
        plan_id: Unique plan identifier
        user_id: User ID (for ownership verification)
        
    Returns:
        True if deleted, False if not found
    """
    plan = get_training_plan_by_id(db, plan_id, user_id)
    if not plan:
        return False
    
    db.delete(plan)
    db.commit()
    return True
