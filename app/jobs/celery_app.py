from celery import Celery
from celery.schedules import crontab
from app.config.settings import settings

celery_app = Celery(
    "user_management_jobs",
    broker=settings.celery_broker_url,
    include=["app.jobs.db_backup"],
)

celery_app.conf.beat_schedule = {
    "daily-database-backup": {
        "task": "app.jobs.db_backup.database_backup",
        "schedule": crontab(hour=4, minute=7),
    },
}

celery_app.conf.timezone = "Asia/Kolkata"
