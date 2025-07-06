from datetime import datetime
from typing import Generic, TypeVar

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

    @classmethod
    def success_message(cls, message: str = "操作成功") -> "MessageResponse":
        """创建成功消息响应"""
        return cls(success=True, message=message)
