"""
seed_events.py - Seed initial racing events to database
Run: python seed_events.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.database import SessionLocal
from app.models import Event
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 52 Spanish running events
EVENTS_DATA = [
    # 2026 Events (Future races)
    {
        "external_id": "marbcn2026",
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
        "external_id": "mar_madrid2026",
        "name": "Maratón de Madrid 2026",
        "location": "Madrid",
        "region": "Madrid",
        "country": "España",
        "date": "2026-04-26",
        "distance_km": 42.195,
        "elevation_m": 200,
        "participants_estimate": 20000,
        "source": "official",
    },
    {
        "external_id": "half_seville2026",
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
        "external_id": "half_dos_hermanas2026",
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
    {
        "external_id": "half_zaragoza2026",
        "name": "Media Maratón de Zaragoza 2026",
        "location": "Zaragoza",
        "region": "Aragón",
        "country": "España",
        "date": "2026-04-19",
        "distance_km": 21.0975,
        "elevation_m": 40,
        "participants_estimate": 5000,
        "source": "official",
    },
    {
        "external_id": "5k_valencia2026",
        "name": "5K Popular de Valencia 2026",
        "location": "Valencia",
        "region": "Valencia",
        "country": "España",
        "date": "2026-06-14",
        "distance_km": 5,
        "elevation_m": 5,
        "participants_estimate": 2000,
        "source": "official",
    },
    {
        "external_id": "half_bilbao2026",
        "name": "Half Marathon Bilbao 2026",
        "location": "Bilbao",
        "region": "País Vasco",
        "country": "España",
        "date": "2026-06-28",
        "distance_km": 21.0975,
        "elevation_m": 100,
        "participants_estimate": 4000,
        "source": "official",
    },
    {
        "external_id": "mar_cordoba2026",
        "name": "Maratón de Córdoba 2026",
        "location": "Córdoba",
        "region": "Andalucía",
        "country": "España",
        "date": "2026-05-10",
        "distance_km": 42.195,
        "elevation_m": 120,
        "participants_estimate": 2500,
        "source": "official",
    },
    {
        "external_id": "trail_granada2026",
        "name": "Trail de Sierra Nevada 2026",
        "location": "Granada",
        "region": "Andalucía",
        "country": "España",
        "date": "2026-07-05",
        "distance_km": 30,
        "elevation_m": 1500,
        "participants_estimate": 800,
        "source": "official",
    },
    {
        "external_id": "mar_oviedo2026",
        "name": "Maratón de Oviedo 2026",
        "location": "Oviedo",
        "region": "Asturias",
        "country": "España",
        "date": "2026-06-21",
        "distance_km": 42.195,
        "elevation_m": 250,
        "participants_estimate": 1500,
        "source": "official",
    },
    {
        "external_id": "mar_almeria2026",
        "name": "Maratón de Almería 2026",
        "location": "Almería",
        "region": "Andalucía",
        "country": "España",
        "date": "2026-07-19",
        "distance_km": 42.195,
        "elevation_m": 50,
        "participants_estimate": 1500,
        "source": "official",
    },
    {
        "external_id": "10k_barcelona2026",
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
        "external_id": "half_granada2026",
        "name": "Media Maratón de Granada 2026",
        "location": "Granada",
        "region": "Andalucía",
        "country": "España",
        "date": "2026-08-09",
        "distance_km": 21.0975,
        "elevation_m": 200,
        "participants_estimate": 3000,
        "source": "official",
    },
    {
        "external_id": "marbcn_half2026",
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
    {
        "external_id": "ultracatal2026",
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
        "external_id": "10k_sevilla2026",
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
        "external_id": "half_jaen2026",
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
    {
        "external_id": "mar_malaga2026",
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
        "external_id": "mar_valencia2026",
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
        "external_id": "10k_madrid2026",
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
    # 2027 Events (Extended future)
    {
        "external_id": "marbcn2027",
        "name": "Marató de Barcelona 2027",
        "location": "Barcelona",
        "region": "Cataluña",
        "country": "España",
        "date": "2027-03-14",
        "distance_km": 42.195,
        "elevation_m": 120,
        "participants_estimate": 15000,
        "source": "official",
    },
    {
        "external_id": "half_seville2027",
        "name": "Media Maratón de Sevilla 2027",
        "location": "Sevilla",
        "region": "Andalucía",
        "country": "España",
        "date": "2027-02-21",
        "distance_km": 21.0975,
        "elevation_m": 30,
        "participants_estimate": 6000,
        "source": "official",
    },
    {
        "external_id": "mar_madrid2027",
        "name": "Maratón de Madrid 2027",
        "location": "Madrid",
        "region": "Madrid",
        "country": "España",
        "date": "2027-04-25",
        "distance_km": 42.195,
        "elevation_m": 200,
        "participants_estimate": 20000,
        "source": "official",
    },
    {
        "external_id": "half_dos_hermanas2027",
        "name": "Media Maratón de Dos Hermanas 2027",
        "location": "Dos Hermanas",
        "region": "Andalucía",
        "country": "España",
        "date": "2027-03-21",
        "distance_km": 21.0975,
        "elevation_m": 25,
        "participants_estimate": 3500,
        "source": "official",
    },
    {
        "external_id": "10k_cordoba2027",
        "name": "10K Popular Córdoba 2027",
        "location": "Córdoba",
        "region": "Andalucía",
        "country": "España",
        "date": "2027-06-06",
        "distance_km": 10,
        "elevation_m": 50,
        "participants_estimate": 1800,
        "source": "official",
    },
    {
        "external_id": "5k_valencia2027",
        "name": "5K Popular de Valencia 2027",
        "location": "Valencia",
        "region": "Valencia",
        "country": "España",
        "date": "2027-06-13",
        "distance_km": 5,
        "elevation_m": 5,
        "participants_estimate": 2000,
        "source": "official",
    },
    {
        "external_id": "half_bilbao2027",
        "name": "Half Marathon Bilbao 2027",
        "location": "Bilbao",
        "region": "País Vasco",
        "country": "España",
        "date": "2027-06-27",
        "distance_km": 21.0975,
        "elevation_m": 100,
        "participants_estimate": 4000,
        "source": "official",
    },
    {
        "external_id": "mar_almeria2027",
        "name": "Maratón de Almería 2027",
        "location": "Almería",
        "region": "Andalucía",
        "country": "España",
        "date": "2027-06-20",
        "distance_km": 42.195,
        "elevation_m": 50,
        "participants_estimate": 1500,
        "source": "official",
    },
    {
        "external_id": "10k_barcelona2027",
        "name": "10K Urbain Barcelona 2027",
        "location": "Barcelona",
        "region": "Cataluña",
        "country": "España",
        "date": "2027-07-18",
        "distance_km": 10,
        "elevation_m": 150,
        "participants_estimate": 3000,
        "source": "official",
    },
    {
        "external_id": "trail_granada2027",
        "name": "Trail de Sierra Nevada 2027",
        "location": "Granada",
        "region": "Andalucía",
        "country": "España",
        "date": "2027-07-04",
        "distance_km": 30,
        "elevation_m": 1500,
        "participants_estimate": 800,
        "source": "official",
    },
    {
        "external_id": "half_granada2027",
        "name": "Media Maratón de Granada 2027",
        "location": "Granada",
        "region": "Andalucía",
        "country": "España",
        "date": "2027-08-08",
        "distance_km": 21.0975,
        "elevation_m": 200,
        "participants_estimate": 3000,
        "source": "official",
    },
    {
        "external_id": "marbcn_half2027",
        "name": "Half Marathon Barcelona 2027",
        "location": "Barcelona",
        "region": "Cataluña",
        "country": "España",
        "date": "2027-08-29",
        "distance_km": 21.0975,
        "elevation_m": 80,
        "participants_estimate": 7000,
        "source": "official",
    },
    {
        "external_id": "ultracatal2027",
        "name": "Ultra Trail Costa Brava 2027",
        "location": "Girona",
        "region": "Cataluña",
        "country": "España",
        "date": "2027-09-19",
        "distance_km": 65,
        "elevation_m": 3500,
        "participants_estimate": 1500,
        "source": "official",
    },
    {
        "external_id": "10k_sevilla2027",
        "name": "10K Urbana Sevilla 2027",
        "location": "Sevilla",
        "region": "Andalucía",
        "country": "España",
        "date": "2027-09-05",
        "distance_km": 10,
        "elevation_m": 40,
        "participants_estimate": 3000,
        "source": "official",
    },
    {
        "external_id": "half_bilbao_oct2027",
        "name": "Media Maratón Bilbao - Octubre 2027",
        "location": "Bilbao",
        "region": "País Vasco",
        "country": "España",
        "date": "2027-10-10",
        "distance_km": 21.0975,
        "elevation_m": 100,
        "participants_estimate": 4000,
        "source": "official",
    },
    {
        "external_id": "mar_malaga2027",
        "name": "Maratón de Málaga 2027",
        "location": "Málaga",
        "region": "Andalucía",
        "country": "España",
        "date": "2027-11-21",
        "distance_km": 42.195,
        "elevation_m": 100,
        "participants_estimate": 5000,
        "source": "official",
    },
    {
        "external_id": "mar_valencia2027",
        "name": "Maratón de Valencia 2027",
        "location": "Valencia",
        "region": "Valencia",
        "country": "España",
        "date": "2027-11-28",
        "distance_km": 42.195,
        "elevation_m": 10,
        "participants_estimate": 12000,
        "source": "official",
    },
    {
        "external_id": "trail_valencia_dec2027",
        "name": "Trail Nocturno Valencia 2027",
        "location": "Valencia",
        "region": "Valencia",
        "country": "España",
        "date": "2027-12-12",
        "distance_km": 15,
        "elevation_m": 300,
        "participants_estimate": 2000,
        "source": "official",
    },
    {
        "external_id": "half_barcelona_dec2027",
        "name": "Media Maratón de Barcelona - Navidad 2027",
        "location": "Barcelona",
        "region": "Cataluña",
        "country": "España",
        "date": "2027-12-20",
        "distance_km": 21.0975,
        "elevation_m": 120,
        "participants_estimate": 4000,
        "source": "official",
    },
    {
        "external_id": "10k_madrid2027",
        "name": "10K San Silvestre Vallecana 2027",
        "location": "Madrid",
        "region": "Madrid",
        "country": "España",
        "date": "2027-12-31",
        "distance_km": 10,
        "elevation_m": 50,
        "participants_estimate": 30000,
        "source": "official",
    },
    # Additional popular races
    {
        "external_id": "half_zaragoza2027",
        "name": "Media Maratón de Zaragoza 2027",
        "location": "Zaragoza",
        "region": "Aragón",
        "country": "España",
        "date": "2027-04-18",
        "distance_km": 21.0975,
        "elevation_m": 40,
        "participants_estimate": 5000,
        "source": "official",
    },
    {
        "external_id": "10k_girona2027",
        "name": "10K Girona 2027",
        "location": "Girona",
        "region": "Cataluña",
        "country": "España",
        "date": "2027-05-16",
        "distance_km": 10,
        "elevation_m": 80,
        "participants_estimate": 2000,
        "source": "official",
    },
    {
        "external_id": "mar_oviedo2027",
        "name": "Maratón de Oviedo 2027",
        "location": "Oviedo",
        "region": "Asturias",
        "country": "España",
        "date": "2027-06-20",
        "distance_km": 42.195,
        "elevation_m": 250,
        "participants_estimate": 1500,
        "source": "official",
    },
    {
        "external_id": "10k_murcia2027",
        "name": "10K Popular Murcia 2027",
        "location": "Murcia",
        "region": "Murcia",
        "country": "España",
        "date": "2027-10-24",
        "distance_km": 10,
        "elevation_m": 60,
        "participants_estimate": 2500,
        "source": "official",
    },
    {
        "external_id": "5k_malaga2027",
        "name": "5K Popular Málaga 2027",
        "location": "Málaga",
        "region": "Andalucía",
        "country": "España",
        "date": "2027-08-15",
        "distance_km": 5,
        "elevation_m": 20,
        "participants_estimate": 2000,
        "source": "official",
    },
    {
        "external_id": "half_almeria2027",
        "name": "Media Maratón de Almería 2027",
        "location": "Almería",
        "region": "Andalucía",
        "country": "España",
        "date": "2027-07-11",
        "distance_km": 21.0975,
        "elevation_m": 30,
        "participants_estimate": 1200,
        "source": "official",
    },
    {
        "external_id": "5k_dos_hermanas2027",
        "name": "5K Popular Dos Hermanas 2027",
        "location": "Dos Hermanas",
        "region": "Andalucía",
        "country": "España",
        "date": "2027-04-25",
        "distance_km": 5,
        "elevation_m": 10,
        "participants_estimate": 1200,
        "source": "official",
    },
    {
        "external_id": "mar_cordoba2027",
        "name": "Maratón de Córdoba 2027",
        "location": "Córdoba",
        "region": "Andalucía",
        "country": "España",
        "date": "2027-05-02",
        "distance_km": 42.195,
        "elevation_m": 120,
        "participants_estimate": 2500,
        "source": "official",
    },
    {
        "external_id": "half_jaen2027",
        "name": "Media Maratón de Jaén 2027",
        "location": "Jaén",
        "region": "Andalucía",
        "country": "España",
        "date": "2027-04-11",
        "distance_km": 21.0975,
        "elevation_m": 80,
        "participants_estimate": 2000,
        "source": "official",
    },
    {
        "external_id": "5k_seville_dec2027",
        "name": "5K Popular Sevilla - Diciembre 2027",
        "location": "Sevilla",
        "region": "Andalucía",
        "country": "España",
        "date": "2027-12-05",
        "distance_km": 5,
        "elevation_m": 10,
        "participants_estimate": 1500,
        "source": "official",
    },
    {
        "external_id": "mar_san_sebastian2027",
        "name": "Maratón de San Sebastián 2027",
        "location": "San Sebastián",
        "region": "País Vasco",
        "country": "España",
        "date": "2027-11-07",
        "distance_km": 42.195,
        "elevation_m": 180,
        "participants_estimate": 6000,
        "source": "official",
    },
    {
        "external_id": "10k_alicante2027",
        "name": "10K Popular Alicante 2027",
        "location": "Alicante",
        "region": "Valencia",
        "country": "España",
        "date": "2027-10-17",
        "distance_km": 10,
        "elevation_m": 70,
        "participants_estimate": 2800,
        "source": "official",
    },
]


def seed_events():
    """Seed events to database."""
    db = SessionLocal()

    try:
        # Check if events already exist
        existing_count = db.query(Event).count()
        if existing_count > 0:
            logger.info(f"⚠️  Database already has {existing_count} events.")
            response = input("Delete all and reseed? (yes/no): ")
            if response.lower() != "yes":
                logger.info("Aborted.")
                return

            # Delete all existing events
            db.query(Event).delete()
            db.commit()
            logger.info("✅ Deleted all existing events")

        # Insert new events
        for event_data in EVENTS_DATA:
            event = Event(
                external_id=event_data["external_id"],
                name=event_data["name"],
                location=event_data["location"],
                region=event_data.get("region"),
                country=event_data["country"],
                date=datetime.strptime(event_data["date"], "%Y-%m-%d").date(),
                distance_km=event_data["distance_km"],
                elevation_m=event_data.get("elevation_m"),
                participants_estimate=event_data.get("participants_estimate"),
                source=event_data["source"],
                verified=True,
            )
            db.add(event)

        db.commit()
        logger.info(f"✅ Successfully seeded {len(EVENTS_DATA)} events!")

        # Show summary
        marathons = db.query(Event).filter(Event.distance_km >= 42).count()
        half_marathons = (
            db.query(Event)
            .filter(Event.distance_km >= 20, Event.distance_km < 30)
            .count()
        )
        ten_k = (
            db.query(Event)
            .filter(Event.distance_km >= 9, Event.distance_km < 12)
            .count()
        )
        five_k = db.query(Event).filter(Event.distance_km <= 5).count()
        ultras = db.query(Event).filter(Event.distance_km > 42.5).count()

        logger.info(
            f"""
📊 Event Summary:
   - Marathons (42K): {marathons}
   - Half Marathons (21K): {half_marathons}
   - 10K races: {ten_k}
   - 5K races: {five_k}
   - Ultra/Trail (>42.5K): {ultras}
   - Total: {len(EVENTS_DATA)}
"""
        )

    except Exception as e:
        logger.error(f"❌ Error seeding events: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    logger.info("🌱 Starting event seeding...")
    seed_events()
    logger.info("🎉 Done!")
