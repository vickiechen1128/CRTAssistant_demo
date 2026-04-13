"""
SOP 模板仓储接口
定义领域层与基础设施层的契约
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from ..entities.sop_template import SOPTemplate
from ..value_objects.template_type import TemplateType
from ..value_objects.template_status import TemplateStatus


class SOPTemplateRepository(ABC):
    """
    SOP 模板仓储接口
    
    职责：
    1. 定义 SOPTemplate 的持久化操作契约
    2. 隐藏具体数据库实现细节
    """
    
    @abstractmethod
    def save(self, template: SOPTemplate) -> SOPTemplate:
        """保存模板"""
        pass
    
    @abstractmethod
    def find_by_id(self, template_id: str) -> Optional[SOPTemplate]:
        """根据ID查找模板"""
        pass
    
    @abstractmethod
    def find_by_template_id(self, template_id: str) -> Optional[SOPTemplate]:
        """根据业务ID查找模板"""
        pass
    
    @abstractmethod
    def find_active_by_type(self, template_type: TemplateType) -> Optional[SOPTemplate]:
        """查找指定类型的活跃模板"""
        pass
    
    @abstractmethod
    def find_all(
        self,
        template_type: Optional[TemplateType] = None,
        status: Optional[TemplateStatus] = None,
        keyword: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[SOPTemplate], int]:
        """查询模板列表"""
        pass
    
    @abstractmethod
    def delete(self, template_id: str) -> bool:
        """删除模板"""
        pass
    
    @abstractmethod
    def exists(self, template_id: str) -> bool:
        """检查模板是否存在"""
        pass
    
    @abstractmethod
    def exists_active_version(self, template_id: str, exclude_id: Optional[str] = None) -> bool:
        """检查是否存在活跃版本"""
        pass
    
    @abstractmethod
    def find_by_template_id_and_version(self, template_id: str, version: str) -> Optional[SOPTemplate]:
        """根据模板ID和版本号查找"""
        pass
