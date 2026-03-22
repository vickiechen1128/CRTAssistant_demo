from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
import enum


class WorkflowStatus(str, enum.Enum):
    """工作流状态"""
    DRAFT = "draft"           # 草稿
    ACTIVE = "active"         # 启用
    ARCHIVED = "archived"     # 已归档


class WorkItemType(str, enum.Enum):
    """工作项类型"""
    RESOURCE_DELIVERY = "resource_delivery"      # 基础资源标准化交付
    INVENTORY = "inventory"                      # 服务对象台账
    PERMISSION_HANDOVER = "permission_handover"  # 生产环境权限移交
    SECURITY_BASELINE = "security_baseline"      # 安全基线核验
    MONITORING = "monitoring"                    # 监控告警配置确认
    CUSTOM = "custom"                            # 自定义工作项


class WorkItemStatus(str, enum.Enum):
    """工作项状态"""
    PENDING = "pending"              # 未开始
    IN_PROGRESS = "in_progress"      # 进行中
    PENDING_REVIEW = "pending_review" # 待验收
    COMPLETED = "completed"          # 已完成
    REJECTED = "rejected"            # 已驳回


class CriteriaStatus(str, enum.Enum):
    """验收标准状态"""
    PENDING = "pending"     # 待验收
    PASSED = "passed"       # 已通过
    FAILED = "failed"       # 未通过


class CriteriaType(str, enum.Enum):
    """验收类型"""
    MANUAL = "manual"       # 人工验收
    AUTO = "auto"           # 自动验收


class Workflow(Base):
    """工作流模板"""
    __tablename__ = "workflows"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="工作流名称")
    description = Column(Text, comment="工作流描述")
    is_preset = Column(Boolean, default=False, comment="是否预置模板")
    status = Column(Enum(WorkflowStatus), default=WorkflowStatus.DRAFT, comment="状态")
    created_by = Column(Integer, ForeignKey("users.id"), comment="创建人ID")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关联关系
    creator = relationship("User", back_populates="workflows")
    work_items = relationship("WorkItem", back_populates="workflow", cascade="all, delete-orphan")
    instances = relationship("WorkflowInstance", back_populates="workflow")


class WorkItem(Base):
    """工作项定义"""
    __tablename__ = "work_items"

    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=False, comment="所属工作流ID")
    name = Column(String(100), nullable=False, comment="工作项名称")
    description = Column(Text, comment="工作项描述")
    work_item_type = Column(Enum(WorkItemType), nullable=False, comment="工作项类型")
    display_order = Column(Integer, default=0, comment="显示顺序")
    estimated_duration = Column(Integer, comment="预估时长(分钟)")
    is_required = Column(Boolean, default=True, comment="是否必填")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关联关系
    workflow = relationship("Workflow", back_populates="work_items")
    acceptance_criteria = relationship("AcceptanceCriteria", back_populates="work_item", cascade="all, delete-orphan")
    dependencies = relationship("WorkItemDependency", foreign_keys="WorkItemDependency.work_item_id", cascade="all, delete-orphan")
    instances = relationship("WorkItemInstance", back_populates="work_item")


class WorkItemDependency(Base):
    """工作项依赖关系"""
    __tablename__ = "work_item_dependencies"

    id = Column(Integer, primary_key=True, index=True)
    work_item_id = Column(Integer, ForeignKey("work_items.id"), nullable=False, comment="当前工作项ID")
    depends_on_id = Column(Integer, ForeignKey("work_items.id"), nullable=False, comment="依赖的工作项ID")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")


class AcceptanceCriteria(Base):
    """验收标准"""
    __tablename__ = "acceptance_criteria"

    id = Column(Integer, primary_key=True, index=True)
    work_item_id = Column(Integer, ForeignKey("work_items.id"), nullable=False, comment="所属工作项ID")
    content = Column(Text, nullable=False, comment="验收内容")
    is_required = Column(Boolean, default=True, comment="是否必填")
    criteria_type = Column(Enum(CriteriaType), default=CriteriaType.MANUAL, comment="验收类型")
    auto_check_script = Column(Text, comment="自动检查脚本")
    display_order = Column(Integer, default=0, comment="显示顺序")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关联关系
    work_item = relationship("WorkItem", back_populates="acceptance_criteria")
    results = relationship("AcceptanceCriteriaResult", back_populates="criteria")


