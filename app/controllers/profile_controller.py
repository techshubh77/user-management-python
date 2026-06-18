from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.models.user import User
from app.services.profile_service import ProfileService
from app.schemas.update_schema import UpdateSchema
from app.schemas.user_response_schema import UserResponseSchema
from app.schemas.password_schema import ChangePassword
from app.utils.response import success_response


class ProfileController:
    @staticmethod
    async def update_profile(
        db: AsyncSession,
        user: User,
        data: UpdateSchema,
        avatar_filename: Optional[str],
    ):
        updated_user = await ProfileService.update_profile(db, user, data, avatar_filename)
        await db.commit()
        return success_response(
            message="Profile updated successfully.",
            data=UserResponseSchema.model_validate(updated_user).model_dump(mode="json"),
        )

    @staticmethod
    async def change_password(
        db: AsyncSession,
        user: User,
        data: ChangePassword,
    ):
        await ProfileService.change_password(db, user, data)
        await db.commit()
        return success_response(message="Password changed successfully.")
