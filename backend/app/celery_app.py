"""
Celery application configuration for background tasks.
Handles periodic tasks like automatic Garmin health sync.
"""

from celery import Celery
from celery.schedules import crontab
from .core.config import settings

# Initialize Celery app
celery_app = Celery(
    "runcoach",
    broker=f"redis://{settings.redis_host}:{settings.redis_port}/0",
    backend=f"redis://{settings.redis_host}:{settings.redis_port}/0",
    include=["app.tasks"],  # Import tasks module
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes max per task
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Periodic tasks schedule (Celery Beat)
celery_app.conf.beat_schedule = {
    # Sync Garmin health data twice daily (morning after wakeup, evening after workout)
    "sync-garmin-health-morning": {
        "task": "app.tasks.sync_all_users_garmin_health",
        "schedule": crontab(hour=7, minute=0),  # Daily at 7:00 AM (after night data)
    },
    "sync-garmin-health-evening": {
        "task": "app.tasks.sync_all_users_garmin_health",
        "schedule": crontab(hour=20, minute=0),  # Daily at 8:00 PM (after workout data)
    },
}
