from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal
from app.models.user import UserRole



class UpdateSchema(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=100)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        if value:
            value = value.strip()
            if not value:
                raise ValueError("Name cannot be empty.")
        return value


class AdminUserUpdateSchema(BaseModel):
    name: Optional[str] = None
    is_verified: Optional[bool] = None
    is_approved: Optional[int] = None
    is_active: Optional[bool] = None
    role: Optional[UserRole] = None


class AccountApprovalSchema(BaseModel):
    approval_status: Literal["approved", "rejected"]

