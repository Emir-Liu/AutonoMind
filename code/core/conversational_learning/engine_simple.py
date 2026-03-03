"""
简化版对话式知识学习引擎实现 - 用于测试
"""

import json
from typing import Dict, Any, Optional, List
from datetime import datetime

from core.conversational_learning.interfaces import (
    IConversationLearningEngine,
    LearningIntent,
    LearningIntentResult,
    KnowledgeExtractionResult,
)


class ConversationalLearningEngine(IConversationLearningEngine):
    """对话式知识学习引擎简化实现"""

    def __init__(self, llm_client=None, model="gpt-4"):
        self.llm_client = llm_client
        self.model = model

    # ========== 学习意图检测 ==========

    async def detect_learning_intent(
        self,
        user_message: str,
        assistant_message: str = "",
        conversation_history: Optional[List[Dict[str, Any]]] = None,
    ) -> LearningIntentResult:
        """检测学习意图"""

        # 如果有LLM客户端,使用LLM检测
        if self.llm_client:
            prompt = self._build_intent_detection_prompt(
                user_message, assistant_message, conversation_history
            )

            try:
                response = await self.llm_client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1,
                    response_format={"type": "json_object"},
                )

                result = json.loads(response.choices[0].message.content)
                intent = result.get("intent", LearningIntent.NONE)
                confidence = float(result.get("confidence", 0.0))
                reasoning = result.get("reasoning", "")

                # 验证意图有效性
                valid_intents = [
                    LearningIntent.ADD,
                    LearningIntent.CORRECT,
                    LearningIntent.SUPPLEMENT,
                    LearningIntent.DELETE,
                    LearningIntent.MERGE,
                    LearningIntent.NONE,
                ]

                if intent not in valid_intents:
                    intent = LearningIntent.NONE
                    confidence = 0.0

                return LearningIntentResult(
                    intent=intent,
                    confidence=confidence,
                    reasoning=reasoning
                )

            except Exception as e:
                # 出错时返回默认结果
                return LearningIntentResult(
                    intent=LearningIntent.NONE,
                    confidence=0.0,
                    reasoning=f"检测失败: {str(e)}"
                )

        # 如果没有LLM客户端,使用简单的关键词匹配
        return self._detect_intent_by_keywords(user_message)

    def _detect_intent_by_keywords(self, user_message: str) -> LearningIntentResult:
        """使用关键词匹配检测意图"""

        user_msg_lower = user_message.lower()

        # 定义关键词映射
        keyword_patterns = {
            LearningIntent.ADD: ["记住", "添加", "新增", "学习", "记下"],
            LearningIntent.CORRECT: ["纠正", "更正", "修改", "错误"],
            LearningIntent.SUPPLEMENT: ["补充", "加上", "补充一下"],
            LearningIntent.DELETE: ["删除", "忘掉", "去掉"],
            LearningIntent.MERGE: ["合并", "整合"],
        }

        # 检查关键词
        for intent, keywords in keyword_patterns.items():
            if any(keyword in user_msg_lower for keyword in keywords):
                return LearningIntentResult(
                    intent=intent,
                    confidence=0.75,
                    reasoning=f"检测到关键词"
                )

        # 默认无学习意图
        return LearningIntentResult(
            intent=LearningIntent.NONE,
            confidence=0.90,
            reasoning="未检测到学习意图关键词"
        )

    def _build_intent_detection_prompt(
        self,
        user_message: str,
        assistant_message: str,
        conversation_history: Optional[List[Dict[str, Any]]]
    ) -> str:
        """构建意图检测提示词"""

        prompt = f"""分析以下对话,判断用户是否有学习意图。

用户消息: {user_message}
助手回复: {assistant_message}

请判断用户的学习意图,返回JSON格式:
{{
    "intent": "add/correct/supplement/delete/merge/none",
    "confidence": 0.0-1.0,
    "reasoning": "判断理由"
}}
"""
        return prompt

    # ========== 知识提取 ==========

    async def extract_knowledge(
        self,
        user_message: str,
        intent: str,
        conversation_history: Optional[List[Dict[str, Any]]] = None,
    ) -> KnowledgeExtractionResult:
        """提取知识"""

        # 如果有LLM客户端,使用LLM提取
        if self.llm_client:
            prompt = self._build_knowledge_extraction_prompt(
                user_message, intent, conversation_history
            )

            try:
                response = await self.llm_client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    response_format={"type": "json_object"},
                )

                result = json.loads(response.choices[0].message.content)

                return KnowledgeExtractionResult(
                    title=result.get("title", ""),
                    knowledge=result.get("knowledge", ""),
                    content=result.get("content", ""),
                    source="conversation",
                    knowledge_id=result.get("knowledge_id"),
                    confidence=float(result.get("confidence", 0.0)),
                    metadata=result.get("metadata", {})
                )

            except Exception as e:
                # 出错时返回空结果
                return KnowledgeExtractionResult(
                    title="",
                    knowledge="",
                    content="",
                    source="conversation",
                    confidence=0.0,
                    metadata={"error": str(e)}
                )

        # 如果没有LLM客户端,简单提取
        return self._extract_knowledge_simple(user_message, intent)

    def _extract_knowledge_simple(
        self,
        user_message: str,
        intent: str
    ) -> KnowledgeExtractionResult:
        """简单知识提取"""

        # 根据意图提取知识
        if intent == LearningIntent.ADD:
            # 提取"记住"或"添加"之后的内容
            for keyword in ["记住:", "记住", "添加:", "添加", "新增:", "新增"]:
                if keyword in user_message:
                    content = user_message.split(keyword, 1)[-1].strip()
                    return KnowledgeExtractionResult(
                        title="对话学习",
                        knowledge=content,
                        content=content,
                        source="conversation",
                        confidence=0.70,
                        metadata={"intent": intent}
                    )

        elif intent == LearningIntent.CORRECT:
            # 提取纠正内容
            for keyword in ["纠正:", "纠正", "更正:", "更正"]:
                if keyword in user_message:
                    content = user_message.split(keyword, 1)[-1].strip()
                    return KnowledgeExtractionResult(
                        title="对话纠正",
                        knowledge=content,
                        content=content,
                        source="conversation",
                        knowledge_id=None,
                        confidence=0.70,
                        metadata={"intent": intent}
                    )

        # 默认返回空
        return KnowledgeExtractionResult(
            title="",
            knowledge="",
            content="",
            source="conversation",
            confidence=0.0,
            metadata={}
        )

    def _build_knowledge_extraction_prompt(
        self,
        user_message: str,
        intent: str,
        conversation_history: Optional[List[Dict[str, Any]]]
    ) -> str:
        """构建知识提取提示词"""

        prompt = f"""从以下用户消息中提取知识。

用户消息: {user_message}
学习意图: {intent}

请提取知识,返回JSON格式:
{{
    "title": "知识标题",
    "knowledge": "知识摘要",
    "content": "详细内容",
    "confidence": 0.0-1.0,
    "metadata": {{}}
}}
"""
        return prompt

    # ========== 冲突检测 ==========

    async def check_conflict(
        self,
        new_knowledge: str,
        existing_knowledges: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """检测知识冲突"""

        # 如果有LLM客户端,使用LLM检测
        if self.llm_client:
            prompt = self._build_conflict_detection_prompt(
                new_knowledge, existing_knowledges
            )

            try:
                response = await self.llm_client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1,
                    response_format={"type": "json_object"},
                )

                return json.loads(response.choices[0].message.content)

            except Exception as e:
                return {
                    "has_conflict": False,
                    "conflict_reason": f"检测失败: {str(e)}",
                    "existing_knowledge_id": None
                }

        # 简单检测:检查是否有完全相同的
        for knowledge in existing_knowledges:
            if knowledge.get("content") == new_knowledge:
                return {
                    "has_conflict": True,
                    "conflict_reason": "知识完全相同",
                    "existing_knowledge_id": knowledge.get("id")
                }

        return {
            "has_conflict": False,
            "conflict_reason": None,
            "existing_knowledge_id": None
        }

    def _build_conflict_detection_prompt(
        self,
        new_knowledge: str,
        existing_knowledges: List[Dict[str, Any]]
    ) -> str:
        """构建冲突检测提示词"""

        existing_text = "\n".join([
            f"- ID: {k.get('id')}, 内容: {k.get('content')}"
            for k in existing_knowledges[:5]  # 只取前5条
        ])

        prompt = f"""检测新知识是否与现有知识冲突。

新知识: {new_knowledge}

现有知识:
{existing_text}

请检测冲突,返回JSON格式:
{{
    "has_conflict": true/false,
    "conflict_reason": "冲突原因",
    "existing_knowledge_id": "冲突知识的ID"
}}
"""
        return prompt

    # ========== 学习处理 ==========

    async def process_learning(
        self,
        user_message: str,
        assistant_message: str = "",
        conversation_history: Optional[List[Dict[str, Any]]] = None,
        existing_knowledges: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """处理学习流程"""

        # 1. 检测意图
        intent_result = await self.detect_learning_intent(
            user_message, assistant_message, conversation_history
        )

        if intent_result.intent == LearningIntent.NONE:
            return {
                "success": False,
                "action": "none",
                "knowledge": None,
                "knowledge_id": None,
                "message": "未检测到学习意图"
            }

        # 2. 提取知识
        extraction_result = await self.extract_knowledge(
            user_message, intent_result.intent, conversation_history
        )

        if not extraction_result.knowledge:
            return {
                "success": False,
                "action": intent_result.intent,
                "knowledge": None,
                "knowledge_id": None,
                "message": "未能提取知识"
            }

        # 3. 检测冲突
        if existing_knowledges:
            conflict_result = await self.check_conflict(
                extraction_result.knowledge, existing_knowledges
            )

            if conflict_result["has_conflict"]:
                return {
                    "success": False,
                    "action": intent_result.intent,
                    "knowledge": extraction_result.knowledge,
                    "knowledge_id": None,
                    "message": f"知识冲突: {conflict_result['conflict_reason']}"
                }

        # 4. 返回成功结果
        return {
            "success": True,
            "action": intent_result.intent,
            "knowledge": extraction_result.knowledge,
            "knowledge_id": f"kno_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "message": "知识处理成功",
            "metadata": extraction_result.metadata
        }
