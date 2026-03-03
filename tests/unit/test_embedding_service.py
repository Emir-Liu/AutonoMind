"""
嵌入服务单元测试
"""

import pytest
from unittest.mock import Mock, AsyncMock, MagicMock
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "code"))

from core.embedding.embedding_service import EmbeddingService
from core.embedding.vector_store import QdrantVectorStore


@pytest.mark.unit
class TestEmbeddingService:
    """嵌入服务测试"""

    @pytest.fixture
    def mock_openai_client(self):
        """模拟OpenAI客户端"""
        mock = AsyncMock()
        mock.embeddings.create = AsyncMock(return_value=MagicMock(
            data=[MagicMock(embedding=np.array([0.1, 0.2, 0.3]).tolist())]
        ))
        return mock

    @pytest.fixture
    def embedding_service(self, mock_openai_client):
        """创建嵌入服务实例"""
        return EmbeddingService(
            openai_client=mock_openai_client,
            model="text-embedding-ada-002"
        )

    async def test_create_embedding_single_text(self, embedding_service, mock_openai_client):
        """测试为单个文本创建嵌入"""
        text = "测试文本"
        embedding = await embedding_service.create_embedding(text)

        assert isinstance(embedding, list)
        assert len(embedding) > 0
        assert all(isinstance(x, (int, float)) for x in embedding)
        mock_openai_client.embeddings.create.assert_called_once()

    async def test_create_embedding_batch(self, embedding_service, mock_openai_client):
        """测试批量创建嵌入"""
        texts = ["文本1", "文本2", "文本3"]
        mock_openai_client.embeddings.create.return_value = MagicMock(
            data=[
                MagicMock(embedding=np.array([0.1, 0.2, 0.3]).tolist()),
                MagicMock(embedding=np.array([0.2, 0.3, 0.4]).tolist()),
                MagicMock(embedding=np.array([0.3, 0.4, 0.5]).tolist())
            ]
        )

        embeddings = await embedding_service.create_embeddings_batch(texts)

        assert len(embeddings) == 3
        assert all(isinstance(emb, list) for emb in embeddings)

    async def test_chunk_text_by_character(self, embedding_service):
        """测试按字符数分块"""
        text = "这是一个测试文本" * 20  # 长文本
        chunks = embedding_service.chunk_text(text, chunk_size=20)

        assert len(chunks) > 1
        assert all(len(chunk) <= 25 for chunk in chunks)  # chunk_size + 25% overlap

    async def test_chunk_text_by_paragraph(self, embedding_service):
        """测试按段落分块"""
        text = "第一段\n\n第二段\n\n第三段"
        chunks = embedding_service.chunk_text(text, strategy="paragraph")

        assert len(chunks) == 3
        assert "第一段" in chunks[0]
        assert "第二段" in chunks[1]

    async def test_chunk_text_with_overlap(self, embedding_service):
        """测试带重叠的分块"""
        text = "测试文本" * 10
        chunks = embedding_service.chunk_text(text, chunk_size=10, overlap=2)

        # 检查相邻块有重叠
        if len(chunks) > 1:
            assert chunks[0][-2:] == chunks[1][:2]

    def test_calculate_similarity(self, embedding_service):
        """测试计算相似度"""
        embedding1 = [1.0, 0.0, 0.0]
        embedding2 = [1.0, 0.0, 0.0]
        embedding3 = [0.0, 1.0, 0.0]

        # 相同向量
        similarity = embedding_service.calculate_similarity(embedding1, embedding2)
        assert similarity == pytest.approx(1.0, abs=0.01)

        # 正交向量
        similarity = embedding_service.calculate_similarity(embedding1, embedding3)
        assert similarity == pytest.approx(0.0, abs=0.01)

    async def test_normalize_embedding(self, embedding_service):
        """测试嵌入归一化"""
        embedding = [3.0, 4.0, 0.0]
        normalized = embedding_service.normalize_embedding(embedding)

        norm = sum(x**2 for x in normalized) ** 0.5
        assert norm == pytest.approx(1.0, abs=0.01)


