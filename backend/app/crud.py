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
    workouts = db.query(models.Workout).filter(models.Workout.user_id == user_id).all()

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
