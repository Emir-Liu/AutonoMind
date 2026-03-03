"""对话式知识学习引擎实现

基于LLM实现对话式知识学习，支持意图识别、知识提取、冲突检测
"""

import json
from typing import Dict, Any, Optional, List
from datetime import datetime

# 简化导入以支持测试
try:
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy import select, and_
    from models.database import (
        LearningRecord as LearningRecordModel,
        Knowledge as KnowledgeModel,
    )
    from utils.logger import logger
    from utils.llm import LLMManager
except ImportError:
    # 测试环境下的模拟导入
    AsyncSession = None
    LearningRecordModel = None
    KnowledgeModel = None
    logger = None
    LLMManager = None

from core.conversational_learning.interfaces import (
    IConversationLearningEngine,
    LearningIntent,
    LearningIntentResult,
    KnowledgeExtractionResult,
)


class ConversationLearningEngine(IConversationLearningEngine):
    """对话式知识学习引擎实现"""

    def __init__(self, db_session: AsyncSession = None, llm_manager: LLMManager = None):
        self.db = db_session
        self.llm = llm_manager

    """对话式知识学习引擎实现"""

    def __init__(self, db_session: AsyncSession, llm_manager: LLMManager):
        self.db = db_session
        self.llm = llm_manager

    # ========== 学习意图检测 ==========

    async def detect_learning_intent(
        self,
        user_message: str,
        assistant_message: str,
        conversation_history: Optional[List[Dict[str, Any]]] = None,
    ) -> LearningIntentResult:
        """检测学习意图"""

        prompt = self._build_intent_detection_prompt(
            user_message, assistant_message, conversation_history
        )

        try:
            response = await self.llm.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,  # 低温度保证一致性
                response_format={"type": "json_object"},
            )

            result = json.loads(response.content)
            intent = result.get("intent", LearningIntent.NONE)
            confidence = float(result.get("confidence", 0.0))
            reasoning = result.get("reasoning", "")

            # 验证意图有效性
            if intent not in [
                LearningIntent.ADD,
                LearningIntent.CORRECT,
                LearningIntent.SUPPLEMENT,
                LearningIntent.DELETE,
                LearningIntent.MERGE,
                LearningIntent.NONE,
            ]:
                intent = LearningIntent.NONE

            logger.info(
                f"检测到学习意图: {intent}, 置信度: {confidence}, 原因: {reasoning}"
            )

            return LearningIntentResult(
                intent=intent,
                confidence=confidence,
                reasoning=reasoning,
            )

        except Exception as e:
            logger.error(f"意图识别失败: {e}")
            return LearningIntentResult(
                intent=LearningIntent.NONE,
                confidence=0.0,
                reasoning=f"意图识别失败: {str(e)}",
            )

    def _build_intent_detection_prompt(
        self,
        user_message: str,
        assistant_message: str,
        conversation_history: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """构建意图识别Prompt"""

        history_text = ""
        if conversation_history:
            history_text = "\n".join(
                [
                    f"{msg['role']}: {msg['content']}"
                    for msg in conversation_history[-3:]  # 最近3轮对话
                ]
            )

        prompt = f"""你是一个AI学习意图识别专家，需要分析用户的输入判断是否有学习意图。

## 最近对话历史
{history_text}

## 当前对话
用户: {user_message}
助手: {assistant_message}

## 学习意图类型
1. add - 用户提供了新知识，需要添加到知识库
   - 示例: "你可以记住，公司成立于2010年"
   - 示例: "补充一条信息：我们的产品支持多语言"

2. correct - 用户纠正了助手的错误回答
   - 示例: "不对，你说错了，价格是100元不是200元"
   - 示例: "你理解错了，应该这样..."

3. supplement - 用户补充了不完整的信息
   - 示例: "补充一下，这个功能还支持批量操作"
   - 示例: "另外，这个系统也支持移动端"

4. delete - 用户要求删除错误或过时的知识
   - 示例: "删除刚才说的，那个信息是过期的"
   - 示例: "这条知识不对，请移除"

5. merge - 用户提供了类似的知识，需要合并
   - 示例: "这条知识和刚才那条很像，可以合并"

6. none - 普通对话，无学习意图

## 输出要求
请以JSON格式输出分析结果，包含以下字段：
{{
  "intent": "意图类型(add/correct/supplement/delete/merge/none)",
  "confidence": 0.0-1.0之间的置信度,
  "reasoning": "判断依据的详细说明"
}}

## 判断标准
- 置信度 > 0.7: 明确的学习意图
- 置信度 0.5-0.7: 可能的学习意图
- 置信度 < 0.5: 无学习意图
"""

        return prompt

    # ========== 知识提取 ==========

    async def extract_knowledge(
        self,
        user_message: str,
        assistant_message: str,
        intent: str,
        conversation_history: Optional[List[Dict[str, Any]]] = None,
    ) -> List[KnowledgeExtractionResult]:
        """从对话中提取知识"""

        # 如果无学习意图，返回空列表
        if intent == LearningIntent.NONE:
            return []

        prompt = self._build_knowledge_extraction_prompt(
            user_message, assistant_message, intent, conversation_history
        )

        try:
            response = await self.llm.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                response_format={"type": "json_object"},
            )

            result = json.loads(response.content)
            knowledge_list = result.get("knowledge", [])

            extracted_knowledge = []
            for item in knowledge_list:
                knowledge = KnowledgeExtractionResult(
                    title=item.get("title", ""),
                    content=item.get("content", ""),
                    source="conversation",
                    knowledge_id=item.get("knowledge_id"),  # 如果是纠正/补充/删除，提供关联知识ID
                    confidence=float(item.get("confidence", 0.0)),
                    metadata={
                        "intent": intent,
                        "user_message": user_message,
                        "assistant_message": assistant_message,
                        "extraction_time": datetime.utcnow().isoformat(),
                    },
                )
                extracted_knowledge.append(knowledge)

            logger.info(f"从对话中提取了 {len(extracted_knowledge)} 条知识")

            return extracted_knowledge

        except Exception as e:
            logger.error(f"知识提取失败: {e}")
            return []

    def _build_knowledge_extraction_prompt(
        self,
        user_message: str,
        assistant_message: str,
        intent: str,
        conversation_history: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """构建知识提取Prompt"""

        history_text = ""
        if conversation_history:
            history_text = "\n".join(
                [f"{msg['role']}: {msg['content']}" for msg in conversation_history[-3:]]
            )

        intent_desc = {
            LearningIntent.ADD: "提取用户提供的全新知识",
            LearningIntent.CORRECT: "提取纠正内容，识别被纠正的知识点",
            LearningIntent.SUPPLEMENT: "提取补充信息，识别被补充的知识点",
            LearningIntent.DELETE: "识别需要删除的知识点",
            LearningIntent.MERGE: "提取可合并的知识内容",
        }.get(intent, "提取知识")

        prompt = f"""你是一个AI知识提取专家，需要从对话中提取结构化的知识。

## 学习意图
{intent} - {intent_desc}

## 对话上下文
{history_text}

## 当前对话
用户: {user_message}
助手: {assistant_message}

## 知识提取要求
请提取对话中的知识，每个知识包含以下信息：
- title: 知识标题（简短准确）
- content: 知识内容（详细完整）
- knowledge_id: 如果是纠正/补充/删除操作，提供关联的知识ID（如果能推断出来）
- confidence: 提取置信度(0.0-1.0)

## 输出格式
{{
  "knowledge": [
    {{
      "title": "知识标题",
      "content": "知识内容",
      "knowledge_id": null,  // 或具体的知识ID
      "confidence": 0.9
    }}
  ]
}}

## 提取原则
1. 标题要简短准确，能够概括知识内容
2. 内容要详细完整，包含所有相关信息
3. 如果是纠正/补充/删除操作，尽可能识别关联的知识ID
4. 置信度要客观反映提取的可靠性
5. 每条知识要独立完整，不依赖上下文
"""

        return prompt

    # ========== 冲突检测 ==========

    async def detect_knowledge_conflicts(
        self,
        new_knowledge: KnowledgeExtractionResult,
        existing_knowledge: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """检测知识冲突"""

        if not existing_knowledge:
            return []

        # 构建现有知识摘要
        existing_summary = "\n".join(
            [
                f"ID: {k['id']}\n标题: {k['title']}\n内容: {k['content']}\n"
                for k in existing_knowledge[:5]  # 最多对比5条最相关的知识
            ]
        )

        prompt = f"""你是一个AI知识冲突检测专家，需要判断新知识是否与现有知识冲突。

## 新知识
标题: {new_knowledge.title}
内容: {new_knowledge.content}
学习意图: {new_knowledge.metadata.get('intent', 'unknown')}

## 现有相关知识
{existing_summary}

## 冲突类型
1. contradiction - 直接矛盾（内容相反或冲突）
2. overlap - 内容重复或高度相似
3. inconsistency - 逻辑不一致
4. none - 无冲突

## 输出格式
{{
  "conflicts": [
    {{
      "knowledge_id": 123,
      "conflict_type": "contradiction",
      "description": "冲突描述",
      "severity": "high",  // high/medium/low
      "suggestion": "解决建议"
    }}
  ]
}}

## 判断标准
- 矛盾: 内容直接相反（如"价格是100元" vs "价格是200元"）
- 重复: 内容高度相似（相似度 > 0.9）
- 不一致: 逻辑上存在冲突但不是直接矛盾
"""

        try:
            response = await self.llm.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                response_format={"type": "json_object"},
            )

            result = json.loads(response.content)
            conflicts = result.get("conflicts", [])

            if conflicts:
                logger.warning(
                    f"检测到 {len(conflicts)} 个知识冲突: {new_knowledge.title}"
                )

            return conflicts

        except Exception as e:
            logger.error(f"冲突检测失败: {e}")
            return []

    # ========== 完整学习流程 ==========

    async def process_learning(
        self,
        user_message: str,
        assistant_message: str,
        conversation_history: Optional[List[Dict[str, Any]]] = None,
        auto_approve: bool = False,
    ) -> Dict[str, Any]:
        """处理对话式学习完整流程"""

        try:
            # 1. 检测学习意图
            intent_result = await self.detect_learning_intent(
                user_message, assistant_message, conversation_history
            )

            # 如果无学习意图，直接返回
            if intent_result.intent == LearningIntent.NONE:
                return {
                    "success": True,
                    "intent": LearningIntent.NONE,
                    "knowledge_extracted": [],
                    "conflicts": [],
                    "status": "none",
                    "new_knowledge_ids": [],
                }

            # 2. 提取知识
            knowledge_list = await self.extract_knowledge(
                user_message,
                assistant_message,
                intent_result.intent,
                conversation_history,
            )

            if not knowledge_list:
                return {
                    "success": True,
                    "intent": intent_result.intent,
                    "knowledge_extracted": [],
                    "conflicts": [],
                    "status": "no_knowledge",
                    "new_knowledge_ids": [],
                }

            # 3. 检测冲突（查询现有知识）
            # TODO: 实现从数据库查询相关知识的逻辑
            existing_knowledge = []
            all_conflicts = []

            for knowledge in knowledge_list:
                conflicts = await self.detect_knowledge_conflicts(
                    knowledge, existing_knowledge
                )
                all_conflicts.extend(conflicts)

            # 4. 创建学习记录
            # TODO: 实现将学习记录保存到数据库
            status = "approved" if auto_approve and not all_conflicts else "pending"

            # TODO: 如果自动批准且无冲突，直接更新知识库

            return {
                "success": True,
                "intent": intent_result.intent,
                "knowledge_extracted": [
                    {
                        "title": k.title,
                        "content": k.content,
                        "confidence": k.confidence,
                    }
                    for k in knowledge_list
                ],
                "conflicts": all_conflicts,
                "status": status,
                "new_knowledge_ids": [],  # TODO: 返回新增的知识ID
            }

        except Exception as e:
            logger.error(f"对话式学习处理失败: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "intent": LearningIntent.NONE,
                "knowledge_extracted": [],
                "conflicts": [],
                "status": "failed",
                "new_knowledge_ids": [],
            }

    # ========== 批准/拒绝 ==========

    async def approve_knowledge(
        self,
        learning_record_id: int,
    ) -> bool:
        """批准学习的知识"""

        try:
            # TODO: 实现批准逻辑
            # 1. 更新学习记录状态为approved
            # 2. 将知识添加到知识库
            # 3. 更新向量数据库

            logger.info(f"批准学习记录: {learning_record_id}")
            return True

        except Exception as e:
            logger.error(f"批准知识失败: {e}")
            return False

    async def reject_knowledge(
        self,
        learning_record_id: int,
        reason: str,
    ) -> bool:
        """拒绝学习的知识"""

        try:
            # TODO: 实现拒绝逻辑
            # 1. 更新学习记录状态为rejected
            # 2. 记录拒绝原因

            logger.info(f"拒绝学习记录: {learning_record_id}, 原因: {reason}")
            return True

        except Exception as e:
            logger.error(f"拒绝知识失败: {e}")
            return False

    # ========== 统计信息 ==========

    async def get_learning_statistics(
        self,
        user_id: int,
        days: int = 30,
    ) -> Dict[str, Any]:
        """获取学习统计信息"""

        try:
            # TODO: 实现统计查询逻辑
            return {
                "total_learned": 0,
                "approved": 0,
                "rejected": 0,
                "pending": 0,
                "accuracy": 0.0,
                "by_intent": {
                    LearningIntent.ADD: 0,
                    LearningIntent.CORRECT: 0,
                    LearningIntent.SUPPLEMENT: 0,
                    LearningIntent.DELETE: 0,
                    LearningIntent.MERGE: 0,
                },
            }

        except Exception as e:
            logger.error(f"获取学习统计失败: {e}")
            return {}
