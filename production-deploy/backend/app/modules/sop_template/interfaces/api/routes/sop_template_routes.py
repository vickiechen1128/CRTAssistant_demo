"""
SOP 模板路由
FastAPI 路由定义
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db

from ....application.sop_template_service import SOPTemplateService
from ....application.dtos.sop_template_dtos import (
    CreateSOPTemplateRequest,
    UpdateSOPTemplateRequest,
    SOPTemplateFilterRequest,
    CloneSOPTemplateRequest,
    InstantiateSOPTemplateRequest,
)
from ....domain.services.sop_template_domain_service import SOPTemplateDomainService
from ....infrastructure.persistence.sop_template_repository_impl import SOPTemplateRepositoryImpl
from ..schemas.sop_template_schemas import (
    CreateSOPTemplateSchema,
    UpdateSOPTemplateSchema,
    SOPTemplateResponseSchema,
    SOPTemplateDetailResponseSchema,
    SOPTemplateListResponseSchema,
    PublishSOPTemplateSchema,
    CloneSOPTemplateSchema,
    DeprecateSOPTemplateSchema,
    InstantiateSOPTemplateSchema,
    ApiResponseSchema,
)

router = APIRouter(prefix="/sop-templates", tags=["SOP模板管理"])


def get_sop_template_service(db: Session = Depends(get_db)) -> SOPTemplateService:
    """依赖注入：获取 SOPTemplateService 实例"""
    repository = SOPTemplateRepositoryImpl(db)
    domain_service = SOPTemplateDomainService(repository)
    return SOPTemplateService(repository, domain_service)


@router.post("", response_model=ApiResponseSchema[SOPTemplateResponseSchema])
def create_template(
    request: CreateSOPTemplateSchema,
    service: SOPTemplateService = Depends(get_sop_template_service),
    current_user: str = "admin"  # TODO: 从认证获取
):
    """创建 SOP 模板"""
    try:
        # 转换嵌套的 workflow_nodes
        node_requests = []
        if request.workflow_nodes:
            from ....application.dtos.sop_template_dtos import WorkflowNodeRequest, WorkItemTemplateRequest
            for node in request.workflow_nodes:
                work_items = []
                if node.work_items:
                    for wi in node.work_items:
                        work_items.append(WorkItemTemplateRequest(
                            template_id=wi.template_id,
                            name=wi.name,
                            category=wi.category,
                            sequence=wi.sequence,
                            description=wi.description,
                            audit_level=wi.audit_level,
                            deliverables_config=wi.deliverables_config,
                            acceptance_criteria_config=wi.acceptance_criteria_config,
                            execution_steps_config=wi.execution_steps_config,
                            children=[WorkItemTemplateRequest(**child.dict()) for child in (wi.children or [])],
                        ))
                node_requests.append(WorkflowNodeRequest(
                    node_id=node.node_id,
                    name=node.name,
                    sequence=node.sequence,
                    entry_conditions=node.entry_conditions,
                    exit_conditions=node.exit_conditions,
                    mandatory_rules=node.mandatory_rules,
                    work_items=work_items,
                ))
        
        dto = CreateSOPTemplateRequest(
            template_id=request.template_id,
            name=request.name,
            template_type=request.template_type,
            description=request.description,
            audit_matrix_config_id=request.audit_matrix_config_id,
            workflow_nodes=node_requests,
        )
        result = service.create_template(dto, current_user)
        return ApiResponseSchema(data=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=ApiResponseSchema[SOPTemplateListResponseSchema])
def list_templates(
    template_type: Optional[str] = Query(None, description="模板类型"),
    status: Optional[str] = Query(None, description="状态"),
    keyword: Optional[str] = Query(None, description="关键词"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    service: SOPTemplateService = Depends(get_sop_template_service)
):
    """查询 SOP 模板列表"""
    filter_request = SOPTemplateFilterRequest(
        template_type=template_type,
        status=status,
        keyword=keyword,
        page=page,
        page_size=page_size,
    )
    result = service.list_templates(filter_request)
    return ApiResponseSchema(data=result)


@router.get("/by-type/{template_type}", response_model=ApiResponseSchema[Optional[SOPTemplateResponseSchema]])
def get_active_template_by_type(
    template_type: str,
    service: SOPTemplateService = Depends(get_sop_template_service)
):
    """根据类型获取活跃模板"""
    result = service.get_active_template_by_type(template_type)
    return ApiResponseSchema(data=result)


@router.get("/{template_id}", response_model=ApiResponseSchema[SOPTemplateDetailResponseSchema])
def get_template(
    template_id: str,
    service: SOPTemplateService = Depends(get_sop_template_service)
):
    """获取 SOP 模板详情"""
    try:
        result = service.get_template(template_id)
        return ApiResponseSchema(data=result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{template_id}", response_model=ApiResponseSchema[SOPTemplateResponseSchema])
def update_template(
    template_id: str,
    request: UpdateSOPTemplateSchema,
    service: SOPTemplateService = Depends(get_sop_template_service),
    current_user: str = "admin"  # TODO: 从认证获取
):
    """更新 SOP 模板"""
    try:
        dto = UpdateSOPTemplateRequest(
            name=request.name,
            description=request.description,
            audit_matrix_config_id=request.audit_matrix_config_id,
        )
        result = service.update_template(template_id, dto, current_user)
        return ApiResponseSchema(data=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{template_id}", response_model=ApiResponseSchema[bool])
def delete_template(
    template_id: str,
    service: SOPTemplateService = Depends(get_sop_template_service),
    current_user: str = "admin"  # TODO: 从认证获取
):
    """删除 SOP 模板"""
    try:
        result = service.delete_template(template_id, current_user)
        return ApiResponseSchema(data=result, message="模板已删除")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{template_id}/publish", response_model=ApiResponseSchema[SOPTemplateResponseSchema])
def publish_template(
    template_id: str,
    request: PublishSOPTemplateSchema,
    service: SOPTemplateService = Depends(get_sop_template_service),
    current_user: str = "admin"  # TODO: 从认证获取
):
    """发布 SOP 模板"""
    try:
        result = service.publish_template(template_id, current_user)
        return ApiResponseSchema(data=result, message="模板已发布")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{template_id}/deprecate", response_model=ApiResponseSchema[SOPTemplateResponseSchema])
def deprecate_template(
    template_id: str,
    request: DeprecateSOPTemplateSchema,
    service: SOPTemplateService = Depends(get_sop_template_service),
    current_user: str = "admin"  # TODO: 从认证获取
):
    """弃用 SOP 模板"""
    try:
        result = service.deprecate_template(template_id, current_user, request.reason)
        return ApiResponseSchema(data=result, message="模板已弃用")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{template_id}/clone", response_model=ApiResponseSchema[SOPTemplateResponseSchema])
def clone_template(
    template_id: str,
    request: CloneSOPTemplateSchema,
    service: SOPTemplateService = Depends(get_sop_template_service),
    current_user: str = "admin"  # TODO: 从认证获取
):
    """克隆 SOP 模板"""
    try:
        dto = CloneSOPTemplateRequest(
            new_version=request.new_version,
            cloned_by=current_user,
        )
        result = service.clone_template(template_id, dto)
        return ApiResponseSchema(data=result, message="模板已克隆")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{template_id}/instantiate", response_model=ApiResponseSchema[dict])
def instantiate_template(
    template_id: str,
    request: InstantiateSOPTemplateSchema,
    service: SOPTemplateService = Depends(get_sop_template_service),
    current_user: str = "admin"  # TODO: 从认证获取
):
    """实例化 SOP 模板"""
    try:
        dto = InstantiateSOPTemplateRequest(
            plan_id=request.plan_id,
            variable_mapping=request.variable_mapping,
            inventory_scope=request.inventory_scope,
        )
        result = service.instantiate_template(template_id, dto)
        return ApiResponseSchema(data=result, message="模板已实例化")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
