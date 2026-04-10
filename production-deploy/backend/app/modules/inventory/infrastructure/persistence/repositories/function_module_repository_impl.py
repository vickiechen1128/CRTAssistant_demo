"""
功能模块仓储实现
"""
import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import select, and_, delete
from sqlalchemy.orm import Session

from app.modules.inventory.domain.entities.function_module import FunctionModule
from app.modules.inventory.domain.repositories.function_module_repository import FunctionModuleRepository
from app.modules.inventory.domain.value_objects.module_status import ModuleStatus
from app.modules.inventory.infrastructure.persistence.models.function_module_model import FunctionModuleModel


class FunctionModuleRepositoryImpl(FunctionModuleRepository):
    """功能模块仓储实现"""

    def __init__(self, session: Session):
        self.session = session

    def _to_entity(self, model: FunctionModuleModel) -> FunctionModule:
        """将模型转换为领域实体"""
        return FunctionModule(
            id=model.id,
            app_id=model.app_id,
            module_code=model.module_code,
            module_name=model.module_name,
            module_description=model.module_description,
            owner=model.owner,
            status=ModuleStatus.from_string(model.status),
            version=model.version,
            parent_module_id=model.parent_module_id,
            related_plan_id=model.related_plan_id,
            launch_time=model.launch_time,
            last_change_time=model.last_change_time,
            created_at=model.created_at,
            updated_at=model.updated_at,
            created_by=model.created_by,
        )

    def _to_model(self, entity: FunctionModule) -> FunctionModuleModel:
        """将领域实体转换为模型"""
        return FunctionModuleModel(
            id=entity.id or str(uuid.uuid4()),
            app_id=entity.app_id,
            module_code=entity.module_code,
            module_name=entity.module_name,
            module_description=entity.module_description,
            owner=entity.owner,
            status=entity.status.value if hasattr(entity.status, 'value') else str(entity.status),
            version=entity.version,
            parent_module_id=entity.parent_module_id,
            related_plan_id=entity.related_plan_id,
            launch_time=entity.launch_time,
            last_change_time=entity.last_change_time,
            created_at=entity.created_at or datetime.utcnow(),
            updated_at=entity.updated_at or datetime.utcnow(),
            created_by=entity.created_by,
        )

    async def get_by_id(self, module_id: str) -> Optional[FunctionModule]:
        """根据ID获取功能模块"""
        result = self.session.execute(
            select(FunctionModuleModel).where(FunctionModuleModel.id == module_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_app_id(self, app_id: str) -> List[FunctionModule]:
        """获取应用下的所有功能模块"""
        result = self.session.execute(
            select(FunctionModuleModel)
            .where(FunctionModuleModel.app_id == app_id)
            .order_by(FunctionModuleModel.module_code)
        )
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def get_by_code_and_version(
        self,
        app_id: str,
        module_code: str,
        version: str
    ) -> Optional[FunctionModule]:
        """根据应用ID、模块编码和版本获取功能模块"""
        result = self.session.execute(
            select(FunctionModuleModel).where(
                and_(
                    FunctionModuleModel.app_id == app_id,
                    FunctionModuleModel.module_code == module_code,
                    FunctionModuleModel.version == version
                )
            )
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_plan_id(self, plan_id: str) -> List[FunctionModule]:
        """获取关联到指定计划的所有功能模块"""
        result = self.session.execute(
            select(FunctionModuleModel)
            .where(FunctionModuleModel.related_plan_id == plan_id)
            .order_by(FunctionModuleModel.module_code)
        )
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def get_children(self, parent_module_id: str) -> List[FunctionModule]:
        """获取子模块列表"""
        result = self.session.execute(
            select(FunctionModuleModel)
            .where(FunctionModuleModel.parent_module_id == parent_module_id)
            .order_by(FunctionModuleModel.module_code)
        )
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def save(self, module: FunctionModule) -> FunctionModule:
        """保存功能模块"""
        if not module.id:
            module.id = str(uuid.uuid4())

        model = self._to_model(module)
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._to_entity(model)

    async def update(self, module: FunctionModule) -> FunctionModule:
        """更新功能模块"""
        result = self.session.execute(
            select(FunctionModuleModel).where(FunctionModuleModel.id == module.id)
        )
        model = result.scalar_one_or_none()
        if model:
            model.module_name = module.module_name
            model.module_description = module.module_description
            model.owner = module.owner
            model.status = module.status.value if hasattr(module.status, 'value') else str(module.status)
            model.version = module.version
            model.parent_module_id = module.parent_module_id
            model.related_plan_id = module.related_plan_id
            model.launch_time = module.launch_time
            model.last_change_time = module.last_change_time
            model.updated_at = datetime.utcnow()
            self.session.commit()
            self.session.refresh(model)
            return self._to_entity(model)
        return module

    async def delete(self, module_id: str) -> bool:
        """删除功能模块"""
        result = self.session.execute(
            delete(FunctionModuleModel).where(FunctionModuleModel.id == module_id)
        )
        self.session.commit()
        return result.rowcount > 0

    async def exists(self, app_id: str, module_code: str, version: str) -> bool:
        """检查功能模块是否存在"""
        result = self.session.execute(
            select(FunctionModuleModel).where(
                and_(
                    FunctionModuleModel.app_id == app_id,
                    FunctionModuleModel.module_code == module_code,
                    FunctionModuleModel.version == version
                )
            )
        )
        return result.scalar_one_or_none() is not None

    async def update_status(
        self,
        module_id: str,
        new_status: str,
        operator: str = ""
    ) -> Optional[FunctionModule]:
        """更新功能模块状态"""
        result = self.session.execute(
            select(FunctionModuleModel).where(FunctionModuleModel.id == module_id)
        )
        model = result.scalar_one_or_none()
        if model:
            model.status = new_status
            model.updated_at = datetime.utcnow()
            self.session.commit()
            self.session.refresh(model)
            return self._to_entity(model)
        return None

    async def launch_module(
        self,
        module_id: str,
        plan_id: str,
        operator: str = ""
    ) -> Optional[FunctionModule]:
        """上线功能模块"""
        result = self.session.execute(
            select(FunctionModuleModel).where(FunctionModuleModel.id == module_id)
        )
        model = result.scalar_one_or_none()
        if model:
            model.status = "online"
            model.related_plan_id = plan_id
            model.launch_time = datetime.utcnow()
            model.last_change_time = datetime.utcnow()
            model.updated_at = datetime.utcnow()
            self.session.commit()
            self.session.refresh(model)
            return self._to_entity(model)
        return None
