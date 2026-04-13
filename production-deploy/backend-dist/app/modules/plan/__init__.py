"""
Plan 模块 - 计划管理

提供计划的创建、管理、状态流转等功能
"""
from .interfaces.api.routes.plan_routes import router as plan_router

__all__ = ['plan_router']
