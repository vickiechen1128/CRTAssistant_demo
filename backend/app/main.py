"""
FastAPI应用入口
极简入口，仅注册路由
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import init_db
from app.core.file_routes import router as file_router
from app.modules.plan import plan_router
from app.modules.inventory import inventory_router, function_module_router, lifecycle_log_router
from app.modules.sop_template.interfaces.api.routes import router as sop_template_router

# 初始化数据库
init_db()

# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION
)

# 健康检查（放在最前面，避免被其他路由捕获）
@app.get("/health")
def health_check():
    """健康检查接口"""
    return {"status": "ok", "message": "服务运行正常"}

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册文件上传路由（无前缀，与前端对齐）
app.include_router(file_router, prefix="/api")

# 注册模块路由
app.include_router(plan_router, prefix="/api/v1")
app.include_router(inventory_router, prefix="/api/v1")
app.include_router(function_module_router, prefix="/api/v1/inventory")
app.include_router(lifecycle_log_router, prefix="/api/v1/inventory")
app.include_router(sop_template_router, prefix="/api/v1")

# 挂载静态文件目录（用于访问上传的文件）
import os
uploads_dir = os.path.join(os.path.dirname(__file__), "..", "uploads")
if os.path.exists(uploads_dir):
    app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

# 挂载前端静态文件目录（生产环境）
# 尝试多个可能的路径
frontend_dist_dir = os.path.join(os.path.dirname(__file__), "..", "..", "production-deploy", "frontend", "dist")
if not os.path.exists(frontend_dist_dir):
    # 部署后的路径：~/opspilot/frontend_dist
    frontend_dist_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend_dist")
if not os.path.exists(frontend_dist_dir):
    # 备用路径：~/opspilot/frontend/dist
    frontend_dist_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend", "dist")

if os.path.exists(frontend_dist_dir):
    from fastapi.responses import FileResponse
    
    # 挂载静态资源目录
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist_dir, "assets")), name="assets")
    
    # 根路径返回 index.html
    @app.get("/")
    async def serve_index():
        return FileResponse(os.path.join(frontend_dist_dir, "index.html"))
    
    # 处理前端路由（返回 index.html 让前端路由处理）
    @app.get("/{path:path}")
    async def serve_spa(path: str):
        # API 路径不走这里（已经被前面的路由处理）
        # 检查是否是静态文件请求
        file_path = os.path.join(frontend_dist_dir, path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        # 否则返回 index.html
        return FileResponse(os.path.join(frontend_dist_dir, "index.html"))



