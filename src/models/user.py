"""User models."""

from datetime import datetime
from typing import ClassVar

from pydantic import field_validator
from sqlmodel import Field, SQLModel

from src.models.base import BaseModel


class UserBase(SQLModel):
    """Base user model with common fields."""

    username: str = Field(
        min_length=3,
        max_length=50,
        unique=True,
        index=True,
        description="Username (3-50 characters)",
    )

    email: str = Field(
        max_length=255, unique=True, index=True, description="Email address"
    )

    full_name: str | None = Field(default=None, max_length=100, description="Full name")

    is_active: bool = Field(default=True, description="Whether the user is active")


class User(UserBase, BaseModel, table=True):
    """User database model (simplified without password hashing)."""

    __tablename__ = "users"

    # Simple password storage (development only, not recommended for production)
    password: str = Field(description="User password (plain text - development only)")

    # Password hash field for testing compatibility
    password_hash: str | None = Field(
        default=None, description="Password hash for testing compatibility"
    )

    # 最后登录时间
    last_login: datetime | None = Field(
        default=None, description="Last login timestamp"
    )

    # 用户头像 URL
    avatar_url: str | None = Field(
        default=None, max_length=500, description="Avatar image URL"
    )

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate username format."""
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError(
                "Username can only contain letters, numbers, underscores, and hyphens"
            )
        return v.lower()

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate and normalize email."""
        return v.lower()


class UserCreate(UserBase):
    """User creation schema."""

    password: str = Field(
        min_length=6, max_length=100, description="Password (6-100 characters)"
    )


class UserUpdate(SQLModel):
    """User update schema."""

    username: str | None = Field(
        default=None,
        min_length=3,
        max_length=50,
        description="New username (3-50 characters)",
    )

    email: str | None = Field(
        default=None, max_length=255, description="New email address"
    )

    full_name: str | None = Field(
        default=None, max_length=100, description="New full name"
    )

    password: str | None = Field(
        default=None,
        min_length=6,
        max_length=100,
        description="New password (6-100 characters)",
    )

    is_active: bool | None = Field(
        default=None, description="Whether the user is active"
    )

    avatar_url: str | None = Field(
        default=None, max_length=500, description="New avatar image URL"
    )


class UserLogin(SQLModel):
    """User login schema."""

    username: str = Field(description="Username or email")

    password: str = Field(description="Password")


class UserResponse(UserBase):
    """User response schema (excludes sensitive data)."""

    id: int
    created_at: datetime
    updated_at: datetime | None = None
    last_login: datetime | None = None
    avatar_url: str | None = None

    class Config:
        """Pydantic configuration."""

        from_attributes = True
        json_encoders: ClassVar = {datetime: lambda v: v.isoformat() if v else None}
