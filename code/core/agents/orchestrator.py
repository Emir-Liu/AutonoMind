"""智能体编排器实现

实现对话流程编排、工具调用等核心功能
"""

import time
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession

from core.agents.interfaces import IAgentOrchestrator
from utils.llm import LLMManager, TokenUsageCallback
from utils.logger import logger
from config import settings


class AgentOrchestrator(IAgentOrchestrator):
    """智能体编排器实现"""

    def __init__(self):
        self.llm_manager = LLMManager()

    async def execute_conversation(
        self,
        session_id: int,
        user_message: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """执行对话流程

        Args:
            session_id: 会话ID
            user_message: 用户消息
            context: 上下文信息

        Returns:
            Dict: {
                "response": "智能体回复",
                "actions": ["执行的操作"],
                "knowledge_used": ["使用的知识"],
                "tokens": {"prompt": 100, "completion": 200, "total": 300},
                "execution_time_ms": 1500
            }
        """
        start_time = time.time()

        try:
            # 1. 获取会话历史
            conversation_history = await self.get_conversation_history(session_id, limit=10)

            # 2. 构建消息列表
            messages = self._build_messages(user_message, conversation_history)

            # 3. 创建Token统计回调
            token_callback = TokenUsageCallback()

            # 4. 调用LLM生成回复
            from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

            # 转换为LangChain消息格式
            langchain_messages = []
            for msg in messages:
                if msg["role"] == "system":
                    langchain_messages.append(SystemMessage(content=msg["content"]))
                elif msg["role"] == "user":
                    langchain_messages.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    langchain_messages.append(AIMessage(content=msg["content"]))

            # 生成回复
            response = await self.llm_manager.generate_response(
                langchain_messages,
                callbacks=[token_callback],
            )

            # 5. 计算执行时间
            execution_time_ms = int((time.time() - start_time) * 1000)

            # 6. 返回结果
            result = {
                "response": response,
                "actions": [],  # TODO: 实现工具调用
                "knowledge_used": [],  # TODO: 实现知识检索
                "tokens": token_callback.get_stats(),
                "execution_time_ms": execution_time_ms,
            }

            logger.info(f"Conversation executed for session {session_id}")
            return result

        except Exception as e:
            logger.error(f"Execute conversation failed: {e}")
            raise

    async def get_conversation_history(
        self,
        session_id: int,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """获取对话历史

        Args:
            session_id: 会话ID
            limit: 限制数量

        Returns:
            List[Dict]: 对话历史列表
        """
        from utils.database import get_db_context
        from models.database import Message
        from sqlalchemy import select

        async with get_db_context() as db:
            query = select(Message).where(
                Message.session_id == session_id,
            ).order_by(Message.created_at.asc())

            if limit:
                query = query.limit(limit)

            result = await db.execute(query)
            messages = result.scalars().all()

            # 转换为字典格式
            history = []
            for msg in messages:
                history.append({
                    "role": msg.role,
                    "content": msg.content,
                })

            return history

    async def clear_conversation_history(self, session_id: int) -> bool:
        """清空对话历史

        Args:
            session_id: 会话ID

        Returns:
            bool: 成功返回True
        """
        from utils.database import get_db_context
        from models.database import Message
        from sqlalchemy import delete

        try:
            async with get_db_context() as db:
                await db.execute(
                    delete(Message).where(Message.session_id == session_id)
                )
                await db.commit()

            logger.info(f"Cleared conversation history for session {session_id}")
            return True

        except Exception as e:
            logger.error(f"Clear conversation history failed: {e}")
            return False

    def _build_messages(
        self,
        user_message: str,
        conversation_history: List[Dict[str, Any]],
    ) -> List[Dict[str, str]]:
        """构建消息列表

        Args:
            user_message: 用户消息
            conversation_history: 对话历史

        Returns:
            List[Dict]: 消息列表
        """
        messages = []

        # 添加系统提示
        system_prompt = self._get_system_prompt()
        messages.append({"role": "system", "content": system_prompt})

        # 添加历史消息
        for msg in conversation_history:
            messages.append({
                "role": msg["role"],
                "content": msg["content"],
            })

        # 添加当前用户消息
        messages.append({"role": "user", "content": user_message})

        return messages

    def _get_system_prompt(self) -> str:
        """获取系统提示词

        Returns:
            str: 系统提示词
        """
        return f"""You are a helpful AI assistant in the AutonoMind system.

Your capabilities:
- Answer questions and provide information
- Help users with various tasks
- Maintain context across the conversation

You should:
- Be helpful and friendly
- Provide accurate information
- Ask clarifying questions when needed
- Maintain conversation flow

Remember: You are part of an AI agent system designed to assist users effectively."""


# 全局编排器实例
agent_orchestrator = AgentOrchestrator()


__all__ = ["AgentOrchestrator", "agent_orchestrator"]
