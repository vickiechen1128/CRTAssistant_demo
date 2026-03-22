"""
准入任务服务
处理准入任务的业务逻辑
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status

from ..models.admission_task import AdmissionTask, TaskStatus
from ..models.checklist import ChecklistTemplate, ChecklistItem, ChecklistItemStatus
from ..models.user import User
from ..schemas.admission_task import AdmissionTaskCreate, AdmissionTaskUpdate


class TaskService:
    """准入任务服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def generate_task_no(self) -> str:
        """生成任务编号 ADM + 年月日 + 4位序号"""
        today = datetime.now().strftime("%Y%m%d")
        # 查询当天最大的序号
        prefix = f"ADM{today}"
        last_task = self.db.query(AdmissionTask).filter(
            AdmissionTask.task_no.like(f"{prefix}%")
        ).order_by(AdmissionTask.task_no.desc()).first()
        
        if last_task:
            # 提取序号并加1
            last_no = int(last_task.task_no[-4:])
            new_no = last_no + 1
        else:
            new_no = 1
        
        return f"{prefix}{new_no:04d}"
    
    def create_task(self, task_data: AdmissionTaskCreate, creator_id: int) -> AdmissionTask:
        """创建准入任务"""
        # 生成任务编号
        task_no = self.generate_task_no()
        
        # 创建任务
        task = AdmissionTask(
            task_no=task_no,
            system_name=task_data.system_name,
            system_code=task_data.system_code,
            version=task_data.version,
            release_date=task_data.release_date,
            creator_id=creator_id,
            manager_id=task_data.manager_id,
            template_id=task_data.template_id,
            remark=task_data.remark,
            status=TaskStatus.DRAFT,
            progress=0
        )
        
        self.db.add(task)
        self.db.flush()  # 获取task.id
        
        # 如果选择了模板，基于模板创建检查项
        if task_data.template_id:
            self._create_checklist_from_template(task.id, task_data.template_id)
        
        self.db.commit()
        self.db.refresh(task)
        return task
    
    def _create_checklist_from_template(self, task_id: int, template_id: int):
        """基于模板创建检查项"""
        template = self.db.query(ChecklistTemplate).filter(
            ChecklistTemplate.id == template_id
        ).first()
        
        if not template:
            return
        
        # 复制模板项到任务检查项
        for template_item in template.items:
            checklist_item = ChecklistItem(
                task_id=task_id,
                template_item_id=template_item.id,
                control_dimension=template_item.control_dimension,
                category=template_item.category,
                item_name=template_item.item_name,
                description=template_item.description,
                acceptance_criteria=template_item.acceptance_criteria,
                status=ChecklistItemStatus.PENDING,
                sort_order=template_item.sort_order
            )
            self.db.add(checklist_item)
    
    def get_task(self, task_id: int) -> Optional[AdmissionTask]:
        """获取任务详情"""
        return self.db.query(AdmissionTask).options(
            joinedload(AdmissionTask.creator),
            joinedload(AdmissionTask.manager)
        ).filter(AdmissionTask.id == task_id).first()
    
    def list_tasks(
        self, 
        skip: int = 0, 
        limit: int = 20,
        status: Optional[str] = None,
        system_name: Optional[str] = None
    ) -> tuple[List[AdmissionTask], int]:
        """获取任务列表"""
        query = self.db.query(AdmissionTask).options(
            joinedload(AdmissionTask.creator),
            joinedload(AdmissionTask.manager)
        )
        
        # 筛选条件
        if status:
            query = query.filter(AdmissionTask.status == status)
        if system_name:
            query = query.filter(AdmissionTask.system_name.contains(system_name))
        
        # 总数
        total = query.count()
        
        # 分页
        tasks = query.order_by(AdmissionTask.created_at.desc()).offset(skip).limit(limit).all()
        
        return tasks, total
    
    def update_task(self, task_id: int, task_data: AdmissionTaskUpdate) -> AdmissionTask:
        """更新任务"""
        task = self.get_task(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="任务不存在"
            )
        
        # 只允许更新草稿状态的任务基本信息
        update_data = task_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(task, key, value)
        
        self.db.commit()
        self.db.refresh(task)
        return task
    
    def update_progress(self, task_id: int):
        """更新任务进度（根据检查项完成情况）"""
        task = self.get_task(task_id)
        if not task:
            return
        
        # 统计检查项完成情况
        total = self.db.query(ChecklistItem).filter(
            ChecklistItem.task_id == task_id
        ).count()
        
        if total == 0:
            task.progress = 0
        else:
            completed = self.db.query(ChecklistItem).filter(
                ChecklistItem.task_id == task_id,
                ChecklistItem.status.in_([ChecklistItemStatus.PASSED, ChecklistItemStatus.NA])
            ).count()
            task.progress = int(completed / total * 100)
        
        self.db.commit()
    
    def start_task(self, task_id: int) -> AdmissionTask:
        """启动任务（从草稿变为进行中）"""
        task = self.get_task(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="任务不存在"
            )
        
        if task.status != TaskStatus.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只有草稿状态的任务可以启动"
            )
        
        task.status = TaskStatus.IN_PROGRESS
        self.db.commit()
        self.db.refresh(task)
        return task
