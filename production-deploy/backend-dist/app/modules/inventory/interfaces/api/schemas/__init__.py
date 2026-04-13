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
from .function_module_schemas import (
    FunctionModuleCreateSchema,
    FunctionModuleUpdateSchema,
    UpdateModuleStatusSchema,
    LaunchModuleSchema,
    FunctionModuleResponseSchema,
    FunctionModuleTreeSchema,
    FunctionModuleListResponseSchema,
    FunctionModuleVersionHistorySchema,
    ModuleStatusTransitionSchema,
)
from .lifecycle_log_schemas import (
    LifecycleLogCreateSchema,
    LifecycleLogResponseSchema,
    TimelineItemSchema,
    TimelineFilterSchema,
    TimelineResponseSchema,
    LogTypeInfoSchema,
    LogTypeListSchema,
    LogStatisticsSchema,
    LogListResponseSchema,
)

__all__ = [
    # 原有Schemas
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
    # 功能模块Schemas
    'FunctionModuleCreateSchema',
    'FunctionModuleUpdateSchema',
    'UpdateModuleStatusSchema',
    'LaunchModuleSchema',
    'FunctionModuleResponseSchema',
    'FunctionModuleTreeSchema',
    'FunctionModuleListResponseSchema',
    'FunctionModuleVersionHistorySchema',
    'ModuleStatusTransitionSchema',
    # 生命周期日志Schemas
    'LifecycleLogCreateSchema',
    'LifecycleLogResponseSchema',
    'TimelineItemSchema',
    'TimelineFilterSchema',
    'TimelineResponseSchema',
    'LogTypeInfoSchema',
    'LogTypeListSchema',
    'LogStatisticsSchema',
    'LogListResponseSchema',
]
