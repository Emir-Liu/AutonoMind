"""工具执行器接口定义

定义工具执行器的抽象接口
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class IToolRunner(ABC):
    """工具执行器接口

    职责: 执行工具操作
    """

    @abstractmethod
    async def execute_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """执行工具

        Args:
            tool_name: 工具名称
            parameters: 工具参数
            context: 上下文信息

        Returns:
            Dict: {
                "success": True,
                "result": "执行结果",
                "error": None
            }
        """
        pass

    @abstractmethod
    async def get_available_tools(self) -> List[Dict[str, Any]]:
        """获取可用工具列表

        Returns:
            List[Dict]: 工具列表
            [{
                "name": "工具名称",
                "description": "工具描述",
                "parameters": {"参数": "参数描述"}
            }]
        """
        pass
