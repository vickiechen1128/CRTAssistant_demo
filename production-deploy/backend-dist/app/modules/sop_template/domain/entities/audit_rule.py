"""
审核规则实体
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import uuid4

from ..value_objects.audit_level import AuditLevel
from ..value_objects.audit_method import AuditMethod


@dataclass
class AuditRule:
    """
    审核规则实体
    
    职责：
    1. 定义特定审核等级的规则
    2. 配置主要/辅助审核方式
    3. 设置抽检比例和自动通过阈值
    """
    # 标识
    id: str
    
    # 审核等级
    audit_level: AuditLevel
    
    # 审核方式
    primary_method: AuditMethod
    secondary_method: Optional[AuditMethod] = None
    
    # 抽检比例（0-1，仅普通项适用）
    sampling_ratio: float = 0.3
    
    # 自动通过阈值（脚本置信度，如 95.00）
    auto_pass_threshold: Optional[float] = None
    
    # 强制审核人角色（关键项适用）
    mandatory_reviewer_role: Optional[str] = None
    
    # 升级规则描述
    escalation_rule: Optional[str] = None
    
    # 关联
    config_id: str = ""
    
    # 审计
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """初始化后校验"""
        # 关键项必须全量审核
        if self.audit_level.value == "critical":
            self.sampling_ratio = 1.0
    
    @classmethod
    def create(
        cls,
        audit_level: AuditLevel,
        primary_method: AuditMethod,
        config_id: str,
        secondary_method: Optional[AuditMethod] = None,
        sampling_ratio: float = 0.3,
        auto_pass_threshold: Optional[float] = None,
        mandatory_reviewer_role: Optional[str] = None,
        escalation_rule: Optional[str] = None,
    ) -> "AuditRule":
        """工厂方法：创建审核规则"""
        # 关键项强制全量审核
        if audit_level.value == "critical":
            sampling_ratio = 1.0
        
        return cls(
            id=str(uuid4()),
            audit_level=audit_level,
            primary_method=primary_method,
            secondary_method=secondary_method,
            sampling_ratio=sampling_ratio,
            auto_pass_threshold=auto_pass_threshold,
            mandatory_reviewer_role=mandatory_reviewer_role,
            escalation_rule=escalation_rule,
            config_id=config_id,
        )
    
    @classmethod
    def create_normal_rule(
        cls,
        primary_method: AuditMethod = None,
        config_id: str = "",
        **kwargs
    ) -> "AuditRule":
        """创建普通项规则"""
        return cls.create(
            audit_level=AuditLevel.normal(),
            primary_method=primary_method or AuditMethod.self_review(),
            sampling_ratio=0.3,
            config_id=config_id,
            **kwargs
        )
    
    @classmethod
    def create_critical_rule(
        cls,
        primary_method: AuditMethod = None,
        config_id: str = "",
        mandatory_reviewer_role: str = "ops_manager",
        **kwargs
    ) -> "AuditRule":
        """创建关键项规则"""
        return cls.create(
            audit_level=AuditLevel.critical(),
            primary_method=primary_method or AuditMethod.expert_manual(),
            sampling_ratio=1.0,  # 强制100%
            mandatory_reviewer_role=mandatory_reviewer_role,
            config_id=config_id,
            **kwargs
        )
    
    def update(
        self,
        primary_method: Optional[AuditMethod] = None,
        secondary_method: Optional[AuditMethod] = None,
        sampling_ratio: Optional[float] = None,
        auto_pass_threshold: Optional[float] = None,
        mandatory_reviewer_role: Optional[str] = None,
        escalation_rule: Optional[str] = None,
    ) -> None:
        """更新规则"""
        if primary_method is not None:
            self.primary_method = primary_method
        if secondary_method is not None:
            self.secondary_method = secondary_method
        if sampling_ratio is not None and self.audit_level.value != "critical":
            self.sampling_ratio = max(0.0, min(1.0, sampling_ratio))
        if auto_pass_threshold is not None:
            self.auto_pass_threshold = auto_pass_threshold
        if mandatory_reviewer_role is not None:
            self.mandatory_reviewer_role = mandatory_reviewer_role
        if escalation_rule is not None:
            self.escalation_rule = escalation_rule
        
        self.updated_at = datetime.utcnow()
    
    def should_audit(self, random_value: float) -> bool:
        """
        根据抽检比例判断是否需要进行审核
        
        Args:
            random_value: 0-1 之间的随机数
        
        Returns:
            是否需要审核
        """
        return random_value <= self.sampling_ratio
    
    def check_auto_pass(self, confidence: float) -> bool:
        """
        检查是否满足自动通过条件
        
        Args:
            confidence: 置信度（0-100）
        
        Returns:
            是否自动通过
        """
        if self.auto_pass_threshold is None:
            return False
        return confidence >= self.auto_pass_threshold
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "audit_level": self.audit_level.value,
            "audit_level_display": self.audit_level.display_name,
            "primary_method": self.primary_method.value,
            "primary_method_display": self.primary_method.display_name,
            "secondary_method": self.secondary_method.value if self.secondary_method else None,
            "secondary_method_display": self.secondary_method.display_name if self.secondary_method else None,
            "sampling_ratio": self.sampling_ratio,
            "auto_pass_threshold": self.auto_pass_threshold,
            "mandatory_reviewer_role": self.mandatory_reviewer_role,
            "escalation_rule": self.escalation_rule,
            "config_id": self.config_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
