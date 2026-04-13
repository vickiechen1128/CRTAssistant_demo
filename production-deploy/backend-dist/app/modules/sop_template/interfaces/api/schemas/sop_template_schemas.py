"""
SOP 模板 API Schemas
"""
from datetime import datetime
from typing import List, Optional, Dict, Any, TypeVar, Generic
from pydantic import BaseModel, Field


T = TypeVar('T')


class ApiResponseSchema(BaseModel, Generic[T]):
    """通用API响应Schema"""
    code: int = 200
    message: str = "success"
    data: Optional[T] = None

    class Config:
        from_attributes = True


class DeliverableConfigSchema(BaseModel):
    """交付物配置 Schema"""
    name: str
    formats: List[str]
    required: bool = True
    description: Optional[str] = None
    
    class Config:
        from_attributes = True


class AcceptanceCriteriaConfigSchema(BaseModel):
    """验收标准配置 Schema"""
    criterion_id: str
    description: str
    verification_method: str = "manual"
    
    class Config:
        from_attributes = True


class ExecutionStepConfigSchema(BaseModel):
    """执行步骤配置 Schema"""
    step_id: str
    sequence: int
    name: str
    description: Optional[str] = None
    responsible_role: Optional[str] = None
    estimated_hours: Optional[float] = None
    
    class Config:
        from_attributes = True


class WorkItemTemplateSchema(BaseModel):
    """工作项模板 Schema"""
    template_id: str
    name: str
    category: str
    sequence: int = 1
    description: Optional[str] = None
    audit_level: str = "normal"
    deliverables_config: Optional[List[DeliverableConfigSchema]] = Field(default_factory=list)
    acceptance_criteria_config: Optional[List[AcceptanceCriteriaConfigSchema]] = Field(default_factory=list)
    execution_steps_config: Optional[List[ExecutionStepConfigSchema]] = Field(default_factory=list)
    children: Optional[List["WorkItemTemplateSchema"]] = Field(default_factory=list)
    
    class Config:
        from_attributes = True


class WorkflowNodeSchema(BaseModel):
    """流程节点 Schema"""
    node_id: str
    name: str
    sequence: int
    entry_conditions: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    exit_conditions: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    mandatory_rules: Optional[Dict[str, Any]] = Field(default_factory=dict)
    work_items: Optional[List[WorkItemTemplateSchema]] = Field(default_factory=list)
    
    class Config:
        from_attributes = True


class CreateSOPTemplateSchema(BaseModel):
    """创建 SOP 模板 Schema"""
    template_id: Optional[str] = None
    name: str = Field(..., min_length=1, max_length=100)
    template_type: str = Field(..., pattern="^(new_system|new_feature|func_change|arch_change|security)$")
    description: Optional[str] = None
    audit_matrix_config_id: Optional[str] = None
    workflow_nodes: Optional[List[WorkflowNodeSchema]] = Field(default_factory=list)


class UpdateSOPTemplateSchema(BaseModel):
    """更新 SOP 模板 Schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    audit_matrix_config_id: Optional[str] = None


class SOPTemplateResponseSchema(BaseModel):
    """SOP 模板响应 Schema"""
    id: str
    template_id: str
    name: str
    template_type: str
    template_type_display: str
    description: Optional[str]
    version: str
    status: str
    status_display: str
    audit_matrix_config_id: Optional[str]
    parent_work_items_config: List[Dict[str, Any]]
    workflow_nodes_count: int
    created_by: str
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime]
    deprecated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class WorkItemTreeSchema(BaseModel):
    """工作项树形结构 Schema"""
    id: str
    template_id: str
    name: str
    category: str
    category_display: str
    category_icon: str
    sequence: int
    description: Optional[str]
    audit_level: str
    audit_level_display: str
    is_parent: bool
    deliverables_config: List[Dict[str, Any]]
    acceptance_criteria_config: List[Dict[str, Any]]
    execution_steps_config: List[Dict[str, Any]]
    children: List["WorkItemTreeSchema"]


class WorkflowNodeDetailSchema(BaseModel):
    """流程节点详情 Schema"""
    id: str
    node_id: str
    name: str
    sequence: int
    entry_conditions: List[Dict[str, Any]]
    exit_conditions: List[Dict[str, Any]]
    mandatory_rules: Dict[str, Any]
    work_items: List[WorkItemTreeSchema]


class SOPTemplateDetailResponseSchema(BaseModel):
    """SOP 模板详情响应 Schema"""
    id: str
    template_id: str
    name: str
    template_type: str
    template_type_display: str
    description: Optional[str]
    version: str
    status: str
    status_display: str
    audit_matrix_config_id: Optional[str]
    nodes: List[WorkflowNodeDetailSchema]
    created_by: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SOPTemplateListItemSchema(BaseModel):
    """SOP 模板列表项 Schema"""
    id: str
    template_id: str
    name: str
    template_type: str
    template_type_display: str
    version: str
    status: str
    status_display: str
    workflow_nodes_count: int
    created_by: str
    created_at: datetime


class SOPTemplateListResponseSchema(BaseModel):
    """SOP 模板列表响应 Schema"""
    items: List[SOPTemplateListItemSchema]
    total: int
    page: int
    page_size: int
    total_pages: int


class PublishSOPTemplateSchema(BaseModel):
    """发布 SOP 模板 Schema"""
    pass  # 无需额外参数


class CloneSOPTemplateSchema(BaseModel):
    """克隆 SOP 模板 Schema"""
    new_version: Optional[str] = None


class DeprecateSOPTemplateSchema(BaseModel):
    """弃用 SOP 模板 Schema"""
    reason: Optional[str] = None


class InstantiateSOPTemplateSchema(BaseModel):
    """实例化 SOP 模板 Schema"""
    plan_id: str
    variable_mapping: Optional[Dict[str, str]] = Field(default_factory=dict)
    inventory_scope: Optional[Dict[str, List[str]]] = Field(default_factory=dict)


class GeneratedWorkItemSchema(BaseModel):
    """生成的工作项 Schema"""
    work_item_id: str
    name: str
    category: str
    audit_level: str
    sub_items: List[Dict[str, Any]]


class InstantiateSOPTemplateResponseSchema(BaseModel):
    """实例化 SOP 模板响应 Schema"""
    workflow_instance_id: str
    plan_id: str
    template_id: str
    template_version: str
    generated_work_items: List[GeneratedWorkItemSchema]
    created_at: datetime
