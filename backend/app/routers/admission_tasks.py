"""
准入任务路由
处理准入任务的CRUD和状态管理
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from ..database import get_db
from ..models.user import User
from ..routers.auth import get_current_user
from ..services.task_service import TaskService
from ..schemas.admission_task import (
    AdmissionTaskCreate, AdmissionTaskUpdate, 
    AdmissionTaskResponse, AdmissionTaskList
)

router = APIRouter(prefix="/api/admission-tasks", tags=["准入任务"])


@router.get("", response_model=dict)
def list_tasks(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    system_name: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取准入任务列表
    - 支持分页
    - 支持按状态和系统名称筛选
    """
    service = TaskService(db)
    skip = (page - 1) * per_page
    tasks, total = service.list_tasks(skip, per_page, status, system_name)
    
    # 构建响应
    items = []
    for task in tasks:
        items.append({
            "id": task.id,
            "task_no": task.task_no,
            "system_name": task.system_name,
            "system_code": task.system_code,
            "version": task.version,
            "release_date": task.release_date.isoformat() if task.release_date else None,
            "status": task.status.value,
            "progress": task.progress,
            "creator": {"id": task.creator.id, "real_name": task.creator.real_name} if task.creator else None,
            "manager": {"id": task.manager.id, "real_name": task.manager.real_name} if task.manager else None,
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "updated_at": task.updated_at.isoformat() if task.updated_at else None
        })
    
    return {
        "code": 0,
        "data": {
            "items": items,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": (total + per_page - 1) // per_page
            }
        }
    }


@router.post("", response_model=dict)
def create_task(
    task_data: AdmissionTaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建准入任务
    - 自动生成任务编号
    - 如果指定了模板，自动创建检查项
    """
    service = TaskService(db)
    task = service.create_task(task_data, current_user.id)
    
    return {
        "code": 0,
        "data": {
            "id": task.id,
            "task_no": task.task_no,
            "system_name": task.system_name,
            "status": task.status.value,
            "progress": task.progress,
            "created_at": task.created_at.isoformat() if task.created_at else None
        },
        "message": "任务创建成功"
    }


@router.get("/{task_id}", response_model=dict)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取任务详情
    - 包含基本信息
    - 包含检查项汇总统计
    - 包含各维度进度
    """
    service = TaskService(db)
    task = service.get_task(task_id)
    
    if not task:
        return {"code": 4040, "message": "任务不存在"}
    
    # 获取检查项汇总
    from ..services.checklist_service import ChecklistService
    checklist_service = ChecklistService(db)
    checklist_summary = checklist_service.get_summary(task_id)
    dimension_progress = checklist_service.get_dimension_progress(task_id)
    
    return {
        "code": 0,
        "data": {
            "id": task.id,
            "task_no": task.task_no,
            "system_name": task.system_name,
            "system_code": task.system_code,
            "version": task.version,
            "release_date": task.release_date.isoformat() if task.release_date else None,
            "status": task.status.value,
            "progress": task.progress,
            "remark": task.remark,
            "creator": {"id": task.creator.id, "real_name": task.creator.real_name} if task.creator else None,
            "manager": {"id": task.manager.id, "real_name": task.manager.real_name} if task.manager else None,
            "checklist_summary": checklist_summary,
            "control_dimension_progress": dimension_progress,
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "updated_at": task.updated_at.isoformat() if task.updated_at else None
        }
    }


@router.post("/{task_id}/start", response_model=dict)
def start_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    启动任务
    - 将任务从草稿状态变为进行中
    """
    service = TaskService(db)
    try:
        task = service.start_task(task_id)
        return {
            "code": 0,
            "data": {
                "id": task.id,
                "status": task.status.value
            },
            "message": "任务已启动"
        }
    except Exception as e:
        return {"code": 4000, "message": str(e)}
