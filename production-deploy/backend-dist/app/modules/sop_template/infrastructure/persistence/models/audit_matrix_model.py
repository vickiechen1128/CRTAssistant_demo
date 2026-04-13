"""
审核矩阵数据库模型
"""
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Numeric, Index
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.core.database import Base


class AuditMatrixConfigModel(Base):
    """审核矩阵配置数据库模型"""
    __tablename__ = 'audit_matrix_configs'
    
    # 主键
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    config_id: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    
    # 基本信息
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # 状态
    status: Mapped[str] = mapped_column(String(20), nullable=False, default='active', index=True)
    
    # 审计信息
    created_by: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    
    # 关联关系
    rules: Mapped[List["AuditRuleModel"]] = relationship(
        "AuditRuleModel",
        back_populates="config",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<AuditMatrixConfigModel(id={self.id}, config_id={self.config_id}, name={self.name})>"


class AuditRuleModel(Base):
    """审核规则数据库模型"""
    __tablename__ = 'audit_rules'
    
    # 主键
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    
    # 审核等级
    audit_level: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    
    # 审核方式
    primary_method: Mapped[str] = mapped_column(String(30), nullable=False)
    secondary_method: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    
    # 抽检比例（0-1）
    sampling_ratio: Mapped[float] = mapped_column(Numeric(3, 2), nullable=False, default=0.30)
    
    # 自动通过阈值
    auto_pass_threshold: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), nullable=True)
    
    # 强制审核人角色
    mandatory_reviewer_role: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # 升级规则
    escalation_rule: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # 外键
    config_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey('audit_matrix_configs.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    # 审计信息
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    
    # 关联关系
    config: Mapped["AuditMatrixConfigModel"] = relationship(
        "AuditMatrixConfigModel", back_populates="rules"
    )
    
    def __repr__(self) -> str:
        return f"<AuditRuleModel(id={self.id}, audit_level={self.audit_level})>"


# 索引
Index('idx_audit_rule_config_level', AuditRuleModel.config_id, AuditRuleModel.audit_level)
