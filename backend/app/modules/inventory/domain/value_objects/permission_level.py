"""
权限级别值对象
"""
from enum import Enum
from dataclasses import dataclass


class PermissionLevelEnum(Enum):
    """权限级别枚举"""
    ADMIN = "admin"
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"


@dataclass(frozen=True)
class PermissionLevel:
    """
    权限级别值对象
    
    权限级别：
    - admin: 管理员权限
    - read: 只读权限
    - write: 读写权限
    - execute: 执行权限
    """
    value: str
    
    VALID_LEVELS = {"admin", "read", "write", "execute"}
    
    def __post_init__(self):
        if self.value not in self.VALID_LEVELS:
            raise ValueError(f"Invalid permission level: {self.value}")
    
    @classmethod
    def admin(cls) -> "PermissionLevel":
        return cls("admin")
    
    @classmethod
    def read(cls) -> "PermissionLevel":
        return cls("read")
    
    @classmethod
    def write(cls) -> "PermissionLevel":
        return cls("write")
    
    @classmethod
    def execute(cls) -> "PermissionLevel":
        return cls("execute")
    
    @property
    def is_admin(self) -> bool:
        return self.value == "admin"
    
    @property
    def display_name(self) -> str:
        """获取显示名称"""
        mapping = {
            "admin": "管理员",
            "read": "只读",
            "write": "读写",
            "execute": "执行",
        }
        return mapping.get(self.value, self.value)
    
    def __str__(self) -> str:
        return self.value
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PermissionLevel):
            return False
        return self.value == other.value
    
    def __hash__(self) -> int:
        return hash(self.value)
