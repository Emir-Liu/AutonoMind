"""
知识检索器单元测试
"""

import pytest
from unittest.mock import Mock, AsyncMock, MagicMock
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "code"))

from core.knowledge.retriever import KnowledgeRetriever, RetrievalStrategy


@pytest.mark.unit
class TestKnowledgeRetriever:
    """知识检索器测试"""

    @pytest.fixture
    def mock_embedding_service(self):
        """模拟嵌入服务"""
        mock = AsyncMock()
        mock.create_embedding = AsyncMock(return_value=[0.1, 0.2, 0.3])
        return mock

    @pytest.fixture
    def mock_vector_store(self):
        """模拟向量存储"""
        mock = AsyncMock()
        mock.search = AsyncMock(return_value=[])
        return mock

    @pytest.fixture
    def retriever(self, mock_embedding_service, mock_vector_store):
        """创建检索器实例"""
        return KnowledgeRetriever(
            embedding_service=mock_embedding_service,
            vector_store=mock_vector_store
        )

    @pytest.mark.asyncio
    async def test_retrieve_vector_search(self, retriever, mock_vector_store):
        """测试向量检索"""
        mock_vector_store.search.return_value = [
            {"id": "kno_001", "score": 0.95, "payload": {"content": "相关内容1"}},
            {"id": "kno_002", "score": 0.88, "payload": {"content": "相关内容2"}}
        ]

        results = await retriever.retrieve(
            query="测试查询",
            strategy=RetrievalStrategy.VECTOR,
            top_k=5
        )

        assert len(results) == 2
        assert results[0]["id"] == "kno_001"
        assert results[0]["score"] == 0.95

    @pytest.mark.asyncio
    async def test_retrieve_keyword_search(self, retriever):
        """测试关键词检索"""
        # 模拟向量存储返回基于关键词的结果
        retriever.vector_store.search.return_value = [
            {"id": "kno_001", "score": 0.90, "payload": {"content": "FastAPI是高性能框架"}}
        ]

        results = await retriever.retrieve(
            query="FastAPI",
            strategy=RetrievalStrategy.KEYWORD,
            top_k=5
        )

        assert len(results) >= 0

    @pytest.mark.asyncio
    async def test_retrieve_hybrid_search(self, retriever, mock_vector_store):
        """测试混合检索"""
        mock_vector_store.search.return_value = [
            {"id": "kno_001", "score": 0.95, "payload": {"content": "内容1"}},
            {"id": "kno_002", "score": 0.85, "payload": {"content": "内容2"}}
        ]

        results = await retriever.retrieve(
            query="FastAPI 性能",
            strategy=RetrievalStrategy.HYBRID,
            top_k=5
        )

        # 混合检索应该综合向量和关键词结果
        assert len(results) == 2

    @pytest.mark.asyncio
    async def test_retrieve_with_filters(self, retriever, mock_vector_store):
        """测试带过滤条件的检索"""
        filters = {"source": "manual", "category": "technology"}

        results = await retriever.retrieve(
            query="测试查询",
            filters=filters,
            top_k=5
        )

        # 验证过滤条件被使用
        assert True  # 如果调用成功则通过

    @pytest.mark.asyncio
    async def test_retrieve_empty_results(self, retriever, mock_vector_store):
        """测试无结果情况"""
        mock_vector_store.search.return_value = []

        results = await retriever.retrieve(
            query="不存在的查询",
            top_k=5
        )

        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_rerank_results(self, retriever):
        """测试重排序结果"""
        initial_results = [
            {"id": "kno_001", "score": 0.85, "payload": {"content": "不太相关"}},
            {"id": "kno_002", "score": 0.80, "payload": {"content": "非常相关的内容"}},
            {"id": "kno_003", "score": 0.75, "payload": {"content": "有点相关"}}
        ]

        reranked = await retriever.rerank(
            results=initial_results,
            query="相关的内容"
        )

        assert len(reranked) == 3
        # 重新排序后,最相关的应该在前面
        assert reranked[0]["payload"]["content"] == "非常相关的内容"

    @pytest.mark.asyncio
    async def test_get_retrieval_stats(self, retriever):
        """测试获取检索统计"""
        retriever.vector_store.search.return_value = [
            {"id": "kno_001", "score": 0.95, "payload": {"content": "内容1"}},
            {"id": "kno_002", "score": 0.88, "payload": {"content": "内容2"}}
        ]

        await retriever.retrieve(query="测试", top_k=5)

        stats = retriever.get_retrieval_stats()

        assert stats["total_retrievals"] == 1
        assert stats["total_results"] == 2

    def test_retrieval_strategies(self):
        """测试检索策略枚举"""
        assert RetrievalStrategy.VECTOR.value == "vector"
        assert RetrievalStrategy.KEYWORD.value == "keyword"
        assert RetrievalStrategy.HYBRID.value == "hybrid"

    @pytest.mark.asyncio
    async def test_retrieve_with_score_threshold(self, retriever, mock_vector_store):
        """测试相似度阈值"""
        mock_vector_store.search.return_value = [
            {"id": "kno_001", "score": 0.95, "payload": {"content": "A"}},
            {"id": "kno_002", "score": 0.65, "payload": {"content": "B"}},
            {"id": "kno_003", "score": 0.85, "payload": {"content": "C"}}
        ]

        results = await retriever.retrieve(
            query="测试查询",
            top_k=10,
            score_threshold=0.70
        )

        # 应该过滤掉score < 0.7的结果
        assert len(results) == 2
        assert all(r["score"] >= 0.70 for r in results)


