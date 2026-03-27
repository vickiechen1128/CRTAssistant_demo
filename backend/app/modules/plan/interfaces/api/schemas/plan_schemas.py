"""
API 请求/响应 Schema
用于 FastAPI 路由层
"""
from datetime import datetime
from typing import List, Optional, Any, Generic, TypeVar
from pydantic import BaseModel, Field, validator


T = TypeVar('T')


class ApiResponseSchema(BaseModel, Generic[T]):
    """统一API响应格式"""
    success: bool = True
    message: str = "Success"
    data: Optional[T] = None
    error: Optional[str] = None


class CreatePlanSchema(BaseModel):
    """创建计划请求Schema"""
    name: str = Field(..., min_length=1, max_length=200, description="计划名称")
    category: str = Field(..., description="计划分类: new_system/new_feature/func_change/arch_change/security_check")
    priority: str = Field(..., description="优先级: P0/P1/P2/P3")
    description: Optional[str] = Field(None, max_length=2000, description="计划描述")
    planned_start_time: Optional[datetime] = Field(None, description="计划开始时间")
    planned_end_time: Optional[datetime] = Field(None, description="计划结束时间")
    workflow_template_id: Optional[str] = Field(None, description="工作流模板ID")
    
    @validator('category')
    def validate_category(cls, v):
        valid = {'new_system', 'new_feature', 'func_change', 'arch_change', 'security_check'}
        if v not in valid:
            raise ValueError(f'分类必须是以下之一: {valid}')
        return v
    
    @validator('priority')
    def validate_priority(cls, v):
        if v not in {'P0', 'P1', 'P2', 'P3'}:
            raise ValueError('优先级必须是 P0, P1, P2, 或 P3')
        return v


class UpdatePlanSchema(BaseModel):
    """更新计划请求Schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    planned_start_time: Optional[datetime] = None
    planned_end_time: Optional[datetime] = None
    priority: Optional[str] = None
    
    @validator('priority')
    def validate_priority(cls, v):
        if v and v not in {'P0', 'P1', 'P2', 'P3'}:
            raise ValueError('优先级必须是 P0, P1, P2, 或 P3')
        return v


class PlanResponseSchema(BaseModel):
    """计划响应Schema"""
    id: str
    data_tag: str
    name: str
    category: str
    priority: str
    status: str
    description: Optional[str] = None
    planned_start_time: Optional[datetime] = None
    planned_end_time: Optional[datetime] = None
    actual_start_time: Optional[datetime] = None
    actual_end_time: Optional[datetime] = None
    workflow_template_id: Optional[str] = None
    inventory_ids: List[str] = []
    inventory_action: Optional[str] = None
    approval_files: List[str] = []
    created_by: str
    created_at: datetime
    updated_at: datetime
    is_overdue: bool = False
    
    class Config:
        from_attributes = True


class PlanListResponseSchema(BaseModel):
    """计划列表响应Schema"""
    items: List[PlanResponseSchema]
    total: int
    page: int
    page_size: int
    total_pages: int


class PlanFilterSchema(BaseModel):
    """计划筛选Schema"""
    status: Optional[str] = Field(None, description="状态: DRAFT/PENDING/IN_PROGRESS/COMPLETED/CANCELLED")
    category: Optional[str] = Field(None, description="分类")
    priority: Optional[str] = Field(None, description="优先级")
    keyword: Optional[str] = Field(None, description="关键词搜索")
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")


class LinkInventorySchema(BaseModel):
    """关联台账请求Schema"""
    inventory_ids: List[str] = Field(..., min_items=1, description="台账ID列表")


class StartPlanSchema(BaseModel):
    """启动计划请求Schema"""
    confirmed: bool = Field(False, description="P0计划是否已确认")
    confirmation_note: Optional[str] = Field(None, description="确认备注")


class CompletePlanSchema(BaseModel):
    """完成计划请求Schema"""
    completion_note: Optional[str] = Field(None, description="完成备注")


class CancelPlanSchema(BaseModel):
    """取消计划请求Schema"""
    reason: str = Field(..., min_length=1, max_length=500, description="取消原因")
