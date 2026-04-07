"""
功能模块数据库模型
"""
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, DateTime, ForeignKey, Text, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from .inventory_model import ApplicationModel


class FunctionModuleModel(Base):
    """功能模块数据模型"""
    __tablename__ = 'inventory_function_modules'
    
    # 主键
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    
    # 关联应用ID
    app_id: Mapped[str] = mapped_column(
        String(36), 
        ForeignKey('inventory_applications.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    # 模块编码
    module_code: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # 模块名称
    module_name: Mapped[str] = mapped_column(String(100), nullable=False)

    # 模块负责人
    owner: Mapped[str] = mapped_column(String(50), nullable=False, default='')

    # 模块描述
    module_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # 版本号
    version: Mapped[str] = mapped_column(String(20), nullable=False, default='1.0.0')
    
    # 状态 (draft/developing/testing/online/offline)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default='draft')
    
    # 父模块ID（支持层级结构）
    parent_module_id: Mapped[Optional[str]] = mapped_column(
        String(36), 
        ForeignKey('inventory_function_modules.id', ondelete='SET NULL'),
        nullable=True,
        index=True
    )
    
    # 关联的计划ID
    related_plan_id: Mapped[Optional[str]] = mapped_column(
        String(50), 
        ForeignKey('plans.id', ondelete='SET NULL'),
        nullable=True,
        index=True
    )
    
    # 上线时间
    launch_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # 最新变更时间
    last_change_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # 创建和更新时间
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # 创建人
    created_by: Mapped[str] = mapped_column(String(100), nullable=False, default='')
    
    # 关联关系
    application: Mapped["ApplicationModel"] = relationship(
        "ApplicationModel",
        back_populates="function_modules_new",
        lazy="joined"
    )
    
    # 父模块关联
    parent_module: Mapped[Optional["FunctionModuleModel"]] = relationship(
        "FunctionModuleModel",
        back_populates="child_modules",
        lazy="joined",
        remote_side=[id]
    )

    # 子模块列表
    child_modules: Mapped[list["FunctionModuleModel"]] = relationship(
        "FunctionModuleModel",
        back_populates="parent_module",
        lazy="selectin"
    )
    
    # 关联计划
    related_plan: Mapped[Optional["PlanModel"]] = relationship(
        "PlanModel",
        lazy="joined"
    )
    
    # 生命周期日志
    lifecycle_logs: Mapped[list["LifecycleLogModel"]] = relationship(
        "LifecycleLogModel",
        back_populates="function_module",
        lazy="selectin",
        cascade="all, delete-orphan"
    )
    
    # 唯一约束：同一应用下模块编码+版本唯一
    __table_args__ = (
        UniqueConstraint('app_id', 'module_code', 'version', name='uq_app_module_version'),
        Index('idx_app_module_code', 'app_id', 'module_code'),
        Index('idx_module_status', 'app_id', 'status'),
        Index('idx_module_plan', 'related_plan_id'),
    )
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'app_id': self.app_id,
            'module_code': self.module_code,
            'module_name': self.module_name,
            'owner': self.owner,
            'module_description': self.module_description,
            'version': self.version,
            'status': self.status,
            'parent_module_id': self.parent_module_id,
            'related_plan_id': self.related_plan_id,
            'launch_time': self.launch_time.isoformat() if self.launch_time else None,
            'last_change_time': self.last_change_time.isoformat() if self.last_change_time else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by,
            'child_count': len(self.child_modules) if self.child_modules else 0,
        }
