"""
台账操作服务实现
与台账管理模块的实际交互
"""
import asyncio
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any

from ...domain.services.inventory_service import (
    InventoryService,
    InventoryLifecycleLogService,
    InventoryOperationResult,
)

# 导入台账管理模块的服务和DTO
from app.modules.inventory.application.inventory_service import InventoryService as InventoryAppService
from app.modules.inventory.application.function_module_service import FunctionModuleService
from app.modules.inventory.application.lifecycle_log_service import LifecycleLogService
from app.modules.inventory.application.dtos.inventory_dtos import (
    CreateApplicationDTO,
    UpdateApplicationDTO,
    FunctionModuleDTO,
)
from app.modules.inventory.application.dtos.function_module_dtos import (
    CreateFunctionModuleDTO,
    UpdateFunctionModuleDTO,
)
from app.modules.inventory.application.dtos.lifecycle_log_dtos import CreateLifecycleLogDTO
from app.modules.inventory.infrastructure.persistence.inventory_repository_impl import InventoryRepositoryImpl
from app.modules.inventory.infrastructure.persistence.repositories.function_module_repository_impl import FunctionModuleRepositoryImpl
from app.modules.inventory.infrastructure.persistence.repositories.lifecycle_log_repository_impl import LifecycleLogRepositoryImpl


