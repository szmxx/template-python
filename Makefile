# Makefile for Python project development

.PHONY: help
help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.PHONY: format
format: ## Format code with black and ruff
	uv run black --config pyproject.black.toml .
	uv run ruff format .
	-uv run ruff check --fix .

.PHONY: format-check
format-check: ## Check code formatting without making changes
	uv run black --config pyproject.black.toml --check .
	uv run ruff format --check .
	uv run ruff check .

# 安装依赖
.PHONY: install dev-install
install: ## Install production dependencies
	uv sync --no-dev

dev-install: ## Install development dependencies
	uv sync

# 代码检查
.PHONY: lint type-check
lint: ## Run ruff linter with auto-fix
	@echo "Running Ruff linter..."
	uv run ruff check . --fix

# 类型检查
type-check: ## Run mypy type checking
	@echo "Running MyPy type checker..."
	uv run mypy .



# 清理缓存文件
.PHONY: clean
clean: ## Clean cache and temporary files
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	rm -rf *.egg-info
	rm -rf dist
	rm -rf build
	rm -rf htmlcov
	rm -rf .coverage
	@echo "🧹 Cleaned up cache files"

# Pre-commit 相关命令
.PHONY: pre-commit-install pre-commit-run pre-commit-update
pre-commit-install: ## Install pre-commit hooks
	@echo "Installing pre-commit hooks..."
	uv run pre-commit install

pre-commit-run: ## Run pre-commit on all files
	@echo "Running pre-commit on all files..."
	uv run pre-commit run --all-files

pre-commit-update: ## Update pre-commit hooks
	@echo "Updating pre-commit hooks..."
	uv run pre-commit autoupdate

# 运行测试
.PHONY: test test-cov check-all
test: ## Run tests
	uv run pytest
	@echo "🧪 Tests completed"

# 运行测试并显示覆盖率
test-cov: ## Run tests with coverage
	uv run pytest --cov=src --cov-report=html --cov-report=term
	@echo "🧪 Tests with coverage completed"

# 运行所有检查
check-all: ## Run all checks (format, lint, type-check, test)
	@echo "🔍 Running all checks..."
	$(MAKE) format-check
	$(MAKE) lint
	$(MAKE) type-check
	$(MAKE) test
	@echo "✅ All checks completed"

# 运行特定测试
.PHONY: test-unit test-integration test-api test-verbose
test-unit: ## Run unit tests only
	uv run pytest -m unit
	@echo "🔬 Unit tests completed"

test-integration: ## Run integration tests only
	uv run pytest -m integration
	@echo "🔗 Integration tests completed"

test-api: ## Run API tests only
	uv run pytest -m api
	@echo "🌐 API tests completed"

# 运行测试（详细输出）
test-verbose: ## Run tests with verbose output
	uv run pytest -v
	@echo "🔍 Verbose tests completed"

# 启动项目
.PHONY: run dev start
run: ## Start the FastAPI application
	@echo "🚀 Starting FastAPI application..."
	uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000

dev: run ## Alias for run (development mode)

start: ## Start the application using main.py
	@echo "🚀 Starting application..."
	uv run python main.py

# Docker 命令
.PHONY: docker-build docker-run docker-dev docker-stop docker-clean docker-logs

docker-build:
	@echo "🐳 构建 Docker 镜像..."
	docker-compose -f docker/docker-compose.yml build

docker-run:
	@echo "🚀 启动生产环境容器..."
	docker-compose -f docker/docker-compose.yml up -d

docker-dev:
	@echo "🛠️ 启动开发环境容器..."
	docker-compose -f docker/docker-compose.dev.yml up -d

docker-stop:
	@echo "🛑 停止所有容器..."
	docker-compose -f docker/docker-compose.yml down
	docker-compose -f docker/docker-compose.dev.yml down

docker-clean:
	@echo "🧹 清理 Docker 资源..."
	docker-compose -f docker/docker-compose.yml down -v --remove-orphans
	docker-compose -f docker/docker-compose.dev.yml down -v --remove-orphans
	docker system prune -f

docker-logs:
	@echo "📋 查看应用日志..."
	docker-compose -f docker/docker-compose.yml logs -f app

docker-logs-dev:
	@echo "📋 查看开发环境日志..."
	docker-compose -f docker/docker-compose.dev.yml logs -f app
