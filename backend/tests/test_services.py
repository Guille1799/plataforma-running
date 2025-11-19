"""
Comprehensive tests for the 4 main AI services.

Tests cover:
1. Overtraining Detector Service (SAI algorithm)
2. HRV Analysis Service
3. Race Prediction Enhanced Service
4. Training Recommendations Service
"""

import pytest
from datetime import datetime, timedelta
from app.services.overtraining_detector_service import (
    OvertariningDetectorService,
    OvertariningScore,
)
from app.services.hrv_analysis_service import (
    HRVAnalysisService,
    HRVMetrics,
    HRVClassification,
)
from app.services.race_prediction_enhanced_service import (
    RacePredictionEnhancedService,
    EnvironmentalFactors,
    RacePredictionResult,
)
from app.services.training_recommendations_service import (
    TrainingRecommendationsService,
    TrainingPhase,
    TrainingRecommendation,
)


class TestOvertainingDetectorService:
    """Test suite for Overtraining Detector Service"""

    @pytest.fixture
    def service(self):
        """Initialize the service"""
        return OvertariningDetectorService()

    def test_sai_calculation_with_valid_metrics(self, service):
        """Test SAI formula: (Volume × Intensity × Stress) ÷ (HRV × Recovery)"""
        # Given
        volume = 10.0  # km
        intensity = 0.85  # 85% effort
        stress_level = 0.7  # stress factor
        hrv = 50  # ms
        recovery = 0.8  # recovery factor

        # When
        sai = service.calculate_sai(
            volume=volume,
            intensity=intensity,
            stress_level=stress_level,
            hrv=hrv,
            recovery=recovery,
        )

        # Then
        expected = (volume * intensity * stress_level) / (hrv * recovery)
        assert abs(sai - expected) < 0.01
        assert sai > 0

    def test_sai_high_risk(self, service):
        """Test SAI detection of high overtraining risk"""
        # Given high volume, high intensity, low HRV
        volume = 20.0  # km - high
        intensity = 0.95  # 95% effort - very high
        stress_level = 0.9  # high stress
        hrv = 20  # low HRV - concerning
        recovery = 0.5  # low recovery - concerning

        # When
        sai = service.calculate_sai(
            volume=volume,
            intensity=intensity,
            stress_level=stress_level,
            hrv=hrv,
            recovery=recovery,
        )

        # Then - SAI should be high (overtraining risk)
        assert sai > 1.5, "SAI should indicate overtraining risk"

    def test_sai_safe_range(self, service):
        """Test SAI for safe training"""
        # Given moderate metrics
        volume = 8.0  # km
        intensity = 0.65  # 65% effort - moderate
        stress_level = 0.4  # low stress
        hrv = 60  # healthy HRV
        recovery = 0.9  # good recovery

        # When
        sai = service.calculate_sai(
            volume=volume,
            intensity=intensity,
            stress_level=stress_level,
            hrv=hrv,
            recovery=recovery,
        )

        # Then - SAI should be low (safe)
        assert sai < 0.8, "SAI should be safe for this training"

    def test_recovery_status_calculation(self, service):
        """Test recovery status based on HRV and HR trends"""
        # Given
        current_hrv = 45
        baseline_hrv = 55
        resting_hr = 62
        baseline_resting_hr = 58

        # When
        recovery_status = service.calculate_recovery_status(
            current_hrv=current_hrv,
            baseline_hrv=baseline_hrv,
            resting_hr=resting_hr,
            baseline_resting_hr=baseline_resting_hr,
        )

        # Then
        assert "status" in recovery_status
        assert recovery_status["status"] in ["excellent", "good", "fair", "poor"]
        assert "percentage" in recovery_status
        assert 0 <= recovery_status["percentage"] <= 100

    def test_overtraining_alert_generation(self, service):
        """Test alert generation for overtraining detection"""
        # Given multiple poor metrics
        metrics = {
            "sai": 1.8,  # high
            "hrv_trend": -15,  # declining
            "resting_hr_trend": 8,  # increasing
            "sleep_quality": 0.4,  # poor
        }

        # When
        alert = service.generate_alert(metrics)

        # Then
        assert alert is not None
        assert "level" in alert
        assert "message" in alert
        assert alert["level"] in ["warning", "critical", "info"]


