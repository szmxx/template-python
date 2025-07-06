# 更新日志

本文档记录了项目的所有重要变更和版本更新。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
并且本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [未发布]

### 新增
- 完整的项目文档体系
- 项目概览和架构设计文档
- 详细的开发指南和最佳实践
- 生产环境部署完整方案
- 快速参考文档和常用命令

### 变更
- 重新组织文档结构，提高可读性
- 优化 README.md 内容和导航

## [1.0.0] - 2024-01-01

### 新增
- 基于 FastAPI + SQLModel 的现代 Python Web 应用框架
- 完整的代码质量工具链集成
  - Ruff: 快速代码检查和格式化
  - Black: 代码格式化
  - MyPy: 静态类型检查
  - Pytest: 测试框架
- 多数据库支持 (SQLite, PostgreSQL, MySQL)
- Docker 容器化部署支持
- 结构化日志系统 (Loguru)
- API 自动文档生成
- 健康检查端点
- 用户和英雄管理示例模块
- 文件上传功能
- 完整的测试覆盖
- CI/CD 配置示例
- Pre-commit 钩子配置

### 技术栈
- **核心框架**: FastAPI 0.104+, SQLModel 0.0.14+
- **数据库**: SQLite (默认), PostgreSQL, MySQL
- **开发工具**: uv, Ruff, Black, MyPy, Pytest
- **部署**: Docker, Docker Compose
- **日志**: Loguru
- **文档**: 自动生成的 OpenAPI 文档

### 项目结构
```
src/
├── api/v1/           # API 路由和端点
├── db/               # 数据库配置和连接
├── models/           # 数据模型定义
├── utils/            # 工具函数和辅助模块
└── main.py           # 应用入口点

tests/                # 测试代码
docs/                 # 项目文档
docker/               # Docker 配置文件
```

### API 端点
- `GET /health` - 健康检查
- `GET /docs` - API 文档
- `GET /api/v1/users/` - 用户列表
- `POST /api/v1/users/` - 创建用户
- `GET /api/v1/users/{user_id}` - 获取用户详情
- `PUT /api/v1/users/{user_id}` - 更新用户
- `DELETE /api/v1/users/{user_id}` - 删除用户
- `GET /api/v1/heroes/` - 英雄列表
- `POST /api/v1/heroes/` - 创建英雄
- `GET /api/v1/heroes/{hero_id}` - 获取英雄详情
- `PUT /api/v1/heroes/{hero_id}` - 更新英雄
- `DELETE /api/v1/heroes/{hero_id}` - 删除英雄
- `POST /api/v1/upload/` - 文件上传

### 配置特性
- 环境变量配置管理
- 多环境支持 (开发/测试/生产)
- 数据库连接池配置
- CORS 跨域配置
- 日志级别和格式配置
- 文件上传限制配置

### 开发特性
- 热重载开发服务器
- 自动代码格式化和检查
- 类型安全的数据模型
- 自动 API 文档生成
- 完整的测试套件
- 代码覆盖率报告

### 部署特性
- Docker 多阶段构建
- 生产环境优化配置
- 健康检查和监控
- 数据持久化支持
- 环境变量安全管理

---

## 版本说明

### 版本格式

本项目使用 [语义化版本](https://semver.org/lang/zh-CN/) 格式：`主版本号.次版本号.修订号`

- **主版本号**: 不兼容的 API 修改
- **次版本号**: 向下兼容的功能性新增
- **修订号**: 向下兼容的问题修正

### 变更类型

- **新增** (Added): 新功能
- **变更** (Changed): 对现有功能的变更
- **弃用** (Deprecated): 即将移除的功能
- **移除** (Removed): 已移除的功能
- **修复** (Fixed): 问题修复
- **安全** (Security): 安全相关的修复

### 发布流程

1. **开发阶段**: 在 `[未发布]` 部分记录变更
2. **版本发布**: 创建新版本部分，移动未发布的变更
3. **标签创建**: 创建对应的 Git 标签
4. **文档更新**: 更新相关文档和 README

### 兼容性说明

- **1.x.x**: 稳定版本，向下兼容
- **0.x.x**: 开发版本，可能包含破坏性变更

### 升级指南

#### 从 0.x.x 升级到 1.0.0

1. **环境要求**:
   - Python 3.11+
   - 更新依赖包到最新版本

2. **配置变更**:
   - 检查 `.env` 文件格式
   - 更新数据库连接配置

3. **代码变更**:
   - 更新导入路径
   - 检查 API 端点变更

4. **数据库迁移**:
   ```bash
   # 备份现有数据
   cp template.db template.db.backup

   # 运行应用进行自动迁移
   python -m src.main
   ```

### 已知问题

#### 1.0.0
- 暂无已知问题

### 计划功能

#### 1.1.0 (计划中)
- [ ] 用户认证和授权系统
- [ ] Redis 缓存集成
- [ ] API 限流功能
- [ ] 更多数据库操作示例

#### 1.2.0 (计划中)
- [ ] 消息队列支持
- [ ] 后台任务处理
- [ ] 更完善的监控和指标
- [ ] GraphQL API 支持

#### 2.0.0 (远期计划)
- [ ] 微服务架构支持
- [ ] 分布式追踪
- [ ] 高级安全特性
- [ ] 性能优化

---

## 贡献指南

### 如何贡献变更日志

1. **记录变更**: 在 `[未发布]` 部分添加你的变更
2. **分类变更**: 使用正确的变更类型 (新增/变更/修复等)
3. **描述清晰**: 简洁明了地描述变更内容
4. **影响说明**: 如果是破坏性变更，请详细说明

### 变更描述格式

```markdown
### 新增
- 新功能的简短描述 (#PR编号)
- 另一个新功能 (@贡献者)

### 变更
- 对现有功能的修改说明
- **破坏性变更**: 详细说明不兼容的变更

### 修复
- 修复的问题描述 (修复 #Issue编号)
```

### 发布检查清单

发布新版本前，请确保：

- [ ] 所有测试通过
- [ ] 文档已更新
- [ ] 变更日志已更新
- [ ] 版本号已更新
- [ ] 破坏性变更已在升级指南中说明
- [ ] 新功能有相应的测试覆盖
- [ ] API 文档已更新

---

## 链接

- [项目主页](https://github.com/your-username/template-python)
- [问题反馈](https://github.com/your-username/template-python/issues)
- [功能请求](https://github.com/your-username/template-python/issues/new?template=feature_request.md)
- [安全问题报告](mailto:security@yourdomain.com)

---

**注意**: 此变更日志遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/) 格式。
