"""
功能模块API路由
"""
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user_optional

from ....application.function_module_service import FunctionModuleService
from ....application.dtos.function_module_dtos import (
    CreateFunctionModuleDTO,
    UpdateFunctionModuleDTO,
    UpdateModuleStatusDTO,
    LaunchModuleDTO,
)
from ....infrastructure.persistence.repositories.function_module_repository_impl import FunctionModuleRepositoryImpl
from ....infrastructure.persistence.repositories.lifecycle_log_repository_impl import LifecycleLogRepositoryImpl
from ...api.schemas.function_module_schemas import (
    FunctionModuleCreateSchema,
    FunctionModuleUpdateSchema,
    UpdateModuleStatusSchema,
    LaunchModuleSchema,
    FunctionModuleResponseSchema,
    FunctionModuleTreeSchema,
    FunctionModuleListResponseSchema,
    FunctionModuleVersionHistorySchema,
)

router = APIRouter(prefix="/applications/{app_id}/modules", tags=["function-modules"])


def get_function_module_service(
    db: Session = Depends(get_db)
) -> FunctionModuleService:
    """依赖注入：获取功能模块服务"""
    module_repo = FunctionModuleRepositoryImpl(db)
    log_repo = LifecycleLogRepositoryImpl(db)
    return FunctionModuleService(module_repo, log_repo)


@router.post(
    "",
    response_model=FunctionModuleResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="创建功能模块"
)
async def create_module(
    app_id: str,
    schema: FunctionModuleCreateSchema,
    service: FunctionModuleService = Depends(get_function_module_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """创建新的功能模块"""
    try:
        dto = CreateFunctionModuleDTO(
            module_code=schema.module_code,
            module_name=schema.module_name,
            version=schema.version,
            parent_module_id=schema.parent_module_id,
            related_plan_id=schema.related_plan_id,
            description=schema.description,
        )
        result = await service.create_module(
            app_id,
            dto,
            (current_user or {}).get("username", "system")
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "",
    response_model=FunctionModuleListResponseSchema,
    summary="获取功能模块列表"
)
async def list_modules(
    app_id: str,
    status: Optional[str] = Query(None, description="状态过滤"),
    service: FunctionModuleService = Depends(get_function_module_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """获取应用的功能模块列表"""
    modules = await service.list_modules(app_id, status)
    return FunctionModuleListResponseSchema(
        items=modules,
        total=len(modules)
    )


@router.get(
    "/tree",
    response_model=List[FunctionModuleTreeSchema],
    summary="获取功能模块树"
)
async def get_module_tree(
    app_id: str,
    service: FunctionModuleService = Depends(get_function_module_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """获取功能模块的树形结构"""
    return await service.get_module_tree(app_id)


@router.get(
    "/{module_id}",
    response_model=FunctionModuleResponseSchema,
    summary="获取功能模块详情"
)
async def get_module(
    app_id: str,
    module_id: str,
    service: FunctionModuleService = Depends(get_function_module_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """获取功能模块详情"""
    try:
        return await service.get_module(module_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put(
    "/{module_id}",
    response_model=FunctionModuleResponseSchema,
    summary="更新功能模块"
)
async def update_module(
    app_id: str,
    module_id: str,
    schema: FunctionModuleUpdateSchema,
    service: FunctionModuleService = Depends(get_function_module_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """更新功能模块"""
    try:
        dto = UpdateFunctionModuleDTO(
            module_name=schema.module_name,
            description=schema.description,
            parent_module_id=schema.parent_module_id,
        )
        return await service.update_module(
            module_id,
            dto,
            (current_user or {}).get("username", "system")
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete(
    "/{module_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除功能模块"
)
async def delete_module(
    app_id: str,
    module_id: str,
    service: FunctionModuleService = Depends(get_function_module_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """删除功能模块"""
    try:
        success = await service.delete_module(
            module_id,
            (current_user or {}).get("username", "system")
        )
        if not success:
            raise HTTPException(status_code=400, detail="Failed to delete module")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch(
    "/{module_id}/status",
    response_model=FunctionModuleResponseSchema,
    summary="更新功能模块状态"
)
async def update_module_status(
    app_id: str,
    module_id: str,
    schema: UpdateModuleStatusSchema,
    service: FunctionModuleService = Depends(get_function_module_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """更新功能模块状态"""
    try:
        dto = UpdateModuleStatusDTO(
            status=schema.status,
            operator=(current_user or {}).get("username", "system")
        )
        return await service.update_status(module_id, dto)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/{module_id}/launch",
    response_model=FunctionModuleResponseSchema,
    summary="上线功能模块"
)
async def launch_module(
    app_id: str,
    module_id: str,
    schema: LaunchModuleSchema,
    service: FunctionModuleService = Depends(get_function_module_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """上线功能模块"""
    try:
        dto = LaunchModuleDTO(
            plan_id=schema.plan_id,
            operator=(current_user or {}).get("username", "system")
        )
        return await service.launch_module(module_id, dto)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/{module_id}/versions",
    response_model=FunctionModuleVersionHistorySchema,
    summary="获取功能模块版本历史"
)
async def get_version_history(
    app_id: str,
    module_id: str,
    service: FunctionModuleService = Depends(get_function_module_service),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """获取功能模块的版本历史"""
    # 先获取模块信息以获取module_code
    module = await service.get_module(module_id)
    versions = await service.get_version_history(app_id, module.module_code)
    return FunctionModuleVersionHistorySchema(versions=versions)
