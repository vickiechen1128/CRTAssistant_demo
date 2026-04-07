"""
生命周期日志仓储接口
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional, Dict, Any

from app.modules.inventory.domain.entities.lifecycle_log import LifecycleLog


class LifecycleLogRepository(ABC):
    """生命周期日志仓储接口"""
    
    @abstractmethod
    async def get_by_id(self, log_id: str) -> Optional[LifecycleLog]:
        """根据ID获取日志"""
        pass
    
    @abstractmethod
    async def get_by_app_id(
        self, 
        app_id: str,
        log_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[LifecycleLog]:
        """获取应用的生命周期日志"""
        pass
    
    @abstractmethod
    async def get_by_plan_id(self, plan_id: str) -> List[LifecycleLog]:
        """获取关联到指定计划的所有日志（用于双向追溯）"""
        pass
    
    @abstractmethod
    async def get_by_module_id(self, module_id: str) -> List[LifecycleLog]:
        """获取功能模块相关的日志"""
        pass
    
    @abstractmethod
    async def get_timeline(
        self, 
        app_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[LifecycleLog]:
        """获取应用的时间线数据"""
        pass
    
    @abstractmethod
    async def save(self, log: LifecycleLog) -> LifecycleLog:
        """保存日志"""
        pass
    
    @abstractmethod
    async def save_many(self, logs: List[LifecycleLog]) -> List[LifecycleLog]:
        """批量保存日志"""
        pass
    
    @abstractmethod
    async def delete_by_app_id(self, app_id: str) -> int:
        """删除应用的所有日志"""
        pass
    
    @abstractmethod
    async def count_by_app_id(
        self, 
        app_id: str,
        log_type: Optional[str] = None
    ) -> int:
        """统计日志数量"""
        pass
    
    @abstractmethod
    async def get_latest_by_type(
        self, 
        app_id: str, 
        log_type: str
    ) -> Optional[LifecycleLog]:
        """获取指定类型的最新日志"""
        pass
    
    @abstractmethod
    async def create_module_launch_log(
        self,
        app_id: str,
        module_name: str,
        plan_id: Optional[str] = None,
        plan_title: Optional[str] = None,
        operator: str = ""
    ) -> LifecycleLog:
        """创建功能上线日志"""
        pass
    
    @abstractmethod
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
        pass
