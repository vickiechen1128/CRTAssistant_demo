"""
计划完成领域服务
处理计划完成时的台账更新和生命周期日志生成
"""
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict, Any

from ..entities.plan import Plan
from ..value_objects.category import Category
from ..events.plan_events import PlanCompletedEvent
from .inventory_service import (
    InventoryService,
    InventoryLifecycleLogService,
    InventoryOperationResult,
)


@dataclass
class CompletionResult:
    """计划完成操作结果"""
    success: bool
    updated_inventory_ids: List[str]
    created_module_ids: List[str]
    lifecycle_log_ids: List[str]
    sync_log_id: Optional[str] = None  # 数据同步日志ID
    error_message: Optional[str] = None


class PlanCompletionService:
    """
    计划完成服务
    协调计划完成时的所有台账操作和数据同步
    """

    def __init__(
        self,
        inventory_service: InventoryService,
        lifecycle_service: InventoryLifecycleLogService,
        data_sync_service=None  # 可选的数据同步服务
    ):
        self._inventory_service = inventory_service
        self._lifecycle_service = lifecycle_service
        self._data_sync_service = data_sync_service

    def complete_plan(
        self,
        plan: Plan,
        completed_by: str
    ) -> CompletionResult:
        """
        完成计划并执行相应的台账操作
        
        根据计划分类执行不同的操作：
        - new_system: 创建应用系统 + 功能模块
        - new_feature: 创建功能模块
        - func_change: 更新功能模块
        - arch_change: 更新应用系统 + 功能模块
        - security_check: 仅记录检查日志
        """
        category = plan.category.value
        
        try:
            if category == "new_system":
                return self._handle_new_system_completion(plan, completed_by)
            elif category == "new_feature":
                return self._handle_new_feature_completion(plan, completed_by)
            elif category == "func_change":
                return self._handle_func_change_completion(plan, completed_by)
            elif category == "arch_change":
                return self._handle_arch_change_completion(plan, completed_by)
            elif category == "security_check":
                return self._handle_security_check_completion(plan, completed_by)
            else:
                return CompletionResult(
                    success=False,
                    updated_inventory_ids=[],
                    created_module_ids=[],
                    lifecycle_log_ids=[],
                    error_message=f"Unknown category: {category}"
                )
        except Exception as e:
            return CompletionResult(
                success=False,
                updated_inventory_ids=[],
                created_module_ids=[],
                lifecycle_log_ids=[],
                error_message=str(e)
            )

    def _handle_new_system_completion(
        self,
        plan: Plan,
        completed_by: str
    ) -> CompletionResult:
        """处理新系统上线的完成逻辑"""
        # 从 affected_modules 中提取模块数据
        modules = [
            {
                "module_code": m.module_id,
                "module_name": m.module_name,
                "module_description": m.change_description or "",
                "owner": completed_by,
                "version": m.after_version or "v1.0.0",
                "parent_module_id": None,
            }
            for m in plan.affected_modules
        ]

        # 创建应用系统
        result = self._inventory_service.create_application(
            app_data={
                "app_name": plan.name,
                "app_description": plan.description or "",
                "system_type": "web",
                "deploy_env": "production",
                "business_owner": completed_by,
                "project_owner": completed_by,
                "current_version": "v1.0.0",
                "launch_time": datetime.utcnow().isoformat(),
            },
            modules=modules,
            cloud_resources=[],
            accounts=[],
            related_plan_id=plan.id
        )

        if not result.success:
            return CompletionResult(
                success=False,
                updated_inventory_ids=[],
                created_module_ids=[],
                lifecycle_log_ids=[],
                error_message=result.error_message
            )

        # 创建生命周期日志
        log = self._lifecycle_service.create_log(
            log_type="system_launch",
            inventory_id=result.inventory_id,
            event_title=f"【系统上线】{plan.name} 正式上线",
            before_data=None,
            after_data={
                "app_name": plan.name,
                "version": "v1.0.0",
                "modules": [m.module_name for m in plan.affected_modules],
            },
            related_plan_id=plan.id,
            operator=completed_by
        )

        # 执行数据同步
        sync_log_id = None
        if self._data_sync_service:
            sync_result = self._data_sync_service.sync_plan_completed(
                plan_id=plan.id,
                plan_name=plan.name,
                category=plan.category.value,
                inventory_ids=[result.inventory_id] if result.inventory_id else [],
                affected_modules=[{"module_name": m.module_name} for m in plan.affected_modules],
                completed_by=completed_by
            )
            sync_log_id = sync_result.id

        return CompletionResult(
            success=True,
            updated_inventory_ids=[result.inventory_id] if result.inventory_id else [],
            created_module_ids=result.module_ids or [],
            lifecycle_log_ids=[log.get("id")] if log else [],
            sync_log_id=sync_log_id
        )

    def _handle_new_feature_completion(
        self,
        plan: Plan,
        completed_by: str
    ) -> CompletionResult:
        """处理新功能上线的完成逻辑
        
        注意：功能模块已在创建计划时同步创建，这里只更新模块状态和创建生命周期日志
        """
        if not plan.inventory_ids:
            return CompletionResult(
                success=False,
                updated_inventory_ids=[],
                created_module_ids=[],
                lifecycle_log_ids=[],
                error_message="No application selected for new feature"
            )

        app_id = plan.inventory_ids[0]
        
        # 功能模块已在创建计划时创建，这里只更新模块状态为 online
        # 并创建生命周期日志
        log_ids = []
        for module in plan.affected_modules:
            # 更新模块状态为 online
            try:
                self._inventory_service.update_function_module_status(
                    app_id=app_id,
                    module_code=module.module_id,
                    status="online",
                    related_plan_id=plan.id
                )
            except Exception as e:
                print(f"Failed to update module status for {module.module_id}: {e}")
            
            # 创建生命周期日志
            log = self._lifecycle_service.create_log(
                log_type="module_launch",
                inventory_id=app_id,
                event_title=f"【功能上线】{module.module_name} 正式上线",
                before_data=None,
                after_data={
                    "module_name": module.module_name,
                    "version": module.after_version or "v1.0.0",
                },
                related_plan_id=plan.id,
                operator=completed_by
            )
            if log:
                log_ids.append(log.get("id"))

        return CompletionResult(
            success=True,
            updated_inventory_ids=[app_id],
            created_module_ids=[],  # 模块已在创建计划时创建
            lifecycle_log_ids=log_ids
        )

    def _handle_func_change_completion(
        self,
        plan: Plan,
        completed_by: str
    ) -> CompletionResult:
        """处理功能变更的完成逻辑"""
        if not plan.inventory_ids:
            return CompletionResult(
                success=False,
                updated_inventory_ids=[],
                created_module_ids=[],
                lifecycle_log_ids=[],
                error_message="No application selected for function change"
            )

        app_id = plan.inventory_ids[0]
        
        # 更新功能模块
        module_updates = [
            {
                "module_id": m.module_id,
                "before_version": m.before_version,
                "after_version": m.after_version,
                "change_description": m.change_description,
            }
            for m in plan.affected_modules
        ]

        result = self._inventory_service.update_function_modules(
            app_id=app_id,
            module_updates=module_updates,
            related_plan_id=plan.id
        )

        if not result.success:
            return CompletionResult(
                success=False,
                updated_inventory_ids=[],
                created_module_ids=[],
                lifecycle_log_ids=[],
                error_message=result.error_message
            )

        # 创建生命周期日志
        log_ids = []
        for module in plan.affected_modules:
            log = self._lifecycle_service.create_log(
                log_type="module_update",
                inventory_id=app_id,
                event_title=f"【功能变更】{module.module_name} 更新至 {module.after_version}",
                before_data={
                    "version": module.before_version,
                },
                after_data={
                    "version": module.after_version,
                    "change_description": module.change_description,
                },
                related_plan_id=plan.id,
                operator=completed_by
            )
            if log:
                log_ids.append(log.get("id"))

        return CompletionResult(
            success=True,
            updated_inventory_ids=[app_id],
            created_module_ids=[],
            lifecycle_log_ids=log_ids
        )

    def _handle_arch_change_completion(
        self,
        plan: Plan,
        completed_by: str
    ) -> CompletionResult:
        """处理架构变更的完成逻辑"""
        if not plan.inventory_ids:
            return CompletionResult(
                success=False,
                updated_inventory_ids=[],
                created_module_ids=[],
                lifecycle_log_ids=[],
                error_message="No applications selected for architecture change"
            )

        # 更新应用系统
        affected_modules = [
            {
                "module_id": m.module_id,
                "module_name": m.module_name,
                "action": m.action,
                "before_version": m.before_version,
                "after_version": m.after_version,
            }
            for m in plan.affected_modules
        ]

        result = self._inventory_service.update_application_system(
            app_ids=plan.inventory_ids,
            affected_modules=affected_modules,
            related_plan_id=plan.id
        )

        if not result.success:
            return CompletionResult(
                success=False,
                updated_inventory_ids=[],
                created_module_ids=[],
                lifecycle_log_ids=[],
                error_message=result.error_message
            )

        # 创建生命周期日志
        log_ids = []
        for app_id in plan.inventory_ids:
            log = self._lifecycle_service.create_log(
                log_type="system_upgrade",
                inventory_id=app_id,
                event_title=f"【架构变更】{plan.name}",
                before_data={
                    "affected_modules": [
                        {"name": m.module_name, "version": m.before_version}
                        for m in plan.affected_modules
                    ]
                },
                after_data={
                    "affected_modules": [
                        {"name": m.module_name, "version": m.after_version}
                        for m in plan.affected_modules
                    ]
                },
                related_plan_id=plan.id,
                operator=completed_by
            )
            if log:
                log_ids.append(log.get("id"))

        return CompletionResult(
            success=True,
            updated_inventory_ids=plan.inventory_ids,
            created_module_ids=[],
            lifecycle_log_ids=log_ids
        )

    def _handle_security_check_completion(
        self,
        plan: Plan,
        completed_by: str
    ) -> CompletionResult:
        """处理安全检查的完成逻辑"""
        # 安全检查不修改台账，仅记录日志
        log_ids = []
        
        for app_id in plan.inventory_ids:
            log = self._lifecycle_service.create_log(
                log_type="security_check",
                inventory_id=app_id,
                event_title=f"【安全检查】{plan.name}",
                before_data=None,
                after_data={
                    "check_result": "completed",
                    "plan_name": plan.name,
                },
                related_plan_id=plan.id,
                operator=completed_by
            )
            if log:
                log_ids.append(log.get("id"))

        return CompletionResult(
            success=True,
            updated_inventory_ids=plan.inventory_ids,
            created_module_ids=[],
            lifecycle_log_ids=log_ids
        )

    def preview_changes(
        self,
        plan: Plan
    ) -> Dict[str, Any]:
        """
        预览计划变更
        用于 Step 4 预览确认
        """
        category = plan.category.value
        
        inventory_changes = []
        lifecycle_logs_preview = []

        if category == "new_system":
            inventory_changes.append({
                "change_type": "create",
                "change_object": "application_system",
                "operation": "创建应用系统",
                "details": {
                    "app_name": plan.name,
                    "modules": [m.module_name for m in plan.affected_modules],
                }
            })
            lifecycle_logs_preview.append({
                "log_type": "system_launch",
                "log_type_label": "系统上线",
                "event_title": f"【系统上线】{plan.name} 正式上线"
            })

        elif category == "new_feature":
            inventory_changes.append({
                "change_type": "create",
                "change_object": "function_module",
                "operation": "创建功能模块",
                "details": {
                    "app_id": plan.inventory_ids[0] if plan.inventory_ids else None,
                    "modules": [m.module_name for m in plan.affected_modules],
                }
            })
            for module in plan.affected_modules:
                lifecycle_logs_preview.append({
                    "log_type": "module_launch",
                    "log_type_label": "功能上线",
                    "event_title": f"【功能上线】{module.module_name} 正式上线"
                })

        elif category == "func_change":
            inventory_changes.append({
                "change_type": "update",
                "change_object": "function_module",
                "operation": "更新功能模块",
                "details": {
                    "app_id": plan.inventory_ids[0] if plan.inventory_ids else None,
                    "modules": [
                        {
                            "name": m.module_name,
                            "from_version": m.before_version,
                            "to_version": m.after_version,
                        }
                        for m in plan.affected_modules
                    ],
                }
            })
            for module in plan.affected_modules:
                lifecycle_logs_preview.append({
                    "log_type": "module_update",
                    "log_type_label": "功能变更",
                    "event_title": f"【功能变更】{module.module_name} 更新至 {module.after_version}"
                })

        elif category == "arch_change":
            inventory_changes.append({
                "change_type": "update",
                "change_object": "application_system",
                "operation": "架构变更",
                "details": {
                    "app_ids": plan.inventory_ids,
                    "affected_modules": [m.module_name for m in plan.affected_modules],
                }
            })
            lifecycle_logs_preview.append({
                "log_type": "system_upgrade",
                "log_type_label": "架构变更",
                "event_title": f"【架构变更】{plan.name}"
            })

        elif category == "security_check":
            inventory_changes.append({
                "change_type": "scan",
                "change_object": "security",
                "operation": "安全检查",
                "details": {
                    "app_ids": plan.inventory_ids,
                    "scope": "full"
                }
            })
            lifecycle_logs_preview.append({
                "log_type": "security_check",
                "log_type_label": "安全检查",
                "event_title": f"【安全检查】{plan.name}"
            })

        return {
            "plan_name": plan.name,
            "category": category,
            "category_label": plan.category.label,
            "inventory_changes": inventory_changes,
            "lifecycle_logs_preview": lifecycle_logs_preview,
        }
