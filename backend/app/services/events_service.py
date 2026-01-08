"""
events_service.py - Service for managing running events and races
Now uses PostgreSQL database instead of hardcoded data
"""
import logging
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
import unicodedata
import re
import time

from app import models

logger = logging.getLogger(__name__)

# Caché para búsquedas de carreras (TTL 1 hora)
_search_cache = {}
_cache_timestamps = {}

def _get_cached_search(query: str) -> Optional[List[Dict]]:
    """Obtiene resultado del caché si existe y no ha expirado (1 hora)"""
    now = time.time()
    if query in _search_cache:
        if now - _cache_timestamps[query] < 3600:  # 3600 segundos = 1 hora
            logger.debug(f"Cache HIT for race search: {query}")
            return _search_cache[query]
        else:
            # Caché expirado, elimina
            del _search_cache[query]
            del _cache_timestamps[query]
    return None

def _set_cache_search(query: str, results: List[Dict]):
    """Guarda resultado en caché con timestamp"""
    _search_cache[query] = results
    _cache_timestamps[query] = time.time()
    logger.debug(f"Cache SET for race search: {query} ({len(results)} results)")


class EventsService:
    """Service for managing running events and race searches."""
    
    def __init__(self, db: Session = None):
        self.db = db
    
    @staticmethod
    def _remove_accents(text: str) -> str:
        """Remove accents from text for fuzzy matching."""
        nfd = unicodedata.normalize('NFD', text)
        return ''.join(char for char in nfd if unicodedata.category(char) != 'Mn')
    
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
    # 2025 Q1
    {
        "id": "marbcn2025",
        "name": "Marató de Barcelona",
        "location": "Barcelona",
        "region": "Cataluña",
        "country": "España",
        "date": "2025-03-09",
        "distance_km": 42.195,
        "elevation_m": 120,
        "participants_estimate": 15000,
        "source": "official",
    },
    {
        "id": "marval2025",
        "name": "Media Maratón de Valencia",
        "location": "Valencia",
        "region": "Valencia",
        "country": "España",
        "date": "2025-05-18",
        "distance_km": 21.0975,
        "elevation_m": 15,
        "participants_estimate": 8000,
        "source": "official",
    },
    {
        "id": "mar_madrid2025",
        "name": "Maratón de Madrid",
        "location": "Madrid",
        "region": "Madrid",
        "country": "España",
        "date": "2025-04-13",
        "distance_km": 42.195,
        "elevation_m": 200,
        "participants_estimate": 20000,
        "source": "official",
    },
    {
        "id": "10k_madrid2025",
        "name": "10K San Silvestre Vallecana",
        "location": "Madrid",
        "region": "Madrid",
        "country": "España",
        "date": "2025-12-31",
        "distance_km": 10,
        "elevation_m": 50,
        "participants_estimate": 30000,
        "source": "official",
    },
    {
        "id": "marbil2025",
        "name": "Maratón de Málaga",
        "location": "Málaga",
        "region": "Andalucía",
        "country": "España",
        "date": "2025-11-23",
        "distance_km": 42.195,
        "elevation_m": 100,
        "participants_estimate": 5000,
        "source": "official",
    },
    # 2025 Q2-Q3
    {
        "id": "half_seville2025",
        "name": "Media Maratón de Sevilla",
        "location": "Sevilla",
        "region": "Andalucía",
        "country": "España",
        "date": "2025-02-23",
        "distance_km": 21.0975,
        "elevation_m": 30,
        "participants_estimate": 6000,
        "source": "official",
    },
    {
        "id": "5k_valencia2025",
        "name": "5K Popular de Valencia",
        "location": "Valencia",
        "region": "Valencia",
        "country": "España",
        "date": "2025-06-15",
        "distance_km": 5,
        "elevation_m": 5,
        "participants_estimate": 2000,
        "source": "official",
    },
    {
        "id": "ultracatal2025",
        "name": "Ultra Trail Costa Brava",
        "location": "Girona",
        "region": "Cataluña",
        "country": "España",
        "date": "2025-09-21",
        "distance_km": 65,
        "elevation_m": 3500,
        "participants_estimate": 1500,
        "source": "official",
    },
    {
        "id": "half_bilbao2025",
        "name": "Half Marathon Bilbao",
        "location": "Bilbao",
        "region": "País Vasco",
        "country": "España",
        "date": "2025-10-12",
        "distance_km": 21.0975,
        "elevation_m": 100,
        "participants_estimate": 4000,
        "source": "official",
    },
    {
        "id": "10k_barcelona2025",
        "name": "10K Urbain Barcelona",
        "location": "Barcelona",
        "region": "Cataluña",
        "country": "España",
        "date": "2025-07-20",
        "distance_km": 10,
        "elevation_m": 150,
        "participants_estimate": 3000,
        "source": "official",
    },
    # 2025 Q4
    {
        "id": "mar_valencia2025",
        "name": "Maratón de Valencia",
        "location": "Valencia",
        "region": "Valencia",
        "country": "España",
        "date": "2025-11-30",
        "distance_km": 42.195,
        "elevation_m": 10,
        "participants_estimate": 12000,
        "source": "official",
    },
    {
        "id": "marbcn_half2025",
        "name": "Half Marathon Barcelona",
        "location": "Barcelona",
        "region": "Cataluña",
        "country": "España",
        "date": "2025-08-31",
        "distance_km": 21.0975,
        "elevation_m": 80,
        "participants_estimate": 7000,
        "source": "official",
    },
    {
        "id": "mar_malaga2025_dec",
        "name": "Maratón de Málaga - Diciembre",
        "location": "Málaga",
        "region": "Andalucía",
        "country": "España",
        "date": "2025-12-07",
        "distance_km": 42.195,
        "elevation_m": 100,
        "participants_estimate": 5000,
        "source": "official",
    },
    {
        "id": "10k_madrid_dec2025",
        "name": "10K San Silvestre Vallecana",
        "location": "Madrid",
        "region": "Madrid",
        "country": "España",
        "date": "2025-12-31",
        "distance_km": 10,
        "elevation_m": 50,
        "participants_estimate": 30000,
        "source": "official",
    },
    {
        "id": "half_barcelona_dec2025",
        "name": "Media Maratón de Barcelona - Navidad",
        "location": "Barcelona",
        "region": "Cataluña",
        "country": "España",
        "date": "2025-12-21",
        "distance_km": 21.0975,
        "elevation_m": 120,
        "participants_estimate": 4000,
        "source": "official",
    },
    {
        "id": "trail_valencia_dec2025",
        "name": "Trail Nocturno Valencia",
        "location": "Valencia",
        "region": "Valencia",
        "country": "España",
        "date": "2025-12-13",
        "distance_km": 15,
        "elevation_m": 300,
        "participants_estimate": 2000,
        "source": "official",
    },
    {
        "id": "5k_seville_dec2025",
        "name": "5K Popular Sevilla - Diciembre",
        "location": "Sevilla",
        "region": "Andalucía",
        "country": "España",
        "date": "2025-12-06",
        "distance_km": 5,
        "elevation_m": 10,
        "participants_estimate": 1500,
        "source": "official",
    },
    # Andalucía - Expanded
    {
        "id": "half_dos_hermanas2025",
        "name": "Media Maratón de Dos Hermanas",
        "location": "Dos Hermanas",
        "region": "Andalucía",
        "country": "España",
        "date": "2025-03-23",
        "distance_km": 21.0975,
        "elevation_m": 25,
        "participants_estimate": 3500,
        "source": "official",
    },
    {
        "id": "5k_dos_hermanas2025",
        "name": "5K Popular Dos Hermanas",
        "location": "Dos Hermanas",
        "region": "Andalucía",
        "country": "España",
        "date": "2025-04-27",
        "distance_km": 5,
        "elevation_m": 10,
        "participants_estimate": 1200,
        "source": "official",
    },
    {
        "id": "mar_cordoba2025",
        "name": "Maratón de Córdoba",
        "location": "Córdoba",
        "region": "Andalucía",
        "country": "España",
        "date": "2025-05-04",
        "distance_km": 42.195,
        "elevation_m": 120,
        "participants_estimate": 2500,
        "source": "official",
    },
    {
        "id": "10k_cordoba2025",
        "name": "10K Popular Córdoba",
        "location": "Córdoba",
        "region": "Andalucía",
        "country": "España",
        "date": "2025-06-08",
        "distance_km": 10,
        "elevation_m": 50,
        "participants_estimate": 1800,
        "source": "official",
    },
    {
        "id": "half_jaen2025",
        "name": "Media Maratón de Jaén",
        "location": "Jaén",
        "region": "Andalucía",
        "country": "España",
        "date": "2025-04-13",
        "distance_km": 21.0975,
        "elevation_m": 80,
        "participants_estimate": 2000,
        "source": "official",
    },
    {
        "id": "mar_almeria2025",
        "name": "Maratón de Almería",
        "location": "Almería",
        "region": "Andalucía",
        "country": "España",
        "date": "2025-06-22",
        "distance_km": 42.195,
        "elevation_m": 50,
        "participants_estimate": 1500,
        "source": "official",
    },
    {
        "id": "half_almeria2025",
        "name": "Media Maratón de Almería",
        "location": "Almería",
        "region": "Andalucía",
        "country": "España",
        "date": "2025-07-13",
        "distance_km": 21.0975,
        "elevation_m": 30,
        "participants_estimate": 1200,
        "source": "official",
    },
    {
        "id": "5k_malaga2025",
        "name": "5K Popular Málaga",
        "location": "Málaga",
        "region": "Andalucía",
        "country": "España",
        "date": "2025-08-17",
        "distance_km": 5,
        "elevation_m": 20,
        "participants_estimate": 2000,
        "source": "official",
    },
    {
        "id": "10k_sevilla2025",
        "name": "10K Urbana Sevilla",
        "location": "Sevilla",
        "region": "Andalucía",
        "country": "España",
        "date": "2025-09-07",
        "distance_km": 10,
        "elevation_m": 40,
        "participants_estimate": 3000,
        "source": "official",
    },
    {
        "id": "trail_granada2025",
        "name": "Trail de Sierra Nevada",
        "location": "Granada",
        "region": "Andalucía",
        "country": "España",
        "date": "2025-05-18",
        "distance_km": 25,
        "elevation_m": 1200,
        "participants_estimate": 800,
        "source": "official",
    },
    {
        "id": "half_granada2025",
        "name": "Media Maratón de Granada",
        "location": "Granada",
        "region": "Andalucía",
        "country": "España",
        "date": "2025-07-27",
        "distance_km": 21.0975,
        "elevation_m": 100,
        "participants_estimate": 2200,
        "source": "official",
    },
    # Más España
    {
        "id": "10k_girona2025",
        "name": "10K Popular Girona",
        "location": "Girona",
        "region": "Cataluña",
        "country": "España",
        "date": "2025-05-25",
        "distance_km": 10,
        "elevation_m": 80,
        "participants_estimate": 1500,
        "source": "official",
    },
    {
        "id": "half_zaragoza2025",
        "name": "Media Maratón de Zaragoza",
        "location": "Zaragoza",
        "region": "Aragón",
        "country": "España",
        "date": "2025-04-20",
        "distance_km": 21.0975,
        "elevation_m": 40,
        "participants_estimate": 2500,
        "source": "official",
    },
    {
        "id": "mar_oviedo2025",
        "name": "Maratón de Oviedo",
        "location": "Oviedo",
        "region": "Asturias",
        "country": "España",
        "date": "2025-06-29",
        "distance_km": 42.195,
        "elevation_m": 200,
        "participants_estimate": 2000,
        "source": "official",
    },
    {
        "id": "10k_murcia2025",
        "name": "10K Popular Murcia",
        "location": "Murcia",
        "region": "Murcia",
        "country": "España",
        "date": "2025-05-11",
        "distance_km": 10,
        "elevation_m": 30,
        "participants_estimate": 1800,
        "source": "official",
    },
    # ===== 2026 CARRERAS NACIONALES =====
    # 2026 Enero-Febrero
    {
        "id": "marbcn2026",
        "name": "Marató de Barcelona 2026",
        "location": "Barcelona",
        "region": "Cataluña",
        "country": "España",
        "date": "2026-03-08",
        "distance_km": 42.195,
        "elevation_m": 120,
        "participants_estimate": 15000,
        "source": "official",
    },
    {
        "id": "mar_madrid2026",
        "name": "Maratón de Madrid 2026",
        "location": "Madrid",
        "region": "Madrid",
        "country": "España",
        "date": "2026-04-12",
        "distance_km": 42.195,
        "elevation_m": 200,
        "participants_estimate": 20000,
        "source": "official",
    },
    {
        "id": "half_seville2026",
        "name": "Media Maratón de Sevilla 2026",
        "location": "Sevilla",
        "region": "Andalucía",
        "country": "España",
        "date": "2026-02-22",
        "distance_km": 21.0975,
        "elevation_m": 30,
        "participants_estimate": 6000,
        "source": "official",
    },
    {
        "id": "half_dos_hermanas2026",
        "name": "Media Maratón de Dos Hermanas 2026",
        "location": "Dos Hermanas",
        "region": "Andalucía",
        "country": "España",
        "date": "2026-03-22",
        "distance_km": 21.0975,
        "elevation_m": 25,
        "participants_estimate": 3500,
        "source": "official",
    },
    # 2026 Marzo-Abril
    {
        "id": "half_zaragoza2026",
        "name": "Media Maratón de Zaragoza 2026",
        "location": "Zaragoza",
        "region": "Aragón",
        "country": "España",
        "date": "2026-04-19",
        "distance_km": 21.0975,
        "elevation_m": 40,
        "participants_estimate": 2500,
        "source": "official",
    },
    {
        "id": "5k_valencia2026",
        "name": "5K Popular de Valencia 2026",
        "location": "Valencia",
        "region": "Valencia",
        "country": "España",
        "date": "2026-05-10",
        "distance_km": 5,
        "elevation_m": 5,
        "participants_estimate": 2000,
        "source": "official",
    },
    {
        "id": "half_bilbao2026",
        "name": "Half Marathon Bilbao 2026",
        "location": "Bilbao",
        "region": "País Vasco",
        "country": "España",
        "date": "2026-05-17",
        "distance_km": 21.0975,
        "elevation_m": 100,
        "participants_estimate": 4000,
        "source": "official",
    },
    # 2026 Mayo-Junio
    {
        "id": "mar_cordoba2026",
        "name": "Maratón de Córdoba 2026",
        "location": "Córdoba",
        "region": "Andalucía",
        "country": "España",
        "date": "2026-05-03",
        "distance_km": 42.195,
        "elevation_m": 120,
        "participants_estimate": 2500,
        "source": "official",
    },
    {
        "id": "trail_granada2026",
        "name": "Trail de Sierra Nevada 2026",
        "location": "Granada",
        "region": "Andalucía",
        "country": "España",
        "date": "2026-05-17",
        "distance_km": 25,
        "elevation_m": 1200,
        "participants_estimate": 800,
        "source": "official",
    },
    {
        "id": "mar_oviedo2026",
        "name": "Maratón de Oviedo 2026",
        "location": "Oviedo",
        "region": "Asturias",
        "country": "España",
        "date": "2026-06-28",
        "distance_km": 42.195,
        "elevation_m": 200,
        "participants_estimate": 2000,
        "source": "official",
    },
    {
        "id": "mar_almeria2026",
        "name": "Maratón de Almería 2026",
        "location": "Almería",
        "region": "Andalucía",
        "country": "España",
        "date": "2026-06-21",
        "distance_km": 42.195,
        "elevation_m": 50,
        "participants_estimate": 1500,
        "source": "official",
    },
    # 2026 Julio-Agosto
    {
        "id": "10k_barcelona2026",
        "name": "10K Urbain Barcelona 2026",
        "location": "Barcelona",
        "region": "Cataluña",
        "country": "España",
        "date": "2026-07-19",
        "distance_km": 10,
        "elevation_m": 150,
        "participants_estimate": 3000,
        "source": "official",
    },
    {
        "id": "half_granada2026",
        "name": "Media Maratón de Granada 2026",
        "location": "Granada",
        "region": "Andalucía",
        "country": "España",
        "date": "2026-07-26",
        "distance_km": 21.0975,
        "elevation_m": 100,
        "participants_estimate": 2200,
        "source": "official",
    },
    {
        "id": "marbcn_half2026",
        "name": "Half Marathon Barcelona 2026",
        "location": "Barcelona",
        "region": "Cataluña",
        "country": "España",
        "date": "2026-08-30",
        "distance_km": 21.0975,
        "elevation_m": 80,
        "participants_estimate": 7000,
        "source": "official",
    },
    # 2026 Septiembre-Octubre
    {
        "id": "ultracatal2026",
        "name": "Ultra Trail Costa Brava 2026",
        "location": "Girona",
        "region": "Cataluña",
        "country": "España",
        "date": "2026-09-20",
        "distance_km": 65,
        "elevation_m": 3500,
        "participants_estimate": 1500,
        "source": "official",
    },
    {
        "id": "10k_sevilla2026",
        "name": "10K Urbana Sevilla 2026",
        "location": "Sevilla",
        "region": "Andalucía",
        "country": "España",
        "date": "2026-09-06",
        "distance_km": 10,
        "elevation_m": 40,
        "participants_estimate": 3000,
        "source": "official",
    },
    {
        "id": "half_jaen2026",
        "name": "Media Maratón de Jaén 2026",
        "location": "Jaén",
        "region": "Andalucía",
        "country": "España",
        "date": "2026-04-12",
        "distance_km": 21.0975,
        "elevation_m": 80,
        "participants_estimate": 2000,
        "source": "official",
    },
    # 2026 Noviembre-Diciembre
    {
        "id": "mar_malaga2026",
        "name": "Maratón de Málaga 2026",
        "location": "Málaga",
        "region": "Andalucía",
        "country": "España",
        "date": "2026-11-22",
        "distance_km": 42.195,
        "elevation_m": 100,
        "participants_estimate": 5000,
        "source": "official",
    },
    {
        "id": "mar_valencia2026",
        "name": "Maratón de Valencia 2026",
        "location": "Valencia",
        "region": "Valencia",
        "country": "España",
        "date": "2026-11-29",
        "distance_km": 42.195,
        "elevation_m": 10,
        "participants_estimate": 12000,
        "source": "official",
    },
    {
        "id": "10k_madrid2026",
        "name": "10K San Silvestre Vallecana 2026",
        "location": "Madrid",
        "region": "Madrid",
        "country": "España",
        "date": "2026-12-31",
        "distance_km": 10,
        "elevation_m": 50,
        "participants_estimate": 30000,
        "source": "official",
    },
]


