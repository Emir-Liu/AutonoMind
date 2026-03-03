"""知识库相关接口模块"""

from fastapi import APIRouter
from api.v1.knowledge.routes import (
    create_knowledge,
    list_knowledge,
    get_knowledge,
    update_knowledge,
    delete_knowledge,
    batch_delete_knowledge,
    search_knowledge,
    upload_knowledge_file,
)

router = APIRouter(prefix="/knowledge", tags=["知识库"])

# 注册路由
router.add_api_route("/knowledge", create_knowledge, methods=["POST"])
router.add_api_route("/knowledge", list_knowledge, methods=["GET"])
router.add_api_route("/knowledge/{knowledge_id}", get_knowledge, methods=["GET"])
router.add_api_route("/knowledge/{knowledge_id}", update_knowledge, methods=["PUT"])
router.add_api_route("/knowledge/{knowledge_id}", delete_knowledge, methods=["DELETE"])
router.add_api_route("/knowledge/batch-delete", batch_delete_knowledge, methods=["POST"])
router.add_api_route("/knowledge/search", search_knowledge, methods=["POST"])
router.add_api_route("/knowledge/upload", upload_knowledge_file, methods=["POST"])

__all__ = ["router"]
