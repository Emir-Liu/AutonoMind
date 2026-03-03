"""数据库工具模块

提供数据库连接、会话管理、初始化等功能
"""

from typing import AsyncGenerator
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool

from config import settings
from models.database import Base

# 创建异步引擎
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # 开发环境打印SQL
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_recycle=settings.DB_POOL_RECYCLE,
    pool_pre_ping=True,  # 连接前检测
)

# 创建异步会话工厂
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # 提交后不过期
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话（依赖注入用）

    Args:
        Yield: AsyncSession

    Example:
        ```python
        @app.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(User))
            return result.scalars().all()
        ```
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_db_context() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话上下文管理器（手动管理用）

    Args:
        Yield: AsyncSession

    Example:
        ```python
        async with get_db_context() as db:
            user = User(username="test", email="test@example.com")
            db.add(user)
            await db.commit()
        ```
    """
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """初始化数据库表

    注意: 生产环境应使用Alembic迁移
    """
    async with engine.begin() as conn:
        # 创建所有表
        await conn.run_sync(Base.metadata.create_all)


async def drop_db() -> None:
    """删除所有表（危险操作，仅用于开发测试）

    注意: 生产环境严禁使用
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def check_db_connection() -> bool:
    """检查数据库连接

    Returns:
        bool: 连接成功返回True
    """
    try:
        async with engine.begin() as conn:
            await conn.execute("SELECT 1")
        return True
    except Exception:
        return False


async def close_db() -> None:
    """关闭数据库连接"""
    await engine.dispose()


__all__ = [
    "engine",
    "async_session_maker",
    "get_db",
    "get_db_context",
    "init_db",
    "drop_db",
    "check_db_connection",
    "close_db",
]
