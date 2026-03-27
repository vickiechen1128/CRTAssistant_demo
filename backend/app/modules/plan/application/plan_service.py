"""
计划应用服务
协调领域对象完成用例
"""
from datetime import datetime
from typing import List, Optional, Tuple

from ..domain.entities.plan import Plan
from ..domain.value_objects.category import Category
from ..domain.value_objects.priority import Priority
from ..domain.value_objects.plan_status import PlanStatus
from ..domain.repositories.plan_repository import PlanRepository
from ..domain.services.plan_domain_service import PlanDomainService
from .dtos.plan_dtos import (
    CreatePlanRequest,
    UpdatePlanRequest,
    PlanResponse,
    PlanListResponse,
    PlanFilterRequest
)


class PlanService:
    """
    计划应用服务
    
    职责：
    1. 接收DTO，转换为领域对象
    2. 协调领域服务和仓储
    3. 执行用例并返回DTO
    4. 处理事务边界
    """
    
    def __init__(
        self,
        plan_repository: PlanRepository,
        plan_domain_service: PlanDomainService
    ):
        self._repository = plan_repository
        self._domain_service = plan_domain_service
    
    def create_plan(
        self,
        request: CreatePlanRequest,
        created_by: str
    ) -> PlanResponse:
        """创建计划"""
        # 转换值对象
        category = Category(request.category)
        priority = Priority.from_string(request.priority)
        
        # 生成数据标签
        data_tag = self._domain_service.generate_data_tag(
            category,
            datetime.utcnow()
        )
        
        # 创建工作流模板ID（根据分类）
        workflow_template_id = request.workflow_template_id or f"template_{request.category}"
        
        # 创建领域对象
        plan = Plan.create(
            name=request.name,
            category=category,
            priority=priority,
            data_tag=data_tag,
            created_by=created_by,
            description=request.description,
            planned_start_time=request.planned_start_time,
            planned_end_time=request.planned_end_time,
            workflow_template_id=workflow_template_id
        )
        
        # 持久化
        saved_plan = self._repository.save(plan)
        
        return self._to_response(saved_plan)
    
    def update_plan(
        self,
        plan_id: str,
        request: UpdatePlanRequest,
        updated_by: str
    ) -> PlanResponse:
        """更新计划"""
        plan = self._repository.find_by_id(plan_id)
        if not plan:
            raise ValueError(f"Plan not found: {plan_id}")
        
        # 转换优先级
        priority = None
        if request.priority:
            priority = Priority.from_string(request.priority)
        
        # 更新领域对象
        plan.update(
            name=request.name,
            description=request.description,
            planned_start_time=request.planned_start_time,
            planned_end_time=request.planned_end_time,
            priority=priority
        )
        
        # 持久化
        saved_plan = self._repository.save(plan)
        
        return self._to_response(saved_plan)
    
    def get_plan(self, plan_id: str) -> PlanResponse:
        """获取计划详情"""
        plan = self._repository.find_by_id(plan_id)
        if not plan:
            raise ValueError(f"Plan not found: {plan_id}")
        
        return self._to_response(plan)
    
    def list_plans(
        self,
        filter_request: PlanFilterRequest
    ) -> PlanListResponse:
        """查询计划列表"""
        # 转换筛选条件
        status = None
        if filter_request.status:
            status = PlanStatus(filter_request.status)
        
        category = None
        if filter_request.category:
            category = Category(filter_request.category)
        
        priority = None
        if filter_request.priority:
            priority = Priority.from_string(filter_request.priority)
        
        # 查询
        skip = (filter_request.page - 1) * filter_request.page_size
        plans, total = self._repository.find_all(
            status=status,
            category=category,
            priority=priority,
            created_by=filter_request.created_by,
            keyword=filter_request.keyword,
            start_date=filter_request.start_date,
            end_date=filter_request.end_date,
            skip=skip,
            limit=filter_request.page_size
        )
        
        # 构建响应
        total_pages = (total + filter_request.page_size - 1) // filter_request.page_size
        
        return PlanListResponse(
            items=[self._to_response(p) for p in plans],
            total=total,
            page=filter_request.page,
            page_size=filter_request.page_size,
            total_pages=total_pages
        )
    
    def delete_plan(self, plan_id: str, deleted_by: str) -> bool:
        """删除计划"""
        plan = self._repository.find_by_id(plan_id)
        if not plan:
            raise ValueError(f"Plan not found: {plan_id}")
        
        if not plan.can_delete():
            raise ValueError(f"Cannot delete plan in {plan.status.value} status")
        
        return self._repository.delete(plan_id)
    
    def start_plan(self, plan_id: str, started_by: str) -> PlanResponse:
        """启动计划"""
        plan = self._repository.find_by_id(plan_id)
        if not plan:
            raise ValueError(f"Plan not found: {plan_id}")
        
        plan.start(started_by)
        saved_plan = self._repository.save(plan)
        
        return self._to_response(saved_plan)
    
    def complete_plan(self, plan_id: str, completed_by: str) -> PlanResponse:
        """完成计划"""
        plan = self._repository.find_by_id(plan_id)
        if not plan:
            raise ValueError(f"Plan not found: {plan_id}")
        
        plan.complete(completed_by)
        saved_plan = self._repository.save(plan)
        
        return self._to_response(saved_plan)
    
    def cancel_plan(
        self,
        plan_id: str,
        cancelled_by: str,
        reason: Optional[str] = None
    ) -> PlanResponse:
        """取消计划"""
        plan = self._repository.find_by_id(plan_id)
        if not plan:
            raise ValueError(f"Plan not found: {plan_id}")
        
        plan.cancel(cancelled_by, reason)
        saved_plan = self._repository.save(plan)
        
        return self._to_response(saved_plan)
    
    def link_inventory(
        self,
        plan_id: str,
        inventory_ids: List[str],
        linked_by: str
    ) -> PlanResponse:
        """关联台账"""
        plan = self._repository.find_by_id(plan_id)
        if not plan:
            raise ValueError(f"Plan not found: {plan_id}")
        
        # 验证台账关联
        if not self._domain_service.validate_inventory_link(
            plan.category,
            inventory_ids,
            plan.inventory_action
        ):
            raise ValueError("Invalid inventory link for this category")
        
        plan.link_inventory(inventory_ids, linked_by)
        saved_plan = self._repository.save(plan)
        
        return self._to_response(saved_plan)
    
    def _to_response(self, plan: Plan) -> PlanResponse:
        """将领域对象转换为响应DTO"""
        return PlanResponse(
            id=plan.id,
            data_tag=plan.data_tag,
            name=plan.name,
            category=plan.category.value,
            priority=str(plan.priority),
            status=plan.status.value,
            description=plan.description,
            planned_start_time=plan.planned_start_time,
            planned_end_time=plan.planned_end_time,
            actual_start_time=plan.actual_start_time,
            actual_end_time=plan.actual_end_time,
            workflow_template_id=plan.workflow_template_id,
            inventory_ids=plan.inventory_ids,
            inventory_action=plan.inventory_action,
            approval_files=[str(fid) for fid in plan.approval_files],
            created_by=plan.created_by,
            created_at=plan.created_at,
            updated_at=plan.updated_at,
            is_overdue=plan.is_overdue
        )
