2zai# Docker 部署指南

本项目提供了完整的 Docker 部署配置，支持开发和生产环境。

## 📋 前置要求

- Docker Engine 20.10+
- Docker Compose 2.0+

## 🚀 快速开始

### 生产环境部署

```bash
# 1. 构建镜像
make docker-build

# 2. 启动服务
make docker-run

# 3. 查看日志
make docker-logs
```

或者直接使用 docker-compose：

```bash
# 进入 docker 目录
cd docker

# 构建并启动
docker-compose up --build -d

# 查看日志
docker-compose logs -f app
```

### 开发环境部署

```bash
# 启动开发环境（支持热重载）
make docker-dev

# 查看开发环境日志
make docker-logs-dev
```

或者直接使用 docker-compose：

```bash
# 进入 docker 目录
cd docker

# 启动开发环境
docker-compose -f docker-compose.dev.yml up --build -d

# 查看日志
docker-compose -f docker-compose.dev.yml logs -f app
```

## 📁 文件结构

```
├── docker/                    # Docker 配置目录
│   ├── Dockerfile            # 生产环境镜像
│   ├── Dockerfile.dev        # 开发环境镜像
│   ├── docker-compose.yml    # 生产环境编排
│   ├── docker-compose.dev.yml # 开发环境编排
│   ├── .env.docker           # Docker 环境变量
│   └── init.sql              # 数据库初始化脚本
├── .dockerignore             # Docker 忽略文件
└── ...
```

## 🔧 配置说明

### 生产环境 (docker-compose.yml)

- **应用服务**: FastAPI 应用，端口 8000
- **数据库服务**: PostgreSQL 15，端口 5432
- **缓存服务**: Redis 7，端口 6379
- **数据持久化**: 使用 Docker volumes
- **健康检查**: 自动检测服务状态

### 开发环境 (docker-compose.dev.yml)

- **应用服务**: 支持热重载的 FastAPI 应用
- **数据库**: 使用 SQLite（文件映射）
- **代码同步**: 实时同步本地代码变更

## 🌐 服务访问

| 服务 | 地址 | 说明 |
|------|------|------|
| API 文档 | http://localhost:8000/docs | Swagger UI |
| ReDoc | http://localhost:8000/redoc | ReDoc 文档 |
| 健康检查 | http://localhost:8000/api/v1/health | 服务状态 |
| PostgreSQL | localhost:5432 | 数据库连接 |
| Redis | localhost:6379 | 缓存连接 |

## 📊 数据管理

### 数据库初始化

数据库会在首次启动时自动初始化：

1. 创建数据库表结构
2. 执行 `init.sql` 中的初始化脚本
3. 设置必要的扩展和配置

### 数据备份

```bash
# 备份 PostgreSQL 数据
docker-compose exec db pg_dump -U postgres template_db > backup.sql

# 恢复数据
docker-compose exec -T db psql -U postgres template_db < backup.sql
```

### 数据卷管理

```bash
# 查看数据卷
docker volume ls

# 清理未使用的数据卷
docker volume prune
```

## 🔍 日志管理

### 查看日志

```bash
# 查看所有服务日志
docker-compose logs

# 查看特定服务日志
docker-compose logs app
docker-compose logs db
docker-compose logs redis

# 实时跟踪日志
make docker-logs
```

### 日志配置

应用日志配置在 `.env.docker` 中：

- `LOG_LEVEL`: 日志级别
- `LOG_TO_CONSOLE`: 控制台输出
- `LOG_TO_FILE`: 文件输出
- `LOG_MAX_SIZE`: 日志文件大小限制

## 🛠️ 开发调试

### 进入容器

```bash
# 进入应用容器
docker-compose exec app bash

# 进入数据库容器
docker-compose exec db psql -U postgres template_db
```

### 重建服务

```bash
# 重建并启动
docker-compose up --build -d

# 重建特定服务
docker-compose build app
```

## 🔒 安全配置

### 生产环境安全检查清单

- [ ] 更改默认密码（PostgreSQL、Redis）
- [ ] 设置强密码策略
- [ ] 配置防火墙规则
- [ ] 启用 HTTPS
- [ ] 设置环境变量加密
- [ ] 定期更新镜像

### 环境变量安全

```bash
# 使用 Docker secrets（生产环境推荐）
echo "your-secret-password" | docker secret create db_password -
```

## 🚨 故障排除

### 常见问题

1. **端口冲突**
   ```bash
   # 检查端口占用
   lsof -i :8000

   # 修改 docker-compose.yml 中的端口映射
   ports:
     - "8001:8000"  # 使用其他端口
   ```

2. **数据库连接失败**
   ```bash
   # 检查数据库服务状态
   docker-compose ps

   # 查看数据库日志
   docker-compose logs db
   ```

3. **权限问题**
   ```bash
   # 修复文件权限
   sudo chown -R $USER:$USER logs/ uploads/
   ```

### 性能优化

1. **资源限制**
   ```yaml
   # 在 docker-compose.yml 中添加
   deploy:
     resources:
       limits:
         cpus: '0.5'
         memory: 512M
   ```

2. **镜像优化**
   - 使用多阶段构建
   - 减少镜像层数
   - 清理缓存文件

## 📚 相关命令

```bash
# 构建镜像
make docker-build

# 启动生产环境
make docker-run

# 启动开发环境
make docker-dev

# 停止服务
make docker-stop

# 清理资源
make docker-clean

# 查看日志
make docker-logs
make docker-logs-dev
```

## 🔄 CI/CD 集成

项目已准备好与 CI/CD 流水线集成：

- 自动化测试
- 镜像构建
- 安全扫描
- 自动部署

详细的 CI/CD 配置请参考项目的 `.github/workflows` 目录。
