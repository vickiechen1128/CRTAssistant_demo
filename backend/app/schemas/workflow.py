"""
工作流模块的数据模型 (Pydantic)
用于API请求和响应的数据验证
"""

import enum
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


# ==================== 枚举类型定义（字符串形式）====================

class WorkflowStatus(str, enum.Enum):
    """工作流状态"""
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


class WorkItemType(str, enum.Enum):
    """工作项类型"""
    RESOURCE_DELIVERY = "resource_delivery"
    INVENTORY = "inventory"
    PERMISSION_HANDOVER = "permission_handover"
    SECURITY_BASELINE = "security_baseline"
    MONITORING = "monitoring"
    CUSTOM = "custom"


class WorkItemStatus(str, enum.Enum):
    """工作项状态"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    PENDING_REVIEW = "pending_review"
    COMPLETED = "completed"
    REJECTED = "rejected"


class CriteriaStatus(str, enum.Enum):
    """验收标准状态"""
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"


class CriteriaType(str, enum.Enum):
    """验收类型"""
    MANUAL = "manual"
    AUTO = "auto"


class WorkflowInstanceStatus(str, enum.Enum):
    """工作流实例状态"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


# ==================== 基础模型 ====================

class AcceptanceCriteriaBase(BaseModel):
    """验收标准基础模型"""
    content: str = Field(..., description="验收内容")
    is_required: bool = Field(True, description="是否必填")
    criteria_type: str = Field("manual", description="验收类型")
    auto_check_script: Optional[str] = Field(None, description="自动检查脚本")
    display_order: int = Field(0, description="显示顺序")


class AcceptanceCriteriaCreate(AcceptanceCriteriaBase):
    """创建验收标准请求"""
    pass


class AcceptanceCriteriaUpdate(BaseModel):
    """更新验收标准请求"""
    content: Optional[str] = None
    is_required: Optional[bool] = None
    criteria_type: Optional[str] = None
    auto_check_script: Optional[str] = None
    display_order: Optional[int] = None


class AcceptanceCriteriaResponse(AcceptanceCriteriaBase):
    """验收标准响应"""
    id: int
    work_item_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AcceptanceCriteriaResultBase(BaseModel):
    """验收结果基础模型"""
    status: str = Field("pending", description="验收状态")
    remark: Optional[str] = Field(None, description="验收备注")


class AcceptanceCriteriaResultCreate(AcceptanceCriteriaResultBase):
    """创建验收结果请求"""
    criteria_id: int = Field(..., description="验收标准ID")


class AcceptanceCriteriaResultResponse(AcceptanceCriteriaResultBase):
    """验收结果响应"""
    id: int
    work_item_instance_id: int
    criteria_id: int
    verified_by: Optional[int] = None
    verified_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== 工作项模型 ====================

class WorkItemDependencyBase(BaseModel):
    """工作项依赖基础模型"""
    depends_on_id: int = Field(..., description="依赖的工作项ID")


class WorkItemDependencyCreate(WorkItemDependencyBase):
    """创建工作项依赖请求"""
    pass


class WorkItemBase(BaseModel):
    """工作项基础模型"""
    name: str = Field(..., description="工作项名称", max_length=100)
    description: Optional[str] = Field(None, description="工作项描述")
    work_item_type: str = Field(..., description="工作项类型")
    display_order: int = Field(0, description="显示顺序")
    estimated_duration: Optional[int] = Field(None, description="预估时长(分钟)")
    is_required: bool = Field(True, description="是否必填")


class WorkItemCreate(WorkItemBase):
    """创建工作项请求"""
    acceptance_criteria: List[AcceptanceCriteriaCreate] = Field([], description="验收标准列表")
    depends_on: List[int] = Field([], description="依赖的工作项ID列表")


class WorkItemUpdate(BaseModel):
    """更新工作项请求"""
    name: Optional[str] = None
    description: Optional[str] = None
    work_item_type: Optional[str] = None
    display_order: Optional[int] = None
    estimated_duration: Optional[int] = None
    is_required: Optional[bool] = None