class TestHRVAnalysisService:
    """Test suite for HRV Analysis Service"""

    @pytest.fixture
    def service(self):
        """Initialize the service"""
        return HRVAnalysisService()

    def test_sdnn_calculation(self, service):
        """Test SDNN (Standard Deviation of NN intervals) calculation"""
        # Given sample RR intervals (in ms)
        rr_intervals = [
            800,
            810,
            795,
            820,
            805,
            815,
            800,
            810,
            795,
            825,
        ]

        # When
        sdnn = service.calculate_sdnn(rr_intervals)

        # Then
        assert sdnn > 0
        assert isinstance(sdnn, (int, float))
        # SDNN should be around 10-15ms for these values
        assert 5 < sdnn < 25

    def test_rmssd_calculation(self, service):
        """Test RMSSD (Root Mean Square of Successive Differences)"""
        # Given RR intervals
        rr_intervals = [800, 810, 795, 820, 805, 815, 800, 810, 795, 825]

        # When
        rmssd = service.calculate_rmssd(rr_intervals)

        # Then
        assert rmssd > 0
        assert isinstance(rmssd, (int, float))

    def test_pnn50_calculation(self, service):
        """Test pNN50 (percentage of RR intervals >50ms different)"""
        # Given RR intervals with some large differences
        rr_intervals = [800, 850, 810, 860, 820, 800, 810, 795, 825, 805]

        # When
        pnn50 = service.calculate_pnn50(rr_intervals)

        # Then
        assert 0 <= pnn50 <= 100
        assert isinstance(pnn50, (int, float))

    def test_lf_hf_ratio_calculation(self, service):
        """Test LF/HF ratio (autonomic balance)"""
        # Given HRV metrics
        lf = 800  # Low frequency
        hf = 400  # High frequency

        # When
        ratio = service.calculate_lf_hf_ratio(lf, hf)

        # Then
        assert ratio > 0
        assert ratio == 2.0  # 800/400

    def test_hrv_classification_excellent(self, service):
        """Test HRV classification for excellent state"""
        # Given good metrics
        sdnn = 120
        rmssd = 80
        pnn50 = 35

        # When
        classification = service.classify_hrv(
            sdnn=sdnn, rmssd=rmssd, pnn50=pnn50
        )

        # Then
        assert classification in [
            HRVClassification.EXCELLENT,
            HRVClassification.GOOD,
        ]

    def test_hrv_classification_poor(self, service):
        """Test HRV classification for poor state"""
        # Given poor metrics
        sdnn = 30
        rmssd = 15
        pnn50 = 5

        # When
        classification = service.classify_hrv(
            sdnn=sdnn, rmssd=rmssd, pnn50=pnn50
        )

        # Then
        assert classification in [
            HRVClassification.POOR,
            HRVClassification.FAIR,
        ]

    def test_hrv_analysis_report_generation(self, service):
        """Test complete HRV analysis report"""
        # Given
        rr_intervals = [
            800,
            810,
            795,
            820,
            805,
            815,
            800,
            810,
            795,
            825,
        ]

        # When
        report = service.generate_hrv_report(rr_intervals)

        # Then
        assert "sdnn" in report
        assert "rmssd" in report
        assert "pnn50" in report
        assert "lf_hf_ratio" in report
        assert "classification" in report
        assert "recommendations" in report


