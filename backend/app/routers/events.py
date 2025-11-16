"""
events.py - Endpoints for running events and races
"""
from fastapi import APIRouter, Depends, Query, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional, List
from datetime import datetime

from app import models, security, schemas
from app.database import get_db
from app.services.events_service import events_service

router = APIRouter(prefix="/api/v1/events", tags=["Events"])
security_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db)
):
    """Get current user from JWT token."""
    try:
        user = security.verify_token(credentials.credentials, db)
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )


@router.get("/races/search", response_model=Dict[str, Any])
def search_races(
    q: Optional[str] = Query(None, description="Search query (name, location)"),
    location: Optional[str] = Query(None, description="Filter by location/region"),
    date_from: Optional[str] = Query(None, description="From date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="To date (YYYY-MM-DD)"),
    min_distance: Optional[float] = Query(None, description="Minimum distance in km"),
    max_distance: Optional[float] = Query(None, description="Maximum distance in km"),
    limit: int = Query(20, ge=1, le=100, description="Max results"),
    current_user: models.User = Depends(get_current_user),
):
    """Search for running races/events.
    
    Supports flexible searching:
    - By name: "Madrid", "10K", "Marathon"
    - By location: "Barcelona", "Andalucia"
    - By date range
    - By distance range
    
    Ignores accents in search.
    """
    try:
        races = events_service.search_races(
            query=q,
            location=location,
            date_from=date_from,
            date_to=date_to,
            min_distance=min_distance,
            max_distance=max_distance,
            limit=limit,
        )
        
        return {
            "success": True,
            "count": len(races),
            "races": races
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching races: {str(e)}"
        )


@router.get("/races/upcoming", response_model=Dict[str, Any])
def get_upcoming_races(
    weeks: int = Query(12, ge=1, le=52, description="Weeks ahead to search"),
    limit: int = Query(10, ge=1, le=100, description="Max results"),
    current_user: models.User = Depends(get_current_user),
):
    """Get upcoming races in the next N weeks."""
    try:
        races = events_service.get_upcoming_races(weeks_ahead=weeks, limit=limit)
        
        return {
            "success": True,
            "count": len(races),
            "races": races
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting upcoming races: {str(e)}"
        )


@router.get("/races/{race_id}", response_model=Dict[str, Any])
def get_race_detail(
    race_id: str,
    current_user: models.User = Depends(get_current_user),
):
    """Get detailed information about a specific race."""
    try:
        race = events_service.get_race_by_id(race_id)
        
        if not race:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Race not found"
            )
        
        return {
            "success": True,
            "race": race
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting race: {str(e)}"
        )


@router.get("/races/by-distance/{distance_km}", response_model=Dict[str, Any])
def get_races_by_distance(
    distance_km: float,
    tolerance: float = Query(2.0, ge=0.5, le=10, description="Distance tolerance in km"),
    current_user: models.User = Depends(get_current_user),
):
    """Get races similar to a specific distance."""
    try:
        races = events_service.get_races_by_distance(distance_km, tolerance=tolerance)
        
        return {
            "success": True,
            "count": len(races),
            "target_distance": distance_km,
            "races": races
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting races: {str(e)}"
        )
