"""智能体相关接口模块"""

from fastapi import APIRouter

router = APIRouter(prefix="/agents", tags=["智能体"])

__all__ = ["router"]
