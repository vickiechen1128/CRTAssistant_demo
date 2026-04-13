"""
生命周期日志实体
对应数据模型：inventory_lifecycle_logs

用于记录应用系统和功能模块的生命周期事件：
- 系统上线、升级、回滚、下线
- 功能模块上线、变更、下线
- 配置变更、负责人变更、状态变更等
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import uuid4

from ..value_objects.log_type import LogType


@dataclass
class LifecycleLog:
    """
    生命周期日志实体
    
    核心职责：
    1. 记录系统/模块的生命周期事件
    2. 存储变更前后数据快照
    3. 关联计划信息
    4. 支持附件存储
    """
    
    # 标识
    id: str
    
    # 关联对象
    app_id: str  # 关联的应用系统ID
    
    # 日志信息
    log_type: LogType  # 日志类型
    event_title: str  # 事件标题
    
    # 可选字段
    module_id: Optional[str] = None  # 关联的功能模块ID（可选）
    event_description: Optional[str] = None  # 事件详细描述
    
    # 变更数据快照
    before_data: Optional[Dict[str, Any]] = None  # 变更前数据
    after_data: Optional[Dict[str, Any]] = None  # 变更后数据
    
    # 计划关联
    related_plan_id: Optional[str] = None  # 触发此事件的计划ID
    
    # 操作信息
    operator: str = ""  # 操作人
    operation_time: datetime = field(default_factory=datetime.utcnow)
    
    # 附件
    attachments: List[Dict[str, str]] = field(default_factory=list)  # [{name, url}]
    
    # 审计信息
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    @classmethod
    def create(
        cls,
        app_id: str,
        log_type: LogType,
        event_title: str,
        operator: str,
        module_id: Optional[str] = None,
        event_description: Optional[str] = None,
        before_data: Optional[Dict[str, Any]] = None,
        after_data: Optional[Dict[str, Any]] = None,
        related_plan_id: Optional[str] = None,
        attachments: Optional[List[Dict[str, str]]] = None,
        operation_time: Optional[datetime] = None,
    ) -> "LifecycleLog":
        """工厂方法：创建生命周期日志"""
        log_id = str(uuid4())
        
        return cls(
            id=log_id,
            app_id=app_id,
            log_type=log_type,
            event_title=event_title,
            module_id=module_id,
            event_description=event_description,
            before_data=before_data,
            after_data=after_data,
            related_plan_id=related_plan_id,
            operator=operator,
            operation_time=operation_time or datetime.utcnow(),
            attachments=attachments or [],
        )
    
    @classmethod
    def from_module_status_change(
        cls,
        app_id: str,
        module_id: str,
        module_name: str,
        old_status: str,
        new_status: str,
        operator: str,
        related_plan_id: Optional[str] = None,
    ) -> "LifecycleLog":
        """
        从模块状态变更创建日志
        自动生成事件标题
        """
        event_title = f"【状态变更】模块 {module_name} 由 {old_status} 变更为 {new_status}"
        
        return cls.create(
            app_id=app_id,
            log_type=LogType.status_change(),
            event_title=event_title,
            operator=operator,
            module_id=module_id,
            before_data={"status": old_status},
            after_data={"status": new_status},
            related_plan_id=related_plan_id,
        )
    
    @classmethod
    def from_module_version_change(
        cls,
        app_id: str,
        module_id: str,
        module_name: str,
        old_version: str,
        new_version: str,
        operator: str,
        related_plan_id: Optional[str] = None,
    ) -> "LifecycleLog":
        """
        从模块版本变更创建日志
        自动生成事件标题
        """
        event_title = f"【版本变更】模块 {module_name} 由 {old_version} 更新至 {new_version}"
        
        return cls.create(
            app_id=app_id,
            log_type=LogType.module_update(),
            event_title=event_title,
            operator=operator,
            module_id=module_id,
            before_data={"version": old_version},
            after_data={"version": new_version},
            related_plan_id=related_plan_id,
        )
    
    @classmethod
    def from_owner_change(
        cls,
        app_id: str,
        obj_type: str,  # "application" or "module"
        obj_name: str,
        old_owner: str,
        new_owner: str,
        operator: str,
        module_id: Optional[str] = None,
    ) -> "LifecycleLog":
        """
        从负责人变更创建日志
        """
        event_title = f"【负责人变更】{obj_type} {obj_name} 由 {old_owner} 变更为 {new_owner}"
        
        return cls.create(
            app_id=app_id,
            log_type=LogType.owner_change(),
            event_title=event_title,
            operator=operator,
            module_id=module_id,
            before_data={"owner": old_owner},
            after_data={"owner": new_owner},
        )
    
    @classmethod
    def from_system_launch(
        cls,
        app_id: str,
        app_name: str,
        operator: str,
        related_plan_id: str,
    ) -> "LifecycleLog":
        """系统上线日志"""
        event_title = f"【系统上线】{app_name} 正式上线"
        
        return cls.create(
            app_id=app_id,
            log_type=LogType.system_launch(),
            event_title=event_title,
            operator=operator,
            related_plan_id=related_plan_id,
        )
    
    @classmethod
    def from_module_launch(
        cls,
        app_id: str,
        module_id: str,
        module_name: str,
        operator: str,
        related_plan_id: str,
    ) -> "LifecycleLog":
        """功能模块上线日志"""
        event_title = f"【功能上线】{module_name} 正式上线"
        
        return cls.create(
            app_id=app_id,
            log_type=LogType.module_launch(),
            event_title=event_title,
            operator=operator,
            module_id=module_id,
            related_plan_id=related_plan_id,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "app_id": self.app_id,
            "module_id": self.module_id,
            "log_type": self.log_type.value,
            "log_type_label": self.log_type.label,
            "event_title": self.event_title,
            "event_description": self.event_description,
            "before_data": self.before_data,
            "after_data": self.after_data,
            "related_plan_id": self.related_plan_id,
            "operator": self.operator,
            "operation_time": self.operation_time.isoformat() if self.operation_time else None,
            "attachments": self.attachments,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LifecycleLog":
        """从字典创建实体"""
        return cls(
            id=data["id"],
            app_id=data["app_id"],
            log_type=LogType.from_string(data["log_type"]) if isinstance(data["log_type"], str) else data["log_type"],
            event_title=data["event_title"],
            module_id=data.get("module_id"),
            event_description=data.get("event_description"),
            before_data=data.get("before_data"),
            after_data=data.get("after_data"),
            related_plan_id=data.get("related_plan_id"),
            operator=data.get("operator", ""),
            operation_time=datetime.fromisoformat(data["operation_time"]) if data.get("operation_time") else datetime.utcnow(),
            attachments=data.get("attachments", []),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.utcnow(),
        )
