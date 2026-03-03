"""系统健康检查接口"""

from fastapi import APIRouter
from sqlalchemy import text

from api.v1.system.router import router
from utils.database import get_db_context
from utils.cache import check_redis_connection
from utils.logger import logger


@router.get("/health", tags=["系统"])
async def health_check():
    """健康检查"""
    # 检查数据库
    db_healthy = False
    try:
        async with get_db_context() as db:
            await db.execute(text("SELECT 1"))
            db_healthy = True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")

    # 检查Redis
    redis_healthy = await check_redis_connection()

    # 整体健康状态
    healthy = db_healthy and redis_healthy

    return {
        "status": "healthy" if healthy else "unhealthy",
        "database": {
            "status": "ok" if db_healthy else "error",
        },
        "redis": {
            "status": "ok" if redis_healthy else "error",
        },
    }


@router.get("/info", tags=["系统"])
async def system_info():
    """系统信息"""
    from config import settings

    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": settings.APP_DESCRIPTION,
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG,
    }
