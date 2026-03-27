"""
审核等级值对象
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class AuditLevel:
    """
    审核等级值对象
    
    - normal: 普通项，可配置抽检比例
    - critical: 关键项，必须100%审核
    """
    value: str
    
    VALID_LEVELS = {
        "normal",
        "critical"
    }
    
    def __post_init__(self):
        if self.value not in self.VALID_LEVELS:
            raise ValueError(f"Invalid audit level: {self.value}")
    
    @classmethod
    def normal(cls) -> "AuditLevel":
        return cls("normal")
    
    @classmethod
    def critical(cls) -> "AuditLevel":
        return cls("critical")
    
    @property
    def display_name(self) -> str:
        """获取显示名称"""
        mapping = {
            "normal": "普通项",
            "critical": "关键项",
        }
        return mapping.get(self.value, self.value)
    
    @property
    def color(self) -> str:
        """获取等级颜色"""
        mapping = {
            "normal": "blue",
            "critical": "red",
        }
        return mapping.get(self.value, "default")
    
    @property
    def default_sampling_ratio(self) -> float:
        """默认抽检比例"""
        return 0.3 if self.value == "normal" else 1.0
    
    @property
    def requires_full_audit(self) -> bool:
        """是否需要全量审核"""
        return self.value == "critical"
    
    def __str__(self) -> str:
        return self.value
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AuditLevel):
            return False
        return self.value == other.value
    
    def __hash__(self) -> int:
        return hash(self.value)
