from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.middlewares.auth import require_role
# get_db dependency from database config
from app.config.database import get_db

# Import controller
from app.controllers.admin_controller import AdminController

# Import schemas
from app.schemas.register_schema import RegisterSchema
from app.schemas.update_schema import AccountApprovalSchema


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
