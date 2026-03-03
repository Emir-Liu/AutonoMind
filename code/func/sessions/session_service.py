"""会话服务模块

提供会话创建、消息发送、历史查询等业务逻辑
"""

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime

from models.database import Session, Message
from models.schemas.session import SessionCreate, MessageCreate
from utils.logger import logger


class SessionService:
    """会话服务类"""

    @staticmethod
    async def create_session(
        db: AsyncSession,
        user_id: int,
        session_data: SessionCreate,
    ) -> Session:
        """创建会话

        Args:
            db: 数据库会话
            user_id: 用户ID
            session_data: 会话数据

        Returns:
            Session: 创建的会话对象
        """
        session = Session(
            user_id=user_id,
            title=session_data.title,
            agent_id=session_data.agent_id,
            status="active",
            message_count=0,
        )

        db.add(session)
        await db.commit()
        await db.refresh(session)

        logger.info(f"Session created: {session.id}")
        return session

    @staticmethod
    async def get_session(
        db: AsyncSession,
        session_id: int,
        user_id: int,
    ) -> Optional[Session]:
        """获取会话

        Args:
            db: 数据库会话
            session_id: 会话ID
            user_id: 用户ID

        Returns:
            Optional[Session]: 会话对象，不存在或无权访问返回None
        """
        result = await db.execute(
            select(Session).where(
                Session.id == session_id,
                Session.user_id == user_id,
                Session.status != "deleted",
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_sessions(
        db: AsyncSession,
        user_id: int,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[List[Session], int]:
        """列出用户的会话

        Args:
            db: 数据库会话
            user_id: 用户ID
            status: 过滤状态
            limit: 返回数量限制
            offset: 偏移量

        Returns:
            tuple: (会话列表, 总数)
        """
        # 构建查询
        query = select(Session).where(
            Session.user_id == user_id,
            Session.status != "deleted",
        )

        if status:
            query = query.where(Session.status == status)

        # 获取总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # 获取会话列表
        query = query.order_by(Session.updated_at.desc())
        query = query.limit(limit).offset(offset)
        result = await db.execute(query)
        sessions = result.scalars().all()

        return list(sessions), total

    @staticmethod
    async def add_message(
        db: AsyncSession,
        session_id: int,
        message_data: MessageCreate,
        tokens: Optional[dict] = None,
        execution_time_ms: Optional[int] = None,
    ) -> Message:
        """添加消息到会话

        Args:
            db: 数据库会话
            session_id: 会话ID
            message_data: 消息数据
            tokens: Token统计
            execution_time_ms: 执行耗时

        Returns:
            Message: 创建的消息对象
        """
        message = Message(
            session_id=session_id,
            role=message_data.role,
            content=message_data.content,
            prompt_tokens=tokens.get("prompt_tokens") if tokens else None,
            completion_tokens=tokens.get("completion_tokens") if tokens else None,
            total_tokens=tokens.get("total_tokens") if tokens else None,
            execution_time_ms=execution_time_ms,
        )

        db.add(message)

        # 更新会话消息计数和更新时间
        session = await db.get(Session, session_id)
        if session:
            session.message_count += 1
            session.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(message)

        logger.info(f"Message added to session {session_id}")
        return message

    @staticmethod
    async def get_messages(
        db: AsyncSession,
        session_id: int,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Message]:
        """获取会话的消息历史

        Args:
            db: 数据库会话
            session_id: 会话ID
            limit: 返回数量限制
            offset: 偏移量

        Returns:
            List[Message]: 消息列表
        """
        query = select(Message).where(
            Message.session_id == session_id,
        ).order_by(Message.created_at.asc())

        query = query.limit(limit).offset(offset)
        result = await db.execute(query)
        messages = result.scalars().all()

        return list(messages)

    @staticmethod
    async def update_session(
        db: AsyncSession,
        session_id: int,
        user_id: int,
        title: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Session:
        """更新会话

        Args:
            db: 数据库会话
            session_id: 会话ID
            user_id: 用户ID
            title: 新标题
            status: 新状态

        Returns:
            Session: 更新后的会话对象

        Raises:
            ValueError: 会话不存在
        """
        session = await SessionService.get_session(db, session_id, user_id)

        if not session:
            raise ValueError(f"Session {session_id} not found")

        if title is not None:
            session.title = title
        if status is not None:
            session.status = status
            if status == "archived":
                session.archived_at = datetime.utcnow()

        session.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(session)

        logger.info(f"Session updated: {session_id}")
        return session

    @staticmethod
    async def delete_session(
        db: AsyncSession,
        session_id: int,
        user_id: int,
    ) -> bool:
        """删除会话（软删除）

        Args:
            db: 数据库会话
            session_id: 会话ID
            user_id: 用户ID

        Returns:
            bool: 删除成功返回True

        Raises:
            ValueError: 会话不存在
        """
        session = await SessionService.get_session(db, session_id, user_id)

        if not session:
            raise ValueError(f"Session {session_id} not found")

        session.status = "deleted"
        session.updated_at = datetime.utcnow()

        await db.commit()

        logger.info(f"Session deleted: {session_id}")
        return True


__all__ = ["SessionService"]
