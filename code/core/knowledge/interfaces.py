"""知识检索接口定义

定义知识检索器的抽象接口
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class IKnowledgeRetriever(ABC):
    """知识检索器接口

    职责: 从知识库中检索相关知识
    """

    @abstractmethod
    async def retrieve_knowledge(
        self,
        query: str,
        user_id: int,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """检索相关知识

        Args:
            query: 查询文本
            user_id: 用户ID
            top_k: 返回结果数量
            filters: 过滤条件

        Returns:
            List[Dict]: 知识列表
            [{
                "id": 1,
                "title": "知识标题",
                "content": "知识内容",
                "score": 0.95,
                "metadata": {}
            }]
        """
        pass

    @abstractmethod
    async def add_knowledge(
        self,
        knowledge_id: int,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """添加知识到向量数据库

        Args:
            knowledge_id: 知识ID
            content: 知识内容
            metadata: 元数据

        Returns:
            bool: 成功返回True
        """
        pass

    @abstractmethod
    async def delete_knowledge(self, knowledge_id: int) -> bool:
        """从向量数据库删除知识

        Args:
            knowledge_id: 知识ID

        Returns:
            bool: 成功返回True
        """
        pass

    @abstractmethod
    async def update_knowledge(
        self,
        knowledge_id: int,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """更新向量数据库中的知识

        Args:
            knowledge_id: 知识ID
            content: 新内容
            metadata: 新元数据

        Returns:
            bool: 成功返回True
        """
        pass
