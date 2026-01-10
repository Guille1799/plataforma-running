"""
coach.py - AI Coach endpoints for workout analysis and training plans
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session, joinedload
from typing import Dict, Any, Optional, List
from datetime import datetime

from app import models, security, schemas
from app.database import get_db
from app.core.config import settings
from app.services.coach_service import get_coach_service
from app.utils.rate_limiter import limiter
from app.dependencies.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/coach", tags=["AI Coach"])

# Lazy-loaded coach service
coach_service = None

def _get_coach_service():
    """Get coach service lazily."""
    global coach_service
    if coach_service is None:
        coach_service = get_coach_service()
    return coach_service


# ============================================================================
# POST-WORKOUT ANALYSIS
# ============================================================================

@router.post("/analyze/{workout_id}", response_model=Dict[str, Any])
def analyze_workout(
    workout_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyze workout with AI coach and get personalized feedback.
    
    Provides:
    - Effort assessment based on HR zones and pace
    - Technical analysis of performance metrics
    - Recommendations for next training session
    - Personalized feedback based on coaching style
    
    Args:
        workout_id: ID of workout to analyze
        
    Returns:
        Dict with AI analysis, metrics, and recommendations
    """
    # Get workout with eager loading to prevent N+1 queries
    workout = db.query(models.Workout).filter(
        models.Workout.id == workout_id,
        models.Workout.user_id == current_user.id
    ).options(joinedload(models.Workout.user)).first()
    
    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout not found"
        )
    
    # Get recent workouts for context (last 10)
    # Use eager loading to prevent potential N+1 queries if workout.user is accessed
    recent_workouts = (
        db.query(models.Workout)
        .filter(models.Workout.user_id == current_user.id)
        .options(joinedload(models.Workout.user))  # Eager load user relationship
        .order_by(models.Workout.start_time.desc())
        .limit(10)
        .all()
    )
    
    # Ensure user has max_heart_rate for zone calculation
    if not current_user.max_heart_rate and workout.max_heart_rate:
        # Auto-set max HR from workout if not configured
        current_user.max_heart_rate = workout.max_heart_rate
        db.commit()
    
    try:
        # Call AI coach service
        analysis_result = _get_coach_service().analyze_workout(
            workout=workout,
            user=current_user,
            recent_workouts=recent_workouts,
            db=db
        )
        
        return analysis_result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing workout: {str(e)}"
        )


# ============================================================================
# HR ZONES CALCULATOR
# ============================================================================

@router.get("/hr-zones", response_model=Dict[str, Any])
def get_hr_zones(
    current_user: models.User = Depends(get_current_user)
):
    """Get user's heart rate training zones.
    
    Returns 5-zone system based on max heart rate.
    If max HR not set, uses 220 - age estimate or last workout max.
    
    Returns:
        Dict with zones and their characteristics
    """
    max_hr = current_user.max_heart_rate
    
    if not max_hr:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Max heart rate not configured. Please update your profile or sync workouts."
        )
    
    zones = _get_coach_service().calculate_hr_zones(max_hr)
    
    return {
        "max_heart_rate": max_hr,
        "zones": zones,
        "note": "Estas zonas son estimaciones. Ajusta según tu percepción de esfuerzo."
    }


# ============================================================================
# WEEKLY TRAINING PLAN
# ============================================================================

