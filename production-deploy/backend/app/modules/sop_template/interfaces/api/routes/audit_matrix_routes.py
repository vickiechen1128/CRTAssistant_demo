"""
审核矩阵路由
FastAPI 路由定义
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db

from ....application.audit_matrix_service import AuditMatrixService
from ....application.dtos.audit_matrix_dtos import (
    CreateAuditMatrixRequest,
    UpdateAuditMatrixRequest,
    AuditMatrixFilterRequest,
    AuditRuleRequest,
)
from ....infrastructure.persistence.audit_matrix_repository_impl import AuditMatrixRepositoryImpl
from ..schemas.audit_matrix_schemas import (
    CreateAuditMatrixSchema,
    UpdateAuditMatrixSchema,
    AuditMatrixResponseSchema,
    AuditMatrixListResponseSchema,
    AuditRuleSchema,
    UpdateAuditRuleSchema,
    ApiResponseSchema,
)

router = APIRouter(prefix="/audit-matrix-configs", tags=["审核矩阵管理"])


def get_audit_matrix_service(db: Session = Depends(get_db)) -> AuditMatrixService:
    """依赖注入：获取 AuditMatrixService 实例"""
    repository = AuditMatrixRepositoryImpl(db)
    return AuditMatrixService(repository)


@router.post("", response_model=ApiResponseSchema[AuditMatrixResponseSchema])
def create_matrix(
    request: CreateAuditMatrixSchema,
    service: AuditMatrixService = Depends(get_audit_matrix_service),
    current_user: str = "admin"  # TODO: 从认证获取
):
    """创建审核矩阵配置"""
    try:
        # 转换规则
        rule_requests = []
        if request.rules:
            for rule in request.rules:
                rule_requests.append(AuditRuleRequest(
                    audit_level=rule.audit_level,
                    primary_method=rule.primary_method,
                    secondary_method=rule.secondary_method,
                    sampling_ratio=rule.sampling_ratio,
                    auto_pass_threshold=rule.auto_pass_threshold,
                    mandatory_reviewer_role=rule.mandatory_reviewer_role,
                    escalation_rule=rule.escalation_rule,
                ))
        
        dto = CreateAuditMatrixRequest(
            config_id=request.config_id,
            name=request.name,
            description=request.description,
            rules=rule_requests,
        )
        result = service.create_matrix(dto, current_user)
        return ApiResponseSchema(data=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=ApiResponseSchema[AuditMatrixListResponseSchema])
def list_matrices(
    status: Optional[str] = Query(None, description="状态"),
    keyword: Optional[str] = Query(None, description="关键词"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    service: AuditMatrixService = Depends(get_audit_matrix_service)
):
    """查询审核矩阵列表"""
    filter_request = AuditMatrixFilterRequest(
        status=status,
        keyword=keyword,
        page=page,
        page_size=page_size,
    )
    result = service.list_matrices(filter_request)
    return ApiResponseSchema(data=result)


@router.get("/{config_id}", response_model=ApiResponseSchema[AuditMatrixResponseSchema])
def get_matrix(
    config_id: str,
    service: AuditMatrixService = Depends(get_audit_matrix_service)
):
    """获取审核矩阵详情"""
    try:
        result = service.get_matrix(config_id)
        return ApiResponseSchema(data=result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{config_id}", response_model=ApiResponseSchema[AuditMatrixResponseSchema])
def update_matrix(
    config_id: str,
    request: UpdateAuditMatrixSchema,
    service: AuditMatrixService = Depends(get_audit_matrix_service),
    current_user: str = "admin"  # TODO: 从认证获取
):
    """更新审核矩阵配置"""
    try:
        dto = UpdateAuditMatrixRequest(
            name=request.name,
            description=request.description,
        )
        result = service.update_matrix(config_id, dto, current_user)
        return ApiResponseSchema(data=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{config_id}", response_model=ApiResponseSchema[bool])
def delete_matrix(
    config_id: str,
    service: AuditMatrixService = Depends(get_audit_matrix_service),
    current_user: str = "admin"  # TODO: 从认证获取
):
    """删除审核矩阵配置"""
    try:
        result = service.delete_matrix(config_id, current_user)
        return ApiResponseSchema(data=result, message="审核矩阵已删除")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{config_id}/activate", response_model=ApiResponseSchema[AuditMatrixResponseSchema])
def activate_matrix(
    config_id: str,
    service: AuditMatrixService = Depends(get_audit_matrix_service),
    current_user: str = "admin"  # TODO: 从认证获取
):
    """激活审核矩阵"""
    try:
        result = service.activate_matrix(config_id, current_user)
        return ApiResponseSchema(data=result, message="审核矩阵已激活")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{config_id}/deactivate", response_model=ApiResponseSchema[AuditMatrixResponseSchema])
def deactivate_matrix(
    config_id: str,
    service: AuditMatrixService = Depends(get_audit_matrix_service),
    current_user: str = "admin"  # TODO: 从认证获取
):
    """停用审核矩阵"""
    try:
        result = service.deactivate_matrix(config_id, current_user)
        return ApiResponseSchema(data=result, message="审核矩阵已停用")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{config_id}/rules", response_model=ApiResponseSchema[AuditMatrixResponseSchema])
def add_rule(
    config_id: str,
    request: AuditRuleSchema,
    service: AuditMatrixService = Depends(get_audit_matrix_service),
    current_user: str = "admin"  # TODO: 从认证获取
):
    """添加审核规则"""
    try:
        dto = AuditRuleRequest(
            audit_level=request.audit_level,
            primary_method=request.primary_method,
            secondary_method=request.secondary_method,
            sampling_ratio=request.sampling_ratio,
            auto_pass_threshold=request.auto_pass_threshold,
            mandatory_reviewer_role=request.mandatory_reviewer_role,
            escalation_rule=request.escalation_rule,
        )
        result = service.add_rule(config_id, dto, current_user)
        return ApiResponseSchema(data=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{config_id}/rules/{rule_id}", response_model=ApiResponseSchema[AuditMatrixResponseSchema])
def update_rule(
    config_id: str,
    rule_id: str,
    request: UpdateAuditRuleSchema,
    service: AuditMatrixService = Depends(get_audit_matrix_service),
    current_user: str = "admin"  # TODO: 从认证获取
):
    """更新审核规则"""
    try:
        dto = AuditRuleRequest(
            audit_level="normal",  # 更新时不修改等级
            primary_method=request.primary_method,
            secondary_method=request.secondary_method,
            sampling_ratio=request.sampling_ratio,
            auto_pass_threshold=request.auto_pass_threshold,
            mandatory_reviewer_role=request.mandatory_reviewer_role,
            escalation_rule=request.escalation_rule,
        )
        result = service.update_rule(config_id, rule_id, dto, current_user)
        return ApiResponseSchema(data=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{config_id}/rules/{rule_id}", response_model=ApiResponseSchema[AuditMatrixResponseSchema])
def delete_rule(
    config_id: str,
    rule_id: str,
    service: AuditMatrixService = Depends(get_audit_matrix_service),
    current_user: str = "admin"  # TODO: 从认证获取
):
    """删除审核规则"""
    try:
        result = service.delete_rule(config_id, rule_id, current_user)
        return ApiResponseSchema(data=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
