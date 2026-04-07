"""
生命周期日志仓储实现
"""
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any

from sqlalchemy import select, delete, func, desc
from sqlalchemy.orm import Session

from app.modules.inventory.domain.entities.lifecycle_log import LifecycleLog
from app.modules.inventory.domain.repositories.lifecycle_log_repository import LifecycleLogRepository
from app.modules.inventory.domain.value_objects.log_type import LogType
from app.modules.inventory.infrastructure.persistence.models.lifecycle_log_model import LifecycleLogModel


class LifecycleLogRepositoryImpl(LifecycleLogRepository):
    """生命周期日志仓储实现"""

    def __init__(self, session: Session):
        self.session = session

    def _to_entity(self, model: LifecycleLogModel) -> LifecycleLog:
        """将模型转换为领域实体"""
        return LifecycleLog(
            id=model.id,
            app_id=model.app_id,
            log_type=LogType.from_string(model.log_type),
            event_title=model.event_title,
            module_id=model.related_module_id,
            event_description=model.description,
            before_data=model.before_data,
            after_data=model.after_data,
            related_plan_id=model.related_plan_id,
            operator=model.operator or "",
            operation_time=model.operation_time,
            attachments=[],  # 模型中可能没有这个字段，使用空列表
            created_at=model.created_at,
        )

    def _to_model(self, entity: LifecycleLog) -> LifecycleLogModel:
        """将领域实体转换为模型"""
        return LifecycleLogModel(
            id=entity.id or str(uuid.uuid4()),
            app_id=entity.app_id,
            log_type=entity.log_type.value if hasattr(entity.log_type, 'value') else str(entity.log_type),
            event_title=entity.event_title,
            description=entity.event_description,
            before_data=entity.before_data,
            after_data=entity.after_data,
            related_plan_id=entity.related_plan_id,
            related_module_id=entity.module_id,
            operator=entity.operator,
            operation_time=entity.operation_time or datetime.utcnow(),
        )

    async def get_by_id(self, log_id: str) -> Optional[LifecycleLog]:
        """根据ID获取日志"""
        result = self.session.execute(
            select(LifecycleLogModel).where(LifecycleLogModel.id == log_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_app_id(
        self,
        app_id: str,
        log_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[LifecycleLog]:
        """获取应用的生命周期日志"""
        query = select(LifecycleLogModel).where(LifecycleLogModel.app_id == app_id)

        if log_type:
            query = query.where(LifecycleLogModel.log_type == log_type)

        query = query.order_by(desc(LifecycleLogModel.operation_time))
        query = query.limit(limit).offset(offset)

        result = self.session.execute(query)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def get_by_plan_id(self, plan_id: str) -> List[LifecycleLog]:
        """获取关联到指定计划的所有日志（用于双向追溯）"""
        result = self.session.execute(
            select(LifecycleLogModel)
            .where(LifecycleLogModel.related_plan_id == plan_id)
            .order_by(desc(LifecycleLogModel.operation_time))
        )
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def get_by_module_id(self, module_id: str) -> List[LifecycleLog]:
        """获取功能模块相关的日志"""
        result = self.session.execute(
            select(LifecycleLogModel)
            .where(LifecycleLogModel.related_module_id == module_id)
            .order_by(desc(LifecycleLogModel.operation_time))
        )
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def get_timeline(
        self,
        app_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[LifecycleLog]:
        """获取应用的时间线数据"""
        query = select(LifecycleLogModel).where(LifecycleLogModel.app_id == app_id)

        if start_time:
            query = query.where(LifecycleLogModel.operation_time >= start_time)
        if end_time:
            query = query.where(LifecycleLogModel.operation_time <= end_time)

        query = query.order_by(desc(LifecycleLogModel.operation_time))
        query = query.limit(limit)

        result = self.session.execute(query)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def save(self, log: LifecycleLog) -> LifecycleLog:
        """保存日志"""
        if not log.id:
            log.id = str(uuid.uuid4())
        if not log.operation_time:
            log.operation_time = datetime.utcnow()

        model = self._to_model(log)
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._to_entity(model)

    async def save_many(self, logs: List[LifecycleLog]) -> List[LifecycleLog]:
        """批量保存日志"""
        saved_logs = []
        for log in logs:
            saved_log = self.save(log)
            saved_logs.append(saved_log)
        return saved_logs

    async def delete_by_app_id(self, app_id: str) -> int:
        """删除应用的所有日志"""
        result = self.session.execute(
            delete(LifecycleLogModel).where(LifecycleLogModel.app_id == app_id)
        )
        self.session.commit()
        return result.rowcount

    async def count_by_app_id(
        self,
        app_id: str,
        log_type: Optional[str] = None
    ) -> int:
        """统计日志数量"""
        query = select(func.count()).where(LifecycleLogModel.app_id == app_id)

        if log_type:
            query = query.where(LifecycleLogModel.log_type == log_type)

        result = self.session.execute(query)
        return result.scalar() or 0

    async def get_latest_by_type(
        self,
        app_id: str,
        log_type: str
    ) -> Optional[LifecycleLog]:
        """获取指定类型的最新日志"""
        result = self.session.execute(
            select(LifecycleLogModel)
            .where(
                LifecycleLogModel.app_id == app_id,
                LifecycleLogModel.log_type == log_type
            )
            .order_by(desc(LifecycleLogModel.operation_time))
            .limit(1)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def create_module_launch_log(
        self,
        app_id: str,
        module_name: str,
        plan_id: Optional[str] = None,
        plan_title: Optional[str] = None,
        operator: str = ""
    ) -> LifecycleLog:
        """创建功能上线日志"""
        log = LifecycleLog(
            id=str(uuid.uuid4()),
            app_id=app_id,
            log_type=LogType.module_launch(),
            event_title=f"功能上线: {module_name}",
            event_description=f"功能模块 [{module_name}] 已上线",
            related_plan_id=plan_id,
            operator=operator,
            operation_time=datetime.utcnow(),
        )
        return self.save(log)

    async def create_change_log(
        self,
        app_id: str,
        log_type: str,
        title: str,
        before_data: Optional[Dict[str, Any]] = None,
        after_data: Optional[Dict[str, Any]] = None,
        plan_id: Optional[str] = None,
        module_id: Optional[str] = None,
        operator: str = ""
    ) -> LifecycleLog:
        """创建变更日志"""
        log = LifecycleLog(
            id=str(uuid.uuid4()),
            app_id=app_id,
            log_type=LogType.from_string(log_type) if isinstance(log_type, str) else log_type,
            event_title=title,
            before_data=before_data,
            after_data=after_data,
            related_plan_id=plan_id,
            module_id=module_id,
            operator=operator,
            operation_time=datetime.utcnow(),
        )
        return self.save(log)
