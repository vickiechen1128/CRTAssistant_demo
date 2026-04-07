"""
计划领域服务
处理跨实体的业务逻辑
"""
from datetime import datetime
from typing import Optional

from ..value_objects.plan_tag import PlanTag
from ..value_objects.category import Category
from ..repositories.plan_repository import PlanRepository


class PlanDomainService:
    """
    计划领域服务
    
    职责：
    1. 处理跨实体的业务逻辑
    2. 协调多个聚合根
    3. 执行复杂的业务规则验证
    """
    
    def __init__(self, plan_repository: PlanRepository):
        self._plan_repository = plan_repository
    
    def generate_data_tag(self, category: Category, date: datetime) -> str:
        """生成数据标签"""
        sequence = self.get_next_sequence(date)
        return PlanTag.generate(category.code, date, sequence).value
    
    def get_next_sequence(self, date: datetime) -> int:
        """获取当日流水号（用于生成PlanID）"""
        return self._plan_repository.get_next_sequence(date)
    
    def validate_inventory_link(
        self,
        category: Category,
        inventory_ids: list,
        action: str
    ) -> bool:
        """
        验证台账关联
        
        规则：
        - 安全检查不需要关联台账
        - 新系统上线必须新增台账
        - 其他类型必须选择已有台账
        """
        if not category.requires_inventory:
            return len(inventory_ids) == 0
        
        if category.value == "new_system":
            # 新系统上线：必须新增台账
            return len(inventory_ids) > 0 and action == "create_new"
        
        # 其他类型：必须选择已有台账
        return len(inventory_ids) > 0 and action in ["select_and_edit", "select_existing"]
    
    def check_name_uniqueness(
        self,
        name: str,
        exclude_plan_id: Optional[str] = None
    ) -> bool:
        """检查计划名称是否唯一"""
        plans, _ = self._plan_repository.find_all(keyword=name)
        
        if exclude_plan_id:
            plans = [p for p in plans if p.id != exclude_plan_id]
        
        return len(plans) == 0
    
    def can_start_plan(self, plan_id: str) -> tuple[bool, str]:
        """
        检查是否可以启动计划
        
        规则：
        - 计划必须存在
        - 状态必须是 DRAFT 或 PENDING
        - P0优先级计划需要确认
        """
        plan = self._plan_repository.find_by_id(plan_id)
        if not plan:
            return False, "计划不存在"
        
        if not plan.status.is_startable:
            return False, f"当前状态 {plan.status.value} 不允许启动"
        
        if plan.status.value == "PENDING":
            return True, "P0优先级计划需要二次确认"
        
        return True, "可以启动"
