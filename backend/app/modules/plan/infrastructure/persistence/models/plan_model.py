"""
计划数据库模型
SQLAlchemy ORM 映射
"""
from datetime import datetime
from typing import List, Optional, Dict, Any

from sqlalchemy import Column, String, DateTime, Text, Integer, ForeignKey, Table, Index
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.sqlite import JSON

from app.core.database import Base


class PlanModel(Base):
    """计划数据库模型"""
    __tablename__ = 'plans'
    
    # 主键 - 格式: PLAN-YYYYMMDD-XXX
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    
    # 数据标签 - 格式: {PLAN-ID}-{分类简码}-{Unix时间戳}
    data_tag: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    
    # 基本信息
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # 时间信息
    planned_start_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    planned_end_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    actual_start_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    actual_end_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # 状态
    status: Mapped[str] = mapped_column(String(50), nullable=False, default='DRAFT', index=True)
    
    # 关联信息
    workflow_template_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    inventory_action: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # 关联的台账ID列表
    related_inventory_ids: Mapped[List[str]] = mapped_column(JSON, default=list)
    
    # 受影响功能模块列表（JSON格式）
    # 格式: [{"module_id": "...", "module_name": "...", "action": "create/update/delete", ...}]
    affected_modules: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
    
    # 工作流模板类型
    template_type: Mapped[str] = mapped_column(String(50), nullable=False, default='new_feature')
    
    # 审批材料详细信息（JSON格式）
    # 格式: [{"file_name": "...", "file_url": "...", "file_size": 123, "uploaded_at": "..."}]
    approval_files_detail: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
    
    # 兼容性：审批材料文件ID列表
    approval_files: Mapped[List[str]] = mapped_column(JSON, default=list)
    
    # 审计信息
    created_by: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    # 关联关系 - 计划与台账的关联
    inventory_links = relationship(
        'PlanInventoryLinkModel',
        back_populates='plan',
        cascade='all, delete-orphan',
        lazy='selectin'
    )
    
    # 关联关系 - 生命周期日志（通过外键关联）
    lifecycle_logs = relationship(
        'LifecycleLogModel',
        back_populates='related_plan',
        lazy='dynamic'
    )
    
    # 索引优化
    __table_args__ = (
        Index('idx_plan_category_status', 'category', 'status'),
        Index('idx_plan_priority_status', 'priority', 'status'),
        Index('idx_plan_created_by', 'created_by'),
        Index('idx_plan_planned_start', 'planned_start_time'),
        Index('idx_plan_template_type', 'template_type'),
    )
    
    def __repr__(self) -> str:
        return f"<PlanModel(id={self.id}, name={self.name}, status={self.status})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "data_tag": self.data_tag,
            "name": self.name,
            "category": self.category,
            "priority": self.priority,
            "status": self.status,
            "description": self.description,
            "planned_start_time": self.planned_start_time.isoformat() if self.planned_start_time else None,
            "planned_end_time": self.planned_end_time.isoformat() if self.planned_end_time else None,
            "actual_start_time": self.actual_start_time.isoformat() if self.actual_start_time else None,
            "actual_end_time": self.actual_end_time.isoformat() if self.actual_end_time else None,
            "template_type": self.template_type,
            "related_inventory_ids": self.related_inventory_ids,
            "affected_modules": self.affected_modules,
            "approval_files": self.approval_files_detail,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class PlanInventoryLinkModel(Base):
    """计划与台账关联模型（冗余存储用于快速查询）"""
    __tablename__ = 'plan_inventory_links'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    plan_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey('plans.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    inventory_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    inventory_type: Mapped[str] = mapped_column(String(50), nullable=False, default='application')
    linked_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # 关联关系
    plan = relationship('PlanModel', back_populates='inventory_links')
    
    __table_args__ = (
        Index('idx_plan_inventory', 'plan_id', 'inventory_id', unique=True),
    )
