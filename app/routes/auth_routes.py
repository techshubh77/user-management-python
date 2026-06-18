from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.controllers.auth_controller import AuthController
from app.schemas.register_schema import RegisterSchema
from app.schemas.login_schema import LoginSchema
from app.schemas.password_schema import ForgotPasswordSchema, ResetPasswordSchema

# get_db dependency from database config
from app.config.database import get_db

# Create the router with the /auth prefix
router = APIRouter(prefix="/auth", tags=["Authentication"])

# Define the endpoint. The full path will be .../auth/register
@router.post("/register")
async def register(
    data: RegisterSchema,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    return await AuthController.register(db, data, background_tasks)

@router.post("/verify-email/{token}")
async def verify_email(
    token: str,
    db: AsyncSession = Depends(get_db),
):
    return await AuthController.verify_email(db, token)

@router.post("/login")
async def login(
    data: LoginSchema,
    db: AsyncSession = Depends(get_db),
):
    return await AuthController.login(db, data)

@router.post("/forgot-password")
async def forgot_password(
    data: ForgotPasswordSchema,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    return await AuthController.forgot_password(db, data, background_tasks)

@router.post("/reset-password/{token}")
async def reset_password(
    token: str,
    data: ResetPasswordSchema,
    db: AsyncSession = Depends(get_db),
):
    return await AuthController.reset_password(db, data, token)

@router.post("/logout")
async def logout():
    return await AuthController.logout()
