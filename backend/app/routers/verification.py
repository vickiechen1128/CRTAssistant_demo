"""
验证路由
处理验证脚本和执行记录
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.user import User
from ..routers.auth import get_current_user
from ..services.verification_service import VerificationService
from ..schemas.verification import VerificationExecuteRequest

router = APIRouter(prefix="/api/verification", tags=["验证"])


@router.get("/scripts", response_model=dict)
def list_scripts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取验证脚本列表"""
    service = VerificationService(db)
    scripts = service.list_scripts(skip, limit)
    
    data = []
    for script in scripts:
        data.append({
            "id": script.id,
            "script_name": script.script_name,
            "script_type": script.script_type.value,
            "description": script.description,
            "version": script.version,
            "applicable_os": script.applicable_os,
            "timeout_seconds": script.timeout_seconds
        })
    
    return {"code": 0, "data": {"items": data, "total": len(data)}}


@router.get("/scripts/{script_id}", response_model=dict)
def get_script(
    script_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取脚本详情"""
    service = VerificationService(db)
    script = service.get_script(script_id)
    
    if not script:
        return {"code": 4040, "message": "脚本不存在"}
    
    return {
        "code": 0,
        "data": {
            "id": script.id,
            "script_name": script.script_name,
            "script_type": script.script_type.value,
            "description": script.description,
            "content": script.content,
            "version": script.version,
            "applicable_os": script.applicable_os,
            "parameters": script.parameters,
            "timeout_seconds": script.timeout_seconds
        }
    }


@router.post("/execute", response_model=dict)
def execute_verification(
    data: VerificationExecuteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    执行验证脚本
    - 创建执行记录
    - 实际执行应交给Celery异步处理
    """
    service = VerificationService(db)
    record = service.execute_script(data, current_user.id)
    
    return {
        "code": 0,
        "data": {
            "execution_id": record.execution_id,
            "status": record.status.value,
            "message": "脚本已提交执行，请查询结果"
        }
    }


@router.get("/execute/{execution_id}", response_model=dict)
def get_execution_result(
    execution_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取验证执行结果"""
    service = VerificationService(db)
    record = service.get_execution(execution_id)
    
    if not record:
        return {"code": 4040, "message": "执行记录不存在"}
    
    return {
        "code": 0,
        "data": {
            "execution_id": record.execution_id,
            "task_id": record.task_id,
            "target_server": record.target_server,
            "executor": {"id": record.executor.id, "real_name": record.executor.real_name} if record.executor else None,
            "status": record.status.value,
            "started_at": record.started_at.isoformat() if record.started_at else None,
            "completed_at": record.completed_at.isoformat() if record.completed_at else None,
            "duration_seconds": record.duration_seconds,
            "result_summary": record.result_summary,
            "result_detail": record.result_detail,
            "output_log": record.output_log,
            "error_log": record.error_log
        }
    }


@router.get("/records", response_model=dict)
def list_executions(
    task_id: int = Query(None, description="任务ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取执行记录列表"""
    service = VerificationService(db)
    records = service.list_executions(task_id, skip, limit) if task_id else service.list_all_executions(skip, limit)
    
    data = []
    for record in records:
        data.append({
            "execution_id": record.execution_id,
            "script_name": record.script.script_name if record.script else None,
            "target_server": record.target_server,
            "executor": {"id": record.executor.id, "real_name": record.executor.real_name} if record.executor else None,
            "status": record.status.value,
            "started_at": record.started_at.isoformat() if record.started_at else None,
            "duration_seconds": record.duration_seconds,
            "result_summary": record.result_summary
        })
    
    return {"code": 0, "data": {"items": data, "total": len(data)}}
