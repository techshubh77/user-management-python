from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.schemas.update_schema import UpdateSchema
from app.schemas.password_schema import ChangePassword
from app.config.settings import settings
from app.exceptions.custom_exceptions import AppException
import os

class ProfileService:
    @staticmethod
    async def update_profile(
        db: AsyncSession,
        user: User,
        data: UpdateSchema,
        avatar_filename: str | None,
    ) -> User:
        if data.name is not None:
            user.name = data.name

        if avatar_filename is not None:
            if user.avatar is not None:
                old_avatar_path = os.path.join(settings.uploads_dir, "avatars", user.avatar)
                if os.path.exists(old_avatar_path):
                    os.remove(old_avatar_path)
            user.avatar = avatar_filename

        await db.flush()
        await db.refresh(user)
        return user

    @staticmethod
    async def change_password(
        db: AsyncSession,
        user: User,
        data: ChangePassword,
    ) -> None:
        if not user.verify_password(data.current_password):
            raise AppException("Current password is incorrect.", 400)

        user.password = data.new_password
        await db.flush()
