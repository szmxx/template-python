# API 开发指南

本项目基于 FastAPI 构建，提供了现代化的 RESTful API 开发体验。本指南将帮助你快速上手 API 开发。

## 🚀 FastAPI 特性

- **高性能**：基于 Starlette 和 Pydantic，性能媲美 NodeJS 和 Go
- **自动文档**：自动生成 OpenAPI/Swagger 文档
- **类型安全**：基于 Python 类型提示的数据验证
- **异步支持**：原生支持 async/await
- **依赖注入**：强大的依赖注入系统

## 📁 API 结构

```
src/api/
├── __init__.py
└── v1/
    ├── __init__.py
    ├── api.py              # API 路由汇总
    └── endpoints/
        ├── __init__.py
        ├── users.py        # 用户相关端点
        ├── heroes.py       # 英雄相关端点
        └── files.py        # 文件相关端点
```

## 🛠️ 创建新的 API 端点

### 1. 定义数据模型

首先在 `src/models/` 中定义数据模型：

```python
# src/models/product.py
from typing import Optional
from sqlmodel import SQLModel, Field

class ProductBase(SQLModel):
    name: str = Field(max_length=100)
    description: Optional[str] = None
    price: float = Field(gt=0)
    category: str

class Product(ProductBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

class ProductCreate(ProductBase):
    pass

class ProductUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None

class ProductResponse(ProductBase):
    id: int
```

### 2. 创建 API 端点

在 `src/api/v1/endpoints/` 中创建新的端点文件：

```python
# src/api/v1/endpoints/products.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from src.db.connection import db
from src.models.product import Product, ProductCreate, ProductUpdate, ProductResponse
from src.utils.pagination import PaginationParams, paginate
from src.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()

@router.get("/", response_model=List[ProductResponse])
def get_products(
    pagination: PaginationParams = Depends(),
    category: Optional[str] = Query(None, description="按分类筛选"),
    session: Session = Depends(db.get_session)
):
    """获取产品列表。"""
    logger.info("获取产品列表", extra={"category": category})

    query = select(Product)
    if category:
        query = query.where(Product.category == category)

    return paginate(session, query, pagination)

@router.post("/", response_model=ProductResponse, status_code=201)
def create_product(
    product: ProductCreate,
    session: Session = Depends(db.get_session)
):
    """创建新产品。"""
    logger.info("创建产品", extra={"product_name": product.name})

    db_product = Product.model_validate(product)
    session.add(db_product)
    session.commit()
    session.refresh(db_product)

    logger.success(f"产品创建成功: {db_product.id}")
    return db_product

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    session: Session = Depends(db.get_session)
):
    """获取产品详情。"""
    product = session.get(Product, product_id)
    if not product:
        logger.warning(f"产品不存在: {product_id}")
        raise HTTPException(status_code=404, detail="产品不存在")

    return product

@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_update: ProductUpdate,
    session: Session = Depends(db.get_session)
):
    """更新产品信息。"""
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")

    update_data = product_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)

    session.add(product)
    session.commit()
    session.refresh(product)

    logger.info(f"产品更新成功: {product_id}")
    return product

@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    session: Session = Depends(db.get_session)
):
    """删除产品。"""
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")

    session.delete(product)
    session.commit()

    logger.info(f"产品删除成功: {product_id}")
    return {"message": "产品删除成功"}
```

### 3. 注册路由

在 `src/api/v1/api.py` 中注册新的路由：

```python
# src/api/v1/api.py
from fastapi import APIRouter

from .endpoints import users, heroes, files, products  # 添加 products

api_router = APIRouter()

api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(heroes.router, prefix="/heroes", tags=["heroes"])
api_router.include_router(files.router, prefix="/files", tags=["files"])
api_router.include_router(products.router, prefix="/products", tags=["products"])  # 添加这行
```

## 🔧 常用功能

### 数据验证

FastAPI 基于 Pydantic 提供强大的数据验证：

```python
from pydantic import validator, Field
from typing import Optional

class ProductCreate(SQLModel):
    name: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., gt=0, le=10000)
    email: Optional[str] = Field(None, regex=r'^[\w\.-]+@[\w\.-]+\.\w+$')

    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('产品名称不能为空')
        return v.strip()
```

### 查询参数

```python
from fastapi import Query
from typing import Optional

@router.get("/")
def get_products(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(10, ge=1, le=100, description="返回的记录数"),
    search: Optional[str] = Query(None, min_length=1, description="搜索关键词"),
    category: Optional[str] = Query(None, description="产品分类")
):
    pass
```

### 路径参数

```python
from fastapi import Path

@router.get("/{product_id}")
def get_product(
    product_id: int = Path(..., gt=0, description="产品ID")
):
    pass
```

