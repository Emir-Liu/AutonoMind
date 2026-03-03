"""Qdrant向量数据库客户端

提供向量存储和检索功能
"""

from typing import List, Optional, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    SearchRequest,
    FilterSelector,
)

from config import settings
from utils.logger import logger


class QdrantVectorStore:
    """Qdrant向量存储类"""

    def __init__(self):
        """初始化Qdrant客户端"""
        self.client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
        )
        self.collection_prefix = settings.QDRANT_COLLECTION_PREFIX
        self.dimension = settings.EMBEDDING_DIMENSION

    def get_collection_name(self, user_id: int) -> str:
        """获取用户集合名称

        Args:
            user_id: 用户ID

        Returns:
            str: 集合名称
        """
        return f"{self.collection_prefix}_user_{user_id}"

    async def create_collection(self, user_id: int) -> bool:
        """创建用户集合

        Args:
            user_id: 用户ID

        Returns:
            bool: 创建成功返回True
        """
        collection_name = self.get_collection_name(user_id)

        try:
            # 检查集合是否已存在
            if self.client.collection_exists(collection_name):
                logger.info(f"Collection {collection_name} already exists")
                return True

            # 创建集合
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=self.dimension,
                    distance=Distance.COSINE,
                ),
            )

            logger.info(f"Created collection: {collection_name}")
            return True

        except Exception as e:
            logger.error(f"Create collection failed: {e}")
            return False

    async def delete_collection(self, user_id: int) -> bool:
        """删除用户集合

        Args:
            user_id: 用户ID

        Returns:
            bool: 删除成功返回True
        """
        collection_name = self.get_collection_name(user_id)

        try:
            if self.client.collection_exists(collection_name):
                self.client.delete_collection(collection_name)
                logger.info(f"Deleted collection: {collection_name}")
            return True

        except Exception as e:
            logger.error(f"Delete collection failed: {e}")
            return False

    async def upsert_points(
        self,
        user_id: int,
        points: List[PointStruct],
    ) -> bool:
        """插入或更新向量点

        Args:
            user_id: 用户ID
            points: 向量点列表

        Returns:
            bool: 成功返回True
        """
        collection_name = self.get_collection_name(user_id)

        try:
            # 确保集合存在
            await self.create_collection(user_id)

            # 插入点
            self.client.upsert(
                collection_name=collection_name,
                points=points,
            )

            logger.info(f"Upserted {len(points)} points to {collection_name}")
            return True

        except Exception as e:
            logger.error(f"Upsert points failed: {e}")
            return False

    async def delete_points(
        self,
        user_id: int,
        point_ids: List[str],
    ) -> bool:
        """删除向量点

        Args:
            user_id: 用户ID
            point_ids: 向量点ID列表

        Returns:
            bool: 成功返回True
        """
        collection_name = self.get_collection_name(user_id)

        try:
            self.client.delete(
                collection_name=collection_name,
                points_selector=point_ids,
            )

            logger.info(f"Deleted {len(point_ids)} points from {collection_name}")
            return True

        except Exception as e:
            logger.error(f"Delete points failed: {e}")
            return False

    async def search(
        self,
        user_id: int,
        query_vector: List[float],
        top_k: int = 5,
        score_threshold: float = 0.5,
        filter_conditions: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """向量搜索

        Args:
            user_id: 用户ID
            query_vector: 查询向量
            top_k: 返回结果数量
            score_threshold: 相似度阈值
            filter_conditions: 过滤条件

        Returns:
            List[Dict]: 搜索结果列表
        """
        collection_name = self.get_collection_name(user_id)

        try:
            # 构建过滤器
            query_filter = None
            if filter_conditions:
                conditions = [
                    FieldCondition(
                        key=key,
                        match=MatchValue(value=value),
                    )
                    for key, value in filter_conditions.items()
                ]
                query_filter = Filter(must=conditions)

            # 执行搜索
            search_results = self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=top_k,
                score_threshold=score_threshold,
                query_filter=query_filter,
            )

            # 转换结果格式
            results = []
            for result in search_results:
                results.append({
                    "id": result.id,
                    "score": result.score,
                    "payload": result.payload or {},
                })

            logger.info(f"Found {len(results)} results in {collection_name}")
            return results

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    async def get_collection_info(self, user_id: int) -> Optional[Dict[str, Any]]:
        """获取集合信息

        Args:
            user_id: 用户ID

        Returns:
            Optional[Dict]: 集合信息，不存在返回None
        """
        collection_name = self.get_collection_name(user_id)

        try:
            if not self.client.collection_exists(collection_name):
                return None

            info = self.client.get_collection(collection_name)

            return {
                "name": collection_name,
                "points_count": info.points_count,
                "vectors_count": info.vectors_count,
                "status": info.status,
            }

        except Exception as e:
            logger.error(f"Get collection info failed: {e}")
            return None


# 全局Qdrant客户端实例
qdrant_store = QdrantVectorStore()


__all__ = [
    "QdrantVectorStore",
    "qdrant_store",
]
