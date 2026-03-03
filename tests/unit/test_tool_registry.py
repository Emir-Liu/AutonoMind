"""
工具注册表单元测试
"""

import pytest
from unittest.mock import Mock, AsyncMock, MagicMock
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "code"))

from core.tool.tool_registry import (
    ToolRegistry,
    Tool,
    ToolParameter,
    ToolExecutionResult,
    ToolStatus
)


@pytest.mark.unit
class TestToolRegistry:
    """工具注册表测试"""

    @pytest.fixture
    def registry(self):
        """创建工具注册表实例"""
        return ToolRegistry()

    @pytest.fixture
    def sample_tool(self):
        """示例工具"""
        return Tool(
            name="test_tool",
            description="测试工具",
            parameters=[
                ToolParameter(
                    name="input",
                    type="string",
                    description="输入参数",
                    required=True
                )
            ],
            function=lambda x: {"result": x}
        )

    def test_register_tool(self, registry, sample_tool):
        """测试注册工具"""
        registry.register(sample_tool)

        assert "test_tool" in registry.tools
        assert registry.get_tool("test_tool").name == "test_tool"

    def test_register_duplicate_tool(self, registry, sample_tool):
        """测试注册重复工具"""
        registry.register(sample_tool)

        with pytest.raises(ValueError, match="already exists"):
            registry.register(sample_tool)

    def test_get_tool(self, registry, sample_tool):
        """测试获取工具"""
        registry.register(sample_tool)

        tool = registry.get_tool("test_tool")

        assert tool is not None
        assert tool.name == "test_tool"
        assert tool.description == "测试工具"

    def test_get_nonexistent_tool(self, registry):
        """测试获取不存在的工具"""
        tool = registry.get_tool("nonexistent")

        assert tool is None

    def test_list_tools(self, registry, sample_tool):
        """测试列出工具"""
        registry.register(sample_tool)

        tools = registry.list_tools()

        assert len(tools) == 1
        assert tools[0].name == "test_tool"

    def test_list_enabled_tools(self, registry, sample_tool):
        """测试列出启用的工具"""
        sample_tool.enabled = True
        registry.register(sample_tool)

        # 添加一个禁用的工具
        disabled_tool = Tool(
            name="disabled_tool",
            description="禁用工具",
            parameters=[],
            function=lambda: {},
            enabled=False
        )
        registry.register(disabled_tool)

        enabled_tools = registry.list_tools(enabled_only=True)

        assert len(enabled_tools) == 1
        assert enabled_tools[0].name == "test_tool"

    def test_enable_tool(self, registry, sample_tool):
        """测试启用工具"""
        sample_tool.enabled = False
        registry.register(sample_tool)

        registry.enable_tool("test_tool")

        assert registry.get_tool("test_tool").enabled is True

    def test_disable_tool(self, registry, sample_tool):
        """测试禁用工具"""
        sample_tool.enabled = True
        registry.register(sample_tool)

        registry.disable_tool("test_tool")

        assert registry.get_tool("test_tool").enabled is False

    def test_unregister_tool(self, registry, sample_tool):
        """测试注销工具"""
        registry.register(sample_tool)

        registry.unregister("test_tool")

        assert "test_tool" not in registry.tools

    def test_unregister_nonexistent_tool(self, registry):
        """测试注销不存在的工具"""
        # 应该不抛出异常
        registry.unregister("nonexistent")

    def test_execute_tool(self, registry, sample_tool):
        """测试执行工具"""
        registry.register(sample_tool)

        result = registry.execute("test_tool", input="test_input")

        assert result.status == ToolStatus.SUCCESS
        assert result.output == {"result": "test_input"}

    def test_execute_disabled_tool(self, registry, sample_tool):
        """测试执行禁用的工具"""
        sample_tool.enabled = False
        registry.register(sample_tool)

        result = registry.execute("test_tool", input="test_input")

        assert result.status == ToolStatus.DISABLED
        assert result.error is not None

    def test_execute_nonexistent_tool(self, registry):
        """测试执行不存在的工具"""
        result = registry.execute("nonexistent", input="test")

        assert result.status == ToolStatus.NOT_FOUND

    def test_execute_with_missing_params(self, registry):
        """测试缺少必需参数"""
        tool = Tool(
            name="test_tool",
            description="测试工具",
            parameters=[
                ToolParameter(
                    name="required_param",
                    type="string",
                    description="必需参数",
                    required=True
                )
            ],
            function=lambda **kwargs: {"result": kwargs}
        )
        registry.register(tool)

        result = registry.execute("test_tool")

        assert result.status == ToolStatus.INVALID_PARAMS

    @pytest.mark.asyncio
    async def test_execute_async_tool(self, registry):
        """测试执行异步工具"""
        async def async_function(**kwargs):
            return {"result": kwargs}

        tool = Tool(
            name="async_tool",
            description="异步工具",
            parameters=[],
            function=async_function,
            is_async=True
        )
        registry.register(tool)

        result = await registry.execute_async("async_tool", input="test")

        assert result.status == ToolStatus.SUCCESS
        assert result.output == {"result": {"input": "test"}}


@pytest.mark.unit
class TestTool:
    """工具类测试"""

    def test_tool_creation(self):
        """测试工具创建"""
        tool = Tool(
            name="test_tool",
            description="测试工具",
            parameters=[
                ToolParameter(
                    name="param1",
                    type="string",
                    description="参数1",
                    required=True
                ),
                ToolParameter(
                    name="param2",
                    type="integer",
                    description="参数2",
                    required=False,
                    default=10
                )
            ],
            function=lambda **kwargs: kwargs
        )

        assert tool.name == "test_tool"
        assert tool.description == "测试工具"
        assert len(tool.parameters) == 2
        assert tool.parameters[0].required is True
        assert tool.parameters[1].required is False
        assert tool.parameters[1].default == 10

    def test_tool_with_metadata(self):
        """测试带元数据的工具"""
        tool = Tool(
            name="test_tool",
            description="测试工具",
            parameters=[],
            function=lambda: {},
            metadata={"category": "test", "version": "1.0"}
        )

        assert tool.metadata["category"] == "test"
        assert tool.metadata["version"] == "1.0"


