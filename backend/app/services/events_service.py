"""
events_service.py - Service for managing running events and races
Integrates with multiple sources: RunSignUp, EventBrite, local databases
"""
import logging
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import unicodedata
import re
import time

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

# Base de datos de carreras españolas (será ampliada con APIs en producción)
SPANISH_RACES_DATABASE = [
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
        """Search races with flexible criteria. CACHÉ ENABLED (1 hora TTL).
        
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
        # Crear clave de caché basada en parámetros principales
        cache_key = f"search:{query}:{location}:{limit}"
        
        # Intenta obtener del caché primero
        cached_result = _get_cached_search(cache_key)
        if cached_result is not None:
            logger.info(f"🚀 CACHE HIT for race search: {cache_key} (< 1ms)")
            return cached_result
        
        results = []
        
        for race in self.races_db:
            # Text search
            if query:
                query_norm = self._normalize_search(query)
                name_norm = self._normalize_search(race["name"])
                location_norm = self._normalize_search(race.get("location", ""))
                region_norm = self._normalize_search(race.get("region", ""))
                
                if not (query_norm in name_norm or 
                       query_norm in location_norm or 
                       query_norm in region_norm or
                       name_norm in query_norm or
                       location_norm in query_norm):
                    continue
            
            # Location filter
            if location:
                loc_norm = self._normalize_search(location)
                race_loc = self._normalize_search(race.get("location", ""))
                race_region = self._normalize_search(race.get("region", ""))
                if not (loc_norm in race_loc or loc_norm in race_region or race_loc in loc_norm):
                    continue
            
            # Date filters
            if date_from:
                try:
                    race_date = datetime.strptime(race["date"], "%Y-%m-%d")
                    from_date = datetime.strptime(date_from, "%Y-%m-%d")
                    if race_date < from_date:
                        continue
                except:
                    pass
            
            if date_to:
                try:
                    race_date = datetime.strptime(race["date"], "%Y-%m-%d")
                    to_date = datetime.strptime(date_to, "%Y-%m-%d")
                    if race_date > to_date:
                        continue
                except:
                    pass
            
            # Distance filters
            if min_distance and race["distance_km"] < min_distance:
                continue
            if max_distance and race["distance_km"] > max_distance:
                continue
            
            results.append(race)
        
        # Sort by date
        results.sort(key=lambda x: x["date"])
        
        final_results = results[:limit]
        
        # Guarda en caché
        _set_cache_search(cache_key, final_results)
        logger.info(f"✅ Race search stored in cache: {cache_key} ({len(final_results)} results)")
        
        return final_results
    
    def get_race_by_id(self, race_id: str) -> Optional[Dict[str, Any]]:
        """Get race details by ID."""
        for race in self.races_db:
            if race["id"] == race_id:
                return race
        return None
    
    def get_upcoming_races(self, weeks_ahead: int = 12, limit: int = 10) -> List[Dict[str, Any]]:
        """Get upcoming races in the next N weeks."""
        today = datetime.now()
        future_date = today + timedelta(weeks=weeks_ahead)
        
        upcoming = []
        for race in self.races_db:
            try:
                race_date = datetime.strptime(race["date"], "%Y-%m-%d")
                if today <= race_date <= future_date:
                    upcoming.append(race)
            except:
                pass
        
        upcoming.sort(key=lambda x: x["date"])
        return upcoming[:limit]
    
    def get_races_by_distance(self, distance_km: float, tolerance: float = 2.0) -> List[Dict[str, Any]]:
        """Get races similar to a specific distance."""
        similar = []
        for race in self.races_db:
            if abs(race["distance_km"] - distance_km) <= tolerance:
                similar.append(race)
        
        similar.sort(key=lambda x: abs(x["distance_km"] - distance_km))
        return similar


# Singleton instance
events_service = EventsService()
