"""FastAPI应用主入口"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import settings
from utils.logger import logger
from api.v1 import api_v1_router
from utils.database import init_db, close_db
from utils.cache import check_redis_connection


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理

    启动时: 初始化数据库、检查Redis连接
    关闭时: 清理资源
    """
    # 启动时执行
    logger.info("Starting AutonoMind application...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")

    # 初始化数据库
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

    # 检查Redis连接
    redis_connected = await check_redis_connection()
    if redis_connected:
        logger.info("Redis connected successfully")
    else:
        logger.warning("Redis connection failed, cache features may not work")

    logger.info("AutonoMind application started successfully")

    yield

    # 关闭时执行
    logger.info("Shutting down AutonoMind application...")
    await close_db()
    logger.info("Application shutdown complete")


# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,  # 生产环境关闭文档
    redoc_url="/redoc" if settings.DEBUG else None,
)


# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)


# 注册路由
app.include_router(api_v1_router)


# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理器"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": str(exc) if settings.DEBUG else "An unexpected error occurred"
        }
    )


# 根路径
@app.get("/")
async def root():
    """根路径"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": settings.APP_DESCRIPTION,
        "environment": settings.ENVIRONMENT,
    }


# 健康检查
@app.get("/health")
async def health_check():
    """健康检查端点"""
    db_ok = await check_db_connection()
    redis_ok = await check_redis_connection()

    return {
        "status": "healthy" if db_ok and redis_ok else "unhealthy",
        "database": "ok" if db_ok else "error",
        "redis": "ok" if redis_ok else "error",
    }


# 检查数据库连接
async def check_db_connection():
    """检查数据库连接"""
    try:
        from utils.database import check_db_connection as db_check
        return await db_check()
    except Exception:
        return False


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        workers=settings.WORKERS if not settings.DEBUG else 1,
    )
