"""Loguru 使用示例。"""

from src.utils.logger import LogExecutionTime, get_logger, log_function_call

# 获取当前模块的logger
logger = get_logger(__name__)


class UserService:
    """用户服务示例类。"""

    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)

    @log_function_call(level="INFO")
    def create_user(self, username: str, email: str) -> dict:
        """创建用户示例。"""
        self.logger.info(f"开始创建用户: {username}")

        try:
            # 模拟用户创建逻辑
            user_data = {
                "id": 1,
                "username": username,
                "email": email,
                "created_at": "2024-01-01T00:00:00Z",
            }

            self.logger.success(f"用户创建成功: {username}")
            return user_data

        except Exception:
            self.logger.exception(f"用户创建失败: {username}")
            raise

    def get_user_by_id(self, user_id: int) -> dict:
        """根据ID获取用户。"""
        with LogExecutionTime(f"获取用户 ID: {user_id}", level="DEBUG"):
            # 模拟数据库查询
            import time

            time.sleep(0.1)  # 模拟查询延迟

            if user_id == 1:
                return {"id": 1, "username": "test_user", "email": "test@example.com"}
            else:
                self.logger.warning(f"用户不存在: ID {user_id}")
                return {}

    def delete_user(self, user_id: int) -> bool:
        """删除用户示例。"""
        try:
            # 模拟删除逻辑
            if user_id <= 0:
                raise ValueError("无效的用户ID")

            self.logger.info(f"删除用户: ID {user_id}")
            # 模拟删除操作
        except ValueError:
            self.logger.exception("删除用户失败")
            return False
        except Exception:
            self.logger.exception("删除用户时发生严重错误")
            return False
        else:
            return True


def demonstrate_logging():
    """演示不同级别的日志记录。"""
    logger.debug("🐛 这是调试信息")
    logger.info("ℹ️ 这是普通信息")
    logger.success("✅ 这是成功信息")
    logger.warning("⚠️ 这是警告信息")
    logger.error("❌ 这是错误信息")
    logger.critical("🚨 这是严重错误信息")

    # 结构化日志
    logger.info(
        "用户操作",
        extra={
            "user_id": 123,
            "action": "login",
            "ip_address": "192.168.1.1",
            "timestamp": "2024-01-01T12:00:00Z",
        },
    )

    # 异常日志
    try:
        1 / 0  # noqa: B018
    except ZeroDivisionError:
        logger.exception("除零错误示例")


if __name__ == "__main__":
    # 演示基本日志功能
    demonstrate_logging()

    # 演示服务类的使用
    user_service = UserService()

    # 创建用户
    user = user_service.create_user("john_doe", "john@example.com")
    logger.info(f"创建的用户: {user}")

    # 获取用户
    found_user = user_service.get_user_by_id(1)
    logger.info(f"找到的用户: {found_user}")

    # 删除用户
    deleted = user_service.delete_user(1)
    logger.info(f"删除结果: {deleted}")

    # 尝试删除无效用户
    deleted_invalid = user_service.delete_user(-1)
    logger.info(f"删除无效用户结果: {deleted_invalid}")
