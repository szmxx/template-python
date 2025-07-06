"""Hero models."""

from datetime import datetime
from typing import ClassVar

from pydantic import field_validator
from sqlmodel import Field, SQLModel

from src.models.base import BaseModel


class HeroBase(SQLModel):
    """Base hero fields."""

    name: str = Field(
        min_length=1, max_length=100, unique=True, index=True, description="Hero name"
    )

    secret_name: str = Field(
        min_length=1, max_length=100, description="Hero's secret identity"
    )

    age: int | None = Field(
        default=None, ge=0, le=1000, description="Hero age (0-1000)"
    )

    description: str | None = Field(
        default=None, max_length=1000, description="Hero description"
    )

    power_level: int = Field(
        default=1, ge=1, le=100, description="Hero power level (1-100)"
    )

    is_active: bool = Field(default=True, description="Hero active status")


class Hero(HeroBase, BaseModel, table=True):
    """Hero database model."""

    __tablename__ = "heroes"

    # 英雄头像 URL
    avatar_url: str | None = Field(
        default=None, max_length=500, description="Hero avatar image URL"
    )

    # 英雄所属团队
    team: str | None = Field(
        default=None, max_length=100, description="Hero team affiliation"
    )

    # Hero abilities list (JSON field)
    abilities: str | None = Field(
        default=None, description="Hero abilities (JSON string)"
    )

    # 英雄弱点
    weakness: str | None = Field(
        default=None, max_length=500, description="Hero weakness"
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate hero name."""
        if not v.strip():
            raise ValueError("Hero name cannot be empty")
        return v.strip().title()

    @field_validator("secret_name")
    @classmethod
    def validate_secret_name(cls, v: str) -> str:
        """Validate secret name."""
        if not v.strip():
            raise ValueError("Secret name cannot be empty")
        return v.strip().title()


class HeroCreate(HeroBase):
    """Hero creation schema."""

    avatar_url: str | None = Field(
        default=None, max_length=500, description="Hero avatar image URL"
    )

    team: str | None = Field(
        default=None, max_length=100, description="Hero team affiliation"
    )

    abilities: list[str] | None = Field(default=None, description="Hero abilities list")

    weakness: str | None = Field(
        default=None, max_length=500, description="Hero weakness"
    )


class HeroUpdate(SQLModel):
    """Hero update schema."""

    name: str | None = Field(
        default=None, min_length=1, max_length=100, description="Hero name"
    )

    secret_name: str | None = Field(
        default=None, min_length=1, max_length=100, description="Hero's secret identity"
    )

    age: int | None = Field(
        default=None, ge=0, le=1000, description="Hero age (0-1000)"
    )

    description: str | None = Field(
        default=None, max_length=1000, description="Hero description"
    )

    power_level: int | None = Field(
        default=None, ge=1, le=100, description="Hero power level (1-100)"
    )

    is_active: bool | None = Field(default=None, description="Hero active status")

    avatar_url: str | None = Field(
        default=None, max_length=500, description="Hero avatar image URL"
    )

    team: str | None = Field(
        default=None, max_length=100, description="Hero team affiliation"
    )

    abilities: list[str] | None = Field(default=None, description="Hero abilities list")

    weakness: str | None = Field(
        default=None, max_length=500, description="Hero weakness"
    )


class HeroResponse(HeroBase):
    """Hero response schema."""

    id: int
    created_at: datetime
    updated_at: datetime | None
    avatar_url: str | None
    team: str | None
    abilities: list[str] | None
    weakness: str | None

    class Config:
        """Pydantic configuration."""

        from_attributes = True
        json_encoders: ClassVar = {datetime: lambda v: v.isoformat() if v else None}


class HeroListResponse(SQLModel):
    """Hero list response schema."""

    heroes: list[HeroResponse] = Field(description="List of heroes")

    total: int = Field(description="Total number of heroes")

    page: int = Field(description="Current page number")

    size: int = Field(description="Page size")

    pages: int = Field(description="Total number of pages")
