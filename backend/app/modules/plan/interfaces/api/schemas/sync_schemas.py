"""
数据同步模块API Schema定义
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class SyncLogResponseSchema(BaseModel):
    """同步日志响应Schema"""
    id: str = Field(..., description="同步日志ID")
    sync_type: str = Field(..., description="同步类型: plan_to_inventory / inventory_to_plan / repair")
    source_id: str = Field(..., description="源ID")
    target_id: str = Field(..., description="目标ID")
    operation: str = Field(..., description="操作类型")
    status: str = Field(..., description="状态: pending / success / failed / partial")
    details: Optional[Dict[str, Any]] = Field(None, description="详细信息")
    error_message: Optional[str] = Field(None, description="错误信息")
    created_at: str = Field(..., description="创建时间")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "sync-20240101120000-plan-123",
                "sync_type": "plan_to_inventory",
                "source_id": "PLAN-20240101-001",
                "target_id": "APP-12345678",
                "operation": "plan_completed",
                "status": "success",
                "details": {"module_count": 3},
                "error_message": None,
                "created_at": "2024-01-01T12:00:00"
            }
        }


class SyncStatisticsSchema(BaseModel):
    """同步统计响应Schema"""
    total: int = Field(..., description="总同步次数")
    success: int = Field(..., description="成功次数")
    failed: int = Field(..., description="失败次数")
    partial: int = Field(..., description="部分成功次数")
    success_rate: float = Field(..., description="成功率(%)")
    type_distribution: Dict[str, int] = Field(..., description="类型分布")
    last_sync: Optional[str] = Field(None, description="最后一次同步时间")

    class Config:
        json_schema_extra = {
            "example": {
                "total": 100,
                "success": 95,
                "failed": 3,
                "partial": 2,
                "success_rate": 95.0,
                "type_distribution": {
                    "plan_to_inventory": 80,
                    "inventory_to_plan": 15,
                    "repair": 5
                },
                "last_sync": "2024-01-01T12:00:00"
            }
        }


class InconsistencyItemSchema(BaseModel):
    """不一致项Schema"""
    type: str = Field(..., description="不一致类型")
    plan_id: str = Field(..., description="计划ID")
    inventory_id: Optional[str] = Field(None, description="台账ID")
    plan_status: Optional[str] = Field(None, description="计划状态")
    inventory_status: Optional[str] = Field(None, description="台账状态")
    description: str = Field(..., description="描述")


class ConsistencyCheckResponseSchema(BaseModel):
    """一致性检查响应Schema"""
    checked_at: str = Field(..., description="检查时间")
    plan_id: Optional[str] = Field(None, description="检查的计划ID")
    total_checked: int = Field(..., description="检查总数")
    inconsistent_count: int = Field(..., description="不一致数量")
    inconsistencies: List[InconsistencyItemSchema] = Field(default_factory=list, description="不一致项列表")
    error: Optional[str] = Field(None, description="错误信息")

    class Config:
        json_schema_extra = {
            "example": {
                "checked_at": "2024-01-01T12:00:00",
                "plan_id": "PLAN-20240101-001",
                "total_checked": 10,
                "inconsistent_count": 1,
                "inconsistencies": [
                    {
                        "type": "status_mismatch",
                        "plan_id": "PLAN-20240101-001",
                        "inventory_id": "APP-12345678",
                        "plan_status": "COMPLETED",
                        "inventory_status": "inactive",
                        "description": "计划已完成但台账状态为停用"
                    }
                ],
                "error": None
            }
        }


from typing import TypeVar, Generic

T = TypeVar('T')

class ApiResponseSchema(BaseModel, Generic[T]):
    """通用API响应Schema"""
    code: int = Field(default=200, description="状态码")
    message: str = Field(default="success", description="消息")
    data: Optional[T] = Field(None, description="数据")

    class Config:
        json_schema_extra = {
            "example": {
                "code": 200,
                "message": "success",
                "data": {}
            }
        }
