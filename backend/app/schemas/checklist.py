"""
检查清单Schema
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from ..models.checklist import ControlDimension, ChecklistItemStatus


class ChecklistItemBase(BaseModel):
    """检查项基础Schema"""
    control_dimension: ControlDimension
    category: str = Field(..., min_length=1, max_length=50)
    item_name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    acceptance_criteria: Optional[str] = None


class ChecklistItemUpdate(BaseModel):
    """更新检查项请求Schema"""
    assignee_id: Optional[int] = None
    due_date: Optional[date] = None
    remark: Optional[str] = None


class ChecklistItemVerify(BaseModel):
    """确认检查项请求Schema"""
    status: ChecklistItemStatus  # passed/rejected
    remark: Optional[str] = None


class UserBrief(BaseModel):
    """用户信息简版"""
    id: int
    real_name: str
    
    class Config:
        from_attributes = True


class ChecklistItemResponse(ChecklistItemBase):
    """检查项响应Schema"""
    id: int
    task_id: int
    status: ChecklistItemStatus
    assignee: Optional[UserBrief] = None
    verifier: Optional[UserBrief] = None
    verified_at: Optional[datetime] = None
    verification_remark: Optional[str] = None
    due_date: Optional[date] = None
    deliverables_count: int = 0
    verification_method: str
    sort_order: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ChecklistItemList(BaseModel):
    """检查项列表响应"""
    items: List[ChecklistItemResponse]
    total: int
