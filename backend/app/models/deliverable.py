"""
交付物模型
定义检查项的交付物上传信息
"""

import enum
from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from ..database import Base


class FileType(str, enum.Enum):
    """文件类型枚举"""
    PDF = "pdf"
    WORD = "word"
    EXCEL = "excel"
    SCRIPT = "script"
    LOG = "log"
    OTHER = "other"


class DeliverableStatus(str, enum.Enum):
    """交付物状态枚举"""
    ACTIVE = "active"
    DELETED = "deleted"


class Deliverable(Base):
    """交付物表"""
    __tablename__ = "deliverables"
    
    id = Column(Integer, primary_key=True, index=True)
    checklist_item_id = Column(Integer, ForeignKey("checklist_items.id"), nullable=False, index=True)
    uploader_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    file_name = Column(String(200), nullable=False)
    file_type = Column(Enum("pdf", "word", "excel", "script", "log", "other", name="file_type"), nullable=False)
    file_size = Column(Integer, nullable=False)  # 字节
    file_path = Column(String(500), nullable=False)
    file_hash = Column(String(64))  # MD5
    description = Column(Text)
    status = Column(Enum("active", "deleted", name="deliverable_status"), default="active")
    
    uploaded_at = Column(DateTime, server_default=func.now())
    
    # 关联关系
    checklist_item = relationship("ChecklistItem", back_populates="deliverables")
    uploader = relationship("User")
    
    def __repr__(self):
        return f"<Deliverable {self.file_name}>"
