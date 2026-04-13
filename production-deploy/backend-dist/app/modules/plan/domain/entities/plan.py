"""
计划聚合根实体
对应业务规则：计划创建、状态流转、台账关联
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Any, Dict
from uuid import UUID, uuid4

from ..value_objects.plan_id import PlanId
from ..value_objects.plan_tag import PlanTag
from ..value_objects.plan_status import PlanStatus
from ..value_objects.category import Category
from ..value_objects.priority import Priority
from ..value_objects.template_type import TemplateType
from ..value_objects.affected_module import AffectedModule
from ..events.plan_events import (
    PlanCreatedEvent,
    PlanStatusChangedEvent,
    PlanInventoryLinkedEvent,
    PlanDeletedEvent,
    PlanCompletedEvent,
)


@dataclass
class Plan:
    """
    计划聚合根实体
    
    核心职责：
    1. 维护计划基本信息和状态
    2. 管理台账关联关系
    3. 记录受影响功能模块
    4. 执行状态流转验证
    5. 生成领域事件
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
    
    # 受影响功能模块列表
    affected_modules: List[AffectedModule] = field(default_factory=list)
    
    # 审批材料详细信息（JSON列表）
    approval_files_detail: List[Dict[str, Any]] = field(default_factory=list)
    
    # 工作流模板类型（根据分类自动确定）
    template_type: Optional[str] = None
    
    # 审计信息
    created_by: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    # 领域事件（临时存储，用于跨层通信）
    _domain_events: List[Any] = field(default_factory=list, repr=False)
    
    # 文件关联（兼容性保留）
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
        workflow_template_id: Optional[str] = None,
        affected_modules: Optional[List[AffectedModule]] = None,
        approval_files_detail: Optional[List[Dict[str, Any]]] = None,
        template_type: Optional[str] = None,
    ) -> "Plan":
        """工厂方法：创建新计划"""
        # 生成ID (格式: PLAN-YYYYMMDD-XXX)
        plan_id = PlanId.generate(datetime.utcnow(), 1).value
        
        # 确定初始状态
        initial_status = PlanStatus.pending() if priority.is_p0 else PlanStatus.draft()
        
        # 确定台账操作类型
        inventory_action = category.inventory_action
        
        # 确定模板类型
        template_type = template_type or TemplateType.from_category(category.value).value
        
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
            affected_modules=affected_modules or [],
            approval_files_detail=approval_files_detail or [],
            template_type=template_type,
            created_by=created_by,
        )
        
        # 发布创建事件
        plan._domain_events.append(PlanCreatedEvent(
            plan_id=plan_id,
            name=name,
            category=category.value,
            priority=str(priority),
            status=initial_status.value,
            created_by=created_by,
            template_type=template_type,
        ))
        
        return plan
    
    def update(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        planned_start_time: Optional[datetime] = None,
        planned_end_time: Optional[datetime] = None,
        priority: Optional[Priority] = None,
        affected_modules: Optional[List[AffectedModule]] = None,
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
        if affected_modules is not None:
            self.affected_modules = affected_modules
        
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
        
        # 发布完成事件（触发台账更新和生命周期日志生成）
        self._domain_events.append(PlanCompletedEvent(
            plan_id=self.id,
            plan_name=self.name,
            category=self.category.value,
            affected_modules=[m.to_dict() for m in self.affected_modules],
            inventory_ids=self.inventory_ids,
            completed_by=completed_by,
        ))
        
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
    
    def add_affected_module(self, module: AffectedModule) -> None:
        """添加受影响的功能模块"""
        self.affected_modules.append(module)
        self.updated_at = datetime.utcnow()
    
    def update_affected_modules(self, modules: List[AffectedModule]) -> None:
        """更新受影响的功能模块列表"""
        self.affected_modules = modules
        self.updated_at = datetime.utcnow()
    
    def add_approval_file(self, file_detail: Dict[str, Any]) -> None:
        """添加审批材料（详细格式）"""
        # 检查是否已存在
        existing_urls = {f.get("file_url") for f in self.approval_files_detail}
        if file_detail.get("file_url") not in existing_urls:
            self.approval_files_detail.append(file_detail)
            # 同时更新兼容性字段
            if "file_id" in file_detail:
                file_id = UUID(file_detail["file_id"]) if isinstance(file_detail["file_id"], str) else file_detail["file_id"]
                if file_id not in self.approval_files:
                    self.approval_files.append(file_id)
            self.updated_at = datetime.utcnow()
    
    def remove_approval_file(self, file_url: str) -> None:
        """移除审批材料"""
        self.approval_files_detail = [
            f for f in self.approval_files_detail 
            if f.get("file_url") != file_url
        ]
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
    def template_type_value(self) -> str:
        """获取工作流模板类型值"""
        return self.template_type or TemplateType.from_category(self.category.value).value
    
    @property
    def is_overdue(self) -> bool:
        """是否逾期"""
        if not self.planned_end_time or self.status.value in ["COMPLETED", "CANCELLED"]:
            return False
        return datetime.utcnow() > self.planned_end_time
    
    @property
    def affected_modules_count(self) -> int:
        """受影响功能模块数量"""
        return len(self.affected_modules)
    
    def to_dict(self) -> dict:
        """转换为字典（用于序列化）"""
        return {
            "id": self.id,
            "data_tag": self.data_tag,
            "name": self.name,
            "category": self.category.value,
            "category_label": self.category.label,
            "priority": str(self.priority),
            "status": self.status.value,
            "status_label": self.status.label,
            "description": self.description,
            "planned_start_time": self.planned_start_time.isoformat() if self.planned_start_time else None,
            "planned_end_time": self.planned_end_time.isoformat() if self.planned_end_time else None,
            "actual_start_time": self.actual_start_time.isoformat() if self.actual_start_time else None,
            "actual_end_time": self.actual_end_time.isoformat() if self.actual_end_time else None,
            "workflow_template_id": self.workflow_template_id,
            "template_type": self.template_type_value,
            "inventory_ids": self.inventory_ids,
            "inventory_action": self.inventory_action,
            "affected_modules": [m.to_dict() for m in self.affected_modules],
            "affected_modules_count": self.affected_modules_count,
            "approval_files": self.approval_files_detail,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_overdue": self.is_overdue,
        }
