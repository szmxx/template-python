"""Base model classes."""

from datetime import datetime

from sqlmodel import Field, SQLModel


class BaseModel(SQLModel):
    """Base model with common fields."""

    model_config = {
        "from_attributes": True,
        "json_encoders": {datetime: lambda v: v.isoformat() if v else None},
    }

    id: int | None = Field(default=None, primary_key=True, description="Primary key")

    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Creation timestamp"
    )

    updated_at: datetime | None = Field(
        default=None, description="Last update timestamp"
    )


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
