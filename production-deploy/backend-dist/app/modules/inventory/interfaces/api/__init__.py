"""
台账管理模块 - API接口层
"""
from .routes import (
    inventory_router,
    function_module_router,
    lifecycle_log_router,
)

__all__ = [
    'inventory_router',
    'function_module_router',
    'lifecycle_log_router',
]
