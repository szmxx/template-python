# 配置文件说明

本项目将代码质量工具的配置分离到独立的配置文件中，以提高可维护性和灵活性。

## 配置文件结构

### 1. Ruff 配置 (`ruff.toml`)

Ruff 是一个快速的 Python 代码检查和格式化工具，配置文件位于项目根目录的 `ruff.toml`。

**使用方法：**
```bash
# 检查代码
ruff check .

# 自动修复问题
ruff check --fix .

# 格式化代码
ruff format .
```

### 2. Black 配置 (`pyproject.black.toml`)

Black 是 Python 代码格式化工具，配置文件位于 `pyproject.black.toml`。

**使用方法：**
```bash
# 使用指定配置文件格式化代码
black --config pyproject.black.toml .

# 检查格式但不修改
black --config pyproject.black.toml --check .
```

### 3. MyPy 配置 (`mypy.ini`)

MyPy 是 Python 静态类型检查工具，配置文件位于 `mypy.ini`。

**使用方法：**
```bash
# 类型检查
mypy .

# 指定配置文件（如果不在默认位置）
mypy --config-file mypy.ini .
```

## 配置文件优先级

各工具会按照以下优先级查找配置文件：

### Ruff
1. `ruff.toml`
2. `pyproject.toml` 中的 `[tool.ruff]` 部分
3. `.ruff.toml`

### Black
1. `pyproject.toml` 中的 `[tool.black]` 部分
2. 命令行指定的配置文件（如 `--config pyproject.black.toml`）

### MyPy
1. `mypy.ini`
2. `.mypy.ini`
3. `pyproject.toml` 中的 `[tool.mypy]` 部分
4. `setup.cfg` 中的 `[mypy]` 部分

## 集成到 CI/CD

在 GitHub Actions 或其他 CI/CD 系统中使用这些配置：

```yaml
# .github/workflows/quality.yml 示例
name: Code Quality

on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install ruff black mypy
          pip install -e .

      - name: Run Ruff
        run: ruff check .

      - name: Run Black
        run: black --config pyproject.black.toml --check .

      - name: Run MyPy
        run: mypy .
```

## 编辑器集成

### VS Code

在 `.vscode/settings.json` 中配置：

```json
{
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.formatting.provider": "black",
  "python.formatting.blackArgs": ["--config", "pyproject.black.toml"],
  "python.linting.mypyEnabled": true,
  "python.linting.mypyArgs": ["--config-file", "mypy.ini"]
}
```

### PyCharm

1. **Ruff**: File → Settings → Tools → External Tools 添加 Ruff
2. **Black**: File → Settings → Tools → Black，指定配置文件路径
3. **MyPy**: File → Settings → Tools → External Tools 添加 MyPy

## 迁移说明

如果需要将配置重新合并到 `pyproject.toml`：

1. 将各配置文件的内容复制到 `pyproject.toml` 对应的 `[tool.*]` 部分
2. 删除独立的配置文件
3. 更新 CI/CD 脚本中的命令行参数

## 优势

- **模块化**: 每个工具的配置独立，便于管理
- **复用性**: 配置文件可以在不同项目间共享
- **清晰性**: `pyproject.toml` 更加简洁，专注于项目元数据
- **灵活性**: 可以为不同环境使用不同的配置文件
