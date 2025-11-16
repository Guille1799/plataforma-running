"""
Race Time Predictor
Predicts race times based on recent training and race results
Uses Riegel formula, Jack Daniels VDOT, and AI analysis
"""
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import math

from .. import models


class RacePredictorService:
    """Service for predicting race times."""
    
    # Standard race distances in meters
    RACE_DISTANCES = {
        "5K": 5000,
        "10K": 10000,
        "15K": 15000,
        "Half Marathon": 21097.5,
        "Marathon": 42195
    }
    
    # Riegel formula exponent (1.06 is standard)
    FATIGUE_FACTOR = 1.06
    
    def predict_race_times(
        self,
        db: Session,
        user_id: int,
        base_race: Optional[Tuple[float, float]] = None  # (distance_km, time_minutes)
    ) -> Dict[str, Any]:
        """
        Predict race times for standard distances.
        
        Args:
            db: Database session
            user_id: User ID
            base_race: Optional tuple of (distance_km, time_minutes) for base calculation
            
        Returns:
            Dict with predictions for all distances
        """
        # If no base race provided, find best recent performance
        if not base_race:
            base_race = self._find_best_performance(db, user_id)
        
        if not base_race:
            raise ValueError("No training data available for predictions")
        
        base_distance_m, base_time_min = base_race
        
        # Calculate VDOT
        vdot = self._calculate_vdot(base_distance_m / 1000, base_time_min)
        
        # Predict all distances
        predictions = {}
        for race_name, distance_m in self.RACE_DISTANCES.items():
            # Riegel formula
            predicted_time = self._riegel_prediction(
                base_distance_m, base_time_min, distance_m
            )
            
            # VDOT-based prediction
            vdot_time = self._vdot_prediction(vdot, distance_m / 1000)
            
            # Average both methods
            final_time = (predicted_time + vdot_time) / 2
            
            predictions[race_name] = {
                "distance_km": distance_m / 1000,
                "predicted_time_minutes": round(final_time, 2),
                "predicted_time_formatted": self._format_time(final_time),
                "predicted_pace": self._format_pace(final_time / (distance_m / 1000)),
                "confidence": self._calculate_confidence(base_distance_m, distance_m)
            }
        
        return {
            "predictions": predictions,
            "vdot": round(vdot, 1),
            "base_performance": {
                "distance_km": base_distance_m / 1000,
                "time_minutes": base_time_min,
                "time_formatted": self._format_time(base_time_min),
                "pace": self._format_pace(base_time_min / (base_distance_m / 1000))
            },
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def _find_best_performance(
        self,
        db: Session,
        user_id: int
    ) -> Optional[Tuple[float, float]]:
        """
        Find best recent performance for predictions.
        
        Returns:
            Tuple of (distance_meters, time_minutes) or None
        """
        # Look for workouts in last 3 months
        three_months_ago = datetime.utcnow() - timedelta(days=90)
        
        workouts = db.query(models.Workout).filter(
            models.Workout.user_id == user_id,
            models.Workout.sport_type == 'running',
            models.Workout.start_time >= three_months_ago,
            models.Workout.distance_meters >= 3000,  # At least 3km
            models.Workout.avg_pace.isnot(None)
        ).order_by(models.Workout.start_time.desc()).limit(50).all()
        
        if not workouts:
            return None
        
        # Find best pace workout > 5km
        best_workout = None
        best_speed = 0
        
        for workout in workouts:
            if workout.distance_meters < 5000:
                continue
            
            # Calculate average speed (m/s)
            if workout.duration_seconds > 0:
                speed = workout.distance_meters / workout.duration_seconds
                
                if speed > best_speed:
                    best_speed = speed
                    best_workout = workout
        
        if best_workout:
            return (
                best_workout.distance_meters,
                best_workout.duration_seconds / 60
            )
        
        # Fallback: use most recent long run
        longest = max(workouts, key=lambda w: w.distance_meters)
        return (longest.distance_meters, longest.duration_seconds / 60)
    
    def _riegel_prediction(
        self,
        base_distance_m: float,
        base_time_min: float,
        target_distance_m: float
    ) -> float:
        """
        Riegel formula: T2 = T1 * (D2/D1)^1.06
        
        Returns:
            Predicted time in minutes
        """
        distance_ratio = target_distance_m / base_distance_m
        return base_time_min * (distance_ratio ** self.FATIGUE_FACTOR)
    
    def _calculate_vdot(self, distance_km: float, time_minutes: float) -> float:
        """
        Calculate Jack Daniels VDOT (VO2max estimation).
        
        Simplified formula based on race performance.
        """
        velocity_m_min = (distance_km * 1000) / time_minutes
        
        # Oxygen cost estimation
        percent_vo2max = 0.8 + 0.1894393 * math.exp(-0.012778 * time_minutes) + \
                         0.2989558 * math.exp(-0.1932605 * time_minutes)
        
        # VO2 calculation
        vo2 = -4.60 + 0.182258 * velocity_m_min + 0.000104 * velocity_m_min ** 2
        
        # VDOT
        vdot = vo2 / percent_vo2max
        
        return max(30, min(85, vdot))  # Clamp to reasonable range
    
    def _vdot_prediction(self, vdot: float, distance_km: float) -> float:
        """
        Predict race time from VDOT for given distance.
        
        Returns:
            Time in minutes
        """
        # Training velocity at race pace
        velocity_m_min = 29.54 + 5.000663 * vdot - 0.007546 * vdot ** 2
        
        # Adjust for distance (shorter = faster relative pace)
        if distance_km <= 5:
            velocity_m_min *= 1.03
        elif distance_km >= 21:
            velocity_m_min *= 0.98
        
        time_minutes = (distance_km * 1000) / velocity_m_min
        return time_minutes
    
    def _calculate_confidence(
        self,
        base_distance_m: float,
        target_distance_m: float
    ) -> str:
        """
        Calculate confidence level based on distance extrapolation.
        
        Returns:
            "high", "medium", or "low"
        """
        ratio = target_distance_m / base_distance_m
        
        if 0.8 <= ratio <= 1.5:
            return "high"
        elif 0.5 <= ratio <= 3:
            return "medium"
        else:
            return "low"
    
    def _format_time(self, minutes: float) -> str:
        """Format minutes to HH:MM:SS."""
        hours = int(minutes // 60)
        mins = int(minutes % 60)
        secs = int((minutes % 1) * 60)
        
        if hours > 0:
            return f"{hours}:{mins:02d}:{secs:02d}"
        else:
            return f"{mins}:{secs:02d}"
    
    def _format_pace(self, pace_min_km: float) -> str:
        """Format pace to MM:SS/km."""
        mins = int(pace_min_km)
        secs = int((pace_min_km % 1) * 60)
        return f"{mins}:{secs:02d}/km"
    
    def get_training_paces(
        self,
        vdot: float
    ) -> Dict[str, Dict[str, Any]]:
        """
        Get training pace zones based on VDOT.
        
        Args:
            vdot: Calculated VDOT value
            
        Returns:
            Dict with pace zones for different training types
        """
        # Base velocity
        base_velocity = 29.54 + 5.000663 * vdot - 0.007546 * vdot ** 2  # m/min
        
        zones = {
            "Easy": {
                "percent_effort": "60-70%",
                "pace_min_km": 1000 / (base_velocity * 0.65),
                "purpose": "Recuperación, rodajes suaves"
            },
            "Marathon": {
                "percent_effort": "75-80%",
                "pace_min_km": 1000 / (base_velocity * 0.78),
                "purpose": "Ritmo de maratón, rodajes largos"
            },
            "Threshold": {
                "percent_effort": "85-90%",
                "pace_min_km": 1000 / (base_velocity * 0.88),
                "purpose": "Tempo runs, umbral anaeróbico"
            },
            "Interval": {
                "percent_effort": "95-100%",
                "pace_min_km": 1000 / (base_velocity * 0.98),
                "purpose": "Series, VO2max"
            },
            "Repetition": {
                "percent_effort": "105-110%",
                "pace_min_km": 1000 / (base_velocity * 1.08),
                "purpose": "Repeticiones cortas, velocidad"
            }
        }
        
        # Format paces
        for zone_name, zone_data in zones.items():
            pace = zone_data['pace_min_km']
            zone_data['pace_formatted'] = self._format_pace(pace)
        
        return zones


# Singleton
race_predictor_service = RacePredictorService()
