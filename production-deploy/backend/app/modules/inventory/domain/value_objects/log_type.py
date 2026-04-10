"""
生命周期日志类型值对象
"""
from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class LogType:
    """生命周期日志类型值对象"""
    value: str
    label: str
    description: str
    icon: str = "info-circle"
    color: str = "default"
    
    # 有效日志类型
    VALID_TYPES = {
        "system_launch",
        "system_upgrade",
        "system_rollback",
        "system_offline",
        "module_launch",
        "module_update",
        "module_offline",
        "config_change",
        "owner_change",
        "status_change",
        "manual",
    }
    
    def __post_init__(self):
        if self.value not in self.VALID_TYPES:
            raise ValueError(f"Invalid log type: {self.value}")
    
    @classmethod
    def system_launch(cls) -> "LogType":
        """系统上线"""
        return cls("system_launch", "系统上线", "新系统首次上线", "rocket", "green")
    
    @classmethod
    def system_upgrade(cls) -> "LogType":
        """系统升级"""
        return cls("system_upgrade", "系统升级", "系统版本升级", "arrow-up", "blue")
    
    @classmethod
    def system_rollback(cls) -> "LogType":
        """系统回滚"""
        return cls("system_rollback", "系统回滚", "系统版本回滚", "rollback", "orange")
    
    @classmethod
    def system_offline(cls) -> "LogType":
        """系统下线"""
        return cls("system_offline", "系统下线", "系统下线", "poweroff", "red")
    
    @classmethod
    def module_launch(cls) -> "LogType":
        """功能上线"""
        return cls("module_launch", "功能上线", "功能模块首次上线", "appstore", "cyan")
    
    @classmethod
    def module_update(cls) -> "LogType":
        """功能变更"""
        return cls("module_update", "功能变更", "功能模块更新", "edit", "purple")
    
    @classmethod
    def module_offline(cls) -> "LogType":
        """功能下线"""
        return cls("module_offline", "功能下线", "功能模块下线", "stop", "magenta")
    
    @classmethod
    def config_change(cls) -> "LogType":
        """配置变更"""
        return cls("config_change", "配置变更", "系统配置变更", "setting", "gold")
    
    @classmethod
    def owner_change(cls) -> "LogType":
        """负责人变更"""
        return cls("owner_change", "负责人变更", "负责人变更", "user-switch", "lime")
    
    @classmethod
    def status_change(cls) -> "LogType":
        """状态变更"""
        return cls("status_change", "状态变更", "状态变更", "tag", "geekblue")
    
    @classmethod
    def manual(cls) -> "LogType":
        """手动记录"""
        return cls("manual", "手动记录", "手动添加的记录", "file-text", "default")
    
    @classmethod
    def from_string(cls, value: str) -> "LogType":
        """从字符串创建日志类型"""
        type_map = {
            "system_launch": cls.system_launch(),
            "system_upgrade": cls.system_upgrade(),
            "system_rollback": cls.system_rollback(),
            "system_offline": cls.system_offline(),
            "module_launch": cls.module_launch(),
            "module_update": cls.module_update(),
            "module_offline": cls.module_offline(),
            "config_change": cls.config_change(),
            "owner_change": cls.owner_change(),
            "status_change": cls.status_change(),
            "manual": cls.manual(),
        }
        if value not in type_map:
            raise ValueError(f"Invalid log type: {value}")
        return type_map[value]
    
    def __eq__(self, other) -> bool:
        if isinstance(other, LogType):
            return self.value == other.value
        return self.value == other
    
    def __hash__(self) -> int:
        return hash(self.value)
    
    def __str__(self) -> str:
        return self.value
