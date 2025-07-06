from collections.abc import Generator
from contextlib import contextmanager
from typing import TYPE_CHECKING

from loguru import logger
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session, SQLModel, create_engine

if TYPE_CHECKING:
    from sqlalchemy.engine import Engine

from .config import db_config


class Database:
    """数据库连接管理类。"""

    def __init__(self) -> None:
        """初始化数据库连接。"""
        self.engine: Engine = create_engine(
            db_config.database_url,
            echo=db_config.db_echo,
            pool_pre_ping=True,
        )

    def create_tables(self) -> None:
        """创建所有数据库表。"""
        SQLModel.metadata.create_all(self.engine)

    def drop_tables(self) -> None:
        """删除所有数据库表。"""
        SQLModel.metadata.drop_all(self.engine)

    @contextmanager
    def session(self) -> Generator[Session, None, None]:
        """获取数据库会话上下文管理器。

        Example:
            with db.session() as session:
                user = session.get(User, 1)
                print(user.name)
        """
        session = Session(self.engine)
        try:
            yield session
            session.commit()
        except SQLAlchemyError as e:
            logger.error(f"数据库操作失败: {e!s}", exc_info=True)
            session.rollback()
            raise
        except Exception as e:
            logger.error(f"会话管理中发生未知错误: {e!s}", exc_info=True)
            session.rollback()
            raise
        finally:
            session.close()

    def get_session(self) -> Generator[Session, None, None]:
        """FastAPI 依赖注入的数据库会话。

        Example:
            @app.get("/users/{user_id}")
            def get_user(user_id: int, session: Session = Depends(db.get_session)):
                return session.get(User, user_id)
        """
        session = Session(self.engine)
        try:
            yield session
        except SQLAlchemyError as e:
            logger.error(f"数据库依赖注入会话失败: {e!s}", exc_info=True)
            session.rollback()
            raise
        except Exception as e:
            logger.error(f"依赖注入会话中发生未知错误: {e!s}", exc_info=True)
            session.rollback()
            raise
        finally:
            session.close()


# 全局数据库实例
db = Database()


# 向后兼容的函数
def get_db_session() -> Generator[Session, None, None]:
    """FastAPI 依赖注入函数(向后兼容)。"""
    yield from db.get_session()


def create_tables() -> None:
    """创建数据库表(向后兼容)。"""
    db.create_tables()


def drop_tables() -> None:
    """删除数据库表(向后兼容)。"""
    db.drop_tables()
