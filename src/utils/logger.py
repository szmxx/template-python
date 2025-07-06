"""Loguru 日志配置模块。"""

import sys
from pathlib import Path

from loguru import logger

from ..db.config import db_config

# 日志格式常量
CONSOLE_FORMAT = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
FILE_FORMAT = (
    "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
)


def setup_logger() -> None:
    """设置 loguru 日志配置。"""
    config = db_config

    # 移除默认的处理器
    logger.remove()

    # 创建日志目录
    if config.log_to_file:
        log_file_path = Path(config.log_file)
        log_file_path.parent.mkdir(parents=True, exist_ok=True)

    # 添加控制台处理器
    if config.log_to_console:
        logger.add(
            sys.stdout,
            level=config.log_level,
            format=CONSOLE_FORMAT,
            colorize=True,
            serialize=config.enable_serialize,
        )

    # 添加文件处理器
    if config.log_to_file:
        logger.add(
            config.log_file,
            level=config.log_level,
            format=FILE_FORMAT,
            rotation=config.log_rotation,
            retention=config.log_retention,
            compression="zip",
            serialize=config.enable_serialize,
            encoding="utf-8",
        )

    # 配置第三方库的日志级别
    logger.disable("uvicorn")
    logger.disable("uvicorn.access")
    logger.disable("sqlalchemy")

    # 重新启用并设置合适的级别
    logger.enable("uvicorn")
    logger.enable("uvicorn.access")
    logger.enable("sqlalchemy")


def get_logger(name: str | None = None):
    """获取 logger 实例。"""
    if name:
        return logger.bind(name=name)
    return logger


# 创建一个装饰器用于记录函数调用
def log_function_call(level: str = "DEBUG"):
    """装饰器：记录函数调用。"""

    def decorator(func):
        def wrapper(*args, **kwargs):
            logger.log(
                level, f"调用函数 {func.__name__} 参数: args={args}, kwargs={kwargs}"
            )
            try:
                result = func(*args, **kwargs)
                logger.log(level, f"函数 {func.__name__} 执行成功")
                return result
            except Exception as e:
                logger.error(f"函数 {func.__name__} 执行失败: {e}")
                raise

        return wrapper

    return decorator


# 创建一个上下文管理器用于记录代码块执行时间
class LogExecutionTime:
    """上下文管理器：记录代码块执行时间。"""

    def __init__(self, description: str, level: str = "INFO"):
        self.description = description
        self.level = level
        self.start_time = None

    def __enter__(self):
        import time

        self.start_time = time.time()
        logger.log(self.level, f"开始执行: {self.description}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        import time

        execution_time = time.time() - self.start_time
        if exc_type is None:
            logger.log(
                self.level,
                f"完成执行: {self.description}, 耗时: {execution_time:.4f}秒",
            )
        else:
            logger.error(
                f"执行失败: {self.description}, 耗时: {execution_time:.4f}秒, 错误: {exc_val}"
            )
