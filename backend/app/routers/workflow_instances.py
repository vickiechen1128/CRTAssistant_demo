"""
工作流实例路由
处理工作流实例的创建、执行和进度跟踪
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.workflow import (
    WorkflowInstanceCreate, WorkflowInstanceResponse,
    WorkItemExecuteRequest, WorkItemVerifyRequest,
    WorkflowInstanceListRequest, PaginationResponse,
    WorkflowInstanceStatus
)
from app.services.workflow_service import WorkflowService

router = APIRouter(prefix="/api/workflow-instances", tags=["工作流实例"])


@router.get("", response_model=dict)
def list_instances(
    page: int = Query(1, ge=1, description="页码"),
    per_page: int = Query(20, ge=1, le=100, description="每页条数"),
    workflow_id: Optional[int] = Query(None, description="工作流模板ID"),
    task_id: Optional[int] = Query(None, description="准入任务ID"),
    status: Optional[str] = Query(None, description="状态"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取工作流实例列表
    - 支持按工作流模板筛选
    - 支持按准入任务筛选
    - 支持按状态筛选
    """
    service = WorkflowService(db)
    instances, total = service.list_instances(
        page=page,
        per_page=per_page,
        workflow_id=workflow_id,
        task_id=task_id,
        status=status
    )

    items = []
    for inst in instances:
        items.append({
            "id": inst.id,
            "workflow_id": inst.workflow_id,
            "task_id": inst.task_id,
            "status": inst.status,
            "overall_progress": inst.overall_progress,
            "started_at": inst.started_at,
            "completed_at": inst.completed_at,
            "created_by": inst.created_by,
            "created_at": inst.created_at,
            "updated_at": inst.updated_at
        })

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
def create_instance(
    data: WorkflowInstanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建工作流实例
    - 关联到准入任务
    - 分配工作项责任人
    """
    service = WorkflowService(db)
    instance = service.create_instance(
        workflow_id=data.workflow_id if hasattr(data, 'workflow_id') else 1,
        data=data,
        user_id=current_user.id
    )

    return {
        "code": 0,
        "data": {
            "id": instance.id,
            "workflow_id": instance.workflow_id,
            "task_id": instance.task_id,
            "status": instance.status,
            "message": "工作流实例创建成功"
        }
    }


@router.get("/{instance_id}", response_model=dict)
def get_instance(
    instance_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取工作流实例详情
    - 包含所有工作项实例
    - 包含验收结果
    """
    service = WorkflowService(db)
    instance = service.get_instance(instance_id)

    if not instance:
        raise HTTPException(status_code=404, detail="工作流实例不存在")

    # 构建响应数据
    work_item_instances_data = []
    for wi in instance.work_item_instances:
        criteria_results_data = []
        for result in wi.criteria_results:
            criteria_results_data.append({
                "id": result.id,
                "work_item_instance_id": result.work_item_instance_id,
                "criteria_id": result.criteria_id,
                "status": result.status,
                "remark": result.remark,
                "verified_by": result.verified_by,
                "verified_at": result.verified_at,
                "created_at": result.created_at,
                "updated_at": result.updated_at
            })

        work_item_instances_data.append({
            "id": wi.id,
            "instance_id": wi.instance_id,
            "work_item_id": wi.work_item_id,
            "work_item": {
                "id": wi.work_item.id,
                "name": wi.work_item.name,
                "description": wi.work_item.description,
                "work_item_type": wi.work_item.work_item_type,
                "estimated_duration": wi.work_item.estimated_duration
            } if wi.work_item else None,
            "status": wi.status,
            "progress": wi.progress,
            "assignee_id": wi.assignee_id,
            "reviewer_id": wi.reviewer_id,
            "started_at": wi.started_at,
            "completed_at": wi.completed_at,
            "actual_duration": wi.actual_duration,
            "remark": wi.remark,
            "criteria_results": criteria_results_data,
            "created_at": wi.created_at,
            "updated_at": wi.updated_at
        })

    return {
        "code": 0,
        "data": {
            "id": instance.id,
            "workflow_id": instance.workflow_id,
            "workflow": {
                "id": instance.workflow.id,
                "name": instance.workflow.name
            } if instance.workflow else None,
            "task_id": instance.task_id,
            "status": instance.status,
            "overall_progress": instance.overall_progress,
            "started_at": instance.started_at,
            "completed_at": instance.completed_at,
            "created_by": instance.created_by,
            "created_at": instance.created_at,
            "updated_at": instance.updated_at,
            "work_item_instances": work_item_instances_data
        }
    }


@router.post("/{instance_id}/execute", response_model=dict)
def execute_work_item(
    instance_id: str,
    data: WorkItemExecuteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    开始执行工作项
    - 检查依赖是否完成
    - 更新工作项状态为进行中
    """
    service = WorkflowService(db)

    try:
        work_item_instance = service.execute_work_item(
            instance_id=instance_id,
            data=data,
            user_id=current_user.id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not work_item_instance:
        raise HTTPException(status_code=404, detail="工作项实例不存在")

    return {
        "code": 0,
        "data": {
            "work_item_id": work_item_instance.work_item_id,
            "status": work_item_instance.status,
            "started_at": work_item_instance.started_at,
            "message": "工作项已开始执行"
        }
    }


@router.post("/{instance_id}/verify", response_model=dict)
def verify_work_item(
    instance_id: str,
    data: WorkItemVerifyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    验收工作项
    - 更新验收结果
    - 更新工作项状态
    - 更新整体进度
    """
    service = WorkflowService(db)

    work_item_instance = service.verify_work_item(
        instance_id=instance_id,
        data=data,
        user_id=current_user.id
    )

    if not work_item_instance:
        raise HTTPException(status_code=404, detail="工作项实例不存在")

    return {
        "code": 0,
        "data": {
            "work_item_id": work_item_instance.work_item_id,
            "status": work_item_instance.status,
            "progress": work_item_instance.progress,
            "completed_at": work_item_instance.completed_at,
            "message": "工作项验收成功" if data.status.value == "completed" else "工作项已驳回"
        }
    }


@router.get("/{instance_id}/progress", response_model=dict)
def get_progress(
    instance_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取工作流执行进度
    - 整体进度百分比
    - 各工作项状态
    - 关键路径
    - 阻塞项
    - 预估完成时间
    """
    service = WorkflowService(db)
    progress = service.get_progress(instance_id)

    if not progress:
        raise HTTPException(status_code=404, detail="工作流实例不存在")

    return {
        "code": 0,
        "data": progress
    }


@router.put("/{instance_id}/work-items/{work_item_id}/progress", response_model=dict)
def update_work_item_progress(
    instance_id: str,
    work_item_id: int,
    progress: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新工作项进度
    - 实时更新进度百分比
    """
    service = WorkflowService(db)

    work_item_instance = service.update_work_item_progress(
        instance_id=instance_id,
        work_item_id=work_item_id,
        progress=progress,
        user_id=current_user.id
    )

    if not work_item_instance:
        raise HTTPException(status_code=404, detail="工作项实例不存在")

    return {
        "code": 0,
        "data": {
            "work_item_id": work_item_instance.work_item_id,
            "progress": work_item_instance.progress,
            "message": "进度更新成功"
        }
    }
