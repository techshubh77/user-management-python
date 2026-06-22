from app.utils.logger import logger
import datetime
import os
import subprocess
from app.config.settings import settings
from app.jobs.celery_app import celery_app


@celery_app.task
def database_backup():
    try:
        logger.info("Performing database backup...")

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_folder = "backups"
        os.makedirs(backup_folder, exist_ok=True)
        backup_file = os.path.join(backup_folder, f"backup-{timestamp}.sql")

        db_url = settings.database_url.replace("postgresql+asyncpg", "postgresql")

        command = ["pg_dump", "--dbname", db_url, "--file", backup_file]

        try:
            subprocess.run(command, check=True)
            logger.info(f"Backup successful: {backup_file}")

        except subprocess.CalledProcessError as e:
            logger.error(f"Backup failed! Error: {e}")

    except Exception as e:
        logger.error(f"Failed to perform database backup: {e}")
