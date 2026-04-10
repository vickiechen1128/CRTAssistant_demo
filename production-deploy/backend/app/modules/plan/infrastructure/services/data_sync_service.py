"""
计划与台账数据同步服务
实现计划管理和台账管理之间的数据同步机制

同步策略：
1. 事件驱动实时同步 - 通过领域事件触发同步
2. 定时补偿同步 - 定时任务检查并修复数据不一致
3. 同步日志记录 - 记录所有同步操作便于审计
"""
import asyncio
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum

from app.modules.inventory.application.inventory_service import InventoryService as InventoryAppService
from app.modules.inventory.application.function_module_service import FunctionModuleService
from app.modules.inventory.application.lifecycle_log_service import LifecycleLogService
from app.modules.inventory.infrastructure.persistence.inventory_repository_impl import InventoryRepositoryImpl
from app.modules.inventory.infrastructure.persistence.repositories.function_module_repository_impl import FunctionModuleRepositoryImpl
from app.modules.inventory.infrastructure.persistence.repositories.lifecycle_log_repository_impl import LifecycleLogRepositoryImpl
from app.modules.inventory.domain.value_objects.inventory_status import InventoryStatus


class SyncStatus(Enum):
    """同步状态"""
    PENDING = "pending"      # 待同步
    SUCCESS = "success"      # 同步成功
    FAILED = "failed"        # 同步失败
    PARTIAL = "partial"      # 部分成功


class SyncLog:
    """同步日志"""
    def __init__(
        self,
        sync_type: str,
        source_id: str,
        target_id: str,
        operation: str,
        status: SyncStatus,
        details: Optional[Dict] = None,
        error_message: Optional[str] = None
    ):
        self.id = f"sync-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{source_id[:8]}"
        self.sync_type = sync_type  # plan_to_inventory / inventory_to_plan
        self.source_id = source_id
        self.target_id = target_id
        self.operation = operation
        self.status = status
        self.details = details or {}
        self.error_message = error_message
        self.created_at = datetime.utcnow()


