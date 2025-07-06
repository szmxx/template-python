"""文件上传API的测试用例。"""

import io
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from main import app


class TestFilesAPI:
    """文件上传API测试类。"""

    def setup_method(self):
        """设置测试环境。"""
        self.client = TestClient(app)
        self.test_upload_dir = Path("test_uploads")
        self.test_upload_dir.mkdir(exist_ok=True)

    def teardown_method(self):
        """清理测试环境。"""
        # 清理测试文件
        if self.test_upload_dir.exists():
            for file in self.test_upload_dir.iterdir():
                if file.is_file():
                    file.unlink()
            self.test_upload_dir.rmdir()

    def test_upload_single_file(self):
        """测试单文件上传。"""
        # 创建测试文件
        test_content = b"This is a test file content"
        test_file = io.BytesIO(test_content)

        with patch("src.api.v1.endpoints.files.UPLOAD_DIR", self.test_upload_dir):
            response = self.client.post(
                "/api/v1/files/upload",
                files={"file": ("test.txt", test_file, "text/plain")},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "文件上传成功"
        assert "file_id" in data["data"]
        assert data["data"]["original_name"] == "test.txt"
        assert data["data"]["file_type"] == "document"
        assert data["data"]["file_size"] == len(test_content)

    def test_upload_multiple_files(self):
        """测试多文件上传。"""
        test_files = [
            ("file1.txt", b"Content 1", "text/plain"),
            ("file2.jpg", b"Content 2", "image/jpeg"),
        ]

        files = [
            ("files", (name, io.BytesIO(content), content_type))
            for name, content, content_type in test_files
        ]

        with patch("src.api.v1.endpoints.files.UPLOAD_DIR", self.test_upload_dir):
            response = self.client.post("/api/v1/files/upload/multiple", files=files)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["total_uploaded"] == 2
        assert data["data"]["total_failed"] == 0
        assert len(data["data"]["uploaded_files"]) == 2

    def test_upload_invalid_file_type(self):
        """测试上传不支持的文件类型。"""
        test_content = b"Invalid file content"
        test_file = io.BytesIO(test_content)

        with patch("src.api.v1.endpoints.files.UPLOAD_DIR", self.test_upload_dir):
            response = self.client.post(
                "/api/v1/files/upload",
                files={"file": ("test.xyz", test_file, "application/octet-stream")},
            )

        assert response.status_code == 400
        assert "不支持的文件类型" in response.json()["message"]

    def test_upload_empty_filename(self):
        """测试上传空文件名。"""
        test_content = b"Test content"
        test_file = io.BytesIO(test_content)

        with patch("src.api.v1.endpoints.files.UPLOAD_DIR", self.test_upload_dir):
            response = self.client.post(
                "/api/v1/files/upload", files={"file": ("", test_file, "text/plain")}
            )

        assert response.status_code == 422
        # FastAPI对空文件名返回422，检查错误信息
        response_data = response.json()
        assert "detail" in response_data

    def test_upload_large_file(self):
        """测试上传超大文件。"""
        # 创建一个超过限制的大文件内容
        large_content = b"x" * (11 * 1024 * 1024)  # 11MB

        with patch("src.api.v1.endpoints.files.UPLOAD_DIR", self.test_upload_dir):
            response = self.client.post(
                "/api/v1/files/upload",
                files={"file": ("large.txt", large_content, "text/plain")},
            )

        assert response.status_code == 413  # 应该返回413错误
        assert "文件大小超过限制" in response.json()["message"]

    def test_list_files(self):
        """测试获取文件列表。"""
        # 先上传一个文件
        test_content = b"Test file for listing"
        test_file = io.BytesIO(test_content)

        with patch("src.api.v1.endpoints.files.UPLOAD_DIR", self.test_upload_dir):
            # 上传文件
            upload_response = self.client.post(
                "/api/v1/files/upload",
                files={"file": ("test.txt", test_file, "text/plain")},
            )
            assert upload_response.status_code == 200

            # 获取文件列表
            list_response = self.client.get("/api/v1/files/list")

        assert list_response.status_code == 200
        data = list_response.json()
        assert data["success"] is True
        assert data["data"]["total_count"] >= 1
        assert len(data["data"]["files"]) >= 1

    def test_get_file_info(self):
        """测试获取文件信息。"""
        # 先上传一个文件
        test_content = b"info_test"

        with patch("src.api.v1.endpoints.files.UPLOAD_DIR", self.test_upload_dir):
            upload_response = self.client.post(
                "/api/v1/files/upload",
                files={"file": ("info_test.txt", test_content, "text/plain")},
            )

            file_id = upload_response.json()["data"]["file_id"]

            # 获取文件信息
            info_response = self.client.get(f"/api/v1/files/info/{file_id}")

        assert info_response.status_code == 200
        file_info = info_response.json()["data"]
        assert "uploaded_file" in file_info["original_name"]
        assert file_info["file_size"] == len(test_content)
        assert file_info["content_type"] == "application/octet-stream"

    def test_get_file_info_not_found(self):
        """测试获取不存在文件的信息。"""
        with patch("src.api.v1.endpoints.files.UPLOAD_DIR", self.test_upload_dir):
            response = self.client.get("/api/v1/files/info/nonexistent-id")

        assert response.status_code == 200
        data = response.json()
        assert "文件不存在" in data["message"]

    def test_delete_file(self):
        """测试删除文件。"""
        test_content = b"File to be deleted"
        test_file = io.BytesIO(test_content)

        with patch("src.api.v1.endpoints.files.UPLOAD_DIR", self.test_upload_dir):
            # 上传文件
            upload_response = self.client.post(
                "/api/v1/files/upload",
                files={"file": ("delete_test.txt", test_file, "text/plain")},
            )
            assert upload_response.status_code == 200
            file_id = upload_response.json()["data"]["file_id"]

            # 删除文件
            delete_response = self.client.delete(f"/api/v1/files/delete/{file_id}")

        assert delete_response.status_code == 200
        data = delete_response.json()
        assert data["success"] is True
        assert data["data"]["deleted"] is True

    def test_delete_file_not_found(self):
        """测试删除不存在的文件。"""
        with patch("src.api.v1.endpoints.files.UPLOAD_DIR", self.test_upload_dir):
            response = self.client.delete("/api/v1/files/delete/nonexistent-id")

        assert response.status_code == 200
        data = response.json()
        assert "文件不存在" in data["message"]

    def test_download_file(self):
        """测试文件下载。"""
        test_content = b"Download test content"
        test_file = io.BytesIO(test_content)

        with patch("src.api.v1.endpoints.files.UPLOAD_DIR", self.test_upload_dir):
            # 上传文件
            upload_response = self.client.post(
                "/api/v1/files/upload",
                files={"file": ("download_test.txt", test_file, "text/plain")},
            )
            assert upload_response.status_code == 200
            file_id = upload_response.json()["data"]["file_id"]

            # 下载文件
            download_response = self.client.get(f"/api/v1/files/download/{file_id}")

        assert download_response.status_code == 200
        assert download_response.content == test_content

    def test_download_file_not_found(self):
        """测试下载不存在的文件。"""
        with patch("src.api.v1.endpoints.files.UPLOAD_DIR", self.test_upload_dir):
            response = self.client.get("/api/v1/files/download/nonexistent-id")

        assert response.status_code == 200
        data = response.json()
        assert "文件不存在" in data["message"]

    def test_get_upload_stats(self):
        """测试获取上传统计信息。"""
        with patch("src.api.v1.endpoints.files.UPLOAD_DIR", self.test_upload_dir):
            response = self.client.get("/api/v1/files/stats")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "total_files" in data["data"]
        assert "total_size" in data["data"]
        assert "type_statistics" in data["data"]
        assert "upload_directory" in data["data"]

    def test_upload_too_many_files(self):
        """测试上传过多文件。"""
        # 创建超过限制数量的文件
        files = [
            ("files", (f"file{i}.txt", io.BytesIO(b"content"), "text/plain"))
            for i in range(11)  # 超过10个文件的限制
        ]

        with patch("src.api.v1.endpoints.files.UPLOAD_DIR", self.test_upload_dir):
            response = self.client.post("/api/v1/files/upload/multiple", files=files)

        assert response.status_code == 400
        assert "一次最多只能上传10个文件" in response.json()["message"]
