"""
SOP 模板类型值对象
对应 5 种计划分类
"""
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(frozen=True)
class TemplateType:
    """
    SOP 模板类型值对象
    
    5 种模板类型对应 5 种计划分类：
    - new_system: 新系统上线
    - new_feature: 新功能上线
    - func_change: 功能变更
    - arch_change: 架构变更
    - security: 安全检查
    """
    value: str
    
    VALID_TYPES = {
        "new_system",
        "new_feature",
        "func_change",
        "arch_change",
        "security"
    }
    
    # 模板类型对应的默认父工作项配置
    DEFAULT_PARENT_ITEMS: Dict[str, List[Dict]] = field(default_factory=lambda: {
        "new_system": [
            {"name": "基础资源标准化交付", "required": True, "category": "base_resource"},
            {"name": "服务对象台账更新", "required": True, "category": "inventory"},
            {"name": "上线前安全检测", "required": True, "category": "security"},
            {"name": "监控告警配置确认", "required": True, "category": "monitoring"},
        ],
        "new_feature": [
            {"name": "服务对象台账更新", "required": True, "category": "inventory"},
            {"name": "监控告警配置确认", "required": True, "category": "monitoring"},
        ],
        "func_change": [
            {"name": "服务对象台账更新", "required": True, "category": "inventory"},
            {"name": "监控告警配置确认", "required": True, "category": "monitoring"},
        ],
        "arch_change": [
            {"name": "基础资源标准化交付", "required": True, "category": "base_resource"},
            {"name": "服务对象台账更新", "required": True, "category": "inventory"},
            {"name": "上线前安全检测", "required": True, "category": "security"},
            {"name": "监控告警配置确认", "required": True, "category": "monitoring"},
        ],
        "security": [
            {"name": "系统漏洞修复", "required": True, "category": "security"},
            {"name": "基线加固", "required": True, "category": "security"},
            {"name": "渗透测试", "required": True, "category": "security"},
            {"name": "文件安全", "required": True, "category": "security"},
        ],
    })

    def __post_init__(self):
        if self.value not in self.VALID_TYPES:
            raise ValueError(f"Invalid template type: {self.value}")
    
    @classmethod
    def new_system(cls) -> "TemplateType":
        return cls("new_system")
    
    @classmethod
    def new_feature(cls) -> "TemplateType":
        return cls("new_feature")
    
    @classmethod
    def func_change(cls) -> "TemplateType":
        return cls("func_change")
    
    @classmethod
    def arch_change(cls) -> "TemplateType":
        return cls("arch_change")
    
    @classmethod
    def security(cls) -> "TemplateType":
        return cls("security")
    
    @property
    def default_parent_items(self) -> List[Dict]:
        """获取该模板类型的默认父工作项配置"""
        return self.DEFAULT_PARENT_ITEMS.get(self.value, [])
    
    @property
    def display_name(self) -> str:
        """获取显示名称"""
        mapping = {
            "new_system": "新系统上线",
            "new_feature": "新功能上线",
            "func_change": "功能变更",
            "arch_change": "架构变更",
            "security": "安全检查",
        }
        return mapping.get(self.value, self.value)
    
    @classmethod
    def from_plan_category(cls, category: str) -> "TemplateType":
        """从计划分类创建模板类型"""
        mapping = {
            "new_system": "new_system",
            "new_feature": "new_feature",
            "func_change": "func_change",
            "arch_change": "arch_change",
            "security_check": "security",
        }
        template = mapping.get(category)
        if not template:
            raise ValueError(f"No template mapping for category: {category}")
        return cls(template)
    
    def __str__(self) -> str:
        return self.value
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TemplateType):
            return False
        return self.value == other.value
    
    def __hash__(self) -> int:
        return hash(self.value)
