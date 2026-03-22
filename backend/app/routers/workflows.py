"""
工作流管理路由
处理工作流模板的CRUD操作
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.workflow import (
    WorkflowCreate, WorkflowUpdate, WorkflowDetailResponse,
    WorkflowListResponse, WorkflowListRequest, WorkflowListData,
    PaginationResponse, WorkItemCreate, WorkItemUpdate, WorkItemResponse,
    WorkflowStatus
)
from app.services.workflow_service import WorkflowService

router = APIRouter(prefix="/api/workflows", tags=["工作流管理"])


@router.get("", response_model=dict)
def list_workflows(
    page: int = Query(1, ge=1, description="页码"),
    per_page: int = Query(20, ge=1, le=100, description="每页条数"),
    is_preset: Optional[bool] = Query(None, description="是否预置模板"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取工作流模板列表
    - 支持分页
    - 支持按预置模板筛选
    - 支持关键词搜索
    """
    service = WorkflowService(db)
    workflows, total = service.list_workflows(
        page=page,
        per_page=per_page,
        is_preset=is_preset,
        keyword=keyword
    )

    # 计算工作项数量
    items = []
    for wf in workflows:
        item_data = {
            "id": wf.id,
            "name": wf.name,
            "description": wf.description,
            "is_preset": wf.is_preset,
            "status": wf.status,
            "work_item_count": len(wf.work_items),
            "created_by": wf.created_by,
            "created_at": wf.created_at
        }
        items.append(item_data)

    return {
        "code": 0,
        "data": {
            "items": items,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page
            }
        }
    }


@router.post("", response_model=dict)
def create_workflow(
    data: WorkflowCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建工作流模板
    - 同时创建工作项和验收标准
    - 支持设置工作项依赖关系
    """
    service = WorkflowService(db)
    workflow = service.create_workflow(data, current_user.id)

    return {
        "code": 0,
        "data": {
            "id": workflow.id,
            "name": workflow.name,
            "message": "工作流模板创建成功"
        }
    }


@router.get("/{workflow_id}", response_model=dict)
def get_workflow(
    workflow_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取工作流模板详情
    - 包含所有工作项和验收标准
    """
    service = WorkflowService(db)
    workflow = service.get_workflow(workflow_id)

    if not workflow:
        raise HTTPException(status_code=404, detail="工作流模板不存在")

    # 构建响应数据
    work_items_data = []
    for wi in workflow.work_items:
        criteria_data = []
        for criteria in wi.acceptance_criteria:
            criteria_data.append({
                "id": criteria.id,
                "work_item_id": criteria.work_item_id,
                "content": criteria.content,
                "is_required": criteria.is_required,
                "criteria_type": criteria.criteria_type,
                "auto_check_script": criteria.auto_check_script,
                "display_order": criteria.display_order,
                "created_at": criteria.created_at,
                "updated_at": criteria.updated_at
            })

        work_items_data.append({
            "id": wi.id,
            "workflow_id": wi.workflow_id,
            "name": wi.name,
            "description": wi.description,
            "work_item_type": wi.work_item_type,
            "display_order": wi.display_order,
            "estimated_duration": wi.estimated_duration,
            "is_required": wi.is_required,
            "acceptance_criteria": criteria_data,
            "created_at": wi.created_at,
            "updated_at": wi.updated_at
        })

    return {
        "code": 0,
        "data": {
            "id": workflow.id,
            "name": workflow.name,
            "description": workflow.description,
            "is_preset": workflow.is_preset,
            "status": workflow.status,
            "work_items": work_items_data,
            "created_by": workflow.created_by,
            "created_at": workflow.created_at,
            "updated_at": workflow.updated_at
        }
    }


@router.put("/{workflow_id}", response_model=dict)
def update_workflow(
    workflow_id: int,
    data: WorkflowUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新工作流模板
    - 支持更新基本信息
    - 支持更新状态
    """
    service = WorkflowService(db)
    workflow = service.update_workflow(workflow_id, data, current_user.id)

    if not workflow:
        raise HTTPException(status_code=404, detail="工作流模板不存在")

    return {
        "code": 0,
        "data": {
            "id": workflow.id,
            "name": workflow.name,
            "message": "工作流模板更新成功"
        }
    }


@router.delete("/{workflow_id}", response_model=dict)
def delete_workflow(
    workflow_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除工作流模板
    - 检查是否有正在执行的实例
    """
    service = WorkflowService(db)

    try:
        success = service.delete_workflow(workflow_id, current_user.id)
        if not success:
            raise HTTPException(status_code=404, detail="工作流模板不存在")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "code": 0,
        "data": {
            "message": "工作流模板删除成功"
        }
    }


# ==================== 工作项管理 ====================

@router.post("/{workflow_id}/work-items", response_model=dict)
def create_work_item(
    workflow_id: int,
    data: WorkItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    在工作流中创建工作项
    - 支持设置验收标准
    - 支持设置依赖关系
    """
    service = WorkflowService(db)

    # 检查工作流是否存在
    workflow = service.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="工作流模板不存在")

    work_item = service.create_work_item(workflow_id, data)

    return {
        "code": 0,
        "data": {
            "id": work_item.id,
            "name": work_item.name,
            "message": "工作项创建成功"
        }
    }


@router.put("/{workflow_id}/work-items/{work_item_id}", response_model=dict)
def update_work_item(
    workflow_id: int,
    work_item_id: int,
    data: WorkItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新工作项
    """
    service = WorkflowService(db)

    # 检查工作流是否存在
    workflow = service.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="工作流模板不存在")

    work_item = service.update_work_item(work_item_id, data)

    if not work_item:
        raise HTTPException(status_code=404, detail="工作项不存在")

    return {
        "code": 0,
        "data": {
            "id": work_item.id,
            "name": work_item.name,
            "message": "工作项更新成功"
        }
    }


@router.delete("/{workflow_id}/work-items/{work_item_id}", response_model=dict)
def delete_work_item(
    workflow_id: int,
    work_item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除工作项
    """
    service = WorkflowService(db)

    # 检查工作流是否存在
    workflow = service.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="工作流模板不存在")

    success = service.delete_work_item(work_item_id)

    if not success:
        raise HTTPException(status_code=404, detail="工作项不存在")

    return {
        "code": 0,
        "data": {
            "message": "工作项删除成功"
        }
    }
