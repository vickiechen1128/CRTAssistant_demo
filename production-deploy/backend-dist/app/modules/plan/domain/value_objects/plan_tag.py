"""
数据标签值对象
对应业务规则：自动生成的业务标签
"""
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class PlanTag:
    """
    数据标签值对象
    
    格式：[分类简码]-[YYYYMMDD]-[序号]
    """
    value: str
    
    def __post_init__(self):
        parts = self.value.split("-")
        if len(parts) != 3:
            raise ValueError(f"Invalid PlanTag format: {self.value}")
    
    @classmethod
    def generate(cls, category_code: str, date: datetime, sequence: int) -> "PlanTag":
        date_str = date.strftime("%Y%m%d")
        return cls(f"{category_code}-{date_str}-{sequence:04d}")
    
    def __str__(self) -> str:
        return self.value
