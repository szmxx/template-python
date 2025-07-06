"""FastAPI 应用主入口文件。"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api import api_router
from src.db.config import DatabaseConfig
from src.db.connection import db  # 使用简化的 db 实例
from src.utils.response import (
    json_error_response,
    json_success_response,
)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    """应用生命周期管理。"""
    # Create database tables on startup
    db.create_tables()
    # Cleanup work on shutdown (if needed)
    yield


# 创建 FastAPI 应用
app = FastAPI(
    title="FastAPI Template",
    description="一个使用 SQLModel 和 FastAPI 的模板项目",
    version="1.0.0",
    lifespan=lifespan,
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含 API 路由
app.include_router(api_router, prefix="")


@app.get("/")
def read_root() -> JSONResponse:
    """根路径欢迎信息。"""
    return json_success_response(
        message="欢迎使用 FastAPI Template!",
        data={
            "version": "1.0.0",
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/api/v1/health",
        },
    )


@app.exception_handler(404)  # type: ignore[misc]
async def not_found_handler(_request: Request, _exc: HTTPException) -> JSONResponse:
    """404 错误处理器。"""
    return json_error_response(
        message="请求的资源未找到", error_code="NOT_FOUND", status_code=404
    )


@app.exception_handler(500)  # type: ignore[misc]
async def internal_error_handler(_request: Request, _exc: Exception) -> JSONResponse:
    """500 错误处理器。"""
    return json_error_response(
        message="服务器内部错误", error_code="INTERNAL_SERVER_ERROR", status_code=500
    )


def main() -> None:
    """应用入口点。"""
    # 初始化数据库配置
    db_config = DatabaseConfig()

    print("Starting Template Python API...")
    print(f"Database URL: {db_config.database_url}")

    try:
        uvicorn.run(
            "main:app", host="0.0.0.0", port=8000, reload=True, log_level="info"
        )
    except KeyboardInterrupt:
        print("\n应用已停止")
        raise
    except Exception as e:
        print(f"应用启动失败: {e}")
        raise


if __name__ == "__main__":
    main()
