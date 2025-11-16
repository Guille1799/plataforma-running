"""
Strava Integration Router
Handles OAuth flow and activity sync
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
import secrets

from app.database import get_db
from app import models, crud
from app.security import verify_token
from app.core.config import settings
from app.services.strava_service import strava_service

router = APIRouter(prefix="/api/v1/strava", tags=["Strava"])
security_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db)
) -> models.User:
    """Extract current user from JWT token."""
    token = credentials.credentials
    payload = verify_token(token, settings.secret_key, settings.algorithm)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    user_id = int(payload.get("sub"))
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user


@router.get("/auth-url")
def get_strava_auth_url(
    user_id: int = Depends(get_current_user)
):
    """
    Get Strava OAuth authorization URL.
    
    Returns URL for user to authorize the app.
    """
    # Generate CSRF token
    state = secrets.token_urlsafe(32)
    
    # TODO: Store state in session or cache with user_id
    # For now, we'll just return the URL
    
    auth_url = strava_service.get_authorization_url(state)
    
    return {
        "auth_url": auth_url,
        "state": state
    }


@router.post("/connect")
def connect_strava(
    code: str,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Connect Strava account using OAuth code.
    
    Exchanges authorization code for access token and stores credentials.
    """
    try:
        # Exchange code for tokens
        token_data = strava_service.exchange_code_for_token(code)
        
        # Update user with Strava credentials
        user = crud.get_user_by_id(db, user_id)
        
        # Store tokens (encrypted in production!)
        # For now, storing in JSON field in preferences
        if not user.preferences:
            user.preferences = {}
        
        user.preferences['strava'] = {
            'access_token': token_data['access_token'],
            'refresh_token': token_data['refresh_token'],
            'expires_at': token_data['expires_at'],
            'athlete_id': token_data['athlete']['id'],
            'connected_at': str(models.datetime.utcnow())
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
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Sync activities from Strava.
    
    Downloads recent activities and stores them as workouts.
    """
    try:
        user = crud.get_user_by_id(db, user_id)
        
        # Check if Strava is connected
        if not user.preferences or 'strava' not in user.preferences:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Strava not connected. Connect first using /connect endpoint."
            )
        
        strava_data = user.preferences['strava']
        access_token = strava_data['access_token']
        
        # Check if token expired and refresh if needed
        expires_at = strava_data['expires_at']
        if expires_at < int(models.datetime.utcnow().timestamp()):
            # Refresh token
            token_data = strava_service.refresh_access_token(
                strava_data['refresh_token']
            )
            access_token = token_data['access_token']
            
            # Update stored tokens
            user.preferences['strava'].update({
                'access_token': token_data['access_token'],
                'refresh_token': token_data['refresh_token'],
                'expires_at': token_data['expires_at']
            })
            db.commit()
        
        # Calculate after_date
        from datetime import datetime, timedelta
        after_date = datetime.utcnow() - timedelta(days=after_days)
        
        # Sync activities
        workouts = strava_service.sync_activities(
            db, user_id, access_token, after_date
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
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get Strava connection status."""
    user = crud.get_user_by_id(db, user_id)
    
    if not user.preferences or 'strava' not in user.preferences:
        return {
            "connected": False,
            "athlete": None
        }
    
    strava_data = user.preferences['strava']
    
    return {
        "connected": True,
        "athlete": {
            "id": strava_data.get('athlete_id'),
            "connected_at": strava_data.get('connected_at')
        }
    }


@router.delete("/disconnect")
def disconnect_strava(
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Disconnect Strava account."""
    user = crud.get_user_by_id(db, user_id)
    
    if user.preferences and 'strava' in user.preferences:
        del user.preferences['strava']
        db.commit()
    
    return {"message": "Strava disconnected"}
