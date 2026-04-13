"""
审批材料实体
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


@dataclass
class ApprovalFile:
    """审批材料实体"""
    id: UUID
    plan_id: str
    file_name: str
    file_type: str
    file_size: int
    storage_path: str
    uploaded_by: str
    uploaded_at: datetime
    description: Optional[str] = None
    
    MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB
    ALLOWED_EXTENSIONS = {'.pdf', '.xlsx', '.xls', '.doc', '.docx', '.txt', '.sh', '.py'}
    
    @classmethod
    def create(
        cls,
        plan_id: str,
        file_name: str,
        file_type: str,
        file_size: int,
        storage_path: str,
        uploaded_by: str,
        description: Optional[str] = None
    ) -> "ApprovalFile":
        if file_size > cls.MAX_FILE_SIZE:
            raise ValueError(f"File size exceeds maximum {cls.MAX_FILE_SIZE} bytes (20MB)")
        
        ext = file_type.lower()
        if ext not in cls.ALLOWED_EXTENSIONS:
            raise ValueError(f"File type '{ext}' not allowed")
        
        return cls(
            id=uuid4(),
            plan_id=plan_id,
            file_name=file_name,
            file_type=ext,
            file_size=file_size,
            storage_path=storage_path,
            uploaded_by=uploaded_by,
            uploaded_at=datetime.utcnow(),
            description=description
        )
    
    @property
    def size_in_mb(self) -> float:
        return round(self.file_size / (1024 * 1024), 2)
    
    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "plan_id": self.plan_id,
            "file_name": self.file_name,
            "file_type": self.file_type,
            "file_size": self.file_size,
            "size_in_mb": self.size_in_mb,
            "storage_path": self.storage_path,
            "description": self.description,
            "uploaded_by": self.uploaded_by,
            "uploaded_at": self.uploaded_at.isoformat() if self.uploaded_at else None
        }
