"""
计划状态值对象
对应业务规则：状态流转图
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class PlanStatus:
    """
    计划状态值对象
    
    状态说明：
    - DRAFT: 草稿（可编辑）
    - PENDING: 待确认（P0优先级初始状态，需二次确认）
    - IN_PROGRESS: 执行中
    - COMPLETED: 已完成
    - CANCELLED: 已取消
    """
    value: str
    
    VALID_STATUSES = {
        "DRAFT",
        "PENDING",
        "IN_PROGRESS",
        "COMPLETED",
        "CANCELLED"
    }
    
    # 状态流转图
    TRANSITIONS = {
        "DRAFT": {"IN_PROGRESS", "CANCELLED"},
        "PENDING": {"IN_PROGRESS", "CANCELLED"},
        "IN_PROGRESS": {"COMPLETED", "CANCELLED"},
        "COMPLETED": set(),
        "CANCELLED": set(),
    }
    
    def __post_init__(self):
        if self.value not in self.VALID_STATUSES:
            raise ValueError(f"Invalid status: {self.value}")
    
    @classmethod
    def draft(cls) -> "PlanStatus":
        return cls("DRAFT")
    
    @classmethod
    def pending(cls) -> "PlanStatus":
        return cls("PENDING")
    
    @classmethod
    def in_progress(cls) -> "PlanStatus":
        return cls("IN_PROGRESS")
    
    @classmethod
    def completed(cls) -> "PlanStatus":
        return cls("COMPLETED")
    
    @classmethod
    def cancelled(cls) -> "PlanStatus":
        return cls("CANCELLED")
    
    def can_transition_to(self, target_status: "PlanStatus") -> bool:
        return target_status.value in self.TRANSITIONS.get(self.value, set())
    
    @property
    def is_editable(self) -> bool:
        return self.value == "DRAFT"
    
    @property
    def is_deletable(self) -> bool:
        return self.value == "DRAFT"
    
    @property
    def is_cancellable(self) -> bool:
        return self.value in {"DRAFT", "PENDING", "IN_PROGRESS"}
    
    @property
    def is_startable(self) -> bool:
        return self.value in {"DRAFT", "PENDING"}
    
    def __str__(self) -> str:
        return self.value
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PlanStatus):
            return False
        return self.value == other.value
    
    def __hash__(self) -> int:
        return hash(self.value)
