"""
Garmin Connect integration endpoints.
"""
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from ..database import get_db
from ..services import garmin_service
from .. import models
from ..dependencies.auth import get_current_user


router = APIRouter(prefix="/api/v1/garmin")


class GarminConnectRequest(BaseModel):
    """Request to connect Garmin account."""
    email: EmailStr
    password: str


class GarminSyncRequest(BaseModel):
    """Request to sync Garmin activities."""
    start_date: Optional[str] = None  # ISO format YYYY-MM-DD
    end_date: Optional[str] = None


class GarminStatusResponse(BaseModel):
    """Garmin connection status."""
    connected: bool
    garmin_email: Optional[str] = None
    connected_at: Optional[str] = None
    last_sync: Optional[str] = None


@router.post("/connect", status_code=200)
def connect_garmin(
    request: GarminConnectRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Connect user's Garmin account.
    
    Saves encrypted Garmin credentials for future syncs.
    """
    try:
        user = garmin_service.connect_user_garmin(
            db,
            current_user.id,
            request.email,
            request.password
        )
        
        return {
            "message": "Garmin account connected successfully",
            "garmin_email": user.garmin_email,
            "connected_at": user.garmin_connected_at.isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to connect Garmin: {str(e)}"
        )


@router.post("/sync", status_code=200)
def sync_activities(
    request: Optional[GarminSyncRequest] = None,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Sync activities from Garmin Connect.
    
    Downloads and processes FIT files for running activities.
    """
    try:
        # Parse dates (handle None request or empty values)
        start_date = None
        end_date = None
        
        if request and request.start_date:
            try:
                start_date = date.fromisoformat(request.start_date)
            except ValueError:
                pass
                
        if request and request.end_date:
            try:
                end_date = date.fromisoformat(request.end_date)
            except ValueError:
                pass
        
        # Sync
        workouts = garmin_service.sync_user_activities(
            db,
            current_user.id,
            start_date,
            end_date
        )
        
        # Update last sync time
        from datetime import datetime
        if current_user and len(workouts) > 0:  # Only update if sync was successful (workouts synced)
            current_user.last_garmin_sync = datetime.utcnow()
            db.commit()
        
        return {
            "message": f"Synced {len(workouts)} activities",
            "workouts_synced": len(workouts),
            "activity_ids": [w.id for w in workouts]
        }
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Garmin sync failed for user {current_user.id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Sync failed: {str(e)}"
        )


@router.get("/status", response_model=GarminStatusResponse)
def get_garmin_status(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get Garmin connection status for current user."""
    return {
        "connected": bool(current_user.garmin_token),
        "garmin_email": current_user.garmin_email,
        "connected_at": current_user.garmin_connected_at.isoformat() if current_user.garmin_connected_at else None,
        "last_sync": current_user.last_garmin_sync.isoformat() if current_user.last_garmin_sync else None
    }


@router.delete("/disconnect", status_code=200)
def disconnect_garmin(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Disconnect Garmin account."""
    current_user.garmin_email = None
    current_user.garmin_token = None
    current_user.garmin_connected_at = None
    
    db.commit()
    
    return {"message": "Garmin account disconnected"}
