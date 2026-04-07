"""
台账管理数据库模型
SQLAlchemy ORM 映射
"""
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, String, DateTime, Text, Integer, ForeignKey, Index
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.sqlite import JSON

from app.core.database import Base


class ApplicationModel(Base):
    """应用系统台账数据库模型"""
    __tablename__ = 'inventory_applications'
    
    # 主键
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    
    # 基本信息
    app_name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    app_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    system_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, default='web')
    function_modules: Mapped[List[dict]] = mapped_column(JSON, default=list)
    
    # 部署信息
    hostname: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    app_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # 负责人
    business_owner: Mapped[str] = mapped_column(String(50), nullable=False)
    project_owner: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # 时间
    launch_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # 状态
    status: Mapped[str] = mapped_column(String(50), nullable=False, default='active', index=True)
    
    # 关联计划（JSON数组存储计划ID）
    related_plan_ids: Mapped[List[str]] = mapped_column(JSON, default=list)
    
    # 审计信息
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    created_by: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # 关联关系
    cloud_resources = relationship(
        'CloudResourceModel',
        back_populates='application',
        cascade='all, delete-orphan',
        lazy='dynamic'
    )
    accounts = relationship(
        'AccountModel',
        back_populates='application',
        cascade='all, delete-orphan',
        lazy='dynamic'
    )
    
    # 功能模块（新的独立实体关系）
    function_modules_new = relationship(
        'FunctionModuleModel',
        back_populates='application',
        cascade='all, delete-orphan',
        lazy='selectin'
    )
    
    # 生命周期日志
    lifecycle_logs = relationship(
        'LifecycleLogModel',
        back_populates='application',
        cascade='all, delete-orphan',
        lazy='dynamic',
        order_by='desc(LifecycleLogModel.operation_time)'
    )
    
    def __repr__(self) -> str:
        return f"<ApplicationModel(id={self.id}, name={self.app_name}, status={self.status})>"


class CloudResourceModel(Base):
    """云服务资源台账数据库模型"""
    __tablename__ = 'inventory_cloud_resources'
    
    # 主键
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    
    # 关联应用
    app_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey('inventory_applications.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    # 资源信息
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    resource_name: Mapped[str] = mapped_column(String(100), nullable=False)
    configuration: Mapped[dict] = mapped_column(JSON, default=dict)
    
    # 状态
    status: Mapped[str] = mapped_column(String(50), nullable=False, default='active', index=True)
    
    # 关联计划
    related_plan_ids: Mapped[List[str]] = mapped_column(JSON, default=list)
    
    # 审计信息
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    created_by: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # 关联关系
    application = relationship('ApplicationModel', back_populates='cloud_resources')
    
    def __repr__(self) -> str:
        return f"<CloudResourceModel(id={self.id}, name={self.resource_name}, type={self.resource_type})>"


class AccountModel(Base):
    """系统及软件账号台账数据库模型"""
    __tablename__ = 'inventory_accounts'
    
    # 主键
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    
    # 关联应用
    app_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey('inventory_applications.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    # 账号信息
    account_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    account_name: Mapped[str] = mapped_column(String(100), nullable=False)
    permission_level: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    holder_name: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # 有效期
    valid_from: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    valid_until: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    
    # 密码管理
    password_change_cycle: Mapped[int] = mapped_column(Integer, default=90)
    last_password_change: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # 状态
    status: Mapped[str] = mapped_column(String(50), nullable=False, default='active', index=True)
    
    # 关联计划
    related_plan_ids: Mapped[List[str]] = mapped_column(JSON, default=list)
    
    # 审计信息
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    created_by: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # 关联关系
    application = relationship('ApplicationModel', back_populates='accounts')
    
    def __repr__(self) -> str:
        return f"<AccountModel(id={self.id}, name={self.account_name}, type={self.account_type})>"


# 创建复合索引
Index('idx_resource_app_name', CloudResourceModel.app_id, CloudResourceModel.resource_name, unique=True)
Index('idx_account_app_name', AccountModel.app_id, AccountModel.account_name, unique=True)
