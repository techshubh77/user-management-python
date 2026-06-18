from fastapi import APIRouter, Depends, Form
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.middlewares.auth import authenticate
from app.utils.upload import process_avatar
from app.controllers.profile_controller import ProfileController
from app.schemas.update_schema import UpdateSchema
from app.schemas.password_schema import ChangePassword
from app.models.user import User

router = APIRouter(prefix="/users", tags=["Users"])


@router.patch("/me")
async def update_profile(
    name: Optional[str] = Form(None),
    avatar_filename: Optional[str] = Depends(process_avatar),
    user: User = Depends(authenticate),
    db: AsyncSession = Depends(get_db),
):
    data = UpdateSchema(name=name)
    return await ProfileController.update_profile(db, user, data, avatar_filename)


@router.patch("/me/change-password")
async def change_password(
    data: ChangePassword,
    user: User = Depends(authenticate),
    db: AsyncSession = Depends(get_db),
):
    return await ProfileController.change_password(db, user, data)
