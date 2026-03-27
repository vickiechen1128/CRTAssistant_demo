"""
台账管理模块API Schemas
"""
from datetime import datetime
from typing import Optional, List, Dict, Any, Union

from pydantic import BaseModel, Field, validator


# ==================== 功能模块Schema ====================

class FunctionModuleSchema(BaseModel):
    """功能模块Schema"""
    module_name: str = Field(..., max_length=50, description="模块名称")
    launch_time: Optional[str] = Field(None, description="上线时间(ISO格式)")


# ==================== 应用系统Schemas ====================

class ApplicationCreateSchema(BaseModel):
    """创建应用系统请求Schema"""
    app_name: str = Field(..., max_length=100, description="应用名称")
    business_owner: str = Field(..., max_length=50, description="业务负责人")
    project_owner: str = Field(..., max_length=50, description="项目负责人")
    app_description: Optional[str] = Field(None, description="应用描述")
    hostname: Optional[str] = Field(None, max_length=100, description="主机名")
    app_url: Optional[str] = Field(None, max_length=500, description="应用URL")
    function_modules: Optional[List[Union[str, FunctionModuleSchema]]] = Field(None, description="功能模块列表")
    launch_time: Optional[str] = Field(None, description="上线时间(ISO格式)")


class ApplicationUpdateSchema(BaseModel):
    """更新应用系统请求Schema"""
    app_description: Optional[str] = Field(None, description="应用描述")
    hostname: Optional[str] = Field(None, max_length=100, description="主机名")
    app_url: Optional[str] = Field(None, max_length=500, description="应用URL")
    business_owner: Optional[str] = Field(None, max_length=50, description="业务负责人")
    project_owner: Optional[str] = Field(None, max_length=50, description="项目负责人")
    launch_time: Optional[str] = Field(None, description="上线时间(ISO格式)")


class ApplicationResponseSchema(BaseModel):
    """应用系统响应Schema"""
    id: str
    app_name: str
    app_description: Optional[str]
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

    class Config:
        from_attributes = True


# ==================== 云资源Schemas ====================

class CloudResourceCreateSchema(BaseModel):
    """创建云资源请求Schema"""
    app_id: str = Field(..., description="关联应用ID")
    resource_type: str = Field(
        ...,
        description="资源类型",
        pattern="^(compute|network|storage|backup|middleware|database|cache|message_queue)$"
    )
    resource_name: str = Field(..., max_length=100, description="资源名称")
    configuration: Optional[Dict[str, Any]] = Field(default_factory=dict, description="资源配置")


class CloudResourceUpdateSchema(BaseModel):
    """更新云资源请求Schema"""
    resource_name: Optional[str] = Field(None, max_length=100, description="资源名称")
    configuration: Optional[Dict[str, Any]] = Field(None, description="资源配置")


class CloudResourceResponseSchema(BaseModel):
    """云资源响应Schema"""
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

    class Config:
        from_attributes = True


# ==================== 账号Schemas ====================

class AccountCreateSchema(BaseModel):
    """创建账号请求Schema"""
    app_id: str = Field(..., description="关联应用ID")
    account_type: str = Field(
        ...,
        description="账号类型",
        pattern="^(system|software)$"
    )
    account_name: str = Field(..., max_length=100, description="账号名称")
    permission_level: str = Field(
        ...,
        description="权限级别",
        pattern="^(admin|read|write|execute)$"
    )
    holder_name: str = Field(..., max_length=50, description="持有人")
    valid_from: str = Field(..., description="有效期开始(ISO格式)")
    valid_until: str = Field(..., description="有效期结束(ISO格式)")
    password_change_cycle: int = Field(90, ge=1, le=365, description="密码修改周期(天)")
    
    @validator('valid_until')
    def validate_validity_period(cls, v, values):
        if 'valid_from' in values:
            from_date = datetime.fromisoformat(values['valid_from'].replace('Z', '+00:00'))
            to_date = datetime.fromisoformat(v.replace('Z', '+00:00'))
            if to_date <= from_date:
                raise ValueError('valid_until must be later than valid_from')
            if (to_date - from_date).days > 3650:
                raise ValueError('validity period cannot exceed 10 years')
        return v


class AccountUpdateSchema(BaseModel):
    """更新账号请求Schema"""
    permission_level: Optional[str] = Field(
        None,
        description="权限级别",
        pattern="^(admin|read|write|execute)$"
    )
    holder_name: Optional[str] = Field(None, max_length=50, description="持有人")
    valid_until: Optional[str] = Field(None, description="有效期结束(ISO格式)")
    password_change_cycle: Optional[int] = Field(None, ge=1, le=365, description="密码修改周期(天)")


class AccountResponseSchema(BaseModel):
    """账号响应Schema"""
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

    class Config:
        from_attributes = True


class AccountExtendValiditySchema(BaseModel):
    """延长账号有效期请求Schema"""
    days: int = Field(..., ge=1, le=365, description="延长天数")


# ==================== 通用Schemas ====================

class PlanLinkSchema(BaseModel):
    """计划关联Schema"""
    plan_id: str = Field(..., description="计划ID")


class PaginationSchema(BaseModel):
    """分页响应Schema"""
    page: int
    size: int
    total: int
    total_pages: int


class InventorySummarySchema(BaseModel):
    """台账汇总统计Schema"""
    application_count: int
    cloud_resource_count: int
    account_count: int
    application_status_stats: Dict[str, int]
    resource_type_stats: Dict[str, int]
    expiring_accounts_count: int
    expired_accounts_count: int


class MessageResponseSchema(BaseModel):
    """消息响应Schema"""
    message: str
    data: Optional[Any] = None


class PaginatedApplicationResponseSchema(PaginationSchema):
    """分页应用系统响应"""
    data: List[ApplicationResponseSchema]


class PaginatedCloudResourceResponseSchema(PaginationSchema):
    """分页云资源响应"""
    data: List[CloudResourceResponseSchema]


class PaginatedAccountResponseSchema(PaginationSchema):
    """分页账号响应"""
    data: List[AccountResponseSchema]
