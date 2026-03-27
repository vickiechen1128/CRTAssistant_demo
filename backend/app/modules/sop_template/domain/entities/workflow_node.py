"""
流程节点实体
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import uuid4


@dataclass
class WorkflowNode:
    """
    流程节点实体
    
    职责：
    1. 定义流程中的一个阶段
    2. 管理准入/准出条件
    3. 关联工作项模板
    4. 配置强制管控规则
    """
    # 标识
    id: str
    node_id: str  # 业务标识，如 NODE-001
    
    # 基本信息
    name: str
    sequence: int
    
    # 条件配置
    entry_conditions: List[Dict] = field(default_factory=list)
    exit_conditions: List[Dict] = field(default_factory=list)
    
    # 强制规则
    mandatory_rules: Dict = field(default_factory=dict)
    
    # 关联
    sop_template_id: str = ""
    
    # 子实体
    work_items: List[Any] = field(default_factory=list, repr=False)
    
    # 审计
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    @classmethod
    def create(
        cls,
        node_id: str,
        name: str,
        sequence: int,
        sop_template_id: str,
        entry_conditions: Optional[List[Dict]] = None,
        exit_conditions: Optional[List[Dict]] = None,
        mandatory_rules: Optional[Dict] = None,
    ) -> "WorkflowNode":
        """工厂方法：创建流程节点"""
        return cls(
            id=str(uuid4()),
            node_id=node_id,
            name=name,
            sequence=sequence,
            sop_template_id=sop_template_id,
            entry_conditions=entry_conditions or [],
            exit_conditions=exit_conditions or [],
            mandatory_rules=mandatory_rules or {
                "deliverable_required": True,
                "audit_required": True,
            },
        )
    
    def update(
        self,
        name: Optional[str] = None,
        sequence: Optional[int] = None,
        entry_conditions: Optional[List[Dict]] = None,
        exit_conditions: Optional[List[Dict]] = None,
        mandatory_rules: Optional[Dict] = None,
    ) -> None:
        """更新节点信息"""
        if name is not None:
            self.name = name
        if sequence is not None:
            self.sequence = sequence
        if entry_conditions is not None:
            self.entry_conditions = entry_conditions
        if exit_conditions is not None:
            self.exit_conditions = exit_conditions
        if mandatory_rules is not None:
            self.mandatory_rules = mandatory_rules
        
        self.updated_at = datetime.utcnow()
    
    def add_work_item(self, work_item: Any) -> None:
        """添加工作项"""
        work_item.workflow_node_id = self.id
        self.work_items.append(work_item)
        self.updated_at = datetime.utcnow()
    
    def remove_work_item(self, work_item_id: str) -> bool:
        """移除工作项"""
        for i, wi in enumerate(self.work_items):
            if wi.id == work_item_id:
                del self.work_items[i]
                self.updated_at = datetime.utcnow()
                return True
        return False
    
    def get_parent_work_items(self) -> List[Any]:
        """获取父工作项列表"""
        return [wi for wi in self.work_items if wi.is_parent]
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "node_id": self.node_id,
            "name": self.name,
            "sequence": self.sequence,
            "entry_conditions": self.entry_conditions,
            "exit_conditions": self.exit_conditions,
            "mandatory_rules": self.mandatory_rules,
            "sop_template_id": self.sop_template_id,
            "work_items": [wi.to_dict() for wi in self.work_items],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
