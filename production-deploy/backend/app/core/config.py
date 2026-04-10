"""
全局配置管理
集中管理应用的所有配置项
"""
import os
from pathlib import Path
from typing import List


class Settings:
    """
    应用配置类
    
    支持从环境变量读取配置，提供默认值
    """
    
    # 应用信息
    APP_NAME: str = "OpsPilot"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "准入验收与审计管理系统"
    
    # 运行环境
    ENV: str = os.getenv("ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    # 数据库配置
    _db_url = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{Path(__file__).parent.parent.parent / 'data' / 'app.db'}"
    )
    # 展开 ~ 为用户主目录
    DATABASE_URL: str = os.path.expanduser(_db_url)
    
    # JWT配置
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120"))
    ALGORITHM: str = "HS256"
    
    # CORS配置 - 支持本地开发和生产环境
    # 同域部署：前后端共享同一域名，浏览器不会触发跨域检查
    # 跨域部署：需要将前端域名添加到列表中
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        # Serv00 生产环境域名（同域部署时使用同一域名）
        "https://your-domain.serv00.com",
    ]
    
    # 文件上传配置
    _upload_dir = os.getenv("UPLOAD_DIR")
    if _upload_dir:
        # 展开 ~ 并转换为 Path
        UPLOAD_DIR: Path = Path(os.path.expanduser(_upload_dir))
    else:
        UPLOAD_DIR: Path = Path(__file__).parent.parent.parent / "uploads"
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB
    
    # 分页配置
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    def __init__(self):
        """初始化配置"""
        # 确保上传目录存在
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        
        # 从环境变量读取CORS（如果存在）
        cors_env = os.getenv("CORS_ORIGINS")
        if cors_env:
            self.CORS_ORIGINS = [origin.strip() for origin in cors_env.split(",")]


# 全局配置实例
settings = Settings()