@router.post("/plan", response_model=Dict[str, Any])
def generate_training_plan(
    request: schemas.TrainingPlanRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate highly personalized training plan.
    
    Creates a multi-week training plan based on:
    - General goal (marathon, 10K, fitness, etc.)
    - Priority (speed, endurance, recovery, balanced)
    - Target race information (if applicable)
    - Training availability and preferences
    - Strength training and cross-training preferences
    - Training method (pace-based or HR-based)
    - Recovery focus
    - Injury considerations
    
    Args:
        request: TrainingPlanRequest with all personalization parameters
        
    Returns:
        Dict with complete training plan organized by weeks and days
    """
    try:
        # Get recent workouts for context with eager loading to prevent N+1 queries
        recent_workouts = db.query(models.Workout).filter(
            models.Workout.user_id == current_user.id
        ).options(joinedload(models.Workout.user)).order_by(models.Workout.start_time.desc()).limit(20).all()
        
        plan = _get_coach_service().generate_personalized_training_plan(
            user=current_user,
            recent_workouts=recent_workouts,
            plan_request=request,
            db=db
        )
        
        # SAVE PLAN to user preferences
        if not current_user.preferences:
            current_user.preferences = {}
        
        if "training_plans" not in current_user.preferences:
            current_user.preferences["training_plans"] = []
        
        # Add metadata with ISO strings for JSON serialization
        from datetime import datetime
        plan["plan_id"] = plan.get("id", f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        plan["plan_name"] = plan.get("plan_name", f"{request.general_goal.upper()} Plan")
        plan["goal_date"] = datetime.now().isoformat()
        plan["total_weeks"] = plan.get("plan_duration_weeks", request.plan_duration_weeks or 12)
        plan["created_at"] = datetime.now().isoformat()
        plan["status"] = "active"
        
        current_user.preferences["training_plans"].append(plan)
        db.commit()
        
        logger.info(f"✅ Training plan saved for user {current_user.id}")
        
        return {"plan": plan, "success": True, "message": "Plan created and saved successfully"}
        
    except Exception as e:
        logger.error(f"❌ Error generating plan: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating plan: {str(e)}"
        )


# ============================================================================
# GET TRAINING PLANS
# ============================================================================

@router.get("/plan/list", response_model=Dict[str, Any])
def list_training_plans(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all training plans for the current user."""
    plans = []
    if current_user.preferences and "training_plans" in current_user.preferences:
        plans = current_user.preferences["training_plans"]
    
    return {
        "plans": plans,
        "count": len(plans)
    }


@router.get("/plan/{plan_id}", response_model=Dict[str, Any])
def get_training_plan(
    plan_id: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific training plan by ID."""
    if not current_user.preferences or "training_plans" not in current_user.preferences:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No training plans found"
        )
    
    plan = next((p for p in current_user.preferences["training_plans"] if p.get("id") == plan_id), None)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Training plan {plan_id} not found"
        )
    
    return {
        "plan": plan,
        "success": True
    }


# ============================================================================
# RUNNING FORM ANALYSIS
# ============================================================================

@router.post("/analyze-form/{workout_id}", response_model=Dict[str, Any])
def analyze_running_form(
    workout_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyze running form and technique from workout metrics.
    
    Provides technical analysis of:
    - Pace consistency
    - Heart rate variability
    - Elevation efficiency
    - Overall running economy
    
    Args:
        workout_id: ID of workout to analyze
        
    Returns:
        Dict with form metrics, issues, and recommendations
    """
    # Get workout with eager loading to prevent N+1 queries
    workout = db.query(models.Workout).filter(
        models.Workout.id == workout_id,
        models.Workout.user_id == current_user.id
    ).options(joinedload(models.Workout.user)).first()
    
    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout not found"
        )
    
    try:
        form_analysis = _get_coach_service().analyze_running_form(
            workout=workout,
            user=current_user
        )
        
        return form_analysis
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing form: {str(e)}"
        )


# ============================================================================
# CHATBOT WITH MEMORY
# ============================================================================

@router.post("/chat", response_model=schemas.ChatResponse)
@limiter.limit("10/hour")
def chat_with_coach(
    request: Request,
    message: schemas.ChatMessageCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Chat with AI coach maintaining conversation history.
    
    Natural conversation with your personal running coach.
    The coach has access to your complete profile, goals, and workout history.
    
    Features:
    - Maintains conversation context
    - Personalized advice based on your data
    - Adaptive coaching style
    - Answers questions about training, technique, nutrition, etc.
    
    Args:
        message: User message to send to coach
        
    Returns:
        ChatResponse with assistant reply and conversation metadata
    """
    # Get conversation history (last 20 messages for context)
    conversation_history = db.query(models.ChatMessage).filter(
        models.ChatMessage.user_id == current_user.id
    ).order_by(models.ChatMessage.created_at.desc()).limit(20).all()
    
    # Reverse to chronological order
    conversation_history = list(reversed(conversation_history))
    
    # Get recent workouts for context
    # Use eager loading to prevent potential N+1 queries if workout.user is accessed
    recent_workouts = (
        db.query(models.Workout)
        .filter(models.Workout.user_id == current_user.id)
        .options(joinedload(models.Workout.user))  # Eager load user relationship
        .order_by(models.Workout.start_time.desc())
        .limit(10)
        .all()
    )
    
    try:
        # Get AI response
        chat_result = _get_coach_service().chat_with_coach(
            user=current_user,
            user_message=message.message,
            conversation_history=conversation_history,
            recent_workouts=recent_workouts,
            db=db
        )
        
        # Save user message
        user_msg = models.ChatMessage(
            user_id=current_user.id,
            role="user",
            content=message.message
        )
        db.add(user_msg)
        db.flush()
        
        # Save assistant message
        assistant_msg = models.ChatMessage(
            user_id=current_user.id,
            role="assistant",
            content=chat_result["response"],
            tokens_used=chat_result["tokens_used"]
        )
        db.add(assistant_msg)
        db.commit()
        
        # Refresh to get IDs and timestamps
        db.refresh(user_msg)
        db.refresh(assistant_msg)
        
        return schemas.ChatResponse(
            user_message=schemas.ChatMessageOut(
                id=user_msg.id,
                role=user_msg.role,
                content=user_msg.content,
                created_at=user_msg.created_at
            ),
            assistant_message=schemas.ChatMessageOut(
                id=assistant_msg.id,
                role=assistant_msg.role,
                content=assistant_msg.content,
                created_at=assistant_msg.created_at
            ),
            tokens_used=chat_result["tokens_used"],
            conversation_length=chat_result["conversation_length"]
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in chat: {str(e)}"
        )


@router.get("/chat/history", response_model=List[schemas.ChatMessageOut])
def get_chat_history(
    limit: int = 50,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get chat conversation history.
    
    Args:
        limit: Maximum number of messages to return (default: 50)
        
    Returns:
        List of chat messages ordered by creation time
    """
    messages = db.query(models.ChatMessage).filter(
        models.ChatMessage.user_id == current_user.id
    ).order_by(models.ChatMessage.created_at.desc()).limit(limit).all()
    
    # Reverse to chronological order
    messages = list(reversed(messages))
    
    return [
        schemas.ChatMessageOut(
            id=msg.id,
            role=msg.role,
            content=msg.content,
            created_at=msg.created_at
        )
        for msg in messages
    ]


@router.delete("/chat/history", status_code=status.HTTP_204_NO_CONTENT)
def clear_chat_history(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Clear all chat conversation history.
    
    Deletes all messages in the conversation.
    This action cannot be undone.
    """
    db.query(models.ChatMessage).filter(
        models.ChatMessage.user_id == current_user.id
    ).delete()
    db.commit()
    
    return None


# ============================================================================
# DEEP WORKOUT ANALYSIS (NEW)
# ============================================================================

@router.post("/analyze-deep/{workout_id}", response_model=Dict[str, Any])
def analyze_workout_deep(
    workout_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Análisis exhaustivo de entrenamiento con AI:
    - Análisis completo del workout
    - Comparación con entrenamientos similares
    - Análisis técnico de forma de carrera
    - Áreas de mejora identificadas
    - Plan de entrenamientos personalizado
    
    Returns comprehensive structured analysis.
    """
    # Get the workout with eager loading to prevent N+1 queries
    workout = db.query(models.Workout).filter(
        models.Workout.id == workout_id,
        models.Workout.user_id == current_user.id
    ).options(joinedload(models.Workout.user)).first()
    
    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout not found"
        )
    
    try:
        analysis = _get_coach_service().analyze_workout_deep(
            db=db,
            user=current_user,
            workout=workout
        )
        return analysis
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis error: {str(e)}"
        )


