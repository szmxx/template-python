"""Response utilities for API endpoints."""

import json
from datetime import datetime
from typing import Any, ClassVar

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

    class Config:
        """Pydantic configuration."""

        json_encoders: ClassVar = {datetime: lambda v: v.isoformat() if v else None}


class SuccessResponse(BaseResponse):
    """Success response model."""

    success: bool = Field(default=True)
    data: Any | None = Field(default=None, description="Response data")
    meta: dict[str, Any] | None = Field(default=None, description="Response metadata")

    class Config:
        """Pydantic configuration."""

        json_encoders: ClassVar = {datetime: lambda v: v.isoformat() if v else None}


class ErrorResponse(BaseResponse):
    """Error response model."""

    success: bool = Field(default=False)
    error_code: str | None = Field(default=None, description="Error code")
    details: dict[str, Any] | None = Field(default=None, description="Error details")
    errors: list[dict[str, Any]] | None = Field(
        default=None, description="Validation errors"
    )

    class Config:
        """Pydantic configuration."""

        json_encoders: ClassVar = {datetime: lambda v: v.isoformat() if v else None}


class ValidationErrorDetail(BaseModel):
    """Validation error detail model."""

    field: str = Field(description="Field name that failed validation")
    message: str = Field(description="Validation error message")
    value: Any | None = Field(default=None, description="Invalid value")


def create_response(
    success: bool = True,
    message: str = "Success",
    data: Any | None = None,
    meta: dict[str, Any] | None = None,
    error_code: str | None = None,
    details: dict[str, Any] | None = None,
    errors: list[dict[str, Any]] | None = None,
    status_code: int = status.HTTP_200_OK,
) -> JSONResponse:
    """Create a standardized JSON response.

    Args:
        success: Whether the request was successful
        message: Response message
        data: Response data (for success responses)
        meta: Response metadata
        error_code: Error code (for error responses)
        details: Error details
        errors: Validation errors
        status_code: HTTP status code

    Returns:
        JSONResponse with standardized format
    """
    if success:
        response_model = SuccessResponse(message=message, data=data, meta=meta)
    else:
        response_model = ErrorResponse(
            message=message, error_code=error_code, details=details, errors=errors
        )

    # 使用 model_dump_json 然后解析, 这样会正确应用 json_encoders

    response_json = response_model.model_dump_json(exclude_none=True)
    response_data = json.loads(response_json)

    return JSONResponse(content=response_data, status_code=status_code)


def success_response(
    message: str = "Success",
    data: Any | None = None,
    meta: dict[str, Any] | None = None,
    status_code: int = status.HTTP_200_OK,
) -> JSONResponse:
    """Create a success response.

    Args:
        message: Success message
        data: Response data
        meta: Response metadata
        status_code: HTTP status code

    Returns:
        JSONResponse with success format
    """
    return create_response(
        success=True, message=message, data=data, meta=meta, status_code=status_code
    )


def error_response(
    message: str = "Error",
    error_code: str | None = None,
    details: dict[str, Any] | None = None,
    errors: list[dict[str, Any]] | None = None,
    status_code: int = status.HTTP_400_BAD_REQUEST,
) -> JSONResponse:
    """Create an error response.

    Args:
        message: Error message
        error_code: Error code
        details: Error details
        errors: Validation errors
        status_code: HTTP status code

    Returns:
        JSONResponse with error format
    """
    return create_response(
        success=False,
        message=message,
        error_code=error_code,
        details=details,
        errors=errors,
        status_code=status_code,
    )


def validation_error_response(
    errors: list[ValidationErrorDetail],
    message: str = "Validation failed",
    status_code: int = status.HTTP_422_UNPROCESSABLE_ENTITY,
) -> JSONResponse:
    """Create a validation error response.

    Args:
        message: Error message
        errors: List of validation errors
        status_code: HTTP status code

    Returns:
        JSONResponse with validation error format
    """
    error_list = [error.model_dump() for error in errors]

    return error_response(
        message=message,
        error_code="VALIDATION_ERROR",
        errors=error_list,
        status_code=status_code,
    )


def not_found_response(
    message: str = "Resource not found",
    resource_type: str | None = None,
    resource_id: str | int | None = None,
) -> JSONResponse:
    """Create a not found error response.

    Args:
        message: Error message
        resource_type: Type of resource that was not found
        resource_id: ID of resource that was not found

    Returns:
        JSONResponse with not found error format
    """
    details = {}
    if resource_type:
        details["resource_type"] = resource_type
    if resource_id:
        details["resource_id"] = resource_id

    return error_response(
        message=message,
        error_code="NOT_FOUND",
        details=details if details else None,
        status_code=status.HTTP_404_NOT_FOUND,
    )


def unauthorized_response(
    message: str = "Unauthorized", details: dict[str, Any] | None = None
) -> JSONResponse:
    """Create an unauthorized error response.

    Args:
        message: Error message
        details: Error details

    Returns:
        JSONResponse with unauthorized error format
    """
    return error_response(
        message=message,
        error_code="UNAUTHORIZED",
        details=details,
        status_code=status.HTTP_401_UNAUTHORIZED,
    )


def forbidden_response(
    message: str = "Forbidden", details: dict[str, Any] | None = None
) -> JSONResponse:
    """Create a forbidden error response.

    Args:
        message: Error message
        details: Error details

    Returns:
        JSONResponse with forbidden error format
    """
    return error_response(
        message=message,
        error_code="FORBIDDEN",
        details=details,
        status_code=status.HTTP_403_FORBIDDEN,
    )


def conflict_response(
    message: str = "Conflict", details: dict[str, Any] | None = None
) -> JSONResponse:
    """Create a conflict error response.

    Args:
        message: Error message
        details: Error details

    Returns:
        JSONResponse with conflict error format
    """
    return error_response(
        message=message,
        error_code="CONFLICT",
        details=details,
        status_code=status.HTTP_409_CONFLICT,
    )


def internal_server_error_response(
    message: str = "Internal server error", details: dict[str, Any] | None = None
) -> JSONResponse:
    """Create an internal server error response.

    Args:
        message: Error message
        details: Error details

    Returns:
        JSONResponse with internal server error format
    """
    return error_response(
        message=message,
        error_code="INTERNAL_SERVER_ERROR",
        details=details,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
