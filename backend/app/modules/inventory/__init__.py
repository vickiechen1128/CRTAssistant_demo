"""
台账管理模块 (Inventory Management)
模块编号: Module_02

本模块是OpsPilot平台的基础数据层，管理应用系统、云服务资源、账号等核心资产信息。
台账数据与计划深度关联，为计划的范围选择和工作项生成提供数据支撑。

功能范围：
- 应用系统台账管理
- 云服务资源台账管理（IAAS+PAAS）
- 系统及软件账号台账管理
- 功能模块管理（独立实体，支持状态工作流）
- 生命周期日志（时间线、双向追溯）
- 计划标签关联
"""

from .application import (
    InventoryService,
    FunctionModuleService,
    LifecycleLogService,
)
from .domain.entities import (
    Application,
    CloudResource,
    Account,
    FunctionModule,
    LifecycleLog,
)
from .interfaces.api.routes import (
    inventory_router,
    function_module_router,
    lifecycle_log_router,
)

__all__ = [
    # 服务
    'InventoryService',
    'FunctionModuleService',
    'LifecycleLogService',
    # 实体
    'Application',
    'CloudResource',
    'Account',
    'FunctionModule',
    'LifecycleLog',
    # 路由
    'inventory_router',
    'function_module_router',
    'lifecycle_log_router',
]
