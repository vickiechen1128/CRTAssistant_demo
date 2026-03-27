"""
计划分类值对象
对应业务规则：5种计划分类，每种对应不同的台账操作方式
"""
from enum import Enum
from dataclasses import dataclass


class CategoryCode(Enum):
    """分类简码映射（用于生成数据标签）"""
    NEW_SYSTEM = "NEW"
    NEW_FEATURE = "FTR"
    FUNC_CHANGE = "FUN"
    ARCH_CHANGE = "ARC"
    SECURITY_CHECK = "SEC"


@dataclass(frozen=True)
class Category:
    """
    计划分类值对象
    
    分类说明：
    - new_system: 新系统上线 → 新增应用系统台账
    - new_feature: 新功能上线 → 查询+编辑应用系统台账（功能模块）
    - func_change: 功能变更 → 查询+勾选应用系统台账
    - arch_change: 架构变更 → 查询+勾选应用系统台账（可能涉及云资源/数据库变更）
    - security_check: 安全检查 → 不关联台账（全系统/指定范围安全扫描）
    """
    value: str
    
    VALID_CATEGORIES = {
        "new_system",
        "new_feature", 
        "func_change",
        "arch_change",
        "security_check"
    }
    
    def __post_init__(self):
        if self.value not in self.VALID_CATEGORIES:
            raise ValueError(f"Invalid category: {self.value}")
    
    @classmethod
    def new_system(cls) -> "Category":
        return cls("new_system")
    
    @classmethod
    def new_feature(cls) -> "Category":
        return cls("new_feature")
    
    @classmethod
    def func_change(cls) -> "Category":
        return cls("func_change")
    
    @classmethod
    def arch_change(cls) -> "Category":
        return cls("arch_change")
    
    @classmethod
    def security_check(cls) -> "Category":
        return cls("security_check")
    
    @property
    def code(self) -> str:
        """获取分类简码（用于生成数据标签）"""
        mapping = {
            "new_system": CategoryCode.NEW_SYSTEM.value,
            "new_feature": CategoryCode.NEW_FEATURE.value,
            "func_change": CategoryCode.FUNC_CHANGE.value,
            "arch_change": CategoryCode.ARCH_CHANGE.value,
            "security_check": CategoryCode.SECURITY_CHECK.value,
        }
        return mapping[self.value]
    
    @property
    def requires_inventory(self) -> bool:
        """是否需要关联台账"""
        return self.value != "security_check"
    
    @property
    def inventory_action(self) -> str:
        """
        获取台账操作类型
        - create_new: 新增台账
        - select_and_edit: 选择并编辑
        - select_existing: 选择已有
        - security_scan: 安全检查（不关联）
        """
        mapping = {
            "new_system": "create_new",
            "new_feature": "select_and_edit",
            "func_change": "select_existing",
            "arch_change": "select_existing",
            "security_check": "security_scan",
        }
        return mapping[self.value]
    
    def __str__(self) -> str:
        return self.value
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Category):
            return False
        return self.value == other.value
    
    def __hash__(self) -> int:
        return hash(self.value)
