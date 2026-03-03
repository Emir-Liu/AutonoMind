"""智能体相关接口模块"""

from fastapi import APIRouter
from api.v1.agents.routes import list_agents, get_agent
from api.v1.agents.auth import (
    register,
    login,
    get_current_user_info,
    update_current_user,
    delete_current_user,
)

router = APIRouter(prefix="/agents", tags=["智能体"])

# 注册路由
router.add_api_route("/agents", list_agents, methods=["GET"])
router.add_api_route("/agents/{agent_id}", get_agent, methods=["GET"])
router.add_api_route("/auth/register", register, methods=["POST"])
router.add_api_route("/auth/login", login, methods=["POST"])
router.add_api_route("/auth/me", get_current_user_info, methods=["GET"])
router.add_api_route("/auth/me", update_current_user, methods=["PUT"])
router.add_api_route("/auth/me", delete_current_user, methods=["DELETE"])

__all__ = ["router"]
