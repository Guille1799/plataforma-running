"""
Health metrics synchronization service for Garmin Connect.
Fetches HRV, sleep, stress, body battery, and other wellness data.
"""

import json
import logging
from datetime import datetime, date, timedelta
from typing import Dict, Optional, List
from sqlalchemy.orm import Session

from .. import models
from ..core.config import settings

logger = logging.getLogger(__name__)


def sync_health_metrics(
    api, user_id: int, db: Session, days_back: int = 7
) -> List[models.HealthMetric]:
    """
    Sync health metrics from Garmin Connect for the last N days.

    Fetches:
    - HRV (Heart Rate Variability)
    - Resting HR
    - Sleep data (duration, scores, stages)
    - Body Battery
    - Stress levels
    - Training status and load
    - Daily activity metrics

    Args:
        api: Authenticated Garmin API instance
        user_id: User ID to sync data for
        db: Database session
        days_back: Number of days to fetch (default: 7)

    Returns:
        List of created/updated HealthMetric objects
    """
    print(
        f"[HEALTH] Starting health metrics sync for user {user_id}, {days_back} days back"
    )

    synced_metrics = []
    today = date.today()

    for day_offset in range(days_back):
        metric_date = today - timedelta(days=day_offset)
        date_str = metric_date.strftime("%Y-%m-%d")

        print(f"[HEALTH] Fetching data for {date_str}")

        # Check if we already have data for this date
        existing_metric = (
            db.query(models.HealthMetric)
            .filter(
                models.HealthMetric.user_id == user_id,
                models.HealthMetric.date == metric_date,
            )
            .first()
        )

        # Collect all data for this date
        health_data = {"user_id": user_id, "date": metric_date, "source": "garmin"}

        # 1. HRV Data
        try:
            hrv_data = api.get_hrv_data(date_str)
            if hrv_data:
                print(f"[HEALTH] HRV data keys: {list(hrv_data.keys())}")

                # Extract HRV values - check hrvSummary first
                if "hrvSummary" in hrv_data and isinstance(
                    hrv_data["hrvSummary"], dict
                ):
                    hrv_summary = hrv_data["hrvSummary"]

                    # Try different HRV field names
                    if "lastNightAvg" in hrv_summary and hrv_summary["lastNightAvg"]:
                        health_data["hrv_ms"] = hrv_summary["lastNightAvg"]
                        print(
                            f"[HEALTH] HRV (lastNightAvg): {health_data['hrv_ms']} ms"
                        )
                    elif "weeklyAvg" in hrv_summary and hrv_summary["weeklyAvg"]:
                        health_data["hrv_ms"] = hrv_summary["weeklyAvg"]
                        print(f"[HEALTH] HRV (weeklyAvg): {health_data['hrv_ms']} ms")

                # Also check top level
                if "hrv_ms" not in health_data:
                    if "lastNightAvg" in hrv_data and hrv_data["lastNightAvg"]:
                        health_data["hrv_ms"] = hrv_data["lastNightAvg"]
                        print(f"[HEALTH] HRV: {health_data['hrv_ms']} ms")

                # Log full HRV summary for debugging
                if "hrvSummary" in hrv_data:
                    print(f"[HEALTH] HRV Summary: {hrv_data['hrvSummary']}")
        except Exception as e:
            print(f"[HEALTH] Could not fetch HRV data: {e}")
            import traceback

            traceback.print_exc()

        # 2. Sleep Data
        try:
            sleep_data = api.get_sleep_data(date_str)
            if sleep_data:
                print(f"[HEALTH] Sleep data keys: {list(sleep_data.keys())}")

                # Daily sleep summary
                if "dailySleepDTO" in sleep_data and sleep_data["dailySleepDTO"]:
                    sleep_summary = sleep_data["dailySleepDTO"]

                    # DEBUG: Log the entire sleep summary to see structure
                    print(
                        f"[HEALTH] Daily sleep DTO structure: {json.dumps({k: type(v).__name__ for k, v in sleep_summary.items()}, indent=2)}"
                    )
                    if "overallSleepScore" in sleep_summary:
                        print(
                            f"[HEALTH] overallSleepScore full: {sleep_summary['overallSleepScore']}"
                        )

                    if (
                        "sleepTimeSeconds" in sleep_summary
                        and sleep_summary["sleepTimeSeconds"]
                    ):
                        health_data["sleep_duration_minutes"] = (
                            sleep_summary["sleepTimeSeconds"] // 60
                        )
                        print(
                            f"[HEALTH] Sleep duration: {health_data['sleep_duration_minutes']} min"
                        )

                    # Sleep score - try multiple fields
                    sleep_score = None

                    # Try overallSleepScore first
                    if "overallSleepScore" in sleep_summary:
                        score_data = sleep_summary["overallSleepScore"]
                        if isinstance(score_data, dict):
                            sleep_score = score_data.get("value") or score_data.get(
                                "qualifierKey"
                            )
                        elif isinstance(score_data, (int, float)):
                            sleep_score = score_data

                    # Try sleepScores array
                    if not sleep_score and "sleepScores" in sleep_summary:
                        scores = sleep_summary["sleepScores"]
                        if isinstance(scores, dict):
                            sleep_score = scores.get("overall", {}).get("value")

                    # Try restingHeartRate in sleep data as fallback indicator
                    if not sleep_score and "restingHeartRate" in sleep_summary:
                        # If we have detailed sleep data, create a basic score based on duration
                        duration_hours = (
                            health_data.get("sleep_duration_minutes", 0) / 60
                        )
                        if duration_hours >= 7:
                            sleep_score = min(100, int(85 + (duration_hours - 7) * 5))
                        elif duration_hours > 0:
                            sleep_score = int(duration_hours / 7 * 85)

                    if sleep_score:
                        health_data["sleep_score"] = sleep_score
                        print(f"[HEALTH] Sleep score: {health_data['sleep_score']}")

                    # Sleep stages - check if they exist and are not None
                    if (
                        "deepSleepSeconds" in sleep_summary
                        and sleep_summary["deepSleepSeconds"]
                    ):
                        health_data["deep_sleep_minutes"] = (
                            sleep_summary["deepSleepSeconds"] // 60
                        )
                    if (
                        "remSleepSeconds" in sleep_summary
                        and sleep_summary["remSleepSeconds"]
                    ):
                        health_data["rem_sleep_minutes"] = (
                            sleep_summary["remSleepSeconds"] // 60
                        )
                    if (
                        "lightSleepSeconds" in sleep_summary
                        and sleep_summary["lightSleepSeconds"]
                    ):
                        health_data["light_sleep_minutes"] = (
                            sleep_summary["lightSleepSeconds"] // 60
                        )
                    if (
                        "awakeSleepSeconds" in sleep_summary
                        and sleep_summary["awakeSleepSeconds"]
                    ):
                        health_data["awake_minutes"] = (
                            sleep_summary["awakeSleepSeconds"] // 60
                        )

                    # Average respiration
                    if (
                        "avgSleepRespirationRate" in sleep_summary
                        and sleep_summary["avgSleepRespirationRate"]
                    ):
                        health_data["respiration_rate"] = sleep_summary[
                            "avgSleepRespirationRate"
                        ]

                    # Average SpO2
                    if (
                        "avgOxygenSaturation" in sleep_summary
                        and sleep_summary["avgOxygenSaturation"]
                    ):
                        health_data["spo2_percentage"] = sleep_summary[
                            "avgOxygenSaturation"
                        ]

                    # Log what we got
                    print(
                        f"[HEALTH] Sleep summary parsed: duration={health_data.get('sleep_duration_minutes')}, score={health_data.get('sleep_score')}, deep={health_data.get('deep_sleep_minutes')}"
                    )
        except Exception as e:
            print(f"[HEALTH] Could not fetch sleep data: {e}")
            import traceback

            traceback.print_exc()

        # 3. Body Battery
        try:
            body_battery_data = api.get_body_battery(date_str)
            if body_battery_data:
                print(f"[HEALTH] Body Battery data available")

                # Get current/latest body battery value
                if isinstance(body_battery_data, list) and len(body_battery_data) > 0:
                    # Get the last reading of the day
                    last_reading = body_battery_data[-1]
                    if "charged" in last_reading:
                        health_data["body_battery"] = last_reading["charged"]
                        print(f"[HEALTH] Body Battery: {health_data['body_battery']}")
                elif isinstance(body_battery_data, dict):
                    if "charged" in body_battery_data:
                        health_data["body_battery"] = body_battery_data["charged"]
                    elif "currentValue" in body_battery_data:
                        health_data["body_battery"] = body_battery_data["currentValue"]
        except Exception as e:
            print(f"[HEALTH] Could not fetch body battery: {e}")

        # 4. Stress Data
        try:
            stress_data = api.get_stress_data(date_str)
            if stress_data:
                print(f"[HEALTH] Stress data available")

                # Average stress level
                if isinstance(stress_data, dict):
                    if "avgStressLevel" in stress_data:
                        health_data["stress_level"] = stress_data["avgStressLevel"]
                        print(f"[HEALTH] Stress level: {health_data['stress_level']}")
                    elif "overallStressLevel" in stress_data:
                        health_data["stress_level"] = stress_data["overallStressLevel"]
        except Exception as e:
            print(f"[HEALTH] Could not fetch stress data: {e}")

        # 5. User Summary (contains resting HR, steps, calories)
        try:
            summary_data = api.get_user_summary(date_str)
            if summary_data:
                print(f"[HEALTH] User summary keys: {list(summary_data.keys())}")

                # Resting HR
                if "restingHeartRate" in summary_data:
                    health_data["resting_hr_bpm"] = summary_data["restingHeartRate"]
                    print(f"[HEALTH] Resting HR: {health_data['resting_hr_bpm']} bpm")

                # Steps
                if "totalSteps" in summary_data:
                    health_data["steps"] = summary_data["totalSteps"]
                    print(f"[HEALTH] Steps: {health_data['steps']}")

                # Calories
                if "totalKilocalories" in summary_data:
                    health_data["calories_burned"] = summary_data["totalKilocalories"]
                if "activeKilocalories" in summary_data:
                    health_data["active_calories"] = summary_data["activeKilocalories"]

                # Intensity minutes
                if "moderateIntensityMinutes" in summary_data:
                    moderate = summary_data.get("moderateIntensityMinutes", 0)
                    vigorous = (
                        summary_data.get("vigorousIntensityMinutes", 0) * 2
                    )  # Vigorous counts double
                    health_data["intensity_minutes"] = moderate + vigorous
        except Exception as e:
            print(f"[HEALTH] Could not fetch user summary: {e}")

        # 6. Heart Rate Data (for baseline calculation)
        try:
            hr_data = api.get_heart_rates(date_str)
            if hr_data and "restingHeartRate" in hr_data:
                if "resting_hr_bpm" not in health_data:  # Only if not already set
                    health_data["resting_hr_bpm"] = hr_data["restingHeartRate"]
        except Exception as e:
            print(f"[HEALTH] Could not fetch heart rate data: {e}")

        # Create or update the health metric
        if existing_metric:
            # Update existing
            for key, value in health_data.items():
                if key not in ["user_id", "date"] and value is not None:
                    setattr(existing_metric, key, value)
            db.commit()
            db.refresh(existing_metric)
            synced_metrics.append(existing_metric)
            print(f"[HEALTH] Updated metrics for {date_str}")
        else:
            # Create new
            new_metric = models.HealthMetric(**health_data)
            db.add(new_metric)
            db.commit()
            db.refresh(new_metric)
            synced_metrics.append(new_metric)
            print(f"[HEALTH] Created new metrics for {date_str}")

    # Calculate baselines (7-day averages)
    if synced_metrics:
        _calculate_baselines(user_id, db)

    print(
        f"[HEALTH] Completed health metrics sync: {len(synced_metrics)} days processed"
    )
    return synced_metrics


