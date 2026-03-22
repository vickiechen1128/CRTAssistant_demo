"""
配置管理模块
集中管理应用配置，支持环境变量覆盖
"""

import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = BASE_DIR / "uploads"

# 确保目录存在
DATA_DIR.mkdir(exist_ok=True)
UPLOAD_DIR.mkdir(exist_ok=True)

# 数据库配置
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR}/app.db")

# JWT配置
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120"))

# 文件上传配置
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_EXTENSIONS = {
    '.xlsx', '.xls', '.doc', '.docx', '.pdf', 
    '.txt', '.sh', '.py', '.log'
}

# 验证脚本执行配置
SCRIPT_TIMEOUT = int(os.getenv("SCRIPT_TIMEOUT", "300"))  # 默认5分钟
MAX_CONCURRENT_SCRIPTS = int(os.getenv("MAX_CONCURRENT_SCRIPTS", "5"))

# CORS配置
CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

# 日志配置
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
