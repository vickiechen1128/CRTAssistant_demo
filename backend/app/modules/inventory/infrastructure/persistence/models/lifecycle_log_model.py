"""
生命周期日志数据库模型
"""
from datetime import datetime
from typing import TYPE_CHECKING, Optional, Dict, Any

from sqlalchemy import String, DateTime, ForeignKey, Text, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from .inventory_model import ApplicationModel
    from .function_module_model import FunctionModuleModel


class LifecycleLogModel(Base):
    """生命周期日志数据模型"""
    __tablename__ = 'inventory_lifecycle_logs'
    
    # 主键
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    
    # 关联应用ID
    app_id: Mapped[str] = mapped_column(
        String(36), 
        ForeignKey('inventory_applications.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    # 日志类型 (system_launch/module_launch/config_change 等)
    log_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # 事件标题
    event_title: Mapped[str] = mapped_column(String(200), nullable=False)
    
    # 事件描述
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # 变更前数据快照 (JSON)
    before_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # 变更后数据快照 (JSON)
    after_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # 关联的计划ID (双向追溯)
    related_plan_id: Mapped[Optional[str]] = mapped_column(
        String(50), 
        ForeignKey('plans.id', ondelete='SET NULL'),
        nullable=True,
        index=True
    )
    
    # 关联的功能模块ID
    related_module_id: Mapped[Optional[str]] = mapped_column(
        String(36), 
        ForeignKey('inventory_function_modules.id', ondelete='SET NULL'),
        nullable=True,
        index=True
    )
    
    # 操作人
    operator: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # 操作时间
    operation_time: Mapped[datetime] = mapped_column(
        DateTime, 
        nullable=False, 
        default=datetime.utcnow,
        index=True
    )
    
    # 关联的计划信息（冗余存储，用于展示）
    plan_title: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    
    # 关联关系
    application: Mapped["ApplicationModel"] = relationship(
        "ApplicationModel", 
        back_populates="lifecycle_logs",
        lazy="joined"
    )
    
    # 关联功能模块
    function_module: Mapped[Optional["FunctionModuleModel"]] = relationship(
        "FunctionModuleModel",
        back_populates="lifecycle_logs",
        lazy="joined"
    )
    
    # 关联计划
    related_plan: Mapped[Optional["PlanModel"]] = relationship(
        "PlanModel",
        lazy="joined"
    )
    
    # 索引优化查询
    __table_args__ = (
        Index('idx_log_app_type', 'app_id', 'log_type'),
        Index('idx_log_time', 'operation_time'),
        Index('idx_log_plan', 'related_plan_id', 'operation_time'),
        Index('idx_log_module', 'related_module_id', 'operation_time'),
    )
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'app_id': self.app_id,
            'log_type': self.log_type,
            'event_title': self.event_title,
            'description': self.description,
            'before_data': self.before_data,
            'after_data': self.after_data,
            'related_plan_id': self.related_plan_id,
            'plan_title': self.plan_title,
            'related_module_id': self.related_module_id,
            'operator': self.operator,
            'operation_time': self.operation_time.isoformat() if self.operation_time else None,
        }
    
    def to_timeline_dict(self) -> dict:
        """转换为时间线展示格式"""
        return {
            'id': self.id,
            'type': self.log_type,
            'title': self.event_title,
            'description': self.description,
            'time': self.operation_time.isoformat() if self.operation_time else None,
            'operator': self.operator,
            'plan_id': self.related_plan_id,
            'plan_title': self.plan_title,
            'module_id': self.related_module_id,
            'changes': self._get_changes_summary(),
        }
    
    def _get_changes_summary(self) -> Optional[Dict[str, Any]]:
        """获取变更摘要"""
        if not self.before_data and not self.after_data:
            return None
        
        changes = []
        
        if self.before_data and self.after_data:
            # 比较前后数据找出变更字段
            for key in set(list(self.before_data.keys()) + list(self.after_data.keys())):
                before = self.before_data.get(key)
                after = self.after_data.get(key)
                if before != after:
                    changes.append({
                        'field': key,
                        'before': before,
                        'after': after
                    })
        
        return {
            'fields': list(self.after_data.keys()) if self.after_data else [],
            'changes': changes if changes else []
        }
