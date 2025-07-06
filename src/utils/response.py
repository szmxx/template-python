"""Response utilities for API endpoints."""

from datetime import datetime
from typing import Any

from fastapi import status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field


class BaseResponse(BaseModel):
    """Base response model."""

    success: bool = Field(description="Whether the request was successful")
    message: str = Field(description="Response message")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Response timestamp"
    )

    model_config = {"json_encoders": {datetime: lambda v: v.isoformat() if v else None}}


class SuccessResponse(BaseResponse):
    """Success response model."""

    success: bool = Field(default=True)
    data: Any | None = Field(default=None, description="Response data")
    meta: dict[str, Any] | None = Field(default=None, description="Response metadata")


class ErrorResponse(BaseResponse):
    """Error response model."""

    success: bool = Field(default=False)
    error_code: str | None = Field(default=None, description="Error code")
    details: dict[str, Any] | None = Field(default=None, description="Error details")
    errors: list[dict[str, Any]] | None = Field(
        default=None, description="Validation errors"
    )


class ValidationErrorDetail(BaseModel):
    """Validation error detail model."""

    field: str = Field(description="Field name that failed validation")
    message: str = Field(description="Validation error message")
    value: Any | None = Field(default=None, description="Invalid value")


# Legacy Pydantic response models are kept for backward compatibility
# but the helper functions have been replaced with JSONResponse-based alternatives


# Compatibility functions for JSONResponse
def json_success_response(
    message: str = "Success",
    data: Any | None = None,
    meta: dict[str, Any] | None = None,
    status_code: int = status.HTTP_200_OK,
) -> JSONResponse:
    """Create a JSONResponse compatible success response.

    This function provides backward compatibility with JSONResponse
    while maintaining the same response structure as SuccessResponse.

    Args:
        message: Success message
        data: Response data
        meta: Response metadata
        status_code: HTTP status code

    Returns:
        JSONResponse with standardized structure
    """
    response_data = {
        "success": True,
        "message": message,
        "timestamp": datetime.utcnow().isoformat(),
        "data": data,
        "meta": meta,
    }
    return JSONResponse(content=response_data, status_code=status_code)


def json_error_response(
    message: str = "Error",
    error_code: str | None = None,
    details: dict[str, Any] | None = None,
    errors: list[dict[str, Any]] | None = None,
    status_code: int = status.HTTP_400_BAD_REQUEST,
) -> JSONResponse:
    """Create a JSONResponse compatible error response.

    This function provides backward compatibility with JSONResponse
    while maintaining the same response structure as ErrorResponse.

    Args:
        message: Error message
        error_code: Error code
        details: Error details
        errors: Validation errors
        status_code: HTTP status code

    Returns:
        JSONResponse with standardized structure
    """
    response_data = {
        "success": False,
        "message": message,
        "timestamp": datetime.utcnow().isoformat(),
        "error_code": error_code,
        "details": details,
        "errors": errors,
    }
    return JSONResponse(content=response_data, status_code=status_code)
