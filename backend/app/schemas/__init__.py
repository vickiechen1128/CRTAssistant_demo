"""
Pydantic Schema模块
用于API请求/响应的数据验证和序列化
"""

from .user import UserCreate, UserResponse, UserLogin
from .admission_task import (
    AdmissionTaskCreate, 
    AdmissionTaskUpdate, 
    AdmissionTaskResponse,
    AdmissionTaskList
)
from .checklist import (
    ChecklistItemUpdate,
    ChecklistItemResponse,
    ChecklistItemVerify
)
from .inventory import (
    InventoryCreate,
    InventoryResponse,
    InventoryServerCreate,
    InventoryCloudResourceCreate,
    InventoryAccountCreate
)
from .deliverable import DeliverableCreate, DeliverableResponse
from .verification import (
    VerificationScriptCreate,
    VerificationScriptResponse,
    VerificationExecuteRequest,
    VerificationRecordResponse
)

__all__ = [
    # 用户
    "UserCreate", "UserResponse", "UserLogin",
    # 准入任务
    "AdmissionTaskCreate", "AdmissionTaskUpdate", "AdmissionTaskResponse", "AdmissionTaskList",
    # 检查清单
    "ChecklistItemUpdate", "ChecklistItemResponse", "ChecklistItemVerify",
    # 台账
    "InventoryCreate", "InventoryResponse",
    "InventoryServerCreate", "InventoryCloudResourceCreate", "InventoryAccountCreate",
    # 交付物
    "DeliverableCreate", "DeliverableResponse",
    # 验证
    "VerificationScriptCreate", "VerificationScriptResponse",
    "VerificationExecuteRequest", "VerificationRecordResponse",
]
