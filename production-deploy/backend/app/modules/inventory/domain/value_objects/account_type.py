"""
账号类型值对象
"""
from enum import Enum
from dataclasses import dataclass


class AccountTypeEnum(Enum):
    """账号类型枚举"""
    SYSTEM = "system"
    SOFTWARE = "software"


@dataclass(frozen=True)
class AccountType:
    """
    账号类型值对象
    
    类型说明：
    - system: 系统账号（操作系统级账号）
    - software: 软件账号（应用/软件级账号）
    """
    value: str
    
    VALID_TYPES = {"system", "software"}
    
    def __post_init__(self):
        if self.value not in self.VALID_TYPES:
            raise ValueError(f"Invalid account type: {self.value}")
    
    @classmethod
    def system(cls) -> "AccountType":
        return cls("system")
    
    @classmethod
    def software(cls) -> "AccountType":
        return cls("software")
    
    @property
    def display_name(self) -> str:
        """获取显示名称"""
        mapping = {
            "system": "系统账号",
            "software": "软件账号",
        }
        return mapping.get(self.value, self.value)
    
    def __str__(self) -> str:
        return self.value
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AccountType):
            return False
        return self.value == other.value
    
    def __hash__(self) -> int:
        return hash(self.value)
