"""
FastAPI应用入口
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import os

from . import config
from .database import init_db
from .routers import auth, admission_tasks, checklist_items, inventories, verification, dashboard, deliverables, workflows, workflow_instances

# 初始化数据库（如果不存在）
init_db()

# 创建FastAPI应用
app = FastAPI(
    title="仿真运维经理 API",
    description="业务上线发版前准入管理系统",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理"""
    return JSONResponse(
        status_code=500,
        content={"code": 5000, "message": f"服务器内部错误: {str(exc)}"}
    )


# 健康检查
@app.get("/health")
def health_check():
    """健康检查接口"""
    return {"status": "ok", "message": "服务运行正常"}


# 注册路由
app.include_router(auth.router)
app.include_router(admission_tasks.router)
app.include_router(checklist_items.router)
app.include_router(inventories.router)
app.include_router(verification.router)
app.include_router(dashboard.router)
app.include_router(deliverables.router)
app.include_router(workflows.router)
app.include_router(workflow_instances.router)

# 静态文件服务（文件下载）
if os.path.exists(config.UPLOAD_DIR):
    app.mount("/uploads", StaticFiles(directory=str(config.UPLOAD_DIR)), name="uploads")


# 初始化默认数据（首次启动）
@app.on_event("startup")
def init_default_data():
    """初始化默认数据"""
    from .database import SessionLocal
    from .models.user import User, UserRole
    from .core.security import get_password_hash
    from .services.workflow_service import WorkflowService

    db = SessionLocal()
    try:
        # 检查是否已有用户
        user_count = db.query(User).count()
        if user_count == 0:
            # 创建默认管理员用户
            admin = User(
                username="admin",
                email="admin@example.com",
                real_name="管理员",
                role=UserRole.OPS_MANAGER,
                hashed_password=get_password_hash("admin123"),
                status="active"
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
            print("✅ 默认管理员用户已创建: admin / admin123")

            # 创建预置工作流模板
            workflow_service = WorkflowService(db)
            workflow_service.create_preset_workflows(admin.id)
            print("✅ 预置工作流模板已创建")
    except Exception as e:
        print(f"初始化默认数据失败: {e}")
    finally:
        db.close()
