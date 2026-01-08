"""
Celery tasks for background processing.
Handles automatic Garmin synchronization and other periodic tasks.
"""

import logging
from datetime import datetime
from sqlalchemy.orm import Session
from .celery_app import celery_app
from .database import SessionLocal
from .models import User
from . import models
from .services.garmin_health_service import GarminHealthService

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.sync_all_users_garmin_health")
def sync_all_users_garmin_health():
    """
    Sync Garmin health data for all users with active Garmin connections.
    Runs periodically via Celery Beat.

    Returns:
        dict: Summary of sync operation (success/failure counts)
    """
    logger.info("Starting automatic Garmin health sync for all users")

    db: Session = SessionLocal()
    success_count = 0
    error_count = 0
    skipped_count = 0

    try:
        # Get all users with Garmin tokens
        users = db.query(User).filter(User.garmin_token.isnot(None)).all()

        logger.info(f"Found {len(users)} users with Garmin connections")

        for user in users:
            try:
                logger.info(f"Syncing health data for user {user.id} ({user.email})")

                # Check if user has valid tokens
                if not user.garmin_token:
                    logger.warning(f"User {user.id} has no Garmin token, skipping")
                    skipped_count += 1
                    continue

                # Determine sync period - check if user has health metrics from Garmin
                existing_health = (
                    db.query(models.HealthMetric)
                    .filter(
                        models.HealthMetric.user_id == user.id,
                        models.HealthMetric.source == "garmin",
                    )
                    .first()
                )

                if existing_health:
                    # Incremental sync (last 2 days - today + yesterday)
                    # Garmin data doesn't change retroactively beyond yesterday
                    days = 2
                    logger.info(f"Incremental sync: last 2 days for user {user.id}")
                else:
                    # First sync (last 730 days / 2 years)
                    days = 730
                    logger.info(f"First health sync: last 730 days for user {user.id}")

                # Sync health metrics
                health_service = GarminHealthService()
                synced_metrics = health_service.sync_health_metrics(db, user.id, days)

                # Update last sync timestamp
                user.last_garmin_sync = datetime.utcnow()
                db.commit()

                logger.info(
                    f"Successfully synced health data for user {user.id}: "
                    f"{len(synced_metrics)} metrics"
                )
                success_count += 1

            except Exception as e:
                logger.error(f"Error syncing health data for user {user.id}: {str(e)}")
                error_count += 1
                db.rollback()
                continue

        summary = {
            "status": "completed",
            "timestamp": datetime.utcnow().isoformat(),
            "total_users": len(users),
            "successful": success_count,
            "errors": error_count,
            "skipped": skipped_count,
        }

        logger.info(f"Garmin health sync completed: {summary}")
        return summary

    except Exception as e:
        logger.error(f"Fatal error in sync_all_users_garmin_health: {str(e)}")
        return {
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }
    finally:
        db.close()


@celery_app.task(name="app.tasks.sync_single_user_garmin_health")
def sync_single_user_garmin_health(user_id: int, days: int = 7):
    """
    Sync Garmin health data for a specific user.
    Can be triggered manually or via API.

    Args:
        user_id: Database ID of the user
        days: Number of days to sync (default: 7)

    Returns:
        dict: Sync result with metrics count
    """
    logger.info(f"Starting Garmin health sync for user {user_id}, days={days}")

    db: Session = SessionLocal()

    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User {user_id} not found")

        if not user.garmin_token:
            raise ValueError(f"User {user_id} has no Garmin token")

        # Sync health metrics
        health_service = GarminHealthService()
        synced_metrics = health_service.sync_health_metrics(db, user_id, days)

        # Update last sync timestamp
        user.last_garmin_sync = datetime.utcnow()
        db.commit()

        result = {"metrics_synced": len(synced_metrics)}
        return result
    except Exception as e:
        logger.error(f"Error syncing health data for user {user_id}: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()
