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


import logging as _logging
_router_logger = _logging.getLogger(__name__)


def _garmin_http_error(exc: Exception, operation: str) -> HTTPException:
    """Map Garmin/garth exceptions to appropriate HTTP status codes."""
    # Use repr() as fallback so we always have something human-readable
    exc_str = str(exc) or repr(exc) or exc.__class__.__name__
    msg = exc_str.lower()

    _router_logger.error(
        "Garmin %s error: %s (%s)", operation, exc_str, exc.__class__.__name__,
        exc_info=True,
    )

    if "429" in msg or "too many requests" in msg or "rate limit" in msg:
        return HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Garmin is rate-limiting requests. Wait a few minutes and try again.",
        )
    if "401" in msg or "unauthorized" in msg or "invalid credentials" in msg:
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Garmin credentials. Reconnect your account.",
        )
    if "not connected" in msg:
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Garmin account not connected. Connect your account first.",
        )
    if "login" in msg or "sso" in msg or "signon" in msg or "authentication" in msg:
        return HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=(
                "Garmin login failed — this is usually a temporary rate-limit. "
                "Wait 10–15 minutes and try again."
            ),
        )
    if "timeout" in msg or "timed out" in msg:
        return HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Garmin request timed out. Try again in a moment.",
        )
    # Generic fallback — always include the class name so it's not empty
    detail = f"Garmin {operation} failed: {exc_str}" if exc_str else f"Garmin {operation} failed (unknown error: {exc.__class__.__name__})"
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


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
        raise _garmin_http_error(e, "connect")


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
        raise _garmin_http_error(e, "sync")


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
