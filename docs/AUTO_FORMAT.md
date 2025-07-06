# 自动格式化配置指南

本项目已配置了完整的代码自动格式化功能，支持多种编辑器和开发环境。

## 🛠️ 配置的工具

### 代码格式化工具
- **Black**: Python 代码格式化器
- **Ruff**: 快速的 Python linter 和 formatter
- **MyPy**: 静态类型检查

### 编辑器配置
- **VS Code**: 保存时自动格式化
- **EditorConfig**: 跨编辑器的统一配置
- **Pre-commit**: Git 提交前自动检查

## 📝 VS Code 配置

项目已包含 `.vscode/settings.json` 配置文件，提供以下功能：

- ✅ 保存时自动格式化 (`formatOnSave`)
- ✅ 粘贴时自动格式化 (`formatOnPaste`)
- ✅ 自动导入排序 (`organizeImports`)
- ✅ 自动修复 Ruff 问题 (`fixAll.ruff`)
- ✅ 去除行尾空白字符
- ✅ 文件末尾自动添加换行符

### 推荐的 VS Code 扩展

项目包含 `.vscode/extensions.json`，推荐安装以下扩展：

- `ms-python.python` - Python 支持
- `ms-python.black-formatter` - Black 格式化器
- `charliermarsh.ruff` - Ruff linter
- `ms-python.mypy-type-checker` - MyPy 类型检查
- `tamasfe.even-better-toml` - TOML 文件支持

## 🔧 手动格式化命令

### 使用 Makefile

```bash
# 格式化代码
make format

# 检查格式（不修改文件）
make format-check

# 运行 linter
make lint

# 类型检查
make type-check

# 运行所有检查
make check-all
```

### 直接使用工具

```bash
# Black 格式化
uv run black .

# Ruff 格式化
uv run ruff format .

# Ruff 检查和修复
uv run ruff check --fix .

# MyPy 类型检查
uv run mypy .
```

## 🚀 Pre-commit 钩子

项目配置了 pre-commit 钩子，在每次 Git 提交前自动运行格式化和检查：

```bash
# 安装 pre-commit 钩子
make pre-commit-install

# 手动运行 pre-commit
make pre-commit-run

# 更新 pre-commit 钩子
make pre-commit-update
```

## ⚙️ 配置文件说明

### `.vscode/settings.json`
- VS Code 编辑器配置
- 保存时自动格式化设置
- Python 开发环境配置

### `.editorconfig`
- 跨编辑器的统一配置
- 缩进、换行符、字符编码设置

### `pyproject.toml`
- Black、Ruff、MyPy 的详细配置
- 代码风格和检查规则设置

### `.pre-commit-config.yaml`
- Git 提交前的自动检查配置
- 包含格式化、linting、类型检查

## 🎯 最佳实践

1. **开发时**: 依赖编辑器的保存时自动格式化
2. **提交前**: Pre-commit 钩子自动运行检查
3. **CI/CD**: 使用 `make check-all` 进行完整检查
4. **团队协作**: 确保所有成员安装推荐的编辑器扩展

## 🔍 故障排除

### VS Code 自动格式化不工作

1. 确保安装了推荐的扩展
2. 检查 Python 解释器路径是否正确
3. 重启 VS Code
4. 检查输出面板的错误信息

### Pre-commit 钩子失败

```bash
# 重新安装钩子
uv run pre-commit uninstall
uv run pre-commit install

# 更新钩子版本
uv run pre-commit autoupdate
```

### 格式化冲突

如果 Black 和 Ruff 产生冲突，优先使用 Black 的格式化结果，Ruff 主要用于 linting。

## 📚 相关文档

- [Black 文档](https://black.readthedocs.io/)
- [Ruff 文档](https://docs.astral.sh/ruff/)
- [MyPy 文档](https://mypy.readthedocs.io/)
- [Pre-commit 文档](https://pre-commit.com/)
- [EditorConfig 文档](https://editorconfig.org/)
