"""
台账路由
处理台账数据的CRUD
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.user import User
from ..routers.auth import get_current_user
from ..services.inventory_service import InventoryService
from ..schemas.inventory import InventoryCreate

router = APIRouter(prefix="/api/inventories", tags=["台账"])


from typing import Optional

@router.get("", response_model=dict)
def list_inventories(
    task_id: Optional[int] = None,
    inventory_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取台账列表
    - 可按任务ID查询
    - 可按台账类型查询
    """
    service = InventoryService(db)
    
    if task_id:
        # 按任务查询
        inventories = service.get_task_inventories(task_id)
    elif inventory_type:
        # 按类型查询
        inventories = service.get_inventories_by_type(inventory_type)
    else:
        # 查询所有
        inventories = service.get_all_inventories()
    
    data = []
    for inv in inventories:
        item = {
            "id": inv.id,
            "task_id": inv.task_id,
            "inventory_type": inv.inventory_type.value,
            "status": inv.status.value,
            "created_at": inv.created_at.isoformat() if inv.created_at else None,
            "submitter": {"id": inv.submitter.id, "real_name": inv.submitter.real_name} if inv.submitter else None,
            "task": {"task_no": inv.task.task_no, "system_name": inv.task.system_name} if inv.task else None,
        }
        
        # 添加数量统计
        if inv.inventory_type.value == "server":
            item["server_count"] = len(inv.servers)
        elif inv.inventory_type.value == "cloud_resource":
            item["resource_count"] = len(inv.cloud_resources)
        elif inv.inventory_type.value == "account":
            item["account_count"] = len(inv.accounts)
            
        data.append(item)
    
    return {
        "code": 0,
        "data": {"items": data, "total": len(data)}
    }


@router.get("/{inventory_id}", response_model=dict)
def get_inventory(
    inventory_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取台账详情"""
    service = InventoryService(db)
    inv = service.get_inventory(inventory_id)
    
    if not inv:
        return {"code": 4040, "message": "台账不存在"}
    
    # 构建响应
    result = {
        "id": inv.id,
        "task_id": inv.task_id,
        "inventory_type": inv.inventory_type.value,
        "status": inv.status.value,
        "submitter": {"id": inv.submitter.id, "real_name": inv.submitter.real_name} if inv.submitter else None,
        "submitted_at": inv.submitted_at.isoformat() if inv.submitted_at else None,
        "confirmer": {"id": inv.confirmer.id, "real_name": inv.confirmer.real_name} if inv.confirmer else None,
        "confirmed_at": inv.confirmed_at.isoformat() if inv.confirmed_at else None,
        "created_at": inv.created_at.isoformat() if inv.created_at else None,
        "updated_at": inv.updated_at.isoformat() if inv.updated_at else None
    }
    
    # 根据类型添加明细
    if inv.inventory_type.value == "server":
        result["servers"] = [
            {
                "id": s.id,
                "ip_address": s.ip_address,
                "hostname": s.hostname,
                "os_type": s.os_type,
                "cpu_cores": s.cpu_cores,
                "memory_gb": s.memory_gb,
                "purpose": s.purpose,
                "responsible_person": s.responsible_person
            }
            for s in inv.servers
        ]
    elif inv.inventory_type.value == "cloud_resource":
        result["cloud_resources"] = [
            {
                "id": r.id,
                "resource_type": r.resource_type,
                "service_name": r.service_name,
                "instance_name": r.instance_name,
                "specification": r.specification
            }
            for r in inv.cloud_resources
        ]
    elif inv.inventory_type.value == "account":
        result["accounts"] = [
            {
                "id": a.id,
                "system_name": a.system_name,
                "server_hostname": a.server_hostname,
                "account_name": a.account_name,
                "permission_level": a.permission_level,
                "holder_name": a.holder_name,
                "valid_until": a.valid_until.isoformat() if a.valid_until else None
            }
            for a in inv.accounts
        ]
    
    return {"code": 0, "data": result}


@router.post("", response_model=dict)
def create_inventory(
    task_id: int,
    data: InventoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建台账"""
    service = InventoryService(db)
    inv = service.create_inventory(task_id, data)
    
    return {
        "code": 0,
        "data": {
            "id": inv.id,
            "task_id": inv.task_id,
            "inventory_type": inv.inventory_type.value,
            "status": inv.status.value
        },
        "message": "台账创建成功"
    }


@router.post("/{inventory_id}/submit", response_model=dict)
def submit_inventory(
    inventory_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """提交台账审核"""
    service = InventoryService(db)
    try:
        inv = service.submit_inventory(inventory_id, current_user.id)
        return {
            "code": 0,
            "data": {
                "id": inv.id,
                "status": inv.status.value,
                "submitted_at": inv.submitted_at.isoformat() if inv.submitted_at else None
            },
            "message": "提交成功"
        }
    except Exception as e:
        return {"code": 4000, "message": str(e)}


@router.post("/{inventory_id}/confirm", response_model=dict)
def confirm_inventory(
    inventory_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """确认台账"""
    service = InventoryService(db)
    try:
        inv = service.confirm_inventory(inventory_id, current_user.id)
        return {
            "code": 0,
            "data": {
                "id": inv.id,
                "status": inv.status.value,
                "confirmed_at": inv.confirmed_at.isoformat() if inv.confirmed_at else None
            },
            "message": "确认成功"
        }
    except Exception as e:
        return {"code": 4000, "message": str(e)}
