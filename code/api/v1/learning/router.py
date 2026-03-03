"""对话式学习路由模块"""

from fastapi import APIRouter

router = APIRouter(prefix="/learning", tags=["对话式学习"])

from .routes import *
