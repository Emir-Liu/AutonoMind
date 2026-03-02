"""API v1版本模块"""

from fastapi import APIRouter

# 创建v1路由
api_v1_router = APIRouter(prefix="/api/v1")

__all__ = ["api_v1_router"]
