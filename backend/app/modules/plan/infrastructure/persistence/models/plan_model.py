"""
计划数据库模型
SQLAlchemy ORM 映射
"""
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, String, DateTime, Text, Integer, ForeignKey, Table
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.sqlite import JSON

from app.core.database import Base


# 计划与台账关联表
plan_inventory_association = Table(
    'plan_inventory',
    Base.metadata,
    Column('plan_id', String, ForeignKey('plans.id', ondelete='CASCADE')),
    Column('inventory_id', String, nullable=False)
)


class PlanModel(Base):
    """计划数据库模型"""
    __tablename__ = 'plans'
    
    # 主键
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    data_tag: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    
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
    
    # 审批材料（JSON数组存储文件ID）
    approval_files: Mapped[List[str]] = mapped_column(JSON, default=list)
    
    # 审计信息
    created_by: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    # 关联关系
    inventory_links = relationship(
        'PlanInventoryLinkModel',
        back_populates='plan',
        cascade='all, delete-orphan'
    )
    
    def __repr__(self) -> str:
        return f"<PlanModel(id={self.id}, name={self.name}, status={self.status})>"


class PlanInventoryLinkModel(Base):
    """计划与台账关联模型"""
    __tablename__ = 'plan_inventory_links'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    plan_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey('plans.id', ondelete='CASCADE'),
        nullable=False
    )
    inventory_id: Mapped[str] = mapped_column(String(100), nullable=False)
    linked_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # 关联关系
    plan = relationship('PlanModel', back_populates='inventory_links')
