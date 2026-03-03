"""知识检索服务

封装知识检索的业务逻辑
"""

from typing import List, Dict, Any, Optional

from core.knowledge.retriever import KnowledgeRetriever, RetrievalStrategy
from core.embedding import EmbeddingService, QdrantVectorStore
from utils.logger import logger


class RetrievalService:
    """知识检索服务"""

    def __init__(
        self,
        embedding_service: EmbeddingService,
        vector_store: QdrantVectorStore,
        db_session,
    ):
        self.retriever = KnowledgeRetriever(
            embedding_service=embedding_service,
            vector_store=vector_store,
            db_session=db_session,
        )

    async def search_knowledge(
        self,
        query: str,
        user_id: int,
        top_k: int = 5,
        strategy: str = "vector",
        filters: Optional[Dict[str, Any]] = None,
        rerank: bool = True,
    ) -> Dict[str, Any]:
        """检索知识

        Args:
            query: 查询文本
            user_id: 用户ID
            top_k: 返回结果数量
            strategy: 检索策略 (vector/keyword/hybrid)
            filters: 过滤条件
            rerank: 是否重排序

        Returns:
            Dict: 检索结果
            {
                "success": True,
                "results": [...],
                "total": 5,
                "strategy": "vector"
            }
        """
        try:
            # 验证策略
            if strategy not in ["vector", "keyword", "hybrid"]:
                strategy = "vector"

            # 执行检索
            results = await self.retriever.retrieve_knowledge(
                query=query,
                user_id=user_id,
                top_k=top_k,
                filters=filters,
                strategy=RetrievalStrategy(strategy),
                rerank=rerank,
            )

            logger.info(f"知识检索成功: {len(results)} 条")

            return {
                "success": True,
                "results": results,
                "total": len(results),
                "strategy": strategy,
            }

        except Exception as e:
            logger.error(f"知识检索失败: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "results": [],
                "total": 0,
                "strategy": strategy,
            }

    async def add_knowledge_vectors(
        self,
        knowledge_id: int,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """添加知识向量

        Args:
            knowledge_id: 知识ID
            content: 知识内容
            metadata: 元数据

        Returns:
            Dict: 操作结果
        """
        try:
            success = await self.retriever.add_knowledge(
                knowledge_id=knowledge_id,
                content=content,
                metadata=metadata,
            )

            return {
                "success": success,
                "knowledge_id": knowledge_id,
                "message": "知识向量添加成功" if success else "知识向量添加失败",
            }

        except Exception as e:
            logger.error(f"添加知识向量失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "knowledge_id": knowledge_id,
            }

    async def delete_knowledge_vectors(
        self,
        knowledge_id: int,
    ) -> Dict[str, Any]:
        """删除知识向量

        Args:
            knowledge_id: 知识ID

        Returns:
            Dict: 操作结果
        """
        try:
            success = await self.retriever.delete_knowledge(
                knowledge_id=knowledge_id,
            )

            return {
                "success": success,
                "knowledge_id": knowledge_id,
                "message": "知识向量删除成功" if success else "知识向量删除失败",
            }

        except Exception as e:
            logger.error(f"删除知识向量失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "knowledge_id": knowledge_id,
            }

    async def update_knowledge_vectors(
        self,
        knowledge_id: int,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """更新知识向量

        Args:
            knowledge_id: 知识ID
            content: 新内容
            metadata: 新元数据

        Returns:
            Dict: 操作结果
        """
        try:
            success = await self.retriever.update_knowledge(
                knowledge_id=knowledge_id,
                content=content,
                metadata=metadata,
            )

            return {
                "success": success,
                "knowledge_id": knowledge_id,
                "message": "知识向量更新成功" if success else "知识向量更新失败",
            }

        except Exception as e:
            logger.error(f"更新知识向量失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "knowledge_id": knowledge_id,
            }

    async def get_retrieval_statistics(
        self,
        user_id: int,
        days: int = 30,
    ) -> Dict[str, Any]:
        """获取检索统计

        Args:
            user_id: 用户ID
            days: 统计天数

        Returns:
            Dict: 统计信息
        """
        try:
            # TODO: 实现统计查询
            return {
                "total_queries": 0,
                "avg_results": 0,
                "strategy_usage": {
                    "vector": 0,
                    "keyword": 0,
                    "hybrid": 0,
                },
            }
        except Exception as e:
            logger.error(f"获取检索统计失败: {e}")
            return {}
