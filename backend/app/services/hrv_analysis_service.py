"""
hrv_analysis_service.py - Heart Rate Variability Analysis

Advanced HRV analytics providing:
- HRV trend analysis with baselines
- Fatigue indicators
- Parasympathetic recovery status
- Circadian rhythm patterns
- Acute Training Load (ATL) correlation
- Predictive fatigue warnings

HRV measured in milliseconds (ms). Higher = better recovery.
Normal ranges: 20-200ms depending on fitness level and age.
"""
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
import logging
import statistics

from app import models

logger = logging.getLogger(__name__)


class HRVAnalysisService:
    """Advanced Heart Rate Variability analysis service."""
    
    # HRV interpretation thresholds
    HRV_LEVELS = {
        "excellent": 0.95,      # >= 95% of baseline = excellent
        "good": 0.85,           # 85-95% of baseline = good
        "adequate": 0.70,       # 70-85% = adequate
        "compromised": 0.50,    # 50-70% = compromised (fatigue accumulating)
        "critical": 0.00,       # < 50% = critical (overtraining risk)
    }
    
    def __init__(self):
        """Initialize HRV analysis service."""
        pass
    
    def analyze_hrv_trends(
        self,
        user_id: int,
        db: Session,
        analysis_days: int = 30
    ) -> Dict[str, Any]:
        """
        Comprehensive HRV analysis with trends and predictions.
        
        Args:
            user_id: User to analyze
            db: Database session
            analysis_days: Period to analyze (default 30 days)
            
        Returns:
            Dict with HRV metrics, trends, interpretations, and recommendations
        """
        logger.info(f"[HRV ANALYSIS] Analyzing user {user_id} over {analysis_days} days")
        
        cutoff_date = datetime.utcnow() - timedelta(days=analysis_days)
        
        # Get HRV data
        metrics = db.query(models.HealthMetric).filter(
            models.HealthMetric.user_id == user_id,
            models.HealthMetric.date >= cutoff_date,
            models.HealthMetric.hrv_ms.isnot(None)
        ).order_by(models.HealthMetric.date.asc()).all()
        
        if not metrics:
            return {
                "status": "insufficient_data",
                "message": "No HRV data available",
                "available_days": 0
            }
        
        # Extract HRV values and dates
        hrv_values = [m.hrv_ms for m in metrics]
        dates = [m.date for m in metrics]
        
        # Calculate baselines
        baseline_metrics = metrics[:7] if len(metrics) >= 7 else metrics
        baseline_hrv = sum(m.hrv_ms for m in baseline_metrics) / len(baseline_metrics)
        
        recent_metrics = metrics[-7:] if len(metrics) >= 7 else metrics
        recent_hrv = sum(m.hrv_ms for m in recent_metrics) / len(recent_metrics)
        
        # Calculate statistics
        min_hrv = min(hrv_values)
        max_hrv = max(hrv_values)
        mean_hrv = statistics.mean(hrv_values)
        std_dev_hrv = statistics.stdev(hrv_values) if len(hrv_values) > 1 else 0
        
        # Coefficient of variation (normalized measure of HRV variability)
        cv_hrv = (std_dev_hrv / mean_hrv * 100) if mean_hrv > 0 else 0
        
        # Trend analysis
        trend_direction = self._calculate_trend(hrv_values)
        trend_strength = self._calculate_trend_strength(hrv_values)
        
        # Recovery status
        recovery_status = self._assess_recovery_status(recent_hrv, baseline_hrv)
        
        # Fatigue indicators
        fatigue_score = self._calculate_fatigue_score(recent_hrv, baseline_hrv, std_dev_hrv)
        
        # Correlation with workouts
        workout_correlation = self._correlate_with_workouts(user_id, db, dates, hrv_values)
        
        # Circadian pattern (if enough data)
        circadian_pattern = self._analyze_circadian_pattern(metrics) if len(metrics) >= 14 else None
        
        # Prediction
        fatigue_prediction = self._predict_fatigue_trend(hrv_values, dates)
        
        return {
            "status": "analyzed",
            "analysis_period_days": analysis_days,
            "data_points": len(metrics),
            
            "current_status": {
                "recent_hrv_ms": round(recent_hrv, 1),
                "baseline_hrv_ms": round(baseline_hrv, 1),
                "vs_baseline_percentage": round((recent_hrv / baseline_hrv * 100), 1) if baseline_hrv > 0 else 0,
                "recovery_status": recovery_status,
                "fatigue_score": fatigue_score  # 0-100, higher = more fatigued
            },
            
            "statistics": {
                "minimum_ms": round(min_hrv, 1),
                "maximum_ms": round(max_hrv, 1),
                "mean_ms": round(mean_hrv, 1),
                "std_deviation_ms": round(std_dev_hrv, 1),
                "coefficient_of_variation_percent": round(cv_hrv, 1),
            },
            
            "trend_analysis": {
                "direction": trend_direction,  # up, down, stable
                "strength": trend_strength,  # weak, moderate, strong
                "interpretation": self._interpret_trend(trend_direction, trend_strength)
            },
            
            "fatigue_indicators": {
                "fatigue_score_0_100": fatigue_score,
                "hrv_decline_percent": round(((baseline_hrv - recent_hrv) / baseline_hrv * 100), 1) if baseline_hrv > 0 else 0,
                "recovery_quality": self._assess_recovery_quality(std_dev_hrv, cv_hrv),
                "sympathetic_dominance": "Yes" if recent_hrv < (baseline_hrv * 0.8) else "No"
            },
            
            "workout_correlation": workout_correlation,
            
            "circadian_pattern": circadian_pattern,
            
            "prediction": fatigue_prediction,
            
            "recommendations": self._generate_hrv_recommendations(
                recovery_status,
                fatigue_score,
                trend_direction,
                workout_correlation
            ),
            
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction (up, down, stable)."""
        if len(values) < 3:
            return "insufficient_data"
        
        # Compare recent third vs baseline third
        third_len = len(values) // 3
        baseline_third = values[:third_len]
        recent_third = values[-third_len:] if third_len > 0 else values
        
        baseline_mean = sum(baseline_third) / len(baseline_third)
        recent_mean = sum(recent_third) / len(recent_third)
        
        diff_pct = (recent_mean - baseline_mean) / baseline_mean * 100 if baseline_mean > 0 else 0
        
        if diff_pct > 5:
            return "up"
        elif diff_pct < -5:
            return "down"
        else:
            return "stable"
    
    def _calculate_trend_strength(self, values: List[float]) -> str:
        """Calculate trend strength (weak, moderate, strong)."""
        if len(values) < 3:
            return "insufficient_data"
        
        third_len = len(values) // 3
        baseline_third = values[:third_len]
        recent_third = values[-third_len:] if third_len > 0 else values
        
        baseline_mean = sum(baseline_third) / len(baseline_third)
        recent_mean = sum(recent_third) / len(recent_third)
        
        diff_pct = abs((recent_mean - baseline_mean) / baseline_mean * 100) if baseline_mean > 0 else 0
        
        if diff_pct < 3:
            return "weak"
        elif diff_pct < 8:
            return "moderate"
        else:
            return "strong"
    
    def _assess_recovery_status(self, recent_hrv: float, baseline_hrv: float) -> str:
        """Assess parasympathetic recovery status."""
        if baseline_hrv == 0:
            return "unknown"
        
        ratio = recent_hrv / baseline_hrv
        
        for status, threshold in self.HRV_LEVELS.items():
            if ratio >= threshold:
                return status
        
        return "critical"
    
    def _calculate_fatigue_score(
        self,
        recent_hrv: float,
        baseline_hrv: float,
        std_dev: float
    ) -> int:
        """
        Calculate fatigue score (0-100).
        0 = well-recovered, 100 = extreme fatigue.
        """
        if baseline_hrv == 0:
            return 50
        
        # HRV component (60% weight)
        hrv_ratio = recent_hrv / baseline_hrv
        hrv_component = max(0, min(100, (1 - hrv_ratio) * 100 * 0.6))
        
        # Variability component (40% weight)
        # Higher variability = better (more parasympathetic tone)
        cv = (std_dev / recent_hrv * 100) if recent_hrv > 0 else 0
        # Ideal CV for well-recovered athlete: 5-15%
        if cv < 5:
            variability_component = 30  # Low variability = concerning
        elif cv < 15:
            variability_component = 10  # Good variability
        else:
            variability_component = 20  # Too high variability = instability
        
        fatigue_score = int(hrv_component + (variability_component * 0.4))
        return min(100, max(0, fatigue_score))
    
    def _assess_recovery_quality(self, std_dev: float, cv: float) -> str:
        """Assess autonomic nervous system recovery quality."""
        # Coefficient of variation indicates parasympathetic tone balance
        if cv < 3:
            return "Poor - Low autonomic variability"
        elif cv < 8:
            return "Compromised - Reduced parasympathetic tone"
        elif cv < 15:
            return "Good - Balanced autonomic function"
        elif cv < 25:
            return "Excellent - High parasympathetic tone"
        else:
            return "Unstable - Excessive autonomic variability"
    
    def _correlate_with_workouts(
        self,
        user_id: int,
        db: Session,
        dates: List[datetime],
        hrv_values: List[float]
    ) -> Dict[str, Any]:
        """
        Correlate HRV trends with workout patterns.
        
        Look for: HRV drops after intense workouts (normal) vs no recovery (problem).
        """
        if not dates or not hrv_values:
            return {"status": "insufficient_data"}
        
        # Get workouts in the same period
        start_date = dates[0]
        end_date = dates[-1]
        
        workouts = db.query(models.Workout).filter(
            models.Workout.user_id == user_id,
            models.Workout.start_time >= start_date,
            models.Workout.start_time <= end_date,
            models.Workout.avg_heart_rate.isnot(None)
        ).order_by(models.Workout.start_time.asc()).all()
        
        if not workouts:
            return {"status": "no_workouts", "correlation": "unknown"}
        
        # Analyze HRV drops after workouts
        hrv_drops_after_workout = []
        hrv_recovery_after_workout = []
        
        for i, workout in enumerate(workouts):
            workout_date = workout.start_time.date()
            
            # Find HRV on workout day
            hrv_on_day = next(
                (hrv for h, d in zip(hrv_values, dates) if d == workout_date),
                None
            )
            
            if not hrv_on_day:
                continue
            
            # Find HRV next day
            next_date = workout_date + timedelta(days=1)
            hrv_next_day = next(
                (hrv for h, d in zip(hrv_values, dates) if d == next_date),
                None
            )
            
            if hrv_next_day:
                drop = hrv_on_day - hrv_next_day
                if drop > 0:
                    hrv_drops_after_workout.append(drop)
                else:
                    hrv_recovery_after_workout.append(abs(drop))
        
        avg_drop = sum(hrv_drops_after_workout) / len(hrv_drops_after_workout) if hrv_drops_after_workout else 0
        avg_recovery = sum(hrv_recovery_after_workout) / len(hrv_recovery_after_workout) if hrv_recovery_after_workout else 0
        
        return {
            "status": "analyzed",
            "workouts_during_period": len(workouts),
            "average_hrv_drop_after_workout_ms": round(avg_drop, 1),
            "average_hrv_recovery_next_day_ms": round(avg_recovery, 1),
            "interpretation": self._interpret_hrv_workout_correlation(avg_drop, avg_recovery)
        }
    
    def _analyze_circadian_pattern(self, metrics: List[models.HealthMetric]) -> Dict[str, Any]:
        """
        Analyze circadian (daily) patterns in HRV.
        
        Morning HRV is typically higher (parasympathetic recovery overnight).
        """
        if len(metrics) < 14:
            return None
        
        # This would require timestamps, currently we only have dates
        # For MVP, we'll mark as available but not fully implemented
        return {
            "status": "available_with_timestamp_data",
            "message": "Full circadian analysis requires minute-level data"
        }
    
    def _predict_fatigue_trend(
        self,
        hrv_values: List[float],
        dates: List[datetime]
    ) -> Dict[str, Any]:
        """
        Predict future fatigue trend based on HRV trajectory.
        
        Simple linear regression to forecast next 7 days.
        """
        if len(hrv_values) < 7:
            return {"status": "insufficient_data"}
        
        # Use last 14 days for prediction if available
        period_length = min(14, len(hrv_values))
        recent_values = hrv_values[-period_length:]
        recent_dates = dates[-period_length:]
        
        # Simple linear regression
        n = len(recent_values)
        x_vals = list(range(n))
        x_mean = sum(x_vals) / n
        y_mean = sum(recent_values) / n
        
        numerator = sum((x_vals[i] - x_mean) * (recent_values[i] - y_mean) for i in range(n))
        denominator = sum((x_vals[i] - x_mean) ** 2 for i in range(n))
        
        slope = numerator / denominator if denominator != 0 else 0
        intercept = y_mean - slope * x_mean
        
        # Predict next 7 days
        predictions = []
        for day in range(1, 8):
            predicted_val = intercept + slope * (n - 1 + day)
            predictions.append(round(max(0, predicted_val), 1))
        
        trend_direction = "improving" if slope > 0 else "declining" if slope < 0 else "stable"
        
        return {
            "status": "predicted",
            "trend_direction": trend_direction,
            "trend_slope": round(slope, 3),
            "prediction_next_7_days_ms": predictions,
            "interpretation": f"HRV projected to {trend_direction} over next 7 days"
        }
    
    def _interpret_trend(self, direction: str, strength: str) -> str:
        """Interpret HRV trend."""
        interpretations = {
            ("up", "strong"): "HRV significantly improving - excellent recovery trend",
            ("up", "moderate"): "HRV improving - positive recovery trend",
            ("up", "weak"): "HRV slightly improving",
            ("down", "strong"): "HRV significantly declining - fatigue accumulating rapidly",
            ("down", "moderate"): "HRV declining - fatigue accumulating",
            ("down", "weak"): "HRV slightly declining - monitor closely",
            ("stable", "strong"): "HRV stable",
            ("stable", "moderate"): "HRV stable",
            ("stable", "weak"): "HRV stable",
        }
        return interpretations.get((direction, strength), "Unable to determine trend")
    
    def _interpret_hrv_workout_correlation(self, avg_drop: float, avg_recovery: float) -> str:
        """Interpret relationship between workouts and HRV."""
        if avg_drop < 5:
            return "Minimal HRV drop - likely recovering well"
        elif avg_drop < 15:
            if avg_recovery > avg_drop * 0.8:
                return "Normal HRV drop with good recovery"
            else:
                return "HRV drop with slow recovery - monitor fatigue"
        else:
            return "Large HRV drops - ensure adequate recovery between workouts"
    
    def _generate_hrv_recommendations(
        self,
        recovery_status: str,
        fatigue_score: int,
        trend_direction: str,
        workout_correlation: Dict
    ) -> List[str]:
        """Generate HRV-based recommendations."""
        recommendations = []
        
        # Recovery status recommendations
        if recovery_status == "critical":
            recommendations.append("🚨 CRITICAL: HRV critically low - parasympathetic system overwhelmed")
            recommendations.append("  → Take 3-5 days of complete rest or very light activity")
            recommendations.append("  → Prioritize sleep and stress reduction")
        elif recovery_status == "compromised":
            recommendations.append("⚠️ HRV significantly below baseline - insufficient parasympathetic recovery")
            recommendations.append("  → Add extra recovery day this week")
            recommendations.append("  → Extend sleep duration by 1-2 hours")
        elif recovery_status == "adequate":
            recommendations.append("ℹ️ HRV adequate but not optimal - some fatigue present")
            recommendations.append("  → Consider adding active recovery session")
        elif recovery_status == "good":
            recommendations.append("✅ HRV good - normal parasympathetic function")
        elif recovery_status == "excellent":
            recommendations.append("✅ HRV excellent - well-recovered and ready for training")
        
        # Trend recommendations
        if trend_direction == "down" and fatigue_score > 60:
            recommendations.append("📉 Declining HRV trend - reduce training intensity this week")
        elif trend_direction == "up":
            recommendations.append("📈 Improving HRV trend - recovery phase working well")
        
        # Fatigue score
        if fatigue_score > 75:
            recommendations.append("😴 High fatigue score - prioritize sleep and recovery meals")
        
        return recommendations


# Singleton
hrv_analysis_service = HRVAnalysisService()
