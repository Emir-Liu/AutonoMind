"""进化引擎接口定义

定义进化引擎的抽象接口
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List


class IEvolutionEngine(ABC):
    """进化引擎接口

    职责: 分析智能体行为并触发进化
    """

    @abstractmethod
    async def check_evolution_trigger(
        self,
        session_id: int,
        performance_metrics: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """检查是否触发进化

        Args:
            session_id: 会话ID
            performance_metrics: 性能指标

        Returns:
            Optional[Dict]: 需要进化的信息，不需要进化返回None
            {
                "type": "learning",
                "reason": "触发原因",
                "priority": "high"
            }
        """
        pass

    @abstractmethod
    async def trigger_evolution(
        self,
        agent_id: str,
        evolution_type: str,
        trigger_reason: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """触发进化

        Args:
            agent_id: 智能体ID
            evolution_type: 进化类型
            trigger_reason: 触发原因
            context: 上下文信息

        Returns:
            Dict: {
                "success": True,
                "changes": {"变更": "详情"},
                "record_id": 123
            }
        """
        pass

    @abstractmethod
    async def get_evolution_history(
        self,
        agent_id: str,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """获取进化历史

        Args:
            agent_id: 智能体ID
            limit: 限制数量

        Returns:
            List[Dict]: 进化历史列表
        """
        pass

    @abstractmethod
    async def rollback_evolution(
        self,
        evolution_record_id: int,
    ) -> bool:
        """回滚进化

        Args:
            evolution_record_id: 进化记录ID

        Returns:
            bool: 成功返回True
        """
        pass
