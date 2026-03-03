"""Qdrant 向量存储服务

实现向量数据的增删改查和相似度搜索
"""

from typing import List, Dict, Any, Optional
from uuid import uuid4

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    SearchParams,
)

from utils.logger import logger
from config import settings


class VectorSearchResult:
    """向量搜索结果"""

    def __init__(
        self,
        id: str,
        score: float,
        payload: Dict[str, Any],
        vector: Optional[List[float]] = None,
    ):
        self.id = id
        self.score = score
        self.payload = payload
        self.vector = vector


class QdrantVectorStore:
    """Qdrant向量存储服务"""

    # 默认集合名称
    DEFAULT_COLLECTION = "knowledge_base"

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        collection_name: str = DEFAULT_COLLECTION,
    ):
        self.host = host or settings.QDRANT_HOST
        self.port = port or settings.QDRANT_PORT
        self.collection_name = collection_name

        # 创建客户端
        self.client = AsyncQdrantClient(
            host=self.host,
            port=self.port,
        )

        logger.info(f"初始化Qdrant客户端: {self.host}:{self.port}, 集合: {self.collection_name}")

    # ========== 集合管理 ==========

    async def create_collection(
        self,
        vector_size: int = 1536,
        recreate: bool = False,
    ) -> bool:
        """创建集合

        Args:
            vector_size: 向量维度
            recreate: 如果集合存在是否重建

        Returns:
            bool: 成功返回True
        """
        try:
            # 检查集合是否存在
            exists = await self.client.collection_exists(self.collection_name)

            if exists:
                if recreate:
                    logger.info(f"删除已存在的集合: {self.collection_name}")
                    await self.client.delete_collection(self.collection_name)
                else:
                    logger.info(f"集合已存在: {self.collection_name}")
                    return True

            # 创建集合
            await self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE,
                ),
            )

            logger.info(f"创建集合成功: {self.collection_name}, 向量维度: {vector_size}")
            return True

        except Exception as e:
            logger.error(f"创建集合失败: {e}")
            raise

    async def delete_collection(self) -> bool:
        """删除集合

        Returns:
            bool: 成功返回True
        """
        try:
            await self.client.delete_collection(self.collection_name)
            logger.info(f"删除集合成功: {self.collection_name}")
            return True

        except Exception as e:
            logger.error(f"删除集合失败: {e}")
            raise

    async def get_collection_info(self) -> Optional[Dict[str, Any]]:
        """获取集合信息

        Returns:
            Optional[Dict]: 集合信息
        """
        try:
            info = await self.client.get_collection(self.collection_name)
            return {
                "name": self.collection_name,
                "vectors_count": info.points_count,
                "status": info.status,
            }
        except Exception as e:
            logger.error(f"获取集合信息失败: {e}")
            return None

    # ========== 向量操作 ==========

    async def upsert_points(
        self,
        points: List[Dict[str, Any]],
    ) -> bool:
        """插入或更新向量点

        Args:
            points: 向量点列表
                [{
                    "id": "knowledge_123",
                    "vector": [...],
                    "payload": {...}
                }]

        Returns:
            bool: 成功返回True
        """
        try:
            qdrant_points = []
            for point in points:
                qdrant_points.append(
                    PointStruct(
                        id=point.get("id", str(uuid4())),
                        vector=point["vector"],
                        payload=point.get("payload", {}),
                    )
                )

            await self.client.upsert(
                collection_name=self.collection_name,
                points=qdrant_points,
            )

            logger.info(f"插入/更新向量点成功: {len(points)} 个")
            return True

        except Exception as e:
            logger.error(f"插入/更新向量点失败: {e}")
            raise

    async def delete_points(
        self,
        point_ids: List[str],
    ) -> bool:
        """删除向量点

        Args:
            point_ids: 点ID列表

        Returns:
            bool: 成功返回True
        """
        try:
            await self.client.delete(
                collection_name=self.collection_name,
                points_selector=point_ids,
            )

            logger.info(f"删除向量点成功: {len(point_ids)} 个")
            return True

        except Exception as e:
            logger.error(f"删除向量点失败: {e}")
            raise

    async def search(
        self,
        query_vector: List[float],
        limit: int = 10,
        score_threshold: Optional[float] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[VectorSearchResult]:
        """向量相似度搜索

        Args:
            query_vector: 查询向量
            limit: 返回结果数量
            score_threshold: 分数阈值
            filters: 过滤条件

        Returns:
            List[VectorSearchResult]: 搜索结果列表
        """
        try:
            # 构建过滤条件
            query_filter = None
            if filters:
                conditions = []
                for key, value in filters.items():
                    conditions.append(
                        FieldCondition(
                            key=key,
                            match=MatchValue(value=value),
                        )
                    )
                query_filter = Filter(must=conditions)

            # 执行搜索
            results = await self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                query_filter=query_filter,
                limit=limit,
                score_threshold=score_threshold,
                with_payload=True,
                with_vectors=False,
            )

            # 转换结果
            search_results = []
            for result in results:
                search_results.append(
                    VectorSearchResult(
                        id=str(result.id),
                        score=result.score,
                        payload=result.payload or {},
                    )
                )

            logger.info(f"向量搜索完成: 返回 {len(search_results)} 个结果")
            return search_results

        except Exception as e:
            logger.error(f"向量搜索失败: {e}")
            raise

    async def search_by_id(
        self,
        knowledge_id: int,
        limit: int = 5,
    ) -> List[VectorSearchResult]:
        """根据知识ID搜索相似向量

        Args:
            knowledge_id: 知识ID
            limit: 返回结果数量

        Returns:
            List[VectorSearchResult]: 搜索结果列表
        """
        try:
            # 先获取该知识ID的向量
            # TODO: 实现根据ID检索的逻辑

            # 临时实现：返回空列表
            return []

        except Exception as e:
            logger.error(f"按ID搜索失败: {e}")
            return []

    # ========== 批量操作 ==========

    async def get_point(
        self,
        point_id: str,
    ) -> Optional[Dict[str, Any]]:
        """获取单个向量点

        Args:
            point_id: 点ID

        Returns:
            Optional[Dict]: 向量点信息
        """
        try:
            results = await self.client.retrieve(
                collection_name=self.collection_name,
                ids=[point_id],
                with_payload=True,
                with_vectors=True,
            )

            if results:
                return {
                    "id": str(results[0].id),
                    "vector": results[0].vector,
                    "payload": results[0].payload,
                }

            return None

        except Exception as e:
            logger.error(f"获取向量点失败: {e}")
            return None

    async def scroll(
        self,
        limit: int = 100,
        offset: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """滚动获取向量点

        Args:
            limit: 限制数量
            offset: 偏移量（用于分页）
            filters: 过滤条件

        Returns:
            List[Dict]: 向量点列表
        """
        try:
            points, next_page_offset = await self.client.scroll(
                collection_name=self.collection_name,
                limit=limit,
                offset=offset,
                with_payload=True,
                with_vectors=False,
            )

            result = []
            for point in points:
                result.append(
                    {
                        "id": str(point.id),
                        "payload": point.payload,
                    }
                )

            logger.info(f"滚动获取向量点: {len(result)} 个")
            return result

        except Exception as e:
            logger.error(f"滚动获取失败: {e}")
            return []

    # ========== 集合统计 ==========

    async def count_points(
        self,
        filters: Optional[Dict[str, Any]] = None,
    ) -> int:
        """统计向量点数量

        Args:
            filters: 过滤条件

        Returns:
            int: 向量点数量
        """
        try:
            count = await self.client.count(
                collection_name=self.collection_name,
            )
            return count
        except Exception as e:
            logger.error(f"统计向量点失败: {e}")
            return 0
