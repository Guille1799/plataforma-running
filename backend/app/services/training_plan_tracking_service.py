"""
Training Plan Tracking Service
Calculates adherence, progress, deviations, and metrics for training plans.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session
import logging

from .. import models

logger = logging.getLogger(__name__)


class TrainingPlanTrackingService:
    """Service for tracking training plan progress and adherence."""
    
    def calculate_adherence(
        self,
        plan: models.TrainingPlan,
        db: Session
    ) -> Dict[str, Any]:
        """
        Calculate adherence to the training plan.
        
        Args:
            plan: TrainingPlan model
            db: Database session
            
        Returns:
            Dict with adherence metrics
        """
        plan_data = plan.plan_data
        
        # Count total planned workouts
        total_planned = 0
        completed_planned = 0
        weeks_completed = 0
        
        for week in plan_data.get('weeks', []):
            week_num = week.get('week', 0)
            workouts = week.get('workouts', [])
            
            if week_num <= plan.current_week:
                weeks_completed += 1
                
            for workout in workouts:
                total_planned += 1
                if workout.get('completed', False):
                    completed_planned += 1
        
        adherence_percentage = (completed_planned / total_planned * 100) if total_planned > 0 else 0
        
        return {
            'total_workouts': total_planned,
            'completed_workouts': completed_planned,
            'adherence_percentage': round(adherence_percentage, 1),
            'weeks_completed': weeks_completed,
            'weeks_total': plan.total_weeks,
        }
    
    def calculate_progress(
        self,
        plan: models.TrainingPlan,
        db: Session
    ) -> Dict[str, Any]:
        """
        Calculate progress metrics (planned vs actual).
        
        Args:
            plan: TrainingPlan model
            db: Database session
            
        Returns:
            Dict with progress metrics
        """
        plan_data = plan.plan_data
        
        # Get workouts since plan start
        plan_start = plan.start_date.date() if isinstance(plan.start_date, datetime) else plan.start_date
        actual_workouts = db.query(models.Workout).filter(
            models.Workout.user_id == plan.user_id,
            models.Workout.start_time >= datetime.combine(plan_start, datetime.min.time())
        ).all()
        
        # Calculate planned metrics
        planned_distance = 0
        planned_duration = 0
        planned_workouts_count = 0
        
        for week in plan_data.get('weeks', []):
            if week.get('week', 0) <= plan.current_week:
                for workout in week.get('workouts', []):
                    if workout.get('distance_km'):
                        planned_distance += workout['distance_km']
                    if workout.get('duration_minutes'):
                        planned_duration += workout['duration_minutes']
                    planned_workouts_count += 1
        
        # Calculate actual metrics
        actual_distance = sum(w.distance_meters / 1000 for w in actual_workouts)
        actual_duration = sum(w.duration_seconds / 60 for w in actual_workouts)
        actual_workouts_count = len(actual_workouts)
        
        # Weekly breakdown
        weekly_breakdown = []
        for week in plan_data.get('weeks', []):
            week_num = week.get('week', 0)
            week_start = plan_start + timedelta(weeks=week_num - 1)
            week_end = week_start + timedelta(days=6)
            
            week_planned_km = week.get('total_km', 0)
            week_actual_workouts = [
                w for w in actual_workouts
                if week_start <= w.start_time.date() <= week_end
            ]
            week_actual_km = sum(w.distance_meters / 1000 for w in week_actual_workouts)
            
            weekly_breakdown.append({
                'week': week_num,
                'planned_km': round(week_planned_km, 1),
                'actual_km': round(week_actual_km, 1),
                'workouts_planned': len(week.get('workouts', [])),
                'workouts_actual': len(week_actual_workouts),
                'deviation_percentage': round(
                    ((week_actual_km - week_planned_km) / week_planned_km * 100) if week_planned_km > 0 else 0,
                    1
                ),
            })
        
        return {
            'planned': {
                'distance_km': round(planned_distance, 1),
                'duration_minutes': round(planned_duration, 0),
                'workouts_count': planned_workouts_count,
            },
            'actual': {
                'distance_km': round(actual_distance, 1),
                'duration_minutes': round(actual_duration, 0),
                'workouts_count': actual_workouts_count,
            },
            'deviation': {
                'distance_km': round(actual_distance - planned_distance, 1),
                'distance_percentage': round(
                    ((actual_distance - planned_distance) / planned_distance * 100) if planned_distance > 0 else 0,
                    1
                ),
                'duration_minutes': round(actual_duration - planned_duration, 0),
                'workouts_count': actual_workouts_count - planned_workouts_count,
            },
            'weekly_breakdown': weekly_breakdown,
        }
    
    def detect_deviations(
        self,
        plan: models.TrainingPlan,
        db: Session,
        threshold_percentage: float = 20.0
    ) -> List[Dict[str, Any]]:
        """
        Detect significant deviations from the plan.
        
        Args:
            plan: TrainingPlan model
            db: Database session
            threshold_percentage: Percentage threshold for deviation (default 20%)
            
        Returns:
            List of deviation dicts
        """
        progress = self.calculate_progress(plan, db)
        deviations = []
        
        # Check overall volume deviation
        if abs(progress['deviation']['distance_percentage']) > threshold_percentage:
            deviations.append({
                'type': 'volume',
                'severity': 'high' if abs(progress['deviation']['distance_percentage']) > 40 else 'medium',
                'message': f"Volumen {'por encima' if progress['deviation']['distance_percentage'] > 0 else 'por debajo'} del plan en {abs(progress['deviation']['distance_percentage']):.1f}%",
                'recommendation': 'Considera adaptar el plan' if abs(progress['deviation']['distance_percentage']) > 30 else 'Monitorea el progreso',
            })
        
        # Check weekly deviations
        for week_data in progress['weekly_breakdown']:
            if abs(week_data['deviation_percentage']) > threshold_percentage:
                deviations.append({
                    'type': 'weekly_volume',
                    'week': week_data['week'],
                    'severity': 'medium',
                    'message': f"Semana {week_data['week']}: {'+ Excessive' if week_data['deviation_percentage'] > 0 else '- Insufficient'} volume ({week_data['deviation_percentage']:+.1f}%)",
                    'recommendation': 'Ajustar volumen de la semana',
                })
        
        # Check adherence
        adherence = self.calculate_adherence(plan, db)
        if adherence['adherence_percentage'] < 70:
            deviations.append({
                'type': 'adherence',
                'severity': 'high',
                'message': f"Baja adherencia: {adherence['adherence_percentage']:.1f}% de entrenamientos completados",
                'recommendation': 'Considera reducir el volumen o intensidad del plan',
            })
        
        return deviations
    
    def calculate_metrics(
        self,
        plan: models.TrainingPlan,
        db: Session
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive metrics for the plan.
        
        Args:
            plan: TrainingPlan model
            db: Database session
            
        Returns:
            Dict with all metrics
        """
        adherence = self.calculate_adherence(plan, db)
        progress = self.calculate_progress(plan, db)
        deviations = self.detect_deviations(plan, db)
        
        # Calculate current week progress
        current_week_data = next(
            (w for w in plan.plan_data.get('weeks', []) if w.get('week') == plan.current_week),
            None
        )
        
        current_week_km = current_week_data.get('total_km', 0) if current_week_data else 0
        plan_start = plan.start_date.date() if isinstance(plan.start_date, datetime) else plan.start_date
        week_start = plan_start + timedelta(weeks=plan.current_week - 1)
        week_end = week_start + timedelta(days=6)
        
        current_week_workouts = db.query(models.Workout).filter(
            models.Workout.user_id == plan.user_id,
            models.Workout.start_time >= datetime.combine(week_start, datetime.min.time()),
            models.Workout.start_time <= datetime.combine(week_end, datetime.max.time())
        ).all()
        
        current_week_actual_km = sum(w.distance_meters / 1000 for w in current_week_workouts)
        
        return {
            'adherence': adherence,
            'progress': progress,
            'deviations': deviations,
            'current_week': {
                'week_number': plan.current_week,
                'planned_km': round(current_week_km, 1),
                'actual_km': round(current_week_actual_km, 1),
                'workouts_planned': len(current_week_data.get('workouts', [])) if current_week_data else 0,
                'workouts_actual': len(current_week_workouts),
                'completion_percentage': round(
                    (current_week_actual_km / current_week_km * 100) if current_week_km > 0 else 0,
                    1
                ),
            },
            'overall': {
                'progress_percentage': round((plan.current_week / plan.total_weeks * 100), 1),
                'weeks_remaining': plan.total_weeks - plan.current_week,
                'on_track': adherence['adherence_percentage'] >= 70 and len(deviations) < 3,
            },
        }


# Singleton instance
_tracking_service_instance: Optional[TrainingPlanTrackingService] = None

def get_tracking_service() -> TrainingPlanTrackingService:
    """Get or create the tracking service singleton."""
    global _tracking_service_instance
    if _tracking_service_instance is None:
        _tracking_service_instance = TrainingPlanTrackingService()
    return _tracking_service_instance
