# 部署指南

本文档详细说明了项目在不同环境下的部署方案和配置。

## 🎯 部署概览

### 支持的部署方式

| 部署方式 | 适用场景 | 复杂度 | 推荐度 |
|----------|----------|--------|--------|
| **Docker Compose** | 单机部署、开发测试 | 低 | ⭐⭐⭐⭐⭐ |
| **Docker Swarm** | 小规模集群 | 中 | ⭐⭐⭐⭐ |
| **Kubernetes** | 大规模生产环境 | 高 | ⭐⭐⭐⭐⭐ |
| **云平台部署** | 托管服务 | 中 | ⭐⭐⭐⭐ |
| **传统部署** | 物理服务器 | 中 | ⭐⭐⭐ |

### 环境分类

- **开发环境** (Development): 本地开发，快速迭代
- **测试环境** (Testing): CI/CD 测试，功能验证
- **预发布环境** (Staging): 生产环境镜像，最终测试
- **生产环境** (Production): 正式服务，高可用性

## 🐳 Docker 部署

### Docker Compose 部署 (推荐)

#### 生产环境部署

```bash
# 1. 克隆项目
git clone <repository-url>
cd template-python

# 2. 配置环境变量
cp docker/.env.docker .env
vim .env  # 修改生产环境配置

# 3. 启动服务
docker-compose -f docker/docker-compose.yml up -d

# 4. 查看服务状态
docker-compose -f docker/docker-compose.yml ps

# 5. 查看日志
docker-compose -f docker/docker-compose.yml logs -f app
```

#### 环境变量配置

```bash
# .env 生产环境配置

# 应用配置
APP_NAME="Template Python"
APP_VERSION="1.0.0"
DEBUG=false
ENVIRONMENT=production

# 数据库配置
DATABASE_URL=postgresql://postgres:your_secure_password@db:5432/template_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=template_db

# Redis 配置
REDIS_URL=redis://redis:6379/0
REDIS_PASSWORD=your_redis_password

# 日志配置
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE_ENABLED=true
LOG_FILE_PATH=/app/logs/app.log

# 安全配置
SECRET_KEY=your-very-secure-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API 配置
CORS_ORIGINS=["https://yourdomain.com"]
```

#### 服务访问

部署完成后，可以通过以下地址访问服务：

- **API 文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health
- **API 根路径**: http://localhost:8000/api/v1/
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

#### 数据持久化

```bash
# 查看数据卷
docker volume ls

# 备份数据库
docker-compose -f docker/docker-compose.yml exec db pg_dump -U postgres template_db > backup.sql

# 恢复数据库
docker-compose -f docker/docker-compose.yml exec -T db psql -U postgres template_db < backup.sql
```

### 自定义 Docker 镜像

#### 多阶段构建 Dockerfile

```dockerfile
# docker/Dockerfile.prod
FROM python:3.11-slim as builder

# 安装构建依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 安装 uv
RUN pip install uv

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 创建虚拟环境并安装依赖
RUN uv venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN uv pip install -r requirements.txt

# 生产阶段
FROM python:3.11-slim as production

# 安装运行时依赖
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# 创建非 root 用户
RUN groupadd -r appuser && useradd -r -g appuser appuser

# 设置工作目录
WORKDIR /app

# 从构建阶段复制虚拟环境
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 复制应用代码
COPY src/ ./src/
COPY pyproject.toml .

# 创建日志目录
RUN mkdir -p /app/logs && chown -R appuser:appuser /app

# 切换到非 root 用户
USER appuser

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 构建和推送镜像

```bash
# 构建镜像
docker build -f docker/Dockerfile.prod -t template-python:latest .

# 标记版本
docker tag template-python:latest template-python:1.0.0

# 推送到镜像仓库
docker push template-python:latest
docker push template-python:1.0.0
```

## ☸️ Kubernetes 部署

### 基础 Kubernetes 配置

#### Namespace

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: template-python
  labels:
    name: template-python
```

#### ConfigMap

