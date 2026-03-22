"""
工作流服务层
处理工作流相关的业务逻辑
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from app.models.workflow import (
    Workflow, WorkItem, WorkItemDependency, AcceptanceCriteria,
    WorkflowInstance, WorkItemInstance, AcceptanceCriteriaResult,
    WorkflowStatus, WorkItemStatus, WorkflowInstanceStatus, CriteriaStatus
)
from app.schemas.workflow import (
    WorkflowCreate, WorkflowUpdate, WorkItemCreate, WorkItemUpdate,
    AcceptanceCriteriaCreate, WorkflowInstanceCreate,
    WorkItemExecuteRequest, WorkItemVerifyRequest, AcceptanceCriteriaResultCreate
)


class WorkflowService:
    """工作流服务"""

    def __init__(self, db: Session):
        self.db = db

    # ==================== 工作流模板管理 ====================

    def create_workflow(self, data: WorkflowCreate, user_id: int) -> Workflow:
        """创建工作流模板"""
        # 创建工作流
        workflow = Workflow(
            name=data.name,
            description=data.description,
            created_by=user_id,
            status=WorkflowStatus.ACTIVE
        )
        self.db.add(workflow)
        self.db.flush()  # 获取workflow.id

        # 创建工作项
        work_item_map = {}  # 用于处理依赖关系
        for item_data in data.work_items:
            work_item = WorkItem(
                workflow_id=workflow.id,
                name=item_data.name,
                description=item_data.description,
                work_item_type=item_data.work_item_type,
                display_order=item_data.display_order,
                estimated_duration=item_data.estimated_duration,
                is_required=item_data.is_required
            )
            self.db.add(work_item)
            self.db.flush()
            work_item_map[len(work_item_map)] = work_item.id

            # 创建验收标准
            for criteria_data in item_data.acceptance_criteria:
                criteria = AcceptanceCriteria(
                    work_item_id=work_item.id,
                    content=criteria_data.content,
                    is_required=criteria_data.is_required,
                    criteria_type=criteria_data.criteria_type,
                    auto_check_script=criteria_data.auto_check_script,
                    display_order=criteria_data.display_order
                )
                self.db.add(criteria)

        self.db.commit()
        return workflow

    def get_workflow(self, workflow_id: int) -> Optional[Workflow]:
        """获取工作流详情"""
        return self.db.query(Workflow).options(
            joinedload(Workflow.work_items).joinedload(WorkItem.acceptance_criteria)
        ).filter(Workflow.id == workflow_id).first()

    def list_workflows(
        self,
        page: int = 1,
        per_page: int = 20,
        is_preset: Optional[bool] = None,
        keyword: Optional[str] = None
    ) -> tuple[List[Workflow], int]:
        """获取工作流列表"""
        query = self.db.query(Workflow)

        if is_preset is not None:
            query = query.filter(Workflow.is_preset == is_preset)

        if keyword:
            query = query.filter(Workflow.name.contains(keyword))

        total = query.count()
        workflows = query.order_by(Workflow.created_at.desc()).offset(
            (page - 1) * per_page
        ).limit(per_page).all()

        return workflows, total

    def update_workflow(
        self,
        workflow_id: int,
        data: WorkflowUpdate,
        user_id: int
    ) -> Optional[Workflow]:
        """更新工作流"""
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            return None

        if data.name is not None:
            workflow.name = data.name
        if data.description is not None:
            workflow.description = data.description
        if data.status is not None:
            workflow.status = data.status

        workflow.updated_at = datetime.utcnow()
        self.db.commit()
        return workflow

    def delete_workflow(self, workflow_id: int, user_id: int) -> bool:
        """删除工作流"""
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            return False

        # 检查是否有正在执行的实例
        active_instances = self.db.query(WorkflowInstance).filter(
            WorkflowInstance.workflow_id == workflow_id,
            WorkflowInstance.status == WorkflowInstanceStatus.ACTIVE
        ).count()

        if active_instances > 0:
            raise ValueError("该工作流有正在执行的实例，无法删除")

        self.db.delete(workflow)
        self.db.commit()
        return True

    # ==================== 工作项管理 ====================

    def create_work_item(
        self,
        workflow_id: int,
        data: WorkItemCreate
    ) -> WorkItem:
        """创建工作项"""
        work_item = WorkItem(
            workflow_id=workflow_id,
            name=data.name,
            description=data.description,
            work_item_type=data.work_item_type,
            display_order=data.display_order,
            estimated_duration=data.estimated_duration,
            is_required=data.is_required
        )
        self.db.add(work_item)
        self.db.flush()

        # 创建验收标准
        for criteria_data in data.acceptance_criteria:
            criteria = AcceptanceCriteria(
                work_item_id=work_item.id,
                content=criteria_data.content,
                is_required=criteria_data.is_required,
                criteria_type=criteria_data.criteria_type,
                auto_check_script=criteria_data.auto_check_script,
                display_order=criteria_data.display_order
            )
            self.db.add(criteria)

        # 创建依赖关系
        for depends_on_id in data.depends_on:
            dependency = WorkItemDependency(
                work_item_id=work_item.id,
                depends_on_id=depends_on_id
            )
            self.db.add(dependency)

        self.db.commit()
        return work_item

    def update_work_item(
        self,
        work_item_id: int,
        data: WorkItemUpdate
    ) -> Optional[WorkItem]:
        """更新工作项"""
        work_item = self.db.query(WorkItem).filter(
            WorkItem.id == work_item_id
        ).first()

        if not work_item:
            return None

        if data.name is not None:
            work_item.name = data.name
        if data.description is not None:
            work_item.description = data.description
        if data.work_item_type is not None:
            work_item.work_item_type = data.work_item_type
        if data.display_order is not None:
            work_item.display_order = data.display_order
        if data.estimated_duration is not None:
            work_item.estimated_duration = data.estimated_duration
        if data.is_required is not None:
            work_item.is_required = data.is_required

        work_item.updated_at = datetime.utcnow()
        self.db.commit()
        return work_item

    def delete_work_item(self, work_item_id: int) -> bool:
        """删除工作项"""
        work_item = self.db.query(WorkItem).filter(
            WorkItem.id == work_item_id
        ).first()

        if not work_item:
            return False

        self.db.delete(work_item)
        self.db.commit()
        return True

    # ==================== 工作流实例管理 ====================

    def create_instance(
        self,
        workflow_id: int,
        data: WorkflowInstanceCreate,
        user_id: int
    ) -> WorkflowInstance:
        """创建工作流实例"""
        # 生成实例ID
        instance_id = f"wf_inst_{datetime.now().strftime('%Y%m%d%H%M%S')}_{workflow_id}"

        # 创建工作流实例
        instance = WorkflowInstance(
            id=instance_id,
            workflow_id=workflow_id,
            task_id=data.task_id,
            status=WorkflowInstanceStatus.ACTIVE,
            overall_progress=0,
            created_by=user_id,
            started_at=datetime.utcnow()
        )
        self.db.add(instance)
        self.db.flush()

        # 获取工作流的所有工作项
        work_items = self.db.query(WorkItem).filter(
            WorkItem.workflow_id == workflow_id
        ).all()

        # 创建工作项实例
        for work_item in work_items:
            assignee_id = data.assignees.get(work_item.id)
            work_item_instance = WorkItemInstance(
                instance_id=instance_id,
                work_item_id=work_item.id,
                status=WorkItemStatus.PENDING,
                progress=0,
                assignee_id=assignee_id
            )
            self.db.add(work_item_instance)
            self.db.flush()

            # 创建验收结果记录
            for criteria in work_item.acceptance_criteria:
                result = AcceptanceCriteriaResult(
                    work_item_instance_id=work_item_instance.id,
                    criteria_id=criteria.id,
                    status=CriteriaStatus.PENDING
                )
                self.db.add(result)

        self.db.commit()
        return instance

    def get_instance(self, instance_id: str) -> Optional[WorkflowInstance]:
        """获取工作流实例详情"""
        return self.db.query(WorkflowInstance).options(
            joinedload(WorkflowInstance.work_item_instances).joinedload(
                WorkItemInstance.work_item
            ),
            joinedload(WorkflowInstance.work_item_instances).joinedload(
                WorkItemInstance.criteria_results
            )
        ).filter(WorkflowInstance.id == instance_id).first()

    def list_instances(
        self,
        page: int = 1,
        per_page: int = 20,
        workflow_id: Optional[int] = None,
        task_id: Optional[int] = None,
        status: Optional[WorkflowInstanceStatus] = None
    ) -> tuple[List[WorkflowInstance], int]:
        """获取工作流实例列表"""
        query = self.db.query(WorkflowInstance)

        if workflow_id:
            query = query.filter(WorkflowInstance.workflow_id == workflow_id)
        if task_id:
            query = query.filter(WorkflowInstance.task_id == task_id)
        if status:
            query = query.filter(WorkflowInstance.status == status)

        total = query.count()
        instances = query.order_by(WorkflowInstance.created_at.desc()).offset(
            (page - 1) * per_page
        ).limit(per_page).all()

        return instances, total

    # ==================== 工作项执行和验收 ====================

    def execute_work_item(
        self,
        instance_id: str,
        data: WorkItemExecuteRequest,
        user_id: int
    ) -> Optional[WorkItemInstance]:
        """开始执行工作项"""
        work_item_instance = self.db.query(WorkItemInstance).filter(
            WorkItemInstance.instance_id == instance_id,
            WorkItemInstance.work_item_id == data.work_item_id
        ).first()

        if not work_item_instance:
            return None

        # 检查依赖是否完成
        work_item = self.db.query(WorkItem).filter(
            WorkItem.id == data.work_item_id
        ).first()

        for dependency in work_item.dependencies:
            dep_instance = self.db.query(WorkItemInstance).filter(
                WorkItemInstance.instance_id == instance_id,
                WorkItemInstance.work_item_id == dependency.depends_on_id
            ).first()

            if not dep_instance or dep_instance.status != WorkItemStatus.COMPLETED:
                raise ValueError(f"前置工作项 {dependency.depends_on_id} 尚未完成")

        # 更新状态
        work_item_instance.status = WorkItemStatus.IN_PROGRESS
        work_item_instance.started_at = datetime.utcnow()
        if data.assignee_id:
            work_item_instance.assignee_id = data.assignee_id

        self.db.commit()

        # 更新整体进度
        self._update_overall_progress(instance_id)

        return work_item_instance

    def verify_work_item(
        self,
        instance_id: str,
        data: WorkItemVerifyRequest,
        user_id: int
    ) -> Optional[WorkItemInstance]:
        """验收工作项"""
        work_item_instance = self.db.query(WorkItemInstance).filter(
            WorkItemInstance.instance_id == instance_id,
            WorkItemInstance.work_item_id == data.work_item_id
        ).first()

        if not work_item_instance:
            return None

        # 更新验收结果
        for result_data in data.acceptance_results:
            result = self.db.query(AcceptanceCriteriaResult).filter(
                AcceptanceCriteriaResult.work_item_instance_id == work_item_instance.id,
                AcceptanceCriteriaResult.criteria_id == result_data.criteria_id
            ).first()

            if result:
                result.status = result_data.status
                result.remark = result_data.remark
                result.verified_by = user_id
                result.verified_at = datetime.utcnow()

        # 更新工作项状态
        work_item_instance.status = data.status
        work_item_instance.reviewer_id = user_id

        if data.status == WorkItemStatus.COMPLETED:
            work_item_instance.progress = 100
            work_item_instance.completed_at = datetime.utcnow()
            if work_item_instance.started_at:
                duration = (work_item_instance.completed_at - work_item_instance.started_at).total_seconds() / 60
                work_item_instance.actual_duration = int(duration)
        elif data.status == WorkItemStatus.REJECTED:
            work_item_instance.progress = 0

        self.db.commit()

        # 更新整体进度
        self._update_overall_progress(instance_id)

        # 检查是否全部完成
        self._check_completion(instance_id)

        return work_item_instance

    def update_work_item_progress(
        self,
        instance_id: str,
        work_item_id: int,
        progress: int,
        user_id: int
    ) -> Optional[WorkItemInstance]:
        """更新工作项进度"""
        work_item_instance = self.db.query(WorkItemInstance).filter(
            WorkItemInstance.instance_id == instance_id,
            WorkItemInstance.work_item_id == work_item_id
        ).first()

        if not work_item_instance:
            return None

        work_item_instance.progress = max(0, min(100, progress))
        self.db.commit()

        # 更新整体进度
        self._update_overall_progress(instance_id)

        return work_item_instance

    def _update_overall_progress(self, instance_id: str):
        """更新工作流整体进度"""
        instance = self.db.query(WorkflowInstance).filter(
            WorkflowInstance.id == instance_id
        ).first()

        if not instance:
            return

        # 计算平均进度
        work_items = self.db.query(WorkItemInstance).filter(
            WorkItemInstance.instance_id == instance_id
        ).all()

        if work_items:
            total_progress = sum(item.progress for item in work_items)
            instance.overall_progress = total_progress // len(work_items)

        self.db.commit()

    def _check_completion(self, instance_id: str):
        """检查工作流是否全部完成"""
        instance = self.db.query(WorkflowInstance).filter(
            WorkflowInstance.id == instance_id
        ).first()

        if not instance:
            return

        # 获取所有工作项
        work_items = self.db.query(WorkItemInstance).filter(
            WorkItemInstance.instance_id == instance_id
        ).all()

        # 检查是否全部完成
        all_completed = all(
            item.status == WorkItemStatus.COMPLETED for item in work_items
        )

        if all_completed:
            instance.status = WorkflowInstanceStatus.COMPLETED
            instance.completed_at = datetime.utcnow()
            self.db.commit()

    # ==================== 进度查询 ====================

    def get_progress(self, instance_id: str) -> Dict[str, Any]:
        """获取工作流进度"""
        instance = self.get_instance(instance_id)
        if not instance:
            return None

        # 计算关键路径
        critical_path = self._calculate_critical_path(instance)

        # 找出阻塞项
        blocked_items = self._find_blocked_items(instance)

        # 预估完成时间
        estimated_completion = self._estimate_completion(instance)

        return {
            "workflow_id": instance.workflow_id,
            "overall_progress": instance.overall_progress,
            "status": instance.status,
            "work_items": [
                {
                    "id": wi.work_item_id,
                    "name": wi.work_item.name if wi.work_item else "",
                    "status": wi.status,
                    "progress": wi.progress,
                    "started_at": wi.started_at,
                    "completed_at": wi.completed_at
                }
                for wi in instance.work_item_instances
            ],
            "critical_path": critical_path,
            "blocked_items": blocked_items,
            "estimated_completion": estimated_completion
        }

    def _calculate_critical_path(self, instance: WorkflowInstance) -> List[int]:
        """计算关键路径（简化版）"""
        # 实际实现需要使用图算法
        # 这里返回一个简化版本：按顺序排列的未完成工作项
        pending_items = [
            wi.work_item_id for wi in instance.work_item_instances
            if wi.status != WorkItemStatus.COMPLETED
        ]
        return pending_items[:3]  # 返回前3个

    def _find_blocked_items(self, instance: WorkflowInstance) -> List[int]:
        """找出阻塞的工作项"""
        blocked = []
        for wi in instance.work_item_instances:
            if wi.status == WorkItemStatus.PENDING:
                work_item = self.db.query(WorkItem).filter(
                    WorkItem.id == wi.work_item_id
                ).first()

                if work_item:
                    for dep in work_item.dependencies:
                        dep_instance = self.db.query(WorkItemInstance).filter(
                            WorkItemInstance.instance_id == instance.id,
                            WorkItemInstance.work_item_id == dep.depends_on_id
                        ).first()

                        if not dep_instance or dep_instance.status != WorkItemStatus.COMPLETED:
                            blocked.append(wi.work_item_id)
                            break

        return blocked

    def _estimate_completion(self, instance: WorkflowInstance) -> Optional[datetime]:
        """预估完成时间"""
        # 简化计算：基于剩余工作项的预估时长
        remaining_duration = 0

        for wi in instance.work_item_instances:
            if wi.status != WorkItemStatus.COMPLETED:
                work_item = self.db.query(WorkItem).filter(
                    WorkItem.id == wi.work_item_id
                ).first()

                if work_item and work_item.estimated_duration:
                    remaining_duration += work_item.estimated_duration

        if remaining_duration > 0:
            return datetime.utcnow() + __import__('datetime').timedelta(minutes=remaining_duration)

        return None

    # ==================== 预置模板 ====================

    def create_preset_workflows(self, user_id: int):
        """创建预置工作流模板"""
        # 检查是否已存在预置模板
        existing = self.db.query(Workflow).filter(
            Workflow.is_preset == True
        ).first()

        if existing:
            return

        # 创建标准上线工作流
        from app.models.workflow import WorkItemType

        workflow_data = WorkflowCreate(
            name="标准上线工作流",
            description="适用于一般业务系统上线的标准工作流程",
            work_items=[
                WorkItemCreate(
                    name="基础资源标准化交付",
                    description="服务器、网络、存储资源标准化配置",
                    work_item_type=WorkItemType.RESOURCE_DELIVERY,
                    display_order=1,
                    estimated_duration=480,
                    acceptance_criteria=[
                        AcceptanceCriteriaCreate(
                            content="服务器已按标准配置分区",
                            is_required=True,
                            display_order=1
                        ),
                        AcceptanceCriteriaCreate(
                            content="网络策略已配置完成",
                            is_required=True,
                            display_order=2
                        ),
                        AcceptanceCriteriaCreate(
                            content="存储资源已分配",
                            is_required=True,
                            display_order=3
                        )
                    ],
                    depends_on=[]
                ),
                WorkItemCreate(
                    name="服务对象台账",
                    description="录入应用系统、云服务、系统账户台账信息",
                    work_item_type=WorkItemType.INVENTORY,
                    display_order=2,
                    estimated_duration=240,
                    acceptance_criteria=[
                        AcceptanceCriteriaCreate(
                            content="应用系统台账已填写完整",
                            is_required=True,
                            display_order=1
                        ),
                        AcceptanceCriteriaCreate(
                            content="云服务开通台账已填写完整",
                            is_required=True,
                            display_order=2
                        ),
                        AcceptanceCriteriaCreate(
                            content="系统账户台账已填写完整",
                            is_required=True,
                            display_order=3
                        )
                    ],
                    depends_on=[1]
                ),
                WorkItemCreate(
                    name="生产环境权限移交",
                    description="配置系统账户和权限，完成权限移交",
                    work_item_type=WorkItemType.PERMISSION_HANDOVER,
                    display_order=3,
                    estimated_duration=120,
                    acceptance_criteria=[
                        AcceptanceCriteriaCreate(
                            content="系统账户已创建",
                            is_required=True,
                            display_order=1
                        ),
                        AcceptanceCriteriaCreate(
                            content="权限已按最小化原则配置",
                            is_required=True,
                            display_order=2
                        )
                    ],
                    depends_on=[2]
                ),
                WorkItemCreate(
                    name="安全基线核验",
                    description="执行安全基线检查脚本，确保符合安全要求",
                    work_item_type=WorkItemType.SECURITY_BASELINE,
                    display_order=4,
                    estimated_duration=180,
                    acceptance_criteria=[
                        AcceptanceCriteriaCreate(
                            content="账户安全检查通过",
                            is_required=True,
                            display_order=1
                        ),
                        AcceptanceCriteriaCreate(
                            content="系统配置检查通过",
                            is_required=True,
                            display_order=2
                        ),
                        AcceptanceCriteriaCreate(
                            content="网络安全检查通过",
                            is_required=True,
                            display_order=3
                        )
                    ],
                    depends_on=[1]
                ),
                WorkItemCreate(
                    name="监控告警配置确认",
                    description="配置监控项和告警规则，确保可观测性",
                    work_item_type=WorkItemType.MONITORING,
                    display_order=5,
                    estimated_duration=120,
                    acceptance_criteria=[
                        AcceptanceCriteriaCreate(
                            content="监控项已配置",
                            is_required=True,
                            display_order=1
                        ),
                        AcceptanceCriteriaCreate(
                            content="告警规则已配置",
                            is_required=True,
                            display_order=2
                        ),
                        AcceptanceCriteriaCreate(
                            content="告警通知渠道已测试",
                            is_required=True,
                            display_order=3
                        )
                    ],
                    depends_on=[2, 4]
                )
            ]
        )

        workflow = self.create_workflow(workflow_data, user_id)
        workflow.is_preset = True
        self.db.commit()
