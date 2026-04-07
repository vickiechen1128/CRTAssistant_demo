"""
功能模块状态值对象
"""
from dataclasses import dataclass, field
from typing import Set, Dict, FrozenSet


# 状态流转图 - 模块级常量
TRANSITIONS: Dict[str, FrozenSet[str]] = {
    "draft": frozenset({"developing"}),
    "developing": frozenset({"testing", "draft"}),
    "testing": frozenset({"online", "developing"}),
    "online": frozenset({"offline"}),
    "offline": frozenset({"online"}),
}

# 有效状态值
VALID_STATUSES: FrozenSet[str] = frozenset({
    "draft",        # 草稿
    "developing",   # 开发中
    "testing",      # 测试中
    "online",       # 已上线
    "offline",      # 已下线
})


@dataclass(frozen=True)
class ModuleStatus:
    """功能模块状态值对象"""
    value: str
    label: str
    description: str
    
    def __post_init__(self):
        if self.value not in VALID_STATUSES:
            raise ValueError(f"Invalid module status: {self.value}")
    
    @classmethod
    def draft(cls) -> "ModuleStatus":
        """草稿状态"""
        return cls("draft", "草稿", "模块处于设计阶段")
    
    @classmethod
    def developing(cls) -> "ModuleStatus":
        """开发中状态"""
        return cls("developing", "开发中", "模块正在开发中")
    
    @classmethod
    def testing(cls) -> "ModuleStatus":
        """测试中状态"""
        return cls("testing", "测试中", "模块正在测试阶段")
    
    @classmethod
    def online(cls) -> "ModuleStatus":
        """已上线状态"""
        return cls("online", "已上线", "模块已上线运行")
    
    @classmethod
    def offline(cls) -> "ModuleStatus":
        """已下线状态"""
        return cls("offline", "已下线", "模块已下线")
    
    @classmethod
    def from_string(cls, value: str) -> "ModuleStatus":
        """从字符串创建状态"""
        status_map = {
            "draft": cls.draft(),
            "developing": cls.developing(),
            "testing": cls.testing(),
            "online": cls.online(),
            "offline": cls.offline(),
        }
        if value not in status_map:
            raise ValueError(f"Invalid module status: {value}")
        return status_map[value]
    
    def can_transition_to(self, new_status: "ModuleStatus") -> bool:
        """检查是否可以流转到目标状态"""
        if self.value == new_status.value:
            return True
        return new_status.value in TRANSITIONS.get(self.value, frozenset())
    
    @property
    def is_online(self) -> bool:
        """是否已上线"""
        return self.value == "online"
    
    @property
    def is_offline(self) -> bool:
        """是否已下线"""
        return self.value == "offline"
    
    @property
    def is_editable(self) -> bool:
        """是否可编辑（草稿或开发中）"""
        return self.value in {"draft", "developing"}
    
    @property
    def color(self) -> str:
        """状态对应的颜色（用于前端展示）"""
        color_map = {
            "draft": "default",
            "developing": "blue",
            "testing": "orange",
            "online": "green",
            "offline": "gray",
        }
        return color_map.get(self.value, "default")
    
    @property
    def icon(self) -> str:
        """状态对应的图标"""
        icon_map = {
            "draft": "edit",
            "developing": "code",
            "testing": "experiment",
            "online": "check-circle",
            "offline": "stop",
        }
        return icon_map.get(self.value, "question")
    
    def __eq__(self, other) -> bool:
        if isinstance(other, ModuleStatus):
            return self.value == other.value
        return self.value == other
    
    def __hash__(self) -> int:
        return hash(self.value)
    
    def __str__(self) -> str:
        return self.value
