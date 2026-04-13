"""
台账管理服务
应用层服务，协调领域层和基础设施层
"""
from datetime import datetime
from typing import Optional, List, Dict, Any

from ..domain.repositories.inventory_repository import (
    InventoryRepository,
    ApplicationRepository,
    CloudResourceRepository,
    AccountRepository,
)
from ..domain.entities.application import Application
from ..domain.entities.cloud_resource import CloudResource
from ..domain.entities.account import Account
from ..domain.value_objects.inventory_status import InventoryStatus
from ..domain.value_objects.resource_type import ResourceType
from ..domain.value_objects.account_type import AccountType
from ..domain.value_objects.permission_level import PermissionLevel

from .dtos.inventory_dtos import (
    CreateApplicationDTO,
    UpdateApplicationDTO,
    ApplicationResponseDTO,
    CreateCloudResourceDTO,
    UpdateCloudResourceDTO,
    CloudResourceResponseDTO,
    CreateAccountDTO,
    UpdateAccountDTO,
    AccountResponseDTO,
    InventorySummaryDTO,
    PaginationDTO,
)


class InventoryService:
    """台账管理服务"""
    
    def __init__(self, inventory_repo: InventoryRepository):
        self._repo = inventory_repo
    
    # ==================== 应用系统服务 ====================
    
    def create_application(
        self,
        dto: CreateApplicationDTO,
        created_by: str
    ) -> ApplicationResponseDTO:
        """创建应用系统"""
        # 检查名称唯一性
        
        if self._repo.exists_by_name(dto.app_name):
            raise ValueError(f"Application name '{dto.app_name}' already exists")
        
        # 解析时间
        launch_time = None
        if dto.launch_time:
            launch_time = datetime.fromisoformat(dto.launch_time.replace('Z', '+00:00'))
        
        # 创建功能模块
        function_modules = []
        if dto.function_modules:
            for m in dto.function_modules:
                if isinstance(m, str):
                    function_modules.append({"module_name": m, "launch_time": None})
                else:
                    function_modules.append({"module_name": m.module_name, "launch_time": m.launch_time})
        
        # 创建实体
        application = Application.create(
            app_name=dto.app_name,
            business_owner=dto.business_owner,
            project_owner=dto.project_owner,
            created_by=created_by,
            app_description=dto.app_description,
            hostname=dto.hostname,
            app_url=dto.app_url,
            function_modules=function_modules,
            launch_time=launch_time,
        )
        
        # 保存
        saved = self._repo.save(application)
        
        return self._to_application_dto(saved)
    
    def update_application(
        self,
        app_id: str,
        dto: UpdateApplicationDTO,
        updated_by: str
    ) -> ApplicationResponseDTO:
        """更新应用系统"""
        
        application = self._repo.get_by_id(app_id)
        if not application:
            raise ValueError(f"Application with id '{app_id}' not found")
        
        # 解析时间
        launch_time = None
        if dto.launch_time:
            launch_time = datetime.fromisoformat(dto.launch_time.replace('Z', '+00:00'))
        
        # 更新
        application.update(
            app_description=dto.app_description,
            hostname=dto.hostname,
            app_url=dto.app_url,
            business_owner=dto.business_owner,
            project_owner=dto.project_owner,
            launch_time=launch_time,
            updated_by=updated_by
        )
        
        saved = self._repo.save(application)
        return self._to_application_dto(saved)
    
    def get_application(self, app_id: str) -> ApplicationResponseDTO:
        """获取应用系统详情"""
        
        application = self._repo.get_by_id(app_id)
        if not application:
            raise ValueError(f"Application with id '{app_id}' not found")
        return self._to_application_dto(application)
    
    def list_applications(
        self,
        status: Optional[str] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> PaginationDTO:
        """获取应用系统列表"""
        
        result = self._repo.list_applications(status=status, keyword=keyword, page=page, size=size)
        
        return PaginationDTO(
            page=result['page'],
            size=result['size'],
            total=result['total'],
            total_pages=result['total_pages'],
            data=[self._to_application_dto(app) for app in result['data']]
        )
    
    def delete_application(self, app_id: str, deleted_by: str) -> bool:
        """删除应用系统"""
        
        application = self._repo.get_by_id(app_id)
        if not application:
            raise ValueError(f"Application with id '{app_id}' not found")
        
        if not application.can_delete():
            raise ValueError("Cannot delete application with related plans or resources")
        
        return self._repo.delete(app_id)
    
    def change_application_status(
        self,
        app_id: str,
        new_status: str,
        changed_by: str
    ) -> ApplicationResponseDTO:
        """变更应用系统状态"""
        
        application = self._repo.get_by_id(app_id)
        if not application:
            raise ValueError(f"Application with id '{app_id}' not found")
        
        status = InventoryStatus(new_status)
        application.change_status(status, changed_by)
        
        saved = self._repo.save(application)
        return self._to_application_dto(saved)
    
    # ==================== 云资源服务 ====================
    
    def create_cloud_resource(
        self,
        dto: CreateCloudResourceDTO,
        created_by: str
    ) -> CloudResourceResponseDTO:
        """创建云资源"""
        
        
        # 检查名称唯一性
        if self._repo.exists_by_name(dto.app_id, dto.resource_name):
            raise ValueError(f"Resource name '{dto.resource_name}' already exists in this application")
        
        # 创建资源类型值对象
        resource_type = ResourceType(dto.resource_type)
        
        # 创建实体
        resource = CloudResource.create(
            app_id=dto.app_id,
            resource_type=resource_type,
            resource_name=dto.resource_name,
            created_by=created_by,
            configuration=dto.configuration or {},
        )
        
        saved = self._repo.save(resource)
        return self._to_cloud_resource_dto(saved)
    
    def update_cloud_resource(
        self,
        resource_id: str,
        dto: UpdateCloudResourceDTO,
        updated_by: str
    ) -> CloudResourceResponseDTO:
        """更新云资源"""
        
        resource = self._repo.get_by_id(resource_id)
        if not resource:
            raise ValueError(f"Cloud resource with id '{resource_id}' not found")
        
        resource.update(
            resource_name=dto.resource_name,
            configuration=dto.configuration,
            updated_by=updated_by
        )
        
        saved = self._repo.save(resource)
        return self._to_cloud_resource_dto(saved)
    
    def get_cloud_resource(self, resource_id: str) -> CloudResourceResponseDTO:
        """获取云资源详情"""
        
        resource = self._repo.get_by_id(resource_id)
        if not resource:
            raise ValueError(f"Cloud resource with id '{resource_id}' not found")
        return self._to_cloud_resource_dto(resource)
    
    def list_cloud_resources(
        self,
        app_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> PaginationDTO:
        """获取云资源列表"""
        
        result = self._repo.list_cloud_resources(
            app_id=app_id,
            resource_type=resource_type,
            keyword=keyword,
            page=page,
            size=size
        )
        
        return PaginationDTO(
            page=result['page'],
            size=result['size'],
            total=result['total'],
            total_pages=result['total_pages'],
            data=[self._to_cloud_resource_dto(r) for r in result['data']]
        )
    
    def delete_cloud_resource(self, resource_id: str, deleted_by: str) -> bool:
        """删除云资源"""
        
        resource = self._repo.get_by_id(resource_id)
        if not resource:
            raise ValueError(f"Cloud resource with id '{resource_id}' not found")
        
        if not resource.can_delete():
            raise ValueError("Cannot delete resource with related plans")
        
        return self._repo.delete(resource_id)
    
    # ==================== 账号服务 ====================
    
    def create_account(
        self,
        dto: CreateAccountDTO,
        created_by: str
    ) -> AccountResponseDTO:
        """创建账号"""
        
        
        # 检查名称唯一性
        if self._repo.exists_by_name(dto.app_id, dto.account_name):
            raise ValueError(f"Account name '{dto.account_name}' already exists in this application")
        
        # 创建值对象
        account_type = AccountType(dto.account_type)
        permission_level = PermissionLevel(dto.permission_level)
        
        # 解析时间
        valid_from = datetime.fromisoformat(dto.valid_from.replace('Z', '+00:00'))
        valid_until = datetime.fromisoformat(dto.valid_until.replace('Z', '+00:00'))
        
        # 创建实体
        account = Account.create(
            app_id=dto.app_id,
            account_type=account_type,
            account_name=dto.account_name,
            permission_level=permission_level,
            holder_name=dto.holder_name,
            valid_from=valid_from,
            valid_until=valid_until,
            created_by=created_by,
            password_change_cycle=dto.password_change_cycle,
        )
        
        saved = self._repo.save(account)
        return self._to_account_dto(saved)
    
    def update_account(
        self,
        account_id: str,
        dto: UpdateAccountDTO,
        updated_by: str
    ) -> AccountResponseDTO:
        """更新账号"""
        
        account = self._repo.get_by_id(account_id)
        if not account:
            raise ValueError(f"Account with id '{account_id}' not found")
        
        # 解析参数
        permission_level = None
        if dto.permission_level:
            permission_level = PermissionLevel(dto.permission_level)
        
        valid_until = None
        if dto.valid_until:
            valid_until = datetime.fromisoformat(dto.valid_until.replace('Z', '+00:00'))
        
        account.update(
            permission_level=permission_level,
            holder_name=dto.holder_name,
            valid_until=valid_until,
            password_change_cycle=dto.password_change_cycle,
            updated_by=updated_by
        )
        
        saved = self._repo.save(account)
        return self._to_account_dto(saved)
    
    def get_account(self, account_id: str) -> AccountResponseDTO:
        """获取账号详情"""
        
        account = self._repo.get_by_id(account_id)
        if not account:
            raise ValueError(f"Account with id '{account_id}' not found")
        return self._to_account_dto(account)
    
    def list_accounts(
        self,
        app_id: Optional[str] = None,
        account_type: Optional[str] = None,
        status: Optional[str] = None,
        permission_level: Optional[str] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> PaginationDTO:
        """获取账号列表"""
        
        result = self._repo.list_accounts(
            app_id=app_id,
            account_type=account_type,
            status=status,
            permission_level=permission_level,
            keyword=keyword,
            page=page,
            size=size
        )
        
        return PaginationDTO(
            page=result['page'],
            size=result['size'],
            total=result['total'],
            total_pages=result['total_pages'],
            data=[self._to_account_dto(a) for a in result['data']]
        )
    
    def extend_account_validity(
        self,
        account_id: str,
        days: int,
        extended_by: str
    ) -> AccountResponseDTO:
        """延长账号有效期"""
        
        account = self._repo.get_by_id(account_id)
        if not account:
            raise ValueError(f"Account with id '{account_id}' not found")
        
        account.extend_validity(days, extended_by)
        saved = self._repo.save(account)
        return self._to_account_dto(saved)
    
    def delete_account(self, account_id: str, deleted_by: str) -> bool:
        """删除账号"""
        
        account = self._repo.get_by_id(account_id)
        if not account:
            raise ValueError(f"Account with id '{account_id}' not found")
        
        if not account.can_delete():
            raise ValueError("Cannot delete account with related plans")
        
        return self._repo.delete(account_id)
    
    def get_expiring_accounts(self, days: int = 30) -> List[AccountResponseDTO]:
        """获取即将过期的账号"""
        
        accounts = self._repo.get_expiring_accounts(days)
        return [self._to_account_dto(a) for a in accounts]
    
    # ==================== 计划关联服务 ====================
    
    def link_plan_to_inventory(
        self,
        inventory_type: str,
        inventory_id: str,
        plan_id: str,
        linked_by: str
    ) -> bool:
        """关联计划到台账"""
        return self._repo.link_plan_to_inventory(
            inventory_type, inventory_id, plan_id, linked_by
        )
    
    def unlink_plan_from_inventory(
        self,
        inventory_type: str,
        inventory_id: str,
        plan_id: str,
        unlinked_by: str
    ) -> bool:
        """解除计划与台账的关联"""
        return self._repo.unlink_plan_from_inventory(
            inventory_type, inventory_id, plan_id, unlinked_by
        )
    
    # ==================== 统计服务 ====================
    
    def get_inventory_summary(self) -> InventorySummaryDTO:
        """获取台账汇总统计"""
        summary = self._repo.get_inventory_summary()
        return InventorySummaryDTO(**summary)
    
    # ==================== DTO转换方法 ====================
    
    def _to_application_dto(self, application: Application) -> ApplicationResponseDTO:
        """转换为应用系统DTO"""
        data = application.to_dict()
        return ApplicationResponseDTO(
            id=data['id'],
            app_name=data['app_name'],
            app_description=data['app_description'],
            system_type=data.get('system_type', 'web'),
            function_modules=data['function_modules'],
            hostname=data['hostname'],
            app_url=data['app_url'],
            business_owner=data['business_owner'],
            project_owner=data['project_owner'],
            launch_time=data['launch_time'],
            status=data['status'],
            related_plan_ids=data['related_plan_ids'],
            created_at=data['created_at'],
            updated_at=data['updated_at'],
            created_by=data['created_by'],
        )
    
    def _to_cloud_resource_dto(self, resource: CloudResource) -> CloudResourceResponseDTO:
        """转换为云资源DTO"""
        data = resource.to_dict()
        return CloudResourceResponseDTO(
            id=data['id'],
            app_id=data['app_id'],
            resource_type=data['resource_type'],
            resource_type_display=data['resource_type_display'],
            resource_name=data['resource_name'],
            configuration=data['configuration'],
            status=data['status'],
            related_plan_ids=data['related_plan_ids'],
            created_at=data['created_at'],
            updated_at=data['updated_at'],
            created_by=data['created_by'],
        )
    
    def _to_account_dto(self, account: Account) -> AccountResponseDTO:
        """转换为账号DTO"""
        data = account.to_dict()
        return AccountResponseDTO(
            id=data['id'],
            app_id=data['app_id'],
            account_type=data['account_type'],
            account_type_display=data['account_type_display'],
            account_name=data['account_name'],
            permission_level=data['permission_level'],
            permission_level_display=data['permission_level_display'],
            holder_name=data['holder_name'],
            valid_from=data['valid_from'],
            valid_until=data['valid_until'],
            password_change_cycle=data['password_change_cycle'],
            last_password_change=data['last_password_change'],
            is_password_expired=data['is_password_expired'],
            days_until_password_expiry=data['days_until_password_expiry'],
            days_until_expiry=data['days_until_expiry'],
            status=data['status'],
            related_plan_ids=data['related_plan_ids'],
            created_at=data['created_at'],
            updated_at=data['updated_at'],
            created_by=data['created_by'],
        )
