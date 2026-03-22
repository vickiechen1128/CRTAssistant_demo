"""
验证Schema
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from ..models.verification import ScriptType, ExecutionStatus


# ========== 验证脚本 ==========

class VerificationScriptBase(BaseModel):
    """验证脚本基础Schema"""
    script_name: str = Field(..., min_length=1, max_length=100)
    script_type: ScriptType
    description: Optional[str] = None
    content: str
    version: str = "1.0"
    applicable_os: Optional[str] = Field(None, max_length=200)
    parameters: Optional[List[Dict[str, Any]]] = None
    timeout_seconds: int = Field(default=300, ge=10, le=3600)


class VerificationScriptCreate(VerificationScriptBase):
    """创建验证脚本请求Schema"""
    pass


class VerificationScriptResponse(VerificationScriptBase):
    """验证脚本响应Schema"""
    id: int
    created_by: int
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ========== 验证执行 ==========

class VerificationExecuteRequest(BaseModel):
    """执行验证请求Schema"""
    checklist_item_id: int
    script_id: int
    target_server: str = Field(..., pattern=r"^(\d{1,3}\.){3}\d{1,3}$")
    parameters: Optional[Dict[str, Any]] = None


class ResultDetailItem(BaseModel):
    """验证结果详情项"""
    check_item: str
    expected: Optional[str] = None
    actual: Optional[str] = None
    status: str  # passed/failed/warning
    suggestion: Optional[str] = None


class ResultSummary(BaseModel):
    """验证结果汇总"""
    total: int
    passed: int
    failed: int
    warning: int


class UserBrief(BaseModel):
    """用户信息简版"""
    id: int
    real_name: str
    
    class Config:
        from_attributes = True


class VerificationRecordResponse(BaseModel):
    """验证记录响应Schema"""
    id: int
    execution_id: str
    task_id: int
    checklist_item_id: int
    script_id: int
    target_server: str
    executor: Optional[UserBrief] = None
    status: ExecutionStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    result_summary: Optional[ResultSummary] = None
    result_detail: Optional[List[ResultDetailItem]] = None
    output_log: Optional[str] = None
    error_log: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class VerificationExecuteResponse(BaseModel):
    """执行验证响应Schema"""
    execution_id: str
    status: str  # running
    message: str = "脚本正在执行中，请稍后查询结果"
