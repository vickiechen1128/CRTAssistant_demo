"""
台账管理API路由
提供应用系统、云资源、账号的CRUD接口
"""
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user_optional
from app.core.response import success_response, error_response

from ....application.inventory_service import InventoryService
from ....application.dtos.inventory_dtos import (
    CreateApplicationDTO,
    UpdateApplicationDTO,
    CreateCloudResourceDTO,
    UpdateCloudResourceDTO,
    CreateAccountDTO,
    UpdateAccountDTO,
    ExtendValidityDTO,
    PlanLinkDTO,
)
from ....infrastructure.persistence.inventory_repository_impl import InventoryRepositoryImpl
from ...api.schemas.inventory_schemas import (
    ApplicationCreateSchema,
    ApplicationUpdateSchema,
    ApplicationResponseSchema,
    CloudResourceCreateSchema,
    CloudResourceUpdateSchema,
    CloudResourceResponseSchema,
    AccountCreateSchema,
    AccountUpdateSchema,
    AccountResponseSchema,
    AccountExtendValiditySchema,
    PlanLinkSchema,
    InventorySummarySchema,
    MessageResponseSchema,
    PaginatedApplicationResponseSchema,
    PaginatedCloudResourceResponseSchema,
    PaginatedAccountResponseSchema,
)

router = APIRouter(prefix="/inventory", tags=["inventory"])


def get_inventory_service(db: Session = Depends(get_db)) -> InventoryService:
    """依赖注入：获取台账服务"""
    repo = InventoryRepositoryImpl(db)
    return InventoryService(repo)


# ==================== 汇总统计接口 ====================

