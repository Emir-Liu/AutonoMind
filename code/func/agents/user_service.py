"""用户服务模块

提供用户注册、登录、信息管理等业务逻辑
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.database import User, UserStatus
from models.schemas.user import UserCreate, UserUpdate
from utils.auth import get_password_hash, verify_password
from utils.auth import create_access_token, create_refresh_token
from utils.logger import logger


class UserService:
    """用户服务类"""

    @staticmethod
    async def create_user(
        db: AsyncSession,
        user_data: UserCreate,
    ) -> User:
        """创建用户

        Args:
            db: 数据库会话
            user_data: 用户创建数据

        Returns:
            User: 创建的用户对象

        Raises:
            ValueError: 用户名或邮箱已存在
        """
        # 检查用户名是否已存在
        result = await db.execute(
            select(User).where(User.username == user_data.username)
        )
        if result.scalar_one_or_none():
            raise ValueError(f"Username '{user_data.username}' already exists")

        # 检查邮箱是否已存在
        result = await db.execute(
            select(User).where(User.email == user_data.email)
        )
        if result.scalar_one_or_none():
            raise ValueError(f"Email '{user_data.email}' already exists")

        # 创建用户
        user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=get_password_hash(user_data.password),
            full_name=user_data.full_name,
            status=UserStatus.ACTIVE,
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)

        logger.info(f"User created: {user.username}")
        return user

    @staticmethod
    async def authenticate_user(
        db: AsyncSession,
        username: str,
        password: str,
    ) -> Optional[User]:
        """验证用户登录

        Args:
            db: 数据库会话
            username: 用户名或邮箱
            password: 密码

        Returns:
            Optional[User]: 验证成功返回用户对象，失败返回None
        """
        # 查询用户（支持用户名或邮箱登录）
        result = await db.execute(
            select(User).where(
                (User.username == username) | (User.email == username)
            )
        )
        user = result.scalar_one_or_none()

        # 验证密码
        if not user or not verify_password(password, user.hashed_password):
            return None

        # 更新最后登录时间
        from datetime import datetime
        from sqlalchemy import update

        await db.execute(
            update(User)
            .where(User.id == user.id)
            .values(last_login_at=datetime.utcnow())
        )
        await db.commit()

        logger.info(f"User authenticated: {user.username}")
        return user

    @staticmethod
    async def get_user_by_id(
        db: AsyncSession,
        user_id: int,
    ) -> Optional[User]:
        """根据ID获取用户

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            Optional[User]: 用户对象，不存在返回None
        """
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def update_user(
        db: AsyncSession,
        user_id: int,
        user_data: UserUpdate,
    ) -> User:
        """更新用户信息

        Args:
            db: 数据库会话
            user_id: 用户ID
            user_data: 用户更新数据

        Returns:
            User: 更新后的用户对象

        Raises:
            ValueError: 用户不存在
        """
        user = await UserService.get_user_by_id(db, user_id)

        if not user:
            raise ValueError(f"User with id {user_id} not found")

        # 更新字段
        if user_data.full_name is not None:
            user.full_name = user_data.full_name
        if user_data.avatar_url is not None:
            user.avatar_url = user_data.avatar_url

        await db.commit()
        await db.refresh(user)

        logger.info(f"User updated: {user.username}")
        return user

    @staticmethod
    async def delete_user(
        db: AsyncSession,
        user_id: int,
    ) -> bool:
        """删除用户（软删除，设置为INACTIVE状态）

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            bool: 删除成功返回True

        Raises:
            ValueError: 用户不存在
        """
        user = await UserService.get_user_by_id(db, user_id)

        if not user:
            raise ValueError(f"User with id {user_id} not found")

        # 软删除
        user.status = UserStatus.INACTIVE
        await db.commit()

        logger.info(f"User deleted: {user.username}")
        return True

    @staticmethod
    async def login_user(
        db: AsyncSession,
        username: str,
        password: str,
    ) -> dict:
        """用户登录

        Args:
            db: 数据库会话
            username: 用户名或邮箱
            password: 密码

        Returns:
            dict: {
                "access_token": "xxx",
                "refresh_token": "xxx",
                "token_type": "bearer",
                "user": User对象
            }

        Raises:
            ValueError: 用户名或密码错误
        """
        # 验证用户
        user = await UserService.authenticate_user(db, username, password)

        if not user:
            raise ValueError("Incorrect username or password")

        # 生成Token
        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": user,
        }


__all__ = ["UserService"]
