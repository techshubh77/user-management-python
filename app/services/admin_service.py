from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.schemas.register_schema import RegisterSchema
from app.exceptions.custom_exceptions import AppException
from app.services.user_service import get_user_by_email, get_user_by_id
from app.utils.email import send_account_creation_email, send_account_status_email
from fastapi import BackgroundTasks
from app.models.user import UserRole



class AdminService:

    @staticmethod
    async def index(db: AsyncSession):
        stmt = select(User).where(User.role == UserRole.USER)
        result = await db.execute(stmt)
        users = result.scalars().all()

        return users


    @staticmethod
    async def create(db: AsyncSession, data: RegisterSchema, background_tasks: BackgroundTasks):
        existing_user = await get_user_by_email(
            db=db,
            email=data.email
        )

        if existing_user:
            raise AppException("Email is already registered", 400)

        user = User(
            name=data.name,
            email=data.email,
            password=data.password,
            is_approved=1,
            is_verified=True,
        )

        db.add(user)
        await db.flush()
        await db.refresh(user)

        background_tasks.add_task(send_account_creation_email,user.name, user.email, data.password)

        return user

    @staticmethod
    async def manage_account_approval(db: AsyncSession, data, background_tasks: BackgroundTasks):
        user = await get_user_by_id(db, data["user_id"])
        if not user:
            raise AppException("User not found", 404)

        if user.is_approved != 0:
            raise AppException("User is already approved or rejected", 400)

        if user.is_verified is False:
            raise AppException("User is not verified", 400)

        if data["approval_status"] == "approved":
            user.is_approved = 1
        elif data["approval_status"] == "rejected":
            user.is_approved = 2
        else:
            raise AppException("Invalid approval status", 400)

        await db.commit()
        await db.refresh(user)

        status = "approved" if data["approval_status"] == "approved" else "rejected"
        background_tasks.add_task(send_account_status_email, user.name, user.email, status)

        return user