@router.get(
    "/summary",
    response_model=InventorySummarySchema,
    summary="获取台账汇总统计"
)
def get_inventory_summary(
    service: InventoryService = Depends(get_inventory_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """获取台账汇总统计信息"""
    return service.get_inventory_summary()


# ==================== 应用系统接口 ====================

@router.post(
    "/applications",
    response_model=ApplicationResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="创建应用系统"
)
def create_application(
    schema: ApplicationCreateSchema,
    service: InventoryService = Depends(get_inventory_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """创建新的应用系统台账"""
    try:
        dto = CreateApplicationDTO(
            app_name=schema.app_name,
            business_owner=schema.business_owner,
            project_owner=schema.project_owner,
            app_description=schema.app_description,
            hostname=schema.hostname,
            app_url=schema.app_url,
            function_modules=schema.function_modules,
            launch_time=schema.launch_time,
        )
        result = service.create_application(dto, (current_user or {}).get("username", "system"))
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/applications",
    summary="获取应用系统列表"
)
def list_applications(
    status: Optional[str] = Query(None, description="状态筛选"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    service: InventoryService = Depends(get_inventory_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """获取应用系统列表（支持分页和筛选）"""
    try:
        result = service.list_applications(status, keyword, page, size)
        return success_response({
            "page": result.page,
            "size": result.size,
            "total": result.total,
            "total_pages": result.total_pages,
            "items": result.data
        })
    except Exception as e:
        return error_response(str(e), "获取应用系统列表失败")


@router.get(
    "/applications/{app_id}",
    response_model=ApplicationResponseSchema,
    summary="获取应用系统详情"
)
def get_application(
    app_id: str,
    service: InventoryService = Depends(get_inventory_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """获取应用系统详情"""
    try:
        return service.get_application(app_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put(
    "/applications/{app_id}",
    response_model=ApplicationResponseSchema,
    summary="更新应用系统"
)
def update_application(
    app_id: str,
    schema: ApplicationUpdateSchema,
    service: InventoryService = Depends(get_inventory_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """更新应用系统信息"""
    try:
        dto = UpdateApplicationDTO(
            app_description=schema.app_description,
            hostname=schema.hostname,
            app_url=schema.app_url,
            business_owner=schema.business_owner,
            project_owner=schema.project_owner,
            launch_time=schema.launch_time,
        )
        return service.update_application(app_id, dto, (current_user or {}).get("username", "system"))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete(
    "/applications/{app_id}",
    response_model=MessageResponseSchema,
    summary="删除应用系统"
)
def delete_application(
    app_id: str,
    service: InventoryService = Depends(get_inventory_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """删除应用系统（仅当无关联计划和资源时）"""
    try:
        service.delete_application(app_id, (current_user or {}).get("username", "system"))
        return {"message": "Application deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch(
    "/applications/{app_id}/status",
    response_model=ApplicationResponseSchema,
    summary="变更应用系统状态"
)
def change_application_status(
    app_id: str,
    new_status: str = Query(..., pattern="^(active|inactive|archived)$"),
    service: InventoryService = Depends(get_inventory_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """变更应用系统状态（active/inactive/archived）"""
    try:
        return service.change_application_status(
            app_id, new_status, (current_user or {}).get("username", "system")
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== 云资源接口 ====================

@router.post(
    "/cloud-resources",
    response_model=CloudResourceResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="创建云资源"
)
def create_cloud_resource(
    schema: CloudResourceCreateSchema,
    service: InventoryService = Depends(get_inventory_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """创建新的云服务资源"""
    try:
        dto = CreateCloudResourceDTO(
            app_id=schema.app_id,
            resource_type=schema.resource_type,
            resource_name=schema.resource_name,
            configuration=schema.configuration,
        )
        return service.create_cloud_resource(dto, (current_user or {}).get("username", "system"))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/cloud-resources",
    response_model=PaginatedCloudResourceResponseSchema,
    summary="获取云资源列表"
)
def list_cloud_resources(
    app_id: Optional[str] = Query(None, description="应用ID筛选"),
    resource_type: Optional[str] = Query(None, description="资源类型筛选"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    service: InventoryService = Depends(get_inventory_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """获取云资源列表（支持分页和筛选）"""
    result = service.list_cloud_resources(app_id, resource_type, keyword, page, size)
    return {
        "page": result.page,
        "size": result.size,
        "total": result.total,
        "total_pages": result.total_pages,
        "data": result.data
    }


@router.get(
    "/cloud-resources/{resource_id}",
    response_model=CloudResourceResponseSchema,
    summary="获取云资源详情"
)
def get_cloud_resource(
    resource_id: str,
    service: InventoryService = Depends(get_inventory_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """获取云资源详情"""
    try:
        return service.get_cloud_resource(resource_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put(
    "/cloud-resources/{resource_id}",
    response_model=CloudResourceResponseSchema,
    summary="更新云资源"
)
def update_cloud_resource(
    resource_id: str,
    schema: CloudResourceUpdateSchema,
    service: InventoryService = Depends(get_inventory_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """更新云资源信息"""
    try:
        dto = UpdateCloudResourceDTO(
            resource_name=schema.resource_name,
            configuration=schema.configuration,
        )
        return service.update_cloud_resource(
            resource_id, dto, (current_user or {}).get("username", "system")
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete(
    "/cloud-resources/{resource_id}",
    response_model=MessageResponseSchema,
    summary="删除云资源"
)
def delete_cloud_resource(
    resource_id: str,
    service: InventoryService = Depends(get_inventory_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """删除云资源"""
    try:
        service.delete_cloud_resource(resource_id, (current_user or {}).get("username", "system"))
        return {"message": "Cloud resource deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== 账号接口 ====================

@router.post(
    "/accounts",
    response_model=AccountResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="创建账号"
)
def create_account(
    schema: AccountCreateSchema,
    service: InventoryService = Depends(get_inventory_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """创建新的系统或软件账号"""
    try:
        dto = CreateAccountDTO(
            app_id=schema.app_id,
            account_type=schema.account_type,
            account_name=schema.account_name,
            permission_level=schema.permission_level,
            holder_name=schema.holder_name,
            valid_from=schema.valid_from,
            valid_until=schema.valid_until,
            password_change_cycle=schema.password_change_cycle,
        )
        return service.create_account(dto, (current_user or {}).get("username", "system"))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/accounts",
    response_model=PaginatedAccountResponseSchema,
    summary="获取账号列表"
)
def list_accounts(
    app_id: Optional[str] = Query(None, description="应用ID筛选"),
    account_type: Optional[str] = Query(None, description="账号类型筛选"),
    status: Optional[str] = Query(None, description="状态筛选"),
    permission_level: Optional[str] = Query(None, description="权限级别筛选"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    service: InventoryService = Depends(get_inventory_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """获取账号列表（支持分页和筛选）"""
    result = service.list_accounts(
        app_id, account_type, status, permission_level, keyword, page, size
    )
    return {
        "page": result.page,
        "size": result.size,
        "total": result.total,
        "total_pages": result.total_pages,
        "data": result.data
    }


@router.get(
    "/accounts/expiring",
    response_model=List[AccountResponseSchema],
    summary="获取即将过期的账号"
)
def get_expiring_accounts(
    days: int = Query(30, ge=1, le=365, description="即将过期的天数"),
    service: InventoryService = Depends(get_inventory_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """获取即将过期的账号列表"""
    return service.get_expiring_accounts(days)


@router.get(
    "/accounts/{account_id}",
    response_model=AccountResponseSchema,
    summary="获取账号详情"
)
def get_account(
    account_id: str,
    service: InventoryService = Depends(get_inventory_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """获取账号详情"""
    try:
        return service.get_account(account_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put(
    "/accounts/{account_id}",
    response_model=AccountResponseSchema,
    summary="更新账号"
)
def update_account(
    account_id: str,
    schema: AccountUpdateSchema,
    service: InventoryService = Depends(get_inventory_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """更新账号信息"""
    try:
        dto = UpdateAccountDTO(
            permission_level=schema.permission_level,
            holder_name=schema.holder_name,
            valid_until=schema.valid_until,
            password_change_cycle=schema.password_change_cycle,
        )
        return service.update_account(account_id, dto, (current_user or {}).get("username", "system"))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/accounts/{account_id}/extend",
    response_model=AccountResponseSchema,
    summary="延长账号有效期"
)
def extend_account_validity(
    account_id: str,
    schema: AccountExtendValiditySchema,
    service: InventoryService = Depends(get_inventory_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """延长账号有效期"""
    try:
        return service.extend_account_validity(
            account_id, schema.days, (current_user or {}).get("username", "system")
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete(
    "/accounts/{account_id}",
    response_model=MessageResponseSchema,
    summary="删除账号"
)
def delete_account(
    account_id: str,
    service: InventoryService = Depends(get_inventory_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """删除账号"""
    try:
        service.delete_account(account_id, (current_user or {}).get("username", "system"))
        return {"message": "Account deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== 计划关联接口 ====================

@router.post(
    "/{inventory_type}/{inventory_id}/link-plan",
    response_model=MessageResponseSchema,
    summary="关联计划到台账"
)
def link_plan_to_inventory(
    inventory_type: str,
    inventory_id: str,
    schema: PlanLinkSchema,
    service: InventoryService = Depends(get_inventory_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """关联计划到台账"""
    valid_types = ["application", "cloud_resource", "account"]
    if inventory_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid inventory type. Must be one of: {valid_types}"
        )
    
    success = service.link_plan_to_inventory(
        inventory_type, inventory_id, schema.plan_id,
        (current_user or {}).get("username", "system")
    )
    
    if success:
        return {"message": "Plan linked successfully"}
    else:
        raise HTTPException(status_code=400, detail="Failed to link plan")


@router.post(
    "/{inventory_type}/{inventory_id}/unlink-plan",
    response_model=MessageResponseSchema,
    summary="解除计划与台账的关联"
)
def unlink_plan_from_inventory(
    inventory_type: str,
    inventory_id: str,
    schema: PlanLinkSchema,
    service: InventoryService = Depends(get_inventory_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """解除计划与台账的关联"""
    valid_types = ["application", "cloud_resource", "account"]
    if inventory_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid inventory type. Must be one of: {valid_types}"
        )
    
    success = service.unlink_plan_from_inventory(
        inventory_type, inventory_id, schema.plan_id,
        (current_user or {}).get("username", "system")
    )
    
    if success:
        return {"message": "Plan unlinked successfully"}
    else:
        raise HTTPException(status_code=400, detail="Failed to unlink plan")
