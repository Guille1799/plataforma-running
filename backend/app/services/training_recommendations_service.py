"""
Training Recommendations Engine
AI-powered adaptive training plan generation
Based on HRV, fatigue, readiness, fitness level
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from enum import Enum
import math

from .. import models


class TrainingPhase(str, Enum):
    """Training cycle phases."""
    BASE = "base"  # Aerobic building phase
    BUILD = "build"  # Intensity building
    PEAK = "peak"  # Race-specific preparation
    TAPER = "taper"  # Pre-race recovery
    RECOVERY = "recovery"  # Active recovery


class IntensityZone(str, Enum):
    """Training intensity zones."""
    Z1_RECOVERY = "z1"  # 50-60% max HR
    Z2_AEROBIC = "z2"  # 60-70% max HR
    Z3_TEMPO = "z3"  # 70-80% max HR
    Z4_THRESHOLD = "z4"  # 80-90% max HR
    Z5_INTERVAL = "z5"  # 90-100% max HR


class TrainingRecommendationsService:
    """AI-powered training recommendations engine."""
    
    # Zone definitions (% of max HR)
    ZONE_RANGES = {
        IntensityZone.Z1_RECOVERY: (0.50, 0.60),
        IntensityZone.Z2_AEROBIC: (0.60, 0.70),
        IntensityZone.Z3_TEMPO: (0.70, 0.80),
        IntensityZone.Z4_THRESHOLD: (0.80, 0.90),
        IntensityZone.Z5_INTERVAL: (0.90, 1.00),
    }
    
    # Recommended weekly zone distribution by phase (%)
    ZONE_DISTRIBUTION = {
        TrainingPhase.BASE: {
            IntensityZone.Z1_RECOVERY: 20,
            IntensityZone.Z2_AEROBIC: 70,
            IntensityZone.Z3_TEMPO: 10,
            IntensityZone.Z4_THRESHOLD: 0,
            IntensityZone.Z5_INTERVAL: 0,
        },
        TrainingPhase.BUILD: {
            IntensityZone.Z1_RECOVERY: 15,
            IntensityZone.Z2_AEROBIC: 55,
            IntensityZone.Z3_TEMPO: 15,
            IntensityZone.Z4_THRESHOLD: 10,
            IntensityZone.Z5_INTERVAL: 5,
        },
        TrainingPhase.PEAK: {
            IntensityZone.Z1_RECOVERY: 10,
            IntensityZone.Z2_AEROBIC: 40,
            IntensityZone.Z3_TEMPO: 20,
            IntensityZone.Z4_THRESHOLD: 15,
            IntensityZone.Z5_INTERVAL: 15,
        },
        TrainingPhase.TAPER: {
            IntensityZone.Z1_RECOVERY: 40,
            IntensityZone.Z2_AEROBIC: 40,
            IntensityZone.Z3_TEMPO: 10,
            IntensityZone.Z4_THRESHOLD: 5,
            IntensityZone.Z5_INTERVAL: 5,
        },
        TrainingPhase.RECOVERY: {
            IntensityZone.Z1_RECOVERY: 70,
            IntensityZone.Z2_AEROBIC: 30,
            IntensityZone.Z3_TEMPO: 0,
            IntensityZone.Z4_THRESHOLD: 0,
            IntensityZone.Z5_INTERVAL: 0,
        },
    }
    
    # Weekly training load guidelines (minutes)
    WEEKLY_LOAD = {
        TrainingPhase.BASE: (120, 180),      # 2-3 hours
        TrainingPhase.BUILD: (150, 210),     # 2.5-3.5 hours
        TrainingPhase.PEAK: (180, 240),      # 3-4 hours
        TrainingPhase.TAPER: (90, 150),      # 1.5-2.5 hours
        TrainingPhase.RECOVERY: (60, 120),   # 1-2 hours
    }
    
    def generate_weekly_plan(
        self,
        db: Session,
        user_id: int,
        fatigue_score: float,  # 0-100 (from HRV service)
        readiness_score: float,  # 0-100 (from profile/health)
        phase: TrainingPhase = TrainingPhase.BUILD,
        max_hr: int = 190,
        target_race_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Generate adaptive weekly training plan.
        
        Args:
            db: Database session
            user_id: User ID
            fatigue_score: Current fatigue level (0=fresh, 100=exhausted)
            readiness_score: Recovery readiness (0=not ready, 100=peak ready)
            phase: Training phase
            max_hr: Maximum heart rate
            target_race_date: Optional race date for taper logic
            
        Returns:
            Dict with weekly plan and recommendations
        """
        # Adjust training load based on readiness
        load_adjustment = self._calculate_load_adjustment(
            fatigue_score,
            readiness_score
        )
        
        # Get base weekly load for phase
        base_load_min, base_load_max = self.WEEKLY_LOAD[phase]
        adjusted_load = base_load_min + (base_load_max - base_load_min) * load_adjustment
        
        # Generate 7 daily workouts
        daily_workouts = self._generate_daily_workouts(
            phase=phase,
            adjusted_load=adjusted_load,
            max_hr=max_hr,
            fatigue_score=fatigue_score,
            readiness_score=readiness_score,
        )
        
        # Calculate total weekly metrics
        total_load = sum(w["duration_minutes"] for w in daily_workouts)
        avg_intensity = sum(w["avg_intensity_zone"] for w in daily_workouts) / len(daily_workouts)
        
        # Generate adaptive recommendations
        recommendations = self._generate_adaptive_recommendations(
            fatigue_score,
            readiness_score,
            phase,
            total_load,
        )
        
        # Injury prevention suggestions
        injury_prevention = self._generate_injury_prevention(
            fatigue_score,
            phase,
            daily_workouts,
        )
        
        return {
            "week_plan": {
                "phase": phase.value,
                "total_load_minutes": round(total_load, 0),
                "average_intensity": avg_intensity,
                "load_adjustment_factor": round(load_adjustment, 2),
                "daily_workouts": daily_workouts,
            },
            "athlete_status": {
                "fatigue_score": round(fatigue_score, 1),
                "readiness_score": round(readiness_score, 1),
                "status": self._determine_athlete_status(fatigue_score, readiness_score),
            },
            "recommendations": recommendations,
            "injury_prevention": injury_prevention,
            "weekly_metrics": {
                "total_duration": round(total_load / 60, 1),  # in hours
                "sessions_per_week": len(daily_workouts),
                "intensity_distribution": self._calculate_intensity_distribution(daily_workouts),
            },
            "next_adjustments": self._suggest_next_adjustments(
                fatigue_score,
                readiness_score,
                phase,
            ),
            "generated_at": datetime.utcnow().isoformat(),
        }
    
    def _calculate_load_adjustment(
        self,
        fatigue_score: float,
        readiness_score: float,
    ) -> float:
        """
        Calculate training load adjustment factor (0-1.2).
        
        High readiness → increase volume
        High fatigue → decrease volume
        """
        # Readiness boost: 1.0 at 50%, up to 1.2 at 100%
        readiness_factor = 1.0 + (readiness_score - 50) * 0.004
        
        # Fatigue penalty: 1.0 at 50%, down to 0.6 at 100%
        fatigue_factor = 1.0 - (fatigue_score - 50) * 0.008
        
        # Combined adjustment
        adjustment = (readiness_factor * fatigue_factor) * 0.95 + 0.05  # Ensure not below 0.5
        
        return max(0.5, min(adjustment, 1.2))  # Clamp between 0.5 and 1.2
    
    def _generate_daily_workouts(
        self,
        phase: TrainingPhase,
        adjusted_load: float,
        max_hr: int,
        fatigue_score: float,
        readiness_score: float,
    ) -> List[Dict[str, Any]]:
        """Generate 7 daily workouts following training principles."""
        workouts = []
        week_pattern = self._get_week_pattern(phase, readiness_score)
        
        zone_distribution = self.ZONE_DISTRIBUTION[phase]
        
        for day_num, workout_type in enumerate(week_pattern):
            # Calculate daily load (7 days)
            daily_load = adjusted_load / 7
            
            # Adjust for recovery days
            if workout_type == "recovery":
                daily_load *= 0.4
            elif workout_type == "easy":
                daily_load *= 0.6
            elif workout_type == "long":
                daily_load *= 1.3
            
            # Determine primary zone
            if workout_type == "recovery":
                primary_zone = IntensityZone.Z1_RECOVERY
            elif workout_type == "easy":
                primary_zone = IntensityZone.Z2_AEROBIC
            elif workout_type == "tempo":
                primary_zone = IntensityZone.Z3_TEMPO
            elif workout_type == "threshold":
                primary_zone = IntensityZone.Z4_THRESHOLD
            elif workout_type == "interval":
                primary_zone = IntensityZone.Z5_INTERVAL
            else:  # long
                primary_zone = IntensityZone.Z2_AEROBIC
            
            # Build workout
            workout = {
                "day": day_num + 1,
                "day_name": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][day_num],
                "type": workout_type,
                "duration_minutes": round(daily_load),
                "primary_zone": primary_zone.value,
                "zone_range_bpm": self._get_zone_bpm_range(primary_zone, max_hr),
                "avg_intensity_zone": self._zone_to_numeric(primary_zone),
                "description": self._get_workout_description(
                    workout_type,
                    primary_zone,
                    daily_load,
                    max_hr,
                ),
                "adaptive_notes": self._get_adaptive_notes(
                    workout_type,
                    fatigue_score,
                    readiness_score,
                ),
            }
            workouts.append(workout)
        
        return workouts
    
    def _get_week_pattern(
        self,
        phase: TrainingPhase,
        readiness_score: float,
    ) -> List[str]:
        """Get workout pattern for the week."""
        patterns = {
            TrainingPhase.BASE: [
                "easy", "threshold", "easy", "recovery", "long", "tempo", "recovery"
            ],
            TrainingPhase.BUILD: [
                "easy", "interval", "easy", "recovery", "long", "threshold", "recovery"
            ],
            TrainingPhase.PEAK: [
                "easy", "interval", "interval", "recovery", "long", "threshold", "easy"
            ],
            TrainingPhase.TAPER: [
                "easy", "tempo", "easy", "recovery", "easy", "easy", "recovery"
            ],
            TrainingPhase.RECOVERY: [
                "recovery", "easy", "recovery", "easy", "recovery", "easy", "recovery"
            ],
        }
        
        pattern = patterns[phase]
        
        # If low readiness, add extra recovery days
        if readiness_score < 40:
            pattern = [
                "recovery" if w != "long" else w
                for w in pattern
            ]
        
        return pattern
    
    def _get_zone_bpm_range(self, zone: IntensityZone, max_hr: int) -> Dict[str, int]:
        """Get BPM range for zone."""
        min_pct, max_pct = self.ZONE_RANGES[zone]
        return {
            "min": int(max_hr * min_pct),
            "max": int(max_hr * max_pct),
        }
    
    def _zone_to_numeric(self, zone: IntensityZone) -> float:
        """Convert zone to numeric value for averaging."""
        mapping = {
            IntensityZone.Z1_RECOVERY: 1.0,
            IntensityZone.Z2_AEROBIC: 2.0,
            IntensityZone.Z3_TEMPO: 3.0,
            IntensityZone.Z4_THRESHOLD: 4.0,
            IntensityZone.Z5_INTERVAL: 5.0,
        }
        return mapping[zone]
    
    def _get_workout_description(
        self,
        workout_type: str,
        zone: IntensityZone,
        duration_minutes: float,
        max_hr: int,
    ) -> str:
        """Generate workout description."""
        if workout_type == "recovery":
            return f"{int(duration_minutes)} min easy run - focus on form and breathing"
        elif workout_type == "easy":
            return f"{int(duration_minutes)} min easy-paced run - conversational pace"
        elif workout_type == "long":
            return f"{int(duration_minutes)} min long slow distance - build aerobic base"
        elif workout_type == "tempo":
            return f"Warm-up 10min + {int(duration_minutes - 20)} min tempo ({int(max_hr * 0.75)}-{int(max_hr * 0.85)} BPM) + cool-down"
        elif workout_type == "threshold":
            return f"Warm-up + {int(duration_minutes - 15)} min threshold repeats ({int(max_hr * 0.85)}-{int(max_hr * 0.90)} BPM)"
        elif workout_type == "interval":
            return f"Warm-up + 6-8x3min intervals ({int(max_hr * 0.90)}-{int(max_hr * 1.0)} BPM) with 2min recovery"
        else:
            return f"{int(duration_minutes)} min run"
    
    def _get_adaptive_notes(
        self,
        workout_type: str,
        fatigue_score: float,
        readiness_score: float,
    ) -> str:
        """Generate adaptive notes based on athlete status."""
        notes = []
        
        if fatigue_score > 75:
            if workout_type not in ["recovery", "easy"]:
                notes.append("⚠️ High fatigue - consider reducing intensity or duration")
        
        if readiness_score > 80:
            if workout_type in ["interval", "threshold"]:
                notes.append("✅ Peak readiness - excellent day for hard work")
        
        if fatigue_score > 60 and readiness_score < 50:
            notes.append("🔄 Consider active recovery - prioritize sleep and nutrition")
        
        return " | ".join(notes) if notes else "Standard workout"
    
    def _generate_intensity_distribution(
        self,
        daily_workouts: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Calculate intensity zone distribution percentage."""
        total_minutes = sum(w["duration_minutes"] for w in daily_workouts)
        distribution = {zone.value: 0 for zone in IntensityZone}
        
        for workout in daily_workouts:
            zone = workout["primary_zone"]
            minutes = workout["duration_minutes"]
            distribution[zone] += minutes
        
        # Convert to percentages
        return {k: round(v / total_minutes * 100, 1) for k, v in distribution.items()}
    
    def _generate_adaptive_recommendations(
        self,
        fatigue_score: float,
        readiness_score: float,
        phase: TrainingPhase,
        total_load: float,
    ) -> List[str]:
        """Generate AI recommendations based on athlete state."""
        recommendations = []
        
        # Fatigue recommendations
        if fatigue_score > 75:
            recommendations.append(
                f"🔴 High fatigue ({fatigue_score:.0f}%) - Focus on recovery: sleep 8+ hours, reduce training by 10-15%"
            )
        elif fatigue_score > 60:
            recommendations.append(
                f"🟡 Moderate fatigue ({fatigue_score:.0f}%) - Maintain current load but prioritize easy days"
            )
        else:
            recommendations.append(
                f"🟢 Low fatigue ({fatigue_score:.0f}%) - You can handle challenging workouts"
            )
        
        # Readiness recommendations
        if readiness_score > 85:
            recommendations.append(
                f"✅ Excellent readiness ({readiness_score:.0f}%) - Increase intensity, target personal bests"
            )
        elif readiness_score < 40:
            recommendations.append(
                f"⚠️ Low readiness ({readiness_score:.0f}%) - Focus on recovery, consider deload week"
            )
        
        # Phase-specific recommendations
        if phase == TrainingPhase.PEAK:
            recommendations.append(
                "🎯 Peak phase: Execute race-specific workouts, run at race pace"
            )
        elif phase == TrainingPhase.TAPER:
            recommendations.append(
                "📉 Taper week: Reduce volume 40-50%, maintain intensity, prepare mentally"
            )
        elif phase == TrainingPhase.BASE:
            recommendations.append(
                "🏗️ Base phase: Build aerobic foundation, keep most runs easy (Z2)"
            )
        
        # Nutrition recommendations
        if total_load > 200:
            recommendations.append(
                "🥗 High training volume - increase carbs to 6-8g/kg, protein 1.6g/kg daily"
            )
        
        return recommendations
    
    def _generate_injury_prevention(
        self,
        fatigue_score: float,
        phase: TrainingPhase,
        daily_workouts: List[Dict[str, Any]],
    ) -> Dict[str, List[str]]:
        """Generate injury prevention strategies."""
        return {
            "strength_training": [
                "Single-leg calf raises (3x10 each leg) - ankle stability",
                "Monster walks (3x20m) - glute activation",
                "Plank variations (3x40s) - core stability",
                "Single-leg hops (3x8 each leg) - proprioception",
                "Hamstring curls (3x12) - posterior chain",
            ],
            "stretching": [
                "Hip flexor stretch (2x30s each side)",
                "Calf stretches (2x30s each side)",
                "Hamstring stretches (2x30s each side)",
                "IT band foam roll (2x60s each side)",
                "Glute foam roll (2x60s)",
            ],
            "warnings": [
                "Increase mileage no more than 10% per week",
                f"Current fatigue at {fatigue_score:.0f}% - watch for pain signals",
                "Replace running shoes every 500-800km",
                "Include 1-2 rest days per week minimum",
            ] if fatigue_score > 70 else [
                "Standard injury prevention - maintain consistency",
            ],
        }
    
    def _determine_athlete_status(
        self,
        fatigue_score: float,
        readiness_score: float,
    ) -> str:
        """Determine overall athlete status."""
        if fatigue_score > 75 and readiness_score < 40:
            return "🔴 CRITICAL - Immediate recovery needed"
        elif fatigue_score > 60:
            return "🟡 FATIGUED - Caution advised"
        elif readiness_score > 85:
            return "✅ PEAK FORM - Excellent condition"
        elif readiness_score > 70:
            return "🟢 READY - Good to push"
        else:
            return "🔵 NORMAL - Maintain training"
    
    def _suggest_next_adjustments(
        self,
        fatigue_score: float,
        readiness_score: float,
        phase: TrainingPhase,
    ) -> Dict[str, str]:
        """Suggest next training adjustments."""
        return {
            "today": "Monitor effort - adjust intensity based on how you feel",
            "tomorrow": "Plan recovery activity based on today's fatigue",
            "next_week": (
                "Reduce volume by 20%" if fatigue_score > 70
                else "Maintain current volume" if fatigue_score > 50
                else "Consider increasing volume by 10-15%"
            ),
            "next_phase": (
                f"Progress to {self._suggest_next_phase(phase).value} phase in 2-4 weeks"
                if fatigue_score < 60 and readiness_score > 70
                else "Stay in current phase, focus on recovery"
            ),
        }
    
    def _suggest_next_phase(self, current_phase: TrainingPhase) -> TrainingPhase:
        """Suggest next training phase."""
        progression = {
            TrainingPhase.RECOVERY: TrainingPhase.BASE,
            TrainingPhase.BASE: TrainingPhase.BUILD,
            TrainingPhase.BUILD: TrainingPhase.PEAK,
            TrainingPhase.PEAK: TrainingPhase.TAPER,
            TrainingPhase.TAPER: TrainingPhase.RECOVERY,
        }
        return progression.get(current_phase, TrainingPhase.BASE)
