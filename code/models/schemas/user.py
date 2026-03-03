"""用户相关的Pydantic模型"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """用户基础模型"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    full_name: Optional[str] = Field(None, max_length=100, description="全名")


class UserCreate(UserBase):
    """用户创建模型"""
    password: str = Field(..., min_length=6, max_length=100, description="密码")


class UserUpdate(BaseModel):
    """用户更新模型"""
    full_name: Optional[str] = Field(None, max_length=100)
    avatar_url: Optional[str] = Field(None, max_length=500)


class UserResponse(UserBase):
    """用户响应模型"""
    id: int
    status: str
    is_superuser: bool
    avatar_url: Optional[str]
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime]

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """用户登录模型"""
    username: str = Field(..., description="用户名或邮箱")
    password: str = Field(..., description="密码")


class TokenResponse(BaseModel):
    """Token响应模型"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


__all__ = [
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserLogin",
    "TokenResponse",
]
