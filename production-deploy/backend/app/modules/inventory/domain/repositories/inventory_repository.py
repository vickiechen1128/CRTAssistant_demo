"""
台账管理仓库接口
定义领域层的仓库抽象，遵循依赖倒置原则
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..entities.application import Application
from ..entities.cloud_resource import CloudResource
from ..entities.account import Account


class ApplicationRepository(ABC):
    """应用系统台账仓库接口"""
    
    @abstractmethod
    async def get_by_id(self, app_id: str) -> Optional[Application]:
        """根据ID获取应用系统"""
        pass
    
    @abstractmethod
    async def get_by_name(self, app_name: str) -> Optional[Application]:
        """根据名称获取应用系统"""
        pass
    
    @abstractmethod
    async def list_all(
        self,
        status: Optional[str] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> Dict[str, Any]:
        """获取应用系统列表"""
        pass
    
    @abstractmethod
    async def save(self, application: Application) -> Application:
        """保存应用系统（创建或更新）"""
        pass
    
    @abstractmethod
    async def delete(self, app_id: str) -> bool:
        """删除应用系统"""
        pass
    
    @abstractmethod
    async def exists_by_name(self, app_name: str, exclude_id: Optional[str] = None) -> bool:
        """检查应用名称是否已存在"""
        pass
    
    @abstractmethod
    async def get_related_plans(self, app_id: str) -> List[str]:
        """获取关联的计划ID列表"""
        pass
    
    @abstractmethod
    async def count_by_status(self) -> Dict[str, int]:
        """按状态统计数量"""
        pass


class CloudResourceRepository(ABC):
    """云服务资源仓库接口"""
    
    @abstractmethod
    async def get_by_id(self, resource_id: str) -> Optional[CloudResource]:
        """根据ID获取资源"""
        pass
    
    @abstractmethod
    async def list_by_app(
        self,
        app_id: str,
        resource_type: Optional[str] = None
    ) -> List[CloudResource]:
        """获取应用下的资源列表"""
        pass
    
    @abstractmethod
    async def list_all(
        self,
        app_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> Dict[str, Any]:
        """获取资源列表"""
        pass
    
    @abstractmethod
    async def save(self, resource: CloudResource) -> CloudResource:
        """保存资源（创建或更新）"""
        pass
    
    @abstractmethod
    async def delete(self, resource_id: str) -> bool:
        """删除资源"""
        pass
    
    @abstractmethod
    async def exists_by_name(self, app_id: str, resource_name: str, exclude_id: Optional[str] = None) -> bool:
        """检查资源名称是否已存在（同一应用下）"""
        pass
    
    @abstractmethod
    async def count_by_type(self) -> Dict[str, int]:
        """按类型统计数量"""
        pass


class AccountRepository(ABC):
    """账号台账仓库接口"""
    
    @abstractmethod
    async def get_by_id(self, account_id: str) -> Optional[Account]:
        """根据ID获取账号"""
        pass
    
    @abstractmethod
    async def list_by_app(
        self,
        app_id: str,
        account_type: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Account]:
        """获取应用下的账号列表"""
        pass
    
    @abstractmethod
    async def list_all(
        self,
        app_id: Optional[str] = None,
        account_type: Optional[str] = None,
        status: Optional[str] = None,
        permission_level: Optional[str] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> Dict[str, Any]:
        """获取账号列表"""
        pass
    
    @abstractmethod
    async def save(self, account: Account) -> Account:
        """保存账号（创建或更新）"""
        pass
    
    @abstractmethod
    async def delete(self, account_id: str) -> bool:
        """删除账号"""
        pass
    
    @abstractmethod
    async def exists_by_name(self, app_id: str, account_name: str, exclude_id: Optional[str] = None) -> bool:
        """检查账号名称是否已存在（同一应用下）"""
        pass
    
    @abstractmethod
    async def get_expiring_accounts(self, days: int = 30) -> List[Account]:
        """获取即将过期的账号"""
        pass
    
    @abstractmethod
    async def get_password_expiring_accounts(self, days: int = 7) -> List[Account]:
        """获取密码即将过期的账号"""
        pass


class InventoryRepository(ABC):
    """
    综合台账仓库接口
    提供跨实体的查询和操作
    """
    
    @abstractmethod
    async def get_application_repo(self) -> ApplicationRepository:
        """获取应用系统仓库"""
        pass
    
    @abstractmethod
    async def get_cloud_resource_repo(self) -> CloudResourceRepository:
        """获取云资源仓库"""
        pass
    
    @abstractmethod
    async def get_account_repo(self) -> AccountRepository:
        """获取账号仓库"""
        pass
    
    @abstractmethod
    async def get_inventory_summary(self) -> Dict[str, Any]:
        """获取台账汇总统计"""
        pass
    
    @abstractmethod
    async def link_plan_to_inventory(
        self,
        inventory_type: str,
        inventory_id: str,
        plan_id: str,
        linked_by: str
    ) -> bool:
        """关联计划到台账"""
        pass
    
    @abstractmethod
    async def unlink_plan_from_inventory(
        self,
        inventory_type: str,
        inventory_id: str,
        plan_id: str,
        unlinked_by: str
    ) -> bool:
        """解除计划与台账的关联"""
        pass
    
    @abstractmethod
    async def get_plan_linked_inventories(self, plan_id: str) -> Dict[str, List[Any]]:
        """获取计划关联的所有台账"""
        pass
