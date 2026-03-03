"""智能体编排器接口定义

定义智能体编排器的抽象接口
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime


class IAgentOrchestrator(ABC):
    """智能体编排器接口

    职责: 协调智能体执行对话流程
    """

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    async def clear_conversation_history(self, session_id: int) -> bool:
        """清空对话历史

        Args:
            session_id: 会话ID

        Returns:
            bool: 成功返回True
        """
        pass