class EventsService:
    """Service for managing running events and race searches."""
    
    def __init__(self):
        self.races_db = SPANISH_RACES_DATABASE
        self.last_update = datetime.now()
    
    @staticmethod
    def _remove_accents(text: str) -> str:
        """Remove accents from text for fuzzy matching."""
        nfd = unicodedata.normalize('NFD', text)
        return ''.join(char for char in nfd if unicodedata.category(char) != 'Mn')
    
    @staticmethod
    def _normalize_search(text: str) -> str:
        """Normalize search text."""
        text = EventsService._remove_accents(text)
        return text.lower().strip()
    
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
            models.Event.date >= today,
            models.Event.verified == True
        )
        
        # Text search - search in name, location, region
        if query:
            query_norm = self._normalize_search(query)
            # Use SQL ILIKE for case-insensitive search
            search_filter = or_(
                func.lower(func.unaccent(models.Event.name)).contains(query_norm),
                func.lower(func.unaccent(models.Event.location)).contains(query_norm),
                func.lower(func.unaccent(models.Event.region)).contains(query_norm)
            )
            query_builder = query_builder.filter(search_filter)
        
        # Location filter
        if location:
            loc_norm = self._normalize_search(location)
            location_filter = or_(
                func.lower(func.unaccent(models.Event.location)).contains(loc_norm),
                func.lower(func.unaccent(models.Event.region)).contains(loc_norm)
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
            query_builder = query_builder.filter(models.Event.distance_km >= min_distance)
        if max_distance:
            query_builder = query_builder.filter(models.Event.distance_km <= max_distance)
        
        # Order by date and apply limit
        events = query_builder.order_by(models.Event.date).limit(limit).all()
        
        # Convert to dict format
        results = [self.event_to_dict(event) for event in events]
        
        logger.info(f"🔍 Race search: query='{query}', location='{location}', results={len(results)}")
        return results
    
    def get_race_by_id(self, race_id: str) -> Optional[Dict[str, Any]]:
        """Get race details by external_id."""
        if not self.db:
            return None
        
        event = self.db.query(models.Event).filter(
            models.Event.external_id == race_id
        ).first()
        
        if event:
            return self.event_to_dict(event)
        return None
    
    def get_upcoming_races(self, weeks_ahead: int = 12, limit: int = 10) -> List[Dict[str, Any]]:
        """Get upcoming races in the next N weeks."""
        if not self.db:
            return []
        
        today = date.today()
        future_date = today + timedelta(weeks=weeks_ahead)
        
        events = self.db.query(models.Event).filter(
            and_(
                models.Event.date >= today,
                models.Event.date <= future_date,
                models.Event.verified == True
            )
        ).order_by(models.Event.date).limit(limit).all()
        
        return [self.event_to_dict(event) for event in events]
    
    def get_races_by_distance(self, distance_km: float, tolerance: float = 2.0) -> List[Dict[str, Any]]:
        """Get races similar to a specific distance."""
        if not self.db:
            return []
        
        today = date.today()
        min_dist = distance_km - tolerance
        max_dist = distance_km + tolerance
        
        events = self.db.query(models.Event).filter(
            and_(
                models.Event.date >= today,
                models.Event.distance_km >= min_dist,
                models.Event.distance_km <= max_dist,
                models.Event.verified == True
            )
        ).order_by(models.Event.date).all()
        
        return [self.event_to_dict(event) for event in events]


# DO NOT create singleton - service requires DB session
# Use EventsService(db) in routes instead
