# 数据库配置指南

本项目基于 SQLModel 构建，支持多种数据库后端，提供了灵活的数据库配置方案。

## 🗄️ 支持的数据库

- **SQLite**：轻量级文件数据库，适合开发和测试
- **PostgreSQL**：功能强大的关系型数据库，推荐生产环境
- **MySQL**：流行的关系型数据库，可选生产环境

## ⚙️ 配置方式

### 环境变量配置

数据库配置通过环境变量进行管理，主要配置项：

```env
# 数据库连接 URL
DATABASE_URL=sqlite:///./app.db

# 测试数据库（建议使用内存 SQLite）
TEST_DATABASE_URL=sqlite:///:memory:

# 数据库调试（开启 SQL 查询日志）
DB_ECHO=false

# 连接池配置（仅适用于 PostgreSQL/MySQL）
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600
```

### 数据库 URL 格式

```bash
# SQLite
sqlite:///./app.db          # 相对路径
sqlite:////absolute/path/to/app.db  # 绝对路径
sqlite:///:memory:          # 内存数据库

# PostgreSQL
postgresql://user:password@localhost:5432/dbname
postgresql+psycopg2://user:password@localhost:5432/dbname

# MySQL
mysql://user:password@localhost:3306/dbname
mysql+pymysql://user:password@localhost:3306/dbname
```

## 🔄 数据库切换

### 从 SQLite 切换到 PostgreSQL

1. **安装 PostgreSQL 驱动**
   ```bash
   # 添加到 pyproject.toml dependencies
   uv add psycopg2-binary
   ```

2. **启动 PostgreSQL 服务**
   ```bash
   # 使用 Docker（推荐）
   cd docker
   docker-compose up -d db

   # 或本地安装
   brew install postgresql
   brew services start postgresql
   createdb template_db
   ```

3. **更新环境变量**
   ```env
   DATABASE_URL=postgresql://postgres:password@localhost:5432/template_db
   ```

4. **重建数据库表**
   ```bash
   python rebuild_db.py
   ```

### 从 SQLite 切换到 MySQL

1. **安装 MySQL 驱动**
   ```bash
   uv add pymysql
   ```

2. **启动 MySQL 服务**
   ```bash
   # 使用 Docker
   docker run -d --name mysql \
     -e MYSQL_ROOT_PASSWORD=password \
     -e MYSQL_DATABASE=template_db \
     -p 3306:3306 mysql:8.0
   ```

3. **更新环境变量**
   ```env
   DATABASE_URL=mysql+pymysql://root:password@localhost:3306/template_db
   ```

4. **重建数据库表**
   ```bash
   python rebuild_db.py
   ```

## 🏗️ 数据库架构

### 模型定义

项目使用 SQLModel 定义数据模型，位于 `src/models/` 目录：

- `base.py` - 基础模型类
- `user.py` - 用户模型
- `hero.py` - 英雄模型

### 自动表创建

应用启动时会自动创建数据库表：

```python
from src.db.connection import db

# 创建所有表
db.create_tables()
```

### 数据库会话管理

```python
from src.db.connection import db

# 使用上下文管理器
with db.session() as session:
    user = session.get(User, 1)
    print(user.name)

# FastAPI 依赖注入
from fastapi import Depends
from sqlmodel import Session

@app.get("/users/{user_id}")
def get_user(user_id: int, session: Session = Depends(db.get_session)):
    return session.get(User, user_id)
```

## 🔧 高级配置

### 连接池配置

对于 PostgreSQL 和 MySQL，可以配置连接池参数：

```env
# 连接池大小
DB_POOL_SIZE=5

# 最大溢出连接数
DB_MAX_OVERFLOW=10

# 连接池超时时间（秒）
DB_POOL_TIMEOUT=30

# 连接回收时间（秒）
DB_POOL_RECYCLE=3600
```

### 数据库调试

开启 SQL 查询日志：

```env
DB_ECHO=true
```

这会在控制台输出所有 SQL 查询语句，便于调试。

### 测试数据库

测试时使用独立的数据库配置：

```env
# 推荐使用内存 SQLite，速度快且隔离性好
TEST_DATABASE_URL=sqlite:///:memory:
```

## 🐳 Docker 环境

### 生产环境

Docker Compose 已配置好 PostgreSQL：

```yaml
services:
  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=template_db
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
```

### 开发环境

开发环境默认使用 SQLite，无需额外配置。

## 📊 数据迁移

### 备份数据

```bash
# SQLite 备份
cp app.db app.db.backup

# PostgreSQL 备份
docker-compose exec db pg_dump -U postgres template_db > backup.sql

# MySQL 备份
docker exec mysql mysqldump -u root -p template_db > backup.sql
```

### 恢复数据

```bash
# SQLite 恢复
cp app.db.backup app.db

# PostgreSQL 恢复
docker-compose exec -T db psql -U postgres template_db < backup.sql

# MySQL 恢复
docker exec -i mysql mysql -u root -p template_db < backup.sql
```

## 🔍 故障排除

### 常见问题

1. **连接失败**
   - 检查数据库服务是否启动
   - 验证连接 URL 格式
   - 确认用户名密码正确

2. **权限错误**
   - 确保数据库用户有足够权限
   - 检查文件系统权限（SQLite）

3. **编码问题**
   - 确保数据库使用 UTF-8 编码
   - 检查连接 URL 中的编码参数

### 调试技巧

```python
# 测试数据库连接
from src.db.connection import db

try:
    with db.session() as session:
        result = session.execute("SELECT 1")
        print("数据库连接成功！")
except Exception as e:
    print(f"数据库连接失败：{e}")
```

## 📚 相关资源

- [SQLModel 官方文档](https://sqlmodel.tiangolo.com/)
- [SQLAlchemy 文档](https://docs.sqlalchemy.org/)
- [PostgreSQL 文档](https://www.postgresql.org/docs/)
- [MySQL 文档](https://dev.mysql.com/doc/)
