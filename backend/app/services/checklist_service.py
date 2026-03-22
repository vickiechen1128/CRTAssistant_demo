"""
检查清单服务
处理检查项的业务逻辑
"""

from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status

from ..models.checklist import ChecklistItem, ChecklistItemStatus
from ..models.user import User
from ..schemas.checklist import ChecklistItemUpdate, ChecklistItemVerify


class ChecklistService:
    """检查清单服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_item(self, item_id: int) -> Optional[ChecklistItem]:
        """获取检查项详情"""
        return self.db.query(ChecklistItem).options(
            joinedload(ChecklistItem.assignee),
            joinedload(ChecklistItem.verifier)
        ).filter(ChecklistItem.id == item_id).first()
    
    def list_items(
        self,
        task_id: int,
        control_dimension: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[ChecklistItem]:
        """获取检查项列表"""
        query = self.db.query(ChecklistItem).options(
            joinedload(ChecklistItem.assignee)
        ).filter(ChecklistItem.task_id == task_id)
        
        if control_dimension:
            query = query.filter(ChecklistItem.control_dimension == control_dimension)
        if status:
            query = query.filter(ChecklistItem.status == status)
        
        return query.order_by(ChecklistItem.sort_order).all()
    
    def update_item(self, item_id: int, item_data: ChecklistItemUpdate) -> ChecklistItem:
        """更新检查项"""
        item = self.get_item(item_id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="检查项不存在"
            )
        
        update_data = item_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(item, key, value)
        
        self.db.commit()
        self.db.refresh(item)
        return item
    
    def verify_item(
        self, 
        item_id: int, 
        verify_data: ChecklistItemVerify, 
        verifier_id: int
    ) -> ChecklistItem:
        """确认检查项（通过或驳回）"""
        item = self.get_item(item_id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="检查项不存在"
            )
        
        # 更新状态
        item.status = verify_data.status
        item.verifier_id = verifier_id
        item.verified_at = datetime.now()
        item.verification_remark = verify_data.remark
        
        self.db.commit()
        self.db.refresh(item)
        return item
    
    def get_summary(self, task_id: int) -> dict:
        """获取检查项汇总统计"""
        total = self.db.query(ChecklistItem).filter(
            ChecklistItem.task_id == task_id
        ).count()
        
        pending = self.db.query(ChecklistItem).filter(
            ChecklistItem.task_id == task_id,
            ChecklistItem.status == ChecklistItemStatus.PENDING
        ).count()
        
        in_progress = self.db.query(ChecklistItem).filter(
            ChecklistItem.task_id == task_id,
            ChecklistItem.status == ChecklistItemStatus.IN_PROGRESS
        ).count()
        
        passed = self.db.query(ChecklistItem).filter(
            ChecklistItem.task_id == task_id,
            ChecklistItem.status == ChecklistItemStatus.PASSED
        ).count()
        
        rejected = self.db.query(ChecklistItem).filter(
            ChecklistItem.task_id == task_id,
            ChecklistItem.status == ChecklistItemStatus.REJECTED
        ).count()
        
        return {
            "total": total,
            "pending": pending,
            "in_progress": in_progress,
            "passed": passed,
            "rejected": rejected
        }
    
    def get_dimension_progress(self, task_id: int) -> dict:
        """获取各管控维度进度"""
        from ..models.checklist import ControlDimension
        
        result = {}
        for dimension in ControlDimension:
            total = self.db.query(ChecklistItem).filter(
                ChecklistItem.task_id == task_id,
                ChecklistItem.control_dimension == dimension
            ).count()
            
            completed = self.db.query(ChecklistItem).filter(
                ChecklistItem.task_id == task_id,
                ChecklistItem.control_dimension == dimension,
                ChecklistItem.status.in_([ChecklistItemStatus.PASSED, ChecklistItemStatus.NA])
            ).count()
            
            result[dimension.value] = {
                "total": total,
                "completed": completed
            }
        
        return result
