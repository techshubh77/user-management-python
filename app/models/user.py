from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Enum, event, func, Integer, Index
from enum import Enum as PyEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.config.database import Base
import uuid
from pwdlib import PasswordHash
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.email_verification_token import EmailVerificationToken
    from app.models.password_reset_token import PasswordResetToken


pwd_context = PasswordHash.recommended()


class UserRole(str, PyEnum):
    ADMIN = "admin"
    USER = "user"


class User(Base):
    __tablename__ = "users"

    __table_args__ = (
        Index("idx_user_email_active", "email", "is_active"),
        Index("idx_user_lookup_active", "is_active", "deleted_at", "created_at"),
    )

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(150),
        unique=True,
        nullable=False,
    )

    password: Mapped[str] = mapped_column(String(255), nullable=False)

    avatar: Mapped[str | None] = mapped_column(String, nullable=True)

    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role_enum"),
        index=True,
        default=UserRole.USER,
        nullable=False,
    )

    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        index=True,
        default=False,
    )

    is_approved: Mapped[int] = mapped_column(
        Integer,
        index=True,
        default=0,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        index=True,
        default=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    email_verification_tokens: Mapped[list["EmailVerificationToken"]] = relationship(
        "EmailVerificationToken", back_populates="user", cascade="all, delete-orphan"
    )

    password_reset_tokens: Mapped[list["PasswordResetToken"]] = relationship(
        "PasswordResetToken", back_populates="user", cascade="all, delete-orphan"
    )

    @staticmethod
    def hash_password(raw_password: str) -> str:
        return pwd_context.hash(raw_password)

    def verify_password(self, plain_password: str) -> bool:
        return bool(self.password) and pwd_context.verify(plain_password, self.password)


@event.listens_for(User, "before_insert")
def hash_password_before_insert(mapper, connection, target):
    if target.password and not target.password.startswith("$"):
        target.password = User.hash_password(target.password)


@event.listens_for(User, "before_update")
def hash_password_before_update(mapper, connection, target):
    if target.password and not target.password.startswith("$"):
        target.password = User.hash_password(target.password)