```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: template-python
data:
  APP_NAME: "Template Python"
  APP_VERSION: "1.0.0"
  DEBUG: "false"
  ENVIRONMENT: "production"
  LOG_LEVEL: "INFO"
  LOG_FORMAT: "json"
  API_V1_PREFIX: "/api/v1"
```

#### Secret

```yaml
# k8s/secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
  namespace: template-python
type: Opaque
data:
  DATABASE_URL: cG9zdGdyZXNxbDovL3Bvc3RncmVzOnBhc3N3b3JkQGRiOjU0MzIvdGVtcGxhdGVfZGI=
  SECRET_KEY: eW91ci12ZXJ5LXNlY3VyZS1zZWNyZXQta2V5LWhlcmU=
  REDIS_URL: cmVkaXM6Ly9yZWRpczozNjM3OS8w
```

#### Deployment

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: template-python-app
  namespace: template-python
  labels:
    app: template-python
spec:
  replicas: 3
  selector:
    matchLabels:
      app: template-python
  template:
    metadata:
      labels:
        app: template-python
    spec:
      containers:
      - name: app
        image: template-python:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: app-config
        - secretRef:
            name: app-secrets
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        volumeMounts:
        - name: logs
          mountPath: /app/logs
      volumes:
      - name: logs
        emptyDir: {}
```

#### Service

```yaml
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: template-python-service
  namespace: template-python
spec:
  selector:
    app: template-python
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: ClusterIP
```

#### Ingress

```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: template-python-ingress
  namespace: template-python
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/rate-limit: "100"
spec:
  tls:
  - hosts:
    - api.yourdomain.com
    secretName: template-python-tls
  rules:
  - host: api.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: template-python-service
            port:
              number: 80
```

#### 部署到 Kubernetes

```bash
# 创建命名空间
kubectl apply -f k8s/namespace.yaml

# 应用配置
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml

# 部署应用
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml

# 查看部署状态
kubectl get pods -n template-python
kubectl get services -n template-python
kubectl get ingress -n template-python

# 查看日志
kubectl logs -f deployment/template-python-app -n template-python
```

### Helm 部署

#### Helm Chart 结构

```
helm/
├── Chart.yaml
├── values.yaml
├── values-prod.yaml
├── values-staging.yaml
└── templates/
    ├── deployment.yaml
    ├── service.yaml
    ├── ingress.yaml
    ├── configmap.yaml
    ├── secret.yaml
    └── hpa.yaml
```

#### Chart.yaml

```yaml
# helm/Chart.yaml
apiVersion: v2
name: template-python
description: A modern Python web application template
type: application
version: 1.0.0
appVersion: "1.0.0"
keywords:
  - fastapi
  - python
  - web
  - api
maintainers:
  - name: Your Name
    email: your.email@example.com
```

#### values.yaml

```yaml
# helm/values.yaml
replicaCount: 3

image:
  repository: template-python
  tag: latest
  pullPolicy: IfNotPresent

service:
  type: ClusterIP
  port: 80
  targetPort: 8000

ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
  hosts:
    - host: api.yourdomain.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: template-python-tls
      hosts:
        - api.yourdomain.com

resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "512Mi"
    cpu: "500m"

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
  targetMemoryUtilizationPercentage: 80

config:
  APP_NAME: "Template Python"
  APP_VERSION: "1.0.0"
  DEBUG: false
  ENVIRONMENT: production
  LOG_LEVEL: INFO
  LOG_FORMAT: json

secrets:
  DATABASE_URL: ""
  SECRET_KEY: ""
  REDIS_URL: ""
```

#### 使用 Helm 部署

```bash
# 安装 Helm Chart
helm install template-python ./helm \
  --namespace template-python \
  --create-namespace \
  --values helm/values-prod.yaml

# 升级部署
helm upgrade template-python ./helm \
  --namespace template-python \
  --values helm/values-prod.yaml

# 查看状态
helm status template-python -n template-python

# 回滚
helm rollback template-python 1 -n template-python

