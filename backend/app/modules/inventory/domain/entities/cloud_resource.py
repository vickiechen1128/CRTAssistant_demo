"""
云服务资源台账实体
对应数据模型：inventory_cloud_resources
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import uuid4

from ..value_objects.resource_type import ResourceType
from ..value_objects.inventory_status import InventoryStatus
from ..events.inventory_events import (
    CloudResourceCreatedEvent,
    CloudResourceUpdatedEvent,
    CloudResourceDeletedEvent,
    PlanLinkedEvent,
    PlanUnlinkedEvent,
)


@dataclass
class CloudResource:
    """
    云服务资源台账实体
    
    核心职责：
    1. 维护云服务资源基本信息
    2. 管理资源配置
    3. 关联应用系统
    4. 处理计划关联关系
    """
    # 标识
    id: str
    
    # 关联应用
    app_id: str
    
    # 资源信息
    resource_type: ResourceType
    resource_name: str
    configuration: Dict[str, Any] = field(default_factory=dict)
    
    # 状态
    status: InventoryStatus = field(default_factory=lambda: InventoryStatus.active())
    
    # 关联计划
    related_plan_ids: List[str] = field(default_factory=list)
    
    # 审计信息
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    created_by: str = ""
    
    # 领域事件
    _domain_events: List[Any] = field(default_factory=list, repr=False)
    
    @classmethod
    def create(
        cls,
        app_id: str,
        resource_type: ResourceType,
        resource_name: str,
        created_by: str,
        configuration: Optional[Dict[str, Any]] = None,
    ) -> "CloudResource":
        """工厂方法：创建新云资源"""
        resource_id = str(uuid4())
        
        resource = cls(
            id=resource_id,
            app_id=app_id,
            resource_type=resource_type,
            resource_name=resource_name,
            configuration=configuration or {},
            created_by=created_by,
        )
        
        # 发布创建事件
        resource._domain_events.append(CloudResourceCreatedEvent(
            resource_id=resource_id,
            resource_name=resource_name,
            resource_type=resource_type.value,
            app_id=app_id,
            created_by=created_by
        ))
        
        return resource
    
    def update(
        self,
        resource_name: Optional[str] = None,
        configuration: Optional[Dict[str, Any]] = None,
        updated_by: str = ""
    ) -> None:
        """更新资源信息"""
        if not self.status.is_editable:
            raise ValueError(f"Cannot update resource in {self.status.value} status")
        
        updated_fields = []
        
        if resource_name is not None:
            self.resource_name = resource_name
            updated_fields.append("resource_name")
        if configuration is not None:
            self.configuration.update(configuration)
            updated_fields.append("configuration")
        
        if updated_fields:
            self.updated_at = datetime.utcnow()
            self._domain_events.append(CloudResourceUpdatedEvent(
                resource_id=self.id,
                updated_fields=updated_fields,
                updated_by=updated_by
            ))
    
    def change_status(self, new_status: InventoryStatus, changed_by: str = "") -> None:
        """变更状态"""
        if self.status == new_status:
            return
        
        self.status = new_status
        self.updated_at = datetime.utcnow()
    
    def link_plan(self, plan_id: str, linked_by: str = "") -> None:
        """关联计划"""
        if not self.status.can_associate_plan:
            raise ValueError(f"Cannot link plan to resource in {self.status.value} status")
        
        if plan_id not in self.related_plan_ids:
            self.related_plan_ids.append(plan_id)
            self.updated_at = datetime.utcnow()
            
            self._domain_events.append(PlanLinkedEvent(
                inventory_id=self.id,
                inventory_type="cloud_resource",
                plan_id=plan_id,
                linked_by=linked_by
            ))
    
    def unlink_plan(self, plan_id: str, unlinked_by: str = "") -> None:
        """解除计划关联"""
        if plan_id in self.related_plan_ids:
            self.related_plan_ids.remove(plan_id)
            self.updated_at = datetime.utcnow()
            
            self._domain_events.append(PlanUnlinkedEvent(
                inventory_id=self.id,
                inventory_type="cloud_resource",
                plan_id=plan_id,
                unlinked_by=unlinked_by
            ))
    
    def can_delete(self) -> bool:
        """是否可以删除"""
        if self.related_plan_ids:
            return False
        return True
    
    def get_domain_events(self) -> List[Any]:
        """获取领域事件并清空"""
        events = self._domain_events.copy()
        self._domain_events.clear()
        return events
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "app_id": self.app_id,
            "resource_type": self.resource_type.value,
            "resource_type_display": self.resource_type.display_name,
            "resource_name": self.resource_name,
            "configuration": self.configuration,
            "status": self.status.value,
            "related_plan_ids": self.related_plan_ids,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "created_by": self.created_by,
        }
