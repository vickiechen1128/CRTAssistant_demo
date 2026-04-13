"""
通用 API Schemas
"""
from typing import TypeVar, Generic, Optional
from pydantic import BaseModel

T = TypeVar('T')


class ApiResponseSchema(BaseModel, Generic[T]):
    """通用 API 响应格式"""
    code: int = 200
    message: str = "success"
    data: Optional[T] = None
    
    class Config:
        arbitrary_types_allowed = True
