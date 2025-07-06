# 开发指南

本文档详细说明了项目的开发环境搭建、开发流程和最佳实践。

## 🚀 快速开始

### 环境要求

- **Python**: 3.11+
- **uv**: 最新版本 (推荐的包管理器)
- **Docker**: 可选，用于数据库服务
- **Git**: 版本控制

### 环境搭建

#### 1. 克隆项目

```bash
git clone <repository-url>
cd template-python
```

#### 2. 安装 uv (如果未安装)

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 或使用 pip
pip install uv
```

#### 3. 创建虚拟环境并安装依赖

```bash
# 创建虚拟环境
uv venv

# 激活虚拟环境
# macOS/Linux
source .venv/bin/activate
# Windows
.venv\Scripts\activate

# 安装依赖
uv pip install -r requirements.txt

# 安装开发依赖
uv pip install -r requirements-dev.txt
```

#### 4. 环境配置

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑环境变量
vim .env
```

#### 5. 数据库初始化

```bash
# 使用 SQLite (默认)
python -m src.main

# 或使用 Docker PostgreSQL
docker-compose -f docker/docker-compose.yml up -d db
# 修改 .env 中的 DATABASE_URL
# DATABASE_URL=postgresql://postgres:password@localhost:5432/template_db
```

#### 6. 启动开发服务器

```bash
# 使用 uvicorn 直接启动
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# 或使用 Makefile
make dev

# 或使用 Python 模块
python -m src.main
```

#### 7. 验证安装

访问以下地址验证安装：

- **API 文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health
- **API 根路径**: http://localhost:8000/api/v1/

## 🛠️ 开发工具

### 代码质量工具

项目集成了多个代码质量工具，确保代码的一致性和质量：

#### Ruff - 代码检查和格式化

```bash
# 检查代码
ruff check .

# 自动修复
ruff check . --fix

# 格式化代码
ruff format .
```

#### Black - 代码格式化

```bash
# 格式化代码
black .

# 检查格式
black . --check

# 查看差异
black . --diff
```

#### MyPy - 类型检查

```bash
# 类型检查
mypy .

# 检查特定文件
mypy src/main.py
```

#### 一键运行所有检查

```bash
# 使用 Makefile
make lint

# 或手动运行
ruff check . && black . --check && mypy .
```

### Pre-commit 钩子

项目配置了 pre-commit 钩子，在提交代码前自动运行代码质量检查：

```bash
# 安装 pre-commit
pip install pre-commit

# 安装钩子
pre-commit install

# 手动运行所有钩子
pre-commit run --all-files
```

## 🧪 测试

### 测试结构

```
tests/
├── conftest.py              # 测试配置和 fixtures
├── test_main.py            # 主应用测试
├── api/
│   └── v1/
│       ├── test_health.py  # 健康检查测试
│       ├── test_users.py   # 用户 API 测试
│       └── test_heroes.py  # 英雄 API 测试
├── models/
│   ├── test_user.py        # 用户模型测试
│   └── test_hero.py        # 英雄模型测试
└── utils/
    ├── test_logger.py      # 日志工具测试
    └── test_pagination.py  # 分页工具测试
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_main.py

# 运行特定测试函数
pytest tests/test_main.py::test_health_check

# 运行测试并显示覆盖率
pytest --cov=src

# 生成 HTML 覆盖率报告
pytest --cov=src --cov-report=html

# 使用 Makefile
make test
make test-cov
```

### 测试最佳实践

#### 1. 测试命名

```python
# 好的测试命名
def test_create_user_with_valid_data_should_return_201():
    pass

def test_get_user_with_invalid_id_should_return_404():
    pass

# 避免的命名
def test_user():
    pass

def test_1():
    pass
```

#### 2. 使用 Fixtures

```python
# conftest.py
import pytest
from fastapi.testclient import TestClient
from src.main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def sample_user():
    return {
        "name": "Test User",
        "email": "test@example.com"
    }

# test_users.py
def test_create_user(client, sample_user):
    response = client.post("/api/v1/users/", json=sample_user)
    assert response.status_code == 201
```

