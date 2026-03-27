"""
计划ID值对象
对应业务规则：PLAN-YYYYMMDD-XXXX格式
"""
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class PlanId:
    """
    计划ID值对象
    
    格式：PLAN-YYYYMMDD-XXXX
    """
    value: str
    
    def __post_init__(self):
        parts = self.value.split("-")
        if len(parts) != 3:
            raise ValueError(f"Invalid PlanId format: {self.value}")
        if parts[0] != "PLAN":
            raise ValueError(f"PlanId must start with 'PLAN': {self.value}")
    
    @classmethod
    def generate(cls, date: datetime, sequence: int) -> "PlanId":
        date_str = date.strftime("%Y%m%d")
        sequence_str = f"{sequence:04d}"
        return cls(f"PLAN-{date_str}-{sequence_str}")
    
    @property
    def date_part(self) -> str:
        return self.value.split("-")[1]
    
    @property
    def sequence_number(self) -> int:
        return int(self.value.split("-")[2])
    
    def __str__(self) -> str:
        return self.value
