"""对话式知识学习接口定义

定义对话式知识学习引擎的抽象接口
这是 AutonoMind 的核心功能模块，支持通过对话自动学习新知识
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime


class LearningIntent:
    """学习意图枚举"""

    ADD = "add"  # 新增知识
    CORRECT = "correct"  # 纠正错误
    SUPPLEMENT = "supplement"  # 补充信息
    DELETE = "delete"  # 删除知识
    MERGE = "merge"  # 合并知识
    NONE = "none"  # 无学习意图


class LearningIntentResult:
    """学习意图识别结果"""

    def __init__(
        self,
        intent: str,
        confidence: float,
        reasoning: str,
    ):
        self.intent = intent
        self.confidence = confidence
        self.reasoning = reasoning


class KnowledgeExtractionResult:
    """知识提取结果"""

    def __init__(
        self,
        title: str,
        content: str,
        source: str,
        knowledge_id: Optional[int] = None,
        confidence: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.title = title
        self.content = content
        self.source = source
        self.knowledge_id = knowledge_id
        self.confidence = confidence
        self.metadata = metadata or {}


class IConversationLearningEngine(ABC):
    """对话式知识学习引擎接口

    职责: 从对话中识别学习意图，提取新知识，更新知识库
    """

    @abstractmethod
    async def detect_learning_intent(
        self,
        user_message: str,
        assistant_message: str,
        conversation_history: Optional[List[Dict[str, Any]]] = None,
    ) -> LearningIntentResult:
        """检测学习意图

        Args:
            user_message: 用户消息
            assistant_message: 助手回复
            conversation_history: 对话历史

        Returns:
            LearningIntentResult: 学习意图识别结果
        """
        pass

    @abstractmethod
    async def extract_knowledge(
        self,
        user_message: str,
        assistant_message: str,
        intent: str,
        conversation_history: Optional[List[Dict[str, Any]]] = None,
    ) -> List[KnowledgeExtractionResult]:
        """从对话中提取知识

        Args:
            user_message: 用户消息
            assistant_message: 助手回复
            intent: 学习意图
            conversation_history: 对话历史

        Returns:
            List[KnowledgeExtractionResult]: 提取的知识列表
        """
        pass

    @abstractmethod
    async def detect_knowledge_conflicts(
        self,
        new_knowledge: KnowledgeExtractionResult,
        existing_knowledge: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """检测知识冲突

        Args:
            new_knowledge: 新提取的知识
            existing_knowledge: 现有知识列表

        Returns:
            List[Dict]: 冲突列表
            [{
                "knowledge_id": 123,
                "conflict_type": "contradiction",
                "description": "冲突描述",
                "severity": "high"
            }]
        """
        pass

    @abstractmethod
    async def process_learning(
        self,
        user_message: str,
        assistant_message: str,
        conversation_history: Optional[List[Dict[str, Any]]] = None,
        auto_approve: bool = False,
    ) -> Dict[str, Any]:
        """处理对话式学习完整流程

        Args:
            user_message: 用户消息
            assistant_message: 助手回复
            conversation_history: 对话历史
            auto_approve: 是否自动批准（跳过人工审核）

        Returns:
            Dict: 学习处理结果
            {
                "success": True,
                "intent": "correct",
                "knowledge_extracted": [...],
                "conflicts": [],
                "status": "approved",  # pending/approved/rejected
                "new_knowledge_ids": [1, 2]
            }
        """
        pass

    @abstractmethod
    async def approve_knowledge(
        self,
        learning_record_id: int,
    ) -> bool:
        """批准学习的知识

        Args:
            learning_record_id: 学习记录ID

        Returns:
            bool: 成功返回True
        """
        pass

    @abstractmethod
    async def reject_knowledge(
        self,
        learning_record_id: int,
        reason: str,
    ) -> bool:
        """拒绝学习的知识

        Args:
            learning_record_id: 学习记录ID
            reason: 拒绝原因

        Returns:
            bool: 成功返回True
        """
        pass

    @abstractmethod
    async def get_learning_statistics(
        self,
        user_id: int,
        days: int = 30,
    ) -> Dict[str, Any]:
        """获取学习统计信息

        Args:
            user_id: 用户ID
            days: 统计天数

        Returns:
            Dict: 学习统计信息
            {
                "total_learned": 10,
                "approved": 8,
                "rejected": 1,
                "pending": 1,
                "accuracy": 0.8,
                "by_intent": {
                    "add": 5,
                    "correct": 3,
                    "supplement": 2
                }
            }
        """
        pass
