"""
计划应用服务
协调领域对象完成用例
"""
from datetime import datetime
from typing import List, Optional, Tuple, Dict, Any

from ..domain.entities.plan import Plan
from ..domain.value_objects.category import Category
from ..domain.value_objects.priority import Priority
from ..domain.value_objects.plan_status import PlanStatus
from ..domain.value_objects.affected_module import AffectedModule
from ..domain.repositories.plan_repository import PlanRepository
from ..domain.services.plan_domain_service import PlanDomainService
from ..domain.services.plan_completion_service import PlanCompletionService
from ..domain.services.inventory_service import InventoryService
from .dtos.plan_dtos import (
    CreatePlanRequest,
    UpdatePlanRequest,
    PlanResponse,
    PlanListResponse,
    PlanFilterRequest,
    PlanDetailResponse,
    PlanPreviewRequest,
    PlanPreviewResponse,
    GeneratePlanIdResponse,
    AffectedModuleItem,
    ApprovalFileDetail,
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
        plan_domain_service: PlanDomainService,
        plan_completion_service: Optional[PlanCompletionService] = None,
        inventory_service: Optional[InventoryService] = None
    ):
        self._repository = plan_repository
        self._domain_service = plan_domain_service
        self._completion_service = plan_completion_service
        self._inventory_service = inventory_service
    
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
        
        # 转换受影响功能模块
        affected_modules = [
            AffectedModule(
                module_id=m.module_id,
                module_name=m.module_name,
                action=m.action,
                before_version=m.before_version,
                after_version=m.after_version,
                change_description=m.change_description,
            )
            for m in request.affected_modules
        ]
        
        # 转换审批材料
        approval_files_detail = [
            f.dict() for f in request.approval_files
        ]
        
        # 确定工作流模板ID（根据分类）
        workflow_template_id = request.workflow_template_id or f"template_{request.category}"
        
        # 确定模板类型
        template_type = request.template_type or category.default_template_type
        
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
            workflow_template_id=workflow_template_id,
            affected_modules=affected_modules,
            approval_files_detail=approval_files_detail,
            template_type=template_type,
        )
        
        # 设置关联台账
        if request.related_inventory_ids:
            plan.inventory_ids = request.related_inventory_ids
        
        # 持久化
        saved_plan = self._repository.save(plan)
        
        # 同步更新应用系统的 related_plan_ids（双向关联）
        if request.related_inventory_ids and self._inventory_service:
            for app_id in request.related_inventory_ids:
                try:
                    self._inventory_service.link_to_plan("application", app_id, saved_plan.id)
                except Exception as e:
                    # 记录错误但不影响主流程
                    print(f"Failed to link app {app_id} to plan {saved_plan.id}: {e}")
        
        # 根据计划分类执行相应的台账操作
        # new_system: 创建应用系统时同步创建功能模块
        # new_feature: 创建计划时同步创建功能模块到已有应用系统
        if self._inventory_service and request.related_inventory_ids:
            try:
                self._sync_inventory_on_create(saved_plan, request, created_by)
            except Exception as e:
                # 记录错误但不影响主流程
                print(f"Failed to sync inventory on plan creation: {e}")
        
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
        
        # 转换受影响功能模块
        affected_modules = None
        if request.affected_modules is not None:
            affected_modules = [
                AffectedModule(
                    module_id=m.module_id,
                    module_name=m.module_name,
                    action=m.action,
                    before_version=m.before_version,
                    after_version=m.after_version,
                    change_description=m.change_description,
                )
                for m in request.affected_modules
            ]
        
        # 更新领域对象
        plan.update(
            name=request.name,
            description=request.description,
            planned_start_time=request.planned_start_time,
            planned_end_time=request.planned_end_time,
            priority=priority,
            affected_modules=affected_modules,
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
    
    def get_plan_detail(self, plan_id: str) -> PlanDetailResponse:
        """获取计划详情（包含完整关联信息）"""
        plan = self._repository.find_by_id(plan_id)
        if not plan:
            raise ValueError(f"Plan not found: {plan_id}")

        # 基础响应
        base_response = self._to_response(plan)

        # 加载关联应用系统信息
        related_applications = []
        if plan.inventory_ids and self._completion_service:
            try:
                # 使用台账服务获取应用系统详情
                inventory_service = self._completion_service._inventory_service
                apps = inventory_service.get_applications_by_ids(plan.inventory_ids)
                related_applications = [
                    {
                        "id": app.get("id"),
                        "app_name": app.get("app_name", "未命名应用"),
                        "system_type": app.get("system_type", "unknown"),
                        "business_owner": app.get("business_owner", ""),
                        "project_owner": app.get("project_owner", ""),
                        "status": app.get("status", "unknown"),
                        "view_url": f"/inventories/applications/{app.get('id')}",
                    }
                    for app in apps
                ]
            except Exception as e:
                # 如果获取失败，至少返回ID列表
                related_applications = [
                    {
                        "id": inv_id,
                        "app_name": "未知应用",
                        "system_type": "unknown",
                        "business_owner": "",
                        "project_owner": "",
                        "status": "unknown",
                        "view_url": f"/inventories/applications/{inv_id}",
                    }
                    for inv_id in plan.inventory_ids
                ]

        # 加载影响功能模块详细信息
        related_modules = [
            {
                "id": m.module_id,
                "module_name": m.module_name,
                "action": m.action,
                "action_label": "新增" if m.action == "create" else "更新" if m.action == "update" else "删除",
                "before_version": m.before_version,
                "after_version": m.after_version,
                "change_description": m.change_description,
            }
            for m in plan.affected_modules
        ]

        # TODO: 加载生命周期日志
        lifecycle_logs = []

        # TODO: 加载工作流信息
        workflow = {
            "template_type": plan.template_type_value,
            "work_items": [],
            "progress": 0,
        }

        return PlanDetailResponse(
            **base_response.dict(),
            related_applications=related_applications,
            related_modules=related_modules,
            lifecycle_logs=lifecycle_logs,
            workflow=workflow,
        )
    
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
        
        # 取消与应用系统的关联（双向关联清理）
        if plan.inventory_ids and self._inventory_service:
            for app_id in plan.inventory_ids:
                try:
                    self._inventory_service.unlink_from_plan("application", app_id, plan.id)
                except Exception as e:
                    # 记录错误但不影响主流程
                    print(f"Failed to unlink app {app_id} from plan {plan.id}: {e}")
        
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
        """完成计划 - 触发台账更新和生命周期日志生成"""
        plan = self._repository.find_by_id(plan_id)
        if not plan:
            raise ValueError(f"Plan not found: {plan_id}")
        
        # 完成计划（会触发 PlanCompletedEvent）
        plan.complete(completed_by)
        
        # 执行台账操作和生成生命周期日志
        if self._completion_service:
            result = self._completion_service.complete_plan(plan, completed_by)
            if not result.success:
                raise ValueError(f"Failed to complete plan: {result.error_message}")
        
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
        
        # 同步更新应用系统的 related_plan_ids（双向关联）
        if self._inventory_service:
            for app_id in inventory_ids:
                try:
                    self._inventory_service.link_to_plan("application", app_id, saved_plan.id)
                except Exception as e:
                    # 记录错误但不影响主流程
                    print(f"Failed to link app {app_id} to plan {saved_plan.id}: {e}")
        
        return self._to_response(saved_plan)
    
    def preview_changes(
        self,
        request: PlanPreviewRequest
    ) -> PlanPreviewResponse:
        """预览计划变更（用于Step 4）"""
        category = Category(request.category)
        
        # 使用 PlanCompletionService 生成预览
        if self._completion_service:
            # 创建临时 Plan 对象用于预览
            temp_plan = Plan(
                id="preview",
                data_tag="preview",
                name=request.name,
                category=category,
                priority=Priority.from_string("P1"),
                description="",
                inventory_ids=request.related_inventory_ids,
                affected_modules=[
                    AffectedModule(
                        module_id=m.module_id,
                        module_name=m.module_name,
                        action=m.action,
                        before_version=m.before_version,
                        after_version=m.after_version,
                        change_description=m.change_description,
                    )
                    for m in request.affected_modules
                ],
            )
            preview_data = self._completion_service.preview_changes(temp_plan)
            
            # 工作流预览
            workflow_preview = {
                "template_type": category.default_template_type,
                "check_items": self._get_check_items_preview(category.value),
            }
            
            return PlanPreviewResponse(
                plan_name=preview_data["plan_name"],
                category=preview_data["category"],
                category_label=preview_data["category_label"],
                inventory_changes=preview_data["inventory_changes"],
                lifecycle_logs_preview=preview_data["lifecycle_logs_preview"],
                workflow_preview=workflow_preview,
            )
        
        # 降级方案：如果没有 completion_service，使用原有逻辑
        inventory_changes = []
        lifecycle_logs_preview = []
        
        for module in request.affected_modules:
            inventory_changes.append({
                "change_type": "功能模块",
                "change_object": module.module_name,
                "operation": "新增" if module.action == "create" else "更新" if module.action == "update" else "删除",
                "details": {
                    "module_code": "",
                    "owner": "",
                    "version": module.after_version or "v1.0.0",
                }
            })
            
            if module.action == "create":
                lifecycle_logs_preview.append({
                    "log_type": "module_launch",
                    "log_type_label": "功能上线",
                    "event_title": f"【功能上线】{module.module_name} 正式上线",
                })
            elif module.action == "update":
                lifecycle_logs_preview.append({
                    "log_type": "module_update",
                    "log_type_label": "功能变更",
                    "event_title": f"【功能变更】{module.module_name} 更新至 {module.after_version}",
                })
        
        workflow_preview = {
            "template_type": category.default_template_type,
            "check_items": self._get_check_items_preview(category.value),
        }
        
        return PlanPreviewResponse(
            plan_name=request.name,
            category=request.category,
            category_label=category.label,
            inventory_changes=inventory_changes,
            lifecycle_logs_preview=lifecycle_logs_preview,
            workflow_preview=workflow_preview,
        )
    
    def generate_plan_id(self) -> GeneratePlanIdResponse:
        """预生成 PlanID（用于前端展示）"""
        from ..domain.value_objects.plan_id import PlanId
        
        now = datetime.utcnow()
        # 获取当日流水号（实际应该从数据库或Redis获取）
        sequence = self._domain_service.get_next_sequence(now)
        
        plan_id = PlanId.generate(now, sequence)
        
        # 生成临时数据标签（实际创建时会重新生成）
        temp_category = Category("new_feature")
        data_tag = self._domain_service.generate_data_tag(temp_category, now)
        
        return GeneratePlanIdResponse(
            plan_id=plan_id.value,
            data_tag=data_tag,
        )
    
    def _sync_inventory_on_create(
        self,
        plan: Plan,
        request: CreatePlanRequest,
        created_by: str
    ) -> None:
        """
        创建计划时同步台账数据
        
        根据计划分类执行不同的台账操作：
        - new_system: 已在创建应用系统时同步创建功能模块
        - new_feature: 创建功能模块到已有应用系统
        - func_change: 仅记录关联关系，不修改模块
        - arch_change: 仅记录关联关系，不修改模块
        - security_check: 仅记录关联关系
        """
        category = plan.category.value
        
        if category == "new_feature" and plan.affected_modules:
            # 新功能上线：创建功能模块到已有应用系统
            if plan.inventory_ids:
                app_id = plan.inventory_ids[0]
                
                # 准备功能模块数据
                modules = [
                    {
                        "module_code": m.module_id,
                        "module_name": m.module_name,
                        "module_description": m.change_description or "",
                        "owner": created_by,
                        "version": m.after_version or "v1.0.0",
                        "parent_module_id": None,
                    }
                    for m in plan.affected_modules
                ]
                
                # 调用台账服务创建功能模块
                result = self._inventory_service.create_function_modules(
                    app_id=app_id,
                    modules=modules,
                    related_plan_id=plan.id
                )
                
                if result.success:
                    print(f"Successfully created {len(result.module_ids)} function modules for plan {plan.id}")
                else:
                    print(f"Failed to create function modules: {result.error_message}")
        
        # new_system: 功能模块在创建应用系统时已同步创建，无需额外操作
        # func_change/arch_change/security_check: 在计划完成时处理
    
    def _to_response(self, plan: Plan) -> PlanResponse:
        """将领域对象转换为响应DTO"""
        return PlanResponse(
            id=plan.id,
            data_tag=plan.data_tag,
            name=plan.name,
            category=plan.category.value,
            category_label=plan.category.label,
            priority=str(plan.priority),
            priority_label=plan.priority.label,
            status=plan.status.value,
            status_label=plan.status.label,
            description=plan.description,
            planned_start_time=plan.planned_start_time,
            planned_end_time=plan.planned_end_time,
            actual_start_time=plan.actual_start_time,
            actual_end_time=plan.actual_end_time,
            workflow_template_id=plan.workflow_template_id,
            template_type=plan.template_type_value,
            inventory_ids=plan.inventory_ids,
            related_inventory_ids=plan.inventory_ids,
            inventory_action=plan.inventory_action,
            affected_modules=[m.to_dict() for m in plan.affected_modules],
            affected_modules_count=len(plan.affected_modules),
            approval_files=plan.approval_files_detail,
            created_by=plan.created_by,
            created_at=plan.created_at,
            updated_at=plan.updated_at,
            is_overdue=plan.is_overdue
        )
    
    def _get_check_items_preview(self, category: str) -> List[Dict[str, Any]]:
        """获取检查项预览"""
        check_items_map = {
            "new_system": [
                {"name": "基础资源核验", "required": True},
                {"name": "台账信息核验", "required": True},
                {"name": "安全配置核验", "required": True},
                {"name": "监控配置核验", "required": True},
            ],
            "new_feature": [
                {"name": "功能模块台账核验", "required": True},
                {"name": "接口文档核验", "required": True},
                {"name": "监控配置核验", "required": True},
            ],
            "func_change": [
                {"name": "变更影响评估", "required": True},
                {"name": "回归测试", "required": True},
            ],
            "arch_change": [
                {"name": "架构评审", "required": True},
                {"name": "性能测试", "required": True},
                {"name": "安全评审", "required": True},
            ],
            "security_check": [
                {"name": "漏洞扫描", "required": True},
                {"name": "基线检查", "required": True},
                {"name": "渗透测试", "required": False},
            ],
        }
        return check_items_map.get(category, [])
