# 快速参考

本文档提供项目开发和部署过程中的常用命令、配置和故障排除方法的快速查询。

## 🚀 快速命令

### 项目启动

```bash
# 本地开发启动
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# 使用 Makefile
make dev

# Docker 开发环境
docker-compose -f docker/docker-compose.yml -f docker/docker-compose.dev.yml up -d

# Docker 生产环境
docker-compose -f docker/docker-compose.yml up -d
```

### 依赖管理

```bash
# 安装依赖
uv pip install -r requirements.txt
uv pip install -r requirements-dev.txt

# 添加新依赖
uv add package-name
uv add --dev package-name

# 更新依赖
uv pip install --upgrade package-name

# 生成依赖文件
uv pip freeze > requirements.txt
```

### 代码质量检查

```bash
# 一键检查所有
make lint

# 分别运行
ruff check .                    # 代码检查
ruff check . --fix             # 自动修复
ruff format .                   # 代码格式化
black .                         # Black 格式化
mypy .                          # 类型检查
```

### 测试命令

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_main.py
pytest tests/test_main.py::test_health_check

# 测试覆盖率
pytest --cov=src
pytest --cov=src --cov-report=html

# 使用 Makefile
make test
make test-cov
```

### Docker 命令

```bash
# 构建镜像
docker build -f docker/Dockerfile -t template-python:latest .

# 运行容器
docker run -p 8000:8000 template-python:latest

# 查看日志
docker-compose logs -f app

# 进入容器
docker-compose exec app /bin/bash

# 重建服务
docker-compose up -d --build app

# 清理资源
docker-compose down -v
docker system prune -f
```

### 数据库命令

```bash
# PostgreSQL 连接
psql -h localhost -p 5432 -U postgres -d template_db

# 数据库备份
docker-compose exec db pg_dump -U postgres template_db > backup.sql

# 数据库恢复
docker-compose exec -T db psql -U postgres template_db < backup.sql

# 查看数据库状态
docker-compose exec db psql -U postgres -c "\l"
```

## ⚙️ 环境配置

### 环境变量模板

```bash
# 开发环境 (.env.development)
APP_NAME="Template Python"
APP_VERSION="1.0.0"
DEBUG=true
ENVIRONMENT=development
DATABASE_URL=sqlite:///./template.db
LOG_LEVEL=DEBUG
LOG_FORMAT=console
CORS_ORIGINS=["http://localhost:3000"]

# 生产环境 (.env.production)
APP_NAME="Template Python"
APP_VERSION="1.0.0"
DEBUG=false
ENVIRONMENT=production
DATABASE_URL=postgresql://user:password@host:5432/dbname
LOG_LEVEL=INFO
LOG_FORMAT=json
CORS_ORIGINS=["https://yourdomain.com"]
SECRET_KEY=your-very-secure-secret-key
```

### 数据库 URL 格式

```bash
# SQLite
DATABASE_URL=sqlite:///./template.db

# PostgreSQL
DATABASE_URL=postgresql://user:password@host:port/database
DATABASE_URL=postgresql://postgres:password@localhost:5432/template_db

# MySQL
DATABASE_URL=mysql://user:password@host:port/database
DATABASE_URL=mysql://root:password@localhost:3306/template_db
```

### 日志配置

```bash
# 日志级别
LOG_LEVEL=DEBUG    # 开发环境
LOG_LEVEL=INFO     # 生产环境
LOG_LEVEL=WARNING  # 仅警告和错误
LOG_LEVEL=ERROR    # 仅错误

# 日志格式
LOG_FORMAT=console # 控制台格式（开发）
LOG_FORMAT=json    # JSON 格式（生产）
LOG_FORMAT=file    # 文件格式

# 文件日志
LOG_FILE_ENABLED=true
LOG_FILE_PATH=logs/app.log
LOG_FILE_ROTATION="1 day"
LOG_FILE_RETENTION="30 days"
```

## 🔧 常用配置

### Ruff 配置 (ruff.toml)

```toml
[lint]
select = ["E", "F", "W", "I", "N", "UP", "S", "B", "A", "C4", "T20"]
ignore = ["E501", "S101"]

[lint.per-file-ignores]
"tests/*" = ["S101", "S106"]

