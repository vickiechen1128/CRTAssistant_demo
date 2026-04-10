"""
SOP 模板数据库模型
"""
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, String, DateTime, Text, Integer, ForeignKey, Index
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.sqlite import JSON

from app.core.database import Base


class SOPTemplateModel(Base):
    """SOP 模板数据库模型"""
    __tablename__ = 'sop_templates'
    
    # 主键
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    template_id: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    
    # 基本信息
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    template_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # 版本和状态
    version: Mapped[str] = mapped_column(String(20), nullable=False, default='v1.0')
    status: Mapped[str] = mapped_column(String(20), nullable=False, default='draft', index=True)
    
    # 关联配置
    audit_matrix_config_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    parent_work_items_config: Mapped[List[dict]] = mapped_column(JSON, default=list)
    
    # 审计信息
    created_by: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    deprecated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # 关联关系
    workflow_nodes: Mapped[List["WorkflowNodeModel"]] = relationship(
        "WorkflowNodeModel",
        back_populates="sop_template",
        cascade="all, delete-orphan",
        order_by="WorkflowNodeModel.sequence"
    )
    
    def __repr__(self) -> str:
        return f"<SOPTemplateModel(id={self.id}, template_id={self.template_id}, status={self.status})>"


class WorkflowNodeModel(Base):
    """流程节点数据库模型"""
    __tablename__ = 'workflow_nodes'
    
    # 主键
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    node_id: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # 基本信息
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    sequence: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    
    # 条件配置
    entry_conditions: Mapped[List[dict]] = mapped_column(JSON, default=list)
    exit_conditions: Mapped[List[dict]] = mapped_column(JSON, default=list)
    
    # 强制规则
    mandatory_rules: Mapped[dict] = mapped_column(JSON, default=dict)
    
    # 外键
    sop_template_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey('sop_templates.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    # 审计信息
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    
    # 关联关系
    sop_template: Mapped["SOPTemplateModel"] = relationship(
        "SOPTemplateModel", back_populates="workflow_nodes"
    )
    work_items: Mapped[List["WorkItemTemplateModel"]] = relationship(
        "WorkItemTemplateModel",
        back_populates="workflow_node",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<WorkflowNodeModel(id={self.id}, name={self.name}, sequence={self.sequence})>"


class WorkItemTemplateModel(Base):
    """工作项模板数据库模型"""
    __tablename__ = 'work_item_templates'
    
    # 主键
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    template_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    
    # 基本信息
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    sequence: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # 审核配置
    audit_level: Mapped[str] = mapped_column(String(20), nullable=False, default='normal')
    
    # JSON 配置
    deliverables_config: Mapped[List[dict]] = mapped_column(JSON, default=list)
    acceptance_criteria_config: Mapped[List[dict]] = mapped_column(JSON, default=list)
    execution_steps_config: Mapped[List[dict]] = mapped_column(JSON, default=list)
    
    # 外键（层级结构）
    sop_template_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey('sop_templates.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    workflow_node_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey('workflow_nodes.id', ondelete='CASCADE'),
        nullable=True,
        index=True
    )
    parent_template_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey('work_item_templates.id', ondelete='CASCADE'),
        nullable=True,
        index=True
    )
    
    # 状态
    status: Mapped[str] = mapped_column(String(20), nullable=False, default='active')
    
    # 审计信息
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    
    # 关联关系
    workflow_node: Mapped[Optional["WorkflowNodeModel"]] = relationship(
        "WorkflowNodeModel", back_populates="work_items"
    )
    parent: Mapped[Optional["WorkItemTemplateModel"]] = relationship(
        "WorkItemTemplateModel",
        remote_side="WorkItemTemplateModel.id",
        back_populates="children"
    )
    children: Mapped[List["WorkItemTemplateModel"]] = relationship(
        "WorkItemTemplateModel",
        back_populates="parent",
        cascade="all, delete-orphan",
        order_by="WorkItemTemplateModel.sequence"
    )
    
    def __repr__(self) -> str:
        return f"<WorkItemTemplateModel(id={self.id}, template_id={self.template_id}, name={self.name})>"


# 索引
Index('idx_sop_template_type_status', SOPTemplateModel.template_type, SOPTemplateModel.status)
Index('idx_workflow_node_template', WorkflowNodeModel.sop_template_id, WorkflowNodeModel.sequence)
Index('idx_work_item_template_parent', WorkItemTemplateModel.parent_template_id)
