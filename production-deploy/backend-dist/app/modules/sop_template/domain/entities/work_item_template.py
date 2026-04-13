"""
工作项模板实体
支持父子层级结构（自关联）
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import uuid4

from ..value_objects.audit_level import AuditLevel
from ..value_objects.work_item_category import WorkItemCategory


@dataclass
class WorkItemTemplate:
    """
    工作项模板实体
    
    核心特性：
    1. 支持父子层级（通过 parent_template_id 自关联）
    2. 挂载到 SOP 模板和流程节点
    3. 配置交付物、验收标准、执行步骤
    
    parent_template_id 为 None 时表示父工作项（5大类）
    parent_template_id 非 None 时表示子工作项（验收项）
    """
    # 标识
    id: str
    template_id: str  # 业务唯一标识，如 WI-001
    
    # 基本信息
    name: str
    category: WorkItemCategory
    sequence: int = 1
    description: Optional[str] = None
    
    # 审核配置
    audit_level: AuditLevel = field(default_factory=lambda: AuditLevel.normal())
    
    # JSON 配置
    deliverables_config: List[Dict] = field(default_factory=list)
    acceptance_criteria_config: List[Dict] = field(default_factory=list)
    execution_steps_config: List[Dict] = field(default_factory=list)
    
    # 关联（层级结构）
    sop_template_id: str = ""
    workflow_node_id: Optional[str] = None
    parent_template_id: Optional[str] = None  # 自关联，None 表示父工作项
    
    # 子实体（子工作项）
    children: List["WorkItemTemplate"] = field(default_factory=list, repr=False)
    
    # 状态
    status: str = "active"  # active, inactive
    
    # 审计
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    @classmethod
    def create(
        cls,
        template_id: str,
        name: str,
        category: WorkItemCategory,
        sop_template_id: str,
        workflow_node_id: Optional[str] = None,
        parent_template_id: Optional[str] = None,
        sequence: int = 1,
        description: Optional[str] = None,
        audit_level: Optional[AuditLevel] = None,
        deliverables_config: Optional[List[Dict]] = None,
        acceptance_criteria_config: Optional[List[Dict]] = None,
        execution_steps_config: Optional[List[Dict]] = None,
    ) -> "WorkItemTemplate":
        """工厂方法：创建工作项模板"""
        return cls(
            id=str(uuid4()),
            template_id=template_id,
            name=name,
            category=category,
            sequence=sequence,
            description=description,
            audit_level=audit_level or AuditLevel.normal(),
            deliverables_config=deliverables_config or [],
            acceptance_criteria_config=acceptance_criteria_config or [],
            execution_steps_config=execution_steps_config or [],
            sop_template_id=sop_template_id,
            workflow_node_id=workflow_node_id,
            parent_template_id=parent_template_id,
        )
    
    @classmethod
    def create_parent(
        cls,
        template_id: str,
        name: str,
        category: WorkItemCategory,
        sop_template_id: str,
        workflow_node_id: str,
        **kwargs
    ) -> "WorkItemTemplate":
        """创建父工作项"""
        return cls.create(
            template_id=template_id,
            name=name,
            category=category,
            sop_template_id=sop_template_id,
            workflow_node_id=workflow_node_id,
            parent_template_id=None,  # 父工作项无父级
            **kwargs
        )
    
    @classmethod
    def create_child(
        cls,
        template_id: str,
        name: str,
        category: WorkItemCategory,
        sop_template_id: str,
        parent_template_id: str,
        **kwargs
    ) -> "WorkItemTemplate":
        """创建子工作项"""
        return cls.create(
            template_id=template_id,
            name=name,
            category=category,
            sop_template_id=sop_template_id,
            parent_template_id=parent_template_id,  # 指定父级
            **kwargs
        )
    
    @property
    def is_parent(self) -> bool:
        """是否为父工作项"""
        return self.parent_template_id is None
    
    @property
    def is_child(self) -> bool:
        """是否为子工作项"""
        return self.parent_template_id is not None
    
    @property
    def level(self) -> int:
        """获取层级深度（0表示父级）"""
        if self.is_parent:
            return 0
        # 这里简化处理，实际可能需要递归计算
        return 1
    
    def update(
        self,
        name: Optional[str] = None,
        sequence: Optional[int] = None,
        description: Optional[str] = None,
        audit_level: Optional[AuditLevel] = None,
        deliverables_config: Optional[List[Dict]] = None,
        acceptance_criteria_config: Optional[List[Dict]] = None,
        execution_steps_config: Optional[List[Dict]] = None,
    ) -> None:
        """更新工作项信息"""
        if name is not None:
            self.name = name
        if sequence is not None:
            self.sequence = sequence
        if description is not None:
            self.description = description
        if audit_level is not None:
            self.audit_level = audit_level
        if deliverables_config is not None:
            self.deliverables_config = deliverables_config
        if acceptance_criteria_config is not None:
            self.acceptance_criteria_config = acceptance_criteria_config
        if execution_steps_config is not None:
            self.execution_steps_config = execution_steps_config
        
        self.updated_at = datetime.utcnow()
    
    def add_child(self, child: "WorkItemTemplate") -> None:
        """添加子工作项"""
        child.parent_template_id = self.id
        self.children.append(child)
        self.updated_at = datetime.utcnow()
    
    def remove_child(self, child_id: str) -> bool:
        """移除子工作项"""
        for i, child in enumerate(self.children):
            if child.id == child_id:
                del self.children[i]
                self.updated_at = datetime.utcnow()
                return True
        return False
    
    def deactivate(self) -> None:
        """停用工作项"""
        self.status = "inactive"
        self.updated_at = datetime.utcnow()
    
    def activate(self) -> None:
        """激活工作项"""
        self.status = "active"
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "template_id": self.template_id,
            "name": self.name,
            "category": self.category.value,
            "category_display": self.category.display_name,
            "category_icon": self.category.icon,
            "sequence": self.sequence,
            "description": self.description,
            "audit_level": self.audit_level.value,
            "audit_level_display": self.audit_level.display_name,
            "is_parent": self.is_parent,
            "is_child": self.is_child,
            "level": self.level,
            "sop_template_id": self.sop_template_id,
            "workflow_node_id": self.workflow_node_id,
            "parent_template_id": self.parent_template_id,
            "deliverables_config": self.deliverables_config,
            "acceptance_criteria_config": self.acceptance_criteria_config,
            "execution_steps_config": self.execution_steps_config,
            "children": [child.to_dict() for child in self.children],
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def to_tree_dict(self) -> dict:
        """转换为树形结构字典"""
        return {
            "id": self.id,
            "template_id": self.template_id,
            "name": self.name,
            "category": self.category.value,
            "category_display": self.category.display_name,
            "sequence": self.sequence,
            "audit_level": self.audit_level.value,
            "is_parent": self.is_parent,
            "children": [child.to_tree_dict() for child in self.children],
        }
