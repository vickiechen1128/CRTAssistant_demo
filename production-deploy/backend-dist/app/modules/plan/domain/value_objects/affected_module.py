"""
受影响功能模块值对象
用于记录计划影响的功能模块及变更内容
"""
from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass(frozen=True)
class AffectedModule:
    """
    受影响功能模块值对象
    
    属性:
        module_id: 功能模块ID（新增时为临时ID，完成后替换为实际ID）
        module_name: 模块名称
        action: 操作类型 (create/update/delete)
        before_version: 变更前版本（创建时为null）
        after_version: 变更后版本
        change_description: 变更说明（可选）
    """
    module_id: str
    module_name: str
    action: str  # create, update, delete
    before_version: Optional[str] = None
    after_version: Optional[str] = None
    change_description: Optional[str] = None
    
    def __post_init__(self):
        if self.action not in {"create", "update", "delete"}:
            raise ValueError(f"Invalid action: {self.action}")
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "module_id": self.module_id,
            "module_name": self.module_name,
            "action": self.action,
            "before_version": self.before_version,
            "after_version": self.after_version,
            "change_description": self.change_description,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AffectedModule":
        """从字典创建"""
        return cls(
            module_id=data["module_id"],
            module_name=data["module_name"],
            action=data["action"],
            before_version=data.get("before_version"),
            after_version=data.get("after_version"),
            change_description=data.get("change_description"),
        )
    
    @property
    def is_create(self) -> bool:
        """是否为创建操作"""
        return self.action == "create"
    
    @property
    def is_update(self) -> bool:
        """是否为更新操作"""
        return self.action == "update"
    
    @property
    def is_delete(self) -> bool:
        """是否为删除操作"""
        return self.action == "delete"
    
    @property
    def version_change(self) -> Optional[str]:
        """版本变更描述"""
        if self.before_version and self.after_version:
            return f"{self.before_version} → {self.after_version}"
        elif self.after_version:
            return f"新建 {self.after_version}"
        return None
