"""LLM工具模块

提供LLM调用、Token统计等功能
"""

from typing import Optional, Dict, Any
from langchain_openai import ChatOpenAI
from langchain.callbacks.base import BaseCallbackHandler
from langchain_core.messages import BaseMessage

from config import settings
from utils.logger import logger


class TokenUsageCallback(BaseCallbackHandler):
    """Token使用统计回调

    自动统计LLM调用的Token使用量
    """

    def __init__(self):
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.total_tokens = 0

    def on_llm_end(self, response, **kwargs):
        """LLM调用结束时统计Token"""
        if hasattr(response, 'llm_output') and response.llm_output:
            token_usage = response.llm_output.get('token_usage', {})
            self.prompt_tokens += token_usage.get('prompt_tokens', 0)
            self.completion_tokens += token_usage.get('completion_tokens', 0)
            self.total_tokens += token_usage.get('total_tokens', 0)

    def get_stats(self) -> Dict[str, int]:
        """获取统计结果"""
        return {
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
        }


class LLMManager:
    """LLM管理器

    统一管理LLM实例，支持多种模型
    """

    def __init__(self):
        self._llm: Optional[ChatOpenAI] = None

    def get_llm(self) -> ChatOpenAI:
        """获取LLM实例"""
        if self._llm is None:
            self._llm = ChatOpenAI(
                model=settings.OPENAI_MODEL,
                base_url=settings.OPENAI_API_BASE,
                api_key=settings.OPENAI_API_KEY,
                temperature=settings.OPENAI_TEMPERATURE,
                max_tokens=settings.OPENAI_MAX_TOKENS,
                timeout=settings.OPENAI_TIMEOUT,
                max_retries=settings.OPENAI_MAX_RETRIES,
            )
            logger.info(f"LLM initialized: {settings.OPENAI_MODEL}")
        return self._llm

    async def generate_response(
        self,
        messages: list[BaseMessage],
        callbacks: Optional[list] = None,
    ) -> str:
        """生成响应

        Args:
            messages: 消息列表
            callbacks: 回调函数列表

        Returns:
            str: 生成的响应
        """
        llm = self.get_llm()
        response = await llm.ainvoke(messages, config={"callbacks": callbacks})
        return response.content

    def set_model(self, model_name: str) -> None:
        """切换模型

        Args:
            model_name: 模型名称
        """
        self._llm = None
        logger.info(f"Model switched to: {model_name}")


# 全局LLM管理器实例
llm_manager = LLMManager()


__all__ = [
    "TokenUsageCallback",
    "LLMManager",
    "llm_manager",
]
