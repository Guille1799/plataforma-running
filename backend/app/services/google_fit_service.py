"""
Google Fit Integration Service
Handles OAuth and health data sync for Xiaomi/Amazfit users via Zepp → Google Fit
"""
import requests
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session

from .. import models, crud
from ..core.config import settings


class GoogleFitService:
    """Service for Google Fit API integration."""
    
    def __init__(self):
        self.client_id = settings.google_fit_client_id
        self.client_secret = settings.google_fit_client_secret
        self.redirect_uri = settings.google_fit_redirect_uri
        self.base_url = "https://www.googleapis.com/fitness/v1/users/me"
        self.token_url = "https://oauth2.googleapis.com/token"
    
    def get_authorization_url(self, state: str) -> str:
        """
        Generate Google OAuth authorization URL.
        
        Args:
            state: CSRF token for security
            
        Returns:
            Authorization URL for user to visit
        """
        # Google Fit scopes
        scopes = [
            "https://www.googleapis.com/auth/fitness.activity.read",
            "https://www.googleapis.com/auth/fitness.heart_rate.read",
            "https://www.googleapis.com/auth/fitness.sleep.read",
            "https://www.googleapis.com/auth/fitness.body.read",
        ]
        scope_string = " ".join(scopes)
        
        return (
            f"https://accounts.google.com/o/oauth2/v2/auth"
            f"?client_id={self.client_id}"
            f"&redirect_uri={self.redirect_uri}"
            f"&response_type=code"
            f"&scope={scope_string}"
            f"&state={state}"
            f"&access_type=offline"
            f"&prompt=consent"
        )
    
    def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            
        Returns:
            Token response with access_token, refresh_token
        """
        response = requests.post(
            self.token_url,
            data={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": self.redirect_uri
            }
        )
        response.raise_for_status()
        return response.json()
    
    def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh expired access token.
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            New token response
        """
        response = requests.post(
            self.token_url,
            data={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token"
            }
        )
        response.raise_for_status()
        return response.json()
    
    def _get_valid_token(self, user: models.User) -> str:
        """
        Get valid access token, refreshing if necessary.
        
        Args:
            user: User with Google Fit tokens
            
        Returns:
            Valid access token
        """
        # Check if token is expired
        if user.google_fit_token_expires_at and datetime.utcnow() < user.google_fit_token_expires_at:
            return user.google_fit_access_token
        
        # Refresh token
        print("[GOOGLE FIT] Token expired, refreshing...")
        token_data = self.refresh_access_token(user.google_fit_refresh_token)
        
        # Update user tokens
        user.google_fit_token = token_data["access_token"]
        user.google_fit_token_expires_at = datetime.utcnow() + timedelta(seconds=token_data["expires_in"])
        
        return token_data["access_token"]
    
    def _timestamp_nanos(self, dt: datetime) -> int:
        """Convert datetime to nanoseconds since epoch."""
        return int(dt.timestamp() * 1_000_000_000)
    
    def fetch_heart_rate_data(
        self, 
        access_token: str, 
        target_date: date
    ) -> Dict[str, Any]:
        """
        Fetch heart rate data including resting HR.
        
        Args:
            access_token: Valid Google Fit access token
            target_date: Date to fetch data for
            
        Returns:
            Dict with resting_hr_bpm
        """
        start_time = datetime.combine(target_date, datetime.min.time())
        end_time = start_time + timedelta(days=1)
        
        url = f"{self.base_url}/dataSources/derived:com.google.heart_rate.bpm:com.google.android.gms:merge_heart_rate_bpm/datasets/{self._timestamp_nanos(start_time)}-{self._timestamp_nanos(end_time)}"
        
        try:
            response = requests.get(
                url,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            response.raise_for_status()
            data = response.json()
            
            # Extract resting HR (minimum HR during rest periods)
            hr_values = []
            for point in data.get("point", []):
                for value in point.get("value", []):
                    if value.get("fpVal"):
                        hr_values.append(value["fpVal"])
            
            if not hr_values:
                return {"resting_hr_bpm": None}
            
            # Resting HR is typically the minimum HR
            resting_hr = int(min(hr_values))
            
            return {"resting_hr_bpm": resting_hr}
        except Exception as e:
            print(f"[GOOGLE FIT] Error fetching HR data: {e}")
            return {"resting_hr_bpm": None}
    
    def fetch_sleep_data(
        self, 
        access_token: str, 
        target_date: date
    ) -> Dict[str, Any]:
        """
        Fetch sleep data from Google Fit.
        
        Args:
            access_token: Valid Google Fit access token
            target_date: Date to fetch data for
            
        Returns:
            Dict with sleep metrics
        """
        # Sleep data is stored for the night ending on target_date
        start_time = datetime.combine(target_date - timedelta(days=1), datetime.min.time())
        end_time = datetime.combine(target_date, datetime.max.time())
        
        url = f"{self.base_url}/sessions"
        
        try:
            response = requests.get(
                url,
                params={
                    "startTime": start_time.isoformat() + "Z",
                    "endTime": end_time.isoformat() + "Z",
                    "activityType": 72  # Sleep activity type
                },
                headers={"Authorization": f"Bearer {access_token}"}
            )
            response.raise_for_status()
            data = response.json()
            
            sessions = data.get("session", [])
            if not sessions:
                return {}
            
            # Get the most recent sleep session
            sleep_session = sessions[-1]
            
            start_ms = int(sleep_session["startTimeMillis"])
            end_ms = int(sleep_session["endTimeMillis"])
            duration_minutes = (end_ms - start_ms) // (1000 * 60)
            
            # Fetch sleep stages
            stages_url = f"{self.base_url}/dataSources/derived:com.google.sleep.segment:com.google.android.gms:merged/datasets/{start_ms}000000-{end_ms}000000"
            stages_response = requests.get(
                stages_url,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            deep_minutes = 0
            rem_minutes = 0
            light_minutes = 0
            awake_minutes = 0
            
            if stages_response.ok:
                stages_data = stages_response.json()
                for point in stages_data.get("point", []):
                    stage_value = point.get("value", [{}])[0].get("intVal")
                    start_nanos = int(point["startTimeNanos"])
                    end_nanos = int(point["endTimeNanos"])
                    stage_duration = (end_nanos - start_nanos) // (1_000_000_000 * 60)
                    
                    # Sleep stage mapping (Google Fit values)
                    # 1 = awake, 2 = sleep, 3 = out-of-bed, 4 = light, 5 = deep, 6 = REM
                    if stage_value == 5:
                        deep_minutes += stage_duration
                    elif stage_value == 6:
                        rem_minutes += stage_duration
                    elif stage_value in [2, 4]:
                        light_minutes += stage_duration
                    elif stage_value == 1:
                        awake_minutes += stage_duration
            
            return {
                "sleep_duration_minutes": duration_minutes,
                "deep_sleep_minutes": deep_minutes if deep_minutes > 0 else None,
                "rem_sleep_minutes": rem_minutes if rem_minutes > 0 else None,
                "light_sleep_minutes": light_minutes if light_minutes > 0 else None,
                "awake_minutes": awake_minutes if awake_minutes > 0 else None
            }
        except Exception as e:
            print(f"[GOOGLE FIT] Error fetching sleep data: {e}")
            return {}
    
    def fetch_steps_and_activity(
        self, 
        access_token: str, 
        target_date: date
    ) -> Dict[str, Any]:
        """
        Fetch daily steps and activity data.
        
        Args:
            access_token: Valid Google Fit access token
            target_date: Date to fetch data for
            
        Returns:
            Dict with steps, calories, intensity_minutes
        """
        start_time = datetime.combine(target_date, datetime.min.time())
        end_time = start_time + timedelta(days=1)
        
        # Fetch steps
        steps_url = f"{self.base_url}/dataSources/derived:com.google.step_count.delta:com.google.android.gms:estimated_steps/datasets/{self._timestamp_nanos(start_time)}-{self._timestamp_nanos(end_time)}"
        
        # Fetch calories
        calories_url = f"{self.base_url}/dataSources/derived:com.google.calories.expended:com.google.android.gms:merge_calories_expended/datasets/{self._timestamp_nanos(start_time)}-{self._timestamp_nanos(end_time)}"
        
        # Fetch active minutes
        activity_url = f"{self.base_url}/dataSources/derived:com.google.active_minutes:com.google.android.gms:merge_active_minutes/datasets/{self._timestamp_nanos(start_time)}-{self._timestamp_nanos(end_time)}"
        
        result = {}
        
        try:
            # Steps
            steps_response = requests.get(steps_url, headers={"Authorization": f"Bearer {access_token}"})
            if steps_response.ok:
                steps_data = steps_response.json()
                total_steps = sum(
                    point.get("value", [{}])[0].get("intVal", 0)
                    for point in steps_data.get("point", [])
                )
                result["steps"] = total_steps if total_steps > 0 else None
            
            # Calories
            calories_response = requests.get(calories_url, headers={"Authorization": f"Bearer {access_token}"})
            if calories_response.ok:
                calories_data = calories_response.json()
                total_calories = sum(
                    point.get("value", [{}])[0].get("fpVal", 0)
                    for point in calories_data.get("point", [])
                )
                result["calories_burned"] = int(total_calories) if total_calories > 0 else None
            
            # Active minutes
            activity_response = requests.get(activity_url, headers={"Authorization": f"Bearer {access_token}"})
            if activity_response.ok:
                activity_data = activity_response.json()
                total_minutes = sum(
                    point.get("value", [{}])[0].get("intVal", 0)
                    for point in activity_data.get("point", [])
                )
                result["intensity_minutes"] = total_minutes if total_minutes > 0 else None
        
        except Exception as e:
            print(f"[GOOGLE FIT] Error fetching activity data: {e}")
        
        return result
    
    def sync_health_metrics(
        self,
        db: Session,
        user_id: int,
        days: int = 7
    ) -> List[models.HealthMetric]:
        """
        Sync last N days of health metrics from Google Fit.
        
        Args:
            db: Database session
            user_id: User ID
            days: Number of days to sync
            
        Returns:
            List of synced HealthMetric objects
        """
        user = crud.get_user(db, user_id)
        
        if not user or not user.google_fit_token:
            raise ValueError("User has no Google Fit connection")
        
        # Get valid access token
        access_token = self._get_valid_token(user)
        
        synced_metrics = []
        
        for i in range(days):
            target_date = date.today() - timedelta(days=i)
            
            # Check if already exists
            existing = db.query(models.HealthMetric).filter(
                models.HealthMetric.user_id == user_id,
                models.HealthMetric.date == target_date,
                models.HealthMetric.source == "google_fit"
            ).first()
            
            if existing:
                print(f"[GOOGLE FIT] Skipping {target_date} (already exists)")
                continue
            
            # Fetch metrics
            hr_data = self.fetch_heart_rate_data(access_token, target_date)
            sleep_data = self.fetch_sleep_data(access_token, target_date)
            activity_data = self.fetch_steps_and_activity(access_token, target_date)
            
            # Combine data
            combined = {**hr_data, **sleep_data, **activity_data}
            
            # Skip if no data
            if not any(combined.values()):
                print(f"[GOOGLE FIT] No data for {target_date}")
                continue
            
            # Determine data quality
            quality = "medium"
            if not sleep_data.get("sleep_duration_minutes"):
                quality = "basic"
            
            # Create HealthMetric
            metric = models.HealthMetric(
                user_id=user_id,
                date=target_date,
                source="google_fit",
                data_quality=quality,
                **combined
            )
            
            db.add(metric)
            synced_metrics.append(metric)
        
        db.commit()
        
        # Update last sync timestamp
        user.last_google_fit_sync = datetime.utcnow()
        db.commit()
        
        print(f"[GOOGLE FIT] Synced {len(synced_metrics)} days of health metrics")
        
        return synced_metrics


# Singleton instance
google_fit_service = GoogleFitService()
