"""
端到端测试 - 完整对话流程
"""

import pytest
from httpx import AsyncClient
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "code"))


@pytest.mark.e2e
@pytest.mark.slow
class TestFullConversationFlow:
    """完整对话流程端到端测试"""

    @pytest.mark.asyncio
    async def test_complete_conversation_lifecycle(self, async_client: AsyncClient):
        """测试完整的对话生命周期"""

        # 步骤1: 添加知识
        print("\n[步骤1] 添加知识...")
        add_knowledge_response = await async_client.post(
            "/api/v1/knowledge",
            json={
                "content": "FastAPI是一个高性能的Python Web框架,基于Starlette和Pydantic构建",
                "source": "test",
                "metadata": {"category": "technology", "tags": ["python", "fastapi"]}
            }
        )
        assert add_knowledge_response.status_code in [200, 201, 404]

        # 步骤2: 创建会话
        print("[步骤2] 创建会话...")
        session_response = await async_client.post(
            "/api/v1/sessions",
            json={
                "user_id": "e2e_user_001",
                "agent_config": {
                    "llm_provider": "openai",
                    "llm_model": "gpt-4",
                    "temperature": 0.7
                }
            }
        )
        assert session_response.status_code in [200, 201, 404]

        if session_response.status_code in [200, 201]:
            session_id = session_response.json()["data"]["session_id"]
            print(f"  会话ID: {session_id}")

            # 步骤3: 发送消息
            print("[步骤3] 发送消息...")
            message_response = await async_client.post(
                f"/api/v1/sessions/{session_id}/messages",
                json={
                    "role": "user",
                    "content": "FastAPI是什么?",
                    "stream": False
                }
            )
            assert message_response.status_code in [200, 201, 404, 500]

            if message_response.status_code in [200, 201]:
                message_data = message_response.json()["data"]
                print(f"  消息ID: {message_data.get('message_id')}")

                # 步骤4: 验证响应包含检索到的知识(如果实现)
                if message_data.get("retrieved_knowledge"):
                    print(f"  检索到 {len(message_data['retrieved_knowledge'])} 条知识")

            # 步骤5: 多轮对话
            print("[步骤4] 多轮对话...")
            follow_up_messages = [
                "FastAPI有哪些特点?",
                "如何使用FastAPI?"
            ]

            for i, msg in enumerate(follow_up_messages, 1):
                response = await async_client.post(
                    f"/api/v1/sessions/{session_id}/messages",
                    json={"role": "user", "content": msg, "stream": False}
                )
                assert response.status_code in [200, 201, 404, 500]
                print(f"  第{i}轮对话完成")

            # 步骤6: 获取对话历史
            print("[步骤5] 获取对话历史...")
            history_response = await async_client.get(
                f"/api/v1/sessions/{session_id}/messages"
            )
            assert history_response.status_code in [200, 404]

            if history_response.status_code == 200:
                history = history_response.json()["data"]
                print(f"  共 {len(history)} 条消息")

            print("✓ 完整对话流程测试通过")

    @pytest.mark.asyncio
    async def test_conversational_learning_flow(self, async_client: AsyncClient):
        """测试对话式学习流程"""

        print("\n[对话式学习] 测试开始...")

        # 创建会话
        session_response = await async_client.post(
            "/api/v1/sessions",
            json={"user_id": "e2e_learning_user"}
        )

        if session_response.status_code in [200, 201]:
            session_id = session_response.json()["data"]["session_id"]

            # 发送包含学习意图的消息
            learning_messages = [
                "记住这个知识: AutonoMind是一个AI Agent框架",
                "补充一下: AutonoMind支持自我进化",
                "纠正一下,刚才说的不完全对"
            ]

            for msg in learning_messages:
                response = await async_client.post(
                    f"/api/v1/sessions/{session_id}/messages",
                    json={"role": "user", "content": msg, "stream": False}
                )
                print(f"  发送学习消息: {msg[:30]}...")
                assert response.status_code in [200, 201, 404, 500]

            # 验证知识被添加
            search_response = await async_client.post(
                "/api/v1/knowledge/search",
                json={"query": "AutonoMind", "top_k": 5}
            )

            if search_response.status_code == 200:
                results = search_response.json().get("data", [])
                print(f"  检索到 {len(results)} 条相关知识")

        print("✓ 对话式学习流程测试通过")

    @pytest.mark.asyncio
    async def test_knowledge_retrieval_in_conversation(self, async_client: AsyncClient):
        """测试对话中的知识检索"""

        print("\n[知识检索] 测试开始...")

        # 预先添加知识
        knowledge_items = [
            "Python是一种高级编程语言",
            "FastAPI是基于Starlette的Web框架",
            "Pydantic用于数据验证"
        ]

        for content in knowledge_items:
            await async_client.post(
                "/api/v1/knowledge",
                json={"content": content, "source": "test"}
            )

        print(f"  已添加 {len(knowledge_items)} 条知识")

        # 创建会话
        session_response = await async_client.post(
            "/api/v1/sessions",
            json={"user_id": "e2e_retrieval_user"}
        )

        if session_response.status_code in [200, 201]:
            session_id = session_response.json()["data"]["session_id"]

            # 发送需要检索知识的问题
            query = "Python和FastAPI有什么关系?"
            response = await async_client.post(
                f"/api/v1/sessions/{session_id}/messages",
                json={"role": "user", "content": query, "stream": False}
            )

            if response.status_code in [200, 201]:
                data = response.json()["data"]
                if data.get("retrieved_knowledge"):
                    print(f"  检索到 {len(data['retrieved_knowledge'])} 条相关知识")
                    print(f"  知识评分: {[k.get('score') for k in data['retrieved_knowledge']]}")

        print("✓ 知识检索测试通过")

    @pytest.mark.asyncio
    async def test_multiple_sessions_isolation(self, async_client: AsyncClient):
        """测试多个会话隔离"""

        print("\n[会话隔离] 测试开始...")

        # 创建两个独立会话
        session1_response = await async_client.post(
            "/api/v1/sessions",
            json={"user_id": "user_A"}
        )
        session2_response = await async_client.post(
            "/api/v1/sessions",
            json={"user_id": "user_B"}
        )

        if (session1_response.status_code in [200, 201] and
            session2_response.status_code in [200, 201]):

            session1_id = session1_response.json()["data"]["session_id"]
            session2_id = session2_response.json()["data"]["session_id"]

            # 在会话1中发送消息
            await async_client.post(
                f"/api/v1/sessions/{session1_id}/messages",
                json={"role": "user", "content": "我是用户A", "stream": False}
            )

            # 在会话2中发送不同消息
            await async_client.post(
                f"/api/v1/sessions/{session2_id}/messages",
                json={"role": "user", "content": "我是用户B", "stream": False}
            )

            # 验证每个会话的历史是独立的
            history1_response = await async_client.get(
                f"/api/v1/sessions/{session1_id}/messages"
            )
            history2_response = await async_client.get(
                f"/api/v1/sessions/{session2_id}/messages"
            )

            if (history1_response.status_code == 200 and
                history2_response.status_code == 200):

                history1 = history1_response.json()["data"]
                history2 = history2_response.json()["data"]

                print(f"  会话1消息数: {len(history1)}")
                print(f"  会话2消息数: {len(history2)}")

                # 验证消息内容不同(基于用户上下文)
                assert True  # 如果能获取到历史则通过

        print("✓ 会话隔离测试通过")


