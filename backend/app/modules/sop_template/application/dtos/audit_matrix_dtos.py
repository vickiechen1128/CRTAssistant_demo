"""
审核矩阵相关 DTOs
"""
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class AuditRuleRequest:
    """审核规则请求"""
    audit_level: str
    primary_method: str
    secondary_method: Optional[str] = None
    sampling_ratio: float = 0.3
    auto_pass_threshold: Optional[float] = None
    mandatory_reviewer_role: Optional[str] = None
    escalation_rule: Optional[str] = None


@dataclass
class CreateAuditMatrixRequest:
    """创建审核矩阵请求"""
    config_id: Optional[str]  # 可选，不传则自动生成
    name: str
    description: Optional[str] = None
    rules: List[AuditRuleRequest] = None


@dataclass
class UpdateAuditMatrixRequest:
    """更新审核矩阵请求"""
    name: Optional[str] = None
    description: Optional[str] = None


@dataclass
class AuditRuleResponse:
    """审核规则响应"""
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


@dataclass
class AuditMatrixResponse:
    """审核矩阵响应"""
    id: str
    config_id: str
    name: str
    description: Optional[str]
    status: str
    rules_count: int
    rules: List[AuditRuleResponse]
    created_by: str
    created_at: datetime
    updated_at: datetime


@dataclass
class AuditMatrixListResponse:
    """审核矩阵列表响应"""
    items: List[AuditMatrixResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


@dataclass
class AuditMatrixFilterRequest:
    """审核矩阵筛选请求"""
    status: Optional[str] = None
    keyword: Optional[str] = None
    page: int = 1
    page_size: int = 20
