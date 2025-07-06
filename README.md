# Template Python

一个现代化的 Python 项目模板，基于 FastAPI + SQLModel，集成了完整的开发工具链和最佳实践。

## ✨ 功能特性

### 🚀 核心框架
- **FastAPI**: 高性能异步 Web 框架
- **SQLModel**: 现代化 ORM，支持 SQLite/PostgreSQL
- **Pydantic**: 数据验证和序列化
- **Uvicorn**: ASGI 服务器

### 🛠️ 开发工具
- **uv**: 极速 Python 包管理器
- **Ruff**: 快速代码检查和格式化
- **Black**: 代码格式化
- **MyPy**: 静态类型检查
- **Pre-commit**: Git 钩子确保代码质量

### 📊 监控与日志
- **Loguru**: 强大的日志系统
- **结构化日志**: 支持 JSON 格式
- **请求监控**: 自动记录 HTTP 请求
- **性能分析**: 执行时间监控

### 🐳 部署方案
- **Docker**: 完整的容器化部署
- **Docker Compose**: 多服务编排
- **PostgreSQL**: 生产级数据库
- **Redis**: 缓存支持

### 🧪 测试体系
- **Pytest**: 现代化测试框架
- **异步测试**: 支持 async/await
- **API 测试**: FastAPI TestClient
- **数据库测试**: 内存 SQLite

## 🚀 快速开始

### 本地开发

```bash
# 克隆项目
git clone <your-repo-url>
cd template-python

# 安装依赖
uv sync

# 启动应用
uv run python main.py

# 访问 API 文档
# Swagger UI: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
```

### Docker 部署

```bash
# 生产环境（PostgreSQL + Redis）
cd docker
docker-compose up -d

# 开发环境（SQLite）
docker-compose -f docker-compose.dev.yml up -d
```

### 数据库切换

```bash
# 使用 PostgreSQL（推荐生产环境）
cp .env.example .env
# 编辑 .env 文件，设置 DATABASE_URL=postgresql://...

# 重建数据库
python rebuild_db.py
```

### 安装依赖

```bash
# 安装生产依赖
uv sync --no-dev

# 安装开发依赖
uv sync
```

### 开发工具

#### 使用 Makefile（推荐）

```bash
# 安装依赖
make install

# 代码格式化
make format

# 代码检查
make lint

# 类型检查
make type-check

# 运行测试
make test

# 运行测试（详细输出）
make test-verbose

# 运行测试并生成覆盖率报告
make test-cov

# 运行特定类型的测试
make test-unit        # 单元测试
make test-integration # 集成测试
make test-api         # API 测试

# 运行所有检查（包括测试）
make check-all

# 清理缓存
make clean
```

#### 直接使用工具

```bash
# Ruff - 代码检查和格式化
uv run ruff check .          # 检查代码
uv run ruff check . --fix    # 检查并自动修复
uv run ruff format .         # 格式化代码

# Black - 代码格式化
uv run black .               # 格式化代码
uv run black --check .       # 检查格式（不修改）

# MyPy - 类型检查
uv run mypy .                # 运行类型检查

# Pre-commit
uv run pre-commit run --all-files  # 运行所有钩子
uv run pre-commit install           # 安装钩子
```

## 🧪 测试

项目使用 **pytest** 作为测试框架，支持单元测试、集成测试和 API 测试。

### 测试结构

```
tests/
├── __init__.py          # 测试包初始化
├── test_main.py         # 主模块测试
├── test_api.py          # FastAPI 应用测试
└── test_models.py       # SQLModel 数据库模型测试
```

### 运行测试

```bash
# 运行所有测试
uv run pytest

# 详细输出
uv run pytest -v

# 运行特定测试文件
uv run pytest tests/test_api.py

# 运行特定测试类
uv run pytest tests/test_api.py::TestFastAPIApp

# 运行特定测试方法
uv run pytest tests/test_api.py::TestFastAPIApp::test_read_root

# 按标记运行测试
uv run pytest -m unit
uv run pytest -m api
uv run pytest -m integration
```

### 测试覆盖率

```bash
# 生成覆盖率报告
uv run pytest --cov=. --cov-report=html --cov-report=term

# 查看 HTML 覆盖率报告
open htmlcov/index.html
```

### 测试特性

- **单元测试**：测试独立的函数和类
- **API 测试**：使用 FastAPI TestClient 测试 API 端点
- **数据库测试**：使用内存 SQLite 数据库测试 SQLModel 模型
- **异步测试**：支持 async/await 测试
- **测试标记**：使用 pytest 标记组织和筛选测试

## 🔧 工具配置

所有工具的配置都在 `pyproject.toml` 文件中：

### Ruff 配置
- 启用了推荐的规则集（pycodestyle、pyflakes、isort 等）
- 行长度限制为 88 字符
- 针对 Python 3.11+ 优化
- 为测试文件和 `__init__.py` 提供特殊规则

### Black 配置
- 行长度限制为 88 字符
- 目标 Python 版本 3.11
- 排除构建和分发目录

### MyPy 配置
- 严格模式启用
- 要求所有函数都有类型注解
- 启用各种警告和检查
- 忽略测试文件的类型错误

## Pre-commit 钩子

项目配置了以下 pre-commit 钩子：

1. **Ruff** - 代码检查和格式化
2. **Black** - 代码格式化
3. **MyPy** - 类型检查
4. **通用钩子** - 文件格式检查、语法检查等

