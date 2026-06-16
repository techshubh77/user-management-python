import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.config.settings import settings
from app.seeders.admin_seeder import (
    seed_admin,
)
from app.utils.logger import logger 
engine = create_async_engine(settings.database_url, echo=True)

AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)


async def main():
    """Main execution orchestrator."""
    async with AsyncSessionLocal() as db:
        try:
            logger.info("Starting database seeding...")
            await seed_admin(db)
            logger.info("Seeding execution completed successfully!")
        except Exception as e:
            logger.info(f"Seeding failed with an error: {e}")
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
