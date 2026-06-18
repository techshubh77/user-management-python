from fastapi import Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config.database import get_db
from app.models.user import User
from app.utils.jwt import verify_jwt_token
from app.exceptions.custom_exceptions import AppException

async def authenticate(request: Request, db: AsyncSession = Depends(get_db)) -> User:
    """
    Authenticates the user based on the authentication token.
    """
    token = request.cookies.get("token")

    if not token:
        raise AppException("Invalid or expired authentication token. Please log in.", 401)

    decoded = verify_jwt_token(token)
    if not decoded or decoded.get("id") is None:
        raise AppException("Invalid or expired authentication token.", 401)

    result = await db.execute(select(User).where(User.id == decoded["id"]))
    user = result.scalar_one_or_none()

    if not user:
        raise AppException("user account not found.", 404)

    if not user.is_active or user.deleted_at is not None:
        raise AppException("Your account has been deactivated or deleted.", 401)

    if not user.is_verified:
        raise AppException("Your email has not been verified. Please verify your email to continue.", 401)

    if user.is_approved == 0:
        raise AppException("Your account is pending for approval. Please wait for approval from the admin.", 403)

    if user.is_approved == 2:
        raise AppException("Your account has been rejected. Please contact the admin for more information.", 403)

    return user


def require_role(*roles: str):
    """Restrict routes to specific roles"""
    async def role_dependency(user: User = Depends(authenticate)) -> User:
        if user.role.value not in roles:
            raise AppException("You do not have permission to perform this action.", 403)
        return user
    return role_dependency
