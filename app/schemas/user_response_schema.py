from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from typing import Optional


class UserResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    email: EmailStr
    role: str
    avatar: Optional[str] = None

    is_verified: bool
    is_approved: int
    is_active: bool

    created_at: datetime
    updated_at: datetime