class TestRacePredictionEnhancedService:
    """Test suite for Race Prediction Enhanced Service"""

    @pytest.fixture
    def service(self):
        """Initialize the service"""
        return RacePredictionEnhancedService()

    def test_vdot_calculation(self, service):
        """Test VDOT calculation from recent race"""
        # Given a 10K race time
        distance_m = 10000
        time_seconds = 2400  # 40 minutes

        # When
        vdot = service.calculate_vdot(distance_m, time_seconds)

        # Then
        assert vdot > 0
        assert isinstance(vdot, (int, float))
        # For 10K in 40min, VDOT should be around 50-55
        assert 40 < vdot < 65

    def test_riegel_formula_prediction(self, service):
        """Test Riegel Formula: T2 = T1 × (D2/D1)^1.06"""
        # Given
        # Completed 10K in 40 minutes
        current_distance_m = 10000
        current_time_seconds = 2400
        # Want to predict 21.1K (half marathon)
        target_distance_m = 21100

        # When
        predicted_time = service.predict_with_riegel(
            current_distance_m, current_time_seconds, target_distance_m
        )

        # Then
        assert predicted_time > current_time_seconds
        assert isinstance(predicted_time, (int, float))
        # Half marathon should be roughly 85-90 minutes for this runner
        assert 4500 < predicted_time < 6000

    def test_environmental_factors_impact(self, service):
        """Test impact of environmental factors on prediction"""
        # Given base prediction: 40 minutes for 10K
        base_time = 2400

        # When applying environmental factors
        factors = EnvironmentalFactors(
            temperature=28,  # Hot
            humidity=75,  # High
            wind_speed=3,  # Moderate wind
            altitude=500,  # Altitude
            terrain="trails",  # Trails
        )
        adjusted_time = service.apply_environmental_adjustments(base_time, factors)

        # Then
        assert adjusted_time > base_time  # Should be slower
        assert isinstance(adjusted_time, (int, float))

    def test_environmental_factors_favorable(self, service):
        """Test favorable environmental conditions"""
        # Given base time
        base_time = 2400

        # When applying favorable factors
        factors = EnvironmentalFactors(
            temperature=15,  # Cool
            humidity=45,  # Moderate
            wind_speed=-2,  # Tailwind
            altitude=0,  # Sea level
            terrain="road",  # Road
        )
        adjusted_time = service.apply_environmental_adjustments(base_time, factors)

        # Then
        assert adjusted_time < base_time  # Should be faster
        assert isinstance(adjusted_time, (int, float))

    def test_groq_ai_enhancement(self, service):
        """Test AI enhancement with Groq/Llama"""
        # Given base prediction
        prediction = RacePredictionResult(
            distance_m=21100,
            predicted_time_seconds=5000,
            confidence_score=0.85,
        )

        # When asking AI for insights
        ai_insights = service.get_ai_insights(prediction)

        # Then
        assert ai_insights is not None
        assert isinstance(ai_insights, dict)
        if "insights" in ai_insights:
            assert len(ai_insights["insights"]) > 0