@pytest.mark.unit
class TestQdrantVectorStore:
    """Qdrant向量存储测试"""

    @pytest.fixture
    def mock_qdrant_client(self):
        """模拟Qdrant客户端"""
        mock = Mock()
        mock.upsert = MagicMock()
        mock.search = MagicMock(return_value=[])
        mock.delete = MagicMock()
        mock.count = MagicMock(return_value=MagicMock(count=0))
        return mock

    @pytest.fixture
    def vector_store(self, mock_qdrant_client):
        """创建向量存储实例"""
        return QdrantVectorStore(
            qdrant_client=mock_qdrant_client,
            collection_name="test_collection"
        )

    @pytest.mark.asyncio
    async def test_insert_single_vector(self, vector_store, mock_qdrant_client):
        """测试插入单个向量"""
        vector = [0.1, 0.2, 0.3]
        payload = {"content": "测试内容", "id": "test_id"}

        await vector_store.insert(
            vectors=[vector],
            payloads=[payload],
            ids=["test_id"]
        )

        mock_qdrant_client.upsert.assert_called_once()

    @pytest.mark.asyncio
    async def test_insert_batch_vectors(self, vector_store, mock_qdrant_client):
        """测试批量插入向量"""
        vectors = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
        payloads = [
            {"content": "内容1", "id": "id1"},
            {"content": "内容2", "id": "id2"}
        ]
        ids = ["id1", "id2"]

        await vector_store.insert(
            vectors=vectors,
            payloads=payloads,
            ids=ids
        )

        mock_qdrant_client.upsert.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_vectors(self, vector_store, mock_qdrant_client):
        """测试向量搜索"""
        mock_qdrant_client.search.return_value = [
            MagicMock(
                id="test_id_1",
                score=0.95,
                payload={"content": "相关内容1", "metadata": {}}
            ),
            MagicMock(
                id="test_id_2",
                score=0.85,
                payload={"content": "相关内容2", "metadata": {}}
            )
        ]

        query_vector = [0.1, 0.2, 0.3]
        results = await vector_store.search(
            query_vector=query_vector,
            top_k=10,
            score_threshold=0.7
        )

        assert len(results) == 2
        assert results[0]["score"] == 0.95
        assert results[0]["payload"]["content"] == "相关内容1"

    @pytest.mark.asyncio
    async def test_search_with_filters(self, vector_store, mock_qdrant_client):
        """测试带过滤条件的搜索"""
        query_vector = [0.1, 0.2, 0.3]
        filters = {"must": [{"key": "source", "match": {"value": "manual"}}]}

        await vector_store.search(
            query_vector=query_vector,
            top_k=5,
            filters=filters
        )

        mock_qdrant_client.search.assert_called_once()
        # 验证过滤条件被正确传递
        call_args = mock_qdrant_client.search.call_args
        assert call_args is not None

    @pytest.mark.asyncio
    async def test_delete_vectors(self, vector_store, mock_qdrant_client):
        """测试删除向量"""
        ids = ["id1", "id2", "id3"]

        await vector_store.delete(ids=ids)

        mock_qdrant_client.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_count_vectors(self, vector_store, mock_qdrant_client):
        """测试统计向量数量"""
        mock_qdrant_client.count.return_value = MagicMock(count=42)

        count = await vector_store.count()

        assert count == 42
        mock_qdrant_client.count.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_score_threshold(self, vector_store, mock_qdrant_client):
        """测试相似度阈值过滤"""
        mock_qdrant_client.search.return_value = [
            MagicMock(id="id1", score=0.95, payload={"content": "A"}),
            MagicMock(id="id2", score=0.65, payload={"content": "B"}),
            MagicMock(id="id3", score=0.85, payload={"content": "C"})
        ]

        query_vector = [0.1, 0.2, 0.3]
        results = await vector_store.search(
            query_vector=query_vector,
            score_threshold=0.70
        )

        # 应该过滤掉score < 0.7的结果
        assert len(results) == 2
        assert all(r["score"] >= 0.70 for r in results)

    @pytest.mark.asyncio
    async def test_empty_collection_count(self, vector_store, mock_qdrant_client):
        """测试空集合计数"""
        mock_qdrant_client.count.return_value = MagicMock(count=0)

        count = await vector_store.count()

        assert count == 0

    def test_initialization_with_collection_name(self):
        """测试使用自定义集合名初始化"""
        mock_client = Mock()
        store = QdrantVectorStore(
            qdrant_client=mock_client,
            collection_name="custom_collection"
        )

        assert store.collection_name == "custom_collection"