def _calculate_baselines(user_id: int, db: Session):
    """Calculate 7-day baseline averages for HRV and resting HR."""
    print("[HEALTH] Calculating 7-day baselines...")

    # Get last 7 days of metrics
    seven_days_ago = date.today() - timedelta(days=7)
    recent_metrics = (
        db.query(models.HealthMetric)
        .filter(
            models.HealthMetric.user_id == user_id,
            models.HealthMetric.date >= seven_days_ago,
        )
        .all()
    )

    if not recent_metrics:
        return

    # Calculate HRV baseline
    hrv_values = [m.hrv_ms for m in recent_metrics if m.hrv_ms is not None]
    if hrv_values:
        hrv_baseline = sum(hrv_values) / len(hrv_values)
        print(f"[HEALTH] HRV baseline (7-day avg): {hrv_baseline:.1f} ms")

        # Update all recent metrics with this baseline
        for metric in recent_metrics:
            metric.hrv_baseline_ms = hrv_baseline

    # Calculate resting HR baseline
    hr_values = [
        m.resting_hr_bpm for m in recent_metrics if m.resting_hr_bpm is not None
    ]
    if hr_values:
        hr_baseline = sum(hr_values) / len(hr_values)
        print(f"[HEALTH] Resting HR baseline (7-day avg): {hr_baseline:.1f} bpm")

        # Update all recent metrics with this baseline
        for metric in recent_metrics:
            metric.resting_hr_baseline_bpm = hr_baseline

    db.commit()
    print("[HEALTH] Baselines updated")


def get_latest_health_metric(
    user_id: int, db: Session
) -> Optional[models.HealthMetric]:
    """Get the most recent health metric for a user."""
    return (
        db.query(models.HealthMetric)
        .filter(models.HealthMetric.user_id == user_id)
        .order_by(models.HealthMetric.date.desc())
        .first()
    )


def get_health_metrics_range(
    user_id: int, db: Session, start_date: date, end_date: date
) -> List[models.HealthMetric]:
    """Get health metrics for a date range."""
    return (
        db.query(models.HealthMetric)
        .filter(
            models.HealthMetric.user_id == user_id,
            models.HealthMetric.date >= start_date,
            models.HealthMetric.date <= end_date,
        )
        .order_by(models.HealthMetric.date.desc())
        .all()
    )
