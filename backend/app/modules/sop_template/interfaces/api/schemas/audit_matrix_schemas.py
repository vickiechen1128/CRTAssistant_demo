"""
审核矩阵 API Schemas
"""
from datetime import datetime
from typing import List, Optional, TypeVar, Generic
from pydantic import BaseModel, Field


T = TypeVar('T')


class ApiResponseSchema(BaseModel, Generic[T]):
    """通用API响应Schema"""
    code: int = 200
    message: str = "success"
    data: Optional[T] = None

    class Config:
        from_attributes = True


class AuditRuleSchema(BaseModel):
    """审核规则 Schema"""
    audit_level: str = Field(..., pattern="^(normal|critical)$")
    primary_method: str = Field(..., pattern="^(self_review|script_auto|expert_manual|ai_assist)$")
    secondary_method: Optional[str] = Field(None, pattern="^(self_review|script_auto|expert_manual|ai_assist)$")
    sampling_ratio: float = Field(0.3, ge=0.0, le=1.0)
    auto_pass_threshold: Optional[float] = Field(None, ge=0.0, le=100.0)
    mandatory_reviewer_role: Optional[str] = None
    escalation_rule: Optional[str] = None
    
    class Config:
        from_attributes = True


class CreateAuditMatrixSchema(BaseModel):
    """创建审核矩阵 Schema"""
    config_id: Optional[str] = None
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    rules: Optional[List[AuditRuleSchema]] = Field(default_factory=list)


class UpdateAuditMatrixSchema(BaseModel):
    """更新审核矩阵 Schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None


class AuditRuleResponseSchema(BaseModel):
    """审核规则响应 Schema"""
    id: str
    audit_level: str
    audit_level_display: str
    primary_method: str
    primary_method_display: str
    secondary_method: Optional[str]
    secondary_method_display: Optional[str]
    sampling_ratio: float
    auto_pass_threshold: Optional[float]
    mandatory_reviewer_role: Optional[str]
    escalation_rule: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AuditMatrixResponseSchema(BaseModel):
    """审核矩阵响应 Schema"""
    id: str
    config_id: str
    name: str
    description: Optional[str]
    status: str
    rules_count: int
    rules: List[AuditRuleResponseSchema]
    created_by: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AuditMatrixListItemSchema(BaseModel):
    """审核矩阵列表项 Schema"""
    id: str
    config_id: str
    name: str
    status: str
    rules_count: int
    created_by: str
    created_at: datetime


class AuditMatrixListResponseSchema(BaseModel):
    """审核矩阵列表响应 Schema"""
    items: List[AuditMatrixListItemSchema]
    total: int
    page: int
    page_size: int
    total_pages: int


class UpdateAuditRuleSchema(BaseModel):
    """更新审核规则 Schema"""
    primary_method: str = Field(..., pattern="^(self_review|script_auto|expert_manual|ai_assist)$")
    secondary_method: Optional[str] = Field(None, pattern="^(self_review|script_auto|expert_manual|ai_assist)$")
    sampling_ratio: float = Field(0.3, ge=0.0, le=1.0)
    auto_pass_threshold: Optional[float] = Field(None, ge=0.0, le=100.0)
    mandatory_reviewer_role: Optional[str] = None
    escalation_rule: Optional[str] = None
