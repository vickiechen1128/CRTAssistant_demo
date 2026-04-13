"""
SOP 模板相关 DTOs
"""
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict, Any


@dataclass
class DeliverableConfigRequest:
    """交付物配置请求"""
    name: str
    formats: List[str]
    required: bool = True
    description: Optional[str] = None


@dataclass
class AcceptanceCriteriaConfigRequest:
    """验收标准配置请求"""
    criterion_id: str
    description: str
    verification_method: str = "manual"


@dataclass
class ExecutionStepConfigRequest:
    """执行步骤配置请求"""
    step_id: str
    sequence: int
    name: str
    description: Optional[str] = None
    responsible_role: Optional[str] = None
    estimated_hours: Optional[float] = None


@dataclass
class WorkItemTemplateRequest:
    """工作项模板请求"""
    template_id: str
    name: str
    category: str
    sequence: int = 1
    description: Optional[str] = None
    audit_level: str = "normal"
    deliverables_config: List[DeliverableConfigRequest] = None
    acceptance_criteria_config: List[AcceptanceCriteriaConfigRequest] = None
    execution_steps_config: List[ExecutionStepConfigRequest] = None
    children: List["WorkItemTemplateRequest"] = None


@dataclass
class WorkflowNodeRequest:
    """流程节点请求"""
    node_id: str
    name: str
    sequence: int
    entry_conditions: Optional[List[Dict[str, Any]]] = None
    exit_conditions: Optional[List[Dict[str, Any]]] = None
    mandatory_rules: Optional[Dict[str, Any]] = None
    work_items: List[WorkItemTemplateRequest] = None


@dataclass
class CreateSOPTemplateRequest:
    """创建 SOP 模板请求"""
    template_id: Optional[str]  # 可选，不传则自动生成
    name: str
    template_type: str
    description: Optional[str] = None
    audit_matrix_config_id: Optional[str] = None
    workflow_nodes: List[WorkflowNodeRequest] = None


@dataclass
class UpdateSOPTemplateRequest:
    """更新 SOP 模板请求"""
    name: Optional[str] = None
    description: Optional[str] = None
    audit_matrix_config_id: Optional[str] = None


@dataclass
class SOPTemplateResponse:
    """SOP 模板响应"""
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


@dataclass
class SOPTemplateDetailResponse:
    """SOP 模板详情响应（含完整树状结构）"""
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
    nodes: List[Dict[str, Any]]
    created_by: str
    created_at: datetime
    updated_at: datetime


@dataclass
class SOPTemplateListResponse:
    """SOP 模板列表响应"""
    items: List[SOPTemplateResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


@dataclass
class SOPTemplateFilterRequest:
    """SOP 模板筛选请求"""
    template_type: Optional[str] = None
    status: Optional[str] = None
    keyword: Optional[str] = None
    page: int = 1
    page_size: int = 20


@dataclass
class PublishSOPTemplateRequest:
    """发布 SOP 模板请求"""
    published_by: str


@dataclass
class CloneSOPTemplateRequest:
    """克隆 SOP 模板请求"""
    new_version: Optional[str]  # 可选，不传则自动计算
    cloned_by: str


@dataclass
class InstantiateSOPTemplateRequest:
    """实例化 SOP 模板请求"""
    plan_id: str
    variable_mapping: Optional[Dict[str, str]] = None
    inventory_scope: Optional[Dict[str, List[str]]] = None


@dataclass
class InstantiateSOPTemplateResponse:
    """实例化 SOP 模板响应"""
    workflow_instance_id: str
    plan_id: str
    template_id: str
    template_version: str
    generated_work_items: List[Dict[str, Any]]
    created_at: datetime
