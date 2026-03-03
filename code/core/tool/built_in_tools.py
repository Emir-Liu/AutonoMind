"""内置工具

提供一些常用的内置工具
"""

import httpx
from typing import Dict, Any

from core.tool.tool_registry import (
    Tool,
    ToolParameter,
)
from utils.logger import logger


class BuiltInTools:
    """内置工具类"""

    @staticmethod
    def get_current_time() -> str:
        """获取当前时间"""
        from datetime import datetime
        return datetime.utcnow().isoformat()

    @staticmethod
    def calculate(expression: str) -> float:
        """计算数学表达式"""
        try:
            # 使用eval计算，注意安全性
            # 在生产环境中应使用更安全的计算方式
            result = eval(expression, {"__builtins__": {}}, {})
            return float(result)
        except Exception as e:
            raise ValueError(f"计算失败: {e}")

    @staticmethod
    async def get_weather(city: str) -> Dict[str, Any]:
        """获取天气信息（示例）"""
        # TODO: 集成真实天气API
        return {
            "city": city,
            "temperature": 25,
            "condition": "晴",
            "humidity": 60,
        }

    @staticmethod
    async def web_search(query: str, num_results: int = 5) -> Dict[str, Any]:
        """网络搜索（示例）"""
        # TODO: 集成搜索引擎API
        return {
            "query": query,
            "results": [
                {
                    "title": "示例结果1",
                    "url": "https://example.com/1",
                    "snippet": "示例内容...",
                }
            ],
        }

    @staticmethod
    async def http_get(url: str, timeout: int = 10) -> Dict[str, Any]:
        """HTTP GET请求"""
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(url)
            return {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "content": response.text,
            }

    @staticmethod
    async def http_post(
        url: str,
        data: Dict[str, Any],
        timeout: int = 10,
    ) -> Dict[str, Any]:
        """HTTP POST请求"""
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(url, json=data)
            return {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "content": response.text,
            }

    @staticmethod
    def text_length(text: str) -> int:
        """计算文本长度"""
        return len(text)

    @staticmethod
    def count_words(text: str) -> int:
        """计算单词数量"""
        return len(text.split())


def register_built_in_tools(registry):
    """注册所有内置工具

    Args:
        registry: 工具注册表
    """

    # 1. 获取当前时间
    registry.register(
        name="get_current_time",
        description="获取当前UTC时间",
        function=BuiltInTools.get_current_time,
        parameters=[],
        category="datetime",
    )

    # 2. 计算器
    registry.register(
        name="calculate",
        description="计算数学表达式",
        function=BuiltInTools.calculate,
        parameters=[
            ToolParameter(
                name="expression",
                type="string",
                description="数学表达式，如 '1 + 2 * 3'",
                required=True,
            )
        ],
        category="math",
    )

    # 3. 天气查询
    registry.register(
        name="get_weather",
        description="获取指定城市的天气信息",
        function=BuiltInTools.get_weather,
        parameters=[
            ToolParameter(
                name="city",
                type="string",
                description="城市名称",
                required=True,
            )
        ],
        category="weather",
    )

    # 4. 网络搜索
    registry.register(
        name="web_search",
        description="在网络上搜索信息",
        function=BuiltInTools.web_search,
        parameters=[
            ToolParameter(
                name="query",
                type="string",
                description="搜索关键词",
                required=True,
            ),
            ToolParameter(
                name="num_results",
                type="integer",
                description="返回结果数量",
                required=False,
                default=5,
            ),
        ],
        category="web",
    )

    # 5. HTTP GET
    registry.register(
        name="http_get",
        description="发送HTTP GET请求",
        function=BuiltInTools.http_get,
        parameters=[
            ToolParameter(
                name="url",
                type="string",
                description="请求URL",
                required=True,
            ),
            ToolParameter(
                name="timeout",
                type="integer",
                description="超时时间(秒)",
                required=False,
                default=10,
            ),
        ],
        category="http",
    )

    # 6. HTTP POST
    registry.register(
        name="http_post",
        description="发送HTTP POST请求",
        function=BuiltInTools.http_post,
        parameters=[
            ToolParameter(
                name="url",
                type="string",
                description="请求URL",
                required=True,
            ),
            ToolParameter(
                name="data",
                type="object",
                description="请求体数据",
                required=True,
            ),
            ToolParameter(
                name="timeout",
                type="integer",
                description="超时时间(秒)",
                required=False,
                default=10,
            ),
        ],
        category="http",
    )

    # 7. 文本长度
    registry.register(
        name="text_length",
        description="计算文本长度",
        function=BuiltInTools.text_length,
        parameters=[
            ToolParameter(
                name="text",
                type="string",
                description="待计算的文本",
                required=True,
            )
        ],
        category="text",
    )

    # 8. 单词计数
    registry.register(
        name="count_words",
        description="计算文本中的单词数量",
        function=BuiltInTools.count_words,
        parameters=[
            ToolParameter(
                name="text",
                type="string",
                description="待计算的文本",
                required=True,
            )
        ],
        category="text",
    )

    logger.info(f"注册内置工具完成: {registry.count_tools()} 个")
