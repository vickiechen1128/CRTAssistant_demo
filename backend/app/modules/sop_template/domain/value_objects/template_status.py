"""
SOP 模板状态值对象
"""
from dataclasses import dataclass, field
from typing import Set, Dict


@dataclass(frozen=True)
class TemplateStatus:
    """
    SOP 模板状态值对象

    状态流转：
    - draft: 草稿状态，可编辑所有字段
    - active: 活跃状态，可被计划引用
    - archived: 归档状态，只读访问

    流转规则：
    - draft → active (发布)
    - active → archived (弃用)
    - active → draft (克隆为新版本)
    """
    value: str

    VALID_STATUSES = {
        "draft",
        "active",
        "archived"
    }

    # 状态流转图
    TRANSITIONS: Dict[str, Set[str]] = field(default_factory=lambda: {
        "draft": {"active"},
        "active": {"archived"},
        "archived": set(),
    })
    
    def __post_init__(self):
        if self.value not in self.VALID_STATUSES:
            raise ValueError(f"Invalid template status: {self.value}")
    
    @classmethod
    def draft(cls) -> "TemplateStatus":
        return cls("draft")
    
    @classmethod
    def active(cls) -> "TemplateStatus":
        return cls("active")
    
    @classmethod
    def archived(cls) -> "TemplateStatus":
        return cls("archived")
    
    def can_transition_to(self, new_status: "TemplateStatus") -> bool:
        """检查是否可以流转到指定状态"""
        return new_status.value in self.TRANSITIONS.get(self.value, set())
    
    @property
    def is_editable(self) -> bool:
        """是否可编辑"""
        return self.value == "draft"
    
    @property
    def is_usable(self) -> bool:
        """是否可以被计划引用"""
        return self.value == "active"
    
    @property
    def is_readonly(self) -> bool:
        """是否只读"""
        return self.value in {"active", "archived"}
    
    @property
    def display_name(self) -> str:
        """获取显示名称"""
        mapping = {
            "draft": "草稿",
            "active": "已发布",
            "archived": "已归档",
        }
        return mapping.get(self.value, self.value)
    
    @property
    def color(self) -> str:
        """获取状态颜色（用于前端展示）"""
        mapping = {
            "draft": "default",
            "active": "success",
            "archived": "default",
        }
        return mapping.get(self.value, "default")
    
    def __str__(self) -> str:
        return self.value
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TemplateStatus):
            return False
        return self.value == other.value
    
    def __hash__(self) -> int:
        return hash(self.value)
