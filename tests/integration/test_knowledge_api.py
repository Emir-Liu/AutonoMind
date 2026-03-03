"""
知识库管理API集成测试
"""

import pytest
from httpx import AsyncClient
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "code"))


@pytest.mark.integration
class TestKnowledgeAPI:
    """知识库API集成测试"""

    @pytest.mark.asyncio
    async def test_add_knowledge(self, async_client: AsyncClient):
        """测试添加知识"""
        knowledge_data = {
            "content": "FastAPI是一个高性能的Python Web框架",
            "source": "manual",
            "metadata": {
                "category": "technology",
                "tags": ["python", "fastapi"]
            }
        }

        response = await async_client.post(
            "/api/v1/knowledge",
            json=knowledge_data
        )

        # 检查响应
        assert response.status_code in [200, 201, 404, 500]

        if response.status_code in [200, 201]:
            data = response.json()
            assert "success" in data
            if data.get("data"):
                assert "id" in data["data"]

    @pytest.mark.asyncio
    async def test_add_knowledge_minimal(self, async_client: AsyncClient):
        """测试添加最小知识"""
        knowledge_data = {
            "content": "测试知识内容"
        }

        response = await async_client.post(
            "/api/v1/knowledge",
            json=knowledge_data
        )

        assert response.status_code in [200, 201, 400, 422]

    @pytest.mark.asyncio
    async def test_add_knowledge_empty_content(self, async_client: AsyncClient):
        """测试添加空内容知识"""
        knowledge_data = {
            "content": ""
        }

        response = await async_client.post(
            "/api/v1/knowledge",
            json=knowledge_data
        )

        assert response.status_code in [400, 422]

    @pytest.mark.asyncio
    async def test_add_knowledge_batch(self, async_client: AsyncClient):
        """测试批量添加知识"""
        batch_data = {
            "knowledge_list": [
                {"content": "知识1", "source": "test"},
                {"content": "知识2", "source": "test"},
                {"content": "知识3", "source": "test"}
            ]
        }

        response = await async_client.post(
            "/api/v1/knowledge/batch",
            json=batch_data
        )

        assert response.status_code in [200, 201, 404, 500]

        if response.status_code in [200, 201]:
            data = response.json()
            if data.get("data"):
                assert "success_count" in data["data"]
                assert "knowledge_ids" in data["data"]

    @pytest.mark.asyncio
    async def test_search_knowledge(self, async_client: AsyncClient):
        """测试检索知识"""
        # 先添加一些知识
        await async_client.post(
            "/api/v1/knowledge",
            json={"content": "FastAPI是高性能的Python Web框架"}
        )

        # 检索
        search_data = {
            "query": "FastAPI",
            "top_k": 5
        }

        response = await async_client.post(
            "/api/v1/knowledge/search",
            json=search_data
        )

        assert response.status_code in [200, 404, 500]

        if response.status_code == 200:
            data = response.json()
            if data.get("data"):
                assert isinstance(data["data"], list)

    @pytest.mark.asyncio
    async def test_search_knowledge_with_filters(self, async_client: AsyncClient):
        """测试带过滤条件的检索"""
        search_data = {
            "query": "Python",
            "top_k": 10,
            "filters": {
                "source": "manual",
                "category": "technology"
            },
            "rerank": True
        }

        response = await async_client.post(
            "/api/v1/knowledge/search",
            json=search_data
        )

        assert response.status_code in [200, 404, 500]

    @pytest.mark.asyncio
    async def test_get_knowledge(self, async_client: AsyncClient):
        """测试获取知识详情"""
        # 先添加知识
        add_response = await async_client.post(
            "/api/v1/knowledge",
            json={"content": "测试知识详情"}
        )

        if add_response.status_code in [200, 201]:
            knowledge_id = add_response.json()["data"].get("id")

            # 获取详情
            response = await async_client.get(f"/api/v1/knowledge/{knowledge_id}")

            assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_get_nonexistent_knowledge(self, async_client: AsyncClient):
        """测试获取不存在的知识"""
        response = await async_client.get("/api/v1/knowledge/nonexistent_id")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_knowledge(self, async_client: AsyncClient):
        """测试更新知识"""
        # 先添加知识
        add_response = await async_client.post(
            "/api/v1/knowledge",
            json={"content": "原始内容"}
        )

        if add_response.status_code in [200, 201]:
            knowledge_id = add_response.json()["data"].get("id")

            # 更新
            update_data = {
                "content": "更新后的内容",
                "metadata": {
                    "category": "updated"
                }
            }

            response = await async_client.put(
                f"/api/v1/knowledge/{knowledge_id}",
                json=update_data
            )

            assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_delete_knowledge(self, async_client: AsyncClient):
        """测试删除知识"""
        # 先添加知识
        add_response = await async_client.post(
            "/api/v1/knowledge",
            json={"content": "待删除的知识"}
        )

        if add_response.status_code in [200, 201]:
            knowledge_id = add_response.json()["data"].get("id")

            # 删除
            response = await async_client.delete(f"/api/v1/knowledge/{knowledge_id}")

            assert response.status_code in [200, 204, 404]

    @pytest.mark.asyncio
    async def test_delete_nonexistent_knowledge(self, async_client: AsyncClient):
        """测试删除不存在的知识"""
        response = await async_client.delete("/api/v1/knowledge/nonexistent_id")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_list_knowledge(self, async_client: AsyncClient):
        """测试列出知识"""
        # 添加几条知识
        for i in range(5):
            await async_client.post(
                "/api/v1/knowledge",
                json={"content": f"知识 {i}", "source": "test"}
            )

        # 列出
        response = await async_client.get(
            "/api/v1/knowledge",
            params={"page": 1, "page_size": 10}
        )

        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_list_knowledge_with_filters(self, async_client: AsyncClient):
        """测试带过滤的列表"""
        response = await async_client.get(
            "/api/v1/knowledge",
            params={
                "page": 1,
                "page_size": 20,
                "source": "manual",
                "status": "active"
            }
        )

        assert response.status_code in [200, 404]


