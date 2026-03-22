"""
台账模型
定义三类台账：应用系统、云服务、账户
"""

from sqlalchemy import Column, Integer, String, Enum, DateTime, Date, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from ..database import Base
import enum


class InventoryType(str, enum.Enum):
    """台账类型枚举"""
    SERVER = "server"              # 应用系统台账
    CLOUD_RESOURCE = "cloud_resource"  # 云服务开通台账
    ACCOUNT = "account"            # 系统账户台账


class InventoryStatus(str, enum.Enum):
    """台账状态枚举"""
    DRAFT = "draft"           # 草稿
    FILLING = "filling"       # 填写中
    SUBMITTED = "submitted"   # 已提交
    CONFIRMED = "confirmed"   # 已确认
    EXPIRED = "expired"       # 已过期


class Environment(str, enum.Enum):
    """环境枚举"""
    PRODUCTION = "production"   # 生产环境
    STAGING = "staging"         # 预发环境
    TEST = "test"               # 测试环境


class Inventory(Base):
    """台账主表"""
    __tablename__ = "inventories"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("admission_tasks.id"), nullable=False, index=True)
    inventory_type = Column(Enum(InventoryType), nullable=False)
    status = Column(Enum(InventoryStatus), default=InventoryStatus.DRAFT)
    
    submitted_by = Column(Integer, ForeignKey("users.id"))
    submitted_at = Column(DateTime)
    confirmed_by = Column(Integer, ForeignKey("users.id"))
    confirmed_at = Column(DateTime)
    remark = Column(Text)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # 关联关系
    task = relationship("AdmissionTask", back_populates="inventories")
    submitter = relationship("User", foreign_keys=[submitted_by])
    confirmer = relationship("User", foreign_keys=[confirmed_by])
    servers = relationship("InventoryServer", back_populates="inventory", cascade="all, delete-orphan")
    cloud_resources = relationship("InventoryCloudResource", back_populates="inventory", cascade="all, delete-orphan")
    accounts = relationship("InventoryAccount", back_populates="inventory", cascade="all, delete-orphan")


class InventoryServer(Base):
    """应用系统台账明细表"""
    __tablename__ = "inventory_servers"
    
    id = Column(Integer, primary_key=True, index=True)
    inventory_id = Column(Integer, ForeignKey("inventories.id"), nullable=False, index=True)
    
    ip_address = Column(String(50), nullable=False)
    hostname = Column(String(100), nullable=False)
    os_type = Column(String(50))
    cpu_cores = Column(Integer)
    memory_gb = Column(Integer)
    disk_gb = Column(Integer)
    purpose = Column(String(200))
    system_belong = Column(String(100))
    environment = Column(Enum(Environment))
    responsible_person = Column(String(50))
    online_date = Column(Date)
    status = Column(Enum("active", "inactive", name="server_status"), default="active")
    
    created_at = Column(DateTime, server_default=func.now())
    
    inventory = relationship("Inventory", back_populates="servers")


class InventoryCloudResource(Base):
    """云服务开通台账明细表"""
    __tablename__ = "inventory_cloud_resources"
    
    id = Column(Integer, primary_key=True, index=True)
    inventory_id = Column(Integer, ForeignKey("inventories.id"), nullable=False)
    
    resource_type = Column(Enum("compute", "network", "storage", "backup", name="resource_type"), nullable=False)
    service_type = Column(Enum("iaas", "paas", "self_deployed", name="service_type"), nullable=False)
    service_name = Column(String(100), nullable=False)  # ECS/SLB/RDS/Redis
    instance_id = Column(String(100))
    instance_name = Column(String(100))
    specification = Column(String(200))
    region = Column(String(50))
    zone = Column(String(50))
    network_config = Column(Text)
    software_name = Column(String(100))
    software_version = Column(String(50))
    responsible_person = Column(String(50))
    
    created_at = Column(DateTime, server_default=func.now())
    
    inventory = relationship("Inventory", back_populates="cloud_resources")


class InventoryAccount(Base):
    """系统及软件账户台账明细表"""
    __tablename__ = "inventory_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    inventory_id = Column(Integer, ForeignKey("inventories.id"), nullable=False, index=True)
    
    system_name = Column(String(100), nullable=False)
    server_hostname = Column(String(100), nullable=False)
    server_ip = Column(String(50), nullable=False)
    account_type = Column(Enum("system", "software", name="account_type"), nullable=False)
    account_name = Column(String(100), nullable=False)
    permission_level = Column(Enum("readonly", "readwrite", "admin", name="permission_level"))
    permission_detail = Column(Text)
    holder_name = Column(String(50))
    holder_department = Column(String(50))
    valid_from = Column(Date)
    valid_until = Column(Date, index=True)  # 用于过期提醒
    password_change_cycle = Column(Integer)  # 天
    last_password_change = Column(Date)
    status = Column(Enum("active", "expired", "to_be_revoked", name="account_status"), default="active")
    
    created_at = Column(DateTime, server_default=func.now())
    
    inventory = relationship("Inventory", back_populates="accounts")
