"""Database configuration."""

from pydantic import Field
from pydantic_settings import BaseSettings


class DatabaseConfig(BaseSettings):
    """数据库配置设置 - 自动从环境变量加载。"""

    # 数据库连接配置
    database_url: str = Field(
        default="sqlite:///./app.db", description="数据库连接 URL"
    )

    # 调试配置
    db_echo: bool = Field(default=False, description="启用 SQL 查询日志")

    # 测试数据库配置
    test_database_url: str = Field(
        default="sqlite:///:memory:", description="测试数据库连接 URL"
    )

    # 连接池配置(仅适用于 PostgreSQL/MySQL)
    db_pool_size: int = Field(default=5, description="连接池大小")

    db_max_overflow: int = Field(default=10, description="最大溢出连接数")

    db_pool_timeout: int = Field(default=30, description="连接池超时时间(秒)")

    db_pool_recycle: int = Field(default=3600, description="连接池回收时间(秒)")

    # 应用配置
    app_name: str = Field(default="FastAPI Template", description="应用名称")

    app_version: str = Field(default="1.0.0", description="应用版本")

    debug: bool = Field(default=False, description="调试模式")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @property
    def is_sqlite(self) -> bool:
        """检查是否使用 SQLite 数据库。"""
        return self.database_url.startswith("sqlite")

    @property
    def is_postgres(self) -> bool:
        """检查是否使用 PostgreSQL 数据库。"""
        return self.database_url.startswith("postgresql")

    @property
    def is_mysql(self) -> bool:
        """检查是否使用 MySQL 数据库。"""
        return self.database_url.startswith("mysql")

    def get_engine_kwargs(self) -> dict:
        """获取引擎配置参数。"""
        kwargs = {
            "echo": self.db_echo,
        }

        # SQLite 不支持连接池配置
        if not self.is_sqlite:
            kwargs.update(
                {
                    "pool_size": self.db_pool_size,
                    "max_overflow": self.db_max_overflow,
                    "pool_timeout": self.db_pool_timeout,
                    "pool_recycle": self.db_pool_recycle,
                }
            )

        return kwargs


# 全局配置实例
db_config = DatabaseConfig()
