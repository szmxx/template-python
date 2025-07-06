"""API v1 package."""

from fastapi import APIRouter

from .endpoints import files, health, heroes, users

api_router = APIRouter(prefix="/api/v1")

# 包含各个端点路由
api_router.include_router(health.router, tags=["health"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(heroes.router, prefix="/heroes", tags=["heroes"])
api_router.include_router(files.router, prefix="/files", tags=["files"])

__all__ = ["api_router"]
