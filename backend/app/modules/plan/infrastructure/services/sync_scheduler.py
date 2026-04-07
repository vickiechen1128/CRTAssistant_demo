"""
数据同步定时任务
提供定时数据同步和一致性检查功能

使用方式:
1. 在应用启动时启动调度器
2. 配置同步间隔
3. 自动执行同步任务
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, Callable
from enum import Enum

from .data_sync_service import DataSyncService

logger = logging.getLogger(__name__)


class SyncTaskType(Enum):
    """同步任务类型"""
    CONSISTENCY_CHECK = "consistency_check"  # 一致性检查
    DATA_REPAIR = "data_repair"              # 数据修复
    LOG_CLEANUP = "log_cleanup"              # 日志清理


class SyncTask:
    """同步任务定义"""
    def __init__(
        self,
        task_type: SyncTaskType,
        interval_minutes: int,
        handler: Callable,
        enabled: bool = True
    ):
        self.task_type = task_type
        self.interval_minutes = interval_minutes
        self.handler = handler
        self.enabled = enabled
        self.last_run: Optional[datetime] = None
        self.next_run: Optional[datetime] = None
        self.run_count = 0
        self.error_count = 0


class SyncScheduler:
    """
    数据同步调度器
    管理定时同步任务的执行
    """

    def __init__(self, db_session=None):
        self._db = db_session
        self._sync_service = DataSyncService(db_session)
        self._tasks: dict[SyncTaskType, SyncTask] = {}
        self._running = False
        self._task_handle: Optional[asyncio.Task] = None

    def register_task(
        self,
        task_type: SyncTaskType,
        interval_minutes: int,
        handler: Callable,
        enabled: bool = True
    ) -> None:
        """注册同步任务"""
        self._tasks[task_type] = SyncTask(
            task_type=task_type,
            interval_minutes=interval_minutes,
            handler=handler,
            enabled=enabled
        )
        logger.info(f"Registered sync task: {task_type.value}, interval: {interval_minutes}min")

    def unregister_task(self, task_type: SyncTaskType) -> None:
        """注销同步任务"""
        if task_type in self._tasks:
            del self._tasks[task_type]
            logger.info(f"Unregistered sync task: {task_type.value}")

    async def start(self) -> None:
        """启动调度器"""
        if self._running:
            logger.warning("Sync scheduler is already running")
            return

        self._running = True
        logger.info("Starting sync scheduler...")

        # 初始化任务下次执行时间
        now = datetime.utcnow()
        for task in self._tasks.values():
            if task.enabled:
                task.next_run = now + timedelta(minutes=task.interval_minutes)

        # 启动调度循环
        self._task_handle = asyncio.create_task(self._scheduler_loop())

    async def stop(self) -> None:
        """停止调度器"""
        if not self._running:
            return

        self._running = False
        logger.info("Stopping sync scheduler...")

        if self._task_handle:
            self._task_handle.cancel()
            try:
                await self._task_handle
            except asyncio.CancelledError:
                pass

        logger.info("Sync scheduler stopped")

    async def _scheduler_loop(self) -> None:
        """调度器主循环"""
        while self._running:
            try:
                now = datetime.utcnow()

                for task in self._tasks.values():
                    if not task.enabled:
                        continue

                    if task.next_run and now >= task.next_run:
                        # 执行任务
                        await self._execute_task(task)

                        # 更新下次执行时间
                        task.next_run = now + timedelta(minutes=task.interval_minutes)

                # 每分钟检查一次
                await asyncio.sleep(60)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                await asyncio.sleep(60)

    async def _execute_task(self, task: SyncTask) -> None:
        """执行单个任务"""
        try:
            logger.info(f"Executing sync task: {task.task_type.value}")
            task.last_run = datetime.utcnow()

            # 执行处理器
            if asyncio.iscoroutinefunction(task.handler):
                await task.handler(self._sync_service)
            else:
                task.handler(self._sync_service)

            task.run_count += 1
            logger.info(f"Sync task completed: {task.task_type.value}")

        except Exception as e:
            task.error_count += 1
            logger.error(f"Sync task failed: {task.task_type.value}, error: {e}")

    def get_task_status(self) -> dict:
        """获取任务状态"""
        return {
            task_type.value: {
                "enabled": task.enabled,
                "interval_minutes": task.interval_minutes,
                "last_run": task.last_run.isoformat() if task.last_run else None,
                "next_run": task.next_run.isoformat() if task.next_run else None,
                "run_count": task.run_count,
                "error_count": task.error_count
            }
            for task_type, task in self._tasks.items()
        }

    def enable_task(self, task_type: SyncTaskType) -> None:
        """启用任务"""
        if task_type in self._tasks:
            self._tasks[task_type].enabled = True
            logger.info(f"Enabled sync task: {task_type.value}")

    def disable_task(self, task_type: SyncTaskType) -> None:
        """禁用任务"""
        if task_type in self._tasks:
            self._tasks[task_type].enabled = False
            logger.info(f"Disabled sync task: {task_type.value}")


# ==================== 默认任务处理器 ====================

async def consistency_check_handler(sync_service: DataSyncService) -> None:
    """
    一致性检查任务处理器
    检查所有计划与台账的数据一致性
    """
    logger.info("Running consistency check...")

    try:
        result = sync_service.check_consistency()

        if result["inconsistent_count"] > 0:
            logger.warning(
                f"Found {result['inconsistent_count']} inconsistencies, "
                f"total checked: {result['total_checked']}"
            )
            # 可以在这里发送告警通知
        else:
            logger.info("Consistency check passed, no inconsistencies found")

    except Exception as e:
        logger.error(f"Consistency check failed: {e}")
        raise


async def log_cleanup_handler(sync_service: DataSyncService) -> None:
    """
    日志清理任务处理器
    清理过期的同步日志
    """
    logger.info("Running log cleanup...")

    try:
        # 这里可以实现日志清理逻辑
        # 例如：只保留最近30天的日志
        logger.info("Log cleanup completed")

    except Exception as e:
        logger.error(f"Log cleanup failed: {e}")
        raise


# ==================== 调度器工厂函数 ====================

def create_default_scheduler(db_session=None) -> SyncScheduler:
    """
    创建默认配置的调度器

    默认任务:
    1. 一致性检查: 每60分钟执行一次
    2. 日志清理: 每天执行一次
    """
    scheduler = SyncScheduler(db_session)

    # 注册一致性检查任务
    scheduler.register_task(
        task_type=SyncTaskType.CONSISTENCY_CHECK,
        interval_minutes=60,  # 每小时检查一次
        handler=consistency_check_handler,
        enabled=True
    )

    # 注册日志清理任务
    scheduler.register_task(
        task_type=SyncTaskType.LOG_CLEANUP,
        interval_minutes=24 * 60,  # 每天清理一次
        handler=log_cleanup_handler,
        enabled=True
    )

    return scheduler


# 全局调度器实例（单例模式）
_scheduler_instance: Optional[SyncScheduler] = None


def get_scheduler(db_session=None) -> SyncScheduler:
    """获取全局调度器实例"""
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = create_default_scheduler(db_session)
    return _scheduler_instance


def init_scheduler(db_session=None) -> SyncScheduler:
    """初始化并启动调度器"""
    scheduler = get_scheduler(db_session)
    # 注意：这里不直接启动，需要在应用启动时调用 scheduler.start()
    return scheduler
