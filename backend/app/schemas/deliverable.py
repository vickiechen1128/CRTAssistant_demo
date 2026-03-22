"""
交付物Schema
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class DeliverableCreate(BaseModel):
    """创建交付物请求Schema（实际通过form-data上传）"""
    checklist_item_id: int
    description: Optional[str] = None


class UserBrief(BaseModel):
    """用户信息简版"""
    id: int
    real_name: str
    
    class Config:
        from_attributes = True


class DeliverableResponse(BaseModel):
    """交付物响应Schema"""
    id: int
    checklist_item_id: int
    file_name: str
    file_type: str
    file_size: int
    file_path: str
    file_hash: Optional[str] = None
    description: Optional[str] = None
    uploader: UserBrief
    uploaded_at: datetime
    
    class Config:
        from_attributes = True
