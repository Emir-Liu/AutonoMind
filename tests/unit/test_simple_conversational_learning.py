"""
简化版对话式学习引擎单元测试 - 不依赖数据库
"""

import pytest
from unittest.mock import Mock, AsyncMock, MagicMock
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "code"))


@pytest.mark.unit
class TestLearningIntent:
    """学习意图枚举测试"""

    def test_intent_values(self):
        """测试意图枚举值"""
        from core.conversational_learning.interfaces import LearningIntent

        assert LearningIntent.ADD.value == "add"
        assert LearningIntent.CORRECT.value == "correct"
        assert LearningIntent.SUPPLEMENT.value == "supplement"
        assert LearningIntent.DELETE.value == "delete"
        assert LearningIntent.MERGE.value == "merge"
        assert LearningIntent.NONE.value == "none"

    def test_intent_count(self):
        """测试意图数量"""
        from core.conversational_learning.interfaces import LearningIntent

        assert len(list(LearningIntent)) == 6


@pytest.mark.unit
class TestKnowledgeExtraction:
    """知识提取测试"""

    def test_knowledge_extraction_creation(self):
        """测试知识提取对象创建"""
        from core.conversational_learning.interfaces import KnowledgeExtractionResult

        extraction = KnowledgeExtractionResult(
            title="测试标题",
            knowledge="测试知识",
            content="详细内容",
            source="test",
            confidence=0.95,
            metadata={"category": "test"}
        )

        assert extraction.knowledge == "测试知识"
        assert extraction.confidence == 0.95
        assert extraction.metadata["category"] == "test"


@pytest.mark.unit
class TestLearningIntentResult:
    """学习意图结果测试"""

    def test_learning_intent_result_creation(self):
        """测试学习意图结果创建"""
        from core.conversational_learning.interfaces import LearningIntentResult, LearningIntent

        result = LearningIntentResult(
            intent=LearningIntent.ADD,
            confidence=0.90,
            reasoning="用户明确要求记住新知识"
        )

        assert result.intent == LearningIntent.ADD
        assert result.confidence == 0.90
        assert result.reasoning == "用户明确要求记住新知识"
