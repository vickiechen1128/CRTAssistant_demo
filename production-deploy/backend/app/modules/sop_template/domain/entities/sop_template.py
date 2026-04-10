"""
SOP 模板聚合根实体
对应业务规则：模板生命周期、版本控制、发布校验
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import uuid4

from ..value_objects.template_type import TemplateType
from ..value_objects.template_status import TemplateStatus
from ..events.sop_template_events import (
    SOPTemplateCreatedEvent,
    SOPTemplatePublishedEvent,
    SOPTemplateDeprecatedEvent,
    SOPTemplateClonedEvent,
)


@dataclass
class SOPTemplate:
    """
    SOP 模板聚合根实体
    
    核心职责：
    1. 维护模板基本信息和状态
    2. 管理模板版本
    3. 执行发布完整性校验
    4. 生成领域事件
    """
    # 标识
    id: str
    template_id: str  # 业务唯一标识，如 SOP-NEW-001
    
    # 基本信息
    name: str
    template_type: TemplateType
    description: Optional[str] = None
    version: str = "v1.0"
    status: TemplateStatus = field(default_factory=lambda: TemplateStatus.draft())
    
    # 关联配置
    audit_matrix_config_id: Optional[str] = None
    parent_work_items_config: List[Dict] = field(default_factory=list)
    
    # 审计信息
    created_by: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    published_at: Optional[datetime] = None
    deprecated_at: Optional[datetime] = None
    
    # 子实体（流程节点）
    workflow_nodes: List[Any] = field(default_factory=list, repr=False)
    
    # 领域事件
    _domain_events: List[Any] = field(default_factory=list, repr=False)
    
    @classmethod
    def create(
        cls,
        template_id: str,
        name: str,
        template_type: TemplateType,
        created_by: str,
        description: Optional[str] = None,
        audit_matrix_config_id: Optional[str] = None,
        version: str = "v1.0",
    ) -> "SOPTemplate":
        """工厂方法：创建新模板"""
        template = cls(
            id=str(uuid4()),
            template_id=template_id,
            name=name,
            template_type=template_type,
            description=description,
            version=version,
            status=TemplateStatus.draft(),
            audit_matrix_config_id=audit_matrix_config_id,
            created_by=created_by,
        )
        
        # 初始化默认父工作项配置
        template.parent_work_items_config = template_type.default_parent_items
        
        # 发布创建事件
        template._domain_events.append(SOPTemplateCreatedEvent(
            template_id=template_id,
            name=name,
            template_type=template_type.value,
            version=version,
            created_by=created_by,
        ))
        
        return template
    
    def update(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        audit_matrix_config_id: Optional[str] = None,
    ) -> None:
        """更新模板信息（仅草稿状态可编辑）"""
        if not self.status.is_editable:
            raise ValueError(f"Cannot update template in {self.status.value} status")
        
        if name is not None:
            self.name = name
        if description is not None:
            self.description = description
        if audit_matrix_config_id is not None:
            self.audit_matrix_config_id = audit_matrix_config_id
        
        self.updated_at = datetime.utcnow()
    
    def publish(self, published_by: str) -> None:
        """
        发布模板
        
        执行完整性校验：
        1. 至少包含 1 个流程节点
        2. 每个节点下至少包含 1 个父工作项
        """
        if not self.status.can_transition_to(TemplateStatus.active()):
            raise ValueError(f"Cannot publish template in {self.status.value} status")
        
        # 完整性校验
        self._validate_publish()
        
        # 状态变更
        self.status = TemplateStatus.active()
        self.published_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        
        # 发布事件
        self._domain_events.append(SOPTemplatePublishedEvent(
            template_id=self.template_id,
            version=self.version,
            published_by=published_by,
        ))
    
    def deprecate(self, deprecated_by: str, reason: Optional[str] = None) -> None:
        """弃用模板"""
        if not self.status.can_transition_to(TemplateStatus.archived()):
            raise ValueError(f"Cannot deprecate template in {self.status.value} status")
        
        self.status = TemplateStatus.archived()
        self.deprecated_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        
        self._domain_events.append(SOPTemplateDeprecatedEvent(
            template_id=self.template_id,
            version=self.version,
            deprecated_by=deprecated_by,
            reason=reason,
        ))
    
    def clone(self, new_version: str, cloned_by: str) -> "SOPTemplate":
        """
        克隆模板（创建新版本）
        
        克隆规则：
        1. 复制所有基本信息
        2. 状态设为 draft
        3. 版本号更新
        4. 保留原模板的关联关系
        """
        cloned = SOPTemplate(
            id=str(uuid4()),
            template_id=self.template_id,
            name=self.name,
            template_type=self.template_type,
            description=self.description,
            version=new_version,
            status=TemplateStatus.draft(),
            audit_matrix_config_id=self.audit_matrix_config_id,
            parent_work_items_config=self.parent_work_items_config.copy(),
            created_by=cloned_by,
        )
        
        cloned._domain_events.append(SOPTemplateClonedEvent(
            source_template_id=self.template_id,
            source_version=self.version,
            new_version=new_version,
            cloned_by=cloned_by,
        ))
        
        return cloned
    
    def can_delete(self) -> bool:
        """是否可以删除"""
        return self.status.is_editable
    
    def _validate_publish(self) -> None:
        """发布前完整性校验"""
        # 校验 1：至少包含 1 个流程节点
        if not self.workflow_nodes or len(self.workflow_nodes) == 0:
            raise ValueError("模板至少包含1个流程节点")
        
        # 校验 2：每个节点下至少包含 1 个父工作项
        for node in self.workflow_nodes:
            parent_items = [wi for wi in node.work_items if wi.is_parent]
            if not parent_items or len(parent_items) == 0:
                raise ValueError(f"节点'{node.name}'下至少包含1个父工作项")
    
    def get_next_version(self) -> str:
        """计算下一个版本号"""
        try:
            # 解析版本号 v{major}.{minor}
            parts = self.version.lstrip('v').split('.')
            major = int(parts[0])
            minor = int(parts[1]) if len(parts) > 1 else 0
            return f"v{major}.{minor + 1}"
        except (ValueError, IndexError):
            return "v1.0"
    
    def get_domain_events(self) -> List[Any]:
        """获取领域事件并清空"""
        events = self._domain_events.copy()
        self._domain_events.clear()
        return events
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "template_id": self.template_id,
            "name": self.name,
            "template_type": self.template_type.value,
            "template_type_display": self.template_type.display_name,
            "description": self.description,
            "version": self.version,
            "status": self.status.value,
            "status_display": self.status.display_name,
            "audit_matrix_config_id": self.audit_matrix_config_id,
            "parent_work_items_config": self.parent_work_items_config,
            "workflow_nodes_count": len(self.workflow_nodes),
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "deprecated_at": self.deprecated_at.isoformat() if self.deprecated_at else None,
        }
