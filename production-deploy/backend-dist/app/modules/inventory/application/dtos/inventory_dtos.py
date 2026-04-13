"""
台账管理模块DTOs
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict, Any


# ==================== 功能模块DTO ====================

@dataclass
class FunctionModuleDTO:
    """功能模块DTO"""
    module_name: str
    launch_time: Optional[str] = None


# ==================== 应用系统DTOs ====================

@dataclass
class CreateApplicationDTO:
    """创建应用系统请求DTO"""
    app_name: str
    business_owner: str
    project_owner: str
    app_description: Optional[str] = None
    hostname: Optional[str] = None
    app_url: Optional[str] = None
    function_modules: Optional[List[FunctionModuleDTO]] = None
    launch_time: Optional[str] = None


@dataclass
class UpdateApplicationDTO:
    """更新应用系统请求DTO"""
    app_description: Optional[str] = None
    hostname: Optional[str] = None
    app_url: Optional[str] = None
    business_owner: Optional[str] = None
    project_owner: Optional[str] = None
    launch_time: Optional[str] = None


@dataclass
class ApplicationResponseDTO:
    """应用系统响应DTO"""
    id: str
    app_name: str
    app_description: Optional[str]
    system_type: Optional[str]
    function_modules: List[Dict[str, Any]]
    hostname: Optional[str]
    app_url: Optional[str]
    business_owner: str
    project_owner: str
    launch_time: Optional[str]
    status: str
    related_plan_ids: List[str]
    created_at: str
    updated_at: str
    created_by: str


# ==================== 云资源DTOs ====================

@dataclass
class CreateCloudResourceDTO:
    """创建云资源请求DTO"""
    app_id: str
    resource_type: str
    resource_name: str
    configuration: Optional[Dict[str, Any]] = None


@dataclass
class UpdateCloudResourceDTO:
    """更新云资源请求DTO"""
    resource_name: Optional[str] = None
    configuration: Optional[Dict[str, Any]] = None


@dataclass
class CloudResourceResponseDTO:
    """云资源响应DTO"""
    id: str
    app_id: str
    resource_type: str
    resource_type_display: str
    resource_name: str
    configuration: Dict[str, Any]
    status: str
    related_plan_ids: List[str]
    created_at: str
    updated_at: str
    created_by: str


# ==================== 账号DTOs ====================

@dataclass
class CreateAccountDTO:
    """创建账号请求DTO"""
    app_id: str
    account_type: str
    account_name: str
    permission_level: str
    holder_name: str
    valid_from: str
    valid_until: str
    password_change_cycle: int = 90


@dataclass
class UpdateAccountDTO:
    """更新账号请求DTO"""
    permission_level: Optional[str] = None
    holder_name: Optional[str] = None
    valid_until: Optional[str] = None
    password_change_cycle: Optional[int] = None


@dataclass
class ExtendValidityDTO:
    """延长有效期请求DTO"""
    days: int


@dataclass
class AccountResponseDTO:
    """账号响应DTO"""
    id: str
    app_id: str
    account_type: str
    account_type_display: str
    account_name: str
    permission_level: str
    permission_level_display: str
    holder_name: str
    valid_from: str
    valid_until: str
    password_change_cycle: int
    last_password_change: Optional[str]
    is_password_expired: bool
    days_until_password_expiry: int
    days_until_expiry: int
    status: str
    related_plan_ids: List[str]
    created_at: str
    updated_at: str
    created_by: str


# ==================== 通用DTOs ====================

@dataclass
class InventorySummaryDTO:
    """台账汇总统计DTO"""
    application_count: int
    cloud_resource_count: int
    account_count: int
    application_status_stats: Dict[str, int]
    resource_type_stats: Dict[str, int]
    expiring_accounts_count: int
    expired_accounts_count: int


@dataclass
class PlanLinkDTO:
    """计划关联DTO"""
    plan_id: str


@dataclass
class PaginationDTO:
    """分页DTO"""
    page: int
    size: int
    total: int
    total_pages: int
    data: List[Any]
