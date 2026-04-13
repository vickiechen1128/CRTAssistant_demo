"""
SOP 模板应用服务
协调领域对象完成用例
"""
from datetime import datetime
from typing import List, Optional, Dict, Any

from ..domain.entities.sop_template import SOPTemplate
from ..domain.entities.workflow_node import WorkflowNode
from ..domain.entities.work_item_template import WorkItemTemplate
from ..domain.value_objects.template_type import TemplateType
from ..domain.value_objects.template_status import TemplateStatus
from ..domain.value_objects.audit_level import AuditLevel
from ..domain.value_objects.work_item_category import WorkItemCategory
from ..domain.value_objects.audit_method import AuditMethod
from ..domain.repositories.sop_template_repository import SOPTemplateRepository
from ..domain.services.sop_template_domain_service import SOPTemplateDomainService
from .dtos.sop_template_dtos import (
    CreateSOPTemplateRequest,
    UpdateSOPTemplateRequest,
    SOPTemplateResponse,
    SOPTemplateDetailResponse,
    SOPTemplateListResponse,
    SOPTemplateFilterRequest,
    CloneSOPTemplateRequest,
    InstantiateSOPTemplateRequest,
    InstantiateSOPTemplateResponse,
    WorkflowNodeRequest,
    WorkItemTemplateRequest,
)