# 卸载
helm uninstall template-python -n template-python
```

## ☁️ 云平台部署

### AWS 部署

#### ECS Fargate 部署

```json
// aws/task-definition.json
{
  "family": "template-python",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::account:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "template-python",
      "image": "your-account.dkr.ecr.region.amazonaws.com/template-python:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "ENVIRONMENT",
          "value": "production"
        }
      ],
      "secrets": [
        {
          "name": "DATABASE_URL",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:template-python/database-url"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/template-python",
          "awslogs-region": "us-west-2",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3
      }
    }
  ]
}
```

#### 部署脚本

```bash
#!/bin/bash
# aws/deploy.sh

set -e

# 配置
REGION="us-west-2"
ACCOUNT_ID="your-account-id"
REPO_NAME="template-python"
CLUSTER_NAME="template-python-cluster"
SERVICE_NAME="template-python-service"

# 构建和推送镜像
echo "Building Docker image..."
docker build -f docker/Dockerfile.prod -t $REPO_NAME:latest .

# 登录 ECR
echo "Logging in to ECR..."
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com

# 标记和推送镜像
echo "Pushing image to ECR..."
docker tag $REPO_NAME:latest $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPO_NAME:latest
docker push $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPO_NAME:latest

# 更新任务定义
echo "Updating task definition..."
aws ecs register-task-definition --cli-input-json file://aws/task-definition.json

# 更新服务
echo "Updating service..."
aws ecs update-service --cluster $CLUSTER_NAME --service $SERVICE_NAME --force-new-deployment

echo "Deployment completed!"
```

### Google Cloud Platform 部署

#### Cloud Run 部署

```yaml
# gcp/service.yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: template-python
  annotations:
    run.googleapis.com/ingress: all
    run.googleapis.com/execution-environment: gen2
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/maxScale: "10"
        autoscaling.knative.dev/minScale: "1"
        run.googleapis.com/cpu-throttling: "false"
        run.googleapis.com/memory: "512Mi"
        run.googleapis.com/cpu: "1000m"
    spec:
      containerConcurrency: 100
      timeoutSeconds: 300
      containers:
      - image: gcr.io/your-project/template-python:latest
        ports:
        - containerPort: 8000
        env:
        - name: ENVIRONMENT
          value: production
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: database-url
              key: url
        resources:
          limits:
            memory: "512Mi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
```

#### 部署脚本

```bash
#!/bin/bash
# gcp/deploy.sh

set -e

# 配置
PROJECT_ID="your-project-id"
REGION="us-central1"
SERVICE_NAME="template-python"

# 构建和推送镜像
echo "Building and pushing image..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME:latest .

# 部署到 Cloud Run
echo "Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME:latest \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --max-instances 10 \
  --min-instances 1

echo "Deployment completed!"
```

## 🔧 配置管理

### 环境配置策略

#### 配置层次结构

```
1. 默认配置 (代码中)
2. 环境配置文件 (.env.example)
3. 环境变量 (运行时)
4. 配置管理服务 (Consul, etcd)
5. 密钥管理服务 (Vault, AWS Secrets Manager)
```

#### 配置模板

```bash
# config/production.env
# 生产环境配置模板

# 应用配置
APP_NAME="Template Python"
APP_VERSION="1.0.0"
DEBUG=false
ENVIRONMENT=production

# 数据库配置
DATABASE_URL=postgresql://user:password@host:5432/dbname
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30
DATABASE_POOL_TIMEOUT=30

# Redis 配置
REDIS_URL=redis://host:6379/0
REDIS_PASSWORD=password
REDIS_MAX_CONNECTIONS=20

# 日志配置
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE_ENABLED=true
LOG_FILE_PATH=/app/logs/app.log
LOG_FILE_ROTATION="1 day"
LOG_FILE_RETENTION="30 days"

# 安全配置
SECRET_KEY=your-very-secure-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30
PASSWORD_MIN_LENGTH=8

