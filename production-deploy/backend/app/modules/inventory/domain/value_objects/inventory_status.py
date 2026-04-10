"""
台账状态值对象
"""
from enum import Enum
from dataclasses import dataclass


class InventoryStatusEnum(Enum):
    """台账状态枚举"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"
    EXPIRED = "expired"  # 主要用于账号


@dataclass(frozen=True)
class InventoryStatus:
    """
    台账状态值对象
    
    状态说明：
    - active: 活跃状态，可正常关联计划
    - inactive: 停用状态，不可关联新计划
    - archived: 归档状态，只读访问
    """
    value: str
    
    VALID_STATUSES = {"active", "inactive", "archived", "expired"}
    
    def __post_init__(self):
        if self.value not in self.VALID_STATUSES:
            raise ValueError(f"Invalid inventory status: {self.value}")
    
    @classmethod
    def active(cls) -> "InventoryStatus":
        return cls("active")
    
    @classmethod
    def inactive(cls) -> "InventoryStatus":
        return cls("inactive")
    
    @classmethod
    def archived(cls) -> "InventoryStatus":
        return cls("archived")
    
    @classmethod
    def expired(cls) -> "InventoryStatus":
        return cls("expired")
    
    @property
    def is_active(self) -> bool:
        return self.value == "active"
    
    @property
    def is_editable(self) -> bool:
        """是否可编辑"""
        return self.value in {"active", "inactive"}
    
    @property
    def can_associate_plan(self) -> bool:
        """是否可以关联新计划"""
        return self.value == "active"
    
    def __str__(self) -> str:
        return self.value
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, InventoryStatus):
            return False
        return self.value == other.value
    
    def __hash__(self) -> int:
        return hash(self.value)