class TestTrainingRecommendationsService:
    """Test suite for Training Recommendations Service"""

    @pytest.fixture
    def service(self):
        """Initialize the service"""
        return TrainingRecommendationsService()

    def test_training_phase_progression(self, service):
        """Test progression through 5 training phases"""
        # Given a training cycle
        base = TrainingPhase.BASE
        build = TrainingPhase.BUILD
        peak = TrainingPhase.PEAK
        taper = TrainingPhase.TAPER
        recovery = TrainingPhase.RECOVERY

        # Then verify phase progression
        assert base.value < build.value < peak.value < taper.value < recovery.value

    def test_weekly_load_calculation(self, service):
        """Test weekly training load calculation"""
        # Given workouts for the week
        workouts = [
            {"distance_m": 10000, "intensity": 0.65, "duration_seconds": 3600},
            {"distance_m": 8000, "intensity": 0.75, "duration_seconds": 2400},
            {"distance_m": 15000, "intensity": 0.85, "duration_seconds": 4800},
            {"distance_m": 5000, "intensity": 0.55, "duration_seconds": 1800},
        ]

        # When calculating load
        total_load = service.calculate_total_training_load(workouts)

        # Then
        assert total_load > 0
        assert isinstance(total_load, (int, float))

    def test_adaptive_multiplier(self, service):
        """Test adaptive load multiplier based on recovery"""
        # Given
        current_load = 100
        hrv_recovery = 0.7  # 70% recovery
        fatigue_level = 0.5  # 50% fatigue

        # When calculating adaptive multiplier
        multiplier = service.calculate_adaptive_multiplier(
            hrv_recovery, fatigue_level
        )

        # Then
        assert 0.7 < multiplier < 1.3
        assert isinstance(multiplier, float)

    def test_weekly_plan_generation(self, service):
        """Test generation of weekly training plan"""
        # Given
        phase = TrainingPhase.BUILD
        weekly_target_load = 500
        runner_level = "intermediate"

        # When generating plan
        plan = service.generate_weekly_plan(phase, weekly_target_load, runner_level)

        # Then
        assert plan is not None
        assert len(plan) > 0  # Should have daily plans
        assert "Monday" in plan or "Monday" in str(plan).lower()

    def test_training_recommendation_specificity(self, service):
        """Test specific training recommendations"""
        # Given runner metrics
        vdot = 55
        recent_fatigue = 0.6
        target_race_days = 60

        # When getting recommendations
        recommendations = service.get_recommendations(
            vdot, recent_fatigue, target_race_days
        )

        # Then
        assert recommendations is not None
        assert len(recommendations) > 0

    def test_load_progression_safety(self, service):
        """Test that load increases follow safe progression (10% rule)"""
        # Given
        week1_load = 100
        week2_load = service.calculate_safe_next_week_load(week1_load)

        # Then - should not exceed 10% increase
        max_safe_load = week1_load * 1.1
        assert week2_load <= max_safe_load


# Integration Tests
class TestServiceIntegration:
    """Integration tests between services"""

    def test_overtraining_to_recommendations_flow(self):
        """Test flow: Overtraining detection → Adjust recommendations"""
        # Given
        ot_service = OvertariningDetectorService()
        tr_service = TrainingRecommendationsService()

        # When detecting overtraining
        sai = 1.8  # High
        alert = ot_service.generate_alert(
            {"sai": sai, "hrv_trend": -15, "resting_hr_trend": 8, "sleep_quality": 0.4}
        )

        # Then should reduce training load
        if alert["level"] == "critical":
            phase = TrainingPhase.RECOVERY
        else:
            phase = TrainingPhase.TAPER

        plan = tr_service.generate_weekly_plan(phase, 300, "intermediate")  # Reduced load
        assert plan is not None

    def test_hrv_to_adaptation_flow(self):
        """Test flow: HRV Analysis → Adaptive load calculation"""
        # Given
        hrv_service = HRVAnalysisService()
        tr_service = TrainingRecommendationsService()

        # When analyzing HRV
        rr_intervals = [800, 810, 795, 820, 805, 815, 800, 810, 795, 825]
        hrv_report = hrv_service.generate_hrv_report(rr_intervals)

        # Then use for adaptive load
        recovery_quality = hrv_report.get("recovery_quality", 0.7)
        multiplier = tr_service.calculate_adaptive_multiplier(recovery_quality, 0.5)
        assert 0.7 < multiplier < 1.3

    def test_race_prediction_to_training_flow(self):
        """Test flow: Race prediction → Training plan adaptation"""
        # Given
        rp_service = RacePredictionEnhancedService()
        tr_service = TrainingRecommendationsService()

        # When predicting race performance
        predicted_time_seconds = 5000  # Half marathon

        # Then generate specific training plan
        pace_min_km = predicted_time_seconds / 21.1 / 60
        recommendations = tr_service.get_recommendations(
            vdot=55, recent_fatigue=0.5, target_race_days=45
        )
        assert len(recommendations) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