# API 配置
API_V1_PREFIX=/api/v1
CORS_ORIGINS=["https://yourdomain.com"]
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# 监控配置
METRICS_ENABLED=true
METRICS_PORT=9090
HEALTH_CHECK_INTERVAL=30

# 文件上传配置
UPLOAD_MAX_SIZE=10485760  # 10MB
UPLOAD_ALLOWED_TYPES=["image/jpeg", "image/png", "application/pdf"]
UPLOAD_STORAGE_PATH=/app/uploads
```

### 密钥管理

#### 使用 Docker Secrets

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  app:
    image: template-python:latest
    secrets:
      - database_url
      - secret_key
      - redis_password
    environment:
      - DATABASE_URL_FILE=/run/secrets/database_url
      - SECRET_KEY_FILE=/run/secrets/secret_key
      - REDIS_PASSWORD_FILE=/run/secrets/redis_password

secrets:
  database_url:
    file: ./secrets/database_url.txt
  secret_key:
    file: ./secrets/secret_key.txt
  redis_password:
    file: ./secrets/redis_password.txt
```

#### 使用 Kubernetes Secrets

```bash
# 创建密钥
kubectl create secret generic app-secrets \
  --from-literal=database-url="postgresql://..." \
  --from-literal=secret-key="your-secret-key" \
  --from-literal=redis-password="redis-password" \
  -n template-python

# 或从文件创建
kubectl create secret generic app-secrets \
  --from-file=database-url=./secrets/database_url.txt \
  --from-file=secret-key=./secrets/secret_key.txt \
  -n template-python
```

## 📊 监控和日志

### 应用监控

#### Prometheus 监控

```python
# src/utils/metrics.py
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi import Response
import time

# 定义指标
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

ACTIVE_CONNECTIONS = Gauge(
    'active_connections',
    'Number of active connections'
)

# 中间件
class MetricsMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start_time = time.time()

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                status_code = message["status"]
                method = scope["method"]
                path = scope["path"]

                # 记录指标
                REQUEST_COUNT.labels(
                    method=method,
                    endpoint=path,
                    status_code=status_code
                ).inc()

                REQUEST_DURATION.labels(
                    method=method,
                    endpoint=path
                ).observe(time.time() - start_time)

            await send(message)

        await self.app(scope, receive, send_wrapper)

# 指标端点
@app.get("/metrics")
def metrics():
    return Response(
        generate_latest(),
        media_type="text/plain"
    )
```

#### 健康检查

```python
# src/api/v1/endpoints/health.py
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, text
from src.db.connection import get_session
import redis
import os

router = APIRouter()

@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": os.getenv("APP_VERSION", "unknown")
    }

@router.get("/health/detailed")
def detailed_health_check(session: Session = Depends(get_session)):
    checks = {
        "database": check_database(session),
        "redis": check_redis(),
        "disk_space": check_disk_space(),
        "memory": check_memory()
    }

    overall_status = "healthy" if all(
        check["status"] == "healthy" for check in checks.values()
    ) else "unhealthy"

    return {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat(),
        "checks": checks
    }

def check_database(session: Session):
    try:
        session.exec(text("SELECT 1"))
        return {"status": "healthy", "message": "Database connection OK"}
    except Exception as e:
        return {"status": "unhealthy", "message": f"Database error: {str(e)}"}

def check_redis():
    try:
        r = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))
        r.ping()
        return {"status": "healthy", "message": "Redis connection OK"}
    except Exception as e:
        return {"status": "unhealthy", "message": f"Redis error: {str(e)}"}
```

### 日志聚合

#### ELK Stack 配置

```yaml
# monitoring/docker-compose.yml
version: '3.8'

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.8.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
    ports:
      - "9200:9200"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data

  logstash:
    image: docker.elastic.co/logstash/logstash:8.8.0
    ports:
      - "5044:5044"
    volumes:
      - ./logstash/pipeline:/usr/share/logstash/pipeline
      - ./logstash/config:/usr/share/logstash/config
    depends_on:
      - elasticsearch

  kibana:
    image: docker.elastic.co/kibana/kibana:8.8.0
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    depends_on:
      - elasticsearch

  filebeat:
    image: docker.elastic.co/beats/filebeat:8.8.0
    user: root
    volumes:
      - ./filebeat/filebeat.yml:/usr/share/filebeat/filebeat.yml:ro
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
      - /var/run/docker.sock:/var/run/docker.sock:ro
    depends_on:
      - logstash

volumes:
  elasticsearch_data:
```

