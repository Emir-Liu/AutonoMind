"""会话相关接口模块"""

from fastapi import APIRouter
from api.v1.sessions.routes import (
    create_session,
    list_sessions,
    get_session,
    update_session,
    delete_session,
    get_messages,
    create_conversation,
)

router = APIRouter(prefix="/sessions", tags=["会话"])

# 注册路由
router.add_api_route("/sessions", create_session, methods=["POST"])
router.add_api_route("/sessions", list_sessions, methods=["GET"])
router.add_api_route("/sessions/{session_id}", get_session, methods=["GET"])
router.add_api_route("/sessions/{session_id}", update_session, methods=["PUT"])
router.add_api_route("/sessions/{session_id}", delete_session, methods=["DELETE"])
router.add_api_route("/sessions/{session_id}/messages", get_messages, methods=["GET"])
router.add_api_route("/conversations", create_conversation, methods=["POST"])

__all__ = ["router"]
