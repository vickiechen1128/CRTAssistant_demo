"""
用户模型
定义系统用户的基本信息和角色
"""

from sqlalchemy import Column, Integer, String, Enum, DateTime, func
from sqlalchemy.orm import relationship
from ..database import Base
import enum


class UserRole(str, enum.Enum):
    """用户角色枚举"""
    OPS_MANAGER = "ops_manager"  # 运维经理
    ADMIN = "admin"              # 系统管理员
    DEVELOPER = "developer"      # 开发人员
    SECURITY = "security"        # 安全人员
    VIEWER = "viewer"            # 只读用户


class User(Base):
    """用户表"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), nullable=False)
    real_name = Column(String(50), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.VIEWER)
    department = Column(String(50))
    phone = Column(String(20))
    hashed_password = Column(String(100), nullable=False)
    status = Column(Enum("active", "inactive", name="user_status"), default="active")
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # 关联关系
    created_tasks = relationship("AdmissionTask", foreign_keys="AdmissionTask.creator_id", back_populates="creator")
    managed_tasks = relationship("AdmissionTask", foreign_keys="AdmissionTask.manager_id", back_populates="manager")
    assigned_checklists = relationship("ChecklistItem", foreign_keys="ChecklistItem.assignee_id", back_populates="assignee")

    # 工作流关联
    workflows = relationship("Workflow", back_populates="creator")
    workflow_instances = relationship("WorkflowInstance", back_populates="creator")
    assigned_work_items = relationship("WorkItemInstance", foreign_keys="WorkItemInstance.assignee_id", back_populates="assignee")
    reviewed_work_items = relationship("WorkItemInstance", foreign_keys="WorkItemInstance.reviewer_id", back_populates="reviewer")
    criteria_verifications = relationship("AcceptanceCriteriaResult", back_populates="verifier")

    def __repr__(self):
        return f"<User {self.username}({self.real_name})>"
