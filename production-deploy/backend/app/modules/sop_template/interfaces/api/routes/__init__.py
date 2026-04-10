"""
SOP 模板引擎 - API 路由
"""
from fastapi import APIRouter

from .sop_template_routes import router as sop_template_router
from .audit_matrix_routes import router as audit_matrix_router

# 创建聚合路由
router = APIRouter()
router.include_router(sop_template_router)
router.include_router(audit_matrix_router)

__all__ = [
    'router',
    'sop_template_router',
    'audit_matrix_router',
]
