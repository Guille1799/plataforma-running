"""
Training Plan Matching Service
Automatically matches completed workouts with planned workouts.
"""
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session
import logging

from .. import models

logger = logging.getLogger(__name__)


class TrainingPlanMatchingService:
    """Service for matching completed workouts with planned workouts."""
    
    def match_workout(
        self,
        planned_workout: Dict[str, Any],
        actual_workout: models.Workout,
        date_tolerance_days: int = 1,
        distance_tolerance_percentage: float = 20.0
    ) -> Tuple[bool, float]:
        """
        Determine if an actual workout matches a planned workout.
        
        Args:
            planned_workout: Planned workout dict
            actual_workout: Actual Workout model
            date_tolerance_days: Days tolerance for date matching (default 1)
            distance_tolerance_percentage: Distance tolerance percentage (default 20%)
            
        Returns:
            Tuple of (matches: bool, confidence: float)
        """
        # Date matching
        planned_date = planned_workout.get('date')
        if not planned_date:
            # Calculate date from day number
            return False, 0.0
        
        if isinstance(planned_date, str):
            planned_date_obj = datetime.fromisoformat(planned_date.replace('Z', '+00:00')).date()
        else:
            planned_date_obj = planned_date if isinstance(planned_date, date) else planned_date.date()
        
        actual_date = actual_workout.start_time.date()
        date_diff = abs((actual_date - planned_date_obj).days)
        
        if date_diff > date_tolerance_days:
            return False, 0.0
        
        # Distance matching
        planned_distance = planned_workout.get('distance_km', 0)
        actual_distance = actual_workout.distance_meters / 1000
        
        if planned_distance > 0:
            distance_diff_percentage = abs(actual_distance - planned_distance) / planned_distance * 100
            if distance_diff_percentage > distance_tolerance_percentage:
                return False, 0.0
        
        # Type matching (optional, helps confidence)
        workout_type_match = False
        planned_type = planned_workout.get('type', '').lower()
        # Basic type matching (can be improved)
        if 'easy' in planned_type or 'recovery' in planned_type:
            workout_type_match = actual_workout.avg_pace and actual_workout.avg_pace > 300  # Slow pace
        elif 'tempo' in planned_type or 'interval' in planned_type:
            workout_type_match = actual_workout.avg_pace and actual_workout.avg_pace < 240  # Fast pace
        
        # Calculate confidence score
        confidence = 1.0 - (date_diff / date_tolerance_days * 0.3)
        if planned_distance > 0:
            distance_confidence = 1.0 - (distance_diff_percentage / distance_tolerance_percentage * 0.3)
            confidence = min(confidence, distance_confidence)
        if workout_type_match:
            confidence = min(confidence + 0.1, 1.0)
        
        return True, confidence
    
    def match_all_workouts(
        self,
        plan_data: Dict[str, Any],
        user_id: int,
        db: Session,
        start_date: date
    ) -> List[Dict[str, Any]]:
        """
        Match all workouts in a plan with actual workouts.
        
        Args:
            plan_data: Plan data dict
            user_id: User ID
            db: Database session
            start_date: Plan start date
            
        Returns:
            List of match results
        """
        # Get all actual workouts since plan start
        actual_workouts = db.query(models.Workout).filter(
            models.Workout.user_id == user_id,
            models.Workout.start_time >= datetime.combine(start_date, datetime.min.time())
        ).order_by(models.Workout.start_time).all()
        
        matches = []
        matched_workout_ids = set()
        
        # Build planned workouts list with dates
        planned_workouts = []
        for week in plan_data.get('weeks', []):
            week_start_str = week.get('start_date')
            if isinstance(week_start_str, str):
                week_start = datetime.fromisoformat(week_start_str.replace('Z', '+00:00')).date()
            else:
                week_start = start_date + timedelta(weeks=week.get('week', 1) - 1)
            
            for workout in week.get('workouts', []):
                workout_date = workout.get('date')
                if not workout_date:
                    # Calculate from day number (1-7, Monday-Sunday)
                    day_num = workout.get('day', 1)
                    workout_date = week_start + timedelta(days=(day_num - 1) % 7)
                
                if isinstance(workout_date, str):
                    workout_date = datetime.fromisoformat(workout_date.replace('Z', '+00:00')).date()
                elif isinstance(workout_date, datetime):
                    workout_date = workout_date.date()
                
                planned_workouts.append({
                    'workout': workout,
                    'date': workout_date,
                    'week': week.get('week', 0),
                })
        
        # Match each planned workout with actual workouts
        for planned_item in planned_workouts:
            planned_workout = planned_item['workout']
            planned_date = planned_item['date']
            
            if planned_workout.get('completed', False):
                # Already marked as completed
                matches.append({
                    'planned_workout': planned_workout,
                    'planned_date': planned_date.isoformat(),
                    'week': planned_item['week'],
                    'matched': False,
                    'already_completed': True,
                })
                continue
            
            # Find best matching actual workout
            best_match = None
            best_confidence = 0.0
            
            for actual_workout in actual_workouts:
                if actual_workout.id in matched_workout_ids:
                    continue  # Already matched
                
                # Create planned workout dict with date for matching
                planned_with_date = {**planned_workout, 'date': planned_date.isoformat()}
                
                matches_flag, confidence = self.match_workout(
                    planned_with_date,
                    actual_workout
                )
                
                if matches_flag and confidence > best_confidence:
                    best_match = actual_workout
                    best_confidence = confidence
            
            if best_match and best_confidence > 0.5:  # Minimum confidence threshold
                matched_workout_ids.add(best_match.id)
                matches.append({
                    'planned_workout': planned_workout,
                    'planned_date': planned_date.isoformat(),
                    'week': planned_item['week'],
                    'actual_workout_id': best_match.id,
                    'matched': True,
                    'confidence': round(best_confidence, 2),
                    'actual_data': {
                        'distance_km': round(best_match.distance_meters / 1000, 2),
                        'pace_min_per_km': round(best_match.avg_pace / 60, 2) if best_match.avg_pace else None,
                        'duration_minutes': round(best_match.duration_seconds / 60, 0),
                        'avg_heart_rate': best_match.avg_heart_rate,
                        'date': best_match.start_time.date().isoformat(),
                    },
                })
            else:
                matches.append({
                    'planned_workout': planned_workout,
                    'planned_date': planned_date.isoformat(),
                    'week': planned_item['week'],
                    'matched': False,
                    'confidence': round(best_confidence, 2) if best_match else 0.0,
                })
        
        return matches
    
    def sync_workouts(
        self,
        plan_data: Dict[str, Any],
        user_id: int,
        db: Session,
        start_date: date,
        auto_complete: bool = True
    ) -> Dict[str, Any]:
        """
        Synchronize plan workouts with actual workouts and optionally mark as completed.
        
        Args:
            plan_data: Plan data dict (will be modified)
            user_id: User ID
            db: Database session
            start_date: Plan start date
            auto_complete: Whether to automatically mark workouts as completed
            
        Returns:
            Dict with sync results
        """
        matches = self.match_all_workouts(plan_data, user_id, db, start_date)
        
        completed_count = 0
        updated_count = 0
        
        # Update plan_data with matches
        for match in matches:
            if not match['matched']:
                continue
            
            planned_workout = match['planned_workout']
            week_num = match['week']
            
            # Find and update workout in plan_data
            for week in plan_data.get('weeks', []):
                if week.get('week') != week_num:
                    continue
                
                for workout in week.get('workouts', []):
                    # Match by day and type (basic matching)
                    if (workout.get('day') == planned_workout.get('day') and
                        workout.get('type') == planned_workout.get('type')):
                        
                        if auto_complete and not workout.get('completed'):
                            workout['completed'] = True
                            workout['completed_date'] = match['actual_data']['date']
                            completed_count += 1
                        
                        # Update with actual data
                        workout['actual_distance_km'] = match['actual_data']['distance_km']
                        workout['actual_pace'] = match['actual_data']['pace_min_per_km']
                        workout['actual_hr_avg'] = match['actual_data']['avg_heart_rate']
                        updated_count += 1
                        break
        
        return {
            'matches_found': len([m for m in matches if m['matched']]),
            'workouts_completed': completed_count,
            'workouts_updated': updated_count,
            'total_matches': len(matches),
            'matches': matches[:10],  # Return first 10 for response size
        }


# Singleton instance
_matching_service_instance: Optional[TrainingPlanMatchingService] = None

def get_matching_service() -> TrainingPlanMatchingService:
    """Get or create the matching service singleton."""
    global _matching_service_instance
    if _matching_service_instance is None:
        _matching_service_instance = TrainingPlanMatchingService()
    return _matching_service_instance
