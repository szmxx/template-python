"""Health check endpoints."""

import sys
from datetime import datetime

import psutil  # type: ignore
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlmodel import Session, text

from src.db import get_db_session
from src.utils.api_response import json_success_response

router = APIRouter()


@router.get("/health")
async def health_check() -> JSONResponse:
    """Basic health check endpoint."""
    return json_success_response(
        message="Service is healthy",
        data={
            "status": "healthy",
            "service": "template-python",
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


@router.get("/health/db")
async def database_health_check(db: Session = Depends(get_db_session)) -> JSONResponse:
    """Database health check endpoint."""
    try:
        # 执行简单的数据库查询
        result = db.exec(text("SELECT 1")).scalar()  # type: ignore

        return json_success_response(
            message="Database is healthy",
            data={"status": "healthy", "database": "connected", "query_result": result},
        )
    except Exception as e:
        return json_success_response(
            message="Database is unhealthy",
            data={"status": "unhealthy", "database": "disconnected", "error": str(e)},
        )


@router.get("/health/detailed")
async def detailed_health_check(db: Session = Depends(get_db_session)) -> JSONResponse:
    """Detailed health check with system information."""

    # 数据库健康检查
    db_status = "healthy"
    db_error = None
    try:
        db.exec(text("SELECT 1")).scalar()  # type: ignore
    except Exception as e:
        db_status = "unhealthy"
        db_error = str(e)

    # 系统信息
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    return json_success_response(
        message="Detailed health check completed",
        data={
            "status": "healthy" if db_status == "healthy" else "unhealthy",
            "service": {
                "name": "template-python",
                "version": "1.0.0",
                "python_version": sys.version,
                "uptime": datetime.utcnow().isoformat(),
            },
            "database": {"status": db_status, "error": db_error},
            "system": {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent,
                },
                "disk": {
                    "total": disk.total,
                    "free": disk.free,
                    "percent": (disk.used / disk.total) * 100,
                },
            },
        },
    )
