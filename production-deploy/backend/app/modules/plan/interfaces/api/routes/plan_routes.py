"""
计划模块路由
FastAPI 路由定义
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.core.database import get_db

from ....application.dtos.plan_dtos import (
    CreatePlanRequest,
    UpdatePlanRequest,
    PlanFilterRequest,
    LinkInventoryRequest,
    StartPlanRequest,
    CompletePlanRequest,
    CancelPlanRequest,
    PlanPreviewRequest,
)
from ....application.plan_service import PlanService
from ....domain.services.plan_domain_service import PlanDomainService
from ....domain.services.plan_completion_service import PlanCompletionService
from ....infrastructure.persistence.plan_repository_impl import PlanRepositoryImpl
from ....infrastructure.services.inventory_service_impl import (
    InventoryServiceImpl,
    InventoryLifecycleLogServiceImpl,
)
from ....infrastructure.services.data_sync_service import DataSyncService
from ..schemas.plan_schemas import (
    CreatePlanSchema,
    UpdatePlanSchema,
    PlanResponseSchema,
    PlanDetailResponseSchema,
    PlanListResponseSchema,
    PlanFilterSchema,
    LinkInventorySchema,
    StartPlanSchema,
    CompletePlanSchema,
    CancelPlanSchema,
    ApiResponseSchema,
    PlanPreviewRequestSchema,
    PlanPreviewResponseSchema,
    GeneratePlanIdResponseSchema,
)

router = APIRouter(prefix="/plans", tags=["计划管理"])


def get_plan_service(db: Session = Depends(get_db)) -> PlanService:
    """依赖注入：获取PlanService实例"""
    repository = PlanRepositoryImpl(db)
    domain_service = PlanDomainService(repository)

    # 初始化台账服务
    inventory_service = InventoryServiceImpl(db)
    lifecycle_service = InventoryLifecycleLogServiceImpl(db)

    # 初始化数据同步服务
    data_sync_service = DataSyncService(db)

    # 初始化计划完成服务（包含数据同步）
    completion_service = PlanCompletionService(
        inventory_service,
        lifecycle_service,
        data_sync_service
    )

    return PlanService(repository, domain_service, completion_service, inventory_service)


@router.post("", response_model=ApiResponseSchema[PlanResponseSchema])
def create_plan(
    request: CreatePlanSchema,
    plan_service: PlanService = Depends(get_plan_service),
    current_user: str = "admin"  # TODO: 从认证获取
):
    """创建计划"""
    try:
        dto = CreatePlanRequest(**request.dict())
        result = plan_service.create_plan(dto, current_user)
        return ApiResponseSchema(data=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=ApiResponseSchema[PlanListResponseSchema])
def list_plans(
    status: Optional[str] = Query(None, description="状态筛选"),
    category: Optional[str] = Query(None, description="分类筛选"),
    priority: Optional[str] = Query(None, description="优先级筛选"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    plan_service: PlanService = Depends(get_plan_service)
):
    """查询计划列表"""
    filter_request = PlanFilterRequest(
        status=status,
        category=category,
        priority=priority,
        keyword=keyword,
        page=page,
        page_size=page_size
    )
    result = plan_service.list_plans(filter_request)
    return ApiResponseSchema(data=result)


@router.get("/generate-id", response_model=ApiResponseSchema[GeneratePlanIdResponseSchema])
def generate_plan_id(
    plan_service: PlanService = Depends(get_plan_service)
):
    """预生成PlanID（用于前端展示）"""
    result = plan_service.generate_plan_id()
    return ApiResponseSchema(data=result)


@router.post("/preview", response_model=ApiResponseSchema[PlanPreviewResponseSchema])
def preview_changes(
    request: PlanPreviewRequestSchema,
    plan_service: PlanService = Depends(get_plan_service)
):
    """预览计划变更（用于Step 4）"""
    try:
        dto = PlanPreviewRequest(**request.dict())
        result = plan_service.preview_changes(dto)
        return ApiResponseSchema(data=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{plan_id}", response_model=ApiResponseSchema[PlanResponseSchema])
def get_plan(
    plan_id: str,
    plan_service: PlanService = Depends(get_plan_service)
):
    """获取计划基本信息"""
    try:
        result = plan_service.get_plan(plan_id)
        return ApiResponseSchema(data=result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{plan_id}/detail", response_model=ApiResponseSchema[PlanDetailResponseSchema])
def get_plan_detail(
    plan_id: str,
    plan_service: PlanService = Depends(get_plan_service)
):
    """获取计划详情（包含完整关联信息：台账、模块、生命周期日志）"""
    try:
        result = plan_service.get_plan_detail(plan_id)
        return ApiResponseSchema(data=result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{plan_id}", response_model=ApiResponseSchema[PlanResponseSchema])
def update_plan(
    plan_id: str,
    request: UpdatePlanSchema,
    plan_service: PlanService = Depends(get_plan_service),
    current_user: str = "admin"  # TODO: 从认证获取
):
    """更新计划"""
    try:
        dto = UpdatePlanRequest(**request.dict(exclude_unset=True))
        result = plan_service.update_plan(plan_id, dto, current_user)
        return ApiResponseSchema(data=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{plan_id}", response_model=ApiResponseSchema[bool])
def delete_plan(
    plan_id: str,
    plan_service: PlanService = Depends(get_plan_service),
    current_user: str = "admin"  # TODO: 从认证获取
):
    """删除计划"""
    try:
        result = plan_service.delete_plan(plan_id, current_user)
        return ApiResponseSchema(data=result, message="计划已删除")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{plan_id}/start", response_model=ApiResponseSchema[PlanResponseSchema])
def start_plan(
    plan_id: str,
    request: StartPlanSchema,
    plan_service: PlanService = Depends(get_plan_service),
    current_user: str = "admin"  # TODO: 从认证获取
):
    """启动计划"""
    try:
        result = plan_service.start_plan(plan_id, current_user)
        return ApiResponseSchema(data=result, message="计划已启动")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{plan_id}/complete", response_model=ApiResponseSchema[PlanResponseSchema])
def complete_plan(
    plan_id: str,
    request: CompletePlanSchema,
    plan_service: PlanService = Depends(get_plan_service),
    current_user: str = "admin"  # TODO: 从认证获取
):
    """完成计划 - 触发台账更新和生命周期日志生成"""
    try:
        result = plan_service.complete_plan(plan_id, current_user)
        return ApiResponseSchema(data=result, message="计划已完成")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{plan_id}/cancel", response_model=ApiResponseSchema[PlanResponseSchema])
def cancel_plan(
    plan_id: str,
    request: CancelPlanSchema,
    plan_service: PlanService = Depends(get_plan_service),
    current_user: str = "admin"  # TODO: 从认证获取
):
    """
    取消计划

    PRD v3.1 限制：IN_PROGRESS 状态的计划不允许取消
    错误码：CANNOT_CANCEL_IN_PROGRESS_PLAN
    """
    try:
        result = plan_service.cancel_plan(plan_id, current_user, request.reason)
        return ApiResponseSchema(data=result, message="计划已取消")
    except ValueError as e:
        error_msg = str(e)
        # 检查是否是 IN_PROGRESS 状态取消的错误
        if "IN_PROGRESS" in error_msg and "cancel" in error_msg.lower():
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "CANNOT_CANCEL_IN_PROGRESS_PLAN",
                    "message": "计划已启动，不允许取消",
                    "current_status": "IN_PROGRESS"
                }
            )
        raise HTTPException(status_code=400, detail=error_msg)


@router.post("/{plan_id}/inventory", response_model=ApiResponseSchema[PlanResponseSchema])
def link_inventory(
    plan_id: str,
    request: LinkInventorySchema,
    plan_service: PlanService = Depends(get_plan_service),
    current_user: str = "admin"  # TODO: 从认证获取
):
    """关联台账"""
    try:
        dto = LinkInventoryRequest(inventory_ids=request.inventory_ids)
        result = plan_service.link_inventory(plan_id, dto.inventory_ids, current_user)
        return ApiResponseSchema(data=result, message="台账关联成功")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