class InventoryServiceImpl(InventoryService):
    """
    台账操作服务实现
    实际调用台账管理模块的接口
    """

    def __init__(self, db_session=None):
        self._db = db_session
        # 初始化台账管理模块的仓储和服务
        if db_session:
            self._inventory_repo = InventoryRepositoryImpl(db_session)
            self._module_repo = FunctionModuleRepositoryImpl(db_session)
            self._log_repo = LifecycleLogRepositoryImpl(db_session)

            self._inventory_service = InventoryAppService(self._inventory_repo)
            self._module_service = FunctionModuleService(self._module_repo, self._log_repo)
            self._log_service = LifecycleLogService(self._log_repo)
        else:
            self._inventory_service = None
            self._module_service = None
            self._log_service = None

    def _run_async(self, coro):
        """辅助方法：运行异步协程"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # 如果事件循环已经在运行，使用 run_coroutine_threadsafe
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, coro)
                    return future.result()
            else:
                return loop.run_until_complete(coro)
        except RuntimeError:
            # 没有事件循环，创建一个新的
            return asyncio.run(coro)

    def create_application(
        self,
        app_data: Dict[str, Any],
        modules: List[Dict[str, Any]],
        cloud_resources: List[Dict[str, Any]],
        accounts: List[Dict[str, Any]],
        related_plan_id: str
    ) -> InventoryOperationResult:
        """
        创建应用系统台账
        用于 new_system 分类
        """
        try:
            if not self._inventory_service:
                raise ValueError("Database session not initialized")

            # 转换功能模块数据
            function_modules = []
            for module_data in modules:
                function_modules.append(FunctionModuleDTO(
                    module_name=module_data.get("module_name", ""),
                    launch_time=datetime.utcnow().isoformat()
                ))

            # 创建应用系统DTO
            create_dto = CreateApplicationDTO(
                app_name=app_data.get("app_name", ""),
                business_owner=app_data.get("business_owner", ""),
                project_owner=app_data.get("project_owner", ""),
                app_description=app_data.get("app_description"),
                hostname=app_data.get("hostname"),
                app_url=app_data.get("app_url"),
                function_modules=function_modules if function_modules else None,
                launch_time=app_data.get("launch_time") or datetime.utcnow().isoformat(),
            )

            # 调用台账管理服务创建应用系统
            created_by = app_data.get("business_owner", "system")
            result = self._inventory_service.create_application(create_dto, created_by)

            # 创建功能模块（如果创建应用系统时没有自动创建）
            created_module_ids = []
            for module_data in modules:
                module_dto = CreateFunctionModuleDTO(
                    module_code=module_data.get("module_code", f"MOD-{uuid.uuid4().hex[:6]}"),
                    module_name=module_data.get("module_name", ""),
                    version=module_data.get("version", "1.0.0"),
                    description=module_data.get("module_description"),
                    related_plan_id=related_plan_id,
                )
                module_result = self._run_async(self._module_service.create_module(
                    result.id, module_dto, created_by
                ))
                created_module_ids.append(module_result.id)

            return InventoryOperationResult(
                success=True,
                inventory_id=result.id,
                module_ids=created_module_ids,
                lifecycle_logs=[
                    {
                        "log_type": "system_launch",
                        "event_title": f"【系统上线】{result.app_name} 正式上线",
                    }
                ]
            )
        except Exception as e:
            return InventoryOperationResult(
                success=False,
                error_message=str(e)
            )

    def create_function_modules(
        self,
        app_id: str,
        modules: List[Dict[str, Any]],
        related_plan_id: str
    ) -> InventoryOperationResult:
        """
        创建功能模块
        用于 new_feature 分类
        """
        try:
            if not self._module_service:
                raise ValueError("Database session not initialized")

            created_module_ids = []
            created_by = "system"

            for module_data in modules:
                module_dto = CreateFunctionModuleDTO(
                    module_code=module_data.get("module_code", f"MOD-{uuid.uuid4().hex[:6]}"),
                    module_name=module_data.get("module_name", ""),
                    version=module_data.get("version", "1.0.0"),
                    description=module_data.get("module_description"),
                    related_plan_id=related_plan_id,
                    parent_module_id=module_data.get("parent_module_id"),
                )

                result = self._run_async(self._module_service.create_module(
                    app_id, module_dto, created_by
                ))
                created_module_ids.append(result.id)

            return InventoryOperationResult(
                success=True,
                inventory_id=app_id,
                module_ids=created_module_ids,
            )
        except Exception as e:
            return InventoryOperationResult(
                success=False,
                error_message=str(e)
            )

    def update_function_modules(
        self,
        app_id: str,
        module_updates: List[Dict[str, Any]],
        related_plan_id: str
    ) -> InventoryOperationResult:
        """
        更新功能模块
        用于 func_change 分类
        """
        try:
            if not self._module_service:
                raise ValueError("Database session not initialized")

            updated_module_ids = []
            updated_by = "system"

            for module_data in module_updates:
                module_id = module_data.get("module_id")
                if not module_id:
                    continue

                update_dto = UpdateFunctionModuleDTO(
                    module_name=module_data.get("module_name"),
                    description=module_data.get("change_description"),
                    parent_module_id=module_data.get("parent_module_id"),
                )

                result = self._run_async(self._module_service.update_module(
                    module_id, update_dto, updated_by
                ))
                updated_module_ids.append(result.id)

            return InventoryOperationResult(
                success=True,
                inventory_id=app_id,
                module_ids=updated_module_ids,
            )
        except Exception as e:
            return InventoryOperationResult(
                success=False,
                error_message=str(e)
            )

    def update_function_module_status(
        self,
        app_id: str,
        module_code: str,
        status: str,
        related_plan_id: str
    ) -> bool:
        """
        更新功能模块状态
        用于计划完成时更新模块状态
        """
        try:
            if not self._module_service:
                raise ValueError("Database session not initialized")

            # 先通过 module_code 和 app_id 查找模块
            modules = self._run_async(self._module_service.get_modules_by_app_id(app_id))
            target_module = None
            for module in modules:
                if module.module_code == module_code:
                    target_module = module
                    break

            if not target_module:
                print(f"Module not found with code {module_code} in app {app_id}")
                return False

            # 更新模块状态
            update_dto = UpdateFunctionModuleDTO(
                status=status,
                related_plan_id=related_plan_id,
            )

            self._run_async(self._module_service.update_module(
                target_module.id, update_dto, "system"
            ))

            return True
        except Exception as e:
            print(f"Failed to update module status: {e}")
            return False

    def update_application_system(
        self,
        app_ids: List[str],
        affected_modules: List[Dict[str, Any]],
        related_plan_id: str
    ) -> InventoryOperationResult:
        """
        更新应用系统
        用于 arch_change 分类
        """
        try:
            if not self._inventory_service or not self._module_service:
                raise ValueError("Database session not initialized")

            updated_module_ids = []
            updated_by = "system"

            # 更新每个应用系统
            for app_id in app_ids:
                # 更新应用系统信息
                update_dto = UpdateApplicationDTO(
                    app_description=f"架构变更 - 关联计划: {related_plan_id}",
                )
                self._inventory_service.update_application(app_id, update_dto, updated_by)

            # 更新功能模块
            for module_data in affected_modules:
                module_id = module_data.get("module_id")
                if not module_id:
                    continue

                update_dto = UpdateFunctionModuleDTO(
                    module_name=module_data.get("module_name"),
                    description=module_data.get("change_description"),
                )

                result = self._run_async(self._module_service.update_module(
                    module_id, update_dto, updated_by
                ))
                updated_module_ids.append(result.id)

            return InventoryOperationResult(
                success=True,
                inventory_id=app_ids[0] if app_ids else None,
                module_ids=updated_module_ids,
            )
        except Exception as e:
            return InventoryOperationResult(
                success=False,
                error_message=str(e)
            )

    def get_applications_by_ids(
        self,
        app_ids: List[str]
    ) -> List[Dict[str, Any]]:
        """根据ID列表获取应用系统"""
        try:
            if not self._inventory_service:
                return []

            applications = []
            for app_id in app_ids:
                try:
                    app = self._inventory_service.get_application(app_id)
                    applications.append({
                        "id": app.id,
                        "app_name": app.app_name,
                        "app_description": app.app_description,
                        "system_type": app.system_type or 'web',
                        "status": app.status,
                        "business_owner": app.business_owner,
                        "project_owner": app.project_owner,
                    })
                except ValueError:
                    # 应用不存在，跳过
                    continue

            return applications
        except Exception as e:
            return []

    def get_application_modules(
        self,
        app_id: str
    ) -> List[Dict[str, Any]]:
        """获取应用系统的功能模块"""
        try:
            if not self._module_service:
                return []

            modules = self._run_async(self._module_service.list_modules(app_id))

            return [
                {
                    "id": m.id,
                    "module_code": m.module_code,
                    "module_name": m.module_name,
                    "version": m.version,
                    "status": m.status,
                    "status_display": m.status_display,
                }
                for m in modules
            ]
        except Exception as e:
            return []

    def list_applications(
        self,
        status: Optional[str] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> Dict[str, Any]:
        """
        查询应用系统列表
        用于前端选择应用系统
        """
        try:
            if not self._inventory_service:
                return {
                    "items": [],
                    "total": 0,
                    "page": page,
                    "size": size,
                }

            result = self._inventory_service.list_applications(status, keyword, page, size)

            return {
                "items": [
                    {
                        "id": app.id,
                        "app_name": app.app_name,
                        "app_description": app.app_description,
                        "status": app.status,
                        "business_owner": app.business_owner,
                        "project_owner": app.project_owner,
                        "launch_time": app.launch_time,
                    }
                    for app in result.data
                ],
                "total": result.total,
                "page": result.page,
                "size": result.size,
                "total_pages": result.total_pages,
            }
        except Exception as e:
            return {
                "items": [],
                "total": 0,
                "page": page,
                "size": size,
            }

    def link_to_plan(
        self,
        inventory_type: str,
        inventory_id: str,
        plan_id: str
    ) -> bool:
        """
        关联台账到计划
        调用台账仓储的 link_to_plan 方法
        """
        try:
            if not self._inventory_repo:
                return False
            return self._inventory_repo.link_to_plan(inventory_type, inventory_id, plan_id)
        except Exception as e:
            print(f"Error linking inventory to plan: {e}")
            return False

    def unlink_from_plan(
        self,
        inventory_type: str,
        inventory_id: str,
        plan_id: str
    ) -> bool:
        """
        取消台账与计划的关联
        调用台账仓储的 unlink_from_plan 方法
        """
        try:
            if not self._inventory_repo:
                return False
            return self._inventory_repo.unlink_from_plan(inventory_type, inventory_id, plan_id)
        except Exception as e:
            print(f"Error unlinking inventory from plan: {e}")
            return False


class InventoryLifecycleLogServiceImpl(InventoryLifecycleLogService):
    """
    生命周期日志服务实现
    """

    def __init__(self, db_session=None):
        self._db = db_session
        if db_session:
            self._log_repo = LifecycleLogRepositoryImpl(db_session)
            self._log_service = LifecycleLogService(self._log_repo)
        else:
            self._log_service = None

    def _run_async(self, coro):
        """辅助方法：运行异步协程"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, coro)
                    return future.result()
            else:
                return loop.run_until_complete(coro)
        except RuntimeError:
            return asyncio.run(coro)

    def create_log(
        self,
        log_type: str,
        inventory_id: str,
        event_title: str,
        before_data: Optional[Dict[str, Any]],
        after_data: Optional[Dict[str, Any]],
        related_plan_id: str,
        operator: str
    ) -> Dict[str, Any]:
        """创建生命周期日志"""
        try:
            if not self._log_service:
                # 如果没有初始化服务，返回模拟数据
                log_id = f"log-{uuid.uuid4().hex[:8]}"
                return {
                    "id": log_id,
                    "log_type": log_type,
                    "inventory_id": inventory_id,
                    "event_title": event_title,
                    "before_data": before_data,
                    "after_data": after_data,
                    "related_plan_id": related_plan_id,
                    "operator": operator,
                    "operation_time": datetime.utcnow().isoformat(),
                }

            # 创建日志DTO
            log_dto = CreateLifecycleLogDTO(
                log_type=log_type,
                event_title=event_title,
                description=None,
                before_data=before_data,
                after_data=after_data,
                related_plan_id=related_plan_id,
                related_module_id=None,
                operator=operator,
            )

            result = self._run_async(self._log_service.create_log(log_dto))

            return {
                "id": result.id,
                "log_type": result.log_type,
                "inventory_id": result.app_id if hasattr(result, 'app_id') else inventory_id,
                "event_title": result.event_title,
                "before_data": result.before_data,
                "after_data": result.after_data,
                "related_plan_id": related_plan_id,
                "operator": result.operator,
                "operation_time": result.operation_time,
            }
        except Exception as e:
            # 出错时返回模拟数据
            log_id = f"log-{uuid.uuid4().hex[:8]}"
            return {
                "id": log_id,
                "log_type": log_type,
                "inventory_id": inventory_id,
                "event_title": event_title,
                "before_data": before_data,
                "after_data": after_data,
                "related_plan_id": related_plan_id,
                "operator": operator,
                "operation_time": datetime.utcnow().isoformat(),
            }

    def get_logs_by_plan_id(
        self,
        plan_id: str
    ) -> List[Dict[str, Any]]:
        """获取计划相关的生命周期日志"""
        try:
            if not self._log_service:
                # 如果没有初始化服务，返回空列表
                return []

            # 调用台账服务的查询方法
            logs = self._run_async(self._log_service.get_logs_by_plan_id(plan_id))

            return [
                {
                    "id": log.id,
                    "log_type": log.log_type,
                    "inventory_id": log.app_id,
                    "event_title": log.event_title,
                    "before_data": log.before_data,
                    "after_data": log.after_data,
                    "related_plan_id": log.related_plan_id,
                    "operator": log.operator,
                    "operation_time": log.operation_time,
                }
                for log in logs
            ]
        except Exception as e:
            # 出错时返回空列表
            return []
