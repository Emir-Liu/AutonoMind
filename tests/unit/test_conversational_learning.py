"""
对话式学习引擎单元测试
"""

import pytest
from unittest.mock import Mock, AsyncMock, MagicMock
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "code"))

from core.conversational_learning.engine import ConversationalLearningEngine
from core.conversational_learning.interfaces import (
    LearningIntent,
    KnowledgeExtraction,
    LearningResult
)


@pytest.mark.unit
class TestConversationalLearningEngine:
    """对话式学习引擎测试"""

    @pytest.fixture
    def mock_llm_client(self):
        """模拟LLM客户端"""
        mock = AsyncMock()
        mock.chat.completions.create = AsyncMock()
        return mock

    @pytest.fixture
    def learning_engine(self, mock_llm_client):
        """创建学习引擎实例"""
        return ConversationalLearningEngine(
            llm_client=mock_llm_client,
            model="gpt-4"
        )

    async def test_detect_learning_intent_add(self, learning_engine, mock_llm_client):
        """测试检测新增知识意图"""
        # 模拟LLM返回
        mock_llm_client.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content='{"intent": "add", "confidence": 0.95}'))]
        )

        user_input = "记住这个知识: FastAPI是Python的高性能框架"
        intent = await learning_engine.detect_learning_intent(user_input)

        assert intent.intent == LearningIntent.ADD
        assert intent.confidence == 0.95
        mock_llm_client.chat.completions.create.assert_called_once()

    async def test_detect_learning_intent_correct(self, learning_engine, mock_llm_client):
        """测试检测纠正知识意图"""
        mock_llm_client.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content='{"intent": "correct", "confidence": 0.88}'))]
        )

        user_input = "纠正一下,刚才说的不对"
        intent = await learning_engine.detect_learning_intent(user_input)

        assert intent.intent == LearningIntent.CORRECT
        assert intent.confidence == 0.88

    async def test_detect_learning_intent_none(self, learning_engine, mock_llm_client):
        """测试检测无学习意图"""
        mock_llm_client.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content='{"intent": "none", "confidence": 0.90}'))]
        )

        user_input = "你好,今天天气怎么样?"
        intent = await learning_engine.detect_learning_intent(user_input)

        assert intent.intent == LearningIntent.NONE
        assert intent.confidence == 0.90

    async def test_extract_knowledge_add(self, learning_engine, mock_llm_client):
        """测试提取新增知识"""
        mock_llm_client.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content='''{
                "knowledge": "FastAPI是一个高性能的Python Web框架",
                "confidence": 0.92,
                "metadata": {
                    "category": "technology",
                    "tags": ["python", "fastapi"]
                }
            }'''))]
        )

        user_input = "记住: FastAPI是一个高性能的Python Web框架"
        extraction = await learning_engine.extract_knowledge(
            user_input,
            intent=LearningIntent.ADD
        )

        assert isinstance(extraction, KnowledgeExtraction)
        assert extraction.knowledge == "FastAPI是一个高性能的Python Web框架"
        assert extraction.confidence == 0.92
        assert extraction.metadata["category"] == "technology"

    async def test_extract_knowledge_correct(self, learning_engine, mock_llm_client):
        """测试提取纠正知识"""
        mock_llm_client.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content='''{
                "knowledge_id": "kno_001",
                "corrected_knowledge": "FastAPI基于Starlette构建",
                "confidence": 0.85,
                "reason": "更准确的描述"
            }'''))]
        )

        user_input = "纠正kno_001: FastAPI基于Starlette构建"
        extraction = await learning_engine.extract_knowledge(
            user_input,
            intent=LearningIntent.CORRECT
        )

        assert extraction.knowledge_id == "kno_001"
        assert extraction.corrected_knowledge == "FastAPI基于Starlette构建"
        assert extraction.reason == "更准确的描述"

    async def test_check_conflict(self, learning_engine, mock_llm_client):
        """测试知识冲突检测"""
        mock_llm_client.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content='''{
                "has_conflict": true,
                "conflict_reason": "性能指标数据不一致",
                "existing_knowledge_id": "kno_005"
            }'''))]
        )

        new_knowledge = "FastAPI性能是10000 req/s"
        existing_knowledges = [
            {"id": "kno_005", "content": "FastAPI性能是5000 req/s"}
        ]

        has_conflict = await learning_engine.check_conflict(
            new_knowledge,
            existing_knowledges
        )

        assert has_conflict["has_conflict"] is True
        assert has_conflict["existing_knowledge_id"] == "kno_005"

    async def test_no_conflict(self, learning_engine, mock_llm_client):
        """测试无冲突情况"""
        mock_llm_client.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content='''{
                "has_conflict": false,
                "conflict_reason": null,
                "existing_knowledge_id": null
            }'''))]
        )

        new_knowledge = "FastAPI使用异步编程"
        existing_knowledges = []

        has_conflict = await learning_engine.check_conflict(
            new_knowledge,
            existing_knowledges
        )

        assert has_conflict["has_conflict"] is False

    async def test_process_learning_add_success(self, learning_engine, mock_llm_client):
        """测试处理学习-新增成功"""
        # 设置模拟返回
        mock_llm_client.chat.completions.create.side_effect = [
            # 第一次调用: 检测意图
            MagicMock(choices=[MagicMock(message=MagicMock(content='{"intent": "add", "confidence": 0.95}'))]),
            # 第二次调用: 提取知识
            MagicMock(choices=[MagicMock(message=MagicMock(content='''{
                "knowledge": "测试知识内容",
                "confidence": 0.90,
                "metadata": {}
            }'''))]),
            # 第三次调用: 检测冲突
            MagicMock(choices=[MagicMock(message=MagicMock(content='''{
                "has_conflict": false,
                "conflict_reason": null,
                "existing_knowledge_id": null
            }'''))])
        ]

        user_input = "记住这个: 测试知识内容"
        result = await learning_engine.process_learning(
            user_input,
            existing_knowledges=[]
        )

        assert result.success is True
        assert result.action == "add"
        assert result.knowledge == "测试知识内容"

    async def test_process_learning_no_intent(self, learning_engine, mock_llm_client):
        """测试处理学习-无意图"""
        mock_llm_client.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content='{"intent": "none", "confidence": 0.90}'))]
        )

        user_input = "你好,今天天气怎么样?"
        result = await learning_engine.process_learning(user_input)

        assert result.success is False
        assert result.action == "none"
        assert result.knowledge is None


