"""
检查清单路由
处理检查项的查询、更新和确认
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from ..database import get_db
from ..models.user import User
from ..routers.auth import get_current_user
from ..services.checklist_service import ChecklistService
from ..schemas.checklist import ChecklistItemUpdate, ChecklistItemVerify

router = APIRouter(prefix="/api/checklist-items", tags=["检查清单"])


@router.get("", response_model=dict)
def list_items(
    task_id: int = Query(..., description="任务ID"),
    control_dimension: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取检查项列表
    - 按任务ID查询
    - 支持按管控维度和状态筛选
    """
    service = ChecklistService(db)
    items = service.list_items(task_id, control_dimension, status)
    
    # 构建响应
    data = []
    for item in items:
        data.append({
            "id": item.id,
            "task_id": item.task_id,
            "control_dimension": item.control_dimension.value,
            "category": item.category,
            "item_name": item.item_name,
            "description": item.description,
            "acceptance_criteria": item.acceptance_criteria,
            "status": item.status.value,
            "assignee": {"id": item.assignee.id, "real_name": item.assignee.real_name} if item.assignee else None,
            "verifier": {"id": item.verifier.id, "real_name": item.verifier.real_name} if item.verifier else None,
            "verified_at": item.verified_at.isoformat() if item.verified_at else None,
            "verification_remark": item.verification_remark,
            "due_date": item.due_date.isoformat() if item.due_date else None,
            "sort_order": item.sort_order,
            "created_at": item.created_at.isoformat() if item.created_at else None
        })
    
    return {
        "code": 0,
        "data": {"items": data, "total": len(data)}
    }


@router.get("/{item_id}", response_model=dict)
def get_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取检查项详情"""
    service = ChecklistService(db)
    item = service.get_item(item_id)
    
    if not item:
        return {"code": 4040, "message": "检查项不存在"}
    
    return {
        "code": 0,
        "data": {
            "id": item.id,
            "task_id": item.task_id,
            "control_dimension": item.control_dimension.value,
            "category": item.category,
            "item_name": item.item_name,
            "description": item.description,
            "acceptance_criteria": item.acceptance_criteria,
            "status": item.status.value,
            "assignee": {"id": item.assignee.id, "real_name": item.assignee.real_name} if item.assignee else None,
            "due_date": item.due_date.isoformat() if item.due_date else None,
            "sort_order": item.sort_order
        }
    }


@router.put("/{item_id}", response_model=dict)
def update_item(
    item_id: int,
    item_data: ChecklistItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新检查项
    - 可更新责任人、截止日期、备注
    """
    service = ChecklistService(db)
    try:
        item = service.update_item(item_id, item_data)
        return {
            "code": 0,
            "data": {
                "id": item.id,
                "assignee_id": item.assignee_id,
                "due_date": item.due_date.isoformat() if item.due_date else None
            },
            "message": "更新成功"
        }
    except Exception as e:
        return {"code": 4000, "message": str(e)}


@router.post("/{item_id}/verify", response_model=dict)
def verify_item(
    item_id: int,
    verify_data: ChecklistItemVerify,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    确认检查项
    - 通过：标记为已通过
    - 驳回：标记为已驳回，需要重新处理
    """
    service = ChecklistService(db)
    try:
        item = service.verify_item(item_id, verify_data, current_user.id)
        
        # 更新任务进度
        from ..services.task_service import TaskService
        task_service = TaskService(db)
        task_service.update_progress(item.task_id)
        
        return {
            "code": 0,
            "data": {
                "id": item.id,
                "status": item.status.value,
                "verifier": {"id": current_user.id, "real_name": current_user.real_name},
                "verified_at": item.verified_at.isoformat() if item.verified_at else None
            },
            "message": "确认成功"
        }
    except Exception as e:
        return {"code": 4000, "message": str(e)}
