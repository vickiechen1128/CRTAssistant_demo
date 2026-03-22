"""
验证模型
定义验证脚本和执行记录
"""

from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey, Text, JSON, func
from sqlalchemy.orm import relationship
from ..database import Base
import enum


class ScriptType(str, enum.Enum):
    """脚本类型枚举"""
    BASH = "bash"
    PYTHON = "python"


class ExecutionStatus(str, enum.Enum):
    """执行状态枚举"""
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"


class VerificationScript(Base):
    """验证脚本表"""
    __tablename__ = "verification_scripts"
    
    id = Column(Integer, primary_key=True, index=True)
    script_name = Column(String(100), nullable=False, unique=True)
    script_type = Column(Enum(ScriptType), nullable=False)
    description = Column(Text)
    content = Column(Text, nullable=False)  # 脚本内容
    version = Column(String(20), default="1.0")
    applicable_os = Column(String(200))  # CentOS 7,8/RHEL 7,8
    parameters = Column(JSON)  # [{"name": "timeout", "type": "int"}]
    timeout_seconds = Column(Integer, default=300)
    
    created_by = Column(Integer, ForeignKey("users.id"))
    status = Column(Enum("active", "inactive", name="script_status"), default="active")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # 关联关系
    creator = relationship("User")
    records = relationship("VerificationRecord", back_populates="script")
    
    def __repr__(self):
        return f"<VerificationScript {self.script_name}>"


class VerificationRecord(Base):
    """验证执行记录表"""
    __tablename__ = "verification_records"
    
    id = Column(Integer, primary_key=True, index=True)
    execution_id = Column(String(50), unique=True, nullable=False, index=True)  # exec_20240320160000
    
    task_id = Column(Integer, ForeignKey("admission_tasks.id"), nullable=False, index=True)
    checklist_item_id = Column(Integer, ForeignKey("checklist_items.id"), index=True)
    script_id = Column(Integer, ForeignKey("verification_scripts.id"), nullable=False)
    executor_id = Column(Integer, ForeignKey("users.id"))
    
    target_server = Column(String(100), nullable=False)
    status = Column(Enum(ExecutionStatus), nullable=False)
    
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    duration_seconds = Column(Integer)
    
    result_summary = Column(JSON)  # {"passed": 8, "failed": 2, "warning": 1}
    result_detail = Column(JSON)  # [{"check_item": "...", "status": "..."}]
    output_log = Column(Text)
    error_log = Column(Text)
    
    created_at = Column(DateTime, server_default=func.now())
    
    # 关联关系
    task = relationship("AdmissionTask", back_populates="verification_records")
    checklist_item = relationship("ChecklistItem", back_populates="verification_records")
    script = relationship("VerificationScript", back_populates="records")
    executor = relationship("User")
    
    def __repr__(self):
        return f"<VerificationRecord {self.execution_id}>"