class WorkflowInstanceStatus(str, enum.Enum):
    """工作流实例状态"""
    ACTIVE = "active"         # 执行中
    COMPLETED = "completed"   # 已完成
    SUSPENDED = "suspended"   # 已暂停


class WorkflowInstance(Base):
    """工作流实例"""
    __tablename__ = "workflow_instances"

    id = Column(String(32), primary_key=True, index=True, comment="实例ID")
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=False, comment="工作流模板ID")
    task_id = Column(Integer, ForeignKey("admission_tasks.id"), nullable=False, comment="关联准入任务ID")
    status = Column(Enum(WorkflowInstanceStatus), default=WorkflowInstanceStatus.ACTIVE, comment="实例状态")
    overall_progress = Column(Integer, default=0, comment="整体进度(%)")
    started_at = Column(DateTime, comment="开始时间")
    completed_at = Column(DateTime, comment="完成时间")
    created_by = Column(Integer, ForeignKey("users.id"), comment="创建人ID")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关联关系
    workflow = relationship("Workflow", back_populates="instances")
    task = relationship("AdmissionTask", back_populates="workflow_instances")
    creator = relationship("User", back_populates="workflow_instances")
    work_item_instances = relationship("WorkItemInstance", back_populates="instance", cascade="all, delete-orphan")


class WorkItemInstance(Base):
    """工作项实例"""
    __tablename__ = "work_item_instances"

    id = Column(Integer, primary_key=True, index=True)
    instance_id = Column(String(32), ForeignKey("workflow_instances.id"), nullable=False, comment="工作流实例ID")
    work_item_id = Column(Integer, ForeignKey("work_items.id"), nullable=False, comment="工作项定义ID")
    status = Column(Enum(WorkItemStatus), default=WorkItemStatus.PENDING, comment="状态")
    progress = Column(Integer, default=0, comment="进度(%)")
    assignee_id = Column(Integer, ForeignKey("users.id"), comment="执行人ID")
    reviewer_id = Column(Integer, ForeignKey("users.id"), comment="验收人ID")
    started_at = Column(DateTime, comment="开始时间")
    completed_at = Column(DateTime, comment="完成时间")
    actual_duration = Column(Integer, comment="实际耗时(分钟)")
    remark = Column(Text, comment="备注")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关联关系
    instance = relationship("WorkflowInstance", back_populates="work_item_instances")
    work_item = relationship("WorkItem", back_populates="instances")
    assignee = relationship("User", foreign_keys=[assignee_id], back_populates="assigned_work_items")
    reviewer = relationship("User", foreign_keys=[reviewer_id], back_populates="reviewed_work_items")
    criteria_results = relationship("AcceptanceCriteriaResult", back_populates="work_item_instance", cascade="all, delete-orphan")


class AcceptanceCriteriaResult(Base):
    """验收结果"""
    __tablename__ = "acceptance_criteria_results"

    id = Column(Integer, primary_key=True, index=True)
    work_item_instance_id = Column(Integer, ForeignKey("work_item_instances.id"), nullable=False, comment="工作项实例ID")
    criteria_id = Column(Integer, ForeignKey("acceptance_criteria.id"), nullable=False, comment="验收标准ID")
    status = Column(Enum(CriteriaStatus), default=CriteriaStatus.PENDING, comment="验收状态")
    remark = Column(Text, comment="验收备注")
    verified_by = Column(Integer, ForeignKey("users.id"), comment="验收人ID")
    verified_at = Column(DateTime, comment="验收时间")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关联关系
    work_item_instance = relationship("WorkItemInstance", back_populates="criteria_results")
    criteria = relationship("AcceptanceCriteria", back_populates="results")
    verifier = relationship("User", back_populates="criteria_verifications")
