"""对话服务模块

提供对话编排的业务逻辑
"""

from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from models.schemas.session import ConversationRequest, ConversationResponse
from core.agents.orchestrator import agent_orchestrator
from func.sessions.session_service import SessionService, SessionCreate
from models.schemas.session import MessageCreate
from utils.logger import logger


class ConversationService:
    """对话服务类"""

    @staticmethod
    async def create_conversation(
        db: AsyncSession,
        user_id: int,
        request: ConversationRequest,
    ) -> ConversationResponse:
        """创建对话

        Args:
            db: 数据库会话
            user_id: 用户ID
            request: 对话请求

        Returns:
            ConversationResponse: 对话响应
        """
        # 如果未指定会话ID，创建新会话
        session_id = request.session_id
        if session_id is None:
            session = await SessionService.create_session(
                db,
                user_id,
                SessionCreate(
                    title=request.title or "New Conversation",
                    agent_id=request.agent_id,
                )
            )
            session_id = session.id
        else:
            # 验证会话权限
            session = await SessionService.get_session(db, session_id, user_id)
            if not session:
                raise ValueError("Session not found")

        # 添加用户消息
        user_message = await SessionService.add_message(
            db,
            session_id,
            MessageCreate(role="user", content=request.message),
        )

        try:
            # 调用智能体编排器生成回复
            context = {
                "user_id": user_id,
                "agent_id": request.agent_id,
            }

            result = await agent_orchestrator.execute_conversation(
                session_id,
                request.message,
                context,
            )

            # 添加助手回复
            assistant_message = await SessionService.add_message(
                db,
                session_id,
                MessageCreate(
                    role="assistant",
                    content=result["response"],
                ),
                tokens=result.get("tokens"),
                execution_time_ms=result.get("execution_time_ms"),
            )

            return ConversationResponse(
                session_id=session_id,
                message_id=assistant_message.id,
                response=result["response"],
                tokens=result.get("tokens"),
                execution_time_ms=result.get("execution_time_ms"),
            )

        except Exception as e:
            logger.error(f"Conversation execution failed: {e}")
            # 添加错误消息
            error_message = await SessionService.add_message(
                db,
                session_id,
                MessageCreate(
                    role="assistant",
                    content="Sorry, I encountered an error while processing your request. Please try again.",
                ),
            )
            raise


__all__ = ["ConversationService"]