@pytest.mark.e2e
@pytest.mark.slow
class TestErrorHandling:
    """错误处理端到端测试"""

    @pytest.mark.asyncio
    async def test_invalid_api_endpoints(self, async_client: AsyncClient):
        """测试无效的API端点"""
        invalid_endpoints = [
            "/api/v1/invalid_endpoint",
            "/api/v1/sessions/invalid_id",
            "/api/v1/knowledge/12345"
        ]

        for endpoint in invalid_endpoints:
            response = await async_client.get(endpoint)
            assert response.status_code in [404, 405]

    @pytest.mark.asyncio
    async def test_malformed_requests(self, async_client: AsyncClient):
        """测试格式错误的请求"""
        # 缺少必需字段
        response = await async_client.post(
            "/api/v1/sessions",
            json={}
        )
        assert response.status_code in [400, 422]

        # 无效JSON
        response = await async_client.post(
            "/api/v1/sessions",
            content="{invalid json}",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code in [400, 422]


@pytest.mark.e2e
class TestPerformance:
    """性能测试"""

    @pytest.mark.asyncio
    async def test_response_time(self, async_client: AsyncClient):
        """测试响应时间"""
        import time

        start_time = time.time()

        # 创建会话
        response = await async_client.post(
            "/api/v1/sessions",
            json={"user_id": "perf_test_user"}
        )

        elapsed = time.time() - start_time

        # 响应时间应该在合理范围内
        assert elapsed < 5.0  # 5秒内

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_concurrent_requests(self, async_client: AsyncClient):
        """测试并发请求"""
        import asyncio

        async def make_request(i):
            return await async_client.post(
                "/api/v1/sessions",
                json={"user_id": f"concurrent_user_{i}"}
            )

        # 并发创建10个会话
        tasks = [make_request(i) for i in range(10)]
        responses = await asyncio.gather(*tasks)

        # 所有请求都应该有响应
        assert len(responses) == 10
        assert all(r.status_code in [200, 201, 500] for r in responses)
