"""
用户Schema
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from ..models.user import UserRole


class UserBase(BaseModel):
    """用户基础Schema"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    real_name: str = Field(..., min_length=2, max_length=50)
    role: UserRole = UserRole.VIEWER
    department: Optional[str] = None
    phone: Optional[str] = None


class UserCreate(UserBase):
    """创建用户请求Schema"""
    password: str = Field(..., min_length=6, max_length=100)


class UserLogin(BaseModel):
    """用户登录请求Schema"""
    username: str
    password: str


class UserResponse(UserBase):
    """用户响应Schema"""
    id: int
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True  # Pydantic V2语法，替代orm_mode


class UserInToken(BaseModel):
    """Token中存储的用户信息"""
    id: int
    username: str
    role: UserRole
