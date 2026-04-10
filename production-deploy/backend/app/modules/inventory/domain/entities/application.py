"""
应用系统台账实体
对应数据模型：inventory_applications
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import uuid4

from ..value_objects.inventory_status import InventoryStatus
from ..events.inventory_events import (
    ApplicationCreatedEvent,
    ApplicationUpdatedEvent,
    ApplicationDeletedEvent,
    ApplicationStatusChangedEvent,
    FunctionModuleAddedEvent,
    FunctionModuleUpdatedEvent,
    FunctionModuleRemovedEvent,
    PlanLinkedEvent,
    PlanUnlinkedEvent,
)


@dataclass
class FunctionModule:
    """功能模块值对象"""
    module_name: str
    launch_time: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "module_name": self.module_name,
            "launch_time": self.launch_time.isoformat() if self.launch_time else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FunctionModule":
        launch_time = None
        if data.get("launch_time"):
            if isinstance(data["launch_time"], str):
                launch_time = datetime.fromisoformat(data["launch_time"])
            else:
                launch_time = data["launch_time"]
        return cls(
            module_name=data["module_name"],
            launch_time=launch_time
        )


@dataclass
class Application:
    """
    应用系统台账实体
    
    核心职责：
    1. 维护应用系统基本信息
    2. 管理功能模块
    3. 处理计划关联关系
    4. 管理生命周期状态
    """
    # 标识
    id: str
    
    # 基本信息
    app_name: str
    app_description: Optional[str] = None
    system_type: Optional[str] = field(default='web')
    function_modules: List[FunctionModule] = field(default_factory=list)
    
    # 部署信息
    hostname: Optional[str] = None
    app_url: Optional[str] = None
    
    # 负责人
    business_owner: str = ""
    project_owner: str = ""
    
    # 时间
    launch_time: Optional[datetime] = None
    
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
        app_name: str,
        business_owner: str,
        project_owner: str,
        created_by: str,
        app_description: Optional[str] = None,
        system_type: Optional[str] = 'web',
        hostname: Optional[str] = None,
        app_url: Optional[str] = None,
        function_modules: Optional[List[Dict]] = None,
        launch_time: Optional[datetime] = None,
    ) -> "Application":
        """工厂方法：创建新应用系统"""
        app_id = str(uuid4())
        
        # 转换功能模块
        modules = []
        if function_modules:
            modules = [FunctionModule.from_dict(m) if isinstance(m, dict) else m for m in function_modules]
        
        app = cls(
            id=app_id,
            app_name=app_name,
            app_description=app_description,
            system_type=system_type,
            function_modules=modules,
            hostname=hostname,
            app_url=app_url,
            business_owner=business_owner,
            project_owner=project_owner,
            launch_time=launch_time,
            created_by=created_by,
        )
        
        # 发布创建事件
        app._domain_events.append(ApplicationCreatedEvent(
            app_id=app_id,
            app_name=app_name,
            business_owner=business_owner,
            project_owner=project_owner,
            created_by=created_by
        ))
        
        return app
    
    def update(
        self,
        app_description: Optional[str] = None,
        hostname: Optional[str] = None,
        app_url: Optional[str] = None,
        business_owner: Optional[str] = None,
        project_owner: Optional[str] = None,
        launch_time: Optional[datetime] = None,
        updated_by: str = ""
    ) -> None:
        """更新应用信息"""
        if not self.status.is_editable:
            raise ValueError(f"Cannot update application in {self.status.value} status")
        
        updated_fields = []
        
        if app_description is not None:
            self.app_description = app_description
            updated_fields.append("app_description")
        if hostname is not None:
            self.hostname = hostname
            updated_fields.append("hostname")
        if app_url is not None:
            self.app_url = app_url
            updated_fields.append("app_url")
        if business_owner is not None:
            self.business_owner = business_owner
            updated_fields.append("business_owner")
        if project_owner is not None:
            self.project_owner = project_owner
            updated_fields.append("project_owner")
        if launch_time is not None:
            self.launch_time = launch_time
            updated_fields.append("launch_time")
        
        if updated_fields:
            self.updated_at = datetime.utcnow()
            self._domain_events.append(ApplicationUpdatedEvent(
                app_id=self.id,
                updated_fields=updated_fields,
                updated_by=updated_by
            ))
    
    def add_function_module(self, module_name: str, launch_time: Optional[datetime] = None, added_by: str = "") -> None:
        """添加功能模块"""
        # 检查是否已存在
        for module in self.function_modules:
            if module.module_name == module_name:
                raise ValueError(f"Function module '{module_name}' already exists")
        
        self.function_modules.append(FunctionModule(module_name=module_name, launch_time=launch_time))
        self.updated_at = datetime.utcnow()
        
        self._domain_events.append(FunctionModuleAddedEvent(
            app_id=self.id,
            module_name=module_name,
            added_by=added_by
        ))
    
    def update_function_module(self, module_name: str, launch_time: Optional[datetime] = None, updated_by: str = "") -> None:
        """更新功能模块"""
        for module in self.function_modules:
            if module.module_name == module_name:
                module.launch_time = launch_time
                self.updated_at = datetime.utcnow()
                
                self._domain_events.append(FunctionModuleUpdatedEvent(
                    app_id=self.id,
                    module_name=module_name,
                    updated_by=updated_by
                ))
                return
        
        raise ValueError(f"Function module '{module_name}' not found")
    
    def remove_function_module(self, module_name: str, removed_by: str = "") -> None:
        """移除功能模块"""
        for i, module in enumerate(self.function_modules):
            if module.module_name == module_name:
                self.function_modules.pop(i)
                self.updated_at = datetime.utcnow()
                
                self._domain_events.append(FunctionModuleRemovedEvent(
                    app_id=self.id,
                    module_name=module_name,
                    removed_by=removed_by
                ))
                return
        
        raise ValueError(f"Function module '{module_name}' not found")
    
    def change_status(self, new_status: InventoryStatus, changed_by: str = "") -> None:
        """变更状态"""
        if self.status == new_status:
            return
        
        old_status = self.status
        self.status = new_status
        self.updated_at = datetime.utcnow()
        
        self._domain_events.append(ApplicationStatusChangedEvent(
            app_id=self.id,
            old_status=old_status.value,
            new_status=new_status.value,
            changed_by=changed_by
        ))
    
    def link_plan(self, plan_id: str, linked_by: str = "") -> None:
        """关联计划"""
        if not self.status.can_associate_plan:
            raise ValueError(f"Cannot link plan to application in {self.status.value} status")
        
        if plan_id not in self.related_plan_ids:
            self.related_plan_ids.append(plan_id)
            self.updated_at = datetime.utcnow()
            
            self._domain_events.append(PlanLinkedEvent(
                inventory_id=self.id,
                inventory_type="application",
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
                inventory_type="application",
                plan_id=plan_id,
                unlinked_by=unlinked_by
            ))
    
    def can_delete(self) -> bool:
        """是否可以删除（检查关联关系）"""
        # 检查是否有关联的计划
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
            "app_name": self.app_name,
            "app_description": self.app_description,
            "system_type": self.system_type,
            "function_modules": [m.to_dict() if hasattr(m, 'to_dict') else m for m in self.function_modules],
            "hostname": self.hostname,
            "app_url": self.app_url,
            "business_owner": self.business_owner,
            "project_owner": self.project_owner,
            "launch_time": self.launch_time.isoformat() if self.launch_time else None,
            "status": self.status.value,
            "related_plan_ids": self.related_plan_ids,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "created_by": self.created_by,
        }
