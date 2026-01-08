"""
events_service.py - Service for managing running events and races
Uses PostgreSQL database for persistent storage
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
import unicodedata

from app import models

logger = logging.getLogger(__name__)


class EventsService:
    """Service for managing running events and race searches."""

    def __init__(self, db: Session = None):
        self.db = db

    @staticmethod
    def _remove_accents(text: str) -> str:
        """Remove accents from text for fuzzy matching."""
        nfd = unicodedata.normalize("NFD", text)
        return "".join(char for char in nfd if unicodedata.category(char) != "Mn")

    @staticmethod
    def _normalize_search(text: str) -> str:
        """Normalize search text."""
        text = EventsService._remove_accents(text)
        return text.lower().strip()

    @staticmethod
    def event_to_dict(event: models.Event) -> Dict[str, Any]:
        """Convert Event model to dictionary."""
        return {
            "id": event.external_id,
            "name": event.name,
            "location": event.location,
            "region": event.region,
            "country": event.country,
            "date": event.date.strftime("%Y-%m-%d"),
            "distance_km": event.distance_km,
            "elevation_m": event.elevation_m,
            "participants_estimate": event.participants_estimate,
            "registration_url": event.registration_url,
            "website_url": event.website_url,
            "description": event.description,
            "price_eur": event.price_eur,
            "source": event.source,
        }

    def search_races(
        self,
        query: Optional[str] = None,
        location: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        min_distance: Optional[float] = None,
        max_distance: Optional[float] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Search races with flexible criteria using database.

        Args:
            query: Text search (name, location)
            location: Filter by location/region
            date_from: Filter races from date (YYYY-MM-DD)
            date_to: Filter races until date (YYYY-MM-DD)
            min_distance: Minimum distance in km
            max_distance: Maximum distance in km
            limit: Max results to return

        Returns:
            List of matching races
        """
        if not self.db:
            logger.error("Database session not provided to EventsService")
            return []

        # Start with base query filtering only future races
        today = date.today()
        query_builder = self.db.query(models.Event).filter(
            models.Event.date >= today, models.Event.verified == True
        )

        # Text search - search in name, location, region
        if query:
            query_norm = self._normalize_search(query)
            # Use SQL ILIKE for case-insensitive search
            search_filter = or_(
                func.lower(func.unaccent(models.Event.name)).contains(query_norm),
                func.lower(func.unaccent(models.Event.location)).contains(query_norm),
                func.lower(func.unaccent(models.Event.region)).contains(query_norm),
            )
            query_builder = query_builder.filter(search_filter)

        # Location filter
        if location:
            loc_norm = self._normalize_search(location)
            location_filter = or_(
                func.lower(func.unaccent(models.Event.location)).contains(loc_norm),
                func.lower(func.unaccent(models.Event.region)).contains(loc_norm),
            )
            query_builder = query_builder.filter(location_filter)

        # Date filters
        if date_from:
            try:
                from_date = datetime.strptime(date_from, "%Y-%m-%d").date()
                query_builder = query_builder.filter(models.Event.date >= from_date)
            except ValueError:
                pass

        if date_to:
            try:
                to_date = datetime.strptime(date_to, "%Y-%m-%d").date()
                query_builder = query_builder.filter(models.Event.date <= to_date)
            except ValueError:
                pass

        # Distance filters
        if min_distance:
            query_builder = query_builder.filter(
                models.Event.distance_km >= min_distance
            )
        if max_distance:
            query_builder = query_builder.filter(
                models.Event.distance_km <= max_distance
            )

        # Order by date and apply limit
        events = query_builder.order_by(models.Event.date).limit(limit).all()

        # Convert to dict format
        results = [self.event_to_dict(event) for event in events]

        logger.info(
            f"🔍 Race search: query='{query}', location='{location}', results={len(results)}"
        )
        return results

    def get_race_by_id(self, race_id: str) -> Optional[Dict[str, Any]]:
        """Get race details by external_id."""
        if not self.db:
            return None

        event = (
            self.db.query(models.Event)
            .filter(models.Event.external_id == race_id)
            .first()
        )

        if event:
            return self.event_to_dict(event)
        return None

    def get_upcoming_races(
        self, weeks_ahead: int = 12, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get upcoming races in the next N weeks."""
        if not self.db:
            return []

        today = date.today()
        future_date = today + timedelta(weeks=weeks_ahead)

        events = (
            self.db.query(models.Event)
            .filter(
                and_(
                    models.Event.date >= today,
                    models.Event.date <= future_date,
                    models.Event.verified == True,
                )
            )
            .order_by(models.Event.date)
            .limit(limit)
            .all()
        )

        return [self.event_to_dict(event) for event in events]

    def get_races_by_distance(
        self, distance_km: float, tolerance: float = 2.0
    ) -> List[Dict[str, Any]]:
        """Get races similar to a specific distance."""
        if not self.db:
            return []

        today = date.today()
        min_dist = distance_km - tolerance
        max_dist = distance_km + tolerance

        events = (
            self.db.query(models.Event)
            .filter(
                and_(
                    models.Event.date >= today,
                    models.Event.distance_km >= min_dist,
                    models.Event.distance_km <= max_dist,
                    models.Event.verified == True,
                )
            )
            .order_by(models.Event.date)
            .all()
        )

        return [self.event_to_dict(event) for event in events]
