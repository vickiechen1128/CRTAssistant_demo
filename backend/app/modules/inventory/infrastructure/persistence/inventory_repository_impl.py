"""
台账管理仓库实现
实现领域层定义的仓库接口，使用SQLAlchemy进行数据持久化
"""
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

from sqlalchemy import func, and_, or_
from sqlalchemy.orm import Session
from sqlalchemy.future import select

from ...domain.repositories.inventory_repository import (
    InventoryRepository,
    ApplicationRepository,
    CloudResourceRepository,
    AccountRepository,
)
from ...domain.entities.application import Application
from ...domain.entities.cloud_resource import CloudResource
from ...domain.entities.account import Account
from ...domain.value_objects.inventory_status import InventoryStatus
from ...domain.value_objects.resource_type import ResourceType
from ...domain.value_objects.account_type import AccountType
from ...domain.value_objects.permission_level import PermissionLevel

from .models.inventory_model import (
    ApplicationModel,
    CloudResourceModel,
    AccountModel,
)
from app.modules.plan.infrastructure.persistence.models.plan_model import PlanInventoryLinkModel


class ApplicationRepositoryImpl:
    """应用系统仓库实现"""

    def __init__(self, session: Session):
        self._session = session

    def _to_entity(self, model: ApplicationModel) -> Application:
        """模型转换为实体"""
        return Application(
            id=model.id,
            app_name=model.app_name,
            app_description=model.app_description,
            function_modules=model.function_modules,
            hostname=model.hostname,
            app_url=model.app_url,
            business_owner=model.business_owner,
            project_owner=model.project_owner,
            launch_time=model.launch_time,
            status=InventoryStatus(model.status),
            related_plan_ids=model.related_plan_ids,
            created_at=model.created_at,
            updated_at=model.updated_at,
            created_by=model.created_by,
        )

    def _to_model(self, entity: Application) -> ApplicationModel:
        """实体转换为模型"""
        return ApplicationModel(
            id=entity.id,
            app_name=entity.app_name,
            app_description=entity.app_description,
            function_modules=[m.to_dict() for m in entity.function_modules],
            hostname=entity.hostname,
            app_url=entity.app_url,
            business_owner=entity.business_owner,
            project_owner=entity.project_owner,
            launch_time=entity.launch_time,
            status=entity.status.value,
            related_plan_ids=entity.related_plan_ids,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            created_by=entity.created_by,
        )

    def get_by_id(self, app_id: str) -> Optional[Application]:
        """根据ID获取应用系统"""
        result = self._session.execute(
            select(ApplicationModel).where(ApplicationModel.id == app_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    def list_all(
        self,
        status: Optional[str] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> Dict[str, Any]:
        """获取应用系统列表（支持分页和筛选）"""
        query = select(ApplicationModel)

        # 筛选条件
        if status:
            query = query.where(ApplicationModel.status == status)
        if keyword:
            query = query.where(
                or_(
                    ApplicationModel.app_name.ilike(f"%{keyword}%"),
                    ApplicationModel.business_owner.ilike(f"%{keyword}%"),
                    ApplicationModel.project_owner.ilike(f"%{keyword}%")
                )
            )

        # 统计总数
        count_result = self._session.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar()

        # 分页
        query = query.order_by(ApplicationModel.created_at.desc())
        query = query.offset((page - 1) * size).limit(size)

        result = self._session.execute(query)
        models = result.scalars().all()

        return {
            'page': page,
            'size': size,
            'total': total,
            'total_pages': (total + size - 1) // size,
            'data': [self._to_entity(m) for m in models]
        }

    def save(self, application: Application) -> Application:
        """保存应用系统"""
        model = self._session.get(ApplicationModel, application.id)

        if model:
            # 更新
            model.app_name = application.app_name
            model.app_description = application.app_description
            model.function_modules = [m.to_dict() for m in application.function_modules]
            model.hostname = application.hostname
            model.app_url = application.app_url
            model.business_owner = application.business_owner
            model.project_owner = application.project_owner
            model.launch_time = application.launch_time
            model.status = application.status.value
            model.related_plan_ids = application.related_plan_ids
            model.updated_at = datetime.utcnow()
        else:
            # 创建
            model = self._to_model(application)
            self._session.add(model)

        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)

    def delete(self, app_id: str) -> bool:
        """删除应用系统"""
        model = self._session.get(ApplicationModel, app_id)
        if model:
            self._session.delete(model)
            self._session.commit()
            return True
        return False

    def exists_by_name(self, app_name: str, exclude_id: Optional[str] = None) -> bool:
        """检查应用名称是否已存在"""
        query = select(ApplicationModel).where(ApplicationModel.app_name == app_name)
        if exclude_id:
            query = query.where(ApplicationModel.id != exclude_id)
        result = self._session.execute(query)
        return result.scalar_one_or_none() is not None

    def get_related_plans(self, app_id: str) -> List[str]:
        """获取关联的计划ID列表"""
        model = self._session.get(ApplicationModel, app_id)
        return model.related_plan_ids if model else []

    def count_by_status(self) -> Dict[str, int]:
        """按状态统计数量"""
        result = self._session.execute(
            select(ApplicationModel.status, func.count())
            .group_by(ApplicationModel.status)
        )
        return {status: count for status, count in result.all()}


class CloudResourceRepositoryImpl:
    """云资源仓库实现"""

    def __init__(self, session: Session):
        self._session = session

    def _to_entity(self, model: CloudResourceModel) -> CloudResource:
        return CloudResource(
            id=model.id,
            app_id=model.app_id,
            resource_type=ResourceType(model.resource_type),
            resource_name=model.resource_name,
            configuration=model.configuration,
            status=InventoryStatus(model.status),
            related_plan_ids=model.related_plan_ids,
            created_at=model.created_at,
            updated_at=model.updated_at,
            created_by=model.created_by,
        )

    def _to_model(self, entity: CloudResource) -> CloudResourceModel:
        return CloudResourceModel(
            id=entity.id,
            app_id=entity.app_id,
            resource_type=entity.resource_type.value,
            resource_name=entity.resource_name,
            configuration=entity.configuration,
            status=entity.status.value,
            related_plan_ids=entity.related_plan_ids,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            created_by=entity.created_by,
        )

    def get_by_id(self, resource_id: str) -> Optional[CloudResource]:
        result = self._session.execute(
            select(CloudResourceModel).where(CloudResourceModel.id == resource_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    def list_by_app(
        self,
        app_id: str,
        resource_type: Optional[str] = None
    ) -> List[CloudResource]:
        query = select(CloudResourceModel).where(CloudResourceModel.app_id == app_id)
        if resource_type:
            query = query.where(CloudResourceModel.resource_type == resource_type)

        result = self._session.execute(query)
        return [self._to_entity(m) for m in result.scalars().all()]

    def list_all(
        self,
        app_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> Dict[str, Any]:
        query = select(CloudResourceModel)

        if app_id:
            query = query.where(CloudResourceModel.app_id == app_id)
        if resource_type:
            query = query.where(CloudResourceModel.resource_type == resource_type)
        if keyword:
            query = query.where(CloudResourceModel.resource_name.ilike(f"%{keyword}%"))

        count_result = self._session.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar()

        query = query.order_by(CloudResourceModel.created_at.desc())
        query = query.offset((page - 1) * size).limit(size)

        result = self._session.execute(query)
        models = result.scalars().all()

        return {
            'page': page,
            'size': size,
            'total': total,
            'total_pages': (total + size - 1) // size,
            'data': [self._to_entity(m) for m in models]
        }

    def save(self, resource: CloudResource) -> CloudResource:
        model = self._session.get(CloudResourceModel, resource.id)

        if model:
            model.resource_type = resource.resource_type.value
            model.resource_name = resource.resource_name
            model.configuration = resource.configuration
            model.status = resource.status.value
            model.related_plan_ids = resource.related_plan_ids
            model.updated_at = datetime.utcnow()
        else:
            model = self._to_model(resource)
            self._session.add(model)

        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)

    def delete(self, resource_id: str) -> bool:
        model = self._session.get(CloudResourceModel, resource_id)
        if model:
            self._session.delete(model)
            self._session.commit()
            return True
        return False

    def count_by_status(self) -> Dict[str, int]:
        result = self._session.execute(
            select(CloudResourceModel.status, func.count())
            .group_by(CloudResourceModel.status)
        )
        return {status: count for status, count in result.all()}


class AccountRepositoryImpl:
    """账号仓库实现"""

    def __init__(self, session: Session):
        self._session = session

    def _to_entity(self, model: AccountModel) -> Account:
        return Account(
            id=model.id,
            app_id=model.app_id,
            account_type=AccountType(model.account_type),
            account_name=model.account_name,
            permission_level=PermissionLevel(model.permission_level),
            holder_name=model.holder_name,
            valid_from=model.valid_from,
            valid_until=model.valid_until,
            password_change_cycle=model.password_change_cycle,
            status=InventoryStatus(model.status),
            related_plan_ids=model.related_plan_ids,
            created_at=model.created_at,
            updated_at=model.updated_at,
            created_by=model.created_by,
        )

    def _to_model(self, entity: Account) -> AccountModel:
        return AccountModel(
            id=entity.id,
            app_id=entity.app_id,
            account_type=entity.account_type.value,
            account_name=entity.account_name,
            permission_level=entity.permission_level.value,
            holder_name=entity.holder_name,
            valid_from=entity.valid_from,
            valid_until=entity.valid_until,
            password_change_cycle=entity.password_change_cycle,
            status=entity.status.value,
            related_plan_ids=entity.related_plan_ids,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            created_by=entity.created_by,
        )

    def get_by_id(self, account_id: str) -> Optional[Account]:
        result = self._session.execute(
            select(AccountModel).where(AccountModel.id == account_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    def list_by_app(
        self,
        app_id: str,
        account_type: Optional[str] = None
    ) -> List[Account]:
        query = select(AccountModel).where(AccountModel.app_id == app_id)
        if account_type:
            query = query.where(AccountModel.account_type == account_type)

        result = self._session.execute(query)
        return [self._to_entity(m) for m in result.scalars().all()]

    def list_all(
        self,
        app_id: Optional[str] = None,
        account_type: Optional[str] = None,
        status: Optional[str] = None,
        permission_level: Optional[str] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> Dict[str, Any]:
        query = select(AccountModel)

        if app_id:
            query = query.where(AccountModel.app_id == app_id)
        if account_type:
            query = query.where(AccountModel.account_type == account_type)
        if status:
            query = query.where(AccountModel.status == status)
        if permission_level:
            query = query.where(AccountModel.permission_level == permission_level)
        if keyword:
            query = query.where(
                or_(
                    AccountModel.account_name.ilike(f"%{keyword}%"),
                    AccountModel.holder_name.ilike(f"%{keyword}%")
                )
            )

        count_result = self._session.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar()

        query = query.order_by(AccountModel.created_at.desc())
        query = query.offset((page - 1) * size).limit(size)

        result = self._session.execute(query)
        models = result.scalars().all()

        return {
            'page': page,
            'size': size,
            'total': total,
            'total_pages': (total + size - 1) // size,
            'data': [self._to_entity(m) for m in models]
        }

    def save(self, account: Account) -> Account:
        model = self._session.get(AccountModel, account.id)

        if model:
            model.account_type = account.account_type.value
            model.account_name = account.account_name
            model.permission_level = account.permission_level.value
            model.holder_name = account.holder_name
            model.valid_from = account.valid_from
            model.valid_until = account.valid_until
            model.password_change_cycle = account.password_change_cycle
            model.status = account.status.value
            model.related_plan_ids = account.related_plan_ids
            model.updated_at = datetime.utcnow()
        else:
            model = self._to_model(account)
            self._session.add(model)

        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)

    def delete(self, account_id: str) -> bool:
        model = self._session.get(AccountModel, account_id)
        if model:
            self._session.delete(model)
            self._session.commit()
            return True
        return False

    def count_by_status(self) -> Dict[str, int]:
        result = self._session.execute(
            select(AccountModel.status, func.count())
            .group_by(AccountModel.status)
        )
        return {status: count for status, count in result.all()}

    def count_expiring_soon(self, days: int = 30) -> int:
        """统计即将过期的账号数量"""
        expiry_date = datetime.utcnow() + timedelta(days=days)
        result = self._session.execute(
            select(func.count())
            .where(AccountModel.valid_until <= expiry_date)
            .where(AccountModel.status == 'active')
        )
        return result.scalar()


class InventoryRepositoryImpl:
    """台账仓库实现（组合三个子仓库）"""

    def __init__(self, session: Session):
        self._session = session
        self._app_repo = ApplicationRepositoryImpl(session)
        self._resource_repo = CloudResourceRepositoryImpl(session)
        self._account_repo = AccountRepositoryImpl(session)

    # 应用系统相关
    def get_application(self, app_id: str) -> Optional[Application]:
        return self._app_repo.get_by_id(app_id)

    def list_applications(
        self,
        status: Optional[str] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> Dict[str, Any]:
        return self._app_repo.list_all(status, keyword, page, size)

    def save_application(self, application: Application) -> Application:
        return self._app_repo.save(application)

    def delete_application(self, app_id: str) -> bool:
        return self._app_repo.delete(app_id)

    def get_application_related_plans(self, app_id: str) -> List[str]:
        return self._app_repo.get_related_plans(app_id)

    def exists_by_name(self, app_name: str, exclude_id: Optional[str] = None) -> bool:
        return self._app_repo.exists_by_name(app_name, exclude_id)

    def save(self, application: Application) -> Application:
        return self._app_repo.save(application)

    # 云资源相关
    def get_cloud_resource(self, resource_id: str) -> Optional[CloudResource]:
        return self._resource_repo.get_by_id(resource_id)

    def list_cloud_resources(
        self,
        app_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> Dict[str, Any]:
        return self._resource_repo.list_all(app_id, resource_type, keyword, page, size)

    def save_cloud_resource(self, resource: CloudResource) -> CloudResource:
        return self._resource_repo.save(resource)

    def delete_cloud_resource(self, resource_id: str) -> bool:
        return self._resource_repo.delete(resource_id)

    # 账号相关
    def get_account(self, account_id: str) -> Optional[Account]:
        return self._account_repo.get_by_id(account_id)

    def list_accounts(
        self,
        app_id: Optional[str] = None,
        account_type: Optional[str] = None,
        status: Optional[str] = None,
        permission_level: Optional[str] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> Dict[str, Any]:
        return self._account_repo.list_all(app_id, account_type, status, permission_level, keyword, page, size)

    def save_account(self, account: Account) -> Account:
        return self._account_repo.save(account)

    def delete_account(self, account_id: str) -> bool:
        return self._account_repo.delete(account_id)

    # 统计相关
    def get_inventory_summary(self) -> Dict[str, Any]:
        """获取台账汇总统计"""
        app_stats = self._app_repo.count_by_status()
        resource_stats = self._resource_repo.count_by_status()
        account_stats = self._account_repo.count_by_status()

        total_apps = sum(app_stats.values())
        total_resources = sum(resource_stats.values())
        total_accounts = sum(account_stats.values())

        return {
            'application_count': total_apps,
            'cloud_resource_count': total_resources,
            'account_count': total_accounts,
            'application_status_stats': app_stats,
            'resource_type_stats': resource_stats,
            'expiring_accounts_count': self._account_repo.count_expiring_soon(30),
            'expired_accounts_count': account_stats.get('expired', 0),
        }

    def link_to_plan(self, inventory_type: str, inventory_id: str, plan_id: str) -> bool:
        """关联台账到计划"""
        # 检查是否已存在关联
        result = self._session.execute(
            select(PlanInventoryLinkModel)
            .where(PlanInventoryLinkModel.plan_id == plan_id)
            .where(PlanInventoryLinkModel.inventory_type == inventory_type)
            .where(PlanInventoryLinkModel.inventory_id == inventory_id)
        )
        existing = result.scalar_one_or_none()
        if existing:
            return True

        # 创建关联
        link = PlanInventoryLinkModel(
            plan_id=plan_id,
            inventory_type=inventory_type,
            inventory_id=inventory_id
        )
        self._session.add(link)
        self._session.commit()

        # 更新台账的关联计划ID列表
        if inventory_type == 'application':
            app = self._app_repo.get_by_id(inventory_id)
            if app and plan_id not in app.related_plan_ids:
                app.related_plan_ids.append(plan_id)
                self._app_repo.save(app)
        elif inventory_type == 'cloud_resource':
            resource = self._resource_repo.get_by_id(inventory_id)
            if resource and plan_id not in resource.related_plan_ids:
                resource.related_plan_ids.append(plan_id)
                self._resource_repo.save(resource)
        elif inventory_type == 'account':
            account = self._account_repo.get_by_id(inventory_id)
            if account and plan_id not in account.related_plan_ids:
                account.related_plan_ids.append(plan_id)
                self._account_repo.save(account)

        return True

    def unlink_from_plan(self, inventory_type: str, inventory_id: str, plan_id: str) -> bool:
        """取消台账与计划的关联"""
        result = self._session.execute(
            select(PlanInventoryLinkModel)
            .where(PlanInventoryLinkModel.plan_id == plan_id)
            .where(PlanInventoryLinkModel.inventory_type == inventory_type)
            .where(PlanInventoryLinkModel.inventory_id == inventory_id)
        )
        link = result.scalar_one_or_none()
        if link:
            self._session.delete(link)
            self._session.commit()

        # 更新台账的关联计划ID列表
        if inventory_type == 'application':
            app = self._app_repo.get_by_id(inventory_id)
            if app and plan_id in app.related_plan_ids:
                app.related_plan_ids.remove(plan_id)
                self._app_repo.save(app)
        elif inventory_type == 'cloud_resource':
            resource = self._resource_repo.get_by_id(inventory_id)
            if resource and plan_id in resource.related_plan_ids:
                resource.related_plan_ids.remove(plan_id)
                self._resource_repo.save(resource)
        elif inventory_type == 'account':
            account = self._account_repo.get_by_id(inventory_id)
            if account and plan_id in account.related_plan_ids:
                account.related_plan_ids.remove(plan_id)
                self._account_repo.save(account)

        return True