class DataSyncService:
    """
    数据同步服务
    协调计划管理和台账管理之间的数据同步
    """

    def __init__(self, db_session=None):
        self._db = db_session
        self._sync_logs: List[SyncLog] = []  # 内存中的同步日志，生产环境应持久化

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
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, coro)
                    return future.result()
            else:
                return loop.run_until_complete(coro)
        except RuntimeError:
            return asyncio.run(coro)

    # ==================== 计划 → 台账 同步 ====================

    def sync_plan_started(self, plan_id: str, inventory_ids: List[str], started_by: str) -> SyncLog:
        """
        计划启动时同步到台账
        - 标记关联台账为"计划中"状态
        """
        try:
            if not self._inventory_service:
                raise ValueError("Database session not initialized")

            synced_count = 0
            failed_ids = []

            for app_id in inventory_ids:
                try:
                    # 获取应用系统
                    app = self._inventory_service.get_application(app_id)

                    # 创建生命周期日志记录计划启动
                    from app.modules.inventory.application.dtos.lifecycle_log_dtos import CreateLifecycleLogDTO
                    log_dto = CreateLifecycleLogDTO(
                        log_type="plan_linked",
                        event_title=f"计划启动关联: {plan_id}",
                        description=f"计划 {plan_id} 已启动，关联此应用系统",
                        related_plan_id=plan_id,
                        operator=started_by
                    )
                    self._run_async(self._log_service.create_log(log_dto))

                    synced_count += 1
                except Exception as e:
                    failed_ids.append({"id": app_id, "error": str(e)})

            # 记录同步日志
            status = SyncStatus.SUCCESS if not failed_ids else SyncStatus.PARTIAL if synced_count > 0 else SyncStatus.FAILED
            log = SyncLog(
                sync_type="plan_to_inventory",
                source_id=plan_id,
                target_id=",".join(inventory_ids),
                operation="plan_started",
                status=status,
                details={
                    "synced_count": synced_count,
                    "failed_ids": failed_ids,
                    "started_by": started_by
                },
                error_message=f"Failed to sync {len(failed_ids)} items" if failed_ids else None
            )
            self._sync_logs.append(log)

            return log

        except Exception as e:
            log = SyncLog(
                sync_type="plan_to_inventory",
                source_id=plan_id,
                target_id=",".join(inventory_ids),
                operation="plan_started",
                status=SyncStatus.FAILED,
                error_message=str(e)
            )
            self._sync_logs.append(log)
            return log

    def sync_plan_completed(
        self,
        plan_id: str,
        plan_name: str,
        category: str,
        inventory_ids: List[str],
        affected_modules: List[Dict],
        completed_by: str
    ) -> SyncLog:
        """
        计划完成时同步到台账
        - 根据计划分类执行不同的台账操作
        - 创建生命周期日志
        """
        try:
            if not self._inventory_service or not self._log_service:
                raise ValueError("Database session not initialized")

            # 根据分类执行不同的同步逻辑
            if category == "new_system":
                return self._sync_new_system_completion(
                    plan_id, plan_name, inventory_ids, affected_modules, completed_by
                )
            elif category == "new_feature":
                return self._sync_new_feature_completion(
                    plan_id, plan_name, inventory_ids, affected_modules, completed_by
                )
            elif category == "func_change":
                return self._sync_func_change_completion(
                    plan_id, plan_name, inventory_ids, affected_modules, completed_by
                )
            elif category == "arch_change":
                return self._sync_arch_change_completion(
                    plan_id, plan_name, inventory_ids, affected_modules, completed_by
                )
            elif category == "security_check":
                return self._sync_security_check_completion(
                    plan_id, plan_name, inventory_ids, completed_by
                )
            else:
                raise ValueError(f"Unknown category: {category}")

        except Exception as e:
            log = SyncLog(
                sync_type="plan_to_inventory",
                source_id=plan_id,
                target_id=",".join(inventory_ids) if inventory_ids else "",
                operation=f"plan_completed_{category}",
                status=SyncStatus.FAILED,
                error_message=str(e)
            )
            self._sync_logs.append(log)
            return log

    def _sync_new_system_completion(
        self, plan_id: str, plan_name: str, inventory_ids: List[str],
        affected_modules: List[Dict], completed_by: str
    ) -> SyncLog:
        """新系统上线完成同步"""
        try:
            # 新系统上线时，台账应该已经被创建
            # 这里主要创建生命周期日志
            for app_id in inventory_ids:
                from app.modules.inventory.application.dtos.lifecycle_log_dtos import CreateLifecycleLogDTO
                log_dto = CreateLifecycleLogDTO(
                    log_type="system_launch",
                    event_title=f"【系统上线】{plan_name} 正式上线",
                    description=f"通过计划 {plan_id} 完成系统上线",
                    before_data=None,
                    after_data={
                        "plan_id": plan_id,
                        "plan_name": plan_name,
                        "modules": [m.get("module_name") for m in affected_modules]
                    },
                    related_plan_id=plan_id,
                    operator=completed_by
                )
                self._run_async(self._log_service.create_log(log_dto))

            log = SyncLog(
                sync_type="plan_to_inventory",
                source_id=plan_id,
                target_id=",".join(inventory_ids),
                operation="new_system_completion",
                status=SyncStatus.SUCCESS,
                details={"module_count": len(affected_modules)}
            )
            self._sync_logs.append(log)
            return log

        except Exception as e:
            return SyncLog(
                sync_type="plan_to_inventory",
                source_id=plan_id,
                target_id=",".join(inventory_ids),
                operation="new_system_completion",
                status=SyncStatus.FAILED,
                error_message=str(e)
            )

    def _sync_new_feature_completion(
        self, plan_id: str, plan_name: str, inventory_ids: List[str],
        affected_modules: List[Dict], completed_by: str
    ) -> SyncLog:
        """新功能上线完成同步"""
        try:
            for app_id in inventory_ids:
                from app.modules.inventory.application.dtos.lifecycle_log_dtos import CreateLifecycleLogDTO
                log_dto = CreateLifecycleLogDTO(
                    log_type="feature_release",
                    event_title=f"【功能上线】{plan_name}",
                    description=f"通过计划 {plan_id} 完成功能上线",
                    after_data={
                        "plan_id": plan_id,
                        "modules": [m.get("module_name") for m in affected_modules]
                    },
                    related_plan_id=plan_id,
                    operator=completed_by
                )
                self._run_async(self._log_service.create_log(log_dto))

            log = SyncLog(
                sync_type="plan_to_inventory",
                source_id=plan_id,
                target_id=",".join(inventory_ids),
                operation="new_feature_completion",
                status=SyncStatus.SUCCESS,
                details={"module_count": len(affected_modules)}
            )
            self._sync_logs.append(log)
            return log

        except Exception as e:
            return SyncLog(
                sync_type="plan_to_inventory",
                source_id=plan_id,
                target_id=",".join(inventory_ids),
                operation="new_feature_completion",
                status=SyncStatus.FAILED,
                error_message=str(e)
            )

    def _sync_func_change_completion(
        self, plan_id: str, plan_name: str, inventory_ids: List[str],
        affected_modules: List[Dict], completed_by: str
    ) -> SyncLog:
        """功能变更完成同步"""
        try:
            for app_id in inventory_ids:
                from app.modules.inventory.application.dtos.lifecycle_log_dtos import CreateLifecycleLogDTO
                log_dto = CreateLifecycleLogDTO(
                    log_type="feature_update",
                    event_title=f"【功能变更】{plan_name}",
                    description=f"通过计划 {plan_id} 完成功能变更",
                    before_data={"modules": [{"name": m.get("module_name"), "version": m.get("before_version")} for m in affected_modules]},
                    after_data={"modules": [{"name": m.get("module_name"), "version": m.get("after_version")} for m in affected_modules]},
                    related_plan_id=plan_id,
                    operator=completed_by
                )
                self._run_async(self._log_service.create_log(log_dto))

            log = SyncLog(
                sync_type="plan_to_inventory",
                source_id=plan_id,
                target_id=",".join(inventory_ids),
                operation="func_change_completion",
                status=SyncStatus.SUCCESS,
                details={"module_count": len(affected_modules)}
            )
            self._sync_logs.append(log)
            return log

        except Exception as e:
            return SyncLog(
                sync_type="plan_to_inventory",
                source_id=plan_id,
                target_id=",".join(inventory_ids),
                operation="func_change_completion",
                status=SyncStatus.FAILED,
                error_message=str(e)
            )

    def _sync_arch_change_completion(
        self, plan_id: str, plan_name: str, inventory_ids: List[str],
        affected_modules: List[Dict], completed_by: str
    ) -> SyncLog:
        """架构变更完成同步"""
        try:
            for app_id in inventory_ids:
                from app.modules.inventory.application.dtos.lifecycle_log_dtos import CreateLifecycleLogDTO
                log_dto = CreateLifecycleLogDTO(
                    log_type="arch_change",
                    event_title=f"【架构变更】{plan_name}",
                    description=f"通过计划 {plan_id} 完成架构变更",
                    related_plan_id=plan_id,
                    operator=completed_by
                )
                self._run_async(self._log_service.create_log(log_dto))

            log = SyncLog(
                sync_type="plan_to_inventory",
                source_id=plan_id,
                target_id=",".join(inventory_ids),
                operation="arch_change_completion",
                status=SyncStatus.SUCCESS,
                details={"app_count": len(inventory_ids), "module_count": len(affected_modules)}
            )
            self._sync_logs.append(log)
            return log

        except Exception as e:
            return SyncLog(
                sync_type="plan_to_inventory",
                source_id=plan_id,
                target_id=",".join(inventory_ids),
                operation="arch_change_completion",
                status=SyncStatus.FAILED,
                error_message=str(e)
            )

    def _sync_security_check_completion(
        self, plan_id: str, plan_name: str, inventory_ids: List[str], completed_by: str
    ) -> SyncLog:
        """安全检查完成同步"""
        try:
            # 安全检查不直接关联台账，但如果有指定范围，记录日志
            if inventory_ids:
                for app_id in inventory_ids:
                    from app.modules.inventory.application.dtos.lifecycle_log_dtos import CreateLifecycleLogDTO
                    log_dto = CreateLifecycleLogDTO(
                        log_type="security_check",
                        event_title=f"【安全检查】{plan_name}",
                        description=f"通过计划 {plan_id} 完成安全检查",
                        related_plan_id=plan_id,
                        operator=completed_by
                    )
                    self._run_async(self._log_service.create_log(log_dto))

            log = SyncLog(
                sync_type="plan_to_inventory",
                source_id=plan_id,
                target_id=",".join(inventory_ids) if inventory_ids else "",
                operation="security_check_completion",
                status=SyncStatus.SUCCESS
            )
            self._sync_logs.append(log)
            return log

        except Exception as e:
            return SyncLog(
                sync_type="plan_to_inventory",
                source_id=plan_id,
                target_id=",".join(inventory_ids) if inventory_ids else "",
                operation="security_check_completion",
                status=SyncStatus.FAILED,
                error_message=str(e)
            )

    def sync_plan_cancelled(
        self, plan_id: str, inventory_ids: List[str], reason: Optional[str], cancelled_by: str
    ) -> SyncLog:
        """
        计划取消时同步到台账
        - 在台账中记录计划取消
        """
        try:
            if not self._log_service:
                raise ValueError("Database session not initialized")

            for app_id in inventory_ids:
                from app.modules.inventory.application.dtos.lifecycle_log_dtos import CreateLifecycleLogDTO
                log_dto = CreateLifecycleLogDTO(
                    log_type="plan_cancelled",
                    event_title=f"计划取消: {plan_id}",
                    description=f"关联计划已取消。原因: {reason or '未说明'}",
                    related_plan_id=plan_id,
                    operator=cancelled_by
                )
                self._run_async(self._log_service.create_log(log_dto))

            log = SyncLog(
                sync_type="plan_to_inventory",
                source_id=plan_id,
                target_id=",".join(inventory_ids),
                operation="plan_cancelled",
                status=SyncStatus.SUCCESS,
                details={"reason": reason}
            )
            self._sync_logs.append(log)
            return log

        except Exception as e:
            log = SyncLog(
                sync_type="plan_to_inventory",
                source_id=plan_id,
                target_id=",".join(inventory_ids),
                operation="plan_cancelled",
                status=SyncStatus.FAILED,
                error_message=str(e)
            )
            self._sync_logs.append(log)
            return log

    # ==================== 台账 → 计划 同步 ====================

    def sync_inventory_status_changed(
        self, app_id: str, old_status: str, new_status: str, changed_by: str
    ) -> SyncLog:
        """
        台账状态变更时同步到计划
        - 如果台账被停用或归档，检查关联的计划并提醒
        """
        try:
            # 这里应该查询计划仓储获取关联的计划
            # 由于当前上下文限制，仅记录同步日志
            # 实际实现中应该：
            # 1. 查询所有关联此台账的计划
            # 2. 如果台账变为 inactive/archived，提醒计划负责人

            log = SyncLog(
                sync_type="inventory_to_plan",
                source_id=app_id,
                target_id="",  # 多个计划可能关联
                operation="inventory_status_changed",
                status=SyncStatus.SUCCESS,
                details={
                    "old_status": old_status,
                    "new_status": new_status,
                    "changed_by": changed_by
                }
            )
            self._sync_logs.append(log)
            return log

        except Exception as e:
            log = SyncLog(
                sync_type="inventory_to_plan",
                source_id=app_id,
                target_id="",
                operation="inventory_status_changed",
                status=SyncStatus.FAILED,
                error_message=str(e)
            )
            self._sync_logs.append(log)
            return log

    # ==================== 定时补偿同步 ====================

    def check_consistency(self, plan_id: Optional[str] = None) -> Dict[str, Any]:
        """
        检查计划与台账的数据一致性
        返回不一致的数据列表
        """
        inconsistencies = []

        try:
            # 这里应该：
            # 1. 查询计划及其关联的台账
            # 2. 检查计划状态与台账状态是否匹配
            # 3. 检查关联关系是否有效

            # 由于当前上下文限制，返回空结果
            # 实际实现中需要访问计划仓储

            return {
                "checked_at": datetime.utcnow().isoformat(),
                "plan_id": plan_id,
                "inconsistencies": inconsistencies,
                "total_checked": 0,
                "inconsistent_count": len(inconsistencies)
            }

        except Exception as e:
            return {
                "checked_at": datetime.utcnow().isoformat(),
                "plan_id": plan_id,
                "error": str(e),
                "inconsistencies": [],
                "total_checked": 0,
                "inconsistent_count": 0
            }

    def repair_inconsistency(self, plan_id: str) -> SyncLog:
        """
        修复计划与台账的数据不一致
        """
        try:
            # 检查一致性
            result = self.check_consistency(plan_id)

            if not result["inconsistencies"]:
                return SyncLog(
                    sync_type="repair",
                    source_id=plan_id,
                    target_id="",
                    operation="consistency_repair",
                    status=SyncStatus.SUCCESS,
                    details={"message": "No inconsistencies found"}
                )

            # 修复不一致
            repaired = []
            failed = []

            for inc in result["inconsistencies"]:
                try:
                    # 根据不一致类型执行修复
                    repaired.append(inc)
                except Exception as e:
                    failed.append({"item": inc, "error": str(e)})

            status = SyncStatus.SUCCESS if not failed else SyncStatus.PARTIAL if repaired else SyncStatus.FAILED

            log = SyncLog(
                sync_type="repair",
                source_id=plan_id,
                target_id="",
                operation="consistency_repair",
                status=status,
                details={
                    "repaired": repaired,
                    "failed": failed
                },
                error_message=f"Failed to repair {len(failed)} items" if failed else None
            )
            self._sync_logs.append(log)
            return log

        except Exception as e:
            log = SyncLog(
                sync_type="repair",
                source_id=plan_id,
                target_id="",
                operation="consistency_repair",
                status=SyncStatus.FAILED,
                error_message=str(e)
            )
            self._sync_logs.append(log)
            return log

    # ==================== 同步日志查询 ====================

    def get_sync_logs(
        self,
        sync_type: Optional[str] = None,
        source_id: Optional[str] = None,
        status: Optional[SyncStatus] = None,
        limit: int = 100
    ) -> List[SyncLog]:
        """获取同步日志"""
        logs = self._sync_logs

        if sync_type:
            logs = [log for log in logs if log.sync_type == sync_type]
        if source_id:
            logs = [log for log in logs if log.source_id == source_id]
        if status:
            logs = [log for log in logs if log.status == status]

        # 按时间倒序
        logs = sorted(logs, key=lambda x: x.created_at, reverse=True)
        return logs[:limit]

    def get_sync_statistics(self) -> Dict[str, Any]:
        """获取同步统计信息"""
        total = len(self._sync_logs)
        success = len([log for log in self._sync_logs if log.status == SyncStatus.SUCCESS])
        failed = len([log for log in self._sync_logs if log.status == SyncStatus.FAILED])
        partial = len([log for log in self._sync_logs if log.status == SyncStatus.PARTIAL])

        # 按类型统计
        type_stats = {}
        for log in self._sync_logs:
            type_stats[log.sync_type] = type_stats.get(log.sync_type, 0) + 1

        return {
            "total": total,
            "success": success,
            "failed": failed,
            "partial": partial,
            "success_rate": (success / total * 100) if total > 0 else 0,
            "type_distribution": type_stats,
            "last_sync": self._sync_logs[-1].created_at.isoformat() if self._sync_logs else None
        }
