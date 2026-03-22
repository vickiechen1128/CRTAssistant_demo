"""
准入任务Schema
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from ..models.admission_task import TaskStatus


class AdmissionTaskBase(BaseModel):
    """准入任务基础Schema"""
    system_name: str = Field(..., min_length=1, max_length=100)
    system_code: Optional[str] = Field(None, max_length=50)
    version: str = Field(..., min_length=1, max_length=50)
    release_date: date
    manager_id: int
    template_id: Optional[int] = None
    remark: Optional[str] = None


class AdmissionTaskCreate(AdmissionTaskBase):
    """创建准入任务请求Schema"""
    pass


class AdmissionTaskUpdate(BaseModel):
    """更新准入任务请求Schema"""
    system_name: Optional[str] = Field(None, min_length=1, max_length=100)
    system_code: Optional[str] = Field(None, max_length=50)
    version: Optional[str] = Field(None, min_length=1, max_length=50)
    release_date: Optional[date] = None
    manager_id: Optional[int] = None
    status: Optional[TaskStatus] = None
    remark: Optional[str] = None


class UserBrief(BaseModel):
    """用户信息简版"""
    id: int
    real_name: str
    
    class Config:
        from_attributes = True


class ChecklistSummary(BaseModel):
    """检查清单汇总"""
    total: int
    pending: int
    in_progress: int
    passed: int
    rejected: int


class ControlDimensionProgress(BaseModel):
    """管控维度进度"""
    total: int
    completed: int


class AdmissionTaskResponse(AdmissionTaskBase):
    """准入任务响应Schema"""
    id: int
    task_no: str
    status: TaskStatus
    progress: int
    creator: UserBrief
    manager: UserBrief
    checklist_summary: Optional[ChecklistSummary] = None
    control_dimension_progress: Optional[dict] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class AdmissionTaskList(BaseModel):
    """准入任务列表响应"""
    items: List[AdmissionTaskResponse]
    total: int
    page: int
    per_page: int
