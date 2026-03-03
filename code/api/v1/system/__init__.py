"""系统相关接口模块"""

from fastapi import APIRouter
from api.v1.system.health import health_check, system_info

router = APIRouter(prefix="/system", tags=["系统"])

# 注册路由
router.add_api_route("/health", health_check, methods=["GET"])
router.add_api_route("/info", system_info, methods=["GET"])

__all__ = ["router"]
