"""工具注册表

管理工具的注册、查找和执行
"""

from typing import Dict, Any, Callable, Optional, List
from datetime import datetime
from enum import Enum
import inspect


class ToolStatus(str, Enum):
    """工具状态"""

    ENABLED = "enabled"
    DISABLED = "disabled"
    DEPRECATED = "deprecated"


class ToolParameter:
    """工具参数定义"""

    def __init__(
        self,
        name: str,
        type: str,
        description: str,
        required: bool = True,
        default: Any = None,
    ):
        self.name = name
        self.type = type
        self.description = description
        self.required = required
        self.default = default


class Tool:
    """工具定义"""

    def __init__(
        self,
        name: str,
        description: str,
        function: Callable,
        parameters: List[ToolParameter],
        category: str = "general",
        timeout: int = 30,
        enabled: bool = True,
    ):
        self.name = name
        self.description = description
        self.function = function
        self.parameters = parameters
        self.category = category
        self.timeout = timeout
        self.enabled = enabled
        self.registered_at = datetime.utcnow()

    def validate_parameters(self, params: Dict[str, Any]) -> tuple[bool, str]:
        """验证参数

        Args:
            params: 参数字典

        Returns:
            tuple: (是否有效, 错误信息)
        """
        for param in self.parameters:
            # 检查必填参数
            if param.required and param.name not in params:
                return False, f"缺少必填参数: {param.name}"

            # 检查参数类型
            if param.name in params:
                value = params[param.name]
                if not self._check_type(value, param.type):
                    return False, f"参数类型错误: {param.name} 应为 {param.type}"

        return True, ""

    def _check_type(self, value: Any, expected_type: str) -> bool:
        """检查类型"""
        type_mapping = {
            "string": str,
            "integer": int,
            "float": (int, float),
            "boolean": bool,
            "array": list,
            "object": dict,
        }

        python_type = type_mapping.get(expected_type, str)
        return isinstance(value, python_type)


class ToolExecutionResult:
    """工具执行结果"""

    def __init__(
        self,
        success: bool,
        tool_name: str,
        output: Optional[Any] = None,
        error: Optional[str] = None,
        execution_time_ms: int = 0,
    ):
        self.success = success
        self.tool_name = tool_name
        self.output = output
        self.error = error
        self.execution_time_ms = execution_time_ms

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "success": self.success,
            "tool_name": self.tool_name,
            "output": self.output,
            "error": self.error,
            "execution_time_ms": self.execution_time_ms,
        }


