"""
审批材料信息值对象
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass(frozen=True)
class FileInfo:
    """审批材料信息值对象"""
    file_id: UUID
    file_name: str
    file_type: str
    file_size: int
    upload_time: datetime
    uploader_id: str
    storage_path: Optional[str] = None
    description: Optional[str] = None
    
    MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB
    ALLOWED_TYPES = {'.pdf', '.xlsx', '.xls', '.doc', '.docx', '.txt'}
    
    def __post_init__(self):
        if self.file_size > self.MAX_FILE_SIZE:
            raise ValueError(f"File size exceeds maximum {self.MAX_FILE_SIZE}")
        
        file_ext = self.file_type.lower()
        if file_ext not in self.ALLOWED_TYPES:
            raise ValueError(f"File type {file_ext} not allowed")
    
    @property
    def size_in_mb(self) -> float:
        return self.file_size / (1024 * 1024)
    
    def __str__(self) -> str:
        return f"{self.file_name} ({self.size_in_mb:.2f}MB)"
