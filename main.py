"""FastAPI Template 主应用模块。"""

import time
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from src.api import api_router
from src.db.config import DatabaseConfig
from src.db.connection import db  # 使用简化的 db 实例
from src.utils.api_response import (
    json_error_response,
    json_success_response,
)
from src.utils.logger import get_logger, setup_logger

# 设置日志
setup_logger()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    """应用生命周期管理。"""
    logger.info("🚀 应用启动中...")

    # Create database tables on startup
    try:
        db.create_tables()
        logger.info("✅ 数据库表创建完成")
    except Exception:
        logger.exception("❌ 数据库初始化失败")
        raise

    logger.info("🎉 应用启动完成")

    yield

    logger.info("🛑 应用关闭中...")
    # Cleanup work on shutdown (if needed)
    logger.info("👋 应用关闭完成")


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


# 添加请求日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """记录HTTP请求日志。"""
    start_time = time.time()
    client_ip = request.client.host if request.client else "unknown"

    # 记录请求信息
    logger.info(f"📥 {request.method} {request.url.path} - 客户端: {client_ip}")

    # 处理请求
    response = await call_next(request)

    # 计算处理时间
    process_time = time.time() - start_time

    # 根据状态码选择日志级别和图标
    if response.status_code < 400:
        logger.info(
            f"📤 {request.method} {request.url.path} - {response.status_code} - {process_time:.4f}s"
        )
    elif response.status_code < 500:
        logger.warning(
            f"⚠️ {request.method} {request.url.path} - {response.status_code} - {process_time:.4f}s"
        )
    else:
        logger.error(
            f"💥 {request.method} {request.url.path} - {response.status_code} - {process_time:.4f}s"
        )

    return response


# 包含 API 路由
app.include_router(api_router, prefix="")


@app.get("/")
def read_root() -> JSONResponse:
    """根路径欢迎信息。"""
    logger.info("🏠 访问根路径")
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
async def not_found_handler(request: Request, _exc: HTTPException) -> JSONResponse:
    """404 错误处理器。"""
    logger.warning(f"🔍 404 - 资源未找到: {request.url}")
    return json_error_response(
        message="请求的资源未找到", error_code="NOT_FOUND", status_code=404
    )


@app.exception_handler(500)  # type: ignore[misc]
async def internal_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """500 错误处理器。"""
    logger.error(
        f"💥 500 - 服务器内部错误: {request.url} - {type(exc).__name__}: {exc!s}"
    )
    return json_error_response(
        message="服务器内部错误", error_code="INTERNAL_SERVER_ERROR", status_code=500
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """HTTP异常处理器。"""
    logger.warning(f"⚠️ HTTP异常: {exc.status_code} - {exc.detail} - URL: {request.url}")
    return json_error_response(
        message=exc.detail,
        status_code=exc.status_code,
    )


@app.exception_handler(IntegrityError)
async def integrity_error_handler(
    request: Request, exc: IntegrityError
) -> JSONResponse:
    """数据完整性错误处理器。"""
    logger.warning(f"🔒 数据完整性错误: {request.url} - {exc!s}")
    return json_error_response(
        message="数据冲突：该记录已存在或违反数据约束",
        error_code="INTEGRITY_ERROR",
        status_code=409,
    )


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_error_handler(
    request: Request, exc: SQLAlchemyError
) -> JSONResponse:
    """SQLAlchemy错误处理器。"""
    logger.error(f"💾 数据库错误: {request.url} - {exc!s}")
    return json_error_response(
        message="数据库操作失败，请稍后重试",
        error_code="DATABASE_ERROR",
        status_code=500,
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """通用异常处理器。"""
    logger.error(
        f"💥 未处理的异常: {type(exc).__name__}: {exc!s} - URL: {request.url}",
        exc_info=True,
    )
    return json_error_response(
        message="内部服务器错误",
        status_code=500,
    )


def main() -> None:
    """应用入口点。"""
    # 初始化数据库配置
    db_config = DatabaseConfig()

    logger.info("🚀 启动 Template Python API...")
    logger.info(f"📊 数据库 URL: {db_config.database_url}")
    logger.info(f"🐛 调试模式: {db_config.debug}")

    try:
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="warning",  # 降低uvicorn日志级别，使用我们的日志
            access_log=False,  # 禁用uvicorn访问日志，使用我们的中间件
        )
    except KeyboardInterrupt:
        logger.info("\n👋 应用已停止")
        raise
    except Exception:
        logger.exception("💥 应用启动失败")
        raise


if __name__ == "__main__":
    main()
