"""工具管理API接口"""

from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional
from datetime import datetime

from api.v1.tools.router import router
from utils.database import get_db
from core.tool import ToolRegistry, ToolParameter
from core.tool.built_in_tools import register_built_in_tools, get_all_tool_schemas
from utils.dependencies import get_current_active_user
from utils.logger import logger


# 全局工具注册表实例
_tool_registry: Optional[ToolRegistry] = None


def get_tool_registry() -> ToolRegistry:
    """获取工具注册表实例"""
    global _tool_registry
    if _tool_registry is None:
        _tool_registry = ToolRegistry()
        register_built_in_tools(_tool_registry)
    return _tool_registry


@router.get("/tools")
async def list_tools(
    enabled: bool = Body(None, embed=True, description="是否只返回启用的工具"),
    current_user = Depends(get_current_active_user),
    registry: ToolRegistry = Depends(get_tool_registry),
):
    """列出所有可用工具

    Args:
        enabled: 是否只返回启用的工具
        current_user: 当前用户
        registry: 工具注册表

    Returns:
        list: 工具列表
    """
    try:
        schemas = registry.get_all_schemas(enabled_only=enabled)
        logger.info(f"列出工具: 总数={len(schemas)}, enabled={enabled}")
        return {
            "success": True,
            "data": schemas,
            "total": len(schemas),
        }
    except Exception as e:
        logger.error(f"List tools failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="List tools failed",
        )


@router.get("/tools/{tool_name}")
async def get_tool(
    tool_name: str,
    current_user = Depends(get_current_active_user),
    registry: ToolRegistry = Depends(get_tool_registry),
):
    """获取工具详情

    Args:
        tool_name: 工具名称
        current_user: 当前用户
        registry: 工具注册表

    Returns:
        dict: 工具详情
    """
    try:
        tool = registry.get_tool(tool_name)
        if not tool:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tool '{tool_name}' not found",
            )

        return {
            "success": True,
            "data": {
                "name": tool.name,
                "description": tool.description,
                "category": tool.category,
                "enabled": tool.enabled,
                "parameters": [
                    {
                        "name": p.name,
                        "type": p.type,
                        "description": p.description,
                        "required": p.required,
                        "default": p.default,
                    }
                    for p in tool.parameters
                ],
                "created_at": tool.created_at,
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get tool failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Get tool failed",
        )


@router.post("/tools")
async def register_tool(
    name: str = Body(..., embed=True, min_length=1),
    description: str = Body(..., embed=True, min_length=1),
    category: str = Body("custom", embed=True, description="工具分类"),
    parameters: list[Dict[str, Any]] = Body([], embed=True, description="参数列表"),
    function_name: str = Body(None, embed=True, description="Python函数路径"),
    current_user = Depends(get_current_active_user),
    registry: ToolRegistry = Depends(get_tool_registry),
):
    """注册自定义工具

    Args:
        name: 工具名称
        description: 工具描述
        category: 工具分类
        parameters: 参数列表
        function_name: Python函数路径
        current_user: 当前用户
        registry: 工具注册表

    Returns:
        dict: 注册结果
    """
    try:
        # 检查工具是否已存在
        if registry.get_tool(name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tool '{name}' already exists",
            )

        # 构建参数对象
        tool_params = []
        for param in parameters:
            tool_params.append(
                ToolParameter(
                    name=param.get("name", ""),
                    type=param.get("type", "string"),
                    description=param.get("description", ""),
                    required=param.get("required", False),
                    default=param.get("default"),
                )
            )

        # TODO: 实现动态函数加载
        # 如果提供了function_name,动态导入并注册
        # 这里暂时创建一个占位函数
        async def placeholder_function(**kwargs):
            return {"error": "Tool function not implemented yet"}

        # 注册工具
        registry.register(
            name=name,
            description=description,
            function=placeholder_function,
            parameters=tool_params,
            category=category,
        )

        logger.info(f"工具注册成功: name={name}, user={current_user.id}")
        return {
            "success": True,
            "data": {
                "name": name,
                "message": "Tool registered successfully",
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Register tool failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Register tool failed",
        )


@router.patch("/tools/{tool_name}")
async def update_tool(
    tool_name: str,
    enabled: bool = Body(..., embed=True, description="是否启用"),
    current_user = Depends(get_current_active_user),
    registry: ToolRegistry = Depends(get_tool_registry),
):
    """启用/禁用工具

    Args:
        tool_name: 工具名称
        enabled: 是否启用
        current_user: 当前用户
        registry: 工具注册表

    Returns:
        dict: 更新结果
    """
    try:
        tool = registry.get_tool(tool_name)
        if not tool:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tool '{tool_name}' not found",
            )

        # 更新工具状态
        if enabled:
            registry.enable(tool_name)
        else:
            registry.disable(tool_name)

        logger.info(f"工具状态更新: name={tool_name}, enabled={enabled}")
        return {
            "success": True,
            "data": {
                "name": tool_name,
                "enabled": enabled,
                "message": "Tool updated successfully",
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update tool failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Update tool failed",
        )


@router.delete("/tools/{tool_name}")
async def unregister_tool(
    tool_name: str,
    current_user = Depends(get_current_active_user),
    registry: ToolRegistry = Depends(get_tool_registry),
):
    """删除工具

    Args:
        tool_name: 工具名称
        current_user: 当前用户
        registry: 工具注册表

    Returns:
        dict: 删除结果
    """
    try:
        tool = registry.get_tool(tool_name)
        if not tool:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tool '{tool_name}' not found",
            )

        # 内置工具不允许删除
        if tool.category == "built-in":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Built-in tools cannot be deleted",
            )

        # 删除工具
        registry.unregister(tool_name)

        logger.info(f"工具删除成功: name={tool_name}")
        return {
            "success": True,
            "message": "Tool unregistered successfully",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unregister tool failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unregister tool failed",
        )


