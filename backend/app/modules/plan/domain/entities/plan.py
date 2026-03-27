"""
计划聚合根实体
对应业务规则：计划创建、状态流转、台账关联
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Any
from uuid import UUID, uuid4

from ..value_objects.plan_id import PlanId
from ..value_objects.plan_tag import PlanTag
from ..value_objects.plan_status import PlanStatus
from ..value_objects.category import Category
from ..value_objects.priority import Priority
from ..value_objects.template_type import TemplateType
from ..events.plan_events import (
    PlanCreatedEvent,
    PlanStatusChangedEvent,
    PlanInventoryLinkedEvent,
    PlanDeletedEvent
)


@dataclass
class Plan:
    """
    计划聚合根实体
    
    核心职责：
    1. 维护计划基本信息和状态
    2. 管理台账关联关系
    3. 执行状态流转验证
    4. 生成领域事件
    """
    # 标识
    id: str
    data_tag: str
    
    # 基本信息
    name: str
    category: Category
    priority: Priority
    description: Optional[str] = None
    
    # 时间信息
    planned_start_time: Optional[datetime] = None
    planned_end_time: Optional[datetime] = None
    actual_start_time: Optional[datetime] = None
    actual_end_time: Optional[datetime] = None
    
    # 状态
    status: PlanStatus = field(default_factory=lambda: PlanStatus.draft())
    
    # 关联信息
    workflow_template_id: Optional[str] = None
    inventory_ids: List[str] = field(default_factory=list)
    inventory_action: Optional[str] = None
    
    # 审计信息
    created_by: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    # 领域事件（临时存储，用于跨层通信）
    _domain_events: List[Any] = field(default_factory=list, repr=False)
    
    # 文件关联
    approval_files: List[UUID] = field(default_factory=list)
    
    @classmethod
    def create(
        cls,
        name: str,
        category: Category,
        priority: Priority,
        data_tag: str,
        created_by: str,
        description: Optional[str] = None,
        planned_start_time: Optional[datetime] = None,
        planned_end_time: Optional[datetime] = None,
        workflow_template_id: Optional[str] = None
    ) -> "Plan":
        """工厂方法：创建新计划"""
        # 生成ID
        plan_id = PlanId.generate(datetime.utcnow(), 1).value
        
        # 确定初始状态
        initial_status = PlanStatus.pending() if priority.is_p0 else PlanStatus.draft()
        
        # 确定台账操作类型
        inventory_action = category.inventory_action
        
        plan = cls(
            id=plan_id,
            data_tag=data_tag,
            name=name,
            category=category,
            priority=priority,
            description=description,
            planned_start_time=planned_start_time,
            planned_end_time=planned_end_time,
            status=initial_status,
            workflow_template_id=workflow_template_id,
            inventory_action=inventory_action,
            created_by=created_by,
        )
        
        # 发布创建事件
        plan._domain_events.append(PlanCreatedEvent(
            plan_id=plan_id,
            name=name,
            category=category.value,
            priority=str(priority),
            status=initial_status.value,
            created_by=created_by
        ))
        
        return plan
    
    def update(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        planned_start_time: Optional[datetime] = None,
        planned_end_time: Optional[datetime] = None,
        priority: Optional[Priority] = None
    ) -> None:
        """更新计划信息（仅草稿状态可编辑）"""
        if not self.status.is_editable:
            raise ValueError(f"Cannot update plan in {self.status.value} status")
        
        if name is not None:
            self.name = name
        if description is not None:
            self.description = description
        if planned_start_time is not None:
            self.planned_start_time = planned_start_time
        if planned_end_time is not None:
            self.planned_end_time = planned_end_time
        if priority is not None:
            self.priority = priority
            # 如果变为P0，状态改为PENDING
            if priority.is_p0 and self.status.value == "DRAFT":
                self._change_status(PlanStatus.pending())
            # 如果从P0变为非P0，状态改为DRAFT
            elif not priority.is_p0 and self.status.value == "PENDING":
                self._change_status(PlanStatus.draft())
        
        self.updated_at = datetime.utcnow()
    
    def start(self, started_by: str) -> None:
        """启动计划"""
        if not self.status.is_startable:
            raise ValueError(f"Cannot start plan in {self.status.value} status")
        
        old_status = self.status
        self._change_status(PlanStatus.in_progress())
        self.actual_start_time = datetime.utcnow()
        
        self._domain_events.append(PlanStatusChangedEvent(
            plan_id=self.id,
            old_status=old_status.value,
            new_status=self.status.value,
            changed_by=started_by,
            reason="Plan started"
        ))
    
    def complete(self, completed_by: str) -> None:
        """完成计划"""
        if self.status.value != "IN_PROGRESS":
            raise ValueError(f"Cannot complete plan in {self.status.value} status")
        
        old_status = self.status
        self._change_status(PlanStatus.completed())
        self.actual_end_time = datetime.utcnow()
        
        self._domain_events.append(PlanStatusChangedEvent(
            plan_id=self.id,
            old_status=old_status.value,
            new_status=self.status.value,
            changed_by=completed_by,
            reason="Plan completed"
        ))
    
    def cancel(self, cancelled_by: str, reason: Optional[str] = None) -> None:
        """取消计划"""
        if not self.status.is_cancellable:
            raise ValueError(f"Cannot cancel plan in {self.status.value} status")
        
        old_status = self.status
        self._change_status(PlanStatus.cancelled())
        
        self._domain_events.append(PlanStatusChangedEvent(
            plan_id=self.id,
            old_status=old_status.value,
            new_status=self.status.value,
            changed_by=cancelled_by,
            reason=reason or "Plan cancelled"
        ))
    
    def link_inventory(self, inventory_ids: List[str], linked_by: str) -> None:
        """关联台账"""
        if not self.category.requires_inventory:
            raise ValueError(f"Category {self.category.value} does not require inventory")
        
        self.inventory_ids = inventory_ids
        self.updated_at = datetime.utcnow()
        
        self._domain_events.append(PlanInventoryLinkedEvent(
            plan_id=self.id,
            inventory_ids=inventory_ids,
            linked_by=linked_by
        ))
    
    def add_approval_file(self, file_id: UUID) -> None:
        """添加审批材料"""
        if file_id not in self.approval_files:
            self.approval_files.append(file_id)
            self.updated_at = datetime.utcnow()
    
    def remove_approval_file(self, file_id: UUID) -> None:
        """移除审批材料"""
        if file_id in self.approval_files:
            self.approval_files.remove(file_id)
            self.updated_at = datetime.utcnow()
    
    def _change_status(self, new_status: PlanStatus) -> None:
        """内部方法：改变状态"""
        if not self.status.can_transition_to(new_status):
            raise ValueError(
                f"Invalid status transition from {self.status.value} to {new_status.value}"
            )
        self.status = new_status
        self.updated_at = datetime.utcnow()
    
    def can_delete(self) -> bool:
        """是否可以删除"""
        return self.status.is_deletable
    
    def get_domain_events(self) -> List[Any]:
        """获取领域事件并清空"""
        events = self._domain_events.copy()
        self._domain_events.clear()
        return events
    
    @property
    def template_type(self) -> TemplateType:
        """获取工作流模板类型"""
        return TemplateType.from_category(self.category.value)
    
    @property
    def is_overdue(self) -> bool:
        """是否逾期"""
        if not self.planned_end_time or self.status.value in ["COMPLETED", "CANCELLED"]:
            return False
        return datetime.utcnow() > self.planned_end_time
    
    def to_dict(self) -> dict:
        """转换为字典（用于序列化）"""
        return {
            "id": self.id,
            "data_tag": self.data_tag,
            "name": self.name,
            "category": self.category.value,
            "priority": str(self.priority),
            "status": self.status.value,
            "description": self.description,
            "planned_start_time": self.planned_start_time.isoformat() if self.planned_start_time else None,
            "planned_end_time": self.planned_end_time.isoformat() if self.planned_end_time else None,
            "actual_start_time": self.actual_start_time.isoformat() if self.actual_start_time else None,
            "actual_end_time": self.actual_end_time.isoformat() if self.actual_end_time else None,
            "workflow_template_id": self.workflow_template_id,
            "inventory_ids": self.inventory_ids,
            "inventory_action": self.inventory_action,
            "approval_files": [str(fid) for fid in self.approval_files],
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_overdue": self.is_overdue
        }
