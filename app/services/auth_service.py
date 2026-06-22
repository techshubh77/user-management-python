from datetime import datetime, timedelta, timezone
import secrets

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.email_verification_token import EmailVerificationToken
from app.models.password_reset_token import PasswordResetToken

from app.exceptions.custom_exceptions import AppException
from app.utils.email import send_email, render_verification_email, render_password_reset_email
from app.schemas.register_schema import RegisterSchema
from app.schemas.login_schema import LoginSchema
from app.schemas.user_response_schema import UserResponseSchema
from app.utils.jwt import create_jwt_token
from app.schemas.password_schema import ForgotPasswordSchema, ResetPasswordSchema
from fastapi import BackgroundTasks
from app.utils.avatar import generate_random_avatar


class AuthService:
    def __init__(self):
        pass

    @staticmethod
    async def register_user(
        db: AsyncSession, data: RegisterSchema, background_tasks: BackgroundTasks
    ):
        result = await db.execute(select(User).where(User.email == data.email))
        existing_user = result.scalar_one_or_none()

        if existing_user:
            raise AppException("Email is already registered.", 400)

        avatar_name = await generate_random_avatar(data.name)

        user = User(
            name=data.name,
            email=data.email,
            password=data.password,
            avatar=avatar_name
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)

        background_tasks.add_task(AuthService.send_verification_email, db, user)

        return user

    @staticmethod
    async def send_verification_email(db: AsyncSession, user):
        email = user.email

        token = secrets.token_hex(32)

        expiry_time = datetime.now(timezone.utc) + timedelta(minutes=10)

        insert_data = {
            "user_id": user.id,
            "token": token,
            "expires_at": expiry_time,
        }

        stmt = insert(EmailVerificationToken).values(**insert_data)

        upsert_stmt = stmt.on_conflict_do_update(
            index_elements=["user_id"],
            set_={"token": stmt.excluded.token, "expires_at": stmt.excluded.expires_at},
        ).returning(EmailVerificationToken)

        await db.execute(upsert_stmt)
        await db.commit()

        subject = "Verify Your Email"
        html_content = render_verification_email(user.name, token)

        await send_email(email, subject, html_content)

        return True

    @staticmethod
    async def verify_email(db: AsyncSession, token: str):
        stmt = select(EmailVerificationToken).where(EmailVerificationToken.token == token)
        result = await db.execute(stmt)
        token_record = result.scalar_one_or_none()
        if not token_record:
            raise AppException("Invalid or expired verification token.", 400)

        if token_record.expires_at < datetime.now(timezone.utc):
            await db.delete(token_record)
            await db.commit()
            raise AppException("Verification token has expired.", 400)

        user_result = await db.execute(
            select(User).where(User.id == token_record.user_id)
        )
        user = user_result.scalar_one_or_none()

        if not user:
            raise AppException("User not found.", 404)

        user.is_verified = True
        await db.delete(token_record)
        await db.commit()

        return user

    @staticmethod
    async def login_user(db: AsyncSession, data: LoginSchema):
        email, password = data.email, data.password

        result = await db.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()

        if not user:
            raise AppException("Invalid credentials.", 401)

        if not user.verify_password(password):
            raise AppException("Invalid credentials.", 401)

        if not user.is_verified:
            raise AppException("Please verify your email before logging in.", 403)

        if user.is_approved == 0:
            raise AppException("Your account is not approved yet. Please contact the administrator.", 403)

        if user.is_approved == 2:
            raise AppException("Your account has been rejected. Please contact the administrator.", 403)

        if not user.is_active:
            raise AppException("Your account has been deactivated. Please contact the administrator.", 403)

        if user.deleted_at is not None:
            raise AppException("Your account has been deleted. Please contact the administrator.", 403)

        access_token_payload = {
            "id": str(user.id),
            "email": user.email,
        }

        access_token = create_jwt_token(access_token_payload)

        return {"access_token": access_token, "user": UserResponseSchema.model_validate(user)}


    @staticmethod
    async def forgot_password(db: AsyncSession, data: ForgotPasswordSchema, background_tasks: BackgroundTasks):
        email = data.email

        result = await db.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()

        if not user:
            return  # silent return

        token = secrets.token_hex(32)

        expiry_time = datetime.now(timezone.utc) + timedelta(minutes=10)

        insert_data = {
            "user_id": user.id,
            "token": token,
            "expires_at": expiry_time,
        }

        stmt = insert(PasswordResetToken).values(**insert_data)

        upsert_stmt = stmt.on_conflict_do_update(
            index_elements=["user_id"],
            set_={"token": stmt.excluded.token, "expires_at": stmt.excluded.expires_at},
        ).returning(PasswordResetToken)

        await db.execute(upsert_stmt)
        await db.commit()

        subject = "Reset Your Password"
        html_content = render_password_reset_email(user.name, token)

        background_tasks.add_task(send_email, email, subject, html_content)

        return True

    @staticmethod
    async def reset_password(db: AsyncSession, data: ResetPasswordSchema, token: str):
        result = await db.execute(
            select(PasswordResetToken).where(PasswordResetToken.token == token)
        )
        token_record = result.scalar_one_or_none()

        if not token_record:
            raise AppException("Invalid or expired password reset token.", 400)
        if token_record.expires_at < datetime.now(timezone.utc):
            await db.delete(token_record)
            await db.commit()
            raise AppException("Password reset token has expired.", 400)

        user_result = await db.execute(select(User).where(User.id == token_record.user_id))
        user = user_result.scalar_one_or_none()

        if not user:
            raise AppException("User not found.", 404)

        user.password = data.password

        await db.delete(token_record)
        await db.commit()
        return True

