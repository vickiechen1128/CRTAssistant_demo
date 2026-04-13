"""
数据库连接管理（合并原 database.py 和 db.py）
提供SQLAlchemy引擎、会话管理和数据库初始化
"""
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base, Session

from .config import settings


# ============== SQLAlchemy 核心组件 ==============

# 创建引擎
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {},
    echo=settings.DEBUG,
    pool_pre_ping=True,
)

# 会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 模型基类
Base = declarative_base()


# ============== SQLite 外键支持 ==============

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """启用SQLite外键约束"""
    if settings.DATABASE_URL.startswith("sqlite"):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


# ============== 依赖注入函数 ==============

def get_db() -> Generator[Session, None, None]:
    """
    获取数据库会话（FastAPI依赖注入使用）
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============== 上下文管理器 ==============

@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    数据库会话上下文管理器
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# ============== 数据库初始化 ==============

def init_db() -> None:
    """
    初始化数据库，创建所有表
    """
    # 确保数据库目录存在（对于 SQLite）
    if settings.DATABASE_URL.startswith("sqlite"):
        import os
        # 提取数据库文件路径
        db_path = settings.DATABASE_URL.replace("sqlite:///", "")
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            if settings.DEBUG:
                print(f"📁 创建数据库目录: {db_dir}")
    
    # 延迟导入模型
    try:
        from app.modules.plan.infrastructure.persistence.models import plan_model
    except ImportError:
        pass
    
    try:
        from app.modules.sop_template.infrastructure.persistence.models import (
            sop_template_model,
            audit_matrix_model,
        )
    except ImportError:
        pass
    
    # 导入台账管理模块模型
    try:
        from app.modules.inventory.infrastructure.persistence.models import (
            inventory_model,
            function_module_model,
            lifecycle_log_model,
        )
    except ImportError:
        pass
    
    Base.metadata.create_all(bind=engine)
    
    if settings.DEBUG:
        print(f"✅ 数据库初始化完成: {settings.DATABASE_URL}")
