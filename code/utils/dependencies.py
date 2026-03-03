"""依赖注入模块

提供认证依赖、权限依赖等FastAPI依赖注入功能
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from utils.auth import verify_token
from utils.database import get_db_context
from models.database import User
from utils.logger import logger

# HTTP Bearer认证
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """获取当前用户（仅验证Token，不查询数据库）

    Args:
        credentials: HTTP认证凭证

    Returns:
        dict: Token payload

    Raises:
        HTTPException: Token无效时抛出401
    """
    token = credentials.credentials

    # 验证Token
    payload = verify_token(token, token_type="access")

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload


async def get_current_user_from_db(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> User:
    """获取当前用户（从数据库查询完整用户信息）

    Args:
        credentials: HTTP认证凭证

    Returns:
        User: 用户对象

    Raises:
        HTTPException: Token无效或用户不存在时抛出401
    """
    token = credentials.credentials

    # 验证Token
    payload = verify_token(token, token_type="access")

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 获取用户ID
    user_id = payload.get("sub")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing user ID",
        )

    # 从数据库查询用户
    async with get_db_context() as db:
        from sqlalchemy import select

        result = await db.execute(select(User).where(User.id == int(user_id)))
        user = result.scalar_one_or_none()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )

        return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user_from_db),
) -> User:
    """获取当前活跃用户

    Args:
        current_user: 当前用户

    Returns:
        User: 用户对象

    Raises:
        HTTPException: 用户未激活或被封禁时抛出403
    """
    from models.database import UserStatus

    if current_user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is not active",
        )

    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_user_from_db),
) -> User:
    """获取当前超级用户

    Args:
        current_user: 当前用户

    Returns:
        User: 用户对象

    Raises:
        HTTPException: 用户不是超级用户时抛出403
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    return current_user


__all__ = [
    "get_current_user",
    "get_current_user_from_db",
    "get_current_active_user",
    "get_current_superuser",
]
