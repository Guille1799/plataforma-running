"""
Strava Integration Router
Handles OAuth flow and activity sync
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
import secrets

from app.database import get_db
from app import models
from app.services.strava_service import strava_service
from app.dependencies.auth import get_current_user
from datetime import datetime

router = APIRouter(prefix="/api/v1/strava", tags=["Strava"])


@router.get("/auth-url")
def get_strava_auth_url(
    current_user: models.User = Depends(get_current_user)
):
    """
    Get Strava OAuth authorization URL.
    
    Returns URL for user to authorize the app.
    
    Note: The CSRF state token is returned to the client but not stored server-side.
    For production, consider storing the state in a session or Redis cache with 
    current_user.id to validate the callback and prevent CSRF attacks.
    """
    # Generate CSRF token
    state = secrets.token_urlsafe(32)
    
    auth_url = strava_service.get_authorization_url(state)
    
    return {
        "auth_url": auth_url,
        "state": state
    }


@router.post("/connect")
def connect_strava(
    code: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Connect Strava account using OAuth code.
    
    Exchanges authorization code for access token and stores credentials.
    """
    try:
        # Exchange code for tokens
        token_data = strava_service.exchange_code_for_token(code)
        
        # Store tokens (encrypted in production!)
        # For now, storing in JSON field in preferences
        if not current_user.preferences:
            current_user.preferences = {}
        
        current_user.preferences['strava'] = {
            'access_token': token_data['access_token'],
            'refresh_token': token_data['refresh_token'],
            'expires_at': token_data['expires_at'],
            'athlete_id': token_data['athlete']['id'],
            'connected_at': str(datetime.utcnow())
        }
        
        db.commit()
        
        return {
            "message": "Strava connected successfully",
            "athlete": {
                "id": token_data['athlete']['id'],
                "firstname": token_data['athlete'].get('firstname'),
                "lastname": token_data['athlete'].get('lastname')
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to connect Strava: {str(e)}"
        )


@router.post("/sync")
def sync_strava_activities(
    after_days: int = Query(default=7, description="Sync activities from last N days"),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Sync activities from Strava.
    
    Downloads recent activities and stores them as workouts.
    """
    try:
        # Check if Strava is connected
        if not current_user.preferences or 'strava' not in current_user.preferences:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Strava not connected. Connect first using /connect endpoint."
            )
        
        strava_data = current_user.preferences['strava']
        access_token = strava_data['access_token']
        
        # Check if token expired and refresh if needed
        expires_at = strava_data['expires_at']
        if expires_at < int(datetime.utcnow().timestamp()):
            # Refresh token
            token_data = strava_service.refresh_access_token(
                strava_data['refresh_token']
            )
            access_token = token_data['access_token']
            
            # Update stored tokens
            current_user.preferences['strava'].update({
                'access_token': token_data['access_token'],
                'refresh_token': token_data['refresh_token'],
                'expires_at': token_data['expires_at']
            })
            db.commit()
        
        # Calculate after_date
        from datetime import timedelta
        after_date = datetime.utcnow() - timedelta(days=after_days)
        
        # Sync activities
        workouts = strava_service.sync_activities(
            db, current_user.id, access_token, after_date
        )
        
        return {
            "message": f"Synced {len(workouts)} activities from Strava",
            "workouts_synced": len(workouts),
            "workout_ids": [w.id for w in workouts]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sync failed: {str(e)}"
        )


@router.get("/status")
def get_strava_status(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get Strava connection status."""
    if not current_user.preferences or 'strava' not in current_user.preferences:
        return {
            "connected": False,
            "athlete": None
        }
    
    strava_data = current_user.preferences['strava']
    
    return {
        "connected": True,
        "athlete": {
            "id": strava_data.get('athlete_id'),
            "connected_at": strava_data.get('connected_at')
        }
    }


@router.delete("/disconnect")
def disconnect_strava(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Disconnect Strava account."""
    if current_user.preferences and 'strava' in current_user.preferences:
        del current_user.preferences['strava']
        db.commit()
    
    return {"message": "Strava disconnected"}
