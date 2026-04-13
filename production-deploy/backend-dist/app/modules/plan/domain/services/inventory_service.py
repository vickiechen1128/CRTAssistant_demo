"""
台账操作领域服务
处理计划与台账的交互逻辑
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict, Any

from ..value_objects.category import Category
from ..value_objects.affected_module import AffectedModule


@dataclass
class InventoryOperationResult:
    """台账操作结果"""
    success: bool
    inventory_id: Optional[str] = None
    module_ids: List[str] = None
    error_message: Optional[str] = None
    lifecycle_logs: List[Dict[str, Any]] = None


class InventoryService(ABC):
    """
    台账操作服务抽象类
    定义与台账模块的交互接口
    """

    @abstractmethod
    def create_application(
        self,
        app_data: Dict[str, Any],
        modules: List[Dict[str, Any]],
        cloud_resources: List[Dict[str, Any]],
        accounts: List[Dict[str, Any]],
        related_plan_id: str
    ) -> InventoryOperationResult:
        """
        创建应用系统台账
        用于 new_system 分类
        """
        pass

    @abstractmethod
    def link_to_plan(
        self,
        inventory_type: str,
        inventory_id: str,
        plan_id: str
    ) -> bool:
        """
        关联台账到计划
        在应用系统的 related_plan_ids 中添加计划ID
        """
        pass

    @abstractmethod
    def unlink_from_plan(
        self,
        inventory_type: str,
        inventory_id: str,
        plan_id: str
    ) -> bool:
        """
        取消台账与计划的关联
        从应用系统的 related_plan_ids 中移除计划ID
        """
        pass

    @abstractmethod
    def create_function_modules(
        self,
        app_id: str,
        modules: List[Dict[str, Any]],
        related_plan_id: str
    ) -> InventoryOperationResult:
        """
        创建功能模块
        用于 new_feature 分类
        """
        pass

    @abstractmethod
    def update_function_modules(
        self,
        app_id: str,
        module_updates: List[Dict[str, Any]],
        related_plan_id: str
    ) -> InventoryOperationResult:
        """
        更新功能模块
        用于 func_change 分类
        """
        pass

    @abstractmethod
    def update_function_module_status(
        self,
        app_id: str,
        module_code: str,
        status: str,
        related_plan_id: str
    ) -> bool:
        """
        更新功能模块状态
        用于计划完成时更新模块状态
        """
        pass

    @abstractmethod
    def update_application_system(
        self,
        app_ids: List[str],
        affected_modules: List[Dict[str, Any]],
        related_plan_id: str
    ) -> InventoryOperationResult:
        """
        更新应用系统
        用于 arch_change 分类
        """
        pass

    @abstractmethod
    def get_applications_by_ids(
        self,
        app_ids: List[str]
    ) -> List[Dict[str, Any]]:
        """根据ID列表获取应用系统"""
        pass

    @abstractmethod
    def get_application_modules(
        self,
        app_id: str
    ) -> List[Dict[str, Any]]:
        """获取应用系统的功能模块"""
        pass

    @abstractmethod
    def list_applications(
        self,
        status: Optional[str] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> Dict[str, Any]:
        """
        查询应用系统列表
        用于前端选择应用系统
        """
        pass


class InventoryLifecycleLogService(ABC):
    """
    生命周期日志服务抽象类
    """

    @abstractmethod
    def create_log(
        self,
        log_type: str,
        inventory_id: str,
        event_title: str,
        before_data: Optional[Dict[str, Any]],
        after_data: Optional[Dict[str, Any]],
        related_plan_id: str,
        operator: str
    ) -> Dict[str, Any]:
        """创建生命周期日志"""
        pass

    @abstractmethod
    def get_logs_by_plan_id(
        self,
        plan_id: str
    ) -> List[Dict[str, Any]]:
        """获取计划相关的生命周期日志"""
        pass


class InventoryOperationFactory:
    """
    台账操作工厂
    根据计划分类创建对应的操作参数
    """

    @staticmethod
    def create_new_system_payload(
        app_data: Dict[str, Any],
        modules: List[Dict[str, Any]],
        cloud_resources: List[Dict[str, Any]] = None,
        accounts: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        创建新系统上线的台账数据
        """
        return {
            "action_type": "create_new",
            "app_data": app_data,
            "modules": modules or [],
            "cloud_resources": cloud_resources or [],
            "accounts": accounts or [],
        }

    @staticmethod
    def create_new_feature_payload(
        selected_app_ids: List[str],
        modules: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        创建新功能上线的台账数据
        """
        return {
            "action_type": "create_module",
            "selected_app_ids": selected_app_ids,
            "modules": modules,
        }

    @staticmethod
    def create_func_change_payload(
        selected_app_ids: List[str],
        module_updates: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        创建功能变更的台账数据
        """
        return {
            "action_type": "update_module",
            "selected_app_ids": selected_app_ids,
            "module_updates": module_updates,
        }

    @staticmethod
    def create_arch_change_payload(
        selected_app_ids: List[str],
        affected_modules: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        创建架构变更的台账数据
        """
        return {
            "action_type": "update_system",
            "selected_app_ids": selected_app_ids,
            "affected_modules": affected_modules,
        }

    @staticmethod
    def create_security_check_payload(
        selected_app_ids: List[str],
        check_scope: str = "full"
    ) -> Dict[str, Any]:
        """
        创建安全检查的台账数据
        """
        return {
            "action_type": "security_scan",
            "selected_app_ids": selected_app_ids,
            "check_scope": check_scope,
        }
