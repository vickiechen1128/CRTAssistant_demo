"""
数据库连接管理
提供SQLAlchemy引擎和会话管理
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from . import config

# 创建引擎
# check_same_thread=False 允许多线程使用SQLite
engine = create_engine(
    config.DATABASE_URL,
    connect_args={"check_same_thread": False} if config.DATABASE_URL.startswith("sqlite") else {},
    echo=False,  # 生产环境设为False
)

# 会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 模型基类
Base = declarative_base()

# SQLite外键支持
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """启用SQLite外键约束"""
    if config.DATABASE_URL.startswith("sqlite"):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def get_db():
    """
    获取数据库会话（依赖注入使用）
    用法：
        from fastapi import Depends
        db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """初始化数据库，创建所有表"""
    # 延迟导入模型，避免循环依赖
    from . import models
    Base.metadata.create_all(bind=engine)
