# Loguru 日志系统使用指南

本项目使用 [Loguru](https://loguru.readthedocs.io/) 作为日志管理库，提供了简单易用且功能强大的日志记录功能。

## 特性

- 🎨 **彩色输出**: 控制台日志支持彩色显示
- 📁 **文件轮转**: 自动管理日志文件大小和保留时间
- 🔧 **灵活配置**: 通过环境变量配置日志行为
- 📊 **结构化日志**: 支持JSON格式输出
- ⚡ **性能监控**: 内置请求处理时间记录
- 🎯 **装饰器支持**: 函数调用日志装饰器
- ⏱️ **执行时间**: 代码块执行时间上下文管理器

## 配置

### 环境变量

在 `.env` 文件中配置以下变量：

```env
# 日志级别: TRACE, DEBUG, INFO, SUCCESS, WARNING, ERROR, CRITICAL
LOG_LEVEL=INFO

# 日志文件路径
LOG_FILE=logs/app.log

# 是否输出到控制台
LOG_TO_CONSOLE=true

# 是否输出到文件
LOG_TO_FILE=true

# 日志文件最大大小
LOG_MAX_SIZE=10 MB

# 日志文件保留时间
LOG_RETENTION=30 days

# 日志轮转时间
LOG_ROTATION=1 day

# 是否启用JSON序列化
ENABLE_SERIALIZE=false
```

### 初始化

在应用启动时，日志系统会自动初始化：

```python
from src.utils.logger import setup_logger, get_logger

# 设置日志（在main.py中已完成）
setup_logger()

# 获取logger实例
logger = get_logger(__name__)
```

## 基本使用

### 1. 获取Logger

```python
from src.utils.logger import get_logger

# 获取当前模块的logger
logger = get_logger(__name__)

# 或者获取指定名称的logger
logger = get_logger("my_module")
```

### 2. 记录不同级别的日志

```python
# 调试信息
logger.debug("🐛 调试信息")

# 普通信息
logger.info("ℹ️ 应用启动")

# 成功信息
logger.success("✅ 操作成功")

# 警告信息
logger.warning("⚠️ 这是一个警告")

# 错误信息
logger.error("❌ 发生错误")

# 严重错误
logger.critical("🚨 严重错误")
```

### 3. 异常日志

```python
try:
    result = 1 / 0
except Exception as e:
    # 记录异常信息和堆栈跟踪
    logger.exception("除零错误")

    # 或者使用error并手动添加异常信息
    logger.error(f"计算错误: {e}", exc_info=True)
```

### 4. 结构化日志

```python
# 使用extra参数添加结构化数据
logger.info("用户登录", extra={
    "user_id": 123,
    "username": "john_doe",
    "ip_address": "192.168.1.1",
    "timestamp": "2024-01-01T12:00:00Z"
})
```

## 高级功能

### 1. 函数调用日志装饰器

```python
from src.utils.logger import log_function_call

@log_function_call(level="INFO")
def create_user(username: str, email: str):
    """创建用户。"""
    # 函数逻辑
    return {"id": 1, "username": username, "email": email}

# 调用时会自动记录参数和执行结果
user = create_user("john", "john@example.com")
```

### 2. 执行时间监控

```python
from src.utils.logger import LogExecutionTime

# 使用上下文管理器记录代码块执行时间
with LogExecutionTime("数据库查询", level="DEBUG"):
    # 执行耗时操作
    result = database.query("SELECT * FROM users")
```

### 3. 类中使用Logger

```python
from src.utils.logger import get_logger

class UserService:
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)

    def create_user(self, username: str):
        self.logger.info(f"开始创建用户: {username}")
        try:
            # 创建用户逻辑
            self.logger.success(f"用户创建成功: {username}")
        except Exception as e:
            self.logger.error(f"用户创建失败: {e}")
            raise
```

## 日志格式

### 控制台输出格式

```
2024-01-01 12:00:00 | INFO     | main:read_root:106 - 🏠 访问根路径
```

### 文件输出格式

```
2024-01-01 12:00:00 | INFO     | main:read_root:106 - 🏠 访问根路径
```

### JSON格式（当启用序列化时）

```json
{
  "text": "🏠 访问根路径",
  "record": {
    "elapsed": {
      "repr": "0:00:00.123456",
      "seconds": 0.123456
    },
    "exception": null,
    "extra": {},
    "file": {
      "name": "main.py",
      "path": "/path/to/main.py"
    },
    "function": "read_root",
    "level": {
      "icon": "ℹ️",
      "name": "INFO",
      "no": 20
    },
    "line": 106,
    "message": "🏠 访问根路径",
    "module": "main",
    "name": "main",
    "process": {
      "id": 12345,
      "name": "MainProcess"
    },
    "thread": {
      "id": 67890,
      "name": "MainThread"
    },
    "time": {
      "repr": "2024-01-01 12:00:00.123456+08:00",
      "timestamp": 1704067200.123456
    }
  }
}
```

## HTTP请求日志

应用自动记录所有HTTP请求：

```
📥 GET / - 客户端: 127.0.0.1
📤 GET / - 200 - 0.0123s
```

不同状态码使用不同的图标和日志级别：
- 2xx: 📤 INFO
- 4xx: ⚠️ WARNING
- 5xx: 💥 ERROR

## 应用生命周期日志

应用启动和关闭时的日志：

```
🚀 应用启动中...
✅ 数据库表创建完成
🎉 应用启动完成
🛑 应用关闭中...
👋 应用关闭完成
```

## 异常处理日志

自动记录HTTP异常和未处理的异常：

```
⚠️ HTTP异常: 404 - Not Found - URL: http://localhost:8000/nonexistent
💥 未处理的异常: ValueError: Invalid input - URL: http://localhost:8000/api/test
```

## 最佳实践

1. **使用合适的日志级别**：
   - `DEBUG`: 详细的调试信息
   - `INFO`: 一般信息
   - `SUCCESS`: 成功操作
   - `WARNING`: 警告信息
   - `ERROR`: 错误信息
   - `CRITICAL`: 严重错误

2. **添加上下文信息**：
   ```python
   logger.info("用户操作", extra={"user_id": user_id, "action": "login"})
   ```

3. **使用结构化日志**：便于日志分析和监控

4. **记录异常时包含堆栈跟踪**：
   ```python
   logger.error("操作失败", exc_info=True)
   ```

5. **在类中使用专用logger**：
   ```python
   self.logger = get_logger(self.__class__.__name__)
   ```

6. **使用装饰器记录函数调用**：便于调试和性能分析

7. **监控执行时间**：使用`LogExecutionTime`上下文管理器

## 示例代码

完整的使用示例请参考 `src/utils/logger_example.py` 文件。

## 日志文件管理

- 日志文件位于 `logs/` 目录
- 自动轮转：每天或达到最大大小时创建新文件
- 自动压缩：旧日志文件会被压缩为zip格式
- 自动清理：超过保留期的日志文件会被自动删除
- Git忽略：日志文件已添加到`.gitignore`中
