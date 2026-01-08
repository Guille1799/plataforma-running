"""
Garmin Health Metrics Service
Fetches wellness data (HRV, Sleep, Body Battery, Stress) from Garmin Connect
"""

import tempfile
import os
from datetime import datetime, date, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
import garth
from garminconnect import Garmin as GarminConnectAPI

from .. import models, crud
from ..services.garmin_service import decrypt_token


class GarminHealthService:
    """Service for fetching health metrics from Garmin Connect."""

    def _restore_garmin_session(self, user: models.User) -> GarminConnectAPI:
        """
        Restore Garmin API session from encrypted token.

        Args:
            user: User with garmin_token

        Returns:
            Authenticated GarminConnectAPI instance
        """
        if not user.garmin_token:
            raise ValueError("User has no Garmin token")

        # Decrypt token
        session_data_str = decrypt_token(user.garmin_token)
        import json

        session_data = json.loads(session_data_str)

        # Use persistent directory for Garmin tokens
        persistent_dir = "/app/garmin_tokens"
        os.makedirs(persistent_dir, exist_ok=True)

        # Create user-specific directory
        user_token_dir = os.path.join(persistent_dir, f"user_{user.id}")
        os.makedirs(user_token_dir, exist_ok=True)

        # Restore garth session
        for filename, content in session_data.items():
            file_path = os.path.join(user_token_dir, filename)
            with open(file_path, "w") as f:
                f.write(content)

        garth.resume(user_token_dir)
        garth.configure(domain="garmin.com")

        # Note: Don't clean up - keep tokens persistent for future use

        # Create API instance
        api = GarminConnectAPI()
        return api

    def fetch_heart_rate_data(
        self, api: GarminConnectAPI, target_date: date
    ) -> Dict[str, Any]:
        """
        Fetch heart rate data including HRV and resting HR.

        Args:
            api: Authenticated Garmin API
            target_date: Date to fetch data for

        Returns:
            Dict with hrv_ms, resting_hr_bpm
        """
        date_str = target_date.strftime("%Y-%m-%d")

        try:
            # Get heart rate data for the day
            hr_data = api.get_heart_rates(date_str)

            return {
                "hrv_ms": hr_data.get("heartRateVariability"),
                "resting_hr_bpm": hr_data.get("restingHeartRate"),
            }
        except Exception as e:
            print(f"[GARMIN HEALTH] Error fetching HR data for {date_str}: {e}")
            return {"hrv_ms": None, "resting_hr_bpm": None}

    def fetch_sleep_data(
        self, api: GarminConnectAPI, target_date: date
    ) -> Dict[str, Any]:
        """
        Fetch sleep data including duration, stages, and score.

        Args:
            api: Authenticated Garmin API
            target_date: Date to fetch data for

        Returns:
            Dict with sleep metrics
        """
        date_str = target_date.strftime("%Y-%m-%d")

        try:
            sleep = api.get_sleep_data(date_str)

            if not sleep:
                return {}

            # Sleep stages (convert seconds to minutes)
            deep_seconds = sleep.get("deepSleepSeconds", 0)
            rem_seconds = sleep.get("remSleepSeconds", 0)
            light_seconds = sleep.get("lightSleepSeconds", 0)
            awake_seconds = sleep.get("awakeSleepSeconds", 0)

            return {
                "sleep_duration_minutes": sleep.get("sleepTimeSeconds", 0) // 60,
                "sleep_score": sleep.get("sleepScores", {})
                .get("overall", {})
                .get("value"),
                "deep_sleep_minutes": deep_seconds // 60,
                "rem_sleep_minutes": rem_seconds // 60,
                "light_sleep_minutes": light_seconds // 60,
                "awake_minutes": awake_seconds // 60,
                "respiration_rate": sleep.get("averageRespirationValue"),
            }
        except Exception as e:
            print(f"[GARMIN HEALTH] Error fetching sleep data for {date_str}: {e}")
            return {}

    def fetch_stress_data(
        self, api: GarminConnectAPI, target_date: date
    ) -> Dict[str, Any]:
        """
        Fetch stress data and calculate average.

        Args:
            api: Authenticated Garmin API
            target_date: Date to fetch data for

        Returns:
            Dict with stress_level
        """
        date_str = target_date.strftime("%Y-%m-%d")

        try:
            stress = api.get_stress_data(date_str)

            if not stress or not isinstance(stress, list):
                return {"stress_level": None}

            # Calculate average stress (excluding rest periods which are -1 or -2)
            stress_values = [
                s.get("stressLevel", -1) for s in stress if isinstance(s, dict)
            ]
            valid_stress = [s for s in stress_values if s >= 0]

            if not valid_stress:
                return {"stress_level": None}

            avg_stress = sum(valid_stress) // len(valid_stress)

            return {"stress_level": avg_stress}
        except Exception as e:
            print(f"[GARMIN HEALTH] Error fetching stress data for {date_str}: {e}")
            return {"stress_level": None}

    def fetch_body_battery(
        self, api: GarminConnectAPI, target_date: date
    ) -> Dict[str, Any]:
        """
        Fetch Body Battery data.

        Args:
            api: Authenticated Garmin API
            target_date: Date to fetch data for

        Returns:
            Dict with body_battery
        """
        date_str = target_date.strftime("%Y-%m-%d")

        try:
            bb_data = api.get_body_battery(date_str)

            if not bb_data or not isinstance(bb_data, list):
                return {"body_battery": None}

            # Get most recent Body Battery value (usually last entry of the day)
            bb_values = [
                entry.get("charged")
                for entry in bb_data
                if isinstance(entry, dict) and entry.get("charged")
            ]

            if not bb_values:
                return {"body_battery": None}

            # Return the last (most current) value
            return {"body_battery": bb_values[-1]}
        except Exception as e:
            print(f"[GARMIN HEALTH] Error fetching Body Battery for {date_str}: {e}")
            return {"body_battery": None}

    def fetch_steps_and_activity(
        self, api: GarminConnectAPI, target_date: date
    ) -> Dict[str, Any]:
        """
        Fetch daily steps and activity data.

        Args:
            api: Authenticated Garmin API
            target_date: Date to fetch data for

        Returns:
            Dict with steps, calories, intensity_minutes
        """
        date_str = target_date.strftime("%Y-%m-%d")

        try:
            steps_data = api.get_steps_data(date_str)

            return {
                "steps": steps_data.get("totalSteps"),
                "calories_burned": steps_data.get("totalKilocalories"),
                "active_calories": steps_data.get("activeKilocalories"),
                "intensity_minutes": steps_data.get("moderateIntensityMinutes", 0)
                + steps_data.get("vigorousIntensityMinutes", 0),
            }
        except Exception as e:
            print(f"[GARMIN HEALTH] Error fetching steps data for {date_str}: {e}")
            return {}

    def fetch_daily_summary(
        self, api: GarminConnectAPI, target_date: date
    ) -> Dict[str, Any]:
        """
        Get all health metrics for a specific date.

        Args:
            api: Authenticated Garmin API
            target_date: Date to fetch data for

        Returns:
            Combined dict with all health metrics
        """
        print(f"[GARMIN HEALTH] Fetching metrics for {target_date}")

        # Fetch all metrics
        hr_data = self.fetch_heart_rate_data(api, target_date)
        sleep_data = self.fetch_sleep_data(api, target_date)
        stress_data = self.fetch_stress_data(api, target_date)
        bb_data = self.fetch_body_battery(api, target_date)
        activity_data = self.fetch_steps_and_activity(api, target_date)

        # Combine all data
        combined = {**hr_data, **sleep_data, **stress_data, **bb_data, **activity_data}

        return combined

    def calculate_baselines(
        self, db: Session, user_id: int, days: int = 7
    ) -> Dict[str, float]:
        """
        Calculate HRV and resting HR baselines from recent data.

        Args:
            db: Database session
            user_id: User ID
            days: Number of days to average (default 7)

        Returns:
            Dict with hrv_baseline_ms and resting_hr_baseline_bpm
        """
        cutoff_date = date.today() - timedelta(days=days)

        recent_metrics = (
            db.query(models.HealthMetric)
            .filter(
                models.HealthMetric.user_id == user_id,
                models.HealthMetric.date >= cutoff_date,
                models.HealthMetric.hrv_ms.isnot(None),
            )
            .all()
        )

        if not recent_metrics:
            return {"hrv_baseline_ms": None, "resting_hr_baseline_bpm": None}

        # Calculate averages
        hrv_values = [m.hrv_ms for m in recent_metrics if m.hrv_ms]
        rhr_values = [m.resting_hr_bpm for m in recent_metrics if m.resting_hr_bpm]

        hrv_baseline = sum(hrv_values) / len(hrv_values) if hrv_values else None
        rhr_baseline = sum(rhr_values) / len(rhr_values) if rhr_values else None

        return {
            "hrv_baseline_ms": round(hrv_baseline, 1) if hrv_baseline else None,
            "resting_hr_baseline_bpm": round(rhr_baseline) if rhr_baseline else None,
        }

    def sync_health_metrics(
        self, db: Session, user_id: int, days: int = 7
    ) -> List[models.HealthMetric]:
        """
        Sync last N days of health metrics from Garmin.

        Args:
            db: Database session
            user_id: User ID
            days: Number of days to sync

        Returns:
            List of synced HealthMetric objects
        """
        user = crud.get_user_by_id(db, user_id)

        if not user or not user.garmin_token:
            raise ValueError("User has no Garmin connection")

        # Restore Garmin session
        api = self._restore_garmin_session(user)

        synced_metrics = []

        for i in range(days):
            target_date = date.today() - timedelta(days=i)

            # Check if already exists
            existing = (
                db.query(models.HealthMetric)
                .filter(
                    models.HealthMetric.user_id == user_id,
                    models.HealthMetric.date == target_date,
                )
                .first()
            )

            if existing:
                print(f"[GARMIN HEALTH] Skipping {target_date} (already exists)")
                continue

            # Fetch metrics
            data = self.fetch_daily_summary(api, target_date)

            # Skip if no data
            if not any(data.values()):
                print(f"[GARMIN HEALTH] No data for {target_date}")
                continue

            # Calculate baselines
            baselines = self.calculate_baselines(db, user_id)

            # Determine data quality
            quality = "high"
            if not data.get("hrv_ms") and not data.get("body_battery"):
                quality = "medium"
            if not data.get("sleep_duration_minutes"):
                quality = "basic"

            # Create HealthMetric
            metric = models.HealthMetric(
                user_id=user_id,
                date=target_date,
                source="garmin",
                data_quality=quality,
                hrv_baseline_ms=baselines.get("hrv_baseline_ms"),
                resting_hr_baseline_bpm=baselines.get("resting_hr_baseline_bpm"),
                **data,
            )

            db.add(metric)
            synced_metrics.append(metric)

        db.commit()

        # Update last sync timestamp
        user.last_garmin_sync = datetime.utcnow()
        db.commit()

        print(f"[GARMIN HEALTH] Synced {len(synced_metrics)} days of health metrics")

        return synced_metrics


# Singleton instance
garmin_health_service = GarminHealthService()