### 请求体

```python
from fastapi import Body

@router.post("/")
def create_product(
    product: ProductCreate,
    metadata: dict = Body(..., description="额外元数据")
):
    pass
```

### 文件上传

```python
from fastapi import File, UploadFile
from typing import List

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(..., description="上传的文件")
):
    content = await file.read()
    return {"filename": file.filename, "size": len(content)}

@router.post("/upload-multiple")
async def upload_multiple_files(
    files: List[UploadFile] = File(..., description="多个文件")
):
    results = []
    for file in files:
        content = await file.read()
        results.append({"filename": file.filename, "size": len(content)})
    return results
```

## 🔐 认证和授权

### JWT 认证示例

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="无效的认证凭据")
        return user_id
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="无效的认证凭据")

@router.get("/protected")
def protected_endpoint(current_user: int = Depends(get_current_user)):
    return {"message": f"Hello user {current_user}"}
```

## 📝 响应模型

### 自定义响应

```python
from src.utils.api_response import APIResponse

@router.get("/", response_model=APIResponse[List[ProductResponse]])
def get_products():
    products = [...]
    return APIResponse.success(data=products, message="获取成功")

@router.post("/", response_model=APIResponse[ProductResponse])
def create_product(product: ProductCreate):
    try:
        # 创建逻辑
        return APIResponse.success(data=new_product, message="创建成功")
    except Exception as e:
        return APIResponse.error(message=str(e))
```

### 状态码

```python
from fastapi import status

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_product():
    pass

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product():
    pass
```

## 🧪 API 测试

### 单元测试

```python
# tests/test_products.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_create_product():
    response = client.post(
        "/api/v1/products/",
        json={
            "name": "测试产品",
            "price": 99.99,
            "category": "电子产品"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "测试产品"
    assert data["price"] == 99.99

def test_get_products():
    response = client.get("/api/v1/products/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_product_not_found():
    response = client.get("/api/v1/products/999")
    assert response.status_code == 404
```

### 集成测试

```python
@pytest.mark.asyncio
async def test_product_workflow():
    # 创建产品
    create_response = client.post("/api/v1/products/", json={...})
    product_id = create_response.json()["id"]

    # 获取产品
    get_response = client.get(f"/api/v1/products/{product_id}")
    assert get_response.status_code == 200

    # 更新产品
    update_response = client.put(f"/api/v1/products/{product_id}", json={...})
    assert update_response.status_code == 200

    # 删除产品
    delete_response = client.delete(f"/api/v1/products/{product_id}")
    assert delete_response.status_code == 200
```

## 📚 最佳实践

### 1. 错误处理

```python
from fastapi import HTTPException
from src.utils.logger import get_logger

logger = get_logger(__name__)

@router.post("/")
def create_product(product: ProductCreate):
    try:
        # 业务逻辑
        return new_product
    except ValueError as e:
        logger.warning(f"数据验证错误: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"创建产品失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="内部服务器错误")
```

### 2. 日志记录

```python
from src.utils.logger import get_logger, log_function_call

logger = get_logger(__name__)

@log_function_call(level="INFO")
@router.post("/")
def create_product(product: ProductCreate):
    logger.info("开始创建产品", extra={
        "product_name": product.name,
        "category": product.category
    })

    # 业务逻辑

    logger.success(f"产品创建成功: {new_product.id}")
    return new_product
```

### 3. 依赖注入

```python
from fastapi import Depends

def get_product_service() -> ProductService:
    return ProductService()

@router.post("/")
def create_product(
    product: ProductCreate,
    service: ProductService = Depends(get_product_service)
):
    return service.create(product)
```

### 4. 分页

```python
from src.utils.pagination import PaginationParams, paginate

@router.get("/")
def get_products(
    pagination: PaginationParams = Depends(),
    session: Session = Depends(db.get_session)
):
    query = select(Product)
    return paginate(session, query, pagination)
```

## 🔍 调试技巧

### 1. 启用调试模式

```env
DEBUG=true
DB_ECHO=true
LOG_LEVEL=DEBUG
```

### 2. 使用调试器

```python
import pdb

@router.post("/")
def create_product(product: ProductCreate):
    pdb.set_trace()  # 设置断点
    # 业务逻辑
```

### 3. 查看生成的 OpenAPI 文档

访问 `http://localhost:8000/openapi.json` 查看生成的 OpenAPI 规范。

## 📖 相关资源

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [Pydantic 文档](https://docs.pydantic.dev/)
- [SQLModel 文档](https://sqlmodel.tiangolo.com/)
- [OpenAPI 规范](https://swagger.io/specification/)
