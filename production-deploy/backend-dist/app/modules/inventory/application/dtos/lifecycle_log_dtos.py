"""
生命周期日志DTOs
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any


@dataclass
class CreateLifecycleLogDTO:
    """创建生命周期日志请求DTO"""
    log_type: str
    event_title: str
    app_id: str = ""
    description: Optional[str] = None
    before_data: Optional[Dict[str, Any]] = None
    after_data: Optional[Dict[str, Any]] = None
    related_plan_id: Optional[str] = None
    plan_title: Optional[str] = None
    related_module_id: Optional[str] = None
    operator: str = ""


@dataclass
class LifecycleLogResponseDTO:
    """生命周期日志响应DTO"""
    id: str
    app_id: str
    log_type: str
    log_type_display: str
    event_title: str
    description: Optional[str]
    before_data: Optional[Dict[str, Any]]
    after_data: Optional[Dict[str, Any]]
    related_plan_id: Optional[str]
    plan_title: Optional[str]
    related_module_id: Optional[str]
    operator: Optional[str]
    operation_time: str


@dataclass
class TimelineItemDTO:
    """时间线条目DTO"""
    id: str
    type: str
    type_display: str
    title: str
    description: Optional[str]
    time: str
    operator: Optional[str]
    plan_id: Optional[str]
    plan_title: Optional[str]
    module_id: Optional[str]
    changes: Optional[Dict[str, Any]]
    icon: str
    color: str


@dataclass
class TimelineResponseDTO:
    """时间线响应DTO"""
    items: List[TimelineItemDTO]
    total: int


@dataclass
class TimelineFilterDTO:
    """时间线筛选DTO"""
    log_type: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    limit: int = 100


@dataclass
class LogTypeInfoDTO:
    """日志类型信息DTO"""
    value: str
    label: str
    description: str
    icon: str
    color: str


@dataclass
class LogStatisticsDTO:
    """日志统计DTO"""
    total_count: int
    type_distribution: Dict[str, int]
    monthly_trend: List[Dict[str, Any]]
