"""文件上传和管理相关的API端点。"""

import uuid
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse

from src.utils.response import success_response

router = APIRouter()

# 配置文件上传目录
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# 允许的文件类型
ALLOWED_EXTENSIONS = {
    "image": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"},
    "document": {".pdf", ".doc", ".docx", ".txt", ".rtf"},
    "archive": {".zip", ".rar", ".7z", ".tar", ".gz"},
    "video": {".mp4", ".avi", ".mov", ".wmv", ".flv"},
    "audio": {".mp3", ".wav", ".flac", ".aac"},
}

# 最大文件大小 (10MB)
MAX_FILE_SIZE = 10 * 1024 * 1024


def get_file_type(filename: str) -> str:
    """根据文件扩展名获取文件类型。"""
    ext = Path(filename).suffix.lower()
    for file_type, extensions in ALLOWED_EXTENSIONS.items():
        if ext in extensions:
            return file_type
    return "other"


def validate_file(file: UploadFile) -> None:
    """验证上传的文件。"""
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="文件名不能为空"
        )

    # 检查文件扩展名
    ext = Path(file.filename).suffix.lower()
    all_extensions = set()
    for extensions in ALLOWED_EXTENSIONS.values():
        all_extensions.update(extensions)

    if ext not in all_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"不支持的文件类型: {ext}"
        )


def save_file(file: UploadFile) -> dict:
    """保存上传的文件并返回文件信息。"""
    # 读取文件内容并检查大小
    content = file.file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"文件大小超过限制 ({MAX_FILE_SIZE // (1024 * 1024)}MB)",
        )

    # 生成唯一文件名
    file_id = str(uuid.uuid4())
    ext = Path(file.filename).suffix.lower()
    new_filename = f"{file_id}{ext}"
    file_path = UPLOAD_DIR / new_filename

    # 保存文件
    with file_path.open("wb") as buffer:
        buffer.write(content)

    return {
        "file_id": file_id,
        "original_name": file.filename,
        "filename": new_filename,
        "file_path": str(file_path),
        "file_size": len(content),
        "file_type": get_file_type(file.filename),
        "content_type": file.content_type,
        "upload_time": datetime.utcnow().isoformat(),
    }


@router.post("/upload", response_model=dict)
async def upload_single_file(file: UploadFile = File(...)):
    """上传单个文件。"""
    validate_file(file)

    try:
        file_info = save_file(file)

        return success_response(data=file_info, message="文件上传成功")
    except HTTPException:
        # 重新抛出HTTPException，保持原有状态码
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件上传失败: {e!s}",
        ) from e


@router.post("/upload/multiple", response_model=dict)
async def upload_multiple_files(files: list[UploadFile] = File(...)):
    """上传多个文件。"""
    if len(files) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="一次最多只能上传10个文件"
        )

    uploaded_files = []
    failed_files = []

    for file in files:
        try:
            validate_file(file)
            file_info = save_file(file)
            uploaded_files.append(file_info)
        except Exception as e:
            failed_files.append({"filename": file.filename, "error": str(e)})

    return success_response(
        data={
            "uploaded_files": uploaded_files,
            "failed_files": failed_files,
            "total_uploaded": len(uploaded_files),
            "total_failed": len(failed_files),
        },
        message=f"批量上传完成, 成功: {len(uploaded_files)}, 失败: {len(failed_files)}",
    )


@router.get("/download/{file_id}")
async def download_file(file_id: str):
    """下载文件。"""
    # 查找文件
    file_pattern = f"{file_id}.*"
    matching_files = list(UPLOAD_DIR.glob(file_pattern))

    if not matching_files:
        return success_response(data=None, message="文件不存在")

    file_path = matching_files[0]

    if not file_path.exists():
        return success_response(data=None, message="文件不存在")

    return FileResponse(
        path=file_path, filename=file_path.name, media_type="application/octet-stream"
    )


@router.delete("/delete/{file_id}", response_model=dict)
async def delete_file(file_id: str):
    """删除文件。"""
    # 查找文件
    file_pattern = f"{file_id}.*"
    matching_files = list(UPLOAD_DIR.glob(file_pattern))

    if not matching_files:
        return success_response(data=None, message="文件不存在")

    file_path = matching_files[0]

    try:
        file_path.unlink()  # 删除文件
        return success_response(
            data={"file_id": file_id, "deleted": True}, message="文件删除成功"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件删除失败: {e!s}",
        ) from e


@router.get("/list", response_model=dict)
async def list_files():
    """获取已上传文件列表。"""
    files = []

    for file_path in UPLOAD_DIR.iterdir():
        if file_path.is_file():
            stat = file_path.stat()
            file_id = file_path.stem

            files.append(
                {
                    "file_id": file_id,
                    "filename": file_path.name,
                    "file_size": stat.st_size,
                    "file_type": get_file_type(file_path.name),
                    "upload_time": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                }
            )

    return success_response(
        data={"files": files, "total_count": len(files)}, message="文件列表获取成功"
    )


@router.get("/info/{file_id}", response_model=dict)
async def get_file_info(file_id: str):
    """获取文件信息。"""
    # 查找文件
    file_pattern = f"{file_id}.*"
    matching_files = list(UPLOAD_DIR.glob(file_pattern))

    if not matching_files:
        return success_response(data=None, message="文件不存在")

    file_path = matching_files[0]
    stat = file_path.stat()

    # 从文件名中提取原始文件名（去掉UUID前缀）
    original_name = file_path.name
    if "." in original_name:
        # 如果有扩展名，尝试从文件名推断原始名称
        ext = file_path.suffix
        # 这里简化处理，实际应该从数据库或其他地方获取原始文件名
        original_name = f"uploaded_file{ext}"

    file_info = {
        "file_id": file_id,
        "filename": file_path.name,
        "original_name": original_name,
        "file_size": stat.st_size,
        "file_type": get_file_type(file_path.name),
        "content_type": "application/octet-stream",  # 默认类型
        "upload_time": datetime.fromtimestamp(stat.st_ctime).isoformat(),
        "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        "file_path": str(file_path),
    }

    return success_response(data=file_info, message="文件信息获取成功")


@router.get("/stats", response_model=dict)
async def get_upload_stats():
    """获取上传统计信息。"""
    files = list(UPLOAD_DIR.iterdir())
    total_files = len([f for f in files if f.is_file()])
    total_size = sum(f.stat().st_size for f in files if f.is_file())

    # 按文件类型统计
    type_stats = {}
    for file_path in files:
        if file_path.is_file():
            file_type = get_file_type(file_path.name)
            if file_type not in type_stats:
                type_stats[file_type] = {"count": 0, "size": 0}
            type_stats[file_type]["count"] += 1
            type_stats[file_type]["size"] += file_path.stat().st_size

    return success_response(
        data={
            "total_files": total_files,
            "total_size": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "type_statistics": type_stats,
            "upload_directory": str(UPLOAD_DIR.absolute()),
        },
        message="上传统计信息获取成功",
    )