@pytest.mark.unit
class TestLearningIntent:
    """学习意图枚举测试"""

    def test_intent_values(self):
        """测试意图枚举值"""
        assert LearningIntent.ADD.value == "add"
        assert LearningIntent.CORRECT.value == "correct"
        assert LearningIntent.SUPPLEMENT.value == "supplement"
        assert LearningIntent.DELETE.value == "delete"
        assert LearningIntent.MERGE.value == "merge"
        assert LearningIntent.NONE.value == "none"

    def test_intent_count(self):
        """测试意图数量"""
        assert len(list(LearningIntent)) == 6


@pytest.mark.unit
class TestKnowledgeExtraction:
    """知识提取测试"""

    def test_knowledge_extraction_creation(self):
        """测试知识提取对象创建"""
        extraction = KnowledgeExtraction(
            knowledge="测试知识",
            confidence=0.95,
            metadata={"category": "test"}
        )

        assert extraction.knowledge == "测试知识"
        assert extraction.confidence == 0.95
        assert extraction.metadata["category"] == "test"


@pytest.mark.unit
class TestLearningResult:
    """学习结果测试"""

    def test_learning_result_success(self):
        """测试成功的学习结果"""
        result = LearningResult(
            success=True,
            action="add",
            knowledge="测试知识",
            knowledge_id="kno_001",
            message="知识添加成功"
        )

        assert result.success is True
        assert result.action == "add"
        assert result.knowledge == "测试知识"

    def test_learning_result_failure(self):
        """测试失败的学习结果"""
        result = LearningResult(
            success=False,
            action="none",
            knowledge=None,
            knowledge_id=None,
            message="未检测到学习意图"
        )

        assert result.success is False
        assert result.knowledge is None
