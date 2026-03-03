"""工具管理路由模块"""

from fastapi import APIRouter

router = APIRouter(prefix="/tools", tags=["工具管理"])

from .routes import *
