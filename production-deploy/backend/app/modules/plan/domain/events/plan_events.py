"""
计划模块领域事件
"""
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class DomainEvent:
    """领域事件基类"""
    event_id: str
    event_type: str
    occurred_at: datetime
    aggregate_id: str
    aggregate_type: str
    
    def __init__(self, aggregate_id: str, aggregate_type: str):
        import uuid
        self.event_id = str(uuid.uuid4())
        self.event_type = self.__class__.__name__
        self.occurred_at = datetime.utcnow()
        self.aggregate_id = aggregate_id
        self.aggregate_type = aggregate_type


@dataclass
class PlanCreatedEvent(DomainEvent):
    """计划创建事件"""
    plan_id: str = ""
    name: str = ""
    category: str = ""
    priority: str = ""
    status: str = ""
    template_type: str = ""
    created_by: str = ""
    
    def __init__(self, **kwargs):
        super().__init__(
            aggregate_id=kwargs.get('plan_id', ''),
            aggregate_type='Plan'
        )
        self.plan_id = kwargs.get('plan_id', '')
        self.name = kwargs.get('name', '')
        self.category = kwargs.get('category', '')
        self.priority = kwargs.get('priority', '')
        self.status = kwargs.get('status', '')
        self.template_type = kwargs.get('template_type', '')
        self.created_by = kwargs.get('created_by', '')


@dataclass
class PlanUpdatedEvent(DomainEvent):
    """计划更新事件"""
    plan_id: str = ""
    updated_fields: dict = None
    updated_by: str = ""
    
    def __init__(self, **kwargs):
        super().__init__(
            aggregate_id=kwargs.get('plan_id', ''),
            aggregate_type='Plan'
        )
        self.plan_id = kwargs.get('plan_id', '')
        self.updated_fields = kwargs.get('updated_fields', {})
        self.updated_by = kwargs.get('updated_by', '')


@dataclass
class PlanDeletedEvent(DomainEvent):
    """计划删除事件"""
    plan_id: str = ""
    deleted_by: str = ""
    
    def __init__(self, **kwargs):
        super().__init__(
            aggregate_id=kwargs.get('plan_id', ''),
            aggregate_type='Plan'
        )
        self.plan_id = kwargs.get('plan_id', '')
        self.deleted_by = kwargs.get('deleted_by', '')


@dataclass
class PlanStatusChangedEvent(DomainEvent):
    """计划状态变更事件"""
    plan_id: str = ""
    old_status: str = ""
    new_status: str = ""
    changed_by: str = ""
    reason: Optional[str] = None
    
    def __init__(self, **kwargs):
        super().__init__(
            aggregate_id=kwargs.get('plan_id', ''),
            aggregate_type='Plan'
        )
        self.plan_id = kwargs.get('plan_id', '')
        self.old_status = kwargs.get('old_status', '')
        self.new_status = kwargs.get('new_status', '')
        self.changed_by = kwargs.get('changed_by', '')
        self.reason = kwargs.get('reason')


@dataclass
class PlanInventoryLinkedEvent(DomainEvent):
    """计划台账关联事件"""
    plan_id: str = ""
    inventory_ids: List[str] = None
    linked_by: str = ""
    
    def __init__(self, **kwargs):
        super().__init__(
            aggregate_id=kwargs.get('plan_id', ''),
            aggregate_type='Plan'
        )
        self.plan_id = kwargs.get('plan_id', '')
        self.inventory_ids = kwargs.get('inventory_ids', [])
        self.linked_by = kwargs.get('linked_by', '')


@dataclass
class PlanStartedEvent(DomainEvent):
    """计划启动事件"""
    plan_id: str = ""
    started_by: str = ""
    started_at: datetime = None
    
    def __init__(self, **kwargs):
        super().__init__(
            aggregate_id=kwargs.get('plan_id', ''),
            aggregate_type='Plan'
        )
        self.plan_id = kwargs.get('plan_id', '')
        self.started_by = kwargs.get('started_by', '')
        self.started_at = kwargs.get('started_at', datetime.utcnow())


@dataclass
class PlanCompletedEvent(DomainEvent):
    """计划完成事件 - 触发台账更新和生命周期日志生成"""
    plan_id: str = ""
    plan_name: str = ""
    category: str = ""
    affected_modules: List[dict] = None
    inventory_ids: List[str] = None
    completed_by: str = ""
    completed_at: datetime = None
    
    def __init__(self, **kwargs):
        super().__init__(
            aggregate_id=kwargs.get('plan_id', ''),
            aggregate_type='Plan'
        )
        self.plan_id = kwargs.get('plan_id', '')
        self.plan_name = kwargs.get('plan_name', '')
        self.category = kwargs.get('category', '')
        self.affected_modules = kwargs.get('affected_modules', [])
        self.inventory_ids = kwargs.get('inventory_ids', [])
        self.completed_by = kwargs.get('completed_by', '')
        self.completed_at = kwargs.get('completed_at', datetime.utcnow())


@dataclass
class PlanCancelledEvent(DomainEvent):
    """计划取消事件"""
    plan_id: str = ""
    cancelled_by: str = ""
    reason: Optional[str] = None
    cancelled_at: datetime = None
    
    def __init__(self, **kwargs):
        super().__init__(
            aggregate_id=kwargs.get('plan_id', ''),
            aggregate_type='Plan'
        )
        self.plan_id = kwargs.get('plan_id', '')
        self.cancelled_by = kwargs.get('cancelled_by', '')
        self.reason = kwargs.get('reason')
        self.cancelled_at = kwargs.get('cancelled_at', datetime.utcnow())
