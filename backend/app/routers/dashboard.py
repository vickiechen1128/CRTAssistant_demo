"""
仪表盘路由
处理统计数据和概览信息
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, case

from ..database import get_db
from ..models.user import User
from ..models.admission_task import AdmissionTask, TaskStatus
from ..models.checklist import ChecklistItem
from ..routers.auth import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["仪表盘"])


@router.get("/overview", response_model=dict)
def get_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取仪表盘概览数据
    - 任务统计
    - 我的待办
    - 各维度进度
    """
    # 任务统计
    task_stats = db.query(
        func.count(AdmissionTask.id).label("total"),
        func.sum(case((AdmissionTask.status == TaskStatus.IN_PROGRESS, 1), else_=0)).label("in_progress"),
        func.sum(case((AdmissionTask.status == TaskStatus.PENDING_REVIEW, 1), else_=0)).label("pending_review"),
        func.sum(case((AdmissionTask.status == TaskStatus.PASSED, 1), else_=0)).label("passed"),
        func.sum(case((AdmissionTask.status == TaskStatus.REJECTED, 1), else_=0)).label("rejected")
    ).first()
    
    # 我的任务统计（分配给当前用户的检查项）
    my_assigned = db.query(ChecklistItem).filter(
        ChecklistItem.assignee_id == current_user.id
    ).count()
    
    my_pending = db.query(ChecklistItem).filter(
        ChecklistItem.assignee_id == current_user.id,
        ChecklistItem.status == "pending"
    ).count()
    
    return {
        "code": 0,
        "data": {
            "task_stats": {
                "total": task_stats.total or 0,
                "in_progress": task_stats.in_progress or 0,
                "pending_review": task_stats.pending_review or 0,
                "passed": task_stats.passed or 0,
                "rejected": task_stats.rejected or 0
            },
            "my_tasks": {
                "assigned": my_assigned,
                "pending": my_pending
            }
        }
    }


@router.get("/tasks", response_model=dict)
def get_task_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取任务统计详情"""
    # 按月统计任务创建趋势
    from sqlalchemy import extract
    
    monthly_stats = db.query(
        extract('year', AdmissionTask.created_at).label('year'),
        extract('month', AdmissionTask.created_at).label('month'),
        func.count(AdmissionTask.id).label('count')
    ).group_by('year', 'month').order_by('year', 'month').all()
    
    trend = [
        {"month": f"{int(s.year)}-{int(s.month):02d}", "count": s.count}
        for s in monthly_stats
    ]
    
    return {
        "code": 0,
        "data": {
            "monthly_trend": trend
        }
    }
