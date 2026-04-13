"""
计划优先级值对象
对应业务规则：P0-P3，影响初始状态和二次确认
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Priority:
    """
    计划优先级值对象
    
    优先级说明：
    - P0: 最高优先级，需要二次确认，初始状态为 PENDING
    - P1-P3: 普通优先级，初始状态为 DRAFT
    """
    level: int
    
    VALID_LEVELS = {0, 1, 2, 3}
    
    def __post_init__(self):
        if self.level not in self.VALID_LEVELS:
            raise ValueError(f"Invalid priority level: {self.level}, must be 0-3")
    
    @classmethod
    def p0(cls) -> "Priority":
        """最高优先级"""
        return cls(0)
    
    @classmethod
    def p1(cls) -> "Priority":
        """高优先级"""
        return cls(1)
    
    @classmethod
    def p2(cls) -> "Priority":
        """中优先级"""
        return cls(2)
    
    @classmethod
    def p3(cls) -> "Priority":
        """低优先级"""
        return cls(3)
    
    @classmethod
    def from_string(cls, value: str) -> "Priority":
        """从字符串创建（如 'P0', 'P1'）"""
        if not value.startswith("P"):
            raise ValueError(f"Invalid priority format: {value}")
        try:
            level = int(value[1:])
            return cls(level)
        except (ValueError, IndexError):
            raise ValueError(f"Invalid priority format: {value}")
    
    @property
    def is_p0(self) -> bool:
        """是否为最高优先级"""
        return self.level == 0
    
    @property
    def requires_confirmation(self) -> bool:
        """是否需要二次确认"""
        return self.level == 0
    
    @property
    def initial_status(self) -> str:
        """根据优先级确定初始状态"""
        return "PENDING" if self.level == 0 else "DRAFT"
    
    @property
    def label(self) -> str:
        """获取优先级标签"""
        mapping = {
            0: "P0 - 最高优先级",
            1: "P1 - 高优先级",
            2: "P2 - 中优先级",
            3: "P3 - 低优先级",
        }
        return mapping.get(self.level, f"P{self.level}")
    
    def __str__(self) -> str:
        return f"P{self.level}"
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Priority):
            return False
        return self.level == other.level
    
    def __hash__(self) -> int:
        return hash(self.level)
    
    def __lt__(self, other: "Priority") -> bool:
        return self.level < other.level
    
    def __le__(self, other: "Priority") -> bool:
        return self.level <= other.level
    
    def __gt__(self, other: "Priority") -> bool:
        return self.level > other.level
    
    def __ge__(self, other: "Priority") -> bool:
        return self.level >= other.level
