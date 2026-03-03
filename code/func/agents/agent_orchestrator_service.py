"""智能体编排器服务

集成知识检索、对话式学习和工具调用的完整编排服务
"""

from typing import Dict, Any, Optional, List
from datetime import datetime

from core.agents.interfaces import IAgentOrchestrator
from core.knowledge.retriever import KnowledgeRetriever
from core.conversational_learning import ConversationLearningEngine
from utils.logger import logger
from utils.llm import LLMManager
from utils.time_operator import Timer


class AgentOrchestrator(IAgentOrchestrator):
    """智能体编排器实现"""

    def __init__(
        self,
        llm_manager: LLMManager,
        retriever: KnowledgeRetriever,
        learning_engine: ConversationLearningEngine,
        db_session,
    ):
        self.llm = llm_manager
        self.retriever = retriever
        self.learning = learning_engine
        self.db = db_session

        # 系统提示词
        self.system_prompt = self._build_system_prompt()

    def _build_system_prompt(self) -> str:
        """构建系统提示词"""
        return """你是一个智能AI助手，能够检索知识库并学习新知识。

## 核心能力
1. 检索知识库中的相关信息
2. 基于检索到的知识回答用户问题
3. 从对话中识别学习意图并学习新知识
4. 提供准确、有用、有帮助的回答

## 回答原则
- 优先使用检索到的知识回答
- 如果知识不足，诚实告知用户
- 保持回答简洁准确
- 避免编造不存在的信息

## 学习原则
- 识别用户提供的新知识
- 识别用户的纠正和补充
- 记录学习到的内容
"""

    # ========== 执行对话 ==========

    async def execute_conversation(
        self,
        session_id: int,
        user_id: int,
        message: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """执行对话流程

        Args:
            session_id: 会话ID
            user_id: 用户ID
            message: 用户消息
            context: 上下文信息

        Returns:
            Dict: 对话结果
            {
                "response": "AI回复",
                "retrieved_knowledge": [...],
                "new_knowledge": [...],
                "tokens": {...},
                "execution_time_ms": 1234
            }
        """
        timer = Timer()
        timer.start()

        try:
            logger.info(f"执行对话: session_id={session_id}, user_id={user_id}")

            # 1. 获取对话历史
            conversation_history = await self._get_conversation_history(session_id)

            # 2. 检索知识
            retrieved_knowledge = await self._retrieve_knowledge(
                query=message,
                user_id=user_id,
                top_k=5,
            )

            # 3. 生成回复
            response, tokens = await self._generate_response(
                message=message,
                conversation_history=conversation_history,
                retrieved_knowledge=retrieved_knowledge,
            )

            # 4. 保存消息
            await self._save_messages(
                session_id=session_id,
                user_message=message,
                assistant_message=response,
                retrieved_knowledge=retrieved_knowledge,
            )

            # 5. 对话式学习（异步）
            learning_result = await self._process_conversation_learning(
                user_message=message,
                assistant_message=response,
                conversation_history=conversation_history,
            )

            # 6. 返回结果
            timer.stop()
            execution_time = timer.get_elapsed_ms()

            return {
                "success": True,
                "response": response,
                "retrieved_knowledge": retrieved_knowledge,
                "new_knowledge": learning_result.get("knowledge_extracted", []),
                "learning_intent": learning_result.get("intent"),
                "tokens": tokens,
                "execution_time_ms": execution_time,
            }

        except Exception as e:
            timer.stop()
            logger.error(f"执行对话失败: {e}", exc_info=True)

            return {
                "success": False,
                "error": str(e),
                "response": "抱歉，我遇到了一些问题，请稍后再试。",
                "retrieved_knowledge": [],
                "new_knowledge": [],
                "tokens": {},
                "execution_time_ms": timer.get_elapsed_ms(),
            }

    # ========== 知识检索 ==========

    async def _retrieve_knowledge(
        self,
        query: str,
        user_id: int,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """检索知识

        Args:
            query: 查询文本
            user_id: 用户ID
            top_k: 返回数量

        Returns:
            List[Dict]: 知识列表
        """
        try:
            results = await self.retriever.retrieve_knowledge(
                query=query,
                user_id=user_id,
                top_k=top_k,
                strategy="vector",  # 使用向量检索
                rerank=True,
            )

            logger.info(f"检索知识: {len(results)} 条")
            return results

        except Exception as e:
            logger.error(f"知识检索失败: {e}")
            return []

    # ========== 生成回复 ==========

    async def _generate_response(
        self,
        message: str,
        conversation_history: List[Dict[str, Any]],
        retrieved_knowledge: List[Dict[str, Any]],
    ) -> tuple[str, Dict[str, Any]]:
        """生成回复

        Args:
            message: 用户消息
            conversation_history: 对话历史
            retrieved_knowledge: 检索到的知识

        Returns:
            tuple: (回复内容, token统计)
        """
        try:
            # 构建知识上下文
            knowledge_context = self._build_knowledge_context(retrieved_knowledge)

            # 构建对话历史
            history_context = self._build_history_context(conversation_history)

            # 构建完整Prompt
            prompt = f"""{self.system_prompt}

## 知识库内容
{knowledge_context}

## 对话历史
{history_context}

## 用户问题
{message}

## 回答要求
1. 基于知识库内容回答问题
2. 如果知识库中没有相关信息，诚实告知
3. 回答要简洁准确，条理清晰
4. 避免编造信息
"""

            # 调用LLM
            response = await self.llm.chat_completion(
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    *self._format_history(conversation_history),
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=1000,
            )

            # 获取token统计
            tokens = {
                "prompt_tokens": response.usage.prompt_tokens if hasattr(response, 'usage') else 0,
                "completion_tokens": response.usage.completion_tokens if hasattr(response, 'usage') else 0,
                "total_tokens": response.usage.total_tokens if hasattr(response, 'usage') else 0,
            }

            return response.content, tokens

        except Exception as e:
            logger.error(f"生成回复失败: {e}")
            raise

    def _build_knowledge_context(
        self,
        knowledge: List[Dict[str, Any]],
    ) -> str:
        """构建知识上下文"""
        if not knowledge:
            return "未检索到相关知识。"

        context_parts = []
        for idx, item in enumerate(knowledge, 1):
            context_parts.append(
                f"{idx}. {item.get('title', '')}\n"
                f"   {item.get('content', '')[:500]}..."
            )

        return "\n\n".join(context_parts)

    def _build_history_context(
        self,
        history: List[Dict[str, Any]],
    ) -> str:
        """构建对话历史上下文"""
        if not history:
            return "（暂无对话历史）"

        history_parts = []
        for msg in history[-3:]:  # 最近3轮对话
            role = msg.get("role", "")
            content = msg.get("content", "")
            history_parts.append(f"{role}: {content}")

        return "\n".join(history_parts)

    def _format_history(
        self,
        history: List[Dict[str, Any]],
    ) -> List[Dict[str, str]]:
        """格式化对话历史为LLM消息格式"""
        messages = []
        for msg in history:
            role = "user" if msg.get("role") == "user" else "assistant"
            messages.append(
                {
                    "role": role,
                    "content": msg.get("content", ""),
                }
            )
        return messages

    # ========== 对话式学习 ==========

    async def _process_conversation_learning(
        self,
        user_message: str,
        assistant_message: str,
        conversation_history: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """处理对话式学习

        Args:
            user_message: 用户消息
            assistant_message: 助手回复
            conversation_history: 对话历史

        Returns:
            Dict: 学习结果
        """
        try:
            # 调用对话式学习引擎
            result = await self.learning.process_learning(
                user_message=user_message,
                assistant_message=assistant_message,
                conversation_history=conversation_history,
                auto_approve=False,  # 需要人工审核
            )

            if result.get("success") and result.get("intent") != "none":
                logger.info(
                    f"对话式学习: intent={result.get('intent')}, "
                    f"knowledge={len(result.get('knowledge_extracted', []))}条"
                )

            return result

        except Exception as e:
            logger.error(f"对话式学习失败: {e}")
            return {
                "success": False,
                "intent": "none",
                "error": str(e),
            }

    # ========== 消息保存 ==========

    async def _save_messages(
        self,
        session_id: int,
        user_message: str,
        assistant_message: str,
        retrieved_knowledge: List[Dict[str, Any]],
    ):
        """保存对话消息

        Args:
            session_id: 会话ID
            user_message: 用户消息
            assistant_message: 助手回复
            retrieved_knowledge: 检索到的知识
        """
        try:
            # TODO: 实现保存消息到数据库
            logger.info(f"保存消息: session_id={session_id}")

        except Exception as e:
            logger.error(f"保存消息失败: {e}")

    # ========== 对话历史 ==========

    async def _get_conversation_history(
        self,
        session_id: int,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """获取对话历史

        Args:
            session_id: 会话ID
            limit: 限制数量

        Returns:
            List[Dict]: 对话历史
        """
        try:
            # TODO: 从数据库获取对话历史
            return []
        except Exception as e:
            logger.error(f"获取对话历史失败: {e}")
            return []
