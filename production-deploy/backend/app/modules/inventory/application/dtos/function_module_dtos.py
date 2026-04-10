"""
功能模块DTOs
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any


@dataclass
class CreateFunctionModuleDTO:
    """创建功能模块请求DTO"""
    module_code: str
    module_name: str
    version: str = "1.0.0"
    parent_module_id: Optional[str] = None
    related_plan_id: Optional[str] = None
    description: Optional[str] = None


@dataclass
class UpdateFunctionModuleDTO:
    """更新功能模块请求DTO"""
    module_name: Optional[str] = None
    description: Optional[str] = None
    parent_module_id: Optional[str] = None


@dataclass
class UpdateModuleStatusDTO:
    """更新功能模块状态请求DTO"""
    status: str  # draft/developing/testing/online/offline
    operator: str = ""


@dataclass
class LaunchModuleDTO:
    """上线功能模块请求DTO"""
    plan_id: str
    operator: str = ""


@dataclass
class FunctionModuleResponseDTO:
    """功能模块响应DTO"""
    id: str
    app_id: str
    module_code: str
    module_name: str
    version: str
    status: str
    status_display: str
    parent_module_id: Optional[str]
    related_plan_id: Optional[str]
    launch_time: Optional[str]
    description: Optional[str]
    child_count: int
    created_at: str
    updated_at: str


@dataclass
class FunctionModuleTreeDTO:
    """功能模块树形DTO"""
    id: str
    module_code: str
    module_name: str
    version: str
    status: str
    status_display: str
    children: List['FunctionModuleTreeDTO'] = field(default_factory=list)


@dataclass
class FunctionModuleVersionHistoryDTO:
    """功能模块版本历史DTO"""
    versions: List[FunctionModuleResponseDTO]
