"""
数据同步领域事件处理器
监听计划和台账的领域事件，触发数据同步
"""
from typing import Any

from ...domain.events.plan_events import (
    PlanStartedEvent,
    PlanCompletedEvent,
    PlanCancelledEvent,
    PlanStatusChangedEvent,
    PlanInventoryLinkedEvent,
)
from ..services.data_sync_service import DataSyncService


class PlanSyncEventHandler:
    """
    计划领域事件同步处理器
    处理计划相关事件并触发台账同步
    """

    def __init__(self, db_session=None):
        self._sync_service = DataSyncService(db_session)

    def handle_plan_started(self, event: PlanStartedEvent) -> None:
        """
        处理计划启动事件
        触发：标记关联台账为"计划中"
        """
        # 注意：这里需要获取计划的inventory_ids
        # 实际实现中应该从计划仓储查询
        # 这里仅作为示例结构
        pass

    def handle_plan_completed(self, event: PlanCompletedEvent) -> None:
        """
        处理计划完成事件
        触发：根据分类执行台账操作，创建生命周期日志
        """
        if not event.inventory_ids:
            return

        self._sync_service.sync_plan_completed(
            plan_id=event.plan_id,
            plan_name=event.plan_name,
            category=event.category,
            inventory_ids=event.inventory_ids,
            affected_modules=event.affected_modules or [],
            completed_by=event.completed_by
        )

    def handle_plan_cancelled(self, event: PlanCancelledEvent) -> None:
        """
        处理计划取消事件
        触发：在台账中记录计划取消
        """
        # 需要从计划仓储获取inventory_ids
        pass

    def handle_plan_status_changed(self, event: PlanStatusChangedEvent) -> None:
        """
        处理计划状态变更事件
        根据状态变更类型触发不同的同步逻辑
        """
        # DRAFT/PENDING -> IN_PROGRESS: 标记台账为"计划中"
        if event.new_status == "IN_PROGRESS":
            # 需要获取inventory_ids并调用sync_plan_started
            pass

        # IN_PROGRESS -> CANCELLED: 记录取消
        elif event.new_status == "CANCELLED":
            # 需要获取inventory_ids并调用sync_plan_cancelled
            pass

    def handle_plan_inventory_linked(self, event: PlanInventoryLinkedEvent) -> None:
        """
        处理计划台账关联事件
        触发：在台账中记录计划关联
        """
        # 可以在这里触发台账端的计划关联记录
        pass


class InventorySyncEventHandler:
    """
    台账领域事件同步处理器
    处理台账相关事件并触发计划同步
    """

    def __init__(self, db_session=None):
        self._sync_service = DataSyncService(db_session)

    def handle_application_status_changed(self, event: Any) -> None:
        """
        处理应用系统状态变更事件
        触发：检查关联计划并提醒
        """
        # 从事件中获取信息
        app_id = getattr(event, 'app_id', '')
        old_status = getattr(event, 'old_status', '')
        new_status = getattr(event, 'new_status', '')
        changed_by = getattr(event, 'changed_by', '')

        self._sync_service.sync_inventory_status_changed(
            app_id=app_id,
            old_status=old_status,
            new_status=new_status,
            changed_by=changed_by
        )

    def handle_application_deleted(self, event: Any) -> None:
        """
        处理应用系统删除事件
        触发：检查关联计划，阻止删除或提醒
        """
        # 实际实现中应该：
        # 1. 查询所有关联此应用系统的计划
        # 2. 如果有进行中的计划，阻止删除或提醒
        pass


def register_sync_event_handlers(db_session=None):
    """
    注册同步事件处理器
    返回处理器实例供事件总线注册
    """
    plan_handler = PlanSyncEventHandler(db_session)
    inventory_handler = InventorySyncEventHandler(db_session)

    return {
        # 计划事件
        PlanStartedEvent: plan_handler.handle_plan_started,
        PlanCompletedEvent: plan_handler.handle_plan_completed,
        PlanCancelledEvent: plan_handler.handle_plan_cancelled,
        PlanStatusChangedEvent: plan_handler.handle_plan_status_changed,
        PlanInventoryLinkedEvent: plan_handler.handle_plan_inventory_linked,

        # 台账事件（需要在导入时处理）
        # ApplicationStatusChangedEvent: inventory_handler.handle_application_status_changed,
        # ApplicationDeletedEvent: inventory_handler.handle_application_deleted,
    }
