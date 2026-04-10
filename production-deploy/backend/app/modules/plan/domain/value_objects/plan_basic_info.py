"""
计划基本信息值对象
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .category import Category
from .priority import Priority
from .template_type import TemplateType


@dataclass(frozen=True)
class PlanBasicInfo:
    """计划基本信息值对象"""
    name: str
    category: Category
    priority: Priority
    planned_start_time: datetime
    planned_end_time: Optional[datetime] = None
    description: Optional[str] = None
    
    def __post_init__(self):
        if not self.name or len(self.name) > 200:
            raise ValueError("Plan name must be between 1 and 200 characters")
        
        if self.planned_end_time and self.planned_end_time <= self.planned_start_time:
            raise ValueError("Planned end time must be after planned start time")
    
    @property
    def template_type(self) -> TemplateType:
        return TemplateType.from_category(self.category.value)
    
    @property
    def duration_days(self) -> Optional[int]:
        if not self.planned_end_time:
            return None
        delta = self.planned_end_time - self.planned_start_time
        return delta.days
    
    def __str__(self) -> str:
        return f"{self.name} ({self.category})"
