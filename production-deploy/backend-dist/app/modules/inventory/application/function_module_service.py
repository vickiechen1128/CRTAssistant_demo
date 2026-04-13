"""
功能模块应用服务
应用层服务，协调领域层和基础设施层
"""
from datetime import datetime
from typing import Optional, List, Dict, Any

from app.modules.inventory.domain.entities.function_module import FunctionModule
from app.modules.inventory.domain.repositories.function_module_repository import FunctionModuleRepository
from app.modules.inventory.domain.repositories.lifecycle_log_repository import LifecycleLogRepository
from app.modules.inventory.domain.value_objects.module_status import ModuleStatus

from .dtos.function_module_dtos import (
    CreateFunctionModuleDTO,
    UpdateFunctionModuleDTO,
    UpdateModuleStatusDTO,
    LaunchModuleDTO,
    FunctionModuleResponseDTO,
    FunctionModuleTreeDTO,
)


class FunctionModuleService:
    """功能模块应用服务"""

    def __init__(
        self,
        module_repo: FunctionModuleRepository,
        log_repo: Optional[LifecycleLogRepository] = None
    ):
        self._module_repo = module_repo
        self._log_repo = log_repo

    # ==================== 功能模块CRUD ====================

    async def create_module(
        self,
        app_id: str,
        dto: CreateFunctionModuleDTO,
        created_by: str
    ) -> FunctionModuleResponseDTO:
        """创建功能模块"""
        # 检查同一应用下模块编码+版本是否已存在
        exists = await self._module_repo.exists(
            app_id, dto.module_code, dto.version
        )
        if exists:
            raise ValueError(
                f"Module with code '{dto.module_code}' and version '{dto.version}' "
                f"already exists in this application"
            )

        # 创建实体
        module = FunctionModule.create(
            app_id=app_id,
            module_code=dto.module_code,
            module_name=dto.module_name,
            owner=created_by,
            created_by=created_by,
            module_description=dto.description,
            version=dto.version,
            parent_module_id=dto.parent_module_id,
            related_plan_id=dto.related_plan_id,
        )

        # 保存
        saved = await self._module_repo.save(module)

        # 记录生命周期日志
        if self._log_repo:
            await self._log_repo.create_change_log(
                app_id=app_id,
                log_type="module_launch",
                title=f"创建功能模块: {dto.module_name}",
                after_data={
                    "module_code": dto.module_code,
                    "module_name": dto.module_name,
                    "version": dto.version,
                },
                module_id=saved.id,
                operator=created_by
            )

        return self._to_response_dto(saved)

    async def update_module(
        self,
        module_id: str,
        dto: UpdateFunctionModuleDTO,
        updated_by: str
    ) -> FunctionModuleResponseDTO:
        """更新功能模块"""
        module = await self._module_repo.get_by_id(module_id)
        if not module:
            raise ValueError(f"Module with id '{module_id}' not found")

        # 记录变更前数据
        before_data = {
            "module_name": module.module_name,
            "module_description": module.module_description,
            "parent_module_id": module.parent_module_id,
        }

        # 更新
        changes = module.update(
            module_name=dto.module_name,
            module_description=dto.description,
            parent_module_id=dto.parent_module_id,
            updated_by=updated_by
        )

        saved = await self._module_repo.update(module)

        # 记录生命周期日志
        if self._log_repo and changes:
            await self._log_repo.create_change_log(
                app_id=module.app_id,
                log_type="module_update",
                title=f"更新功能模块: {module.module_name}",
                before_data=before_data,
                after_data={
                    "module_name": saved.module_name,
                    "module_description": saved.module_description,
                    "parent_module_id": saved.parent_module_id,
                },
                module_id=saved.id,
                operator=updated_by
            )

        return self._to_response_dto(saved)

    async def get_module(self, module_id: str) -> FunctionModuleResponseDTO:
        """获取功能模块详情"""
        module = await self._module_repo.get_by_id(module_id)
        if not module:
            raise ValueError(f"Module with id '{module_id}' not found")

        return self._to_response_dto(module)

    async def list_modules(
        self,
        app_id: str,
        status: Optional[str] = None
    ) -> List[FunctionModuleResponseDTO]:
        """获取应用的功能模块列表"""
        modules = await self._module_repo.get_by_app_id(app_id)

        if status:
            modules = [m for m in modules if m.status.value == status]

        return [self._to_response_dto(m) for m in modules]

    async def get_module_tree(self, app_id: str) -> List[FunctionModuleTreeDTO]:
        """获取功能模块树形结构"""
        modules = await self._module_repo.get_by_app_id(app_id)

        # 构建树形结构
        module_map: Dict[str, FunctionModule] = {m.id: m for m in modules}
        root_modules: List[FunctionModule] = []
        children_map: Dict[str, List[str]] = {}

        for m in modules:
            if m.parent_module_id:
                if m.parent_module_id not in children_map:
                    children_map[m.parent_module_id] = []
                children_map[m.parent_module_id].append(m.id)
            else:
                root_modules.append(m)

        def build_tree(module: FunctionModule) -> FunctionModuleTreeDTO:
            children = children_map.get(module.id, [])
            return FunctionModuleTreeDTO(
                id=module.id,
                module_code=module.module_code,
                module_name=module.module_name,
                version=module.version,
                status=module.status.value,
                status_display=module.status.label,
                children=[build_tree(module_map[cid]) for cid in children if cid in module_map]
            )

        return [build_tree(m) for m in root_modules]

    async def delete_module(self, module_id: str, deleted_by: str) -> bool:
        """删除功能模块"""
        module = await self._module_repo.get_by_id(module_id)
        if not module:
            raise ValueError(f"Module with id '{module_id}' not found")

        # 检查是否有子模块
        children = await self._module_repo.get_children(module_id)
        if children:
            raise ValueError("Cannot delete module with child modules")

        # 删除
        success = await self._module_repo.delete(module_id)

        # 记录生命周期日志
        if success and self._log_repo:
            await self._log_repo.create_change_log(
                app_id=module.app_id,
                log_type="module_offline",
                title=f"删除功能模块: {module.module_name}",
                before_data={
                    "module_code": module.module_code,
                    "module_name": module.module_name,
                    "version": module.version,
                },
                operator=deleted_by
            )

        return success

    # ==================== 状态管理 ====================

    async def update_status(
        self,
        module_id: str,
        dto: UpdateModuleStatusDTO
    ) -> FunctionModuleResponseDTO:
        """更新功能模块状态"""
        module = await self._module_repo.get_by_id(module_id)
        if not module:
            raise ValueError(f"Module with id '{module_id}' not found")

        # 验证状态转换
        new_status = ModuleStatus.from_string(dto.status)
        if not module.status.can_transition_to(new_status):
            raise ValueError(
                f"Cannot transition from {module.status.label} to {new_status.label}"
            )

        old_status = module.status

        # 使用领域模型的状态变更方法
        change_info = module.change_status(new_status, dto.operator)

        saved = await self._module_repo.update(module)

        # 记录生命周期日志
        if self._log_repo:
            await self._log_repo.create_change_log(
                app_id=module.app_id,
                log_type="status_change",
                title=f"功能模块状态变更: {module.module_name}",
                before_data={"status": old_status.value},
                after_data={"status": new_status.value},
                module_id=saved.id,
                operator=dto.operator
            )

        return self._to_response_dto(saved)

    async def launch_module(
        self,
        module_id: str,
        dto: LaunchModuleDTO
    ) -> FunctionModuleResponseDTO:
        """上线功能模块"""
        module = await self._module_repo.get_by_id(module_id)
        if not module:
            raise ValueError(f"Module with id '{module_id}' not found")

        # 验证状态
        if module.status.value != "testing":
            raise ValueError("Module must be in testing status to launch")

        # 执行上线
        saved = await self._module_repo.launch_module(
            module_id, dto.plan_id, dto.operator
        )

        if not saved:
            raise ValueError("Failed to launch module")

        # 记录生命周期日志
        if self._log_repo:
            await self._log_repo.create_module_launch_log(
                app_id=module.app_id,
                module_name=module.module_name,
                plan_id=dto.plan_id,
                operator=dto.operator
            )

        return self._to_response_dto(saved)

    async def get_version_history(
        self,
        app_id: str,
        module_code: str
    ) -> List[FunctionModuleResponseDTO]:
        """获取功能模块版本历史"""
        # 获取所有模块，过滤出相同module_code的
        modules = await self._module_repo.get_by_app_id(app_id)
        versions = [m for m in modules if m.module_code == module_code]

        # 按版本号排序
        versions.sort(key=lambda m: m.version, reverse=True)

        return [self._to_response_dto(m) for m in versions]

    # ==================== 辅助方法 ====================

    def _to_response_dto(
        self,
        module: FunctionModule
    ) -> FunctionModuleResponseDTO:
        """转换为响应DTO"""
        return FunctionModuleResponseDTO(
            id=module.id,
            app_id=module.app_id,
            module_code=module.module_code,
            module_name=module.module_name,
            version=module.version,
            status=module.status.value if hasattr(module.status, 'value') else str(module.status),
            status_display=module.status.label if hasattr(module.status, 'label') else str(module.status),
            parent_module_id=module.parent_module_id,
            related_plan_id=module.related_plan_id,
            launch_time=module.launch_time.isoformat() if module.launch_time else None,
            description=module.module_description,
            child_count=0,  # 需要单独查询
            created_at=module.created_at.isoformat() if module.created_at else None,
            updated_at=module.updated_at.isoformat() if module.updated_at else None,
        )
