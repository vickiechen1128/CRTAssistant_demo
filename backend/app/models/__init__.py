"""
模型模块
导出所有SQLAlchemy模型
"""

from .user import User
from .admission_task import AdmissionTask
from .checklist import ChecklistTemplate, ChecklistTemplateItem, ChecklistItem
from .inventory import Inventory, InventoryServer, InventoryCloudResource, InventoryAccount
from .deliverable import Deliverable
from .verification import VerificationScript, VerificationRecord
from .workflow import (
    Workflow, WorkItem, WorkItemDependency, AcceptanceCriteria,
    WorkflowInstance, WorkItemInstance, AcceptanceCriteriaResult,
    WorkflowStatus, WorkItemType, WorkItemStatus, CriteriaStatus,
    CriteriaType, WorkflowInstanceStatus
)

# 导出所有模型，方便Alembic使用
__all__ = [
    "User",
    "AdmissionTask",
    "ChecklistTemplate",
    "ChecklistTemplateItem",
    "ChecklistItem",
    "Inventory",
    "InventoryServer",
    "InventoryCloudResource",
    "InventoryAccount",
    "Deliverable",
    "VerificationScript",
    "VerificationRecord",
    "Workflow",
    "WorkItem",
    "WorkItemDependency",
    "AcceptanceCriteria",
    "WorkflowInstance",
    "WorkItemInstance",
    "AcceptanceCriteriaResult",
    "WorkflowStatus",
    "WorkItemType",
    "WorkItemStatus",
    "CriteriaStatus",
    "CriteriaType",
    "WorkflowInstanceStatus",
]
