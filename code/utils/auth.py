"""认证和授权工具模块

提供JWT Token生成和验证、密码哈希、依赖注入等功能
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext

from config import settings
from utils.logger import logger

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码

    Args:
        plain_password: 明文密码
        hashed_password: 哈希密码

    Returns:
        bool: 密码正确返回True
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """获取密码哈希

    Args:
        password: 明文密码

    Returns:
        str: 哈希后的密码
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建访问Token

    Args:
        data: 要编码的数据
        expires_delta: 过期时间增量

    Returns:
        str: JWT Token
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "type": "access"})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """创建刷新Token

    Args:
        data: 要编码的数据

    Returns:
        str: JWT Token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({"exp": expire, "type": "refresh"})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """解码Token

    Args:
        token: JWT Token

    Returns:
        Optional[dict]: 解码后的数据，失败返回None
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except JWTError as e:
        logger.warning(f"Token decode failed: {e}")
        return None


def verify_token(token: str, token_type: str = "access") -> Optional[dict]:
    """验证Token

    Args:
        token: JWT Token
        token_type: Token类型 (access 或 refresh)

    Returns:
        Optional[dict]: 验证成功返回payload，失败返回None
    """
    payload = decode_token(token)

    if payload is None:
        return None

    # 检查Token类型
    if payload.get("type") != token_type:
        logger.warning(f"Token type mismatch: expected {token_type}, got {payload.get('type')}")
        return None

    return payload


__all__ = [
    "verify_password",
    "get_password_hash",
    "create_access_token",
    "create_refresh_token",
    "decode_token",
    "verify_token",
]