@pytest.mark.unit
class TestToolParameter:
    """工具参数测试"""

    def test_parameter_creation(self):
        """测试参数创建"""
        param = ToolParameter(
            name="test_param",
            type="string",
            description="测试参数",
            required=True
        )

        assert param.name == "test_param"
        assert param.type == "string"
        assert param.description == "测试参数"
        assert param.required is True

    def test_parameter_with_default(self):
        """测试带默认值的参数"""
        param = ToolParameter(
            name="test_param",
            type="integer",
            description="测试参数",
            required=False,
            default=42
        )

        assert param.default == 42

    def test_parameter_types(self):
        """测试不同类型的参数"""
        types = ["string", "integer", "boolean", "array", "object"]

        for param_type in types:
            param = ToolParameter(
                name="test_param",
                type=param_type,
                description="测试",
                required=False
            )
            assert param.type == param_type


@pytest.mark.unit
class TestToolExecutionResult:
    """工具执行结果测试"""

    def test_success_result(self):
        """测试成功结果"""
        result = ToolExecutionResult(
            status=ToolStatus.SUCCESS,
            output={"data": "test"},
            duration_ms=100
        )

        assert result.status == ToolStatus.SUCCESS
        assert result.output == {"data": "test"}
        assert result.duration_ms == 100
        assert result.error is None

    def test_error_result(self):
        """测试错误结果"""
        result = ToolExecutionResult(
            status=ToolStatus.FAILED,
            error="执行失败",
            duration_ms=50
        )

        assert result.status == ToolStatus.FAILED
        assert result.error == "执行失败"
        assert result.output is None

    def test_to_dict(self):
        """测试转换为字典"""
        result = ToolExecutionResult(
            status=ToolStatus.SUCCESS,
            output={"data": "test"},
            duration_ms=100
        )

        result_dict = result.to_dict()

        assert "status" in result_dict
        assert "output" in result_dict
        assert "duration_ms" in result_dict
        assert result_dict["output"] == {"data": "test"}


@pytest.mark.unit
class TestToolStatus:
    """工具状态测试"""

    def test_status_values(self):
        """测试状态值"""
        assert ToolStatus.SUCCESS.value == "success"
        assert ToolStatus.FAILED.value == "failed"
        assert ToolStatus.DISABLED.value == "disabled"
        assert ToolStatus.NOT_FOUND.value == "not_found"
        assert ToolStatus.INVALID_PARAMS.value == "invalid_params"

    def test_status_count(self):
        """测试状态数量"""
        assert len(list(ToolStatus)) == 5

    def test_status_from_string(self):
        """测试从字符串创建状态"""
        assert ToolStatus("success") == ToolStatus.SUCCESS
        assert ToolStatus("failed") == ToolStatus.FAILED
        assert ToolStatus("disabled") == ToolStatus.DISABLED


@pytest.mark.unit
class TestBuiltInTools:
    """内置工具测试"""

    def test_search_tool(self):
        """测试搜索工具"""
        from core.tool.built_in_tools import BuiltInTools

        search_tool = BuiltInTools.SEARCH_TOOL

        assert search_tool.name == "search"
        assert "query" in [p.name for p in search_tool.parameters]

    def test_weather_tool(self):
        """测试天气工具"""
        from core.tool.built_in_tools import BuiltInTools

        weather_tool = BuiltInTools.WEATHER_TOOL

        assert weather_tool.name == "weather"
        assert "location" in [p.name for p in weather_tool.parameters]

    def test_get_all_tools(self):
        """测试获取所有内置工具"""
        from core.tool.built_in_tools import BuiltInTools

        tools = BuiltInTools.get_all_tools()

        assert isinstance(tools, list)
        assert len(tools) > 0
        assert all(isinstance(tool, Tool) for tool in tools)


@pytest.mark.unit
class TestToolValidation:
    """工具验证测试"""

    @pytest.fixture
    def registry(self):
        """创建注册表"""
        return ToolRegistry()

    def test_validate_required_params(self, registry):
        """测试验证必需参数"""
        tool = Tool(
            name="test_tool",
            description="测试",
            parameters=[
                ToolParameter("required_param", "string", "必需", True),
                ToolParameter("optional_param", "string", "可选", False)
            ],
            function=lambda **kwargs: kwargs
        )

        is_valid, missing = registry._validate_parameters(
            tool=tool,
            provided_params={}
        )

        assert is_valid is False
        assert "required_param" in missing

    def test_validate_all_params_provided(self, registry):
        """测试所有参数都已提供"""
        tool = Tool(
            name="test_tool",
            description="测试",
            parameters=[
                ToolParameter("required_param", "string", "必需", True)
            ],
            function=lambda **kwargs: kwargs
        )

        is_valid, missing = registry._validate_parameters(
            tool=tool,
            provided_params={"required_param": "value"}
        )

        assert is_valid is True
        assert len(missing) == 0

    def test_validate_default_values(self, registry):
        """测试默认值"""
        tool = Tool(
            name="test_tool",
            description="测试",
            parameters=[
                ToolParameter("param", "integer", "参数", False, default=42)
            ],
            function=lambda **kwargs: kwargs
        )

        is_valid, missing = registry._validate_parameters(
            tool=tool,
            provided_params={}
        )

        # 可选参数有默认值,应该验证通过
        assert is_valid is True
