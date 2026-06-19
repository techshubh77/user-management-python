from fastapi import BackgroundTasks
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.admin_service import AdminService
from app.schemas.register_schema import RegisterSchema
from app.schemas.update_schema import AdminUserUpdateSchema
from app.schemas.user_response_schema import UserResponseSchema
from app.utils.response import success_response


class AdminController:
    @staticmethod
    async def index(db: AsyncSession):
        users = await AdminService.index(db)
        return success_response(
            message="Users fetched successfully.",
            data=[
                UserResponseSchema.model_validate(user).model_dump(mode="json")
                for user in users
            ],
            status_code=200,
        )

    @staticmethod
    async def create(
        db: AsyncSession, data: RegisterSchema, background_tasks: BackgroundTasks
    ):
        user = await AdminService.create(db, data, background_tasks)
        return success_response(
            message="User created successfully.",
            data=UserResponseSchema.model_validate(user).model_dump(mode="json"),
            status_code=201,
        )

    @staticmethod
    async def manage_account_approval(
        db: AsyncSession, data: dict, background_tasks: BackgroundTasks
    ):
        user = await AdminService.manage_account_approval(db, data, background_tasks)
        return success_response(
            message="User account approval managed successfully.",
            data=UserResponseSchema.model_validate(user).model_dump(mode="json"),
            status_code=200,
        )

    @staticmethod
    async def manage_account_status(db: AsyncSession, data: dict):
        message = await AdminService.manage_account_status(db, data)
        return success_response(
            message=message,
            data=None,
            status_code=200,
        )

    @staticmethod
    async def update(db: AsyncSession, user_id: str, data: AdminUserUpdateSchema):
        user = await AdminService.update(db, user_id, data)
        return success_response(
            message="User updated successfully.",
            data=UserResponseSchema.model_validate(user).model_dump(mode="json"),
            status_code=200,
        )

    @staticmethod
    async def destroy(db: AsyncSession, user_id: str):
        user = await AdminService.destroy(db, user_id)

        user_data = jsonable_encoder(user)
        user_data.pop("password", None)
        return success_response(
            message="User deleted successfully.",
            data=user_data,
            status_code=200,
        )
