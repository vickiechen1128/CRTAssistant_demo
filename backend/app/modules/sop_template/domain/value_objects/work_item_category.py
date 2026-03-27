"""
工作项分类值对象（5大类）
"""
from dataclasses import dataclass, field
from typing import Dict


@dataclass(frozen=True)
class WorkItemCategory:
    """
    工作项分类值对象

    5 大分类：
    - inventory: 服务对象台账收集
    - base_resource: 基础资源标准化交付
    - security: 安全基线核验
    - permission: 生产环境权限移交
    - monitoring: 监控告警配置确认
    """
    value: str

    VALID_CATEGORIES = {
        "inventory",
        "base_resource",
        "security",
        "permission",
        "monitoring"
    }

    # 分类元数据
    METADATA: Dict[str, Dict] = field(default_factory=lambda: {
        "inventory": {
            "name": "服务对象台账收集",
            "icon": "📁",
            "description": "应用系统、资源、账号台账",
        },
        "base_resource": {
            "name": "基础资源标准化交付",
            "icon": "🔧",
            "description": "系统基线、软件部署",
        },
        "security": {
            "name": "安全基线核验",
            "icon": "🔒",
            "description": "安全加固、漏洞检查",
        },
        "permission": {
            "name": "生产环境权限移交",
            "icon": "👤",
            "description": "账号权限、访问控制",
        },
        "monitoring": {
            "name": "监控告警配置确认",
            "icon": "📊",
            "description": "监控项、告警规则",
        },
    })

    def __post_init__(self):
        if self.value not in self.VALID_CATEGORIES:
            raise ValueError(f"Invalid work item category: {self.value}")
    
    @classmethod
    def inventory(cls) -> "WorkItemCategory":
        return cls("inventory")
    
    @classmethod
    def base_resource(cls) -> "WorkItemCategory":
        return cls("base_resource")
    
    @classmethod
    def security(cls) -> "WorkItemCategory":
        return cls("security")
    
    @classmethod
    def permission(cls) -> "WorkItemCategory":
        return cls("permission")
    
    @classmethod
    def monitoring(cls) -> "WorkItemCategory":
        return cls("monitoring")
    
    @property
    def display_name(self) -> str:
        """获取显示名称"""
        return self.METADATA.get(self.value, {}).get("name", self.value)
    
    @property
    def icon(self) -> str:
        """获取图标"""
        return self.METADATA.get(self.value, {}).get("icon", "📄")
    
    @property
    def description(self) -> str:
        """获取描述"""
        return self.METADATA.get(self.value, {}).get("description", "")
    
    @property
    def color(self) -> str:
        """获取分类颜色"""
        mapping = {
            "inventory": "blue",
            "base_resource": "green",
            "security": "red",
            "permission": "orange",
            "monitoring": "purple",
        }
        return mapping.get(self.value, "default")
    
    def __str__(self) -> str:
        return self.value
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, WorkItemCategory):
            return False
        return self.value == other.value
    
    def __hash__(self) -> int:
        return hash(self.value)
