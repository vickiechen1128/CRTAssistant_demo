"""
生命周期日志应用服务
应用层服务，协调领域层和基础设施层
"""
from datetime import datetime
from typing import Optional, List, Dict, Any

from app.modules.inventory.domain.repositories.lifecycle_log_repository import LifecycleLogRepository
from app.modules.inventory.domain.value_objects.log_type import LogType

from .dtos.lifecycle_log_dtos import (
    CreateLifecycleLogDTO,
    LifecycleLogResponseDTO,
    TimelineItemDTO,
    TimelineResponseDTO,
    TimelineFilterDTO,
    LogTypeInfoDTO,
    LogStatisticsDTO,
)


class LifecycleLogService:
    """生命周期日志应用服务"""

    def __init__(self, log_repo: LifecycleLogRepository):
        self._log_repo = log_repo

    # ==================== 日志CRUD ====================

    async def create_log(
        self,
        dto: CreateLifecycleLogDTO
    ) -> LifecycleLogResponseDTO:
        """创建生命周期日志"""
        from app.modules.inventory.domain.entities.lifecycle_log import LifecycleLog

        log = LifecycleLog.create(
            app_id=dto.app_id if hasattr(dto, 'app_id') else "",
            log_type=LogType.from_string(dto.log_type) if isinstance(dto.log_type, str) else dto.log_type,
            event_title=dto.event_title,
            operator=dto.operator,
            module_id=dto.related_module_id,
            event_description=dto.description,
            before_data=dto.before_data,
            after_data=dto.after_data,
            related_plan_id=dto.related_plan_id,
        )

        saved = await self._log_repo.save(log)
        return self._to_response_dto(saved)

    async def get_log(self, log_id: str) -> LifecycleLogResponseDTO:
        """获取日志详情"""
        log = await self._log_repo.get_by_id(log_id)
        if not log:
            raise ValueError(f"Log with id '{log_id}' not found")
        return self._to_response_dto(log)

    async def list_logs(
        self,
        app_id: str,
        log_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[LifecycleLogResponseDTO]:
        """获取日志列表"""
        logs = await self._log_repo.get_by_app_id(
            app_id, log_type=log_type, limit=limit, offset=offset
        )
        return [self._to_response_dto(log) for log in logs]

    async def delete_logs_by_app(self, app_id: str) -> int:
        """删除应用的所有日志"""
        return await self._log_repo.delete_by_app_id(app_id)

    # ==================== 时间线服务 ====================

    async def get_timeline(
        self,
        app_id: str,
        filter_dto: Optional[TimelineFilterDTO] = None
    ) -> TimelineResponseDTO:
        """获取应用的时间线数据"""
        # 解析时间参数
        start_time = None
        end_time = None

        if filter_dto:
            if filter_dto.start_time:
                start_time = datetime.fromisoformat(filter_dto.start_time.replace('Z', '+00:00'))
            if filter_dto.end_time:
                end_time = datetime.fromisoformat(filter_dto.end_time.replace('Z', '+00:00'))

        logs = await self._log_repo.get_timeline(
            app_id,
            start_time=start_time,
            end_time=end_time,
            limit=filter_dto.limit if filter_dto else 100
        )

        # 过滤日志类型
        if filter_dto and filter_dto.log_type:
            logs = [log for log in logs if log.log_type.value == filter_dto.log_type]

        items = [self._to_timeline_item_dto(log) for log in logs]

        return TimelineResponseDTO(
            items=items,
            total=len(items)
        )

    async def get_timeline_by_plan(
        self,
        plan_id: str
    ) -> TimelineResponseDTO:
        """获取计划关联的时间线（双向追溯）"""
        logs = await self._log_repo.get_by_plan_id(plan_id)
        items = [self._to_timeline_item_dto(log) for log in logs]

        return TimelineResponseDTO(
            items=items,
            total=len(items)
        )

    async def get_timeline_by_module(
        self,
        module_id: str
    ) -> TimelineResponseDTO:
        """获取功能模块的时间线"""
        logs = await self._log_repo.get_by_module_id(module_id)
        items = [self._to_timeline_item_dto(log) for log in logs]

        return TimelineResponseDTO(
            items=items,
            total=len(items)
        )

    # ==================== 快捷创建方法 ====================

    async def record_module_launch(
        self,
        app_id: str,
        module_name: str,
        plan_id: Optional[str] = None,
        plan_title: Optional[str] = None,
        operator: str = ""
    ) -> LifecycleLogResponseDTO:
        """记录功能上线"""
        log = await self._log_repo.create_module_launch_log(
            app_id=app_id,
            module_name=module_name,
            plan_id=plan_id,
            plan_title=plan_title,
            operator=operator
        )
        return self._to_response_dto(log)

    async def record_change(
        self,
        app_id: str,
        log_type: str,
        title: str,
        before_data: Optional[Dict[str, Any]] = None,
        after_data: Optional[Dict[str, Any]] = None,
        plan_id: Optional[str] = None,
        module_id: Optional[str] = None,
        operator: str = ""
    ) -> LifecycleLogResponseDTO:
        """记录变更"""
        log = await self._log_repo.create_change_log(
            app_id=app_id,
            log_type=log_type,
            title=title,
            before_data=before_data,
            after_data=after_data,
            plan_id=plan_id,
            module_id=module_id,
            operator=operator
        )
        return self._to_response_dto(log)

    # ==================== 统计服务 ====================

    async def get_statistics(self, app_id: str) -> LogStatisticsDTO:
        """获取日志统计"""
        # 获取所有日志
        logs = await self._log_repo.get_by_app_id(app_id, limit=10000)

        # 类型分布
        type_distribution: Dict[str, int] = {}
        monthly_trend: Dict[str, int] = {}

        for log in logs:
            # 类型统计
            log_type = log.log_type.value if hasattr(log.log_type, 'value') else str(log.log_type)
            type_distribution[log_type] = type_distribution.get(log_type, 0) + 1

            # 月度趋势
            if log.operation_time:
                month_key = log.operation_time.strftime("%Y-%m")
                monthly_trend[month_key] = monthly_trend.get(month_key, 0) + 1

        # 转换月度趋势为列表
        trend_list = [
            {"month": k, "count": v}
            for k, v in sorted(monthly_trend.items())
        ]

        return LogStatisticsDTO(
            total_count=len(logs),
            type_distribution=type_distribution,
            monthly_trend=trend_list
        )

    def get_log_type_list(self) -> List[LogTypeInfoDTO]:
        """获取日志类型列表"""
        types = [
            LogType.system_launch(),
            LogType.system_upgrade(),
            LogType.system_rollback(),
            LogType.system_offline(),
            LogType.module_launch(),
            LogType.module_update(),
            LogType.module_offline(),
            LogType.config_change(),
            LogType.owner_change(),
            LogType.status_change(),
            LogType.manual(),
        ]

        return [
            LogTypeInfoDTO(
                value=t.value,
                label=t.label,
                description=t.description,
                icon=t.icon,
                color=t.color
            )
            for t in types
        ]

    # ==================== DTO转换 ====================

    def _to_response_dto(self, log) -> LifecycleLogResponseDTO:
        """转换为响应DTO"""
        log_type = log.log_type.value if hasattr(log.log_type, 'value') else str(log.log_type)

        # 获取日志类型显示信息
        try:
            log_type_obj = LogType.from_string(log_type)
            log_type_display = log_type_obj.label
        except:
            log_type_display = log_type

        return LifecycleLogResponseDTO(
            id=log.id,
            app_id=log.app_id,
            log_type=log_type,
            log_type_display=log_type_display,
            event_title=log.event_title,
            description=log.event_description,
            before_data=log.before_data,
            after_data=log.after_data,
            related_plan_id=log.related_plan_id,
            plan_title=getattr(log, 'plan_title', None),
            related_module_id=getattr(log, 'module_id', None),
            operator=log.operator,
            operation_time=log.operation_time.isoformat() if log.operation_time else None,
        )

    def _to_timeline_item_dto(self, log) -> TimelineItemDTO:
        """转换为时间线条目DTO"""
        log_type = log.log_type.value if hasattr(log.log_type, 'value') else str(log.log_type)

        # 获取日志类型显示信息
        try:
            log_type_obj = LogType.from_string(log_type)
            type_display = log_type_obj.label
            icon = log_type_obj.icon
            color = log_type_obj.color
        except:
            type_display = log_type
            icon = "info-circle"
            color = "default"

        # 计算变更摘要
        changes = None
        if log.before_data or log.after_data:
            changes = {"fields": [], "changes": []}
            if log.after_data:
                changes["fields"] = list(log.after_data.keys())
            if log.before_data and log.after_data:
                for key in set(list(log.before_data.keys()) + list(log.after_data.keys())):
                    before = log.before_data.get(key)
                    after = log.after_data.get(key)
                    if before != after:
                        changes["changes"].append({
                            "field": key,
                            "before": before,
                            "after": after
                        })

        return TimelineItemDTO(
            id=log.id,
            type=log_type,
            type_display=type_display,
            title=log.event_title,
            description=log.event_description,
            time=log.operation_time.isoformat() if log.operation_time else None,
            operator=log.operator,
            plan_id=log.related_plan_id,
            plan_title=getattr(log, 'plan_title', None),
            module_id=getattr(log, 'module_id', None),
            changes=changes,
            icon=icon,
            color=color
        )
