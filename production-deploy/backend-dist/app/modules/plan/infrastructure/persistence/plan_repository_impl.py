"""
计划仓储实现
使用 SQLAlchemy 实现领域仓储接口
"""
from datetime import datetime
from typing import List, Optional, Tuple, Dict, Any
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from ...domain.entities.plan import Plan
from ...domain.value_objects.plan_status import PlanStatus
from ...domain.value_objects.category import Category
from ...domain.value_objects.priority import Priority
from ...domain.value_objects.affected_module import AffectedModule
from ...domain.repositories.plan_repository import PlanRepository
from .models.plan_model import PlanModel, PlanInventoryLinkModel


class PlanRepositoryImpl(PlanRepository):
    """
    计划仓储 SQLAlchemy 实现
    
    职责：
    1. 领域对象与数据库模型的转换
    2. 数据库操作的具体实现
    """
    
    def __init__(self, db_session: Session):
        self._session = db_session
    
    def save(self, plan: Plan) -> Plan:
        """保存计划"""
        # 查找现有记录
        db_plan = self._session.query(PlanModel).filter_by(id=plan.id).first()
        
        if db_plan:
            # 更新
            self._update_model(db_plan, plan)
        else:
            # 创建
            db_plan = self._to_model(plan)
            self._session.add(db_plan)
        
        self._session.commit()
        self._session.refresh(db_plan)
        
        return self._to_entity(db_plan)
    
    def find_by_id(self, plan_id: str) -> Optional[Plan]:
        """根据ID查找"""
        db_plan = self._session.query(PlanModel).filter_by(id=plan_id).first()
        return self._to_entity(db_plan) if db_plan else None
    
    def find_by_data_tag(self, data_tag: str) -> Optional[Plan]:
        """根据数据标签查找"""
        db_plan = self._session.query(PlanModel).filter_by(data_tag=data_tag).first()
        return self._to_entity(db_plan) if db_plan else None
    
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
    ) -> Tuple[List[Plan], int]:
        """查询计划列表"""
        query = self._session.query(PlanModel)
        
        # 应用筛选条件
        if status:
            query = query.filter(PlanModel.status == status.value)
        
        if category:
            query = query.filter(PlanModel.category == category.value)
        
        if priority:
            query = query.filter(PlanModel.priority == priority.level)
        
        if created_by:
            query = query.filter(PlanModel.created_by == created_by)
        
        if keyword:
            query = query.filter(
                or_(
                    PlanModel.name.ilike(f"%{keyword}%"),
                    PlanModel.description.ilike(f"%{keyword}%"),
                    PlanModel.data_tag.ilike(f"%{keyword}%"),
                    PlanModel.id.ilike(f"%{keyword}%")
                )
            )
        
        if start_date:
            query = query.filter(PlanModel.created_at >= start_date)
        
        if end_date:
            query = query.filter(PlanModel.created_at <= end_date)
        
        # 获取总数
        total = query.count()
        
        # 分页
        db_plans = query.order_by(PlanModel.created_at.desc()).offset(skip).limit(limit).all()
        
        plans = [self._to_entity(p) for p in db_plans]
        return plans, total
    
    def delete(self, plan_id: str) -> bool:
        """删除计划"""
        db_plan = self._session.query(PlanModel).filter_by(id=plan_id).first()
        if not db_plan:
            return False
        
        self._session.delete(db_plan)
        self._session.commit()
        return True
    
    def exists(self, plan_id: str) -> bool:
        """检查是否存在"""
        return self._session.query(PlanModel).filter_by(id=plan_id).first() is not None
    
    def get_next_sequence(self, date: datetime) -> int:
        """获取下一个序号（用于生成PlanID）"""
        date_prefix = f"PLAN-{date.strftime('%Y%m%d')}"
        
        # 查找当天最大的序号
        result = self._session.query(PlanModel).filter(
            PlanModel.id.like(f"{date_prefix}%")
        ).order_by(PlanModel.id.desc()).first()
        
        if not result:
            return 1
        
        # 提取序号
        try:
            sequence = int(result.id.split("-")[-1])
            return sequence + 1
        except (ValueError, IndexError):
            return 1
    
    def _to_model(self, plan: Plan) -> PlanModel:
        """领域对象转数据库模型"""
        return PlanModel(
            id=plan.id,
            data_tag=plan.data_tag,
            name=plan.name,
            category=plan.category.value,
            priority=plan.priority.level,
            description=plan.description,
            planned_start_time=plan.planned_start_time,
            planned_end_time=plan.planned_end_time,
            actual_start_time=plan.actual_start_time,
            actual_end_time=plan.actual_end_time,
            status=plan.status.value,
            workflow_template_id=plan.workflow_template_id,
            inventory_action=plan.inventory_action,
            related_inventory_ids=plan.inventory_ids,
            affected_modules=[m.to_dict() for m in plan.affected_modules],
            template_type=plan.template_type or plan.category.default_template_type,
            approval_files_detail=plan.approval_files_detail,
            approval_files=[str(fid) for fid in plan.approval_files],
            created_by=plan.created_by,
            created_at=plan.created_at,
            updated_at=plan.updated_at
        )
    
    def _update_model(self, db_plan: PlanModel, plan: Plan) -> None:
        """更新数据库模型"""
        db_plan.name = plan.name
        db_plan.priority = plan.priority.level
        db_plan.description = plan.description
        db_plan.planned_start_time = plan.planned_start_time
        db_plan.planned_end_time = plan.planned_end_time
        db_plan.actual_start_time = plan.actual_start_time
        db_plan.actual_end_time = plan.actual_end_time
        db_plan.status = plan.status.value
        db_plan.workflow_template_id = plan.workflow_template_id
        db_plan.inventory_action = plan.inventory_action
        db_plan.related_inventory_ids = plan.inventory_ids
        db_plan.affected_modules = [m.to_dict() for m in plan.affected_modules]
        db_plan.template_type = plan.template_type or db_plan.template_type
        db_plan.approval_files_detail = plan.approval_files_detail
        db_plan.approval_files = [str(fid) for fid in plan.approval_files]
        db_plan.updated_at = plan.updated_at
    
    def _to_entity(self, db_plan: PlanModel) -> Plan:
        """数据库模型转领域对象"""
        # 获取台账ID列表（优先使用JSON字段，否则从关联表获取）
        inventory_ids = db_plan.related_inventory_ids or []
        if not inventory_ids and db_plan.inventory_links:
            inventory_ids = [link.inventory_id for link in db_plan.inventory_links]
        
        # 转换受影响功能模块
        affected_modules = []
        if db_plan.affected_modules:
            for m_data in db_plan.affected_modules:
                try:
                    affected_modules.append(AffectedModule.from_dict(m_data))
                except (ValueError, KeyError):
                    continue
        
        # 转换文件ID（兼容性处理）
        approval_files = []
        if db_plan.approval_files:
            for fid in db_plan.approval_files:
                try:
                    approval_files.append(UUID(fid))
                except ValueError:
                    pass
        
        return Plan(
            id=db_plan.id,
            data_tag=db_plan.data_tag,
            name=db_plan.name,
            category=Category(db_plan.category),
            priority=Priority(db_plan.priority),
            description=db_plan.description,
            planned_start_time=db_plan.planned_start_time,
            planned_end_time=db_plan.planned_end_time,
            actual_start_time=db_plan.actual_start_time,
            actual_end_time=db_plan.actual_end_time,
            status=PlanStatus(db_plan.status),
            workflow_template_id=db_plan.workflow_template_id,
            inventory_ids=inventory_ids,
            inventory_action=db_plan.inventory_action,
            affected_modules=affected_modules,
            template_type=db_plan.template_type,
            approval_files_detail=db_plan.approval_files_detail or [],
            approval_files=approval_files,
            created_by=db_plan.created_by,
            created_at=db_plan.created_at,
            updated_at=db_plan.updated_at
        )
