"""
计划模块数据传输对象 (DTOs)
用于应用层与接口层之间的数据交换
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator


class ApprovalFileDetail(BaseModel):
    """审批材料详细信息"""
    file_name: str = Field(..., description="文件名")
    file_url: str = Field(..., description="文件URL")
    file_size: int = Field(..., ge=0, description="文件大小(字节)")
    uploaded_at: str = Field(..., description="上传时间(ISO格式)")
    file_id: Optional[str] = Field(None, description="文件ID")


class AffectedModuleItem(BaseModel):
    """受影响功能模块项"""
    module_id: str = Field(..., description="模块ID（新增时为临时ID）")
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


class CreatePlanRequest(BaseModel):
    """创建计划请求"""
    name: str = Field(..., min_length=1, max_length=200, description="计划名称")
    category: str = Field(..., description="计划分类")
    priority: str = Field(..., description="优先级 (P0-P3)")
    description: Optional[str] = Field(None, max_length=2000, description="计划描述")
    planned_start_time: Optional[datetime] = Field(None, description="计划开始时间")
    planned_end_time: Optional[datetime] = Field(None, description="计划结束时间")
    workflow_template_id: Optional[str] = Field(None, description="工作流模板ID")
    template_type: Optional[str] = Field(None, description="模板类型")
    
    # 新增字段
    affected_modules: List[AffectedModuleItem] = Field(default_factory=list, description="受影响功能模块")
    approval_files: List[ApprovalFileDetail] = Field(default_factory=list, description="审批材料列表")
    related_inventory_ids: List[str] = Field(default_factory=list, description="关联台账ID列表")
    
    # 幂等性Key
    idempotency_key: Optional[str] = Field(None, description="幂等性Key")
    
    @validator('category')
    def validate_category(cls, v):
        valid_categories = {'new_system', 'new_feature', 'func_change', 'arch_change', 'security_check'}
        if v not in valid_categories:
            raise ValueError(f'Invalid category. Must be one of: {valid_categories}')
        return v
    
    @validator('priority')
    def validate_priority(cls, v):
        if v not in {'P0', 'P1', 'P2', 'P3'}:
            raise ValueError('Priority must be P0, P1, P2, or P3')
        return v
    
    @validator('planned_end_time')
    def validate_end_time(cls, v, values):
        if v and values.get('planned_start_time') and v <= values['planned_start_time']:
            raise ValueError('planned_end_time must be after planned_start_time')
        return v


class UpdatePlanRequest(BaseModel):
    """更新计划请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    planned_start_time: Optional[datetime] = None
    planned_end_time: Optional[datetime] = None
    priority: Optional[str] = None
    affected_modules: Optional[List[AffectedModuleItem]] = None
    
    @validator('priority')
    def validate_priority(cls, v):
        if v and v not in {'P0', 'P1', 'P2', 'P3'}:
            raise ValueError('Priority must be P0, P1, P2, or P3')
        return v


class PlanResponse(BaseModel):
    """计划响应"""
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


class PlanListResponse(BaseModel):
    """计划列表响应"""
    items: List[PlanResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class PlanFilterRequest(BaseModel):
    """计划筛选请求"""
    status: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[str] = None
    created_by: Optional[str] = None
    keyword: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)


class LinkInventoryRequest(BaseModel):
    """关联台账请求"""
    inventory_ids: List[str] = Field(..., min_items=1, description="台账ID列表")


class StartPlanRequest(BaseModel):
    """启动计划请求"""
    confirmed: bool = Field(False, description="P0计划是否已确认")
    confirmation_note: Optional[str] = Field(None, description="确认备注")


class CompletePlanRequest(BaseModel):
    """完成计划请求"""
    completion_note: Optional[str] = Field(None, description="完成备注")


class CancelPlanRequest(BaseModel):
    """取消计划请求"""
    reason: str = Field(..., min_length=1, max_length=500, description="取消原因")


class PlanPreviewRequest(BaseModel):
    """计划变更预览请求（用于Step 4）"""
    name: str = Field(..., description="计划名称")
    category: str = Field(..., description="计划分类")
    affected_modules: List[AffectedModuleItem] = Field(default_factory=list)
    related_inventory_ids: List[str] = Field(default_factory=list)


class PlanPreviewResponse(BaseModel):
    """计划变更预览响应"""
    plan_name: str
    category: str
    category_label: str
    
    # 台账变更摘要
    inventory_changes: List[Dict[str, Any]] = Field(default_factory=list, description="台账变更摘要")
    
    # 生命周期日志预览
    lifecycle_logs_preview: List[Dict[str, Any]] = Field(default_factory=list, description="将要生成的生命周期日志")
    
    # 工作流检查项预览
    workflow_preview: Dict[str, Any] = Field(default_factory=dict, description="工作流检查项预览")


class GeneratePlanIdResponse(BaseModel):
    """预生成PlanID响应"""
    plan_id: str = Field(..., description="预生成的PlanID")
    data_tag: str = Field(..., description="数据标签")


class PlanRelatedInventoryInfo(BaseModel):
    """计划关联的台账信息"""
    id: str
    app_name: str
    system_type: str
    business_owner: str
    project_owner: str
    status: str
    view_url: str


class PlanLifecycleLogInfo(BaseModel):
    """计划相关的生命周期日志信息"""
    id: str
    log_type: str
    log_type_label: str
    event_title: str
    module_name: Optional[str]
    operator: str
    operation_time: str


class PlanDetailResponse(PlanResponse):
    """计划详情响应（包含完整关联信息）"""
    # 关联应用系统列表
    related_applications: List[PlanRelatedInventoryInfo] = Field(default_factory=list)
    
    # 影响功能模块列表
    related_modules: List[Dict[str, Any]] = Field(default_factory=list)
    
    # 生命周期日志
    lifecycle_logs: List[PlanLifecycleLogInfo] = Field(default_factory=list)
    
    # 工作流信息
    workflow: Dict[str, Any] = Field(default_factory=dict)
