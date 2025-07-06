from datetime import datetime
from typing import Any, Generic, TypeVar

from fastapi import status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """统一的API响应格式"""

    success: bool = Field(description="操作是否成功")
    data: T | None = Field(default=None, description="响应数据")
    message: str = Field(description="响应消息")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="响应时间戳"
    )

    model_config = {"json_encoders": {datetime: lambda v: v.isoformat() if v else None}}

    @classmethod
    def success_response(
        cls, data: T | None = None, message: str = "操作成功"
    ) -> "ApiResponse[T]":
        """创建成功响应"""
        return cls(success=True, data=data, message=message)

    @classmethod
    def error_response(
        cls, message: str = "操作失败", data: T | None = None
    ) -> "ApiResponse[T]":
        """创建错误响应"""
        return cls(success=False, data=data, message=message)


class MessageResponse(BaseModel):
    """简单消息响应"""

    success: bool = Field(description="操作是否成功")
    message: str = Field(description="响应消息")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="响应时间戳"
    )

    model_config = {"json_encoders": {datetime: lambda v: v.isoformat() if v else None}}

    @classmethod
    def success_message(cls, message: str = "操作成功") -> "MessageResponse":
        """创建成功消息响应"""
        return cls(success=True, message=message)

    @classmethod
    def error_message(cls, message: str = "操作失败") -> "MessageResponse":
        """创建错误消息响应"""
        return cls(success=False, message=message)


# JSONResponse 兼容函数
def json_success_response(
    message: str = "Success",
    data: Any | None = None,
    meta: dict[str, Any] | None = None,
    status_code: int = status.HTTP_200_OK,
) -> JSONResponse:
    """创建成功的 JSONResponse

    Args:
        message: 成功消息
        data: 响应数据
        meta: 响应元数据
        status_code: HTTP状态码

    Returns:
        JSONResponse 对象
    """
    api_response = ApiResponse.success_response(data=data, message=message)
    response_data = {
        "success": api_response.success,
        "data": api_response.data,
        "message": api_response.message,
        "timestamp": api_response.timestamp.isoformat(),
    }

    # 添加 meta 字段（如果提供）
    if meta is not None:
        response_data["meta"] = meta

    return JSONResponse(content=response_data, status_code=status_code)


def json_error_response(
    message: str = "Error",
    error_code: str | None = None,
    details: dict[str, Any] | None = None,
    errors: list[dict[str, Any]] | None = None,
    status_code: int = status.HTTP_400_BAD_REQUEST,
) -> JSONResponse:
    """创建错误的 JSONResponse

    Args:
        message: 错误消息
        error_code: 错误代码
        details: 错误详情
        errors: 验证错误列表
        status_code: HTTP状态码

    Returns:
        JSONResponse 对象
    """
    api_response = ApiResponse.error_response(message=message, data=None)
    response_data = {
        "success": api_response.success,
        "data": api_response.data,
        "message": api_response.message,
        "timestamp": api_response.timestamp.isoformat(),
    }

    # 添加额外的错误字段（如果提供）
    if error_code is not None:
        response_data["error_code"] = error_code
    if details is not None:
        response_data["details"] = details
    if errors is not None:
        response_data["errors"] = errors

    return JSONResponse(content=response_data, status_code=status_code)
