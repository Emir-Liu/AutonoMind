"""会话相关接口模块"""

from fastapi import APIRouter

router = APIRouter(prefix="/sessions", tags=["会话"])

__all__ = ["router"]
