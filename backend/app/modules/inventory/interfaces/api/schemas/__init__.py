"""
台账管理模块API Schemas
Pydantic模型，用于请求和响应验证
"""
from .inventory_schemas import (
    # 功能模块
    FunctionModuleSchema,
    # 应用系统
    ApplicationCreateSchema,
    ApplicationUpdateSchema,
    ApplicationResponseSchema,
    # 云资源
    CloudResourceCreateSchema,
    CloudResourceUpdateSchema,
    CloudResourceResponseSchema,
    # 账号
    AccountCreateSchema,
    AccountUpdateSchema,
    AccountResponseSchema,
    AccountExtendValiditySchema,
    # 通用
    PlanLinkSchema,
    PaginationSchema,
    InventorySummarySchema,
    MessageResponseSchema,
)

__all__ = [
    'FunctionModuleSchema',
    'ApplicationCreateSchema',
    'ApplicationUpdateSchema',
    'ApplicationResponseSchema',
    'CloudResourceCreateSchema',
    'CloudResourceUpdateSchema',
    'CloudResourceResponseSchema',
    'AccountCreateSchema',
    'AccountUpdateSchema',
    'AccountResponseSchema',
    'AccountExtendValiditySchema',
    'PlanLinkSchema',
    'PaginationSchema',
    'InventorySummarySchema',
    'MessageResponseSchema',
]