## 🚀 CI/CD 流水线

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]
  release:
    types: [published]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install uv
      run: pip install uv

    - name: Install dependencies
      run: |
        uv venv
        source .venv/bin/activate
        uv pip install -r requirements.txt
        uv pip install -r requirements-dev.txt

    - name: Run tests
      run: |
        source .venv/bin/activate
        pytest --cov=src --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml

  build-and-push:
    needs: test
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
    - uses: actions/checkout@v4

    - name: Log in to Container Registry
      uses: docker/login-action@v2
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}

    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v4
      with:
        images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
        tags: |
          type=ref,event=branch
          type=ref,event=pr
          type=semver,pattern={{version}}
          type=semver,pattern={{major}}.{{minor}}

    - name: Build and push Docker image
      uses: docker/build-push-action@v4
      with:
        context: .
        file: ./docker/Dockerfile.prod
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}

  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
    - uses: actions/checkout@v4

    - name: Deploy to production
      run: |
        # 这里添加你的部署脚本
        echo "Deploying to production..."
        # 例如：kubectl apply -f k8s/
        # 或者：helm upgrade template-python ./helm
```

### GitLab CI/CD

```yaml
# .gitlab-ci.yml
stages:
  - test
  - build
  - deploy

variables:
  DOCKER_DRIVER: overlay2
  DOCKER_TLS_CERTDIR: "/certs"

test:
  stage: test
  image: python:3.11
  before_script:
    - pip install uv
    - uv venv
    - source .venv/bin/activate
    - uv pip install -r requirements.txt
    - uv pip install -r requirements-dev.txt
  script:
    - source .venv/bin/activate
    - ruff check .
    - black . --check
    - mypy .
    - pytest --cov=src --cov-report=xml
  coverage: '/TOTAL.+ ([0-9]{1,3}%)$/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml

build:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  before_script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
  script:
    - docker build -f docker/Dockerfile.prod -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
    - docker tag $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA $CI_REGISTRY_IMAGE:latest
    - docker push $CI_REGISTRY_IMAGE:latest
  only:
    - main

deploy_staging:
  stage: deploy
  image: alpine/helm:latest
  before_script:
    - apk add --no-cache curl
    - curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
    - chmod +x kubectl
    - mv kubectl /usr/local/bin/
  script:
    - helm upgrade --install template-python-staging ./helm \
        --namespace template-python-staging \
        --create-namespace \
        --values helm/values-staging.yaml \
        --set image.tag=$CI_COMMIT_SHA
  environment:
    name: staging
    url: https://staging-api.yourdomain.com
  only:
    - main

deploy_production:
  stage: deploy
  image: alpine/helm:latest
  before_script:
    - apk add --no-cache curl
    - curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
    - chmod +x kubectl
    - mv kubectl /usr/local/bin/
  script:
    - helm upgrade --install template-python ./helm \
        --namespace template-python \
        --create-namespace \
        --values helm/values-prod.yaml \
        --set image.tag=$CI_COMMIT_SHA
  environment:
    name: production
    url: https://api.yourdomain.com
  when: manual
  only:
    - main
```

## 🔒 安全最佳实践

### 容器安全

```dockerfile
# 安全的 Dockerfile 示例
FROM python:3.11-slim as base

# 创建非 root 用户
RUN groupadd -r appuser && useradd -r -g appuser appuser

# 更新系统包
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY src/ ./src/

# 设置正确的权限
RUN chown -R appuser:appuser /app

# 切换到非 root 用户
USER appuser

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 网络安全

