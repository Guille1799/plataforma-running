from sqlalchemy import Boolean, Column, Integer, String, DateTime, Float, ForeignKey, JSON, Date, UniqueConstraint
from datetime import datetime
from .database import Base


class User(Base):
    """User model representing registered users in the system.
    
    Attributes:
        id: Unique identifier (primary key)
        name: User's full name
        email: User's email address (unique)
        hashed_password: Bcrypt hashed password
        is_active: Whether the user account is active
        created_at: Account creation timestamp
        garmin_email: User's Garmin Connect email (optional)
        garmin_token: Encrypted Garmin session token (optional)
        garmin_connected_at: When Garmin was last connected (optional)
        
        # Athlete Profile fields
        running_level: Running experience level (beginner/intermediate/advanced)
        max_heart_rate: Maximum heart rate in bpm (optional, calculated or tested)
        goals: JSON array of training goals with targets and deadlines
        coaching_style: Preferred coaching style (motivator/technical/balanced/custom)
        injuries: JSON array of injury history with dates and descriptions
        preferences: JSON object with training preferences (music, pace, time_of_day, etc)
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Garmin Connect integration fields
    garmin_email = Column(String, nullable=True)
    garmin_token = Column(String, nullable=True)  # Encrypted token from garth
    garmin_connected_at = Column(DateTime, nullable=True)
    last_garmin_sync = Column(DateTime, nullable=True)  # Timestamp of last successful sync
    
    # Athlete physical data
    height_cm = Column(Float, nullable=True)  # Height in centimeters
    weight_kg = Column(Float, nullable=True)  # Weight in kilograms
    
    # Heart Rate Zones (JSON: [{"zone": 1, "min": 100, "max": 130}, ...])
    hr_zones = Column(JSON, nullable=True, default=list)
    
    # Power Zones (JSON: [{"zone": 1, "min": 0, "max": 100}, ...])
    power_zones = Column(JSON, nullable=True, default=list)
    
    # Athlete Profile fields
    running_level = Column(String, nullable=True, default="intermediate")  # beginner/intermediate/advanced
    max_heart_rate = Column(Integer, nullable=True)  # bpm
    goals = Column(JSON, nullable=True, default=list)  # [{"name": "sub-40 10K", "target_pace": "4:00", "deadline": "2025-12-31", "type": "race"}]
    coaching_style = Column(String, nullable=True, default="balanced")  # motivator/technical/balanced/custom
    injuries = Column(JSON, nullable=True, default=list)  # [{"date": "2024-06-15", "type": "knee", "description": "IT band", "recovered": true}]
    preferences = Column(JSON, nullable=True, default=dict)  # {"music": true, "preferred_pace_range": [5, 6], "time_of_day": "evening"}
    
    # Strava integration fields
    strava_athlete_id = Column(Integer, nullable=True, unique=True)
    strava_access_token = Column(String, nullable=True)
    strava_refresh_token = Column(String, nullable=True)
    strava_token_expires_at = Column(DateTime, nullable=True)
    strava_connected_at = Column(DateTime, nullable=True)
    last_strava_sync = Column(DateTime, nullable=True)
    
    # Google Fit integration fields
    google_fit_token = Column(String, nullable=True)
    google_fit_refresh_token = Column(String, nullable=True)
    google_fit_token_expires_at = Column(DateTime, nullable=True)
    google_fit_connected_at = Column(DateTime, nullable=True)
    last_google_fit_sync = Column(DateTime, nullable=True)
    
    # Apple Health integration fields (via HealthKit export)
    apple_health_connected_at = Column(DateTime, nullable=True)
    last_apple_health_sync = Column(DateTime, nullable=True)
    
    # Onboarding fields
    onboarding_completed = Column(Boolean, default=False, nullable=False)  # Has user completed onboarding?
    primary_device = Column(String, nullable=True)  # garmin, xiaomi, strava, manual, apple
    use_case = Column(String, nullable=True)  # fitness_tracker, training_coach, race_prep, general_health
    coach_style_preference = Column(String, nullable=True)  # motivator, technical, balanced, custom
    language = Column(String, default="es", nullable=False)  # es, en, fr, etc
    enable_notifications = Column(Boolean, default=True, nullable=False)
    integration_sources = Column(JSON, nullable=True, default=list)  # ["garmin", "strava", "google_fit"] - order matters
    onboarding_completed_at = Column(DateTime, nullable=True)
    
    # Multi-device configuration
    devices_configured = Column(JSON, nullable=True, default=list)  # List of configured device IDs
    device_sync_config = Column(JSON, nullable=True, default=dict)  # {"garmin": {"enabled": true, "sync_interval_hours": 1, "last_sync": "2025-11-14T10:30:00", "auto_sync": true}, ...}
    device_sync_enabled = Column(Boolean, default=True, nullable=False)  # Master toggle for all syncing



class Workout(Base):
    """Workout model representing training sessions from FIT files.
    
    Attributes:
        id: Unique identifier (primary key)
        user_id: Foreign key to User
        sport_type: Type of sport (running, cycling, etc)
        start_time: When the workout started
        duration_seconds: Total workout duration in seconds
        distance_meters: Total distance covered in meters
        avg_heart_rate: Average heart rate (optional)
        max_heart_rate: Maximum heart rate (optional)
        avg_pace: Average pace in min/km (optional)
        max_speed: Maximum speed in km/h (optional)
        calories: Energy expenditure (optional)
        elevation_gain: Total elevation gained (optional)
        
        # Running Form Metrics
        avg_cadence: Average steps per minute (optional)
        max_cadence: Maximum cadence (optional)
        avg_stance_time: Average ground contact time in ms (optional)
        avg_vertical_oscillation: Average vertical bounce in cm (optional)
        avg_leg_spring_stiffness: Average leg spring stiffness (optional)
        left_right_balance: Left/right foot strike balance % (optional)
        
        file_name: Original FIT file name
        created_at: When record was created
    """
    __tablename__ = "workouts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    sport_type = Column(String, nullable=False)
    start_time = Column(DateTime, nullable=False)
    duration_seconds = Column(Integer, nullable=False)
    distance_meters = Column(Float, nullable=False)
    avg_heart_rate = Column(Integer, nullable=True)
    max_heart_rate = Column(Integer, nullable=True)
    avg_pace = Column(Float, nullable=True)
    max_speed = Column(Float, nullable=True)
    calories = Column(Float, nullable=True)
    elevation_gain = Column(Float, nullable=True)
    
    # Running Form Metrics
    avg_cadence = Column(Float, nullable=True)  # steps per minute
    max_cadence = Column(Float, nullable=True)
    avg_stance_time = Column(Float, nullable=True)  # milliseconds
    avg_vertical_oscillation = Column(Float, nullable=True)  # centimeters
    avg_leg_spring_stiffness = Column(Float, nullable=True)  # stiffness ratio
    left_right_balance = Column(Float, nullable=True)  # percentage (0-100, 50=balanced)
    
    # Data source metadata
    source_type = Column(String, nullable=True, default="garmin_fit")  # garmin_fit, garmin_oauth, gpx_upload, tcx_upload, strava
    data_quality = Column(String, nullable=True, default="high")  # high (FIT), medium (GPX with HR), basic (GPX minimal)
    
    file_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class ChatMessage(Base):
    """Chat message model for coach conversations.
    
    Stores conversation history between user and AI coach.
    
    Attributes:
        id: Unique identifier (primary key)
        user_id: Foreign key to User
        role: Message role (user/assistant)
        content: Message content
        tokens_used: Tokens consumed by this message (for assistant messages)
        created_at: When message was sent
    """
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    role = Column(String, nullable=False)  # "user" or "assistant"
    content = Column(String, nullable=False)
    tokens_used = Column(Integer, nullable=True)  # Only for assistant messages
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class HealthMetric(Base):
    """Daily health and wellness metrics from various sources.
    
    Stores recovery, sleep, and readiness data for personalized coaching.
    
    Attributes:
        id: Unique identifier (primary key)
        user_id: Foreign key to User
        date: Date for these metrics (one record per user per day)
        
        # Recovery Metrics
        hrv_ms: Heart Rate Variability in milliseconds (higher = better recovery)
        resting_hr_bpm: Resting heart rate in beats per minute (lower = fitter)
        hrv_baseline_ms: User's 7-day HRV baseline for comparison
        resting_hr_baseline_bpm: User's 7-day resting HR baseline
        
        # Sleep Metrics
        sleep_duration_minutes: Total sleep time
        sleep_score: Overall sleep quality score (0-100)
        deep_sleep_minutes: Deep/slow-wave sleep (physical recovery)
        rem_sleep_minutes: REM sleep (mental/cognitive recovery)
        light_sleep_minutes: Light sleep
        awake_minutes: Time awake during sleep period
        
        # Readiness Metrics
        body_battery: Garmin's energy level score (0-100)
        readiness_score: Normalized readiness across all platforms (0-100)
        stress_level: Average stress level for the day (0-100, lower = better)
        recovery_score: Platform-specific recovery score (Whoop, Polar, etc.)
        
        # Activity Metrics
        steps: Daily step count
        calories_burned: Total calories burned (active + resting)
        active_calories: Calories from activity only
        intensity_minutes: Minutes of moderate-to-vigorous activity
        
        # Respiratory Metrics
        respiration_rate: Average breaths per minute during sleep
        spo2_percentage: Blood oxygen saturation (95-100% normal)
        
        # Subjective Metrics (Manual Entry)
        energy_level: Self-reported energy (1-5 scale)
        soreness_level: Self-reported muscle soreness (1-5 scale)
        mood: Self-reported mood (1-5 scale)
        motivation: Self-reported motivation to train (1-5 scale)
        notes: Free-text notes about how user feels
        
        # Metadata
        source: Data source (garmin, apple_health, google_fit, strava, polar, whoop, oura, manual)
        data_quality: Quality indicator (high, medium, basic)
        created_at: Timestamp when record was created
    """
    __tablename__ = "health_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    
    # Recovery Metrics
    hrv_ms = Column(Float, nullable=True)
    resting_hr_bpm = Column(Integer, nullable=True)
    hrv_baseline_ms = Column(Float, nullable=True)
    resting_hr_baseline_bpm = Column(Integer, nullable=True)
    
    # Sleep Metrics
    sleep_duration_minutes = Column(Integer, nullable=True)
    sleep_score = Column(Integer, nullable=True)
    deep_sleep_minutes = Column(Integer, nullable=True)
    rem_sleep_minutes = Column(Integer, nullable=True)
    light_sleep_minutes = Column(Integer, nullable=True)
    awake_minutes = Column(Integer, nullable=True)
    
    # Readiness Metrics
    body_battery = Column(Integer, nullable=True)
    readiness_score = Column(Integer, nullable=True)
    stress_level = Column(Integer, nullable=True)
    recovery_score = Column(Integer, nullable=True)
    
    # Activity Metrics
    steps = Column(Integer, nullable=True)
    calories_burned = Column(Integer, nullable=True)
    active_calories = Column(Integer, nullable=True)
    intensity_minutes = Column(Integer, nullable=True)
    
    # Respiratory Metrics
    respiration_rate = Column(Float, nullable=True)
    spo2_percentage = Column(Float, nullable=True)
    
    # Subjective Metrics (Manual Entry)
    energy_level = Column(Integer, nullable=True)  # 1-5
    soreness_level = Column(Integer, nullable=True)  # 1-5
    mood = Column(Integer, nullable=True)  # 1-5
    motivation = Column(Integer, nullable=True)  # 1-5
    notes = Column(String, nullable=True)
    
    # Metadata
    source = Column(String, nullable=False, default="manual")
    data_quality = Column(String, nullable=False, default="basic")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        UniqueConstraint('user_id', 'date', name='uix_user_date_health'),
    )