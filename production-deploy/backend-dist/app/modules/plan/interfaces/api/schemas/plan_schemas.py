"""
API 请求/响应 Schema
用于 FastAPI 路由层
"""
from datetime import datetime
from typing import List, Optional, Any, Generic, TypeVar, Dict
from pydantic import BaseModel, Field, validator


T = TypeVar('T')


class ApiResponseSchema(BaseModel, Generic[T]):
    """统一API响应格式"""
    success: bool = True
    message: str = "Success"
    data: Optional[T] = None
    error: Optional[str] = None


class ApprovalFileDetailSchema(BaseModel):
    """审批材料详细信息Schema"""
    file_name: str = Field(..., description="文件名")
    file_url: str = Field(..., description="文件URL")
    file_size: int = Field(..., ge=0, description="文件大小(字节)")
    uploaded_at: str = Field(..., description="上传时间(ISO格式)")
    file_id: Optional[str] = Field(None, description="文件ID")


class AffectedModuleItemSchema(BaseModel):
    """受影响功能模块项Schema"""
    module_id: str = Field(..., description="模块ID")
    module_name: str = Field(..., description="模块名称")
    action: str = Field(..., description="操作类型: create/update/delete")
    before_version: Optional[str] = Field(None, description="变更前版本")
    after_version: Optional[str] = Field(None, description="变更后版本")
    change_description: Optional[str] = Field(None, description="变更说明")
    
    @validator('action')
    def validate_action(cls, v):
        if v not in {'create', 'update', 'delete'}:
            raise ValueError('Action must be create, update, or delete')
        return v


class CreatePlanSchema(BaseModel):
    """创建计划请求Schema（优化版）"""
    name: str = Field(..., min_length=1, max_length=200, description="计划名称")
    category: str = Field(..., description="计划分类: new_system/new_feature/func_change/arch_change/security_check")
    priority: str = Field(..., description="优先级: P0/P1/P2/P3")
    description: Optional[str] = Field(None, max_length=2000, description="计划描述")
    planned_start_time: Optional[datetime] = Field(None, description="计划开始时间")
    planned_end_time: Optional[datetime] = Field(None, description="计划结束时间")
    workflow_template_id: Optional[str] = Field(None, description="工作流模板ID")
    template_type: Optional[str] = Field(None, description="模板类型")
    
    # 新增字段
    affected_modules: List[AffectedModuleItemSchema] = Field(default_factory=list, description="受影响功能模块")
    approval_files: List[ApprovalFileDetailSchema] = Field(default_factory=list, description="审批材料列表")
    related_inventory_ids: List[str] = Field(default_factory=list, description="关联台账ID列表")
    idempotency_key: Optional[str] = Field(None, description="幂等性Key")
    
    @validator('category')
    def validate_category(cls, v):
        valid = {'new_system', 'new_feature', 'func_change', 'arch_change', 'security_check'}
        if v not in valid:
            raise ValueError(f'分类必须是以下之一: {valid}')
        return v
    
    @validator('priority')
    def validate_priority(cls, v):
        if v not in {'P0', 'P1', 'P2', 'P3'}:
            raise ValueError('优先级必须是 P0, P1, P2, 或 P3')
        return v


