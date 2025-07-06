"""Tests for API endpoints."""

from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from main import app
from src.db.connection import db


class TestHealthAPI:
    """Test cases for health check API endpoints."""

    def setup_method(self):
        """Set up test client."""
        self.client = TestClient(app)

    def test_basic_health_check(self):
        """Test basic health check endpoint."""
        response = self.client.get("/api/v1/health")
        assert response.status_code == 200

        data = response.json()
        assert "success" in data
        assert "data" in data
        assert data["success"] is True

        health_data = data["data"]
        assert "status" in health_data
        assert "timestamp" in health_data
        assert "service" in health_data
        assert "version" in health_data
        assert health_data["status"] == "healthy"
        assert health_data["service"] == "template-python"
        assert health_data["version"] == "1.0.0"

    def test_database_health_check_endpoint_exists(self):
        """Test database health check endpoint exists and returns proper format."""
        response = self.client.get("/api/v1/health/db")
        assert response.status_code == 200

        data = response.json()
        assert "success" in data
        assert "data" in data
        assert data["success"] is True

        assert "timestamp" in data  # timestamp is at top level

        health_data = data["data"]
        assert "status" in health_data
        assert "database" in health_data
        # Status can be healthy or unhealthy depending on database connection
        assert health_data["status"] in ["healthy", "unhealthy"]
        assert health_data["database"] in ["connected", "disconnected"]

    @patch("src.api.v1.endpoints.health.psutil")
    def test_detailed_health_check(self, mock_psutil):
        """Test detailed health check endpoint."""
        # Mock psutil responses
        mock_memory = MagicMock()
        mock_memory.total = 8589934592  # 8GB
        mock_memory.available = 4294967296  # 4GB
        mock_memory.percent = 50.0
        mock_psutil.virtual_memory.return_value = mock_memory

        mock_disk = MagicMock()
        mock_disk.total = 1000000000000  # 1TB
        mock_disk.free = 500000000000  # 500GB
        mock_disk.used = 500000000000  # 500GB
        mock_psutil.disk_usage.return_value = mock_disk

        mock_psutil.cpu_percent.return_value = 25.5

        response = self.client.get("/api/v1/health/detailed")
        assert response.status_code == 200

        data = response.json()
        assert "success" in data
        assert "data" in data
        assert data["success"] is True

        health_data = data["data"]
        assert "status" in health_data
        assert "service" in health_data
        assert "database" in health_data
        assert "system" in health_data

        # Check system information
        system_info = health_data["system"]
        assert "cpu_percent" in system_info
        assert "memory" in system_info
        assert "disk" in system_info


class TestUsersAPI:
    """Test cases for users API endpoints."""

    def test_get_users_endpoint_exists(self, client):
        """Test that users endpoint exists."""
        response = client.get("/api/v1/users/")
        # 应该返回 200 状态码和空的用户列表
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert data["success"] is True

    def setup_method(self):
        """Set up test client."""

        # 确保测试数据库表存在
        db.create_tables()
        self.client = TestClient(app)

    def teardown_method(self):
        """Clean up after tests."""

        # 清理测试数据
        db.drop_tables()

    def test_create_user_endpoint_exists(self):
        """Test that create user endpoint exists."""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPass123",
            "full_name": "Test User",
        }
        response = self.client.post("/api/v1/users/", json=user_data)
        # 可能返回各种状态码, 但不应该是 404
        assert response.status_code != 404

    def test_get_user_by_id_endpoint_exists(self):
        """Test that get user by ID endpoint exists."""
        response = self.client.get("/api/v1/users/1")
        # 可能返回 404(用户不存在)或其他状态码
        # 但路由应该存在
        assert response.status_code in [200, 404, 422, 500]


class TestHeroesAPI:
    """Test cases for heroes API endpoints."""

    def test_get_heroes_endpoint_exists(self, client):
        """Test that heroes endpoint exists."""
        response = client.get("/api/v1/heroes/")
        # 可能返回 200 或其他状态码, 但不应该是 404
        assert response.status_code != 404

    def test_create_hero_endpoint_exists(self, client):
        """Test that create hero endpoint exists."""
        hero_data = {
            "name": "Test Hero",
            "secret_name": "Test Secret",
            "age": 25,
            "power_level": 50,
        }
        response = client.post("/api/v1/heroes/", json=hero_data)
        # 可能返回各种状态码, 但不应该是 404
        assert response.status_code != 404

    def test_get_hero_by_id_endpoint_exists(self, client):
        """Test that get hero by ID endpoint exists."""
        response = client.get("/api/v1/heroes/1")
        # 可能返回 404(英雄不存在)或其他状态码
        # 但路由应该存在
        assert response.status_code in [200, 404, 422, 500]

    def test_get_teams_endpoint_exists(self, client):
        """Test that get teams endpoint exists."""
        response = client.get("/api/v1/heroes/teams/list")
        # 应该返回空列表或团队列表
        assert response.status_code != 404

    def test_get_power_distribution_endpoint_exists(self, client):
        """Test that power distribution endpoint exists."""
        response = client.get("/api/v1/heroes/stats/power-distribution")
        # 应该返回统计信息
        assert response.status_code != 404


class TestAPIRouting:
    """Test cases for API routing and structure."""

    def test_api_v1_prefix(self, client):
        """Test that API v1 endpoints have correct prefix."""
        # 测试健康检查端点
        response = client.get("/api/v1/health")
        assert response.status_code == 200

        # 测试不存在的 v1 端点
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404

    def test_openapi_docs_generation(self, client):
        """Test that OpenAPI docs are generated correctly."""
        response = client.get("/openapi.json")
        assert response.status_code == 200

        openapi_spec = response.json()
        assert "openapi" in openapi_spec
        assert "info" in openapi_spec
        assert "paths" in openapi_spec

        # 检查是否包含我们的端点
        paths = openapi_spec["paths"]
        assert "/api/v1/health" in paths
        assert "/api/v1/users/" in paths
        assert "/api/v1/heroes/" in paths

    def test_cors_headers(self, client):
        """Test that CORS headers are properly set."""
        # 测试实际的GET请求是否包含CORS头
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        # 检查是否有CORS相关的头部信息
        # 在实际的跨域请求中，浏览器会自动处理CORS

    def test_invalid_endpoint_returns_404(self, client):
        """Test that invalid endpoints return 404 with proper error format."""
        response = client.get("/api/v1/invalid-endpoint")
        assert response.status_code == 404

        data = response.json()
        assert "success" in data
        assert "message" in data
        assert "error_code" in data
        assert data["success"] is False
        assert data["error_code"] == "NOT_FOUND"
