# Docker 配置

本目录包含了项目的所有 Docker 相关配置文件。

## 📁 文件说明

- `Dockerfile` - 生产环境镜像配置
- `Dockerfile.dev` - 开发环境镜像配置（支持热重载）
- `docker-compose.yml` - 生产环境服务编排
- `docker-compose.dev.yml` - 开发环境服务编排
- `.env.docker` - Docker 环境变量配置
- `init.sql` - PostgreSQL 数据库初始化脚本

## 🚀 快速开始

### 生产环境

```bash
# 构建并启动所有服务
docker-compose up --build -d

# 查看服务状态
docker-compose ps

# 查看应用日志
docker-compose logs -f app

# 停止服务
docker-compose down
```

### 开发环境

```bash
# 启动开发环境（支持热重载）
docker-compose -f docker-compose.dev.yml up --build -d

# 查看日志
docker-compose -f docker-compose.dev.yml logs -f app

# 停止服务
docker-compose -f docker-compose.dev.yml down
```

## 🔧 服务配置

### 生产环境服务

- **app**: FastAPI 应用 (端口 8000)
- **db**: PostgreSQL 数据库 (端口 5432)
- **redis**: Redis 缓存 (端口 6379)

### 开发环境服务

- **app**: FastAPI 应用，支持热重载 (端口 8000)
- 使用 SQLite 数据库（无需额外服务）

## 📊 数据持久化

生产环境使用 Docker volumes 进行数据持久化：

- `postgres_data`: PostgreSQL 数据
- `redis_data`: Redis 数据
- `../logs`: 应用日志文件
- `../uploads`: 文件上传目录

## 🛠️ 自定义配置

1. **修改环境变量**: 编辑 `.env.docker` 文件
2. **修改端口映射**: 编辑对应的 `docker-compose.yml` 文件
3. **添加新服务**: 在 `docker-compose.yml` 中添加新的服务定义

## 📋 常用命令

```bash
# 重建特定服务
docker-compose build app

# 查看所有服务日志
docker-compose logs

# 进入应用容器
docker-compose exec app bash

# 进入数据库容器
docker-compose exec db psql -U postgres template_db

# 清理所有资源
docker-compose down -v --remove-orphans
```

## 🔍 故障排除

1. **端口冲突**: 修改 `docker-compose.yml` 中的端口映射
2. **权限问题**: 确保 `logs/` 和 `uploads/` 目录有正确的权限
3. **数据库连接失败**: 检查 `.env.docker` 中的数据库配置

更多详细信息请参考 [Docker 部署指南](../docs/docker.md)。