[format]
quote-style = "double"
indent-style = "space"
skip-string-normalization = false
line-ending = "auto"
```

### Black 配置 (pyproject.black.toml)

```toml
[tool.black]
line-length = 88
target-version = ['py311']
include = '\.pyi?$'
extend-exclude = '''
/(
  migrations
  | .venv
  | build
  | dist
)/
'''
```

### MyPy 配置 (mypy.ini)

```ini
[mypy]
python_version = 3.11
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
disallow_incomplete_defs = True
check_untyped_defs = True
disallow_untyped_decorators = True
no_implicit_optional = True
warn_redundant_casts = True
warn_unused_ignores = True
warn_no_return = True
warn_unreachable = True
strict_equality = True
```

### Pytest 配置 (pytest.ini)

```ini
[tool:pytest]
minversion = 6.0
addopts = -ra -q --strict-markers --strict-config
testpaths = tests
python_files = tests/*.py
python_classes = Test*
python_functions = test_*
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    unit: marks tests as unit tests
```

## 🐛 故障排除

### 常见错误及解决方案

#### 1. 端口占用

```bash
# 查看端口占用
lsof -i :8000
netstat -tulpn | grep :8000

# 杀死进程
kill -9 <PID>

# 使用不同端口
uvicorn src.main:app --port 8001
```

#### 2. 数据库连接失败

```bash
# 检查数据库服务状态
docker-compose ps db

# 查看数据库日志
docker-compose logs db

# 测试连接
telnet localhost 5432
psql -h localhost -p 5432 -U postgres

# 重启数据库服务
docker-compose restart db
```

#### 3. 依赖安装失败

```bash
# 清理缓存
uv cache clean
pip cache purge

# 重新创建虚拟环境
rm -rf .venv
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt

# 使用镜像源
uv pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
```

#### 4. Docker 构建失败

```bash
# 清理 Docker 缓存
docker builder prune
docker system prune -f

# 无缓存构建
docker build --no-cache -f docker/Dockerfile -t template-python .

# 查看构建日志
docker build --progress=plain -f docker/Dockerfile -t template-python .
```

#### 5. 权限问题

```bash
# 修复文件权限
sudo chown -R $USER:$USER .
chmod +x scripts/*.sh

# Docker 权限问题
sudo usermod -aG docker $USER
# 重新登录或运行
newgrp docker
```

### 调试技巧

#### 1. 应用调试

```python
# 添加调试断点
import pdb; pdb.set_trace()
# 或使用 ipdb
import ipdb; ipdb.set_trace()
# 或使用 Python 3.7+ 的 breakpoint()
breakpoint()

# 添加调试日志
from src.utils.logger import get_logger
logger = get_logger(__name__)
logger.debug(f"Debug info: {variable}")
```

#### 2. API 调试

```bash
# 使用 curl 测试 API
curl -X GET "http://localhost:8000/health"
curl -X POST "http://localhost:8000/api/v1/users/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test User", "email": "test@example.com"}'

# 使用 httpie
http GET localhost:8000/health
http POST localhost:8000/api/v1/users/ name="Test User" email="test@example.com"
```

#### 3. 数据库调试

```python
# 启用 SQL 日志
from sqlmodel import create_engine
engine = create_engine(database_url, echo=True)

# 查看生成的 SQL
from sqlmodel import select
from src.models.user import User
statement = select(User).where(User.email == "test@example.com")
print(statement)
```

## 📊 性能监控

### 性能指标

```bash
# 查看应用性能
curl http://localhost:8000/metrics

# 系统资源监控
top
htop
docker stats

# 数据库性能
psql -c "SELECT * FROM pg_stat_activity;"
psql -c "SELECT * FROM pg_stat_database;"
```

### 日志查看

```bash
# 应用日志
tail -f logs/app.log
docker-compose logs -f app

# 数据库日志
docker-compose logs -f db

# 系统日志
journalctl -u docker
journalctl -f
```

## 🔐 安全检查

### 安全检查清单

```bash
# 检查敏感信息
grep -r "password\|secret\|key" . --exclude-dir=.git

# 检查文件权限
find . -type f -perm 777

# 扫描依赖漏洞
safety check
bandit -r src/

# Docker 安全扫描
docker scout cves template-python:latest
```

### 环境变量安全

```bash
# 生成安全密钥
python -c "import secrets; print(secrets.token_urlsafe(32))"
openssl rand -base64 32

# 检查环境变量
env | grep -E "(PASSWORD|SECRET|KEY)"

# 加密敏感文件
gpg --symmetric --cipher-algo AES256 .env.production
```

## 📦 部署检查

### 部署前检查

```bash
# 代码质量检查
make lint
make test

# 构建测试
docker build -f docker/Dockerfile -t template-python:test .

# 安全扫描
safety check
bandit -r src/

# 依赖检查
uv pip check
```

### 部署后验证

```bash
# 健康检查
curl http://localhost:8000/health

# API 测试
curl http://localhost:8000/docs
curl http://localhost:8000/api/v1/

# 服务状态
docker-compose ps
kubectl get pods -n template-python

# 日志检查
docker-compose logs app | grep ERROR
kubectl logs -l app=template-python -n template-python
```

## 🔄 版本管理

### Git 工作流

```bash
# 创建功能分支
git checkout -b feature/new-feature

# 提交代码
git add .
git commit -m "feat: add new feature"

# 推送分支
git push origin feature/new-feature

# 合并主分支
git checkout main
git pull origin main
git merge feature/new-feature
git push origin main

# 删除功能分支
git branch -d feature/new-feature
git push origin --delete feature/new-feature
```

### 版本标签

```bash
# 创建版本标签
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# 查看标签
git tag -l
git show v1.0.0

# 删除标签
git tag -d v1.0.0
git push origin --delete v1.0.0
```

## 📞 获取帮助

### 文档链接

- [项目概览](overview.md) - 项目架构和设计理念
- [开发指南](development.md) - 开发环境和流程
- [API 开发](api-guide.md) - API 开发指南
- [数据库配置](database.md) - 数据库设置
- [部署指南](deployment.md) - 生产环境部署
- [Docker 部署](docker.md) - 容器化部署

### 常用资源

- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [SQLModel 文档](https://sqlmodel.tiangolo.com/)
- [Docker 文档](https://docs.docker.com/)
- [Kubernetes 文档](https://kubernetes.io/docs/)
- [Python 官方文档](https://docs.python.org/3/)

### 社区支持

- [GitHub Issues](https://github.com/your-repo/issues) - 问题反馈
- [GitHub Discussions](https://github.com/your-repo/discussions) - 讨论交流
- [Stack Overflow](https://stackoverflow.com/questions/tagged/fastapi) - 技术问答

---

💡 **提示**: 将此文档加入书签，方便快速查询常用命令和配置！
