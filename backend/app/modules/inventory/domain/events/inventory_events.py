"""
台账管理领域事件
定义台账生命周期中发生的各种领域事件
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List


@dataclass
class DomainEvent:
    """领域事件基类"""
    occurred_at: datetime = datetime.utcnow()


# ==================== 应用系统台账事件 ====================

@dataclass
class ApplicationCreatedEvent(DomainEvent):
    """应用系统创建事件"""
    app_id: str = ""
    app_name: str = ""
    business_owner: str = ""
    project_owner: str = ""
    created_by: str = ""


@dataclass
class ApplicationUpdatedEvent(DomainEvent):
    """应用系统更新事件"""
    app_id: str = ""
    updated_fields: List[str] = None
    updated_by: str = ""


@dataclass
class ApplicationDeletedEvent(DomainEvent):
    """应用系统删除事件"""
    app_id: str = ""
    app_name: str = ""
    deleted_by: str = ""


@dataclass
class ApplicationStatusChangedEvent(DomainEvent):
    """应用系统状态变更事件"""
    app_id: str = ""
    old_status: str = ""
    new_status: str = ""
    changed_by: str = ""


# ==================== 云服务资源事件 ====================

@dataclass
class CloudResourceCreatedEvent(DomainEvent):
    """云资源创建事件"""
    resource_id: str = ""
    resource_name: str = ""
    resource_type: str = ""
    app_id: str = ""
    created_by: str = ""


@dataclass
class CloudResourceUpdatedEvent(DomainEvent):
    """云资源更新事件"""
    resource_id: str = ""
    updated_fields: List[str] = None
    updated_by: str = ""


@dataclass
class CloudResourceDeletedEvent(DomainEvent):
    """云资源删除事件"""
    resource_id: str = ""
    resource_name: str = ""
    app_id: str = ""
    deleted_by: str = ""


# ==================== 账号台账事件 ====================

@dataclass
class AccountCreatedEvent(DomainEvent):
    """账号创建事件"""
    account_id: str = ""
    account_name: str = ""
    account_type: str = ""
    app_id: str = ""
    holder_name: str = ""
    created_by: str = ""


@dataclass
class AccountUpdatedEvent(DomainEvent):
    """账号更新事件"""
    account_id: str = ""
    updated_fields: List[str] = None
    updated_by: str = ""


@dataclass
class AccountDeletedEvent(DomainEvent):
    """账号删除事件"""
    account_id: str = ""
    account_name: str = ""
    app_id: str = ""
    deleted_by: str = ""


@dataclass
class AccountExpiredEvent(DomainEvent):
    """账号过期事件"""
    account_id: str = ""
    account_name: str = ""
    app_id: str = ""
    expired_at: datetime = None


# ==================== 计划关联事件 ====================

@dataclass
class PlanLinkedEvent(DomainEvent):
    """计划关联事件"""
    inventory_id: str = ""
    inventory_type: str = ""  # application, cloud_resource, account
    plan_id: str = ""
    linked_by: str = ""


@dataclass
class PlanUnlinkedEvent(DomainEvent):
    """计划解除关联事件"""
    inventory_id: str = ""
    inventory_type: str = ""
    plan_id: str = ""
    unlinked_by: str = ""


# ==================== 功能模块事件 ====================

@dataclass
class FunctionModuleAddedEvent(DomainEvent):
    """功能模块添加事件"""
    app_id: str = ""
    module_name: str = ""
    added_by: str = ""


@dataclass
class FunctionModuleUpdatedEvent(DomainEvent):
    """功能模块更新事件"""
    app_id: str = ""
    module_name: str = ""
    updated_by: str = ""


@dataclass
class FunctionModuleRemovedEvent(DomainEvent):
    """功能模块移除事件"""
    app_id: str = ""
    module_name: str = ""
    removed_by: str = ""
