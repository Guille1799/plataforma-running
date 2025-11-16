"""
Garmin Connect integration endpoints.
"""
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from ..database import get_db
from ..services import garmin_service
from .. import security
from ..core.config import settings


router = APIRouter(prefix="/api/v1/garmin")
security_scheme = HTTPBearer()


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


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db)
) -> int:
    """Extract user ID from JWT token."""
    token = credentials.credentials
    payload = security.verify_token(token, settings.secret_key, settings.algorithm)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    return int(payload.get('sub'))


@router.post("/connect", status_code=200)
def connect_garmin(
    request: GarminConnectRequest,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Connect user's Garmin account.
    
    Saves encrypted Garmin credentials for future syncs.
    """
    try:
        user = garmin_service.connect_user_garmin(
            db,
            user_id,
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
    user_id: int = Depends(get_current_user),
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
            user_id,
            start_date,
            end_date
        )
        
        return {
            "message": f"Synced {len(workouts)} activities",
            "workouts_synced": len(workouts),
            "activity_ids": [w.id for w in workouts]
        }
    except Exception as e:
        import traceback
        print(f"[SYNC ERROR] {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Sync failed: {str(e)}"
        )


@router.get("/status", response_model=GarminStatusResponse)
def get_garmin_status(
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get Garmin connection status for current user."""
    from .. import crud
    
    user = crud.get_user_by_id(db, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "connected": bool(user.garmin_token),
        "garmin_email": user.garmin_email,
        "connected_at": user.garmin_connected_at.isoformat() if user.garmin_connected_at else None,
        "last_sync": None  # TODO: Track last sync time
    }


@router.delete("/disconnect", status_code=200)
def disconnect_garmin(
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Disconnect Garmin account."""
    from .. import crud
    
    user = crud.get_user_by_id(db, user_id)
    
    user.garmin_email = None
    user.garmin_token = None
    user.garmin_connected_at = None
    
    db.commit()
    
    return {"message": "Garmin account disconnected"}
