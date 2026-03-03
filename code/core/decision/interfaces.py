"""决策引擎接口定义

定义决策引擎的抽象接口
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class IDecisionEngine(ABC):
    """决策引擎接口

    职责: 根据上下文和知识做出决策
    """

    @abstractmethod
    async def make_decision(
        self,
        context: Dict[str, Any],
        available_actions: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """做出决策

        Args:
            context: 上下文信息
            available_actions: 可用操作列表

        Returns:
            Dict: {
                "action": "选择的操作",
                "parameters": {"参数": "值"},
                "reasoning": "决策原因",
                "confidence": 0.95
            }
        """
        pass

    @abstractmethod
    async def evaluate_decision(
        self,
        decision: Dict[str, Any],
        outcome: Dict[str, Any],
    ) -> Dict[str, Any]:
        """评估决策效果

        Args:
            decision: 决策
            outcome: 结果

        Returns:
            Dict: {
                "success": True,
                "score": 0.9,
                "feedback": "反馈信息"
            }
        """
        pass
