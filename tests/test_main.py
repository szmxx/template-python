"""Tests for main module."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from main import app, main


class TestMainApp:
    """Test cases for the main FastAPI application."""

    def setup_method(self):
        """Set up test client."""
        self.client = TestClient(app)

    def test_root_endpoint(self):
        """Test root endpoint returns correct response."""
        response = self.client.get("/")
        assert response.status_code == 200

        data = response.json()
        assert "message" in data
        assert "data" in data
        assert "success" in data
        assert data["success"] is True

        response_data = data["data"]
        assert "version" in response_data
        assert "docs" in response_data
        assert "redoc" in response_data
        assert "health" in response_data
        assert response_data["version"] == "1.0.0"

    def test_docs_endpoint_accessible(self):
        """Test that docs endpoint is accessible."""
        response = self.client.get("/docs")
        assert response.status_code == 200

    def test_redoc_endpoint_accessible(self):
        """Test that redoc endpoint is accessible."""
        response = self.client.get("/redoc")
        assert response.status_code == 200

    def test_health_endpoint(self):
        """Test health endpoint returns correct format"""
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

    def test_not_found_endpoint(self):
        """Test 404 error handling."""
        response = self.client.get("/nonexistent")
        assert response.status_code == 404

        data = response.json()
        assert "success" in data
        assert "message" in data
        assert "error_code" in data
        assert data["success"] is False
        assert data["error_code"] == "NOT_FOUND"


class TestMainFunction:
    """Test cases for the main function."""

    def test_main_function_exists(self):
        """Test that main function exists and is callable."""
        assert callable(main)

    @patch("main.uvicorn.run")
    @patch("main.DatabaseConfig")
    @patch("builtins.print")
    def test_main_function_call(self, mock_print, mock_db_config, mock_uvicorn_run):
        """Test that main function can be called without errors."""
        # Mock database config
        mock_config = MagicMock()
        mock_config.database_url = "sqlite:///test.db"
        mock_db_config.return_value = mock_config

        try:
            main()
        except Exception as e:
            pytest.fail(f"main() raised {e} unexpectedly!")

        # Verify that uvicorn.run was called
        mock_uvicorn_run.assert_called_once_with(
            "main:app", host="0.0.0.0", port=8000, reload=True, log_level="info"
        )

        # Verify print statements
        mock_print.assert_any_call("Starting Template Python API...")
        mock_print.assert_any_call(f"Database URL: {mock_config.database_url}")

    @patch("main.uvicorn.run")
    @patch("main.DatabaseConfig")
    def test_main_database_config(self, mock_db_config, _mock_uvicorn_run):
        """Test that main function properly configures database."""
        mock_config = MagicMock()
        mock_config.database_url = "sqlite:///test.db"
        mock_db_config.return_value = mock_config

        with patch("builtins.print"):
            main()

        # Verify DatabaseConfig was instantiated
        mock_db_config.assert_called_once()

    @patch("main.uvicorn.run", side_effect=KeyboardInterrupt)
    @patch("main.DatabaseConfig")
    def test_main_handles_keyboard_interrupt(self, mock_db_config, _mock_uvicorn_run):
        """Test that main function handles KeyboardInterrupt gracefully."""
        mock_config = MagicMock()
        mock_config.database_url = "sqlite:///test.db"
        mock_db_config.return_value = mock_config

        with patch("builtins.print"), pytest.raises(KeyboardInterrupt):
            main()