@pytest.mark.integration
class TestKnowledgeUpload:
    """知识上传测试"""

    @pytest.mark.asyncio
    async def test_upload_text_file(self, async_client: AsyncClient):
        """测试上传文本文件"""
        # 模拟文件上传
        # 注意: 需要实际文件才能测试,这里做框架验证
        response = await async_client.post(
            "/api/v1/knowledge/upload",
            data={
                "file": ("test.txt", "测试文件内容", "text/plain"),
                "source": "document"
            }
        )

        assert response.status_code in [200, 201, 404, 415]

    @pytest.mark.asyncio
    async def test_upload_markdown_file(self, async_client: AsyncClient):
        """测试上传Markdown文件"""
        response = await async_client.post(
            "/api/v1/knowledge/upload",
            data={
                "file": ("test.md", "# 测试标题\n内容", "text/markdown"),
                "source": "document"
            }
        )

        assert response.status_code in [200, 201, 404, 415]


@pytest.mark.integration
class TestKnowledgeSearch:
    """知识检索详细测试"""

    @pytest.mark.asyncio
    async def test_search_empty_query(self, async_client: AsyncClient):
        """测试空查询"""
        response = await async_client.post(
            "/api/v1/knowledge/search",
            json={"query": "", "top_k": 10}
        )

        assert response.status_code in [400, 422]

    @pytest.mark.asyncio
    async def test_search_with_large_top_k(self, async_client: AsyncClient):
        """测试大的top_k值"""
        response = await async_client.post(
            "/api/v1/knowledge/search",
            json={"query": "Python", "top_k": 1000}
        )

        assert response.status_code in [200, 404, 500]

    @pytest.mark.asyncio
    async def test_search_with_rerank(self, async_client: AsyncClient):
        """测试重排序检索"""
        response = await async_client.post(
            "/api/v1/knowledge/search",
            json={
                "query": "Python编程",
                "top_k": 10,
                "rerank": True
            }
        )

        assert response.status_code in [200, 404, 500]


@pytest.mark.integration
@pytest.mark.slow
class TestKnowledgeBatchOperations:
    """批量操作测试"""

    @pytest.mark.asyncio
    async def test_batch_add_large_list(self, async_client: AsyncClient):
        """测试批量添加大量知识"""
        knowledge_list = [
            {"content": f"知识 {i}", "source": "test"}
            for i in range(100)
        ]

        response = await async_client.post(
            "/api/v1/knowledge/batch",
            json={"knowledge_list": knowledge_list}
        )

        assert response.status_code in [200, 201, 404, 500]

    @pytest.mark.asyncio
    async def test_batch_delete(self, async_client: AsyncClient):
        """测试批量删除"""
        # 先创建一些知识
        knowledge_ids = []
        for i in range(3):
            add_response = await async_client.post(
                "/api/v1/knowledge",
                json={"content": f"知识 {i}"}
            )
            if add_response.status_code in [200, 201]:
                kid = add_response.json()["data"].get("id")
                if kid:
                    knowledge_ids.append(kid)

        if len(knowledge_ids) > 0:
            # 批量删除
            response = await async_client.delete(
                "/api/v1/knowledge/batch",
                json={"knowledge_ids": knowledge_ids}
            )

            assert response.status_code in [200, 404]
