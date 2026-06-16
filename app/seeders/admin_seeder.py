from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.user import UserRole

from app.utils.password import hash_password
from app.utils.logger import logger


async def seed_admin(
    db: AsyncSession,
) -> None:
    """
    Create default admin user
    if it does not exist.
    """

    result = await db.execute(select(User).where(User.email == "admin@gmail.com"))

    admin = result.scalar_one_or_none()

    if admin:
        logger.info("Admin already exists")
        return

    admin = User(
        name="admin sir ",
        email="admin@gmail.com",
        password=hash_password("Admin@123"),
        role=UserRole.ADMIN,
        is_verified=True,
        is_approved=True,
        is_active=True,
    )

    db.add(admin)

    await db.commit()

    logger.info("Default admin user created")
