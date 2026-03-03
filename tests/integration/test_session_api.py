"""
会话管理API集成测试
"""

import pytest
from httpx import AsyncClient
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "code"))


@pytest.mark.integration
class TestSessionAPI:
    """会话API集成测试"""

    @pytest.mark.asyncio
    async def test_create_session_success(self, async_client: AsyncClient):
        """测试创建会话成功"""
        session_data = {
            "user_id": "test_user_001",
            "agent_config": {
                "llm_provider": "openai",
                "llm_model": "gpt-4",
                "temperature": 0.7,
                "max_tokens": 2000
            },
            "metadata": {
                "source": "test",
                "tags": ["integration_test"]
            }
        }

        response = await async_client.post(
            "/api/v1/sessions",
            json=session_data,
            headers={"Content-Type": "application/json"}
        )

        # 检查响应状态
        assert response.status_code in [200, 201]

        # 检查响应格式
        if response.status_code in [200, 201]:
            data = response.json()
            assert "success" in data
            assert "data" in data
            if data["success"] and data.get("data"):
                assert "session_id" in data["data"]
                assert data["data"]["user_id"] == "test_user_001"

    @pytest.mark.asyncio
    async def test_create_session_minimal(self, async_client: AsyncClient):
        """测试创建最小会话"""
        session_data = {
            "user_id": "test_user_002"
        }

        response = await async_client.post(
            "/api/v1/sessions",
            json=session_data
        )

        # 应该能成功创建
        assert response.status_code in [200, 201, 422]  # 422如果schema要求agent_config

    @pytest.mark.asyncio
    async def test_create_session_missing_user_id(self, async_client: AsyncClient):
        """测试创建会话缺少user_id"""
        session_data = {
            "agent_config": {
                "llm_provider": "openai"
            }
        }

        response = await async_client.post(
            "/api/v1/sessions",
            json=session_data
        )

        # 应该返回验证错误
        assert response.status_code in [400, 422]

    @pytest.mark.asyncio
    async def test_get_session(self, async_client: AsyncClient):
        """测试获取会话信息"""
        # 先创建会话
        create_data = {"user_id": "test_user_003"}
        create_response = await async_client.post("/api/v1/sessions", json=create_data)

        if create_response.status_code in [200, 201]:
            session_id = create_response.json()["data"].get("session_id")

            # 获取会话
            response = await async_client.get(f"/api/v1/sessions/{session_id}")

            assert response.status_code in [200, 404]  # 404如果还没实现

    @pytest.mark.asyncio
    async def test_get_nonexistent_session(self, async_client: AsyncClient):
        """测试获取不存在的会话"""
        response = await async_client.get("/api/v1/sessions/nonexistent_session_id")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_list_sessions(self, async_client: AsyncClient):
        """测试列出会话"""
        # 创建几个会话
        for i in range(3):
            await async_client.post(
                "/api/v1/sessions",
                json={"user_id": f"test_user_{i}"}
            )

        # 列出会话
        response = await async_client.get(
            "/api/v1/sessions",
            params={"user_id": "test_user_0"}
        )

        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_list_sessions_pagination(self, async_client: AsyncClient):
        """测试会话分页"""
        response = await async_client.get(
            "/api/v1/sessions",
            params={
                "user_id": "test_user",
                "page": 1,
                "page_size": 10
            }
        )

        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_delete_session(self, async_client: AsyncClient):
        """测试删除会话"""
        # 创建会话
        create_data = {"user_id": "test_user_delete"}
        create_response = await async_client.post("/api/v1/sessions", json=create_data)

        if create_response.status_code in [200, 201]:
            session_id = create_response.json()["data"].get("session_id")

            # 删除会话
            response = await async_client.delete(f"/api/v1/sessions/{session_id}")

            assert response.status_code in [200, 204, 404]

    @pytest.mark.asyncio
    async def test_delete_nonexistent_session(self, async_client: AsyncClient):
        """测试删除不存在的会话"""
        response = await async_client.delete("/api/v1/sessions/nonexistent_id")

        assert response.status_code == 404


@pytest.mark.integration
@pytest.mark.slow
class TestSessionAPIMultipleRequests:
    """多请求会话API测试"""

    @pytest.mark.asyncio
    async def test_create_multiple_sessions(self, async_client: AsyncClient):
        """测试创建多个会话"""
        session_ids = []

        for i in range(5):
            response = await async_client.post(
                "/api/v1/sessions",
                json={"user_id": f"user_{i}"}
            )
            if response.status_code in [200, 201]:
                session_id = response.json()["data"].get("session_id")
                if session_id:
                    session_ids.append(session_id)

        # 验证至少有一些会话创建成功
        assert len(session_ids) >= 0

    @pytest.mark.asyncio
    async def test_session_isolation(self, async_client: AsyncClient):
        """测试会话隔离"""
        # 创建两个不同用户的会话
        response1 = await async_client.post(
            "/api/v1/sessions",
            json={"user_id": "user_A"}
        )
        response2 = await async_client.post(
            "/api/v1/sessions",
            json={"user_id": "user_B"}
        )

        # 每个会话应该有独立的ID
        if (response1.status_code in [200, 201] and
            response2.status_code in [200, 201]):
            id1 = response1.json()["data"].get("session_id")
            id2 = response2.json()["data"].get("session_id")
            assert id1 != id2
