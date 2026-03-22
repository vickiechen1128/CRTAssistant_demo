"""
安全模块
处理密码哈希、JWT Token生成和验证
"""

from datetime import datetime, timedelta
from typing import Optional
import bcrypt
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from .. import config
from ..schemas.user import UserInToken

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证明文密码与哈希密码是否匹配
    bcrypt限制密码长度不能超过72字节，需要截断
    """
    try:
        # bcrypt 限制密码长度 72 字节
        password_bytes = plain_password[:72].encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """生成密码哈希
    bcrypt限制密码长度不能超过72字节，需要截断
    """
    # bcrypt 限制密码长度 72 字节
    password_bytes = password[:72].encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def create_access_token(user_id: int, username: str, role: str, expires_delta: Optional[timedelta] = None) -> str:
    """
    创建JWT访问令牌
    
    Args:
        user_id: 用户ID
        username: 用户名
        role: 用户角色
        expires_delta: 过期时间，默认使用配置值
    
    Returns:
        JWT Token字符串
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {
        "sub": str(user_id),
        "username": username,
        "role": role,
        "exp": expire,
        "iat": datetime.utcnow(),
    }
    
    encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> UserInToken:
    """
    解码JWT Token
    
    Args:
        token: JWT Token字符串
    
    Returns:
        UserInToken: 用户信息
    
    Raises:
        HTTPException: Token无效或过期
    """
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        user_id = int(payload.get("sub"))
        username = payload.get("username")
        role = payload.get("role")
        
        if user_id is None or username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的认证令牌"
            )
        
        return UserInToken(id=user_id, username=username, role=role)
    
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="认证令牌已过期或无效"
        )


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends()) -> "User":
    """
    获取当前登录用户（依赖注入使用）
    验证JWT Token并返回用户对象
    
    注意：此函数使用延迟导入避免循环依赖
    """
    from ..database import get_db
    from ..models.user import User
    
    # 获取数据库会话
    if db is None:
        db = next(get_db())
    
    token_data = decode_token(token)
    user = db.query(User).filter(User.id == token_data.id).first()
    if not user or user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在或已被禁用"
        )
    return user
