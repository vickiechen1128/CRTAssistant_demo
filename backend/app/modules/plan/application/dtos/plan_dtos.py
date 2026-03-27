"""
计划模块数据传输对象 (DTOs)
用于应用层与接口层之间的数据交换
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, validator


class CreatePlanRequest(BaseModel):
    """创建计划请求"""
    name: str = Field(..., min_length=1, max_length=200, description="计划名称")
    category: str = Field(..., description="计划分类")
    priority: str = Field(..., description="优先级 (P0-P3)")
    description: Optional[str] = Field(None, max_length=2000, description="计划描述")
    planned_start_time: Optional[datetime] = Field(None, description="计划开始时间")
    planned_end_time: Optional[datetime] = Field(None, description="计划结束时间")
    workflow_template_id: Optional[str] = Field(None, description="工作流模板ID")
    
    @validator('category')
    def validate_category(cls, v):
        valid_categories = {'new_system', 'new_feature', 'func_change', 'arch_change', 'security_check'}
        if v not in valid_categories:
            raise ValueError(f'Invalid category. Must be one of: {valid_categories}')
        return v
    
    @validator('priority')
    def validate_priority(cls, v):
        if v not in {'P0', 'P1', 'P2', 'P3'}:
            raise ValueError('Priority must be P0, P1, P2, or P3')
        return v
    
    @validator('planned_end_time')
    def validate_end_time(cls, v, values):
        if v and values.get('planned_start_time') and v <= values['planned_start_time']:
            raise ValueError('planned_end_time must be after planned_start_time')
        return v


class UpdatePlanRequest(BaseModel):
    """更新计划请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    planned_start_time: Optional[datetime] = None
    planned_end_time: Optional[datetime] = None
    priority: Optional[str] = None
    
    @validator('priority')
    def validate_priority(cls, v):
        if v and v not in {'P0', 'P1', 'P2', 'P3'}:
            raise ValueError('Priority must be P0, P1, P2, or P3')
        return v


class PlanResponse(BaseModel):
    """计划响应"""
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


class PlanListResponse(BaseModel):
    """计划列表响应"""
    items: List[PlanResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class PlanFilterRequest(BaseModel):
    """计划筛选请求"""
    status: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[str] = None
    created_by: Optional[str] = None
    keyword: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)


class LinkInventoryRequest(BaseModel):
    """关联台账请求"""
    inventory_ids: List[str] = Field(..., min_items=1, description="台账ID列表")


class StartPlanRequest(BaseModel):
    """启动计划请求"""
    confirmed: bool = Field(False, description="P0计划是否已确认")
    confirmation_note: Optional[str] = Field(None, description="确认备注")


class CompletePlanRequest(BaseModel):
    """完成计划请求"""
    completion_note: Optional[str] = Field(None, description="完成备注")


class CancelPlanRequest(BaseModel):
    """取消计划请求"""
    reason: str = Field(..., min_length=1, max_length=500, description="取消原因")