@router.get("/personalized-recommendation", response_model=Dict[str, Any])
def get_personalized_recommendation(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get personalized workout recommendation based on device type and use case.
    
    Tailors coaching style and recommendations to the user's primary device
    and selected use case (fitness tracker, training coach, race prep, etc).
    """
    primary_device = current_user.primary_device or 'manual'
    use_case = current_user.use_case or 'general_health'
    coach_style = current_user.coach_style_preference or 'balanced'
    
    # Get base recommendation
    base_recommendation = _get_coach_service().generate_health_aware_recommendation(db, current_user)
    
    # Customize based on device type
    device_focus = {
        'garmin': {
            'title': 'Garmin Advanced Training',
            'focus': 'Advanced metrics (HRV, Body Battery, Training Load)',
            'tips': [
                'Monitor your Body Battery - train hard when it\'s above 60',
                'Use HRV trends to identify overtraining patterns',
                'Respect your training load recommendations from your watch'
            ]
        },
        'xiaomi': {
            'title': 'Daily Activity Tracker',
            'focus': 'Consistent activity and sleep optimization',
            'tips': [
                'Aim for consistent daily activity levels',
                'Sleep quality matters more than quantity',
                'Build streaks of consecutive training days'
            ]
        },
        'manual': {
            'title': 'Personal Training Log',
            'focus': 'Self-awareness and goal tracking',
            'tips': [
                'Log your workouts consistently for better insights',
                'Pay attention to how you feel each day',
                'Track personal records and celebrate achievements'
            ]
        },
        'apple': {
            'title': 'Apple Health Integration',
            'focus': 'Holistic wellness tracking',
            'tips': [
                'Your Apple Watch captures detailed metrics',
                'Focus on activity rings and workout consistency',
                'Use heart rate data to guide intensity'
            ]
        },
        'strava': {
            'title': 'Social Training Network',
            'focus': 'Community engagement and segment PRs',
            'tips': [
                'Use segments to track improvement over time',
                'Share your achievements with the community',
                'Find running partners through Strava'
            ]
        }
    }
    
    # Customize based on use case
    use_case_guidance = {
        'fitness_tracker': 'Focus on consistency and daily movement. No pressure for intensity.',
        'training_coach': 'Follow structured training plans. Balance easy and hard efforts.',
        'race_prep': 'Follow your training plan religiously. Every workout matters for peak race fitness.',
        'general_health': 'Exercise for overall wellness. Enjoy the process, don\'t obsess over metrics.'
    }
    
    # Build personalized response
    personalized = base_recommendation.copy()
    personalized['device_customization'] = device_focus.get(primary_device, device_focus['manual'])
    personalized['use_case_guidance'] = use_case_guidance.get(use_case, use_case_guidance['general_health'])
    personalized['coaching_style'] = coach_style
    
    # Add device-specific metrics to watch
    if primary_device == 'garmin':
        personalized['key_metrics'] = ['body_battery', 'hrv_ms', 'stress_level', 'training_load']
    elif primary_device == 'xiaomi':
        personalized['key_metrics'] = ['sleep_score', 'daily_steps', 'activity_streak']
    else:
        personalized['key_metrics'] = ['workout_frequency', 'total_distance', 'average_pace']
    
    return personalized

