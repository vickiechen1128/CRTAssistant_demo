"""
验证服务
处理验证脚本的执行和结果管理
"""

import json
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status

from ..models.verification import (
    VerificationScript, VerificationRecord, 
    ScriptType, ExecutionStatus
)
from ..schemas.verification import VerificationExecuteRequest


class VerificationService:
    """验证服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_script(self, script_id: int) -> Optional[VerificationScript]:
        """获取脚本详情"""
        return self.db.query(VerificationScript).filter(
            VerificationScript.id == script_id
        ).first()
    
    def list_scripts(self, skip: int = 0, limit: int = 100) -> list:
        """获取脚本列表"""
        return self.db.query(VerificationScript).filter(
            VerificationScript.status == "active"
        ).offset(skip).limit(limit).all()
    
    def create_script(self, data: dict, creator_id: int) -> VerificationScript:
        """创建验证脚本"""
        script = VerificationScript(
            script_name=data["script_name"],
            script_type=data["script_type"],
            description=data.get("description"),
            content=data["content"],
            version=data.get("version", "1.0"),
            applicable_os=data.get("applicable_os"),
            parameters=data.get("parameters"),
            timeout_seconds=data.get("timeout_seconds", 300),
            created_by=creator_id
        )
        self.db.add(script)
        self.db.commit()
        self.db.refresh(script)
        return script
    
    def execute_script(
        self, 
        data: VerificationExecuteRequest, 
        executor_id: int
    ) -> VerificationRecord:
        """
        执行验证脚本（简化版实现）
        实际项目中应使用Celery异步执行
        """
        # 生成执行ID
        execution_id = f"exec_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        # 创建执行记录
        record = VerificationRecord(
            execution_id=execution_id,
            task_id=data.checklist_item_id,  # 简化处理
            checklist_item_id=data.checklist_item_id,
            script_id=data.script_id,
            executor_id=executor_id,
            target_server=data.target_server,
            status=ExecutionStatus.RUNNING,
            started_at=datetime.now()
        )
        self.db.add(record)
        self.db.commit()
        
        # TODO: 实际应提交到Celery任务队列异步执行
        # 这里返回记录，实际执行在后台进行
        
        return record
    
    def get_execution(self, execution_id: str) -> Optional[VerificationRecord]:
        """获取执行记录"""
        return self.db.query(VerificationRecord).options(
            joinedload(VerificationRecord.executor),
            joinedload(VerificationRecord.script)
        ).filter(VerificationRecord.execution_id == execution_id).first()
    
    def list_executions(
        self, 
        task_id: int, 
        skip: int = 0, 
        limit: int = 20
    ) -> list:
        """获取执行记录列表"""
        return self.db.query(VerificationRecord).options(
            joinedload(VerificationRecord.script),
            joinedload(VerificationRecord.executor)
        ).filter(
            VerificationRecord.task_id == task_id
        ).order_by(
            VerificationRecord.created_at.desc()
        ).offset(skip).limit(limit).all()
    
    def list_all_executions(
        self, 
        skip: int = 0, 
        limit: int = 20
    ) -> list:
        """获取所有执行记录"""
        return self.db.query(VerificationRecord).options(
            joinedload(VerificationRecord.script),
            joinedload(VerificationRecord.executor)
        ).order_by(
            VerificationRecord.created_at.desc()
        ).offset(skip).limit(limit).all()
    
    def update_execution_result(
        self, 
        execution_id: str, 
        result: dict
    ) -> VerificationRecord:
        """更新执行结果（由异步任务调用）"""
        record = self.db.query(VerificationRecord).filter(
            VerificationRecord.execution_id == execution_id
        ).first()
        
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="执行记录不存在"
            )
        
        record.status = result.get("status", ExecutionStatus.FAILED)
        record.completed_at = datetime.now()
        record.duration_seconds = result.get("duration_seconds")
        record.result_summary = result.get("result_summary")
        record.result_detail = result.get("result_detail")
        record.output_log = result.get("output_log")
        record.error_log = result.get("error_log")
        
        self.db.commit()
        self.db.refresh(record)
        return record