#### 3. 数据库测试

```python
# 使用内存数据库进行测试
import pytest
from sqlmodel import create_engine, Session
from src.db.connection import get_session
from src.main import app

@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    with Session(engine) as session:
        yield session

@pytest.fixture
def client(session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    yield TestClient(app)
    app.dependency_overrides.clear()
```

## 📁 项目结构

### 目录组织原则

1. **功能模块化**: 按功能组织代码，而不是按技术层次
2. **清晰分层**: API、业务逻辑、数据访问分层清晰
3. **可测试性**: 每个模块都有对应的测试
4. **可扩展性**: 新功能可以独立添加

### 添加新功能模块

#### 1. 创建数据模型

```python
# src/models/product.py
from sqlmodel import SQLModel, Field
from typing import Optional

class ProductBase(SQLModel):
    name: str
    description: Optional[str] = None
    price: float

class Product(ProductBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

class ProductCreate(ProductBase):
    pass

class ProductRead(ProductBase):
    id: int

class ProductUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
```

#### 2. 创建 API 端点

```python
# src/api/v1/endpoints/products.py
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from src.db.connection import get_session
from src.models.product import Product, ProductCreate, ProductRead, ProductUpdate
from src.utils.api_response import create_response

router = APIRouter()

@router.post("/", response_model=ProductRead)
def create_product(
    product: ProductCreate,
    session: Session = Depends(get_session)
):
    db_product = Product.model_validate(product)
    session.add(db_product)
    session.commit()
    session.refresh(db_product)
    return db_product

@router.get("/{product_id}", response_model=ProductRead)
def get_product(
    product_id: int,
    session: Session = Depends(get_session)
):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
```

#### 3. 注册路由

```python
# src/api/v1/api.py
from fastapi import APIRouter
from src.api.v1.endpoints import health, users, heroes, products

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(heroes.router, prefix="/heroes", tags=["heroes"])
api_router.include_router(products.router, prefix="/products", tags=["products"])  # 新增
```

#### 4. 添加测试

```python
# tests/api/v1/test_products.py
import pytest
from fastapi.testclient import TestClient

def test_create_product(client: TestClient):
    product_data = {
        "name": "Test Product",
        "description": "A test product",
        "price": 99.99
    }
    response = client.post("/api/v1/products/", json=product_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == product_data["name"]
    assert "id" in data

def test_get_product(client: TestClient):
    # 先创建产品
    product_data = {"name": "Test Product", "price": 99.99}
    create_response = client.post("/api/v1/products/", json=product_data)
    product_id = create_response.json()["id"]

    # 获取产品
    response = client.get(f"/api/v1/products/{product_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == product_id
```

## 🔧 配置管理

### 环境变量

项目使用环境变量进行配置管理，支持多环境部署：

```bash
# .env 文件示例

# 应用配置
APP_NAME="Template Python"
APP_VERSION="1.0.0"
DEBUG=true
ENVIRONMENT=development

# 数据库配置
DATABASE_URL=sqlite:///./template.db
# DATABASE_URL=postgresql://user:password@localhost:5432/dbname
# DATABASE_URL=mysql://user:password@localhost:3306/dbname

# 日志配置
LOG_LEVEL=INFO
LOG_FORMAT=console
LOG_FILE_ENABLED=false
LOG_FILE_PATH=logs/app.log

# API 配置
API_V1_PREFIX=/api/v1
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080"]

# 安全配置
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 配置类

```python
# src/config.py
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # 应用配置
    app_name: str = "Template Python"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "production"

    # 数据库配置
    database_url: str = "sqlite:///./template.db"

    # 日志配置
    log_level: str = "INFO"
    log_format: str = "console"
    log_file_enabled: bool = False
    log_file_path: str = "logs/app.log"

    # API 配置
    api_v1_prefix: str = "/api/v1"
    cors_origins: List[str] = ["*"]

    # 安全配置
    secret_key: str = "your-secret-key-here"
    access_token_expire_minutes: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
```

## 🔍 调试技巧

### 日志调试

```python
from src.utils.logger import get_logger

