"""API v1版本模块"""

from fastapi import APIRouter

# 创建v1路由
api_v1_router = APIRouter(prefix="/api/v1")

# 导入并注册子路由
from api.v1.system import router as system_router
from api.v1.agents import router as agents_router
from api.v1.sessions import router as sessions_router
from api.v1.knowledge import router as knowledge_router
from api.v1.tools import router as tools_router
from api.v1.learning import router as learning_router
from api.v1.logs import router as logs_router
from api.v1.ws import router as ws_router

api_v1_router.include_router(system_router)
api_v1_router.include_router(agents_router)
api_v1_router.include_router(sessions_router)
api_v1_router.include_router(knowledge_router)
api_v1_router.include_router(tools_router)
api_v1_router.include_router(learning_router)
api_v1_router.include_router(logs_router)
api_v1_router.include_router(ws_router)

__all__ = ["api_v1_router"]
