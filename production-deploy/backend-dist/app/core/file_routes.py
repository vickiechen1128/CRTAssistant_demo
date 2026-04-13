"""
文件上传路由
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List

from .upload import save_upload_file

router = APIRouter(prefix="/upload", tags=["文件上传"])


@router.post("")
async def upload_file(file: UploadFile = File(...)):
    """
    上传单个文件
    
    支持上传图片（jpg, png, gif, webp）和文档（pdf, doc, docx）
    最大文件大小：20MB
    
    Returns:
        文件信息
    """
    result = await save_upload_file(file)
    return {
        "success": True,
        "message": "文件上传成功",
        "data": result
    }


@router.post("/batch")
async def upload_files(files: List[UploadFile] = File(...)):
    """
    批量上传文件
    
    同时上传多个文件
    最大文件大小：每个20MB
    
    Returns:
        文件信息列表
    """
    results = []
    errors = []
    
    for file in files:
        try:
            result = await save_upload_file(file)
            results.append(result)
        except HTTPException as e:
            errors.append({
                "file_name": file.filename,
                "error": e.detail
            })
    
    return {
        "success": len(errors) == 0,
        "message": f"成功上传 {len(results)} 个文件，失败 {len(errors)} 个",
        "data": {
            "success_files": results,
            "failed_files": errors
        }
    }
