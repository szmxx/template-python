"""数据库异常处理工具模块。"""

from collections.abc import Callable
from functools import wraps
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from src.utils.logger import logger


def handle_db_errors(func: Callable[..., Any]) -> Callable[..., Any]:
    """数据库操作异常处理装饰器。

    用于捕获和处理数据库操作中的各种异常，包括：
    - IntegrityError: 数据完整性错误（如唯一约束违反）
    - SQLAlchemyError: 其他数据库相关错误
    - Exception: 其他未预期的错误

    Args:
        func: 需要包装的函数

    Returns:
        包装后的函数
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except IntegrityError as e:
            # 处理数据完整性错误（如唯一约束违反）
            logger.warning(f"数据完整性错误: {e!s}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="数据冲突：该记录已存在或违反数据约束",
            ) from e
        except SQLAlchemyError as e:
            logger.error(f"数据库操作失败: {e!s}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="数据库操作失败，请稍后重试",
            ) from e
        except HTTPException:
            # 重新抛出 HTTPException，保持原有的状态码和消息
            raise
        except Exception as e:
            # 处理其他未预期的错误
            logger.error(f"未知错误: {e!s}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="服务器内部错误",
            ) from e

    return wrapper


def handle_db_transaction(func: Callable[..., Any]) -> Callable[..., Any]:
    """数据库事务处理装饰器。

    用于确保数据库操作在事务中执行，并在出现异常时自动回滚。

    Args:
        func: 需要包装的函数

    Returns:
        包装后的函数
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        # 从参数中获取数据库会话
        db = None
        for arg in args:
            if (
                hasattr(arg, "add")
                and hasattr(arg, "commit")
                and hasattr(arg, "rollback")
            ):
                db = arg
                break

        if "db" in kwargs:
            db = kwargs["db"]

        try:
            result = func(*args, **kwargs)
            if db:
                db.commit()
            return result
        except Exception:
            if db:
                db.rollback()
                logger.warning("数据库事务已回滚")
            raise

    return wrapper
