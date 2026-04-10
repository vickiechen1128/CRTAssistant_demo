"""
生命周期日志API路由
"""
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user_optional

from ....application.lifecycle_log_service import LifecycleLogService
from ....application.dtos.lifecycle_log_dtos import (
    CreateLifecycleLogDTO,
    TimelineFilterDTO,
)
from ....infrastructure.persistence.repositories.lifecycle_log_repository_impl import LifecycleLogRepositoryImpl
from ...api.schemas.lifecycle_log_schemas import (
    LifecycleLogCreateSchema,
    LifecycleLogResponseSchema,
    LogListResponseSchema,
    TimelineResponseSchema,
    TimelineFilterSchema,
    LogTypeInfoSchema,
    LogStatisticsSchema,
)

router = APIRouter(prefix="/applications/{app_id}/logs", tags=["lifecycle-logs"])


def get_lifecycle_log_service(
    db: Session = Depends(get_db)
) -> LifecycleLogService:
    """依赖注入：获取生命周期日志服务"""
    log_repo = LifecycleLogRepositoryImpl(db)
    return LifecycleLogService(log_repo)


@router.post(
    "",
    response_model=LifecycleLogResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="创建生命周期日志"
)
async def create_log(
    app_id: str,
    schema: LifecycleLogCreateSchema,
    service: LifecycleLogService = Depends(get_lifecycle_log_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """创建新的生命周期日志"""
    try:
        dto = CreateLifecycleLogDTO(
            log_type=schema.log_type,
            event_title=schema.event_title,
            description=schema.description,
            before_data=schema.before_data,
            after_data=schema.after_data,
            related_plan_id=schema.related_plan_id,
            related_module_id=schema.related_module_id,
            operator=(current_user or {}).get("username", "system"),
        )
        return await service.create_log(dto)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "",
    response_model=LogListResponseSchema,
    summary="获取生命周期日志列表"
)
async def list_logs(
    app_id: str,
    log_type: Optional[str] = Query(None, description="日志类型过滤"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    service: LifecycleLogService = Depends(get_lifecycle_log_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """获取应用的生命周期日志列表"""
    logs = await service.list_logs(app_id, log_type, limit, offset)
    return LogListResponseSchema(
        items=logs,
        total=len(logs)
    )


@router.get(
    "/{log_id}",
    response_model=LifecycleLogResponseSchema,
    summary="获取生命周期日志详情"
)
async def get_log(
    app_id: str,
    log_id: str,
    service: LifecycleLogService = Depends(get_lifecycle_log_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """获取生命周期日志详情"""
    try:
        return await service.get_log(log_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete(
    "/{log_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除生命周期日志"
)
async def delete_log(
    app_id: str,
    log_id: str,
    service: LifecycleLogService = Depends(get_lifecycle_log_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """删除生命周期日志"""
    # 这里需要实现删除方法
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get(
    "/timeline",
    response_model=TimelineResponseSchema,
    summary="获取时间线数据"
)
async def get_timeline(
    app_id: str,
    start_time: Optional[str] = Query(None, description="开始时间(ISO格式)"),
    end_time: Optional[str] = Query(None, description="结束时间(ISO格式)"),
    log_type: Optional[str] = Query(None, description="日志类型过滤"),
    limit: int = Query(100, ge=1, le=500),
    service: LifecycleLogService = Depends(get_lifecycle_log_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """获取应用的时间线数据"""
    filter_dto = TimelineFilterDTO(
        start_time=start_time,
        end_time=end_time,
        log_type=log_type,
        limit=limit
    )
    return await service.get_timeline(app_id, filter_dto)


@router.get(
    "/timeline/by-plan/{plan_id}",
    response_model=TimelineResponseSchema,
    summary="获取计划关联的时间线"
)
async def get_timeline_by_plan(
    app_id: str,
    plan_id: str,
    service: LifecycleLogService = Depends(get_lifecycle_log_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """获取计划关联的时间线（双向追溯）"""
    return await service.get_timeline_by_plan(plan_id)


@router.get(
    "/timeline/by-module/{module_id}",
    response_model=TimelineResponseSchema,
    summary="获取功能模块的时间线"
)
async def get_timeline_by_module(
    app_id: str,
    module_id: str,
    service: LifecycleLogService = Depends(get_lifecycle_log_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """获取功能模块的时间线"""
    return await service.get_timeline_by_module(module_id)


@router.get(
    "/types/list",
    response_model=List[LogTypeInfoSchema],
    summary="获取日志类型列表"
)
async def get_log_types(
    app_id: str,
    service: LifecycleLogService = Depends(get_lifecycle_log_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """获取所有可用的日志类型列表"""
    return service.get_log_type_list()


@router.get(
    "/statistics/overview",
    response_model=LogStatisticsSchema,
    summary="获取日志统计"
)
async def get_statistics(
    app_id: str,
    service: LifecycleLogService = Depends(get_lifecycle_log_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """获取应用的日志统计信息"""
    return await service.get_statistics(app_id)
