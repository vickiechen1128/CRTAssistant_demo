"""
计划仓储接口（抽象）
定义领域层与基础设施层的契约
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime

from ..entities.plan import Plan
from ..value_objects.plan_status import PlanStatus
from ..value_objects.category import Category
from ..value_objects.priority import Priority


class PlanRepository(ABC):
    """
    计划仓储接口
    
    职责：
    1. 定义领域对象的持久化操作
    2. 屏蔽底层存储细节
    3. 支持领域对象的重建
    """
    
    @abstractmethod
    def save(self, plan: Plan) -> Plan:
        """保存计划（创建或更新）"""
        pass
    
    @abstractmethod
    def find_by_id(self, plan_id: str) -> Optional[Plan]:
        """根据ID查找计划"""
        pass
    
    @abstractmethod
    def find_by_data_tag(self, data_tag: str) -> Optional[Plan]:
        """根据数据标签查找计划"""
        pass
    
    @abstractmethod
    def find_all(
        self,
        status: Optional[PlanStatus] = None,
        category: Optional[Category] = None,
        priority: Optional[Priority] = None,
        created_by: Optional[str] = None,
        keyword: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[List[Plan], int]:
        """
        查询计划列表
        
        Returns:
            (计划列表, 总数)
        """
        pass
    
    @abstractmethod
    def delete(self, plan_id: str) -> bool:
        """删除计划"""
        pass
    
    @abstractmethod
    def exists(self, plan_id: str) -> bool:
        """检查计划是否存在"""
        pass
    
    @abstractmethod
    def get_next_sequence(self, date: datetime) -> int:
        """获取指定日期的下一个序号（用于生成ID）"""
        pass