```yaml
# k8s/network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: template-python-netpol
  namespace: template-python
spec:
  podSelector:
    matchLabels:
      app: template-python
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: database
    ports:
    - protocol: TCP
      port: 5432
  - to: []
    ports:
    - protocol: TCP
      port: 53
    - protocol: UDP
      port: 53
```

## 📈 性能优化

### 应用性能优化

```python
# src/utils/cache.py
import redis
import json
from functools import wraps
from typing import Any, Optional

redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))

def cache(expire: int = 300, key_prefix: str = ""):
    """缓存装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(kwargs))}"

            # 尝试从缓存获取
            cached_result = redis_client.get(cache_key)
            if cached_result:
                return json.loads(cached_result)

            # 执行函数并缓存结果
            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, expire, json.dumps(result, default=str))

            return result
        return wrapper
    return decorator

# 使用示例
@cache(expire=600, key_prefix="user")
async def get_user_profile(user_id: int):
    # 数据库查询逻辑
    pass
```

### 数据库性能优化

```python
# src/db/config.py
from sqlmodel import create_engine
from sqlalchemy.pool import QueuePool

def get_engine(database_url: str):
    return create_engine(
        database_url,
        poolclass=QueuePool,
        pool_size=20,              # 连接池大小
        max_overflow=30,           # 最大溢出连接
        pool_timeout=30,           # 获取连接超时
        pool_recycle=3600,         # 连接回收时间
        pool_pre_ping=True,        # 连接前检查
        echo=False,                # 生产环境关闭 SQL 日志
        connect_args={
            "connect_timeout": 10,
            "application_name": "template-python"
        }
    )
```

## 🔧 故障排除

### 常见问题

#### 1. 容器启动失败

```bash
# 查看容器日志
docker logs container_name

# 进入容器调试
docker exec -it container_name /bin/bash

# 检查容器资源使用
docker stats container_name
```

#### 2. 数据库连接问题

```bash
# 测试数据库连接
psql -h localhost -p 5432 -U postgres -d template_db

# 检查数据库日志
docker logs postgres_container

# 验证网络连通性
telnet db_host 5432
```

#### 3. Kubernetes 部署问题

```bash
# 查看 Pod 状态
kubectl get pods -n template-python

# 查看 Pod 日志
kubectl logs -f pod_name -n template-python

# 查看 Pod 事件
kubectl describe pod pod_name -n template-python

# 查看服务状态
kubectl get svc -n template-python

# 测试服务连通性
kubectl port-forward svc/template-python-service 8080:80 -n template-python
```

### 监控和告警

```yaml
# monitoring/alerts.yml
groups:
- name: template-python
  rules:
  - alert: HighErrorRate
    expr: rate(http_requests_total{status_code=~"5.."}[5m]) > 0.1
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "High error rate detected"
      description: "Error rate is {{ $value }} errors per second"

  - alert: HighResponseTime
    expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High response time detected"
      description: "95th percentile response time is {{ $value }} seconds"

  - alert: DatabaseConnectionFailed
    expr: up{job="template-python"} == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "Application is down"
      description: "Template Python application has been down for more than 1 minute"
```

## 📚 参考资源

### 部署相关

- [Docker 最佳实践](https://docs.docker.com/develop/dev-best-practices/)
- [Kubernetes 部署指南](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- [Helm Chart 开发](https://helm.sh/docs/chart_best_practices/)
- [AWS ECS 部署](https://docs.aws.amazon.com/ecs/)
- [Google Cloud Run](https://cloud.google.com/run/docs)

### 监控和日志

- [Prometheus 监控](https://prometheus.io/docs/)
- [Grafana 可视化](https://grafana.com/docs/)
- [ELK Stack](https://www.elastic.co/elastic-stack/)
- [Jaeger 分布式追踪](https://www.jaegertracing.io/docs/)

### 安全

- [容器安全最佳实践](https://kubernetes.io/docs/concepts/security/)
- [OWASP API 安全](https://owasp.org/www-project-api-security/)
- [密钥管理](https://kubernetes.io/docs/concepts/configuration/secret/)