class SOPTemplateService:
    """
    SOP 模板应用服务
    
    职责：
    1. 接收DTO，转换为领域对象
    2. 协调领域服务和仓储
    3. 执行用例并返回DTO
    4. 处理事务边界
    """
    
    def __init__(
        self,
        template_repository: SOPTemplateRepository,
        domain_service: SOPTemplateDomainService,
    ):
        self._repository = template_repository
        self._domain_service = domain_service
    
    def create_template(
        self,
        request: CreateSOPTemplateRequest,
        created_by: str
    ) -> SOPTemplateResponse:
        """创建 SOP 模板"""
        # 转换值对象
        template_type = TemplateType(request.template_type)
        
        # 生成模板ID（如果未提供）
        template_id = request.template_id or self._domain_service.generate_template_id(template_type)
        
        # 检查 template_id 是否已存在
        if self._repository.exists(template_id):
            raise ValueError(f"Template ID already exists: {template_id}")
        
        # 创建领域对象
        template = SOPTemplate.create(
            template_id=template_id,
            name=request.name,
            template_type=template_type,
            created_by=created_by,
            description=request.description,
            audit_matrix_config_id=request.audit_matrix_config_id,
        )
        
        # 创建流程节点和工作项
        if request.workflow_nodes:
            for node_req in request.workflow_nodes:
                node = self._create_node_from_request(node_req, template.id)
                template.workflow_nodes.append(node)
        
        # 持久化
        saved_template = self._repository.save(template)
        
        return self._to_response(saved_template)
    
    def _create_node_from_request(
        self,
        request: WorkflowNodeRequest,
        template_id: str
    ) -> WorkflowNode:
        """从请求创建流程节点"""
        node = WorkflowNode.create(
            node_id=request.node_id,
            name=request.name,
            sequence=request.sequence,
            sop_template_id=template_id,
            entry_conditions=request.entry_conditions,
            exit_conditions=request.exit_conditions,
            mandatory_rules=request.mandatory_rules,
        )
        
        # 创建工作项
        if request.work_items:
            for wi_req in request.work_items:
                work_item = self._create_work_item_from_request(wi_req, template_id, node.id)
                node.work_items.append(work_item)
        
        return node
    
    def _create_work_item_from_request(
        self,
        request: WorkItemTemplateRequest,
        template_id: str,
        node_id: str,
        parent_id: Optional[str] = None
    ) -> WorkItemTemplate:
        """从请求创建工作项模板"""
        category = WorkItemCategory(request.category)
        audit_level = AuditLevel(request.audit_level)
        
        work_item = WorkItemTemplate.create(
            template_id=request.template_id,
            name=request.name,
            category=category,
            sop_template_id=template_id,
            workflow_node_id=node_id,
            parent_template_id=parent_id,
            sequence=request.sequence,
            description=request.description,
            audit_level=audit_level,
            deliverables_config=[
                dc.__dict__ for dc in (request.deliverables_config or [])
            ],
            acceptance_criteria_config=[
                ac.__dict__ for ac in (request.acceptance_criteria_config or [])
            ],
            execution_steps_config=[
                es.__dict__ for es in (request.execution_steps_config or [])
            ],
        )
        
        # 递归创建子工作项
        if request.children:
            for child_req in request.children:
                child = self._create_work_item_from_request(
                    child_req, template_id, node_id, work_item.id
                )
                work_item.children.append(child)
        
        return work_item
    
    def update_template(
        self,
        template_id: str,
        request: UpdateSOPTemplateRequest,
        updated_by: str
    ) -> SOPTemplateResponse:
        """更新 SOP 模板"""
        template = self._repository.find_by_id(template_id)
        if not template:
            raise ValueError(f"Template not found: {template_id}")
        
        # 更新领域对象
        template.update(
            name=request.name,
            description=request.description,
            audit_matrix_config_id=request.audit_matrix_config_id,
        )
        
        # 持久化
        saved_template = self._repository.save(template)
        
        return self._to_response(saved_template)
    
    def get_template(self, template_id: str) -> SOPTemplateDetailResponse:
        """获取模板详情（含完整树状结构）"""
        template = self._repository.find_by_id(template_id)
        if not template:
            raise ValueError(f"Template not found: {template_id}")
        
        return self._to_detail_response(template)
    
    def list_templates(
        self,
        filter_request: SOPTemplateFilterRequest
    ) -> SOPTemplateListResponse:
        """查询模板列表"""
        # 转换筛选条件
        template_type = None
        if filter_request.template_type:
            template_type = TemplateType(filter_request.template_type)
        
        status = None
        if filter_request.status:
            status = TemplateStatus(filter_request.status)
        
        # 查询
        skip = (filter_request.page - 1) * filter_request.page_size
        templates, total = self._repository.find_all(
            template_type=template_type,
            status=status,
            keyword=filter_request.keyword,
            skip=skip,
            limit=filter_request.page_size
        )
        
        # 构建响应
        total_pages = (total + filter_request.page_size - 1) // filter_request.page_size
        
        return SOPTemplateListResponse(
            items=[self._to_response(t) for t in templates],
            total=total,
            page=filter_request.page,
            page_size=filter_request.page_size,
            total_pages=total_pages
        )
    
    def delete_template(self, template_id: str, deleted_by: str) -> bool:
        """删除模板"""
        template = self._repository.find_by_id(template_id)
        if not template:
            raise ValueError(f"Template not found: {template_id}")
        
        if not template.can_delete():
            raise ValueError(f"Cannot delete template in {template.status.value} status")
        
        return self._repository.delete(template_id)
    
    def publish_template(
        self,
        template_id: str,
        published_by: str
    ) -> SOPTemplateResponse:
        """发布模板"""
        template = self._repository.find_by_id(template_id)
        if not template:
            raise ValueError(f"Template not found: {template_id}")
        
        # 执行发布（包含校验）
        template.publish(published_by)
        
        # 持久化
        saved_template = self._repository.save(template)
        
        return self._to_response(saved_template)
    
    def deprecate_template(
        self,
        template_id: str,
        deprecated_by: str,
        reason: Optional[str] = None
    ) -> SOPTemplateResponse:
        """弃用模板"""
        template = self._repository.find_by_id(template_id)
        if not template:
            raise ValueError(f"Template not found: {template_id}")
        
        template.deprecate(deprecated_by, reason)
        
        # 持久化
        saved_template = self._repository.save(template)
        
        return self._to_response(saved_template)
    
    def clone_template(
        self,
        template_id: str,
        request: CloneSOPTemplateRequest
    ) -> SOPTemplateResponse:
        """克隆模板"""
        source_template = self._repository.find_by_id(template_id)
        if not source_template:
            raise ValueError(f"Template not found: {template_id}")
        
        # 计算新版本号
        new_version = request.new_version or source_template.get_next_version()
        
        # 检查版本号是否已存在
        existing = self._repository.find_by_template_id_and_version(
            source_template.template_id, new_version
        )
        if existing:
            raise ValueError(f"Version {new_version} already exists for template {source_template.template_id}")
        
        # 克隆
        cloned = source_template.clone(new_version, request.cloned_by)
        
        # 复制流程节点和工作项
        for source_node in source_template.workflow_nodes:
            new_node = WorkflowNode.create(
                node_id=source_node.node_id,
                name=source_node.name,
                sequence=source_node.sequence,
                sop_template_id=cloned.id,
                entry_conditions=source_node.entry_conditions.copy(),
                exit_conditions=source_node.exit_conditions.copy(),
                mandatory_rules=source_node.mandatory_rules.copy(),
            )
            
            # 复制工作项
            for source_wi in source_node.work_items:
                if source_wi.is_parent:  # 只复制父级，子级在复制父级时处理
                    new_wi = self._clone_work_item(source_wi, cloned.id, new_node.id, None)
                    new_node.work_items.append(new_wi)
            
            cloned.workflow_nodes.append(new_node)
        
        # 持久化
        saved_template = self._repository.save(cloned)
        
        return self._to_response(saved_template)
    
    def _clone_work_item(
        self,
        source: WorkItemTemplate,
        template_id: str,
        node_id: str,
        parent_id: Optional[str]
    ) -> WorkItemTemplate:
        """递归克隆工作项"""
        cloned = WorkItemTemplate.create(
            template_id=source.template_id,
            name=source.name,
            category=source.category,
            sop_template_id=template_id,
            workflow_node_id=node_id,
            parent_template_id=parent_id,
            sequence=source.sequence,
            description=source.description,
            audit_level=source.audit_level,
            deliverables_config=source.deliverables_config.copy(),
            acceptance_criteria_config=source.acceptance_criteria_config.copy(),
            execution_steps_config=source.execution_steps_config.copy(),
        )
        
        # 递归克隆子工作项
        for source_child in source.children:
            child = self._clone_work_item(source_child, template_id, node_id, cloned.id)
            cloned.children.append(child)
        
        return cloned
    
    def instantiate_template(
        self,
        template_id: str,
        request: InstantiateSOPTemplateRequest
    ) -> Dict[str, Any]:
        """实例化模板"""
        template = self._repository.find_by_id(template_id)
        if not template:
            raise ValueError(f"Template not found: {template_id}")
        
        if not template.status.is_usable:
            raise ValueError(f"Template is not active: {template.status.value}")
        
        # 准备变量映射
        variable_mapping = request.variable_mapping or {}
        
        # 执行实例化
        result = self._domain_service.instantiate_template(
            template,
            variable_mapping
        )
        
        return result
    
    def get_active_template_by_type(self, template_type: str) -> Optional[SOPTemplateResponse]:
        """根据类型获取活跃模板"""
        template = self._repository.find_active_by_type(TemplateType(template_type))
        if not template:
            return None
        return self._to_response(template)
    
    def _to_response(self, template: SOPTemplate) -> SOPTemplateResponse:
        """转换为响应DTO"""
        return SOPTemplateResponse(
            id=template.id,
            template_id=template.template_id,
            name=template.name,
            template_type=template.template_type.value,
            template_type_display=template.template_type.display_name,
            description=template.description,
            version=template.version,
            status=template.status.value,
            status_display=template.status.display_name,
            audit_matrix_config_id=template.audit_matrix_config_id,
            parent_work_items_config=template.parent_work_items_config,
            workflow_nodes_count=len(template.workflow_nodes),
            created_by=template.created_by,
            created_at=template.created_at,
            updated_at=template.updated_at,
            published_at=template.published_at,
            deprecated_at=template.deprecated_at,
        )
    
    def _to_detail_response(self, template: SOPTemplate) -> SOPTemplateDetailResponse:
        """转换为详情响应DTO"""
        tree = self._domain_service.build_template_tree(template)
        
        return SOPTemplateDetailResponse(
            id=template.id,
            template_id=template.template_id,
            name=template.name,
            template_type=template.template_type.value,
            template_type_display=template.template_type.display_name,
            description=template.description,
            version=template.version,
            status=template.status.value,
            status_display=template.status.display_name,
            audit_matrix_config_id=template.audit_matrix_config_id,
            nodes=tree.get("nodes", []),
            created_by=template.created_by,
            created_at=template.created_at,
            updated_at=template.updated_at,
        )
