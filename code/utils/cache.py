"""Redis缓存工具模块

提供Redis连接、缓存操作等功能
"""

import json
from typing import Optional, Any
import redis.asyncio as redis

from config import settings

# 创建Redis连接池
redis_pool = redis.ConnectionPool.from_url(
    settings.REDIS_URL,
    max_connections=settings.REDIS_MAX_CONNECTIONS,
    decode_responses=True,
)

# 创建Redis客户端
redis_client = redis.Redis(connection_pool=redis_pool)


async def get_cache(key: str) -> Optional[Any]:
    """获取缓存

    Args:
        key: 缓存键

    Returns:
        缓存值，不存在返回None

    Example:
        ```python
        user = await get_cache("user:123")
        ```
    """
    value = await redis_client.get(key)
    if value is None:
        return None

    # 尝试解析JSON
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return value


async def set_cache(
    key: str,
    value: Any,
    expire: Optional[int] = None,
) -> bool:
    """设置缓存

    Args:
        key: 缓存键
        value: 缓存值
        expire: 过期时间(秒)，None表示永不过期

    Returns:
        bool: 设置成功返回True

    Example:
        ```python
        await set_cache("user:123", {"name": "Alice"}, expire=3600)
        ```
    """
    # 序列化值
    if isinstance(value, (dict, list)):
        value = json.dumps(value, ensure_ascii=False)

    return await redis_client.set(key, value, ex=expire)


async def delete_cache(key: str) -> bool:
    """删除缓存

    Args:
        key: 缓存键

    Returns:
        bool: 删除成功返回True

    Example:
        ```python
        await delete_cache("user:123")
        ```
    """
    return await redis_client.delete(key) > 0


async def delete_cache_pattern(pattern: str) -> int:
    """批量删除匹配模式的缓存

    Args:
        pattern: 匹配模式，如 "user:*"

    Returns:
        int: 删除的键数量

    Example:
        ```python
        count = await delete_cache_pattern("user:*")
        ```
    """
    keys = []
    async for key in redis_client.scan_iter(match=pattern):
        keys.append(key)

    if keys:
        return await redis_client.delete(*keys)
    return 0


async def exists_cache(key: str) -> bool:
    """检查缓存是否存在

    Args:
        key: 缓存键

    Returns:
        bool: 存在返回True

    Example:
        ```python
        if await exists_cache("user:123"):
            print("缓存存在")
        ```
    """
    return await redis_client.exists(key) > 0


async def expire_cache(key: str, seconds: int) -> bool:
    """设置缓存过期时间

    Args:
        key: 缓存键
        seconds: 过期秒数

    Returns:
        bool: 设置成功返回True

    Example:
        ```python
        await expire_cache("user:123", 3600)
        ```
    """
    return await redis_client.expire(key, seconds)


async def get_cache_ttl(key: str) -> int:
    """获取缓存剩余过期时间

    Args:
        key: 缓存键

    Returns:
        int: 剩余秒数，-1表示永不过期，-2表示不存在

    Example:
        ```python
        ttl = await get_cache_ttl("user:123")
        ```
    """
    return await redis_client.ttl(key)


async def incr_cache(key: str, amount: int = 1) -> int:
    """递增缓存值（计数器）

    Args:
        key: 缓存键
        amount: 递增量，默认1

    Returns:
        int: 递增后的值

    Example:
        ```python
        count = await incr_cache("api_calls:123")
        ```
    """
    return await redis_client.incrby(key, amount)


async def check_redis_connection() -> bool:
    """检查Redis连接

    Returns:
        bool: 连接成功返回True
    """
    try:
        await redis_client.ping()
        return True
    except Exception:
        return False


async def close_redis() -> None:
    """关闭Redis连接"""
    await redis_client.close()


__all__ = [
    "redis_client",
    "get_cache",
    "set_cache",
    "delete_cache",
    "delete_cache_pattern",
    "exists_cache",
    "expire_cache",
    "get_cache_ttl",
    "incr_cache",
    "check_redis_connection",
    "close_redis",
]
