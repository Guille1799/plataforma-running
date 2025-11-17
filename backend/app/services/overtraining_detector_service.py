"""
overtraining_detector_service.py - Overtraining Detection Algorithm

Detects signs of overtraining through analysis of:
- Resting heart rate trends (elevated = fatigue)
- HRV decline (low = insufficient recovery)
- Recovery heart rate patterns (slow = central fatigue)
- Workout frequency and intensity distribution
- Readiness score trends
- Sleep quality patterns

Based on sports physiology research and athlete monitoring best practices.
"""
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
import logging
from enum import Enum

from app import models

logger = logging.getLogger(__name__)


class OvertreaningStatus(str, Enum):
    """Overtraining risk levels."""
    HEALTHY = "healthy"           # Low risk (0-30%)
    CAUTION = "caution"           # Moderate risk (30-60%)
    WARNING = "warning"           # High risk (60-80%)
    CRITICAL = "critical"         # Very high risk (80-100%)


class OvertreaningDetectorService:
    """Service for detecting overtraining syndrome indicators."""
    
    # Configuration thresholds (can be personalized per athlete)
    CONFIG = {
        "resting_hr_increase_threshold": 0.05,      # 5% increase = concern
        "hrv_decline_threshold": 0.15,              # 15% below baseline = concern
        "consecutive_intense_days": 3,              # Max 3 consecutive hard days
        "weekly_intense_workouts": 3,               # Max 3 high-intensity per week
        "recovery_window_hours": 48,                # Recovery needed between hard sessions
        "readiness_low_threshold": 50,              # Readiness score < 50 = concern
        "consecutive_low_readiness_days": 3,        # 3+ days low readiness = warning
        "sleep_debt_hours": 5,                      # Sleep deficit vs baseline
    }
    
    def __init__(self):
        """Initialize the overtraining detector."""
        self.config = self.CONFIG.copy()
    
    def detect_overtraining_risk(
        self,
        user_id: int,
        db: Session,
        analysis_days: int = 30
    ) -> Dict[str, Any]:
        """
        Comprehensive overtraining analysis.
        
        Args:
            user_id: User to analyze
            db: Database session
            analysis_days: Number of days to analyze (default 30)
            
        Returns:
            Dict with overall risk level, contributing factors, and recommendations
        """
        logger.info(f"[OVERTRAINING] Analyzing user {user_id} over {analysis_days} days")
        
        cutoff_date = datetime.utcnow() - timedelta(days=analysis_days)
        
        # Gather all analysis components
        rhr_analysis = self._analyze_resting_hr_trend(user_id, db, cutoff_date)
        hrv_analysis = self._analyze_hrv_trend(user_id, db, cutoff_date)
        recovery_analysis = self._analyze_recovery_patterns(user_id, db, cutoff_date)
        intensity_analysis = self._analyze_intensity_distribution(user_id, db, cutoff_date)
        readiness_analysis = self._analyze_readiness_trends(user_id, db, cutoff_date)
        sleep_analysis = self._analyze_sleep_patterns(user_id, db, cutoff_date)
        
        # Calculate overall risk score (0-100)
        risk_score = self._calculate_risk_score(
            rhr_analysis,
            hrv_analysis,
            recovery_analysis,
            intensity_analysis,
            readiness_analysis,
            sleep_analysis
        )
        
        # Determine status
        status = self._determine_status(risk_score)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            status,
            rhr_analysis,
            hrv_analysis,
            recovery_analysis,
            intensity_analysis,
            readiness_analysis,
            sleep_analysis
        )
        
        return {
            "risk_score": round(risk_score, 1),
            "status": status.value,
            "risk_percentage": f"{int(risk_score)}%",
            "analysis_period_days": analysis_days,
            
            # Contributing factors
            "factors": {
                "resting_heart_rate": rhr_analysis,
                "heart_rate_variability": hrv_analysis,
                "recovery_patterns": recovery_analysis,
                "intensity_distribution": intensity_analysis,
                "readiness_trends": readiness_analysis,
                "sleep_quality": sleep_analysis,
            },
            
            # Actionable recommendations
            "recommendations": recommendations,
            
            # Emergency flags
            "immediate_action_required": status in [OvertreaningStatus.WARNING, OvertreaningStatus.CRITICAL],
            "suggested_action": self._suggest_immediate_action(status),
            
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def _analyze_resting_hr_trend(
        self,
        user_id: int,
        db: Session,
        cutoff_date: datetime
    ) -> Dict[str, Any]:
        """
        Analyze resting heart rate trend.
        
        Elevated resting HR is a key indicator of central fatigue.
        Concern: 5%+ increase from baseline over 2-3 weeks.
        """
        metrics = db.query(models.HealthMetric).filter(
            models.HealthMetric.user_id == user_id,
            models.HealthMetric.date >= cutoff_date,
            models.HealthMetric.resting_hr_bpm.isnot(None)
        ).order_by(models.HealthMetric.date.asc()).all()
        
        if len(metrics) < 7:
            return {
                "status": "insufficient_data",
                "risk_factor": 0,
                "message": "Insufficient resting HR data (need 7+ days)"
            }
        
        # Get baseline (first week)
        baseline_metrics = metrics[:7]
        baseline_rhr = sum(m.resting_hr_bpm for m in baseline_metrics) / len(baseline_metrics)
        
        # Get recent (last week)
        recent_metrics = metrics[-7:]
        recent_rhr = sum(m.resting_hr_bpm for m in recent_metrics) / len(recent_metrics)
        
        # Calculate increase percentage
        rhr_increase_pct = (recent_rhr - baseline_rhr) / baseline_rhr
        
        # Risk calculation
        threshold = self.config["resting_hr_increase_threshold"]
        if rhr_increase_pct < 0:
            risk_factor = 0  # Improvement, no risk
        elif rhr_increase_pct < threshold:
            risk_factor = 20  # Minor concern
        elif rhr_increase_pct < threshold * 2:
            risk_factor = 50  # Moderate concern
        else:
            risk_factor = 80  # High concern
        
        # Trend analysis
        trend = "↓" if rhr_increase_pct < 0 else "→" if rhr_increase_pct < 0.02 else "↑"
        
        return {
            "status": "analyzed",
            "baseline_bpm": round(baseline_rhr, 1),
            "recent_bpm": round(recent_rhr, 1),
            "increase_percentage": round(rhr_increase_pct * 100, 1),
            "trend": trend,
            "risk_factor": risk_factor,
            "interpretation": self._interpret_rhr_trend(rhr_increase_pct)
        }
    
    def _analyze_hrv_trend(
        self,
        user_id: int,
        db: Session,
        cutoff_date: datetime
    ) -> Dict[str, Any]:
        """
        Analyze Heart Rate Variability (HRV) trend.
        
        HRV is measured in milliseconds. Low HRV = sympathetic overactivity = fatigue.
        Concern: 15%+ decline from baseline indicates insufficient parasympathetic recovery.
        """
        metrics = db.query(models.HealthMetric).filter(
            models.HealthMetric.user_id == user_id,
            models.HealthMetric.date >= cutoff_date,
            models.HealthMetric.hrv_ms.isnot(None)
        ).order_by(models.HealthMetric.date.asc()).all()
        
        if len(metrics) < 7:
            return {
                "status": "insufficient_data",
                "risk_factor": 0,
                "message": "Insufficient HRV data (need 7+ days)"
            }
        
        # Get baseline (first week)
        baseline_metrics = metrics[:7]
        baseline_hrv = sum(m.hrv_ms for m in baseline_metrics) / len(baseline_metrics)
        
        # Get recent (last week)
        recent_metrics = metrics[-7:]
        recent_hrv = sum(m.hrv_ms for m in recent_metrics) / len(recent_metrics)
        
        # Calculate decline percentage
        hrv_decline_pct = (baseline_hrv - recent_hrv) / baseline_hrv
        
        # Risk calculation
        threshold = self.config["hrv_decline_threshold"]
        if hrv_decline_pct < 0:
            risk_factor = 0  # Improvement
        elif hrv_decline_pct < threshold:
            risk_factor = 15  # Normal variation
        elif hrv_decline_pct < threshold * 2:
            risk_factor = 50  # Moderate concern
        else:
            risk_factor = 75  # High concern
        
        trend = "↓" if hrv_decline_pct > 0 else "↑"
        
        return {
            "status": "analyzed",
            "baseline_ms": round(baseline_hrv, 1),
            "recent_ms": round(recent_hrv, 1),
            "decline_percentage": round(hrv_decline_pct * 100, 1),
            "trend": trend,
            "risk_factor": risk_factor,
            "interpretation": self._interpret_hrv_trend(hrv_decline_pct)
        }
    
    def _analyze_recovery_patterns(
        self,
        user_id: int,
        db: Session,
        cutoff_date: datetime
    ) -> Dict[str, Any]:
        """
        Analyze workout recovery heart rate patterns.
        
        Key indicator: How fast does HR drop after intense exercise?
        Slow recovery HR = poor cardiac autonomic function = fatigue sign.
        """
        workouts = db.query(models.Workout).filter(
            models.Workout.user_id == user_id,
            models.Workout.start_time >= cutoff_date,
            models.Workout.max_heart_rate.isnot(None),
            models.Workout.avg_heart_rate.isnot(None)
        ).order_by(models.Workout.start_time.desc()).limit(10).all()
        
        if len(workouts) < 3:
            return {
                "status": "insufficient_data",
                "risk_factor": 0,
                "message": "Insufficient workout data (need 3+ intense sessions)"
            }
        
        recovery_indices = []
        for workout in workouts:
            # Recovery index: (Max HR - Avg HR) indicates intensity variation
            # Higher = better (large HR drop = good recovery response)
            if workout.max_heart_rate and workout.avg_heart_rate:
                recovery_idx = (workout.max_heart_rate - workout.avg_heart_rate) / workout.max_heart_rate
                recovery_indices.append(recovery_idx)
        
        if not recovery_indices:
            return {
                "status": "no_data",
                "risk_factor": 0,
                "message": "No HR data available for recovery analysis"
            }
        
        avg_recovery_index = sum(recovery_indices) / len(recovery_indices)
        min_recovery_index = min(recovery_indices)
        
        # Risk: If recovery indices are low (poor HR drop), indicates fatigue
        if avg_recovery_index < 0.15:  # Poor recovery
            risk_factor = 70
            interpretation = "Poor recovery patterns - high sympathetic dominance"
        elif avg_recovery_index < 0.25:
            risk_factor = 40
            interpretation = "Moderate recovery patterns"
        else:
            risk_factor = 10
            interpretation = "Good recovery patterns - autonomic balance maintained"
        
        return {
            "status": "analyzed",
            "average_recovery_index": round(avg_recovery_index, 3),
            "minimum_recovery_index": round(min_recovery_index, 3),
            "workouts_analyzed": len(recovery_indices),
            "risk_factor": risk_factor,
            "interpretation": interpretation
        }
    
    def _analyze_intensity_distribution(
        self,
        user_id: int,
        db: Session,
        cutoff_date: datetime
    ) -> Dict[str, Any]:
        """
        Analyze workout intensity distribution.
        
        Red flags:
        - More than 3 high-intensity workouts per week
        - More than 2 consecutive intense days
        - Insufficient low-intensity volume (base training)
        """
        workouts = db.query(models.Workout).filter(
            models.Workout.user_id == user_id,
            models.Workout.start_time >= cutoff_date
        ).order_by(models.Workout.start_time.asc()).all()
        
        if not workouts:
            return {
                "status": "no_data",
                "risk_factor": 0,
                "message": "No workout data available"
            }
        
        # Classify intensity based on HR zones (assume max HR = 190)
        high_intensity_count = 0
        moderate_intensity_count = 0
        low_intensity_count = 0
        consecutive_intense = 0
        max_consecutive_intense = 0
        
        for workout in workouts:
            if not workout.avg_heart_rate or not workout.max_heart_rate:
                continue
            
            # Simple classification (would be better with user's max HR)
            max_hr_estimate = workout.max_heart_rate or 190
            intensity_pct = (workout.avg_heart_rate / max_hr_estimate) * 100
            
            if intensity_pct > 85:  # High intensity (threshold+)
                high_intensity_count += 1
                consecutive_intense += 1
            elif intensity_pct > 75:  # Moderate
                moderate_intensity_count += 1
                consecutive_intense = 0
            else:  # Low
                low_intensity_count += 1
                consecutive_intense = 0
            
            max_consecutive_intense = max(max_consecutive_intense, consecutive_intense)
        
        total_workouts = len(workouts)
        high_intensity_pct = (high_intensity_count / total_workouts * 100) if total_workouts > 0 else 0
        low_intensity_pct = (low_intensity_count / total_workouts * 100) if total_workouts > 0 else 0
        
        # Risk calculation based on polarized training principle
        # Ideal: 80% low intensity, 20% high intensity
        risk_factor = 0
        
        # Too many intense workouts?
        if high_intensity_count > self.config["weekly_intense_workouts"] * 4:  # Per 30 days
            risk_factor += 30
        
        # Consecutive intense days?
        if max_consecutive_intense > self.config["consecutive_intense_days"]:
            risk_factor += 25
        
        # Insufficient base training?
        if low_intensity_pct < 60:
            risk_factor += 20
        
        interpretation_notes = []
        if high_intensity_pct > 25:
            interpretation_notes.append(f"High-intensity workouts at {high_intensity_pct:.0f}% (ideal: 15-25%)")
        if max_consecutive_intense > 2:
            interpretation_notes.append(f"{max_consecutive_intense} consecutive intense days (max recommended: 3)")
        if low_intensity_pct < 65:
            interpretation_notes.append(f"Base training at {low_intensity_pct:.0f}% (ideal: 70-80%)")
        
        if not interpretation_notes:
            interpretation_notes.append("Training distribution appears balanced")
        
        return {
            "status": "analyzed",
            "total_workouts": total_workouts,
            "high_intensity_count": high_intensity_count,
            "high_intensity_percentage": round(high_intensity_pct, 1),
            "moderate_intensity_count": moderate_intensity_count,
            "low_intensity_count": low_intensity_count,
            "low_intensity_percentage": round(low_intensity_pct, 1),
            "max_consecutive_intense_days": max_consecutive_intense,
            "risk_factor": min(risk_factor, 75),
            "interpretation": " | ".join(interpretation_notes)
        }
    
    def _analyze_readiness_trends(
        self,
        user_id: int,
        db: Session,
        cutoff_date: datetime
    ) -> Dict[str, Any]:
        """
        Analyze readiness score trends.
        
        Persistent low readiness (< 50) indicates insufficient recovery.
        Concern: 3+ consecutive days of low readiness.
        """
        # This would use the readiness calculation from health metrics
        # For now, we'll track patterns if readiness data is available
        
        metrics = db.query(models.HealthMetric).filter(
            models.HealthMetric.user_id == user_id,
            models.HealthMetric.date >= cutoff_date
        ).order_by(models.HealthMetric.date.asc()).all()
        
        if not metrics:
            return {
                "status": "insufficient_data",
                "risk_factor": 0,
                "message": "No health metrics available"
            }
        
        # For MVP, we'll flag if readiness scores are consistently low
        low_readiness_days = 0
        consecutive_low = 0
        max_consecutive_low = 0
        average_readiness = 0
        
        # This is a simplified calculation - would need actual readiness scores
        # For now, estimate from body_battery and other factors
        for metric in metrics:
            # Simple estimate: body_battery directly corresponds to readiness
            if metric.body_battery and metric.body_battery < 30:
                low_readiness_days += 1
                consecutive_low += 1
            else:
                consecutive_low = 0
            
            max_consecutive_low = max(max_consecutive_low, consecutive_low)
        
        days_with_data = len(metrics)
        low_readiness_pct = (low_readiness_days / days_with_data * 100) if days_with_data > 0 else 0
        
        # Risk calculation
        risk_factor = 0
        if max_consecutive_low >= 3:
            risk_factor += 50
        if low_readiness_pct > 40:
            risk_factor += 30
        
        return {
            "status": "analyzed",
            "days_analyzed": days_with_data,
            "low_readiness_days": low_readiness_days,
            "low_readiness_percentage": round(low_readiness_pct, 1),
            "max_consecutive_low_days": max_consecutive_low,
            "risk_factor": min(risk_factor, 70),
            "interpretation": f"{low_readiness_pct:.0f}% of days with low readiness"
        }
    
    def _analyze_sleep_patterns(
        self,
        user_id: int,
        db: Session,
        cutoff_date: datetime
    ) -> Dict[str, Any]:
        """
        Analyze sleep quality and duration trends.
        
        Overtraining often causes sleep disruption.
        Concern: Chronic sleep debt (>2h below baseline) or poor sleep quality.
        """
        metrics = db.query(models.HealthMetric).filter(
            models.HealthMetric.user_id == user_id,
            models.HealthMetric.date >= cutoff_date,
            models.HealthMetric.sleep_duration_minutes.isnot(None)
        ).order_by(models.HealthMetric.date.asc()).all()
        
        if len(metrics) < 7:
            return {
                "status": "insufficient_data",
                "risk_factor": 0,
                "message": "Insufficient sleep data (need 7+ days)"
            }
        
        # Get baseline (first week) and recent (last week)
        baseline_metrics = metrics[:7]
        baseline_sleep_hours = sum(m.sleep_duration_minutes for m in baseline_metrics) / 7 / 60
        
        recent_metrics = metrics[-7:]
        recent_sleep_hours = sum(m.sleep_duration_minutes for m in recent_metrics) / 7 / 60
        
        sleep_deficit_hours = baseline_sleep_hours - recent_sleep_hours
        
        # Sleep quality analysis
        baseline_quality = sum(m.sleep_score for m in baseline_metrics if m.sleep_score) / len(
            [m for m in baseline_metrics if m.sleep_score]
        ) if any(m.sleep_score for m in baseline_metrics) else 0
        
        recent_quality = sum(m.sleep_score for m in recent_metrics if m.sleep_score) / len(
            [m for m in recent_metrics if m.sleep_score]
        ) if any(m.sleep_score for m in recent_metrics) else 0
        
        # Risk calculation
        risk_factor = 0
        
        if sleep_deficit_hours > self.config["sleep_debt_hours"]:
            risk_factor += 50
        elif sleep_deficit_hours > 2:
            risk_factor += 30
        elif sleep_deficit_hours > 1:
            risk_factor += 15
        
        # Quality drop
        quality_drop = baseline_quality - recent_quality
        if quality_drop > 15:
            risk_factor += 25
        
        return {
            "status": "analyzed",
            "baseline_sleep_hours": round(baseline_sleep_hours, 1),
            "recent_sleep_hours": round(recent_sleep_hours, 1),
            "sleep_deficit_hours": round(sleep_deficit_hours, 1),
            "baseline_quality_score": round(baseline_quality, 1) if baseline_quality else None,
            "recent_quality_score": round(recent_quality, 1) if recent_quality else None,
            "quality_drop": round(quality_drop, 1) if recent_quality and baseline_quality else None,
            "risk_factor": min(risk_factor, 70),
            "interpretation": f"Sleep deficit: {sleep_deficit_hours:.1f}h | Quality drop: {quality_drop:.0f} points"
        }
    
    def _calculate_risk_score(
        self,
        rhr_analysis: Dict,
        hrv_analysis: Dict,
        recovery_analysis: Dict,
        intensity_analysis: Dict,
        readiness_analysis: Dict,
        sleep_analysis: Dict
    ) -> float:
        """Calculate overall overtraining risk score (0-100)."""
        factors = [
            ("resting_hr", rhr_analysis.get("risk_factor", 0), 0.20),
            ("hrv", hrv_analysis.get("risk_factor", 0), 0.20),
            ("recovery", recovery_analysis.get("risk_factor", 0), 0.15),
            ("intensity", intensity_analysis.get("risk_factor", 0), 0.20),
            ("readiness", readiness_analysis.get("risk_factor", 0), 0.15),
            ("sleep", sleep_analysis.get("risk_factor", 0), 0.10),
        ]
        
        weighted_score = sum(factor[1] * factor[2] for factor in factors)
        return weighted_score
    
    def _determine_status(self, risk_score: float) -> OvertreaningStatus:
        """Determine overtraining status from risk score."""
        if risk_score < 30:
            return OvertreaningStatus.HEALTHY
        elif risk_score < 60:
            return OvertreaningStatus.CAUTION
        elif risk_score < 80:
            return OvertreaningStatus.WARNING
        else:
            return OvertreaningStatus.CRITICAL
    
    def _generate_recommendations(
        self,
        status: OvertreaningStatus,
        rhr_analysis: Dict,
        hrv_analysis: Dict,
        recovery_analysis: Dict,
        intensity_analysis: Dict,
        readiness_analysis: Dict,
        sleep_analysis: Dict
    ) -> List[str]:
        """Generate actionable recommendations based on analysis."""
        recommendations = []
        
        # Resting HR recommendations
        if rhr_analysis.get("risk_factor", 0) > 40:
            recommendations.append("🚨 Elevated resting HR detected - reduce training intensity for 3-5 days")
        elif rhr_analysis.get("risk_factor", 0) > 20:
            recommendations.append("⚠️ Resting HR trending up - monitor closely and ensure adequate recovery")
        
        # HRV recommendations
        if hrv_analysis.get("risk_factor", 0) > 50:
            recommendations.append("🚨 HRV significantly declined - prioritize sleep and recovery days")
        elif hrv_analysis.get("risk_factor", 0) > 20:
            recommendations.append("⚠️ HRV lower than baseline - add extra recovery days")
        
        # Recovery recommendations
        if recovery_analysis.get("risk_factor", 0) > 60:
            recommendations.append("🚨 Poor recovery patterns detected - likely central fatigue")
        
        # Intensity recommendations
        if intensity_analysis.get("risk_factor", 0) > 40:
            intensity_msg = intensity_analysis.get("interpretation", "")
            recommendations.append(f"📊 Training distribution concerns: {intensity_msg}")
        
        # Readiness recommendations
        if readiness_analysis.get("risk_factor", 0) > 50:
            recommendations.append("🚨 Consistently low readiness - consider rest day")
        
        # Sleep recommendations
        if sleep_analysis.get("risk_factor", 0) > 40:
            sleep_deficit = sleep_analysis.get("sleep_deficit_hours", 0)
            recommendations.append(f"😴 Sleep debt of {sleep_deficit:.1f}h - prioritize sleep recovery")
        
        # Add status-specific recommendations
        if status == OvertreaningStatus.CRITICAL:
            recommendations.insert(0, "🛑 CRITICAL: Take 3-7 days of easy training/rest. Consult healthcare provider if symptoms persist.")
        elif status == OvertreaningStatus.WARNING:
            recommendations.insert(0, "⚠️ WARNING: Reduce training volume by 40-50% and add extra recovery days")
        elif status == OvertreaningStatus.CAUTION:
            recommendations.insert(0, "ℹ️ Caution: Monitor trends closely. Reduce intensity 1-2 sessions this week")
        else:
            recommendations.insert(0, "✅ Healthy: Continue with current training load")
        
        return recommendations
    
    def _suggest_immediate_action(self, status: OvertreaningStatus) -> str:
        """Suggest immediate action based on status."""
        actions = {
            OvertreaningStatus.HEALTHY: "Continue training as planned",
            OvertreaningStatus.CAUTION: "Reduce intensity by 20-30%",
            OvertreaningStatus.WARNING: "Take a complete rest day or easy recovery run",
            OvertreaningStatus.CRITICAL: "STOP training. Take 3-7 days complete rest or very light activity"
        }
        return actions.get(status, "Unknown")
    
    # ===== Interpretation helpers =====
    
    @staticmethod
    def _interpret_rhr_trend(increase_pct: float) -> str:
        """Interpret resting HR trend."""
        if increase_pct < 0:
            return "Improving - HR dropping (positive)"
        elif increase_pct < 0.03:
            return "Stable - normal variation"
        elif increase_pct < 0.05:
            return "Slight elevation - monitor"
        elif increase_pct < 0.10:
            return "Elevated - possible fatigue accumulation"
        else:
            return "Significantly elevated - signs of overtraining"
    
    @staticmethod
    def _interpret_hrv_trend(decline_pct: float) -> str:
        """Interpret HRV trend."""
        if decline_pct < 0:
            return "Improving - HRV increasing (positive)"
        elif decline_pct < 0.10:
            return "Normal variation"
        elif decline_pct < 0.25:
            return "Moderate decline - accumulating fatigue"
        else:
            return "Significant decline - insufficient recovery"


# Singleton
overtraining_detector = OvertreaningDetectorService()
