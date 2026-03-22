"""
准入任务模型
定义准入检查任务的核心信息
"""

import enum

from sqlalchemy import Column, Integer, String, Enum, DateTime, Date, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from ..database import Base


class TaskStatus(str, enum.Enum):
    """任务状态枚举"""
    DRAFT = "draft"                    # 草稿
    IN_PROGRESS = "in_progress"        # 进行中
    PENDING_REVIEW = "pending_review"  # 待审核
    APPROVING = "approving"            # 审批中
    PASSED = "passed"                  # 已通过
    REJECTED = "rejected"              # 已驳回
    CANCELLED = "cancelled"            # 已取消


class AdmissionTask(Base):
    """准入任务表"""
    __tablename__ = "admission_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    task_no = Column(String(32), unique=True, nullable=False, index=True)  # ADM202403200001
    system_name = Column(String(100), nullable=False)
    system_code = Column(String(50))
    version = Column(String(50), nullable=False)
    release_date = Column(Date, nullable=False)
    
    # 关联用户
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    manager_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 关联模板
    template_id = Column(Integer, ForeignKey("checklist_templates.id"))
    
    # 状态和进度
    status = Column(Enum(TaskStatus), default=TaskStatus.DRAFT)
    progress = Column(Integer, default=0)  # 完成进度 0-100
    remark = Column(Text)
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    completed_at = Column(DateTime)
    
    # 关联关系
    creator = relationship("User", foreign_keys=[creator_id], back_populates="created_tasks")
    manager = relationship("User", foreign_keys=[manager_id], back_populates="managed_tasks")
    template = relationship("ChecklistTemplate", back_populates="tasks")
    checklist_items = relationship("ChecklistItem", back_populates="task", cascade="all, delete-orphan")
    inventories = relationship("Inventory", back_populates="task", cascade="all, delete-orphan")
    verification_records = relationship("VerificationRecord", back_populates="task")
    workflow_instances = relationship("WorkflowInstance", back_populates="task")

    def __repr__(self):
        return f"<AdmissionTask {self.task_no}: {self.system_name}>"
