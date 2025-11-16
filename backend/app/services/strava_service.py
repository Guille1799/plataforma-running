"""
Strava Integration Service
Handles OAuth, activity sync, and webhook subscriptions
"""
import requests
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from .. import models, crud
from ..core.config import settings


class StravaService:
    """Service for Strava API integration."""
    
    def __init__(self):
        self.client_id = settings.strava_client_id
        self.client_secret = settings.strava_client_secret
        self.redirect_uri = settings.strava_redirect_uri
        self.base_url = "https://www.strava.com/api/v3"
    
    def get_authorization_url(self, state: str) -> str:
        """
        Generate Strava OAuth authorization URL.
        
        Args:
            state: CSRF token for security
            
        Returns:
            Authorization URL for user to visit
        """
        scope = "activity:read_all,profile:read_all"
        return (
            f"https://www.strava.com/oauth/authorize"
            f"?client_id={self.client_id}"
            f"&redirect_uri={self.redirect_uri}"
            f"&response_type=code"
            f"&scope={scope}"
            f"&state={state}"
        )
    
    def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            
        Returns:
            Token response with access_token, refresh_token, athlete data
        """
        response = requests.post(
            "https://www.strava.com/oauth/token",
            data={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "code": code,
                "grant_type": "authorization_code"
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
            "https://www.strava.com/oauth/token",
            data={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token"
            }
        )
        response.raise_for_status()
        return response.json()
    
    def get_activities(
        self,
        access_token: str,
        after: Optional[int] = None,
        per_page: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Fetch activities from Strava.
        
        Args:
            access_token: Valid access token
            after: Timestamp to fetch activities after
            per_page: Number of activities per page
            
        Returns:
            List of activity objects
        """
        params = {
            "per_page": per_page,
            "page": 1
        }
        if after:
            params["after"] = after
        
        response = requests.get(
            f"{self.base_url}/athlete/activities",
            headers={"Authorization": f"Bearer {access_token}"},
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    def get_activity_detail(
        self,
        access_token: str,
        activity_id: int
    ) -> Dict[str, Any]:
        """
        Get detailed activity data including streams.
        
        Args:
            access_token: Valid access token
            activity_id: Strava activity ID
            
        Returns:
            Detailed activity object
        """
        response = requests.get(
            f"{self.base_url}/activities/{activity_id}",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        response.raise_for_status()
        return response.json()
    
    def parse_activity_to_workout(
        self,
        activity: Dict[str, Any],
        user_id: int
    ) -> models.Workout:
        """
        Convert Strava activity to Workout model.
        
        Args:
            activity: Strava activity object
            user_id: Database user ID
            
        Returns:
            Workout instance (not yet saved)
        """
        # Map Strava type to our sport_type
        sport_type_map = {
            "Run": "running",
            "TrailRun": "trail_running",
            "VirtualRun": "running",
            "Ride": "cycling",
            "Walk": "walking",
            "Hike": "hiking"
        }
        sport_type = sport_type_map.get(activity.get("type"), "other")
        
        # Parse start time
        start_time = datetime.fromisoformat(
            activity["start_date"].replace("Z", "+00:00")
        )
        
        # Extract metrics
        workout = models.Workout(
            user_id=user_id,
            sport_type=sport_type,
            start_time=start_time,
            duration_seconds=activity.get("moving_time", 0),
            distance_meters=activity.get("distance", 0),
            avg_heart_rate=activity.get("average_heartrate"),
            max_heart_rate=activity.get("max_heartrate"),
            avg_pace=(
                activity.get("moving_time", 0) / (activity.get("distance", 1) / 1000)
                if activity.get("distance") and activity.get("distance") > 0
                else None
            ),
            max_speed=activity.get("max_speed"),
            calories=activity.get("calories"),
            elevation_gain=activity.get("total_elevation_gain"),
            avg_cadence=activity.get("average_cadence"),
            file_name=f"strava_{activity['id']}",
            source_type="strava",
            data_quality="medium" if activity.get("average_heartrate") else "basic",
            created_at=datetime.utcnow()
        )
        
        return workout
    
    def sync_activities(
        self,
        db: Session,
        user_id: int,
        access_token: str,
        after_date: Optional[datetime] = None
    ) -> List[models.Workout]:
        """
        Sync activities from Strava to database.
        
        Args:
            db: Database session
            user_id: User ID
            access_token: Valid Strava access token
            after_date: Only sync activities after this date
            
        Returns:
            List of synced workouts
        """
        # Convert datetime to timestamp
        after_ts = None
        if after_date:
            after_ts = int(after_date.timestamp())
        
        # Fetch activities
        activities = self.get_activities(access_token, after=after_ts, per_page=50)
        
        synced_workouts = []
        for activity in activities:
            # Check if already exists
            existing = db.query(models.Workout).filter(
                models.Workout.user_id == user_id,
                models.Workout.file_name == f"strava_{activity['id']}"
            ).first()
            
            if existing:
                continue
            
            # Parse and save
            workout = self.parse_activity_to_workout(activity, user_id)
            db.add(workout)
            synced_workouts.append(workout)
        
        db.commit()
        print(f"[STRAVA] Synced {len(synced_workouts)} new activities")
        return synced_workouts


# Singleton instance
strava_service = StravaService()
