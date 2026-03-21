from __future__ import annotations

from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from .db import init_db
from .routers import items

# 初始化数据库
init_db()

app = FastAPI(
    title="CRTAssistant API",
    description="Backend API for CRTAssistant Demo",
    version="1.0.0",
)

# CORS 配置 - 允许前端访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # Vite 默认端口
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(items.router)


@app.get("/health")
def health_check() -> dict:
    """健康检查接口"""
    return {"status": "ok", "message": "CRTAssistant API is running"}


# 生产环境：挂载 React 构建产物
frontend_dist = Path(__file__).resolve().parents[2] / "frontend" / "dist"
if frontend_dist.exists():
    @app.get("/", response_class=HTMLResponse)
    def index() -> str:
        index_path = frontend_dist / "index.html"
        return index_path.read_text(encoding="utf-8")
    
    app.mount("/assets", StaticFiles(directory=str(frontend_dist / "assets")), name="assets")
