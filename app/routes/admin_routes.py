from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.middlewares.auth import require_role
# get_db dependency from database config
from app.config.database import get_db

# Import controller
from app.controllers.admin_controller import AdminController

# Import schemas
from app.schemas.register_schema import RegisterSchema
from app.schemas.update_schema import AccountApprovalSchema, AdminUserUpdateSchema


router = APIRouter(prefix="/admins", tags=["Admin"])

@router.get("/users")
async def index(
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_role("admin"))
):
    return await AdminController.index(db)


@router.post("/users")
async def create(
    data: RegisterSchema,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_role("admin"))
):
    return await AdminController.create(db, data, background_tasks)

@router.patch("/users/{user_id}/account-approval")
async def account_approval(
    user_id: str,
    data: AccountApprovalSchema,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_role("admin"))
):
    payload = {"user_id": user_id, "approval_status": data.approval_status}
    return await AdminController.manage_account_approval(db, payload, background_tasks)

@router.patch("/users/{user_id}/account-status")
async def account_status(
    user_id: str,
    data: dict,
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_role("admin"))
):
    payload = {"user_id": user_id, "account_status": data["account_status"]}
    return await AdminController.manage_account_status(db, payload)

@router.patch("/users/{user_id}")
async def update(
    user_id: str,
    data: AdminUserUpdateSchema,
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_role("admin"))
):
    return await AdminController.update(db, user_id, data)

@router.delete("/users/{user_id}")
async def destroy(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_role("admin"))
):
    return await AdminController.destroy(db, user_id)
