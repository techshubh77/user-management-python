import re
from datetime import datetime
from pydantic import (
    BaseModel,
    EmailStr,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)
from typing_extensions import Self
from typing import Optional
from app.models.user import UserRole


def validate_password_strength(value: str) -> str:
    if not re.search(r"[A-Z]", value):
        raise ValueError("Password must contain at least one uppercase letter")
    if not re.search(r"[a-z]", value):
        raise ValueError("Password must contain at least one lowercase letter")
    if not re.search(r"\d", value):
        raise ValueError("Password must contain at least one digit")
    if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?]", value):
        raise ValueError("Password must contain at least one special character")
    return value


class UserCreate(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=100,
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=16,
    )

    confirm_password: str = Field(
        min_length=8,
        max_length=16,
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Name cannot be empty.")

        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        return validate_password_strength(value)

    @model_validator(mode="after")
    def verify_password_match(self) -> Self:
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self


class UserLogin(BaseModel):
    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128,
    )


class UserUpdate(BaseModel):
    name: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=100,
    )


class ChangePassword(BaseModel):
    current_password: str

    new_password: str = Field(
        min_length=8,
        max_length=16,
    )

    confirm_new_password: str = Field(
        min_length=8,
        max_length=16,
    )

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        return validate_password_strength(value)

    @model_validator(mode="after")
    def verify_new_password_match(self) -> Self:
        if self.new_password != self.confirm_new_password:
            raise ValueError("New passwords do not match")
        return self


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    email: EmailStr
    role: str

    is_verified: bool
    is_approved: bool
    is_active: bool

    created_at: datetime
    updated_at: datetime


class AdminUserUpdate(BaseModel):
    name: Optional[str] = None

    is_verified: Optional[bool] = None

    is_approved: Optional[bool] = None

    is_active: Optional[bool] = None

    role: Optional[UserRole] = None
