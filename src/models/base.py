"""Base model classes."""

from datetime import datetime
from typing import ClassVar

from sqlmodel import Field, SQLModel


class BaseModel(SQLModel):
    """Base model with common fields."""

    id: int | None = Field(default=None, primary_key=True, description="Primary key")

    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Creation timestamp"
    )

    updated_at: datetime | None = Field(
        default=None, description="Last update timestamp"
    )

    class Config:
        """Pydantic configuration."""

        # 允许从 ORM 对象创建
        from_attributes = True
        # JSON 编码器
        json_encoders: ClassVar = {datetime: lambda v: v.isoformat() if v else None}


class TimestampMixin(SQLModel):
    """Timestamp mixin for models that need creation and update timestamps."""

    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Creation timestamp"
    )

    updated_at: datetime | None = Field(
        default=None, description="Last update timestamp"
    )


class SoftDeleteMixin(SQLModel):
    """Soft delete mixin for models that support soft deletion."""

    is_deleted: bool = Field(default=False, description="Soft delete flag")

    deleted_at: datetime | None = Field(default=None, description="Deletion timestamp")
