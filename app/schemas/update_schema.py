from pydantic import BaseModel, Field, field_validator, EmailStr
from typing import Optional, Literal
from typing_extensions import Self
from app.utils.password_strength import validate_password_strength
from pydantic import model_validator


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
    name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(default=None, min_length=8, max_length=16)
    confirm_password: Optional[str] = Field(default=None, min_length=8, max_length=16)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        if value:
            value = value.strip()
            if not value:
                raise ValueError("Name cannot be empty.")
        return value

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        if value:
            value = value.strip().lower()
            if not value:
                raise ValueError("Email cannot be empty.")
        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if value:
            value = value.strip()
            if not value:
                raise ValueError("Password cannot be empty.")
            if len(value) < 8:
                raise ValueError("Password must be at least 8 characters long.")
        return validate_password_strength(value)

    @model_validator(mode="after")
    def verify_password_match(self) -> Self:
        if self.password is not None:
            if self.password != self.confirm_password:
                raise ValueError("Passwords do not match")
        return self


class AccountApprovalSchema(BaseModel):
    approval_status: Literal["approved", "rejected"]

