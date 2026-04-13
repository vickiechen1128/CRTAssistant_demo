"""
审核矩阵配置实体
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from ..value_objects.audit_level import AuditLevel


@dataclass
class AuditMatrixConfig:
    """
    审核矩阵配置实体
    
    职责：
    1. 定义审核矩阵的基本信息
    2. 管理审核规则列表
    3. 提供根据等级获取规则的方法
    """
    # 标识
    id: str
    config_id: str  # 业务唯一标识
    
    # 基本信息
    name: str
    description: Optional[str] = None
    
    # 状态
    status: str = "active"  # active, inactive
    
    # 关联
    created_by: str = ""
    
    # 子实体
    rules: List["AuditRule"] = field(default_factory=list, repr=False)
    
    # 审计
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    @classmethod
    def create(
        cls,
        config_id: str,
        name: str,
        created_by: str,
        description: Optional[str] = None,
    ) -> "AuditMatrixConfig":
        """工厂方法：创建审核矩阵配置"""
        return cls(
            id=str(uuid4()),
            config_id=config_id,
            name=name,
            description=description,
            created_by=created_by,
        )
    
    def update(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> None:
        """更新配置信息"""
        if name is not None:
            self.name = name
        if description is not None:
            self.description = description
        self.updated_at = datetime.utcnow()
    
    def add_rule(self, rule: "AuditRule") -> None:
        """添加审核规则"""
        rule.config_id = self.id
        self.rules.append(rule)
        self.updated_at = datetime.utcnow()
    
    def remove_rule(self, rule_id: str) -> bool:
        """移除审核规则"""
        for i, rule in enumerate(self.rules):
            if rule.id == rule_id:
                del self.rules[i]
                self.updated_at = datetime.utcnow()
                return True
        return False
    
    def get_rule_by_level(self, level: AuditLevel) -> Optional["AuditRule"]:
        """根据审核等级获取规则"""
        for rule in self.rules:
            if rule.audit_level == level:
                return rule
        return None
    
    def deactivate(self) -> None:
        """停用配置"""
        self.status = "inactive"
        self.updated_at = datetime.utcnow()
    
    def activate(self) -> None:
        """激活配置"""
        self.status = "active"
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "config_id": self.config_id,
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "rules_count": len(self.rules),
            "rules": [rule.to_dict() for rule in self.rules],
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
