"""
LLM配置模板
提供常用的LLM配置和初始化代码
"""

from langchain_openai import ChatOpenAI
from langchain_core.callbacks import BaseCallbackHandler
from typing import Dict


class TokenUsageCallback(BaseCallbackHandler):
    """Token使用统计回调"""
    
    def __init__(self):
        super().__init__()
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.total_tokens = 0
        self.call_count = 0
    
    def on_llm_start(self, serialized, prompts, **kwargs):
        """LLM开始调用"""
        self.call_count += 1
    
    def on_llm_end(self, response, **kwargs):
        """LLM结束调用"""
        if hasattr(response, 'llm_output') and response.llm_output:
            token_usage = response.llm_output.get('token_usage', {})
            self.prompt_tokens += token_usage.get('prompt_tokens', 0)
            self.completion_tokens += token_usage.get('completion_tokens', 0)
            self.total_tokens += token_usage.get('total_tokens', 0)
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            'prompt_tokens': self.prompt_tokens,
            'completion_tokens': self.completion_tokens,
            'total_tokens': self.total_tokens,
            'call_count': self.call_count
        }


def create_llm_openai(
    model_name: str = "gpt-4",
    api_key: str = "",
    base_url: str = "",
    max_retries: int = 3,
    streaming: bool = False,
    extra_body: Dict = None
) -> ChatOpenAI:
    """创建OpenAI兼容的LLM实例
    
    Args:
        model_name: 模型名称
        api_key: API密钥
        base_url: API基础URL
        max_retries: 最大重试次数
        streaming: 是否流式输出
        extra_body: 额外配置参数
    
    Returns:
        ChatOpenAI实例
    """
    return ChatOpenAI(
        model=model_name,
        api_key=api_key,
        base_url=base_url,
        max_retries=max_retries,
        streaming=streaming,
        extra_body=extra_body or {}
    )


def create_llm_qwen3(
    model_name: str = "qwen3-32b-awq",
    api_key: str = "",
    base_url: str = "",
    enable_thinking: bool = False
) -> ChatOpenAI:
    """创建Qwen3模型实例
    
    Args:
        model_name: 模型名称
        api_key: API密钥
        base_url: API基础URL
        enable_thinking: 是否启用思考模式
    
    Returns:
        ChatOpenAI实例
    """
    return ChatOpenAI(
        model=model_name,
        api_key=api_key,
        base_url=base_url,
        max_retries=5,
        extra_body={
            "chat_template_kwargs": {"enable_thinking": enable_thinking}
        }
    )


def create_llm_with_callback(
    llm_config: Dict,
    callbacks: list = None
) -> ChatOpenAI:
    """创建带回调的LLM实例
    
    Args:
        llm_config: LLM配置字典
        callbacks: 回调处理器列表
    
    Returns:
        ChatOpenAI实例
    """
    return create_llm_openai(**llm_config)
