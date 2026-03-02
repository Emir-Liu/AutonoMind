"""系统相关接口模块"""

from fastapi import APIRouter

router = APIRouter(prefix="/system", tags=["系统"])

__all__ = ["router"]
