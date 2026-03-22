"""
台账服务
处理台账数据的业务逻辑
"""

from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status

from ..models.inventory import (
    Inventory, InventoryType, InventoryStatus,
    InventoryServer, InventoryCloudResource, InventoryAccount
)
from ..schemas.inventory import InventoryCreate


class InventoryService:
    """台账服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_inventory(self, inventory_id: int) -> Optional[Inventory]:
        """获取台账详情"""
        return self.db.query(Inventory).options(
            joinedload(Inventory.servers),
            joinedload(Inventory.cloud_resources),
            joinedload(Inventory.accounts),
            joinedload(Inventory.submitter),
            joinedload(Inventory.confirmer)
        ).filter(Inventory.id == inventory_id).first()
    
    def get_task_inventories(self, task_id: int) -> List[Inventory]:
        """获取任务的所有台账"""
        return self.db.query(Inventory).options(
            joinedload(Inventory.submitter),
            joinedload(Inventory.task)
        ).filter(
            Inventory.task_id == task_id
        ).all()
    
    def get_inventories_by_type(self, inventory_type: str) -> List[Inventory]:
        """按类型获取台账列表"""
        return self.db.query(Inventory).options(
            joinedload(Inventory.servers),
            joinedload(Inventory.cloud_resources),
            joinedload(Inventory.accounts),
            joinedload(Inventory.submitter),
            joinedload(Inventory.task)
        ).filter(
            Inventory.inventory_type == inventory_type
        ).all()
    
    def get_all_inventories(self) -> List[Inventory]:
        """获取所有台账"""
        return self.db.query(Inventory).options(
            joinedload(Inventory.servers),
            joinedload(Inventory.cloud_resources),
            joinedload(Inventory.accounts),
            joinedload(Inventory.submitter),
            joinedload(Inventory.task)
        ).all()
    
    def create_inventory(self, task_id: int, data: InventoryCreate) -> Inventory:
        """创建台账"""
        # 创建台账主表
        inventory = Inventory(
            task_id=task_id,
            inventory_type=data.inventory_type,
            status=InventoryStatus.DRAFT
        )
        self.db.add(inventory)
        self.db.flush()
        
        # 根据类型创建明细
        if data.inventory_type == InventoryType.SERVER and data.servers:
            for server_data in data.servers:
                server = InventoryServer(
                    inventory_id=inventory.id,
                    **server_data.model_dump()
                )
                self.db.add(server)
        
        elif data.inventory_type == InventoryType.CLOUD_RESOURCE and data.cloud_resources:
            for resource_data in data.cloud_resources:
                resource = InventoryCloudResource(
                    inventory_id=inventory.id,
                    **resource_data.model_dump()
                )
                self.db.add(resource)
        
        elif data.inventory_type == InventoryType.ACCOUNT and data.accounts:
            for account_data in data.accounts:
                account = InventoryAccount(
                    inventory_id=inventory.id,
                    **account_data.model_dump()
                )
                self.db.add(account)
        
        self.db.commit()
        self.db.refresh(inventory)
        return inventory
    
    def submit_inventory(self, inventory_id: int, submitter_id: int) -> Inventory:
        """提交台账审核"""
        inventory = self.get_inventory(inventory_id)
        if not inventory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="台账不存在"
            )
        
        inventory.status = InventoryStatus.SUBMITTED
        inventory.submitted_by = submitter_id
        inventory.submitted_at = datetime.now()
        
        self.db.commit()
        self.db.refresh(inventory)
        return inventory
    
    def confirm_inventory(self, inventory_id: int, confirmer_id: int) -> Inventory:
        """确认台账"""
        inventory = self.get_inventory(inventory_id)
        if not inventory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="台账不存在"
            )
        
        inventory.status = InventoryStatus.CONFIRMED
        inventory.confirmed_by = confirmer_id
        inventory.confirmed_at = datetime.now()
        
        self.db.commit()
        self.db.refresh(inventory)
        return inventory
