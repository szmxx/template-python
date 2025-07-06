from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy.engine import Engine
from sqlmodel import Session, SQLModel, create_engine

from .config import db_config


class Database:
    """简化的数据库管理器。"""

    def __init__(self):
        self._engine: Engine | None = None

    @property
    def engine(self) -> Engine:
        """获取数据库引擎实例。"""
        if self._engine is None:
            self._engine = create_engine(
                db_config.database_url, **db_config.get_engine_kwargs()
            )
        return self._engine

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
        except Exception:
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
        with self.session() as session:
            yield session


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
