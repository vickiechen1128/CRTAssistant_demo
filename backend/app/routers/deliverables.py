"""
交付物路由
处理文件上传、下载和管理
"""

from fastapi import APIRouter, Depends, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from typing import Optional
import os
import hashlib
from datetime import datetime

from ..database import get_db
from ..models.user import User
from ..routers.auth import get_current_user
from ..services.deliverable_service import DeliverableService
from .. import config

router = APIRouter(prefix="/api/deliverables", tags=["交付物"])


@router.get("", response_model=dict)
def list_deliverables(
    task_id: Optional[int] = Query(None, description="任务ID"),
    checklist_item_id: Optional[int] = Query(None, description="检查项ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取交付物列表
    - 可按任务ID查询
    - 可按检查项ID查询
    """
    service = DeliverableService(db)
    
    if checklist_item_id:
        deliverables = service.get_by_checklist_item(checklist_item_id)
    elif task_id:
        deliverables = service.get_by_task(task_id)
    else:
        deliverables = service.get_all()
    
    data = []
    for d in deliverables:
        data.append({
            "id": d.id,
            "checklist_item_id": d.checklist_item_id,
            "file_name": d.file_name,
            "file_type": d.file_type.value if d.file_type else "other",
            "file_size": d.file_size,
            "file_path": d.file_path,
            "description": d.description,
            "uploaded_at": d.uploaded_at.isoformat() if d.uploaded_at else None,
            "uploader": {
                "id": d.uploader.id,
                "real_name": d.uploader.real_name
            } if d.uploader else None
        })
    
    return {"code": 0, "data": {"items": data, "total": len(data)}}


@router.post("", response_model=dict)
def upload_deliverable(
    checklist_item_id: int = Form(..., description="检查项ID"),
    description: Optional[str] = Form(None, description="文件描述"),
    file: UploadFile = File(..., description="上传的文件"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    上传交付物
    - 支持多种文件类型
    - 文件大小限制50MB
    - 自动计算文件Hash
    """
    service = DeliverableService(db)
    
    try:
        # 保存文件
        deliverable = service.upload_file(
            checklist_item_id=checklist_item_id,
            file=file,
            description=description,
            uploader_id=current_user.id
        )
        
        return {
            "code": 0,
            "data": {
                "id": deliverable.id,
                "file_name": deliverable.file_name,
                "file_type": deliverable.file_type.value if deliverable.file_type else "other",
                "file_size": deliverable.file_size,
                "description": deliverable.description,
                "uploaded_at": deliverable.uploaded_at.isoformat() if deliverable.uploaded_at else None,
                "uploader": {
                    "id": current_user.id,
                    "real_name": current_user.real_name
                }
            },
            "message": "上传成功"
        }
    except ValueError as e:
        return {"code": 4000, "message": str(e)}
    except Exception as e:
        return {"code": 5000, "message": f"上传失败: {str(e)}"}


@router.get("/{deliverable_id}")
def download_deliverable(
    deliverable_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    下载交付物
    - 返回文件流
    """
    from fastapi.responses import FileResponse
    
    service = DeliverableService(db)
    deliverable = service.get_by_id(deliverable_id)
    
    if not deliverable:
        return {"code": 4040, "message": "文件不存在"}
    
    if not os.path.exists(deliverable.file_path):
        return {"code": 4040, "message": "文件已丢失"}
    
    # 获取文件类型对应的Content-Type
    content_type_map = {
        "pdf": "application/pdf",
        "word": "application/msword",
        "excel": "application/vnd.ms-excel",
        "text": "text/plain",
        "script": "text/plain",
        "log": "text/plain",
    }
    content_type = content_type_map.get(
        deliverable.file_type.value if deliverable.file_type else "other",
        "application/octet-stream"
    )
    
    return FileResponse(
        path=deliverable.file_path,
        filename=deliverable.file_name,
        media_type=content_type
    )


@router.delete("/{deliverable_id}", response_model=dict)
def delete_deliverable(
    deliverable_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除交付物（软删除）
    - 仅上传者或管理员可删除
    """
    service = DeliverableService(db)
    
    try:
        service.delete_deliverable(deliverable_id, current_user.id)
        return {"code": 0, "message": "删除成功"}
    except ValueError as e:
        return {"code": 4000, "message": str(e)}
    except Exception as e:
        return {"code": 5000, "message": f"删除失败: {str(e)}"}
