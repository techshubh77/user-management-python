from pydantic import BaseModel, EmailStr, Field, field_validator
from app.utils.password_strength import validate_password_strength


class LoginSchema(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=16)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        value = value.strip().lower()
        if not value:
            raise ValueError("Email cannot be empty.")
        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        return validate_password_strength(value)
