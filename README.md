# Template Python

一个现代化的 Python 项目模板，集成了完整的代码质量工具链。

## 功能特性

- 🚀 使用 [uv](https://github.com/astral-sh/uv) 进行快速依赖管理
- 🔧 集成 [Ruff](https://github.com/astral-sh/ruff) 进行代码检查和格式化
- 🎨 使用 [Black](https://github.com/psf/black) 进行代码格式化
- 🔍 使用 [MyPy](https://github.com/python/mypy) 进行静态类型检查
- 🪝 配置 [Pre-commit](https://pre-commit.com/) 钩子确保代码质量
- 🔄 GitHub Actions CI/CD 工作流

## 🚀 快速开始

```bash
# 克隆项目
git clone <your-repo-url>
cd template-python

# 安装依赖
uv sync

# 运行项目
uv run python main.py

# 运行测试
uv run pytest
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

## 项目结构

```
.
├── .github/
│   └── workflows/
│       └── ci.yml          # GitHub Actions 工作流
├── .pre-commit-config.yaml # Pre-commit 配置
├── .gitignore
├── .python-version
├── Makefile                # 开发命令
├── README.md
├── main.py                 # 主程序文件
├── pyproject.toml          # 项目配置和工具配置
└── uv.lock                 # 依赖锁定文件
```

## 开发工作流

1. **编写代码** - 在你的编辑器中编写 Python 代码
2. **自动检查** - Pre-commit 钩子会在提交时自动运行检查
3. **手动检查** - 使用 `make check-all` 运行所有检查
4. **修复问题** - 根据工具输出修复代码问题
5. **提交代码** - 提交通过所有检查的代码

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 确保所有检查通过（`make check-all`）
4. 提交更改
5. 创建 Pull Request

## 许可证

[添加你的许可证信息]
