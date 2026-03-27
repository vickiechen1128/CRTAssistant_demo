"""
用户相关的 Pydantic 模型
"""
from pydantic import BaseModel


class UserInToken(BaseModel):
    """Token中包含的用户信息"""
    id: int
    username: str
    role: str = "user"

    class Config:
        from_attributes = True
