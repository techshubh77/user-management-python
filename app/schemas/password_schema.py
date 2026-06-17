from pydantic import Field, model_validator, EmailStr, BaseModel, field_validator
from typing_extensions import Self
from app.utils.password_strength import validate_password_strength


class ForgotPasswordSchema(BaseModel):
    email: EmailStr


class ResetPasswordSchema(BaseModel):
    password: str = Field(min_length=8, max_length=16)
    confirm_password: str = Field(min_length=8, max_length=16)

    @model_validator(mode="after")
    def confirm_password_match(self) -> "ResetPasswordSchema":
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self

    @field_validator("password", "confirm_password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if value != value.strip():
            raise ValueError("Password cannot contain leading or trailing spaces")
        return validate_password_strength(value)


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

    @field_validator("new_password", "confirm_new_password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if value != value.strip():
            raise ValueError("Password cannot contain leading or trailing spaces")
        return validate_password_strength(value)

    @model_validator(mode="after")
    def verify_new_password_match(self) -> Self:
        if self.new_password != self.confirm_new_password:
            raise ValueError("New passwords do not match")
        return self
