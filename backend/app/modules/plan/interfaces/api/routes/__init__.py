"""路由模块"""
from .plan_routes import router as plan_router
from .sync_routes import router as sync_router

# 主路由
router = plan_router

__all__ = ['router', 'plan_router', 'sync_router']
