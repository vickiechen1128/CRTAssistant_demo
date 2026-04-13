"""
台账管理模块API路由
"""
from .inventory_routes import router as inventory_router
from .function_module_routes import router as function_module_router
from .lifecycle_log_routes import router as lifecycle_log_router

__all__ = [
    'inventory_router',
    'function_module_router', 
    'lifecycle_log_router',
]
