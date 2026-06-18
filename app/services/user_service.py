from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.schemas.register_schema import RegisterSchema
from app.schemas.login_schema import LoginSchema
from app.schemas.user_response_schema import UserResponseSchema


async def get_user_by_email(
    db: AsyncSession,
    email: str,
) -> User | None:

    stmt = select(User).where(User.email == email)

    result = await db.execute(stmt)

    return result.scalar_one_or_none()


async def get_user_by_id(
    db: AsyncSession,
    user_id: str,
) -> User | None:

    stmt = select(User).where(User.id == user_id)

    result = await db.execute(stmt)

    return result.scalar_one_or_none()


async def create_user(
    db: AsyncSession,
    data: RegisterSchema
) -> User:

    existing_user = await get_user_by_email(
        db=db,
        email=data.email,
    )

    if existing_user:
        raise ValueError("Email is already registered")

    user = User(
        name=data.name,
        email=data.email,
        password=data.password
    )

    db.add(user)
    await db.flush()

    await db.refresh(user)
    return user


