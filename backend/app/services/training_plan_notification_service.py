"""
Training Plan Notification Service
Handles notifications and reminders for training plans.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, date, time
from sqlalchemy.orm import Session
import logging

from .. import models

logger = logging.getLogger(__name__)


class TrainingPlanNotificationService:
    """Service for training plan notifications and reminders."""
    
    def get_upcoming_workouts(
        self,
        plan_data: Dict[str, Any],
        start_date: date,
        days_ahead: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Get upcoming workouts in the next N days.
        
        Args:
            plan_data: Plan data dictionary
            start_date: Plan start date
            days_ahead: Number of days to look ahead
            
        Returns:
            List of upcoming workouts with dates
        """
        upcoming = []
        today = date.today()
        end_date = today + timedelta(days=days_ahead)
        
        for week in plan_data.get('weeks', []):
            week_num = week.get('week', 1)
            week_start = start_date + timedelta(weeks=week_num - 1)
            
            # Skip past weeks
            if week_start + timedelta(days=6) < today:
                continue
            
            for workout in week.get('workouts', []):
                if workout.get('completed'):
                    continue
                
                day_num = workout.get('day', 1)
                workout_date = week_start + timedelta(days=(day_num - 1) % 7)
                
                # Only include future workouts within range
                if today <= workout_date <= end_date:
                    upcoming.append({
                        'date': workout_date.isoformat(),
                        'week': week_num,
                        'day': day_num,
                        'workout': workout,
                        'days_until': (workout_date - today).days,
                    })
        
        # Sort by date
        upcoming.sort(key=lambda x: x['date'])
        return upcoming
    
    def get_reminders(
        self,
        plan_data: Dict[str, Any],
        start_date: date,
        reminder_days: List[int] = [1, 0]  # 1 day before, day of
    ) -> List[Dict[str, Any]]:
        """
        Get reminders for upcoming workouts.
        
        Args:
            plan_data: Plan data dictionary
            start_date: Plan start date
            reminder_days: Days before workout to send reminder (e.g., [1, 0] = 1 day before and day of)
            
        Returns:
            List of reminder dicts
        """
        reminders = []
        today = date.today()
        
        for week in plan_data.get('weeks', []):
            week_num = week.get('week', 1)
            week_start = start_date + timedelta(weeks=week_num - 1)
            
            for workout in week.get('workouts', []):
                if workout.get('completed'):
                    continue
                
                day_num = workout.get('day', 1)
                workout_date = week_start + timedelta(days=(day_num - 1) % 7)
                
                # Skip past workouts
                if workout_date < today:
                    continue
                
                # Check if reminder should be sent today
                days_until = (workout_date - today).days
                if days_until in reminder_days:
                    reminders.append({
                        'workout_date': workout_date.isoformat(),
                        'days_until': days_until,
                        'week': week_num,
                        'workout': workout,
                        'message': self._generate_reminder_message(workout, days_until),
                    })
        
        return reminders
    
    def _generate_reminder_message(
        self,
        workout: Dict[str, Any],
        days_until: int
    ) -> str:
        """Generate reminder message for a workout."""
        workout_name = workout.get('name', workout.get('type', 'Entrenamiento'))
        
        if days_until == 0:
            return f"¡Hoy tienes {workout_name} programado!"
        elif days_until == 1:
            return f"Mañana tienes {workout_name} programado"
        else:
            return f"En {days_until} días tienes {workout_name} programado"
    
    def check_missed_workouts(
        self,
        plan_data: Dict[str, Any],
        start_date: date,
        current_week: int
    ) -> List[Dict[str, Any]]:
        """
        Check for missed workouts in the past.
        
        Args:
            plan_data: Plan data dictionary
            start_date: Plan start date
            current_week: Current week number
            
        Returns:
            List of missed workouts
        """
        missed = []
        today = date.today()
        
        for week in plan_data.get('weeks', []):
            week_num = week.get('week', 1)
            
            # Only check weeks up to current week
            if week_num > current_week:
                break
            
            week_start = start_date + timedelta(weeks=week_num - 1)
            
            for workout in week.get('workouts', []):
                if workout.get('completed'):
                    continue
                
                day_num = workout.get('day', 1)
                workout_date = week_start + timedelta(days=(day_num - 1) % 7)
                
                # Check if workout was missed (past and not completed)
                if workout_date < today:
                    missed.append({
                        'date': workout_date.isoformat(),
                        'week': week_num,
                        'workout': workout,
                        'days_missed': (today - workout_date).days,
                    })
        
        return missed
    
    def generate_notification_summary(
        self,
        plan_data: Dict[str, Any],
        start_date: date,
        current_week: int
    ) -> Dict[str, Any]:
        """
        Generate a summary of notifications (upcoming, reminders, missed).
        
        Args:
            plan_data: Plan data dictionary
            start_date: Plan start date
            current_week: Current week number
            
        Returns:
            Notification summary dict
        """
        upcoming = self.get_upcoming_workouts(plan_data, start_date, days_ahead=7)
        reminders = self.get_reminders(plan_data, start_date)
        missed = self.check_missed_workouts(plan_data, start_date, current_week)
        
        return {
            'upcoming_workouts': upcoming,
            'reminders': reminders,
            'missed_workouts': missed,
            'summary': {
                'upcoming_count': len(upcoming),
                'reminders_count': len(reminders),
                'missed_count': len(missed),
                'next_workout_date': upcoming[0]['date'] if upcoming else None,
            }
        }


# Singleton instance
_notification_service_instance: Optional[TrainingPlanNotificationService] = None

def get_notification_service() -> TrainingPlanNotificationService:
    """Get or create the notification service singleton."""
    global _notification_service_instance
    if _notification_service_instance is None:
        _notification_service_instance = TrainingPlanNotificationService()
    return _notification_service_instance
