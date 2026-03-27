"""
台账管理模块 (Inventory Management)
模块编号: Module_02

本模块是OpsPilot平台的基础数据层，管理应用系统、云服务资源、账号等核心资产信息。
台账数据与计划深度关联，为计划的范围选择和工作项生成提供数据支撑。

功能范围：
- 应用系统台账管理
- 云服务资源台账管理（IAAS+PAAS）
- 系统及软件账号台账管理
- 计划标签关联
"""

from .application.inventory_service import InventoryService
from .domain.entities import Application, CloudResource, Account
from .interfaces.api.routes import router

__all__ = [
    'InventoryService',
    'Application',
    'CloudResource',
    'Account',
    'router',
]