class ToolRegistry:
    """工具注册表"""

    def __init__(self):
        self._tools: Dict[str, Tool] = {}
        self._categories: Dict[str, List[str]] = {}

    # ========== 工具注册 ==========

    def register(
        self,
        name: str,
        description: str,
        function: Callable,
        parameters: List[ToolParameter],
        category: str = "general",
        timeout: int = 30,
        enabled: bool = True,
        replace: bool = False,
    ) -> bool:
        """注册工具

        Args:
            name: 工具名称
            description: 工具描述
            function: 工具函数
            parameters: 参数定义
            category: 工具分类
            timeout: 超时时间(秒)
            enabled: 是否启用
            replace: 是否替换已存在的工具

        Returns:
            bool: 成功返回True
        """
        if not replace and name in self._tools:
            return False

        tool = Tool(
            name=name,
            description=description,
            function=function,
            parameters=parameters,
            category=category,
            timeout=timeout,
            enabled=enabled,
        )

        self._tools[name] = tool

        # 更新分类索引
        if category not in self._categories:
            self._categories[category] = []
        if name not in self._categories[category]:
            self._categories[category].append(name)

        return True

    def unregister(self, name: str) -> bool:
        """注销工具

        Args:
            name: 工具名称

        Returns:
            bool: 成功返回True
        """
        if name not in self._tools:
            return False

        # 从分类索引中移除
        tool = self._tools[name]
        if tool.category in self._categories and name in self._categories[tool.category]:
            self._categories[tool.category].remove(name)

        # 删除工具
        del self._tools[name]
        return True

    # ========== 工具查询 ==========

    def get_tool(self, name: str) -> Optional[Tool]:
        """获取工具

        Args:
            name: 工具名称

        Returns:
            Optional[Tool]: 工具对象
        """
        return self._tools.get(name)

    def list_tools(
        self,
        category: Optional[str] = None,
        enabled_only: bool = True,
    ) -> List[Tool]:
        """列出工具

        Args:
            category: 过滤分类
            enabled_only: 只返回启用的工具

        Returns:
            List[Tool]: 工具列表
        """
        tools = list(self._tools.values())

        # 过滤分类
        if category:
            tool_names = self._categories.get(category, [])
            tools = [t for t in tools if t.name in tool_names]

        # 过滤状态
        if enabled_only:
            tools = [t for t in tools if t.enabled]

        return tools

    def get_categories(self) -> List[str]:
        """获取所有分类

        Returns:
            List[str]: 分类列表
        """
        return list(self._categories.keys())

    def count_tools(self, enabled_only: bool = True) -> int:
        """统计工具数量

        Args:
            enabled_only: 只统计启用的工具

        Returns:
            int: 工具数量
        """
        if enabled_only:
            return sum(1 for t in self._tools.values() if t.enabled)
        return len(self._tools)

    # ========== 工具执行 ==========

    async def execute(
        self,
        name: str,
        parameters: Dict[str, Any],
    ) -> ToolExecutionResult:
        """执行工具

        Args:
            name: 工具名称
            parameters: 参数字典

        Returns:
            ToolExecutionResult: 执行结果
        """
        from utils.time_operator import Timer

        timer = Timer()
        timer.start()

        try:
            # 检查工具是否存在
            tool = self.get_tool(name)
            if not tool:
                return ToolExecutionResult(
                    success=False,
                    tool_name=name,
                    error=f"工具不存在: {name}",
                    execution_time_ms=timer.get_elapsed_ms(),
                )

            # 检查工具是否启用
            if not tool.enabled:
                return ToolExecutionResult(
                    success=False,
                    tool_name=name,
                    error=f"工具已禁用: {name}",
                    execution_time_ms=timer.get_elapsed_ms(),
                )

            # 验证参数
            valid, error_msg = tool.validate_parameters(parameters)
            if not valid:
                return ToolExecutionResult(
                    success=False,
                    tool_name=name,
                    error=f"参数验证失败: {error_msg}",
                    execution_time_ms=timer.get_elapsed_ms(),
                )

            # 执行工具函数
            if inspect.iscoroutinefunction(tool.function):
                output = await tool.function(**parameters)
            else:
                output = tool.function(**parameters)

            timer.stop()

            return ToolExecutionResult(
                success=True,
                tool_name=name,
                output=output,
                execution_time_ms=timer.get_elapsed_ms(),
            )

        except Exception as e:
            timer.stop()
            return ToolExecutionResult(
                success=False,
                tool_name=name,
                error=str(e),
                execution_time_ms=timer.get_elapsed_ms(),
            )

    def get_tool_schema(
        self,
        name: str,
    ) -> Optional[Dict[str, Any]]:
        """获取工具的JSON Schema

        Args:
            name: 工具名称

        Returns:
            Optional[Dict]: JSON Schema
        """
        tool = self.get_tool(name)
        if not tool:
            return None

        parameters_schema = {
            "type": "object",
            "properties": {},
            "required": [],
        }

        for param in tool.parameters:
            parameters_schema["properties"][param.name] = {
                "type": param.type,
                "description": param.description,
            }
            if param.default is not None:
                parameters_schema["properties"][param.name]["default"] = param.default

            if param.required:
                parameters_schema["required"].append(param.name)

        return {
            "name": tool.name,
            "description": tool.description,
            "parameters": parameters_schema,
        }

    def get_all_schemas(
        self,
        enabled_only: bool = True,
    ) -> List[Dict[str, Any]]:
        """获取所有工具的JSON Schema

        Args:
            enabled_only: 只返回启用的工具

        Returns:
            List[Dict]: JSON Schema列表
        """
        tools = self.list_tools(enabled_only=enabled_only)
        return [self.get_tool_schema(t.name) for t in tools]