class WorkItemResponse(WorkItemBase):
    """工作项响应"""
    id: int
    workflow_id: int
    acceptance_criteria: List[AcceptanceCriteriaResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== 工作流模板模型 ====================

class WorkflowBase(BaseModel):
    """工作流基础模型"""
    name: str = Field(..., description="工作流名称", max_length=100)
    description: Optional[str] = Field(None, description="工作流描述")


class WorkflowCreate(WorkflowBase):
    """创建工作流请求"""
    work_items: List[WorkItemCreate] = Field([], description="工作项列表")


class WorkflowUpdate(BaseModel):
    """更新工作流请求"""
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class WorkflowListResponse(WorkflowBase):
    """工作流列表响应"""
    id: int
    is_preset: bool
    status: str
    work_item_count: int = Field(0, description="工作项数量")
    created_by: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class WorkflowDetailResponse(WorkflowListResponse):
    """工作流详情响应"""
    work_items: List[WorkItemResponse] = []


class WorkflowProgressItem(BaseModel):
    """工作流进度项"""
    id: int
    name: str
    status: str
    progress: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class WorkflowProgressResponse(BaseModel):
    """工作流进度响应"""
    workflow_id: int
    overall_progress: int
    status: str
    work_items: List[WorkflowProgressItem]
    critical_path: List[int] = []
    blocked_items: List[int] = []
    estimated_completion: Optional[datetime] = None


# ==================== 工作流实例模型 ====================

class WorkItemInstanceBase(BaseModel):
    """工作项实例基础模型"""
    progress: int = Field(0, description="进度(%)", ge=0, le=100)
    remark: Optional[str] = Field(None, description="备注")


class WorkItemInstanceResponse(WorkItemInstanceBase):
    """工作项实例响应"""
    id: int
    instance_id: str
    work_item_id: int
    work_item: Optional[WorkItemResponse] = None
    assignee_id: Optional[int] = None
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WorkflowInstanceBase(BaseModel):
    """工作流实例基础模型"""
    task_id: int = Field(..., description="关联的准入任务ID")
    remark: Optional[str] = Field(None, description="备注")


class WorkflowInstanceCreate(WorkflowInstanceBase):
    """创建工作流实例请求"""
    pass


class WorkflowInstanceUpdate(BaseModel):
    """更新工作流实例请求"""
    status: Optional[str] = None
    remark: Optional[str] = None


class WorkflowInstanceResponse(WorkflowInstanceBase):
    """工作流实例响应"""
    id: str
    workflow_id: int
    workflow: Optional[WorkflowListResponse] = None
    status: str
    overall_progress: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_by: int
    created_at: datetime
    updated_at: datetime
    work_items: List[WorkItemInstanceResponse] = []

    class Config:
        from_attributes = True


class WorkItemExecuteRequest(BaseModel):
    """执行工作项请求"""
    work_item_id: int = Field(..., description="工作项ID")
    assignee_id: Optional[int] = Field(None, description="执行人ID")
    remark: Optional[str] = Field(None, description="备注")


class WorkItemVerifyRequest(BaseModel):
    """验收工作项请求"""
    work_item_id: int = Field(..., description="工作项ID")
    status: str = Field(..., description="验收状态: completed/rejected")
    progress: int = Field(100, description="进度(%)", ge=0, le=100)
    remark: Optional[str] = Field(None, description="备注")
    criteria_results: List[AcceptanceCriteriaResultCreate] = Field([], description="验收结果列表")


# ==================== 列表请求模型 ====================

class WorkflowListRequest(BaseModel):
    """工作流列表查询请求"""
    page: int = Field(1, ge=1, description="页码")
    per_page: int = Field(20, ge=1, le=100, description="每页条数")
    is_preset: Optional[bool] = Field(None, description="是否预置模板")
    keyword: Optional[str] = Field(None, description="关键词搜索")


class WorkflowInstanceListRequest(BaseModel):
    """工作流实例列表查询请求"""
    page: int = Field(1, ge=1, description="页码")
    per_page: int = Field(20, ge=1, le=100, description="每页条数")
    workflow_id: Optional[int] = Field(None, description="工作流模板ID")
    task_id: Optional[int] = Field(None, description="准入任务ID")
    status: Optional[str] = Field(None, description="状态")


class PaginationResponse(BaseModel):
    """分页信息响应"""
    page: int
    per_page: int
    total: int
    pages: int


class WorkflowListData(BaseModel):
    """工作流列表数据"""
    items: List[WorkflowListResponse]
    pagination: PaginationResponse
