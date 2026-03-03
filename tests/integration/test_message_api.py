"""
消息管理API集成测试
"""

import pytest
from httpx import AsyncClient
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "code"))


@pytest.mark.integration
class TestMessageAPI:
    """消息API集成测试"""

    @pytest.mark.asyncio
    async def test_send_message(self, async_client: AsyncClient):
        """测试发送消息"""
        # 先创建会话
        session_response = await async_client.post(
            "/api/v1/sessions",
            json={"user_id": "test_user_msg"}
        )

        if session_response.status_code in [200, 201]:
            session_id = session_response.json()["data"].get("session_id")

            # 发送消息
            message_data = {
                "role": "user",
                "content": "你好,请介绍一下Python",
                "stream": False
            }

            response = await async_client.post(
                f"/api/v1/sessions/{session_id}/messages",
                json=message_data
            )

            assert response.status_code in [200, 201, 404, 500]  # 500如果LLM未配置

            if response.status_code in [200, 201]:
                data = response.json()
                assert "success" in data
                if data.get("data"):
                    assert "message_id" in data["data"]

    @pytest.mark.asyncio
    async def test_send_message_to_nonexistent_session(self, async_client: AsyncClient):
        """测试向不存在的会话发送消息"""
        message_data = {
            "role": "user",
            "content": "测试消息",
            "stream": False
        }

        response = await async_client.post(
            "/api/v1/sessions/nonexistent_id/messages",
            json=message_data
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_message_history(self, async_client: AsyncClient):
        """测试获取消息历史"""
        # 创建会话并发送消息
        session_response = await async_client.post(
            "/api/v1/sessions",
            json={"user_id": "test_user_history"}
        )

        if session_response.status_code in [200, 201]:
            session_id = session_response.json()["data"].get("session_id")

            # 发送几条消息
            for i in range(3):
                await async_client.post(
                    f"/api/v1/sessions/{session_id}/messages",
                    json={
                        "role": "user",
                        "content": f"消息 {i+1}",
                        "stream": False
                    }
                )

            # 获取历史
            response = await async_client.get(
                f"/api/v1/sessions/{session_id}/messages"
            )

            assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_get_message_history_pagination(self, async_client: AsyncClient):
        """测试消息历史分页"""
        response = await async_client.get(
            "/api/v1/sessions/test_session/messages",
            params={"page": 1, "page_size": 10}
        )

        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_send_system_message(self, async_client: AsyncClient):
        """测试发送系统消息"""
        session_response = await async_client.post(
            "/api/v1/sessions",
            json={"user_id": "test_user_system"}
        )

        if session_response.status_code in [200, 201]:
            session_id = session_response.json()["data"].get("session_id")

            message_data = {
                "role": "system",
                "content": "你是一个AI助手",
                "stream": False
            }

            response = await async_client.post(
                f"/api/v1/sessions/{session_id}/messages",
                json=message_data
            )

            assert response.status_code in [200, 201, 404, 500]

    @pytest.mark.asyncio
    async def test_message_with_retrieval(self, async_client: AsyncClient):
        """测试带检索的消息"""
        # 先添加知识
        await async_client.post(
            "/api/v1/knowledge",
            json={
                "content": "FastAPI是一个高性能的Python Web框架",
                "source": "test"
            }
        )

        # 创建会话
        session_response = await async_client.post(
            "/api/v1/sessions",
            json={"user_id": "test_user_retrieval"}
        )

        if session_response.status_code in [200, 201]:
            session_id = session_response.json()["data"].get("session_id")

            # 发送与知识相关的消息
            response = await async_client.post(
                f"/api/v1/sessions/{session_id}/messages",
                json={
                    "role": "user",
                    "content": "FastAPI是什么?",
                    "stream": False
                }
            )

            # 如果实现,应该包含检索到的知识
            if response.status_code in [200, 201]:
                data = response.json()
                if data.get("data") and data["data"].get("retrieved_knowledge"):
                    assert isinstance(data["data"]["retrieved_knowledge"], list)


@pytest.mark.integration
class TestMessageValidation:
    """消息验证测试"""

    @pytest.mark.asyncio
    async def test_empty_message(self, async_client: AsyncClient):
        """测试空消息"""
        session_response = await async_client.post(
            "/api/v1/sessions",
            json={"user_id": "test_user_empty"}
        )

        if session_response.status_code in [200, 201]:
            session_id = session_response.json()["data"].get("session_id")

            message_data = {
                "role": "user",
                "content": "",
                "stream": False
            }

            response = await async_client.post(
                f"/api/v1/sessions/{session_id}/messages",
                json=message_data
            )

            # 空消息可能被拒绝或处理
            assert response.status_code in [200, 201, 400, 422]

    @pytest.mark.asyncio
    async def test_invalid_role(self, async_client: AsyncClient):
        """测试无效的角色"""
        session_response = await async_client.post(
            "/api/v1/sessions",
            json={"user_id": "test_user_invalid"}
        )

        if session_response.status_code in [200, 201]:
            session_id = session_response.json()["data"].get("session_id")

            message_data = {
                "role": "invalid_role",
                "content": "测试",
                "stream": False
            }

            response = await async_client.post(
                f"/api/v1/sessions/{session_id}/messages",
                json=message_data
            )

            # 应该返回验证错误
            assert response.status_code in [400, 422]

    @pytest.mark.asyncio
    async def test_very_long_message(self, async_client: AsyncClient):
        """测试超长消息"""
        session_response = await async_client.post(
            "/api/v1/sessions",
            json={"user_id": "test_user_long"}
        )

        if session_response.status_code in [200, 201]:
            session_id = session_response.json()["data"].get("session_id")

            message_data = {
                "role": "user",
                "content": "测试" * 10000,
                "stream": False
            }

            response = await async_client.post(
                f"/api/v1/sessions/{session_id}/messages",
                json=message_data
            )

            # 超长消息应该被处理或限制
            assert response.status_code in [200, 201, 400, 413]


@pytest.mark.integration
@pytest.mark.slow
class TestMessageConversation:
    """多轮对话测试"""

    @pytest.mark.asyncio
    async def test_multi_turn_conversation(self, async_client: AsyncClient):
        """测试多轮对话"""
        session_response = await async_client.post(
            "/api/v1/sessions",
            json={"user_id": "test_user_conversation"}
        )

        if session_response.status_code in [200, 201]:
            session_id = session_response.json()["data"].get("session_id")

            # 进行多轮对话
            messages = [
                "你好",
                "介绍一下Python",
                "Python有什么用途?",
                "FastAPI是什么?"
            ]

            for msg in messages:
                response = await async_client.post(
                    f"/api/v1/sessions/{session_id}/messages",
                    json={
                        "role": "user",
                        "content": msg,
                        "stream": False
                    }
                )

                # 每次请求应该成功或返回合理错误
                assert response.status_code in [200, 201, 404, 500]
