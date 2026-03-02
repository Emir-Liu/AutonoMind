"""知识库相关接口模块"""

from fastapi import APIRouter

router = APIRouter(prefix="/knowledge", tags=["知识库"])

__all__ = ["router"]
