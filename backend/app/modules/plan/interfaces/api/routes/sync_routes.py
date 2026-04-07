"""
数据同步API路由
提供数据同步相关的查询和管理接口
"""
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db

from ....infrastructure.services.data_sync_service import DataSyncService, SyncStatus
from ..schemas.sync_schemas import (
    SyncLogResponseSchema,
    SyncStatisticsSchema,
    ConsistencyCheckResponseSchema,
    ApiResponseSchema,
)

router = APIRouter(prefix="/sync", tags=["数据同步"])


def get_sync_service(db: Session = Depends(get_db)) -> DataSyncService:
    """依赖注入：获取DataSyncService实例"""
    return DataSyncService(db)


@router.get("/logs", response_model=ApiResponseSchema[List[SyncLogResponseSchema]])
def get_sync_logs(
    sync_type: Optional[str] = Query(None, description="同步类型: plan_to_inventory / inventory_to_plan / repair"),
    source_id: Optional[str] = Query(None, description="源ID"),
    status: Optional[str] = Query(None, description="状态: pending / success / failed / partial"),
    limit: int = Query(100, ge=1, le=1000, description="返回条数"),
    sync_service: DataSyncService = Depends(get_sync_service)
):
    """获取数据同步日志"""
    try:
        status_enum = None
        if status:
            try:
                status_enum = SyncStatus(status)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid status: {status}")

        logs = sync_service.get_sync_logs(
            sync_type=sync_type,
            source_id=source_id,
            status=status_enum,
            limit=limit
        )

        result = [
            {
                "id": log.id,
                "sync_type": log.sync_type,
                "source_id": log.source_id,
                "target_id": log.target_id,
                "operation": log.operation,
                "status": log.status.value,
                "details": log.details,
                "error_message": log.error_message,
                "created_at": log.created_at.isoformat()
            }
            for log in logs
        ]

        return ApiResponseSchema(data=result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics", response_model=ApiResponseSchema[SyncStatisticsSchema])
def get_sync_statistics(
    sync_service: DataSyncService = Depends(get_sync_service)
):
    """获取数据同步统计信息"""
    try:
        stats = sync_service.get_sync_statistics()
        return ApiResponseSchema(data=stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/consistency-check", response_model=ApiResponseSchema[ConsistencyCheckResponseSchema])
def check_consistency(
    plan_id: Optional[str] = Query(None, description="计划ID（可选，不传则检查所有）"),
    sync_service: DataSyncService = Depends(get_sync_service)
):
    """检查计划与台账的数据一致性"""
    try:
        result = sync_service.check_consistency(plan_id)
        return ApiResponseSchema(data=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/repair/{plan_id}", response_model=ApiResponseSchema[SyncLogResponseSchema])
def repair_consistency(
    plan_id: str,
    sync_service: DataSyncService = Depends(get_sync_service)
):
    """修复指定计划的数据不一致"""
    try:
        result = sync_service.repair_inconsistency(plan_id)

        return ApiResponseSchema(
            data={
                "id": result.id,
                "sync_type": result.sync_type,
                "source_id": result.source_id,
                "target_id": result.target_id,
                "operation": result.operation,
                "status": result.status.value,
                "details": result.details,
                "error_message": result.error_message,
                "created_at": result.created_at.isoformat()
            },
            message="修复完成" if result.status == SyncStatus.SUCCESS else "修复部分完成" if result.status == SyncStatus.PARTIAL else "修复失败"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
