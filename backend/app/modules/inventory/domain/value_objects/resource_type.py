"""
云服务资源类型值对象
"""
from enum import Enum
from dataclasses import dataclass


class ResourceTypeEnum(Enum):
    """资源类型枚举"""
    COMPUTE = "compute"
    NETWORK = "network"
    STORAGE = "storage"
    BACKUP = "backup"
    MIDDLEWARE = "middleware"
    DATABASE = "database"
    CACHE = "cache"
    MESSAGE_QUEUE = "message_queue"


@dataclass(frozen=True)
class ResourceType:
    """
    云服务资源类型值对象
    
    资源类型：
    - compute: 计算服务（ECS/VM/容器实例）
    - network: 网络服务（VPC/SLB/安全组）
    - storage: 存储服务（对象存储/块存储/NAS）
    - backup: 备份服务（快照/备份策略）
    - middleware: 中间件（Nginx/Tomcat等）
    - database: 数据库（MySQL/Redis/MongoDB等）
    - cache: 缓存服务（Redis/Memcached等）
    - message_queue: 消息队列（Kafka/RabbitMQ等）
    """
    value: str
    
    VALID_TYPES = {
        "compute", "network", "storage", "backup",
        "middleware", "database", "cache", "message_queue"
    }
    
    def __post_init__(self):
        if self.value not in self.VALID_TYPES:
            raise ValueError(f"Invalid resource type: {self.value}")
    
    @classmethod
    def compute(cls) -> "ResourceType":
        return cls("compute")
    
    @classmethod
    def network(cls) -> "ResourceType":
        return cls("network")
    
    @classmethod
    def storage(cls) -> "ResourceType":
        return cls("storage")
    
    @classmethod
    def backup(cls) -> "ResourceType":
        return cls("backup")
    
    @classmethod
    def middleware(cls) -> "ResourceType":
        return cls("middleware")
    
    @classmethod
    def database(cls) -> "ResourceType":
        return cls("database")
    
    @classmethod
    def cache(cls) -> "ResourceType":
        return cls("cache")
    
    @classmethod
    def message_queue(cls) -> "ResourceType":
        return cls("message_queue")
    
    @property
    def is_iaas(self) -> bool:
        """是否为IAAS层资源"""
        return self.value in {"compute", "network", "storage", "backup"}
    
    @property
    def is_paas(self) -> bool:
        """是否为PAAS层资源"""
        return self.value in {"middleware", "database", "cache", "message_queue"}
    
    @property
    def display_name(self) -> str:
        """获取显示名称"""
        mapping = {
            "compute": "计算服务",
            "network": "网络服务",
            "storage": "存储服务",
            "backup": "备份服务",
            "middleware": "中间件",
            "database": "数据库",
            "cache": "缓存服务",
            "message_queue": "消息队列",
        }
        return mapping.get(self.value, self.value)
    
    def __str__(self) -> str:
        return self.value
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ResourceType):
            return False
        return self.value == other.value
    
    def __hash__(self) -> int:
        return hash(self.value)
