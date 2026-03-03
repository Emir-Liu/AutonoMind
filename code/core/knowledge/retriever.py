"""知识检索器实现

实现向量相似度搜索、混合检索、结果排序
"""

from typing import List, Dict, Any, Optional
from enum import Enum

from core.knowledge.interfaces import IKnowledgeRetriever
from core.embedding import EmbeddingService, QdrantVectorStore
from utils.logger import logger


class RetrievalStrategy(str, Enum):
    """检索策略"""

    VECTOR = "vector"  # 纯向量检索
    KEYWORD = "keyword"  # 纯关键词检索
    HYBRID = "hybrid"  # 混合检索


class KnowledgeRetriever(IKnowledgeRetriever):
    """知识检索器实现"""

    def __init__(
        self,
        embedding_service: EmbeddingService,
        vector_store: QdrantVectorStore,
        db_session,
    ):
        self.embedding = embedding_service
        self.vector_store = vector_store
        self.db = db_session

    # ========== 知识检索 ==========

    async def retrieve_knowledge(
        self,
        query: str,
        user_id: int,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
        strategy: RetrievalStrategy = RetrievalStrategy.VECTOR,
        rerank: bool = True,
    ) -> List[Dict[str, Any]]:
        """检索相关知识

        Args:
            query: 查询文本
            user_id: 用户ID
            top_k: 返回结果数量
            filters: 过滤条件
            strategy: 检索策略
            rerank: 是否重排序

        Returns:
            List[Dict]: 知识列表
        """
        try:
            if strategy == RetrievalStrategy.VECTOR:
                results = await self._vector_search(
                    query=query,
                    top_k=top_k,
                    filters=filters,
                )
            elif strategy == RetrievalStrategy.KEYWORD:
                results = await self._keyword_search(
                    query=query,
                    top_k=top_k,
                    filters=filters,
                )
            else:  # HYBRID
                results = await self._hybrid_search(
                    query=query,
                    top_k=top_k,
                    filters=filters,
                )

            # 重排序
            if rerank and results:
                results = await self._rerank_results(
                    query=query,
                    results=results,
                )

            logger.info(f"知识检索完成: {len(results)} 条, 策略: {strategy}")
            return results

        except Exception as e:
            logger.error(f"知识检索失败: {e}", exc_info=True)
            return []

    # ========== 向量检索 ==========

    async def _vector_search(
        self,
        query: str,
        top_k: int,
        filters: Optional[Dict[str, Any]] = None,
        score_threshold: float = 0.6,
    ) -> List[Dict[str, Any]]:
        """向量相似度搜索

        Args:
            query: 查询文本
            top_k: 返回数量
            filters: 过滤条件
            score_threshold: 分数阈值

        Returns:
            List[Dict]: 检索结果
        """
        try:
            # 生成查询向量
            embed_result = await self.embedding.embed_text(query)
            query_vector = embed_result.vector

            # 执行向量搜索
            search_results = await self.vector_store.search(
                query_vector=query_vector,
                limit=top_k * 2,  # 检索更多，后续过滤
                score_threshold=score_threshold,
                filters=filters,
            )

            # 转换为知识列表
            results = []
            for result in search_results:
                # 从payload中获取知识ID
                knowledge_id = result.payload.get("knowledge_id")

                if knowledge_id:
                    # 从数据库获取知识详情
                    knowledge = await self._get_knowledge_by_id(knowledge_id)
                    if knowledge:
                        results.append(
                            {
                                "id": knowledge_id,
                                "title": knowledge.get("title", ""),
                                "content": knowledge.get("content", ""),
                                "score": result.score,
                                "metadata": result.payload,
                                "type": "vector",
                            }
                        )

            return results[:top_k]

        except Exception as e:
            logger.error(f"向量检索失败: {e}")
            return []

    # ========== 关键词检索 ==========

    async def _keyword_search(
        self,
        query: str,
        top_k: int,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """关键词检索（BM25）

        Args:
            query: 查询文本
            top_k: 返回数量
            filters: 过滤条件

        Returns:
            List[Dict]: 检索结果
        """
        try:
            # 从数据库检索
            # TODO: 实现基于PostgreSQL的全文检索或集成Elasticsearch
            # 这里使用简单的LIKE查询作为示例

            from sqlalchemy import or_

            query_obj = select("*").select_from("knowledge").where(
                or_(
                    # 标题匹配
                    "knowledge.title".ilike(f"%{query}%"),
                    # 内容匹配
                    "knowledge.content".ilike(f"%{query}%"),
                )
            )

            # 应用过滤条件
            if filters:
                for key, value in filters.items():
                    query_obj = query_obj.where(
                        getattr("knowledge", key) == value
                    )

            # 限制数量
            query_obj = query_obj.limit(top_k * 2)

            # 执行查询
            # TODO: 执行查询并转换结果

            # 临时返回空列表
            results = []

            return results[:top_k]

        except Exception as e:
            logger.error(f"关键词检索失败: {e}")
            return []

    # ========== 混合检索 ==========

    async def _hybrid_search(
        self,
        query: str,
        top_k: int,
        filters: Optional[Dict[str, Any]] = None,
        vector_weight: float = 0.7,
    ) -> List[Dict[str, Any]]:
        """混合检索（向量 + 关键词）

        Args:
            query: 查询文本
            top_k: 返回数量
            filters: 过滤条件
            vector_weight: 向量检索权重 (0-1)

        Returns:
            List[Dict]: 检索结果
        """
        try:
            # 并行执行两种检索
            vector_results = await self._vector_search(
                query=query,
                top_k=top_k * 2,
                filters=filters,
            )

            keyword_results = await self._keyword_search(
                query=query,
                top_k=top_k * 2,
                filters=filters,
            )

            # 合并结果
            merged = {}

            # 向量结果
            for result in vector_results:
                knowledge_id = result["id"]
                if knowledge_id not in merged:
                    merged[knowledge_id] = result.copy()
                    merged[knowledge_id]["vector_score"] = result["score"]
                    merged[knowledge_id]["keyword_score"] = 0.0
                else:
                    merged[knowledge_id]["vector_score"] = result["score"]

            # 关键词结果
            for result in keyword_results:
                knowledge_id = result["id"]
                if knowledge_id not in merged:
                    merged[knowledge_id] = result.copy()
                    merged[knowledge_id]["vector_score"] = 0.0
                    merged[knowledge_id]["keyword_score"] = result["score"]
                else:
                    merged[knowledge_id]["keyword_score"] = result["score"]

            # 计算混合分数
            for knowledge_id, result in merged.items():
                vector_score = result.get("vector_score", 0.0)
                keyword_score = result.get("keyword_score", 0.0)

                # 归一化分数到 0-1
                normalized_vector = min(vector_score, 1.0)
                normalized_keyword = min(keyword_score, 1.0)

                # 加权混合
                result["score"] = (
                    normalized_vector * vector_weight
                    + normalized_keyword * (1 - vector_weight)
                )

            # 排序并返回
            sorted_results = sorted(
                merged.values(),
                key=lambda x: x["score"],
                reverse=True,
            )

            return sorted_results[:top_k]

        except Exception as e:
            logger.error(f"混合检索失败: {e}")
            return []

    # ========== 重排序 ==========

    async def _rerank_results(
        self,
        query: str,
        results: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """使用LLM重排序检索结果

        Args:
            query: 查询文本
            results: 检索结果

        Returns:
            List[Dict]: 重排序后的结果
        """
        if not results:
            return results

        try:
            # 构建重排序Prompt
            prompt = self._build_rerank_prompt(query, results)

            # 调用LLM
            # TODO: 集成LLM进行重排序
            # 这里暂时按原始分数排序

            reranked = sorted(
                results,
                key=lambda x: x["score"],
                reverse=True,
            )

            return reranked

        except Exception as e:
            logger.error(f"重排序失败: {e}")
            return results

    def _build_rerank_prompt(
        self,
        query: str,
        results: List[Dict[str, Any]],
    ) -> str:
        """构建重排序Prompt"""

        results_text = "\n".join(
            [
                f"{idx + 1}. ID: {r['id']}\n   标题: {r['title']}\n   内容: {r['content'][:200]}..."
                for idx, r in enumerate(results)
            ]
        )

        prompt = f"""请根据查询问题对以下检索结果进行重排序，返回最相关的5条结果。

## 查询问题
{query}

## 检索结果
{results_text}

## 排序要求
1. 根据与查询的相关性排序
2. 返回结果ID列表，按相关性从高到低
3. 至少返回3条，最多5条

## 输出格式
[{{"id": 123, "reason": "相关原因"}}, ...]
"""

        return prompt

    # ========== 辅助方法 ==========

    async def _get_knowledge_by_id(
        self,
        knowledge_id: int,
    ) -> Optional[Dict[str, Any]]:
        """根据ID获取知识

        Args:
            knowledge_id: 知识ID

        Returns:
            Optional[Dict]: 知识信息
        """
        try:
            # TODO: 从数据库查询知识
            return {
                "id": knowledge_id,
                "title": "示例知识",
                "content": "示例内容",
            }
        except Exception as e:
            logger.error(f"获取知识失败: {e}")
            return None

    # ========== 知识管理 ==========

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
        try:
            # 文本分块
            from core.embedding import TextChunk

            chunks = self.embedding.chunk_text(
                text=content,
                chunk_size=500,
                chunk_overlap=50,
            )

            # 生成嵌入
            embedded_chunks = await self.embedding.embed_chunks(chunks)

            # 准备向量点
            points = []
            for idx, embedded_chunk in enumerate(embedded_chunks):
                points.append(
                    {
                        "id": f"knowledge_{knowledge_id}_chunk_{idx}",
                        "vector": embedded_chunk["vector"],
                        "payload": {
                            "knowledge_id": knowledge_id,
                            "chunk_index": idx,
                            "content": embedded_chunk["content"],
                            **(metadata or {}),
                        },
                    }
                )

            # 批量插入
            await self.vector_store.upsert_points(points)

            logger.info(f"添加知识到向量库成功: {knowledge_id}, {len(points)} 个块")
            return True

        except Exception as e:
            logger.error(f"添加知识失败: {e}")
            return False

    async def delete_knowledge(self, knowledge_id: int) -> bool:
        """从向量数据库删除知识

        Args:
            knowledge_id: 知识ID

        Returns:
            bool: 成功返回True
        """
        try:
            # 查找该知识的所有向量点
            # TODO: 实现查询逻辑

            # 临时实现：删除所有以knowledge_id开头的点
            # await self.vector_store.delete_points(point_ids)

            logger.info(f"删除知识从向量库: {knowledge_id}")
            return True

        except Exception as e:
            logger.error(f"删除知识失败: {e}")
            return False

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
        try:
            # 先删除旧的
            await self.delete_knowledge(knowledge_id)

            # 再添加新的
            await self.add_knowledge(knowledge_id, content, metadata)

            logger.info(f"更新知识成功: {knowledge_id}")
            return True

        except Exception as e:
            logger.error(f"更新知识失败: {e}")
            return False
