from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import BackgroundTasks
from app.services.auth_service import AuthService
from app.schemas.user import UserCreate, UserLogin
from app.schemas.password_schema import ForgotPasswordSchema, ResetPasswordSchema
from app.utils.response import success_response
from fastapi import Response
from app.config.settings import settings


class AuthController:
    @staticmethod
    async def register(
        db: AsyncSession, data: UserCreate, background_tasks: BackgroundTasks
    ):
        user = await AuthService.register_user(db, data, background_tasks)
        return success_response(
            message="Registration successful. Please check your email for verification.",
            data={"id": user.id, "email": user.email},
            status_code=201,
        )

    @staticmethod
    async def verify_email(db: AsyncSession, token: str):
        user = await AuthService.verify_email(db, token)
        return success_response(
            message="Email verification successful.",
            data={
                "id": user.id,
                "email": user.email,
                "is_verified": user.is_verified,
            },
            status_code=200,
        )

    @staticmethod
    async def login(db: AsyncSession, data: UserLogin):
        result = await AuthService.login_user(db, data)

        res = success_response(
            message="Login successful.",
            data=result["user"].model_dump(mode='json'),
            status_code=200,
        )

        res.set_cookie(
            key="token",
            value=result["access_token"],
            httponly=True,
            samesite="lax",
            secure=settings.env == "production",
            max_age=settings.access_token_exp_minutes * 60,
        )

        return res

    @staticmethod
    async def forgot_password(db: AsyncSession, data: ForgotPasswordSchema, background_tasks: BackgroundTasks):
        await AuthService.forgot_password(db, data, background_tasks)
        return success_response(
            message="Password reset link sent successfully.",
            status_code=200,
        )

    @staticmethod
    async def reset_password(db: AsyncSession, data: ResetPasswordSchema):
        await AuthService.reset_password(db, data)
        return success_response(
            message="Password reset successful.",
            status_code=200,
        )

