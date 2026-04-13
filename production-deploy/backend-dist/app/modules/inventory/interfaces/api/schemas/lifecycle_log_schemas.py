"""
生命周期日志API Schemas
"""
from datetime import datetime
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field, validator


class LifecycleLogCreateSchema(BaseModel):
    """创建生命周期日志请求Schema"""
    log_type: str = Field(
        ...,
        pattern="^(system_launch|system_upgrade|system_rollback|system_offline|module_launch|module_update|module_offline|config_change|owner_change|status_change|manual)$",
        description="日志类型"
    )
    event_title: str = Field(..., max_length=200, description="事件标题")
    description: Optional[str] = Field(None, description="事件描述")
    before_data: Optional[Dict[str, Any]] = Field(None, description="变更前数据")
    after_data: Optional[Dict[str, Any]] = Field(None, description="变更后数据")
    related_plan_id: Optional[str] = Field(None, description="关联计划ID")
    plan_title: Optional[str] = Field(None, max_length=200, description="计划标题")
    related_module_id: Optional[str] = Field(None, description="关联模块ID")


class LifecycleLogResponseSchema(BaseModel):
    """生命周期日志响应Schema"""
    id: str
    app_id: str
    log_type: str
    log_type_display: str
    event_title: str
    description: Optional[str]
    before_data: Optional[Dict[str, Any]]
    after_data: Optional[Dict[str, Any]]
    related_plan_id: Optional[str]
    plan_title: Optional[str]
    related_module_id: Optional[str]
    operator: Optional[str]
    operation_time: str

    class Config:
        from_attributes = True


class TimelineChangeSchema(BaseModel):
    """时间线变更详情"""
    field: str
    before: Any
    after: Any


class TimelineChangesSchema(BaseModel):
    """时间线变更摘要"""
    fields: List[str]
    changes: List[TimelineChangeSchema]


class TimelineItemSchema(BaseModel):
    """时间线条目Schema"""
    id: str
    type: str
    type_display: str
    title: str
    description: Optional[str]
    time: str
    operator: Optional[str]
    plan_id: Optional[str]
    plan_title: Optional[str]
    module_id: Optional[str]
    changes: Optional[TimelineChangesSchema]
    icon: str
    color: str


class TimelineFilterSchema(BaseModel):
    """时间线筛选Schema"""
    log_type: Optional[str] = Field(None, description="日志类型过滤")
    start_time: Optional[str] = Field(None, description="开始时间(ISO格式)")
    end_time: Optional[str] = Field(None, description="结束时间(ISO格式)")
    limit: int = Field(default=100, ge=1, le=1000, description="返回数量限制")


class TimelineResponseSchema(BaseModel):
    """时间线响应Schema"""
    items: List[TimelineItemSchema]
    total: int


class LogTypeInfoSchema(BaseModel):
    """日志类型信息Schema"""
    value: str
    label: str
    description: str
    icon: str
    color: str


class LogTypeListSchema(BaseModel):
    """日志类型列表Schema"""
    types: List[LogTypeInfoSchema]


class MonthlyTrendSchema(BaseModel):
    """月度趋势数据"""
    month: str
    count: int


class LogStatisticsSchema(BaseModel):
    """日志统计Schema"""
    total_count: int
    type_distribution: Dict[str, int]
    monthly_trend: List[MonthlyTrendSchema]


class LogListResponseSchema(BaseModel):
    """日志列表响应Schema"""
    items: List[LifecycleLogResponseSchema]
    total: int