logger = get_logger(__name__)

# 基本日志
logger.info("Processing user request")
logger.warning("Invalid input detected")
logger.error("Database connection failed")

# 结构化日志
logger.info("User created", extra={
    "user_id": user.id,
    "email": user.email,
    "action": "create_user"
})

# 异常日志
try:
    # 一些操作
    pass
except Exception as e:
    logger.exception("Unexpected error occurred")
```

### 断点调试

```python
# 使用 pdb
import pdb; pdb.set_trace()

# 使用 ipdb (更好的体验)
import ipdb; ipdb.set_trace()

# 使用 breakpoint() (Python 3.7+)
breakpoint()
```

### API 调试

```python
# 在端点中添加调试信息
@router.post("/users/")
def create_user(user: UserCreate, session: Session = Depends(get_session)):
    logger.info(f"Creating user: {user.model_dump()}")

    # 调试数据库查询
    existing_user = session.exec(
        select(User).where(User.email == user.email)
    ).first()
    logger.debug(f"Existing user check: {existing_user}")

    if existing_user:
        logger.warning(f"User already exists: {user.email}")
        raise HTTPException(status_code=400, detail="User already exists")

    db_user = User.model_validate(user)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    logger.info(f"User created successfully: {db_user.id}")
    return db_user
```

## 🚀 部署准备

### 生产环境检查清单

- [ ] **环境变量**: 所有敏感信息使用环境变量
- [ ] **数据库**: 使用生产级数据库 (PostgreSQL)
- [ ] **日志**: 配置适当的日志级别和输出
- [ ] **安全**: 更新默认密钥和安全配置
- [ ] **测试**: 所有测试通过
- [ ] **文档**: API 文档和部署文档更新

### Docker 构建

```bash
# 构建生产镜像
docker build -f docker/Dockerfile -t template-python:latest .

# 运行生产环境
docker-compose -f docker/docker-compose.yml up -d

# 查看日志
docker-compose -f docker/docker-compose.yml logs -f app
```

### 性能优化

```python
# 数据库连接池配置
from sqlmodel import create_engine

engine = create_engine(
    database_url,
    pool_size=20,          # 连接池大小
    max_overflow=30,       # 最大溢出连接
    pool_timeout=30,       # 获取连接超时
    pool_recycle=3600,     # 连接回收时间
    echo=False             # 生产环境关闭 SQL 日志
)
```

## 📚 学习资源

### 官方文档

- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [SQLModel 文档](https://sqlmodel.tiangolo.com/)
- [Pydantic 文档](https://docs.pydantic.dev/)
- [Pytest 文档](https://docs.pytest.org/)

### 最佳实践

- [FastAPI 最佳实践](https://github.com/zhanymkanov/fastapi-best-practices)
- [Python 类型提示](https://docs.python.org/3/library/typing.html)
- [RESTful API 设计](https://restfulapi.net/)

### 工具文档

- [Ruff 文档](https://docs.astral.sh/ruff/)
- [Black 文档](https://black.readthedocs.io/)
- [MyPy 文档](https://mypy.readthedocs.io/)
- [uv 文档](https://docs.astral.sh/uv/)

## 🤝 贡献指南

### 开发流程

1. **Fork 项目**
2. **创建功能分支**: `git checkout -b feature/new-feature`
3. **编写代码**: 遵循项目代码规范
4. **添加测试**: 确保新功能有测试覆盖
5. **运行测试**: `make test` 确保所有测试通过
6. **代码检查**: `make lint` 确保代码质量
7. **提交代码**: 使用清晰的提交信息
8. **创建 PR**: 详细描述变更内容

### 代码规范

- 使用类型提示
- 编写文档字符串
- 遵循 PEP 8 规范
- 保持函数简洁
- 添加适当的测试

### 提交信息规范

```
type(scope): description

[optional body]

[optional footer]
```

类型:
- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `style`: 代码格式化
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

示例:
```
feat(api): add user authentication endpoint

Add JWT-based authentication for user login and registration.
Includes password hashing and token validation.

Closes #123
```
