"""
系统及软件账号台账实体
对应数据模型：inventory_accounts
"""
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from uuid import uuid4

from ..value_objects.account_type import AccountType
from ..value_objects.permission_level import PermissionLevel
from ..value_objects.inventory_status import InventoryStatus
from ..events.inventory_events import (
    AccountCreatedEvent,
    AccountUpdatedEvent,
    AccountDeletedEvent,
    AccountExpiredEvent,
    PlanLinkedEvent,
    PlanUnlinkedEvent,
)


@dataclass
class Account:
    """
    系统及软件账号台账实体
    
    核心职责：
    1. 维护账号基本信息
    2. 管理有效期
    3. 监控密码修改周期
    4. 处理计划关联关系
    """
    # 标识
    id: str
    
    # 关联应用
    app_id: str
    
    # 账号信息
    account_type: AccountType
    account_name: str
    permission_level: PermissionLevel
    holder_name: str
    
    # 有效期
    valid_from: datetime
    valid_until: datetime
    
    # 密码管理
    password_change_cycle: int = 90  # 默认90天
    last_password_change: Optional[datetime] = None
    
    # 状态
    status: InventoryStatus = field(default_factory=lambda: InventoryStatus.active())
    
    # 关联计划
    related_plan_ids: List[str] = field(default_factory=list)
    
    # 审计信息
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    created_by: str = ""
    
    # 领域事件
    _domain_events: List[Any] = field(default_factory=list, repr=False)
    
    @classmethod
    def create(
        cls,
        app_id: str,
        account_type: AccountType,
        account_name: str,
        permission_level: PermissionLevel,
        holder_name: str,
        valid_from: datetime,
        valid_until: datetime,
        created_by: str,
        password_change_cycle: int = 90,
    ) -> "Account":
        """工厂方法：创建新账号"""
        account_id = str(uuid4())
        
        # 验证有效期
        if valid_until <= valid_from:
            raise ValueError("valid_until must be later than valid_from")
        
        # 验证有效期跨度不超过10年
        if (valid_until - valid_from).days > 3650:
            raise ValueError("validity period cannot exceed 10 years")
        
        account = cls(
            id=account_id,
            app_id=app_id,
            account_type=account_type,
            account_name=account_name,
            permission_level=permission_level,
            holder_name=holder_name,
            valid_from=valid_from,
            valid_until=valid_until,
            password_change_cycle=password_change_cycle,
            last_password_change=datetime.utcnow(),
            created_by=created_by,
        )
        
        # 发布创建事件
        account._domain_events.append(AccountCreatedEvent(
            account_id=account_id,
            account_name=account_name,
            account_type=account_type.value,
            app_id=app_id,
            holder_name=holder_name,
            created_by=created_by
        ))
        
        return account
    
    def update(
        self,
        permission_level: Optional[PermissionLevel] = None,
        holder_name: Optional[str] = None,
        valid_until: Optional[datetime] = None,
        password_change_cycle: Optional[int] = None,
        updated_by: str = ""
    ) -> None:
        """更新账号信息"""
        if not self.status.is_editable:
            raise ValueError(f"Cannot update account in {self.status.value} status")
        
        updated_fields = []
        
        if permission_level is not None:
            self.permission_level = permission_level
            updated_fields.append("permission_level")
        if holder_name is not None:
            self.holder_name = holder_name
            updated_fields.append("holder_name")
        if valid_until is not None:
            if valid_until <= self.valid_from:
                raise ValueError("valid_until must be later than valid_from")
            if (valid_until - self.valid_from).days > 3650:
                raise ValueError("validity period cannot exceed 10 years")
            self.valid_until = valid_until
            updated_fields.append("valid_until")
        if password_change_cycle is not None:
            self.password_change_cycle = password_change_cycle
            updated_fields.append("password_change_cycle")
        
        if updated_fields:
            self.updated_at = datetime.utcnow()
            self._domain_events.append(AccountUpdatedEvent(
                account_id=self.id,
                updated_fields=updated_fields,
                updated_by=updated_by
            ))
    
    def extend_validity(self, days: int, extended_by: str = "") -> None:
        """延长有效期"""
        new_valid_until = self.valid_until + timedelta(days=days)
        self.update(valid_until=new_valid_until, updated_by=extended_by)
    
    def record_password_change(self) -> None:
        """记录密码修改"""
        self.last_password_change = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def check_and_update_expired_status(self) -> bool:
        """检查并更新过期状态"""
        now = datetime.utcnow()
        
        # 检查有效期
        if now > self.valid_until:
            if self.status.value == "active":
                self.status = InventoryStatus.expired() if hasattr(InventoryStatus, 'expired') else InventoryStatus.inactive()
                self._domain_events.append(AccountExpiredEvent(
                    account_id=self.id,
                    account_name=self.account_name,
                    app_id=self.app_id,
                    expired_at=now
                ))
            return True
        return False
    
    def is_password_expired(self) -> bool:
        """检查密码是否过期"""
        if not self.last_password_change:
            return True
        expiry_date = self.last_password_change + timedelta(days=self.password_change_cycle)
        return datetime.utcnow() > expiry_date
    
    @property
    def days_until_password_expiry(self) -> int:
        """距离密码过期的天数"""
        if not self.last_password_change:
            return 0
        expiry_date = self.last_password_change + timedelta(days=self.password_change_cycle)
        days = (expiry_date - datetime.utcnow()).days
        return max(0, days)
    
    @property
    def days_until_expiry(self) -> int:
        """距离账号过期的天数"""
        days = (self.valid_until - datetime.utcnow()).days
        return max(0, days)
    
    def change_status(self, new_status: InventoryStatus, changed_by: str = "") -> None:
        """变更状态"""
        if self.status == new_status:
            return
        
        self.status = new_status
        self.updated_at = datetime.utcnow()
    
    def link_plan(self, plan_id: str, linked_by: str = "") -> None:
        """关联计划"""
        if not self.status.can_associate_plan:
            raise ValueError(f"Cannot link plan to account in {self.status.value} status")
        
        if plan_id not in self.related_plan_ids:
            self.related_plan_ids.append(plan_id)
            self.updated_at = datetime.utcnow()
            
            self._domain_events.append(PlanLinkedEvent(
                inventory_id=self.id,
                inventory_type="account",
                plan_id=plan_id,
                linked_by=linked_by
            ))
    
    def unlink_plan(self, plan_id: str, unlinked_by: str = "") -> None:
        """解除计划关联"""
        if plan_id in self.related_plan_ids:
            self.related_plan_ids.remove(plan_id)
            self.updated_at = datetime.utcnow()
            
            self._domain_events.append(PlanUnlinkedEvent(
                inventory_id=self.id,
                inventory_type="account",
                plan_id=plan_id,
                unlinked_by=unlinked_by
            ))
    
    def can_delete(self) -> bool:
        """是否可以删除"""
        if self.related_plan_ids:
            return False
        return True
    
    def get_domain_events(self) -> List[Any]:
        """获取领域事件并清空"""
        events = self._domain_events.copy()
        self._domain_events.clear()
        return events
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "app_id": self.app_id,
            "account_type": self.account_type.value,
            "account_type_display": self.account_type.display_name,
            "account_name": self.account_name,
            "permission_level": self.permission_level.value,
            "permission_level_display": self.permission_level.display_name,
            "holder_name": self.holder_name,
            "valid_from": self.valid_from.isoformat() if self.valid_from else None,
            "valid_until": self.valid_until.isoformat() if self.valid_until else None,
            "password_change_cycle": self.password_change_cycle,
            "last_password_change": self.last_password_change.isoformat() if self.last_password_change else None,
            "is_password_expired": self.is_password_expired(),
            "days_until_password_expiry": self.days_until_password_expiry,
            "days_until_expiry": self.days_until_expiry,
            "status": self.status.value,
            "related_plan_ids": self.related_plan_ids,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "created_by": self.created_by,
        }
