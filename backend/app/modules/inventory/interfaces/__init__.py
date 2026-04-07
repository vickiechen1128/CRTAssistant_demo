"""
台账管理模块 - 接口层
"""
from .api.routes import (
    inventory_router,
    function_module_router,
    lifecycle_log_router,
)

__all__ = [
    'inventory_router',
    'function_module_router',
    'lifecycle_log_router',
]