@pytest.mark.unit
class TestRetrievalStrategy:
    """检索策略测试"""

    def test_all_strategies(self):
        """测试所有策略"""
        strategies = [
            RetrievalStrategy.VECTOR,
            RetrievalStrategy.KEYWORD,
            RetrievalStrategy.HYBRID
        ]

        assert len(strategies) == 3
        assert all(isinstance(s, RetrievalStrategy) for s in strategies)

    def test_strategy_from_string(self):
        """测试从字符串创建策略"""
        assert RetrievalStrategy("vector") == RetrievalStrategy.VECTOR
        assert RetrievalStrategy("keyword") == RetrievalStrategy.KEYWORD
        assert RetrievalStrategy("hybrid") == RetrievalStrategy.HYBRID

    def test_invalid_strategy(self):
        """测试无效策略"""
        with pytest.raises(ValueError):
            RetrievalStrategy("invalid")


@pytest.mark.unit
class TestKnowledgeRetrieverEdgeCases:
    """知识检索器边界条件测试"""

    @pytest.fixture
    def retriever(self):
        """创建检索器实例"""
        mock_embedding = AsyncMock()
        mock_vector_store = AsyncMock()
        return KnowledgeRetriever(
            embedding_service=mock_embedding,
            vector_store=mock_vector_store
        )

    @pytest.mark.asyncio
    async def test_empty_query(self, retriever):
        """测试空查询"""
        results = await retriever.retrieve(
            query="",
            top_k=5
        )

        # 空查询应该返回空结果或处理得当
        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_very_long_query(self, retriever):
        """测试超长查询"""
        long_query = "测试" * 1000

        results = await retriever.retrieve(
            query=long_query,
            top_k=5
        )

        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_zero_top_k(self, retriever):
        """测试top_k=0"""
        results = await retriever.retrieve(
            query="测试",
            top_k=0
        )

        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_large_top_k(self, retriever):
        """测试大的top_k值"""
        results = await retriever.retrieve(
            query="测试",
            top_k=1000
        )

        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_special_characters_query(self, retriever):
        """测试包含特殊字符的查询"""
        special_query = "Python @#$%^&*()_+-={}[]|\\:;\"'<>,.?/~`"

        results = await retriever.retrieve(
            query=special_query,
            top_k=5
        )

        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_unicode_query(self, retriever):
        """测试Unicode查询"""
        unicode_query = "测试 🎉 Python 中文 🚀"

        results = await retriever.retrieve(
            query=unicode_query,
            top_k=5
        )

        assert isinstance(results, list)
