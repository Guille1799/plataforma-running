"""
Enhanced Race Prediction Service
Refines race predictions with weather, terrain, and altitude adjustments
Plus confidence scoring and advanced analysis
"""
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import math
from enum import Enum

from .. import models


class TerrainType(str, Enum):
    """Terrain difficulty classification."""
    FLAT = "flat"  # Road, track
    ROLLING = "rolling"  # Some hills
    HILLY = "hilly"  # Significant elevation
    MOUNTAIN = "mountain"  # Major climbs


class WeatherCondition(str, Enum):
    """Weather conditions affecting performance."""
    IDEAL = "ideal"  # Cool, dry, no wind
    GOOD = "good"  # Normal conditions
    FAIR = "fair"  # Slightly adverse
    POOR = "poor"  # Very challenging


class RacePredictionEnhancedService:
    """Enhanced race prediction with environmental factors."""
    
    # Environmental adjustment factors (multipliers)
    WEATHER_ADJUSTMENTS = {
        WeatherCondition.IDEAL: 0.98,  # 2% improvement
        WeatherCondition.GOOD: 1.00,   # Neutral
        WeatherCondition.FAIR: 1.02,   # 2% slower
        WeatherCondition.POOR: 1.05,   # 5% slower
    }
    
    # Terrain difficulty factors
    TERRAIN_ADJUSTMENTS = {
        TerrainType.FLAT: 0.98,      # 2% improvement (optimal)
        TerrainType.ROLLING: 1.00,   # Neutral
        TerrainType.HILLY: 1.04,     # 4% slower
        TerrainType.MOUNTAIN: 1.08,  # 8% slower
    }
    
    # Altitude factors (above sea level)
    # Performance decreases at high altitude due to reduced oxygen
    ALTITUDE_THRESHOLD = 1500  # meters
    
    # Temperature adjustment (optimal is 10-15°C for distance running)
    TEMP_OPTIMAL_MIN = 10
    TEMP_OPTIMAL_MAX = 15
    
    # Humidity adjustment (optimal is 40-60%)
    HUMIDITY_OPTIMAL_MIN = 40
    HUMIDITY_OPTIMAL_MAX = 60
    
    # Wind adjustment (km/h)
    WIND_THRESHOLD = 15  # km/h headwind becomes significant
    
    def predict_with_conditions(
        self,
        db: Session,
        user_id: int,
        base_time_minutes: float,
        base_distance_km: float,
        target_distance_km: float,
        weather: Optional[Dict[str, Any]] = None,
        terrain: TerrainType = TerrainType.ROLLING,
        altitude_m: int = 0,
    ) -> Dict[str, Any]:
        """
        Predict race time with environmental adjustments.
        
        Args:
            db: Database session
            user_id: User ID
            base_time_minutes: Time for base race (in minutes)
            base_distance_km: Distance of base race
            target_distance_km: Target race distance
            weather: Dict with temp_c, humidity_pct, wind_kmh, condition
            terrain: Terrain type
            altitude_m: Altitude above sea level
            
        Returns:
            Dict with prediction, adjustments, and confidence
        """
        # Base prediction using Riegel formula
        base_prediction = self._riegel_prediction(
            base_distance_km,
            base_time_minutes,
            target_distance_km
        )
        
        # Calculate all adjustment factors
        weather_factor = self._calculate_weather_factor(weather)
        terrain_factor = self._calculate_terrain_factor(terrain)
        altitude_factor = self._calculate_altitude_factor(altitude_m)
        
        # Combined adjustment
        total_adjustment = weather_factor * terrain_factor * altitude_factor
        adjusted_prediction = base_prediction * total_adjustment
        
        # Calculate confidence score (0-100)
        confidence = self._calculate_advanced_confidence(
            base_distance_km,
            target_distance_km,
            weather_factor,
            terrain_factor,
            altitude_factor
        )
        
        # Generate recommendations
        recommendations = self._generate_race_recommendations(
            weather_factor,
            terrain_factor,
            altitude_factor,
            adjusted_prediction
        )
        
        return {
            "prediction": {
                "base_prediction_minutes": round(base_prediction, 2),
                "adjusted_prediction_minutes": round(adjusted_prediction, 2),
                "pace_km_per_hour": round(target_distance_km / (adjusted_prediction / 60), 2),
                "formatted_time": self._format_time(adjusted_prediction),
                "formatted_pace": self._format_pace(adjusted_prediction / target_distance_km),
            },
            "adjustments": {
                "weather_factor": round(weather_factor, 4),
                "terrain_factor": round(terrain_factor, 4),
                "altitude_factor": round(altitude_factor, 4),
                "total_adjustment": round(total_adjustment, 4),
                "adjustment_percentage": round((total_adjustment - 1) * 100, 2),
            },
            "conditions": {
                "weather": weather or {},
                "terrain": terrain.value,
                "altitude_m": altitude_m,
            },
            "confidence": {
                "score": round(confidence, 1),
                "level": self._confidence_level(confidence),
                "factors": self._confidence_factors_detail(
                    base_distance_km,
                    target_distance_km,
                    confidence
                ),
            },
            "recommendations": recommendations,
            "generated_at": datetime.utcnow().isoformat(),
        }
    
    def _calculate_weather_factor(
        self,
        weather: Optional[Dict[str, Any]]
    ) -> float:
        """Calculate weather impact on performance."""
        if not weather:
            return 1.0  # Neutral if no data
        
        factor = 1.0
        
        # Temperature adjustment
        temp = weather.get("temp_c", 12.5)  # Assume neutral
        if temp < self.TEMP_OPTIMAL_MIN:
            # Too cold: 1% slower per 2°C below optimal
            factor *= (1 + (self.TEMP_OPTIMAL_MIN - temp) * 0.005)
        elif temp > self.TEMP_OPTIMAL_MAX:
            # Too hot: 2% slower per °C above optimal
            factor *= (1 + (temp - self.TEMP_OPTIMAL_MAX) * 0.02)
        
        # Humidity adjustment
        humidity = weather.get("humidity_pct", 50)  # Assume neutral
        if humidity < self.HUMIDITY_OPTIMAL_MIN:
            # Too dry: minimal impact
            factor *= 1.005
        elif humidity > self.HUMIDITY_OPTIMAL_MAX:
            # Too humid: increases effort
            factor *= (1 + (humidity - self.HUMIDITY_OPTIMAL_MAX) * 0.005)
        
        # Wind adjustment (assume headwind)
        wind = weather.get("wind_kmh", 0)
        if wind > self.WIND_THRESHOLD:
            # Significant headwind impact
            # Approximately 1% slower per km/h above threshold
            factor *= (1 + (wind - self.WIND_THRESHOLD) * 0.01)
        
        # Condition override
        condition = weather.get("condition")
        if condition and condition in [c.value for c in WeatherCondition]:
            condition_enum = WeatherCondition(condition)
            factor *= self.WEATHER_ADJUSTMENTS[condition_enum]
        
        return factor
    
    def _calculate_terrain_factor(self, terrain: TerrainType) -> float:
        """Calculate terrain impact on performance."""
        return self.TERRAIN_ADJUSTMENTS.get(terrain, 1.0)
    
    def _calculate_altitude_factor(self, altitude_m: int) -> float:
        """
        Calculate altitude impact on performance.
        
        Performance decreases significantly above 1500m.
        Formula: impact ≈ (altitude - threshold) * 0.0001 + 1
        """
        if altitude_m <= self.ALTITUDE_THRESHOLD:
            return 1.0  # No impact below threshold
        
        # Linear approximation for altitude impact
        excess_altitude = altitude_m - self.ALTITUDE_THRESHOLD
        factor = 1 + (excess_altitude * 0.0001)
        
        return min(factor, 1.15)  # Cap at 15% slower
    
    def _riegel_prediction(
        self,
        base_distance_km: float,
        base_time_minutes: float,
        target_distance_km: float,
    ) -> float:
        """
        Riegel formula for race time prediction.
        
        T2 = T1 * (D2/D1) ^ 1.06
        """
        distance_ratio = target_distance_km / base_distance_km
        exponent = 1.06  # Riegel constant (1.06-1.07)
        predicted_time = base_time_minutes * (distance_ratio ** exponent)
        return predicted_time
    
    def _calculate_advanced_confidence(
        self,
        base_distance_km: float,
        target_distance_km: float,
        weather_factor: float,
        terrain_factor: float,
        altitude_factor: float,
    ) -> float:
        """
        Calculate confidence score (0-100).
        
        Higher when:
        - Base and target distances are closer
        - Conditions are favorable
        - Environmental factors are optimal
        """
        # Distance similarity confidence (0-40 points)
        distance_ratio = target_distance_km / base_distance_km
        if 0.8 <= distance_ratio <= 1.2:
            distance_confidence = 40
        else:
            distance_confidence = max(0, 40 - (abs(distance_ratio - 1) * 20))
        
        # Conditions confidence (0-60 points)
        # Optimal conditions = high confidence
        weather_confidence = (1 - min(abs(weather_factor - 1), 0.1) / 0.1) * 20
        terrain_confidence = (1 - min(abs(terrain_factor - 1), 0.1) / 0.1) * 20
        altitude_confidence = (1 - min(abs(altitude_factor - 1), 0.1) / 0.1) * 20
        
        total = distance_confidence + weather_confidence + terrain_confidence + altitude_confidence
        return min(total, 100)
    
    def _confidence_level(self, confidence: float) -> str:
        """Convert confidence score to level."""
        if confidence >= 85:
            return "very_high"
        elif confidence >= 70:
            return "high"
        elif confidence >= 55:
            return "moderate"
        elif confidence >= 40:
            return "low"
        else:
            return "very_low"
    
    def _confidence_factors_detail(
        self,
        base_distance_km: float,
        target_distance_km: float,
        confidence: float,
    ) -> Dict[str, Any]:
        """Detailed confidence factors."""
        distance_ratio = target_distance_km / base_distance_km
        
        return {
            "distance_ratio": round(distance_ratio, 2),
            "distance_impact": "High match" if 0.8 <= distance_ratio <= 1.2 else "Lower confidence due to distance difference",
            "overall_score": round(confidence, 1),
        }
    
    def _generate_race_recommendations(
        self,
        weather_factor: float,
        terrain_factor: float,
        altitude_factor: float,
        predicted_time_minutes: float,
    ) -> List[str]:
        """Generate actionable race recommendations."""
        recommendations = []
        
        # Weather recommendations
        if weather_factor > 1.03:
            recommendations.append("⚠️ Challenging weather expected - adjust pace strategy")
            recommendations.append("💧 Carry extra fluids for adverse conditions")
        elif weather_factor < 0.99:
            recommendations.append("✅ Favorable weather predicted - optimal race conditions")
        
        # Terrain recommendations
        if terrain_factor > 1.04:
            recommendations.append("⛰️ Hilly terrain - practice downhill running technique")
            recommendations.append("🔋 Build lower body strength for hills")
        elif terrain_factor < 0.99:
            recommendations.append("🏃 Flat terrain - focus on speed and tempo work")
        
        # Altitude recommendations
        if altitude_factor > 1.02:
            recommendations.append("🏔️ High altitude race - arrive 2-3 weeks early for acclimatization")
            recommendations.append("📊 Increase iron intake and hydration at altitude")
        
        # General recommendations
        if predicted_time_minutes < 100:  # 5K-10K
            recommendations.append("🎯 Focus on aerobic capacity and lactate threshold")
        elif predicted_time_minutes < 180:  # Half marathon
            recommendations.append("🎯 Balance speed work with endurance training")
        else:  # Marathon
            recommendations.append("🎯 Prioritize aerobic base and race-day fueling strategy")
        
        return recommendations if recommendations else ["✅ Standard race preparation recommended"]
    
    def _format_time(self, minutes: float) -> str:
        """Format time as HH:MM:SS."""
        total_seconds = int(minutes * 60)
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def _format_pace(self, pace_min_per_km: float) -> str:
        """Format pace as MM:SS per km."""
        total_seconds = int(pace_min_per_km * 60)
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes:02d}:{seconds:02d} /km"
