"""
Adaptive Coaching Service

Dynamically adjusts training plans based on user performance and health metrics.
Uses AI to make intelligent modifications to workouts based on:
- Recovery readiness score
- Sleep quality
- Recent performance (pace, HR)
- Fatigue level
- Injury considerations
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json

class AdaptiveCoachingService:
    """Service for adaptive workout adjustments."""
    
    # Adjustment thresholds
    LOW_READINESS_THRESHOLD = 0.4  # 40% readiness
    POOR_SLEEP_THRESHOLD = 5  # hours
    HIGH_FATIGUE_THRESHOLD = 0.7  # 70% fatigue
    
    # Adjustment multipliers
    INTENSITY_REDUCTION_LOW_READINESS = 0.8  # Reduce by 20%
    INTENSITY_REDUCTION_POOR_SLEEP = 0.75  # Reduce by 25%
    INTENSITY_REDUCTION_HIGH_FATIGUE = 0.7  # Reduce by 30%
    
    def __init__(self, groq_client=None):
        """Initialize with optional Groq client for AI suggestions."""
        self.groq_client = groq_client
    
    def get_adjusted_workout(
        self,
        workout: Dict[str, Any],
        user_health_metrics: Optional[Dict[str, Any]] = None,
        recent_workouts: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Get an adjusted version of a workout based on health and performance data.
        
        Args:
            workout: Original workout from plan
            user_health_metrics: Current health metrics (readiness, sleep, fatigue, etc.)
            recent_workouts: Last 3-7 workouts for trend analysis
            
        Returns:
            Adjusted workout with modified intensity/volume
        """
        if not user_health_metrics:
            return workout  # Return original if no metrics
        
        adjusted = workout.copy()
        adjustments = []
        
        # Calculate adjustment factor based on health metrics
        adjustment_factor = self._calculate_adjustment_factor(user_health_metrics)
        
        if adjustment_factor < 1.0:
            # Need to adjust workout down
            adjustments.append(
                self._adjust_workout_intensity(adjusted, adjustment_factor)
            )
        
        # Check for specific conditions
        readiness_score = user_health_metrics.get("readiness_score")
        if readiness_score and readiness_score < self.LOW_READINESS_THRESHOLD:
            adjustments.append(
                self._handle_low_readiness(adjusted, readiness_score)
            )
        
        sleep_hours = user_health_metrics.get("sleep_hours")
        if sleep_hours and sleep_hours < self.POOR_SLEEP_THRESHOLD:
            adjustments.append(
                self._handle_poor_sleep(adjusted, sleep_hours)
            )
        
        fatigue_level = user_health_metrics.get("fatigue_level", 0)
        if fatigue_level > self.HIGH_FATIGUE_THRESHOLD:
            adjustments.append(
                self._handle_high_fatigue(adjusted, fatigue_level)
            )
        
        # Add adjustment notes
        if adjustments:
            adjusted["adjustment_notes"] = " | ".join(adjustments)
            adjusted["is_adapted"] = True
        else:
            adjusted["is_adapted"] = False
        
        return adjusted
    
    def _calculate_adjustment_factor(self, health_metrics: Dict[str, Any]) -> float:
        """
        Calculate overall adjustment factor (0.0-1.0) based on all metrics.
        1.0 = no adjustment needed
        0.7 = reduce by 30%
        """
        factors = []
        
        # Readiness score (0-1)
        readiness = health_metrics.get("readiness_score", 0.5)
        if readiness < self.LOW_READINESS_THRESHOLD:
            factors.append(self.INTENSITY_REDUCTION_LOW_READINESS)
        else:
            # Scale: low readiness affects more
            factors.append(0.9 + (readiness * 0.1))
        
        # Sleep (hours)
        sleep = health_metrics.get("sleep_hours", 7)
        if sleep < self.POOR_SLEEP_THRESHOLD:
            factors.append(self.INTENSITY_REDUCTION_POOR_SLEEP)
        else:
            # Optimal sleep is 7-9 hours
            if sleep > 9:
                factors.append(0.95)  # Slight reduction for over-sleep
            else:
                factors.append(1.0)
        
        # Fatigue (0-1)
        fatigue = health_metrics.get("fatigue_level", 0)
        if fatigue > self.HIGH_FATIGUE_THRESHOLD:
            factors.append(self.INTENSITY_REDUCTION_HIGH_FATIGUE)
        else:
            # Scale: more fatigue = more reduction
            factors.append(1.0 - (fatigue * 0.3))
        
        # Heart rate variance (if available - HRV)
        hrv = health_metrics.get("heart_rate_variability")
        if hrv:
            # Lower HRV = more stressed = reduce intensity
            if hrv < 20:  # Low HRV threshold
                factors.append(0.85)
            else:
                factors.append(1.0)
        
        # Return minimum factor (most restrictive)
        return min(factors) if factors else 1.0
    
    def _adjust_workout_intensity(self, workout: Dict[str, Any], factor: float) -> str:
        """Reduce workout intensity by factor."""
        original_distance = workout.get("distance_km", 0)
        new_distance = original_distance * factor
        
        # Round to nearest 0.5 km
        new_distance = round(new_distance * 2) / 2
        
        workout["distance_km"] = new_distance
        
        # Adjust pace (make it easier - slower)
        original_pace = workout.get("pace_target", "")
        if original_pace:
            new_pace = self._adjust_pace(original_pace, factor)
            workout["pace_target"] = new_pace
            return f"Reducida intensidad: {original_distance}km → {new_distance}km"
        
        return f"Volumen reducido a {new_distance}km"
    
    def _adjust_pace(self, pace_str: str, factor: float) -> str:
        """
        Adjust pace string for reduced intensity.
        Slower pace = higher numbers (e.g., 6:00 is slower than 5:00)
        """
        try:
            # Parse "5:30-6:00 min/km" format
            parts = pace_str.split("-")
            if len(parts) < 2:
                return pace_str
            
            # Extract first pace (min:sec)
            start_pace = parts[0].strip()
            minutes, seconds = map(int, start_pace.split(":"))
            pace_seconds = minutes * 60 + seconds
            
            # Make it slower (increase time per km)
            new_pace_seconds = pace_seconds / factor  # Divide by factor < 1 makes it slower
            new_minutes = int(new_pace_seconds // 60)
            new_seconds = int(new_pace_seconds % 60)
            
            # Extract end pace if exists
            if len(parts) > 1:
                end_pace = parts[1].split()[0]
                return f"{new_minutes}:{new_seconds:02d}-{end_pace} min/km"
            else:
                return f"{new_minutes}:{new_seconds:02d} min/km"
        except:
            return pace_str
    
    def _handle_low_readiness(self, workout: Dict[str, Any], score: float) -> str:
        """Handle low readiness score."""
        if score < 0.2:
            # Very low readiness - convert to recovery run
            workout["type"] = "recovery_run"
            workout["name"] = "Recovery Run (Low Readiness)"
            workout["distance_km"] = max(3, workout.get("distance_km", 5) * 0.5)
            workout["pace_target"] = "6:30-7:00 min/km"
            return "Readiness muy baja: convertido a easy recovery run"
        else:
            # Moderate low readiness - just reduce
            return "Readiness baja: intensidad reducida"
    
    def _handle_poor_sleep(self, workout: Dict[str, Any], sleep_hours: float) -> str:
        """Handle poor sleep."""
        reduction = max(0.5, sleep_hours / 7.0)  # Scale reduction based on sleep
        workout["distance_km"] = workout.get("distance_km", 5) * reduction
        return f"Sueño insuficiente ({sleep_hours}h): volumen reducido"
    
    def _handle_high_fatigue(self, workout: Dict[str, Any], fatigue_level: float) -> str:
        """Handle high fatigue level."""
        if fatigue_level > 0.85:
            # Very high fatigue - rest day
            workout["type"] = "rest_day"
            workout["name"] = "Día de descanso (Fatiga alta)"
            workout["distance_km"] = 0
            return "Fatiga crítica: convertido a día de descanso"
        else:
            # Moderate fatigue - easy day
            reduction = 1.0 - (fatigue_level * 0.3)
            workout["distance_km"] = workout.get("distance_km", 5) * reduction
            return f"Fatiga moderada: intensidad reducida {fatigue_level:.0%}"
    
    def should_skip_workout(self, health_metrics: Dict[str, Any]) -> bool:
        """
        Determine if workout should be skipped entirely.
        Returns True if user should rest instead.
        """
        # Skip if critical conditions
        readiness = health_metrics.get("readiness_score", 0.5)
        fatigue = health_metrics.get("fatigue_level", 0)
        sleep = health_metrics.get("sleep_hours", 7)
        
        # Too many critical conditions
        critical_count = 0
        if readiness < 0.15:
            critical_count += 1
        if fatigue > 0.9:
            critical_count += 1
        if sleep < 4:
            critical_count += 1
        
        return critical_count >= 2
    
    def get_recovery_recommendation(self, health_metrics: Dict[str, Any]) -> Dict[str, str]:
        """
        Get recovery and adaptation recommendations.
        """
        recommendations = {
            "primary": "Normal training",
            "secondary": [],
            "actions": []
        }
        
        readiness = health_metrics.get("readiness_score", 0.5)
        sleep = health_metrics.get("sleep_hours", 7)
        fatigue = health_metrics.get("fatigue_level", 0)
        
        if readiness < 0.3 or fatigue > 0.8:
            recommendations["primary"] = "Rest or easy recovery"
            recommendations["secondary"].append("Prioriza el sueño y la recuperación")
            recommendations["actions"].append("Reduce intensity significantly")
        elif readiness < 0.5:
            recommendations["primary"] = "Easy day recommended"
            recommendations["secondary"].append("Aumenta hidratación y nutrición")
            recommendations["actions"].append("Stay in Zone 2 (conversational pace)")
        
        if sleep < 6:
            recommendations["secondary"].append(f"Dormir más (actual: {sleep}h)")
            recommendations["actions"].append("Consider postponing hard workout")
        
        if sleep > 9:
            recommendations["secondary"].append("Over-sleeping detected")
            recommendations["actions"].append("Could indicate fatigue or illness")
        
        # Positive recommendations
        if readiness > 0.8 and fatigue < 0.3:
            recommendations["primary"] = "Go for it! Feeling great"
            recommendations["secondary"].append("Good day for hard workout or long run")
        
        return recommendations
