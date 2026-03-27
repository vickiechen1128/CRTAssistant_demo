"""
审核矩阵仓储接口
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from ..entities.audit_matrix_config import AuditMatrixConfig


class AuditMatrixRepository(ABC):
    """
    审核矩阵仓储接口
    
    职责：
    1. 定义 AuditMatrixConfig 的持久化操作契约
    2. 管理审核规则和审核矩阵配置
    """
    
    @abstractmethod
    def save(self, config: AuditMatrixConfig) -> AuditMatrixConfig:
        """保存审核矩阵配置"""
        pass
    
    @abstractmethod
    def find_by_id(self, config_id: str) -> Optional[AuditMatrixConfig]:
        """根据ID查找配置"""
        pass
    
    @abstractmethod
    def find_by_config_id(self, config_id: str) -> Optional[AuditMatrixConfig]:
        """根据业务ID查找配置"""
        pass
    
    @abstractmethod
    def find_all(
        self,
        status: Optional[str] = None,
        keyword: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[AuditMatrixConfig], int]:
        """查询配置列表"""
        pass
    
    @abstractmethod
    def delete(self, config_id: str) -> bool:
        """删除配置"""
        pass
    
    @abstractmethod
    def exists(self, config_id: str) -> bool:
        """检查配置是否存在"""
        pass
    
    @abstractmethod
    def is_referenced_by_template(self, config_id: str) -> bool:
        """检查是否被模板引用"""
        pass
