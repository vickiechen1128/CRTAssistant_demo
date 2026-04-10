"""
文件上传工具模块
"""
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import UploadFile, HTTPException

# 上传文件存储目录
UPLOAD_DIR = Path(__file__).parent.parent.parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# 允许的文件类型
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
ALLOWED_DOCUMENT_TYPES = {"application/pdf", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
ALLOWED_FILE_TYPES = ALLOWED_IMAGE_TYPES | ALLOWED_DOCUMENT_TYPES

# 最大文件大小 (20MB)
MAX_FILE_SIZE = 20 * 1024 * 1024


def validate_file(file: UploadFile) -> None:
    """
    验证文件类型和大小
    
    Args:
        file: 上传的文件
        
    Raises:
        HTTPException: 验证失败时抛出
    """
    # 验证文件类型
    content_type = file.content_type
    if content_type not in ALLOWED_FILE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型: {content_type}。只允许上传图片和PDF文件。"
        )
    
    # 验证文件大小（在读取后验证）


def generate_file_path(filename: str) -> Path:
    """
    生成文件存储路径
    
    Args:
        filename: 原始文件名
        
    Returns:
        生成的文件路径
    """
    # 提取文件扩展名
    ext = Path(filename).suffix.lower()
    
    # 生成唯一文件名
    unique_name = f"{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:8]}{ext}"
    
    # 按日期创建子目录
    date_dir = UPLOAD_DIR / datetime.now().strftime('%Y%m')
    date_dir.mkdir(exist_ok=True)
    
    return date_dir / unique_name


def get_file_url(file_path: Path) -> str:
    """
    获取文件访问URL
    
    Args:
        file_path: 文件路径
        
    Returns:
        文件URL
    """
    # 获取相对于上传目录的路径
    relative_path = file_path.relative_to(UPLOAD_DIR)
    return f"/uploads/{relative_path}"


async def save_upload_file(file: UploadFile) -> dict:
    """
    保存上传的文件
    
    Args:
        file: 上传的文件
        
    Returns:
        文件信息字典
        
    Raises:
        HTTPException: 保存失败时抛出
    """
    # 验证文件
    validate_file(file)
    
    # 生成文件路径
    file_path = generate_file_path(file.filename)
    
    try:
        # 读取文件内容
        content = await file.read()
        
        # 验证文件大小
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"文件大小超过限制。最大允许 {MAX_FILE_SIZE // 1024 // 1024}MB"
            )
        
        # 保存文件
        with open(file_path, "wb") as f:
            f.write(content)
        
        # 返回文件信息
        return {
            "file_id": str(uuid.uuid4()),
            "file_name": file.filename,
            "file_url": get_file_url(file_path),
            "file_size": len(content),
            "content_type": file.content_type,
            "uploaded_at": datetime.utcnow().isoformat(),
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"文件保存失败: {str(e)}"
        )
    finally:
        await file.close()
