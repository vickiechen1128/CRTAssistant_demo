"""
功能模块实体 - 独立实体（非值对象）
对应数据模型：inventory_function_modules

变更说明：
- 从 Application 中的 JSON 字段升级为独立实体
- 支持完整的生命周期管理
- 支持层级结构（父模块-子模块）
- 与计划强关联
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import uuid4

from ..value_objects.module_status import ModuleStatus
from ..events.inventory_events import (
    FunctionModuleCreatedEvent,
    FunctionModuleUpdatedEvent,
    FunctionModuleStatusChangedEvent,
    FunctionModuleDeletedEvent,
)


@dataclass
class FunctionModule:
    """
    功能模块实体
    
    核心职责：
    1. 维护功能模块完整信息（编码、名称、描述、负责人等）
    2. 管理模块生命周期状态（草稿→开发中→测试中→已上线→已下线）
    3. 支持版本管理
    4. 支持层级结构（父模块-子模块）
    5. 记录与计划的关联
    """
    
    # 标识
    id: str
    app_id: str  # 关联的应用系统ID
    
    # 基本信息
    module_code: str  # 模块编码，应用内唯一
    module_name: str
    module_description: Optional[str] = None
    
    # 负责人
    owner: str = ""
    
    # 生命周期状态
    status: ModuleStatus = field(default_factory=lambda: ModuleStatus.draft())
    
    # 版本管理
    version: Optional[str] = None
    
    # 时间信息
    launch_time: Optional[datetime] = None  # 首次上线时间
    last_change_time: Optional[datetime] = None  # 最新变更时间
    
    # 层级结构
    parent_module_id: Optional[str] = None  # 父模块ID，支持层级
    
    # 计划关联（创建/上线时关联的计划）
    related_plan_id: Optional[str] = None
    
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
        module_code: str,
        module_name: str,
        owner: str,
        created_by: str,
        module_description: Optional[str] = None,
        version: Optional[str] = None,
        parent_module_id: Optional[str] = None,
        related_plan_id: Optional[str] = None,
    ) -> "FunctionModule":
        """工厂方法：创建新功能模块"""
        module_id = str(uuid4())
        
        module = cls(
            id=module_id,
            app_id=app_id,
            module_code=module_code,
            module_name=module_name,
            module_description=module_description,
            owner=owner,
            version=version or "v1.0.0",
            parent_module_id=parent_module_id,
            related_plan_id=related_plan_id,
            created_by=created_by,
        )
        
        # 发布创建事件
        module._domain_events.append(FunctionModuleCreatedEvent(
            module_id=module_id,
            app_id=app_id,
            module_code=module_code,
            module_name=module_name,
            owner=owner,
            related_plan_id=related_plan_id,
            created_by=created_by,
        ))
        
        return module
    
    def update(
        self,
        module_name: Optional[str] = None,
        module_description: Optional[str] = None,
        owner: Optional[str] = None,
        version: Optional[str] = None,
        parent_module_id: Optional[str] = None,
        updated_by: str = "",
    ) -> Dict[str, Any]:
        """
        更新模块信息
        返回变更前后对比，用于生成生命周期日志
        """
        changes = {}
        
        if module_name is not None and module_name != self.module_name:
            changes["module_name"] = {"before": self.module_name, "after": module_name}
            self.module_name = module_name
            
        if module_description is not None and module_description != self.module_description:
            changes["module_description"] = {"before": self.module_description, "after": module_description}
            self.module_description = module_description
            
        if owner is not None and owner != self.owner:
            changes["owner"] = {"before": self.owner, "after": owner}
            self.owner = owner
            
        if version is not None and version != self.version:
            changes["version"] = {"before": self.version, "after": version}
            self.version = version
            self.last_change_time = datetime.utcnow()
            
        if parent_module_id is not None and parent_module_id != self.parent_module_id:
            changes["parent_module_id"] = {"before": self.parent_module_id, "after": parent_module_id}
            self.parent_module_id = parent_module_id
        
        if changes:
            self.updated_at = datetime.utcnow()
            self._domain_events.append(FunctionModuleUpdatedEvent(
                module_id=self.id,
                app_id=self.app_id,
                changes=list(changes.keys()),
                updated_by=updated_by,
            ))
        
        return changes
    
    def change_status(
        self,
        new_status: ModuleStatus,
        changed_by: str = "",
    ) -> Dict[str, Any]:
        """
        变更模块状态
        状态流转：draft → developing → testing → online → offline
        返回变更信息用于生成生命周期日志
        """
        if self.status == new_status:
            return {}
        
        # 状态流转校验
        if not self.status.can_transition_to(new_status):
            raise ValueError(
                f"Cannot transition from {self.status.value} to {new_status.value}"
            )
        
        old_status = self.status
        self.status = new_status
        self.updated_at = datetime.utcnow()
        
        # 状态特定处理
        if new_status.is_online:
            if not self.launch_time:
                self.launch_time = datetime.utcnow()
            self.last_change_time = datetime.utcnow()
        
        change_info = {
            "status": {
                "before": old_status.value,
                "after": new_status.value,
            }
        }
        
        self._domain_events.append(FunctionModuleStatusChangedEvent(
            module_id=self.id,
            app_id=self.app_id,
            module_name=self.module_name,
            old_status=old_status.value,
            new_status=new_status.value,
            changed_by=changed_by,
        ))
        
        return change_info
    
    def mark_as_launched(self, plan_id: str, launched_by: str = "") -> None:
        """标记为已上线（由计划完成时调用）"""
        if not self.status.is_online:
            self.change_status(ModuleStatus.online(), launched_by)
        self.related_plan_id = plan_id
        self.launch_time = datetime.utcnow()
        self.last_change_time = datetime.utcnow()
    
    def can_delete(self) -> bool:
        """是否可以删除（检查关联关系）"""
        # 已上线的模块不能删除
        if self.status.is_online:
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
            "module_code": self.module_code,
            "module_name": self.module_name,
            "module_description": self.module_description,
            "owner": self.owner,
            "status": self.status.value,
            "version": self.version,
            "launch_time": self.launch_time.isoformat() if self.launch_time else None,
            "last_change_time": self.last_change_time.isoformat() if self.last_change_time else None,
            "parent_module_id": self.parent_module_id,
            "related_plan_id": self.related_plan_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "created_by": self.created_by,
        }
