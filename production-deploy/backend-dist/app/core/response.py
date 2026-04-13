"""
统一 API 响应格式
提供标准的响应包装
"""
from typing import Any, Optional, TypeVar, Generic
from pydantic import BaseModel

T = TypeVar('T')


class ApiResponse(BaseModel, Generic[T]):
    """
    统一 API 响应格式
    
    Attributes:
        success: 是否成功
        message: 提示消息
        data: 响应数据
        error: 错误信息（失败时）
    """
    success: bool = True
    message: str = "Success"
    data: Optional[T] = None
    error: Optional[str] = None
    
    @classmethod
    def success_response(cls, data: Any = None, message: str = "Success") -> dict:
        """成功响应"""
        return {
            "success": True,
            "message": message,
            "data": data,
            "error": None
        }
    
    @classmethod
    def error_response(cls, error: str, message: str = "Error") -> dict:
        """错误响应"""
        return {
            "success": False,
            "message": message,
            "data": None,
            "error": error
        }


def success_response(data: Any = None, message: str = "Success") -> dict:
    """
    创建成功响应
    
    Args:
        data: 响应数据
        message: 成功消息
        
    Returns:
        标准响应字典
    """
    return {
        "success": True,
        "message": message,
        "data": data,
        "error": None
    }


def error_response(error: str, message: str = "Error") -> dict:
    """
    创建错误响应
    
    Args:
        error: 错误信息
        message: 错误消息
        
    Returns:
        标准响应字典
    """
    return {
        "success": False,
        "message": message,
        "data": None,
        "error": error
    }
