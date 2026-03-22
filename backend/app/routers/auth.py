"""
认证路由
处理用户登录、登出、Token刷新
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from ..database import get_db
from ..models.user import User
from ..core.security import verify_password, create_access_token, decode_token
from ..schemas.user import UserLogin, UserResponse

router = APIRouter(prefix="/api/auth", tags=["认证"])

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    获取当前登录用户（依赖注入使用）
    验证JWT Token并返回用户对象
    """
    token_data = decode_token(token)
    user = db.query(User).filter(User.id == token_data.id).first()
    if not user or user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在或已被禁用"
        )
    return user


@router.post("/login", response_model=dict)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    用户登录
    - 验证用户名密码
    - 生成JWT Token
    """
    # 查找用户
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    # 验证密码
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    # 生成Token
    access_token = create_access_token(
        user_id=user.id,
        username=user.username,
        role=user.role.value
    )
    
    return {
        "code": 0,
        "data": {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": 7200,  # 2小时
            "user": {
                "id": user.id,
                "username": user.username,
                "real_name": user.real_name,
                "role": user.role.value
            }
        }
    }


@router.get("/me", response_model=dict)
def get_me(current_user: User = Depends(get_current_user)):
    """
    获取当前登录用户信息
    """
    return {
        "code": 0,
        "data": {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "real_name": current_user.real_name,
            "role": current_user.role.value,
            "department": current_user.department
        }
    }


@router.post("/logout", response_model=dict)
def logout():
    """
    用户登出（前端清除Token即可）
    """
    return {"code": 0, "message": "登出成功"}