### 安装和使用

```bash
# 安装 pre-commit 钩子
uv run pre-commit install

# 手动运行所有钩子
uv run pre-commit run --all-files

# 更新钩子版本
uv run pre-commit autoupdate
```

## CI/CD

项目包含 GitHub Actions 工作流（`.github/workflows/ci.yml`），会在每次推送和 PR 时自动运行：

- 代码检查（Ruff）
- 格式检查（Ruff + Black）
- 类型检查（MyPy）
- Pre-commit 钩子验证

## 📁 项目架构

```
.
├── src/                    # 源代码目录
│   ├── api/               # API 路由
│   │   └── v1/           # API v1 版本
│   │       └── endpoints/ # API 端点
│   ├── db/               # 数据库配置
│   ├── models/           # 数据模型
│   └── utils/            # 工具函数
├── tests/                 # 测试代码
├── docker/               # Docker 配置
├── docs/                 # 项目文档
├── logs/                 # 日志文件
├── uploads/              # 文件上传目录
├── main.py               # 应用入口
├── pyproject.toml        # 项目配置
└── Makefile             # 开发命令
```

## 🌐 API 端点

### 核心端点
- `GET /` - 欢迎页面
- `GET /api/v1/health` - 健康检查
- `GET /docs` - Swagger UI 文档
- `GET /redoc` - ReDoc 文档

### 用户管理
- `GET /api/v1/users` - 获取用户列表
- `POST /api/v1/users` - 创建用户
- `GET /api/v1/users/{user_id}` - 获取用户详情
- `PUT /api/v1/users/{user_id}` - 更新用户
- `DELETE /api/v1/users/{user_id}` - 删除用户

### 英雄管理
- `GET /api/v1/heroes` - 获取英雄列表
- `POST /api/v1/heroes` - 创建英雄
- `GET /api/v1/heroes/{hero_id}` - 获取英雄详情
- `PUT /api/v1/heroes/{hero_id}` - 更新英雄
- `DELETE /api/v1/heroes/{hero_id}` - 删除英雄

### 文件管理
- `POST /api/v1/files/upload` - 单文件上传
- `POST /api/v1/files/upload-multiple` - 多文件上传
- `GET /api/v1/files/{file_id}/download` - 文件下载
- `GET /api/v1/files/stats` - 上传统计

## ⚙️ 环境配置

### 环境变量

复制 `.env.example` 到 `.env` 并根据需要修改：

```bash
cp .env.example .env
```

主要配置项：

```env
# 数据库配置
DATABASE_URL=sqlite:///./app.db  # 开发环境
# DATABASE_URL=postgresql://user:pass@localhost:5432/db  # 生产环境

# 应用配置
APP_NAME=FastAPI Template
DEBUG=false

# 日志配置
LOG_LEVEL=INFO
LOG_TO_CONSOLE=true
LOG_TO_FILE=true
```

### 数据库配置

项目支持多种数据库：

- **SQLite**（默认）：适合开发和测试
- **PostgreSQL**：推荐生产环境
- **MySQL**：可选生产环境

切换数据库只需修改 `DATABASE_URL` 环境变量。

## 📚 文档导航

### 项目概览
- [项目概览](docs/overview.md) - 项目架构和设计理念
- [开发指南](docs/development.md) - 开发环境搭建和开发流程

### 开发指南
- [API 开发指南](docs/api-guide.md) - API 端点开发和最佳实践
- [数据库配置](docs/database.md) - 数据库设置和迁移指南
- [配置说明](docs/configuration.md) - 开发工具配置详解
- [日志系统](docs/logging.md) - Loguru 日志使用指南

### 部署指南
- [部署指南](docs/deployment.md) - 生产环境部署完整方案
- [Docker 部署](docs/docker.md) - 容器化部署快速指南

### 快速参考
- [快速参考](docs/quick-reference.md) - 常用命令和配置速查

### 📋 其他资源
- [更新日志](CHANGELOG.md) - 版本变更记录
- [Makefile 命令](Makefile) - 常用开发命令
- [环境变量](.env.example) - 配置参数说明

## 🔄 开发工作流

1. **环境准备**
   ```bash
   uv sync                    # 安装依赖
   cp .env.example .env       # 配置环境
   uv run pre-commit install  # 安装 Git 钩子
   ```

2. **开发代码**
   ```bash
   uv run python main.py      # 启动开发服务器
   # 访问 http://localhost:8000/docs
   ```

3. **代码检查**
   ```bash
   make format               # 格式化代码
   make lint                 # 代码检查
   make type-check          # 类型检查
   make test                # 运行测试
   ```

4. **提交代码**
   ```bash
   git add .
   git commit -m "feat: 添加新功能"
   # Pre-commit 钩子会自动运行检查
   ```

## 🤝 贡献指南

1. **Fork 项目**并创建功能分支
2. **遵循代码规范**：使用 Ruff + Black + MyPy
3. **编写测试**：确保新功能有对应测试
4. **更新文档**：如有必要更新相关文档
5. **提交 PR**：确保所有检查通过

### 提交规范

使用 [Conventional Commits](https://conventionalcommits.org/) 规范：

- `feat:` 新功能
- `fix:` 修复 bug
- `docs:` 文档更新
- `style:` 代码格式
- `refactor:` 重构
- `test:` 测试相关
- `chore:` 构建/工具相关

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件
