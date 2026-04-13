"""
功能模块仓储接口
"""
from abc import ABC, abstractmethod
from typing import List, Optional

from app.modules.inventory.domain.entities.function_module import FunctionModule


class FunctionModuleRepository(ABC):
    """功能模块仓储接口"""
    
    @abstractmethod
    async def get_by_id(self, module_id: str) -> Optional[FunctionModule]:
        """根据ID获取功能模块"""
        pass
    
    @abstractmethod
    async def get_by_app_id(self, app_id: str) -> List[FunctionModule]:
        """获取应用下的所有功能模块"""
        pass
    
    @abstractmethod
    async def get_by_code_and_version(
        self, 
        app_id: str, 
        module_code: str, 
        version: str
    ) -> Optional[FunctionModule]:
        """根据应用ID、模块编码和版本获取功能模块"""
        pass
    
    @abstractmethod
    async def get_by_plan_id(self, plan_id: str) -> List[FunctionModule]:
        """获取关联到指定计划的所有功能模块"""
        pass
    
    @abstractmethod
    async def get_children(self, parent_module_id: str) -> List[FunctionModule]:
        """获取子模块列表"""
        pass
    
    @abstractmethod
    async def save(self, module: FunctionModule) -> FunctionModule:
        """保存功能模块"""
        pass
    
    @abstractmethod
    async def update(self, module: FunctionModule) -> FunctionModule:
        """更新功能模块"""
        pass
    
    @abstractmethod
    async def delete(self, module_id: str) -> bool:
        """删除功能模块"""
        pass
    
    @abstractmethod
    async def exists(self, app_id: str, module_code: str, version: str) -> bool:
        """检查功能模块是否存在"""
        pass
    
    @abstractmethod
    async def update_status(
        self, 
        module_id: str, 
        new_status: str,
        operator: str = ""
    ) -> Optional[FunctionModule]:
        """更新功能模块状态"""
        pass
    
    @abstractmethod
    async def launch_module(
        self, 
        module_id: str, 
        plan_id: str,
        operator: str = ""
    ) -> Optional[FunctionModule]:
        """上线功能模块"""
        pass
