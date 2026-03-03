"""对话式知识学习模块

这是 AutonoMind 的核心功能，支持通过对话自动学习新知识
"""

from core.conversational_learning.interfaces import (
    IConversationLearningEngine,
    LearningIntent,
    LearningIntentResult,
    KnowledgeExtractionResult,
)

# 尝试导入完整版本,失败则导入简化版本
ConversationLearningEngine = None
try:
    from core.conversational_learning.engine import ConversationLearningEngine
except ImportError:
    try:
        from core.conversational_learning.engine_simple import ConversationalLearningEngine
    except ImportError:
        pass

# 导出简化版本供测试使用
from core.conversational_learning.engine_simple import ConversationalLearningEngine as SimpleConversationalLearningEngine

__all__ = [
    "IConversationLearningEngine",
    "ConversationLearningEngine",
    "SimpleConversationalLearningEngine",
    "LearningIntent",
    "LearningIntentResult",
    "KnowledgeExtractionResult",
]


