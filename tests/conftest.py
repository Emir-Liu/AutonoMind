"""
测试配置文件 - 提供测试所需的fixture和配置
"""

import pytest
import asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import Mock, AsyncMock, MagicMock
from httpx import AsyncClient, ASGITransport

# 导入主应用
import sys
from pathlib import Path

# 将code目录添加到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "code"))

# 尝试导入主应用,如果失败则设置None(用于单元测试)
try:
    from main import app
except ImportError:
    app = None
    # 不抛出异常,让测试可以继续


@pytest.fixture
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """异步HTTP客户端"""
    if app is None:
        pytest.skip("需要安装数据库依赖才能运行集成测试")
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client


@pytest.fixture
def mock_llm_client():
    """模拟LLM客户端"""
    mock = AsyncMock()
    mock.chat.completions.create = AsyncMock()
    return mock


@pytest.fixture
def mock_embedding_client():
    """模拟嵌入客户端"""
    mock = AsyncMock()
    mock.embeddings.create = AsyncMock(return_value=MagicMock(
        data=[MagicMock(embedding=[0.1] * 1536)]
    ))
    return mock


@pytest.fixture
def mock_qdrant_client():
    """模拟Qdrant客户端"""
    mock = Mock()
    mock.upsert = MagicMock()
    mock.search = MagicMock(return_value=[
        MagicMock(
            id="test_id",
            score=0.95,
            payload={
                "content": "测试知识内容",
                "metadata": {}
            }
        )
    ])
    mock.delete = MagicMock()
    mock.count = MagicMock(return_value=MagicMock(count=10))
    return mock


@pytest.fixture
def sample_knowledge_data():
    """示例知识数据"""
    return {
        "content": "FastAPI 是一个高性能的 Python Web 框架",
        "source": "manual",
        "metadata": {
            "category": "technology",
            "tags": ["python", "fastapi"]
        }
    }


@pytest.fixture
def sample_session_data():
    """示例会话数据"""
    return {
        "user_id": "test_user_001",
        "agent_config": {
            "llm_provider": "openai",
            "llm_model": "gpt-4",
            "temperature": 0.7,
            "max_tokens": 2000
        },
        "metadata": {
            "source": "web",
            "tags": ["test"]
        }
    }


@pytest.fixture
def sample_message_data():
    """示例消息数据"""
    return {
        "role": "user",
        "content": "帮我查询一下Python FastAPI的性能特点",
        "stream": False
    }


@pytest.fixture
def auth_headers():
    """认证请求头"""
    return {
        "Authorization": "Bearer test_token_12345",
        "Content-Type": "application/json"
    }


@pytest.fixture
def test_user_token():
    """测试用户token"""
    return "test_jwt_token_for_testing"


# Pytest配置
def pytest_configure(config):
    """Pytest配置"""
    config.addinivalue_line(
        "markers", "unit: 标记单元测试"
    )
    config.addinivalue_line(
        "markers", "integration: 标记集成测试"
    )
    config.addinivalue_line(
        "markers", "e2e: 标记端到端测试"
    )
    config.addinivalue_line(
        "markers", "slow: 标记慢速测试"
    )