class UpdatePlanSchema(BaseModel):
    """更新计划请求Schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    planned_start_time: Optional[datetime] = None
    planned_end_time: Optional[datetime] = None
    priority: Optional[str] = None
    affected_modules: Optional[List[AffectedModuleItemSchema]] = None
    
    @validator('priority')
    def validate_priority(cls, v):
        if v and v not in {'P0', 'P1', 'P2', 'P3'}:
            raise ValueError('优先级必须是 P0, P1, P2, 或 P3')
        return v


class PlanResponseSchema(BaseModel):
    """计划响应Schema（优化版）"""
    id: str
    data_tag: str
    name: str
    category: str
    category_label: str = ""
    priority: str
    priority_label: str = ""
    status: str
    status_label: str = ""
    description: Optional[str] = None
    planned_start_time: Optional[datetime] = None
    planned_end_time: Optional[datetime] = None
    actual_start_time: Optional[datetime] = None
    actual_end_time: Optional[datetime] = None
    workflow_template_id: Optional[str] = None
    template_type: str = ""
    
    # 关联信息
    inventory_ids: List[str] = []
    related_inventory_ids: List[str] = []
    inventory_action: Optional[str] = None
    
    # 新增字段
    affected_modules: List[Dict[str, Any]] = []
    affected_modules_count: int = 0
    approval_files: List[Dict[str, Any]] = []
    
    created_by: str
    created_at: datetime
    updated_at: datetime
    is_overdue: bool = False
    
    class Config:
        from_attributes = True


class PlanListResponseSchema(BaseModel):
    """计划列表响应Schema"""
    items: List[PlanResponseSchema]
    total: int
    page: int
    page_size: int
    total_pages: int


class PlanFilterSchema(BaseModel):
    """计划筛选Schema"""
    status: Optional[str] = Field(None, description="状态: DRAFT/PENDING/IN_PROGRESS/COMPLETED/CANCELLED")
    category: Optional[str] = Field(None, description="分类")
    priority: Optional[str] = Field(None, description="优先级")
    keyword: Optional[str] = Field(None, description="关键词搜索")
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")


class LinkInventorySchema(BaseModel):
    """关联台账请求Schema"""
    inventory_ids: List[str] = Field(..., min_items=1, description="台账ID列表")


class StartPlanSchema(BaseModel):
    """启动计划请求Schema"""
    confirmed: bool = Field(False, description="P0计划是否已确认")
    confirmation_note: Optional[str] = Field(None, description="确认备注")


class CompletePlanSchema(BaseModel):
    """完成计划请求Schema"""
    completion_note: Optional[str] = Field(None, description="完成备注")


class CancelPlanSchema(BaseModel):
    """取消计划请求Schema"""
    reason: str = Field(..., min_length=1, max_length=500, description="取消原因")


# ============ 新增Schema ============

class PlanPreviewRequestSchema(BaseModel):
    """计划变更预览请求Schema"""
    name: str = Field(..., description="计划名称")
    category: str = Field(..., description="计划分类")
    affected_modules: List[AffectedModuleItemSchema] = Field(default_factory=list)
    related_inventory_ids: List[str] = Field(default_factory=list)


class InventoryChangePreviewSchema(BaseModel):
    """台账变更预览项"""
    change_type: str = Field(..., description="变更类型")
    change_object: str = Field(..., description="变更对象")
    operation: str = Field(..., description="操作")
    details: Dict[str, Any] = Field(default_factory=dict, description="详细信息")


class LifecycleLogPreviewSchema(BaseModel):
    """生命周期日志预览项"""
    log_type: str = Field(..., description="日志类型")
    log_type_label: str = Field(..., description="日志类型标签")
    event_title: str = Field(..., description="事件标题")


class WorkflowPreviewSchema(BaseModel):
    """工作流预览"""
    template_type: str = Field(..., description="模板类型")
    check_items: List[Dict[str, Any]] = Field(default_factory=list, description="检查项")


class PlanPreviewResponseSchema(BaseModel):
    """计划变更预览响应Schema"""
    plan_name: str = Field(..., description="计划名称")
    category: str = Field(..., description="计划分类")
    category_label: str = Field(..., description="分类标签")
    inventory_changes: List[InventoryChangePreviewSchema] = Field(default_factory=list)
    lifecycle_logs_preview: List[LifecycleLogPreviewSchema] = Field(default_factory=list)
    workflow_preview: WorkflowPreviewSchema = Field(default_factory=dict)


class GeneratePlanIdResponseSchema(BaseModel):
    """预生成PlanID响应Schema"""
    plan_id: str = Field(..., description="预生成的PlanID")
    data_tag: str = Field(..., description="数据标签")


class PlanRelatedInventorySchema(BaseModel):
    """计划关联的台账信息Schema"""
    id: str
    app_name: str
    system_type: str
    business_owner: str
    project_owner: str
    status: str
    view_url: str


class PlanLifecycleLogSchema(BaseModel):
    """计划相关的生命周期日志Schema"""
    id: str
    log_type: str
    log_type_label: str
    event_title: str
    module_name: Optional[str]
    operator: str
    operation_time: str


class PlanDetailResponseSchema(PlanResponseSchema):
    """计划详情响应Schema"""
    related_applications: List[PlanRelatedInventorySchema] = Field(default_factory=list)
    related_modules: List[Dict[str, Any]] = Field(default_factory=list)
    lifecycle_logs: List[PlanLifecycleLogSchema] = Field(default_factory=list)
    workflow: Dict[str, Any] = Field(default_factory=dict)
