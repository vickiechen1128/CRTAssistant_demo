"""
台账Schema
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from ..models.inventory import InventoryType, InventoryStatus, Environment


# ========== 应用系统台账 ==========

class InventoryServerBase(BaseModel):
    """服务器台账基础Schema"""
    ip_address: str = Field(..., pattern=r"^(\d{1,3}\.){3}\d{1,3}$")
    hostname: str = Field(..., min_length=1, max_length=100)
    os_type: Optional[str] = Field(None, max_length=50)
    cpu_cores: Optional[int] = Field(None, ge=1)
    memory_gb: Optional[int] = Field(None, ge=1)
    disk_gb: Optional[int] = Field(None, ge=1)
    purpose: Optional[str] = Field(None, max_length=200)
    system_belong: Optional[str] = Field(None, max_length=100)
    environment: Optional[Environment] = Environment.PRODUCTION
    responsible_person: Optional[str] = Field(None, max_length=50)
    online_date: Optional[date] = None


class InventoryServerCreate(InventoryServerBase):
    """创建服务器台账Schema"""
    pass


class InventoryServerResponse(InventoryServerBase):
    """服务器台账响应Schema"""
    id: int
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# ========== 云服务台账 ==========

class InventoryCloudResourceBase(BaseModel):
    """云服务台账基础Schema"""
    resource_type: str  # compute/network/storage/backup
    service_type: str  # iaas/paas/self_deployed
    service_name: str = Field(..., min_length=1, max_length=100)
    instance_id: Optional[str] = Field(None, max_length=100)
    instance_name: Optional[str] = Field(None, max_length=100)
    specification: Optional[str] = Field(None, max_length=200)
    region: Optional[str] = Field(None, max_length=50)
    zone: Optional[str] = Field(None, max_length=50)
    network_config: Optional[str] = None
    software_name: Optional[str] = Field(None, max_length=100)
    software_version: Optional[str] = Field(None, max_length=50)
    responsible_person: Optional[str] = Field(None, max_length=50)


class InventoryCloudResourceCreate(InventoryCloudResourceBase):
    """创建云服务台账Schema"""
    pass


class InventoryCloudResourceResponse(InventoryCloudResourceBase):
    """云服务台账响应Schema"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ========== 账户台账 ==========

class InventoryAccountBase(BaseModel):
    """账户台账基础Schema"""
    system_name: str = Field(..., min_length=1, max_length=100)
    server_hostname: str = Field(..., min_length=1, max_length=100)
    server_ip: str = Field(..., pattern=r"^(\d{1,3}\.){3}\d{1,3}$")
    account_type: str  # system/software
    account_name: str = Field(..., min_length=1, max_length=100)
    permission_level: Optional[str] = None  # readonly/readwrite/admin
    permission_detail: Optional[str] = None
    holder_name: Optional[str] = Field(None, max_length=50)
    holder_department: Optional[str] = Field(None, max_length=50)
    valid_from: Optional[date] = None
    valid_until: Optional[date] = None
    password_change_cycle: Optional[int] = Field(None, ge=1)
    last_password_change: Optional[date] = None


class InventoryAccountCreate(InventoryAccountBase):
    """创建账户台账Schema"""
    pass


class InventoryAccountResponse(InventoryAccountBase):
    """账户台账响应Schema"""
    id: int
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# ========== 台账主表 ==========

class InventoryCreate(BaseModel):
    """创建台账请求Schema"""
    inventory_type: InventoryType
    servers: Optional[List[InventoryServerCreate]] = None
    cloud_resources: Optional[List[InventoryCloudResourceCreate]] = None
    accounts: Optional[List[InventoryAccountCreate]] = None


class UserBrief(BaseModel):
    """用户信息简版"""
    id: int
    real_name: str
    
    class Config:
        from_attributes = True


class InventoryResponse(BaseModel):
    """台账响应Schema"""
    id: int
    task_id: int
    inventory_type: InventoryType
    status: InventoryStatus
    servers: List[InventoryServerResponse] = []
    cloud_resources: List[InventoryCloudResourceResponse] = []
    accounts: List[InventoryAccountResponse] = []
    submitter: Optional[UserBrief] = None
    submitted_at: Optional[datetime] = None
    confirmer: Optional[UserBrief] = None
    confirmed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