@router.post("/tools/execute")
async def execute_tool(
    tool_name: str = Body(..., embed=True),
    parameters: Dict[str, Any] = Body({}, embed=True),
    current_user = Depends(get_current_active_user),
    registry: ToolRegistry = Depends(get_tool_registry),
):
    """执行工具

    Args:
        tool_name: 工具名称
        parameters: 工具参数
        current_user: 当前用户
        registry: 工具注册表

    Returns:
        dict: 执行结果
    """
    try:
        tool = registry.get_tool(tool_name)
        if not tool:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tool '{tool_name}' not found",
            )

        # 检查工具是否启用
        if not tool.enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tool '{tool_name}' is disabled",
            )

        # 执行工具
        result = await registry.execute(
            name=tool_name,
            parameters=parameters,
        )

        logger.info(f"工具执行成功: name={tool_name}, user={current_user.id}")
        return {
            "success": True,
            "data": result,
            "tool_name": tool_name,
        }
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"工具参数验证失败: name={tool_name}, error={e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid parameters: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Execute tool failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Execute tool failed",
        )


@router.get("/tools/stats")
async def get_tool_stats(
    current_user = Depends(get_current_active_user),
    registry: ToolRegistry = Depends(get_tool_registry),
):
    """获取工具统计

    Args:
        current_user: 当前用户
        registry: 工具注册表

    Returns:
        dict: 统计信息
    """
    try:
        all_tools = registry.get_all_schemas(enabled_only=False)
        enabled_tools = registry.get_all_schemas(enabled_only=True)

        # 按分类统计
        by_category: Dict[str, int] = {}
        for tool in all_tools:
            category = tool.get("category", "unknown")
            by_category[category] = by_category.get(category, 0) + 1

        return {
            "success": True,
            "data": {
                "total": len(all_tools),
                "enabled": len(enabled_tools),
                "disabled": len(all_tools) - len(enabled_tools),
                "by_category": by_category,
            },
        }
    except Exception as e:
        logger.error(f"Get tool stats failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Get tool stats failed",
        )
