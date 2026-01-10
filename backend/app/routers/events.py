"""
events.py - Endpoints for running events and races
"""

from fastapi import APIRouter, Depends, Query, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional, List
from datetime import datetime

from app import models, schemas
from app import security
from app.database import get_db
from app.services.events_service import EventsService
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/api/v1/events", tags=["Events"])


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
    db: Session = Depends(get_db),
    response: Response = None,
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
        events_service = EventsService(db)
        races = events_service.search_races(
            query=q,
            location=location,
            date_from=date_from,
            date_to=date_to,
            min_distance=min_distance,
            max_distance=max_distance,
            limit=limit,
        )

        # Force no-cache headers
        if response:
            response.headers["Cache-Control"] = (
                "no-cache, no-store, must-revalidate, max-age=0"
            )
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"

        return {"success": True, "count": len(races), "races": races}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching races: {str(e)}",
        )


@router.get("/races/upcoming", response_model=Dict[str, Any])
def get_upcoming_races(
    weeks: int = Query(12, ge=1, le=52, description="Weeks ahead to search"),
    limit: int = Query(10, ge=1, le=100, description="Max results"),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get upcoming races in the next N weeks."""
    try:
        events_service = EventsService(db)
        races = events_service.get_upcoming_races(weeks_ahead=weeks, limit=limit)

        return {"success": True, "count": len(races), "races": races}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting upcoming races: {str(e)}",
        )


@router.get("/races/{race_id}", response_model=Dict[str, Any])
def get_race_detail(
    race_id: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get detailed information about a specific race."""
    try:
        events_service = EventsService(db)
        race = events_service.get_race_by_id(race_id)

        if not race:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Race not found"
            )

        return {"success": True, "race": race}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting race: {str(e)}",
        )


@router.get("/races/by-distance/{distance_km}", response_model=Dict[str, Any])
def get_races_by_distance(
    distance_km: float,
    tolerance: float = Query(
        2.0, ge=0.5, le=10, description="Distance tolerance in km"
    ),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get races similar to a specific distance."""
    try:
        events_service = EventsService(db)
        races = events_service.get_races_by_distance(distance_km, tolerance=tolerance)

        return {
            "success": True,
            "count": len(races),
            "target_distance": distance_km,
            "races": races,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting races by distance: {str(e)}",
        )


# ============================================================================
# ADMIN ENDPOINTS - Event Management (CRUD)
# ============================================================================


@router.post(
    "/admin/races", response_model=schemas.EventOut, status_code=status.HTTP_201_CREATED
)
def create_race(
    event_data: schemas.EventCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new race event (admin only)."""
    security.require_admin(current_user)
    try:
        # Check if external_id already exists
        existing = (
            db.query(models.Event)
            .filter(models.Event.external_id == event_data.external_id)
            .first()
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Event with external_id '{event_data.external_id}' already exists",
            )

        # Create new event
        new_event = models.Event(**event_data.model_dump())

        db.add(new_event)
        db.commit()
        db.refresh(new_event)

        return new_event

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating race: {str(e)}",
        )


@router.get("/admin/races", response_model=List[schemas.EventOut])
def list_all_races(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    verified_only: bool = Query(False),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all races (admin only) - includes past events."""
    security.require_admin(current_user)
    try:
        query = db.query(models.Event)

        if verified_only:
            query = query.filter(models.Event.verified == True)

        events = (
            query.order_by(models.Event.date.desc()).offset(skip).limit(limit).all()
        )

        return events

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing races: {str(e)}",
        )


@router.get("/admin/stats", response_model=Dict[str, Any])
def get_race_stats(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get statistics about races in database (admin only)."""
    security.require_admin(current_user)
    try:
        from datetime import date

        today = date.today()

        total = db.query(models.Event).count()
        verified = db.query(models.Event).filter(models.Event.verified == True).count()
        future = db.query(models.Event).filter(models.Event.date >= today).count()
        past = db.query(models.Event).filter(models.Event.date < today).count()

        # Distance breakdown
        marathons = (
            db.query(models.Event).filter(models.Event.distance_km >= 42).count()
        )
        half_marathons = (
            db.query(models.Event)
            .filter(models.Event.distance_km >= 20, models.Event.distance_km < 30)
            .count()
        )
        ten_k = (
            db.query(models.Event)
            .filter(models.Event.distance_km >= 9, models.Event.distance_km < 12)
            .count()
        )
        five_k = db.query(models.Event).filter(models.Event.distance_km <= 5).count()
        ultras = db.query(models.Event).filter(models.Event.distance_km > 42.5).count()

        # Latest event
        latest_event = db.query(models.Event).order_by(models.Event.date.desc()).first()

        return {
            "success": True,
            "total_events": total,
            "verified_events": verified,
            "future_events": future,
            "past_events": past,
            "by_distance": {
                "marathons_42k": marathons,
                "half_marathons_21k": half_marathons,
                "10k": ten_k,
                "5k": five_k,
                "ultras": ultras,
            },
            "latest_event_date": (
                latest_event.date.strftime("%Y-%m-%d") if latest_event else None
            ),
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting stats: {str(e)}",
        )


@router.put("/admin/races/{race_id}", response_model=schemas.EventOut)
def update_race(
    race_id: int,
    event_update: schemas.EventUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update an existing race event (admin only)."""
    security.require_admin(current_user)
    try:
        # Find the event
        event = db.query(models.Event).filter(models.Event.id == race_id).first()
        
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Race with id {race_id} not found"
            )
        
        # Update only provided fields
        update_data = event_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(event, field, value)
        
        # Update timestamp
        event.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(event)
        
        return event
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating race: {str(e)}",
        )


@router.delete("/admin/races/{race_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_race(
    race_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a race event (admin only)."""
    security.require_admin(current_user)
    try:
        # Find the event
        event = db.query(models.Event).filter(models.Event.id == race_id).first()
        
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Race with id {race_id} not found"
            )
        
        db.delete(event)
        db.commit()
        
        return None
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting race: {str(e)}",
        )
