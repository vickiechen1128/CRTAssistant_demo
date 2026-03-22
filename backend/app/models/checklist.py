"""
检查清单模型
定义检查清单模板和任务实例化的检查项
"""

from sqlalchemy import Column, Integer, String, Enum, DateTime, Date, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from ..database import Base
import enum


class ControlDimension(str, enum.Enum):
    """管控维度枚举"""
    INVENTORY = "inventory"      # 台账收集
    BASELINE = "baseline"        # 系统基线
    DEPLOYMENT = "deployment"    # 软件部署
    SECURITY = "security"        # 系统安全
    MONITORING = "monitoring"    # 监控告警


class ChecklistItemStatus(str, enum.Enum):
    """检查项状态枚举"""
    PENDING = "pending"              # 未开始
    IN_PROGRESS = "in_progress"      # 进行中
    PENDING_REVIEW = "pending_review" # 待审核
    PASSED = "passed"                # 已通过
    REJECTED = "rejected"            # 已驳回
    NA = "na"                        # 不适用


class VerificationMethod(str, enum.Enum):
    """验证方式枚举"""
    MANUAL = "manual"      # 人工确认
    SCRIPT = "script"      # 脚本验证
    UPLOAD = "upload"      # 交付物上传


class ChecklistTemplate(Base):
    """检查清单模板表"""
    __tablename__ = "checklist_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)  # web_app/api_service/...
    description = Column(Text)
    is_default = Column(Enum("true", "false", name="bool_enum"), default="false")
    status = Column(Enum("active", "inactive", name="template_status"), default="active")
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.now())
    
    # 关联关系
    items = relationship("ChecklistTemplateItem", back_populates="template", cascade="all, delete-orphan")
    tasks = relationship("AdmissionTask", back_populates="template")


class ChecklistTemplateItem(Base):
    """检查清单模板项表"""
    __tablename__ = "checklist_template_items"
    
    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("checklist_templates.id"), nullable=False)
    control_dimension = Column(Enum(ControlDimension), nullable=False)
    category = Column(String(50), nullable=False)
    item_name = Column(String(200), nullable=False)
    description = Column(Text)
    acceptance_criteria = Column(Text)
    deliverable_types = Column(String(200))  # manual,script,log 逗号分隔
    verification_method = Column(Enum(VerificationMethod), default=VerificationMethod.MANUAL)
    script_id = Column(Integer, ForeignKey("verification_scripts.id"))
    sort_order = Column(Integer, default=0)
    is_required = Column(Enum("true", "false", name="bool_enum"), default="true")
    created_at = Column(DateTime, server_default=func.now())
    
    # 关联关系
    template = relationship("ChecklistTemplate", back_populates="items")
    script = relationship("VerificationScript")


class ChecklistItem(Base):
    """检查清单项表（任务实例化后的检查项）"""
    __tablename__ = "checklist_items"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("admission_tasks.id"), nullable=False, index=True)
    template_item_id = Column(Integer, ForeignKey("checklist_template_items.id"))
    
    control_dimension = Column(Enum(ControlDimension), nullable=False)
    category = Column(String(50), nullable=False)
    item_name = Column(String(200), nullable=False)
    description = Column(Text)
    acceptance_criteria = Column(Text)
    
    status = Column(Enum(ChecklistItemStatus), default=ChecklistItemStatus.PENDING)
    assignee_id = Column(Integer, ForeignKey("users.id"))
    verifier_id = Column(Integer, ForeignKey("users.id"))
    verified_at = Column(DateTime)
    verification_remark = Column(Text)
    due_date = Column(Date)
    sort_order = Column(Integer, default=0)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # 关联关系
    task = relationship("AdmissionTask", back_populates="checklist_items")
    assignee = relationship("User", foreign_keys=[assignee_id], back_populates="assigned_checklists")
    verifier = relationship("User", foreign_keys=[verifier_id])
    deliverables = relationship("Deliverable", back_populates="checklist_item", cascade="all, delete-orphan")
    verification_records = relationship("VerificationRecord", back_populates="checklist_item")
