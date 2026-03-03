"""WebSocket实时通信路由模块"""

from fastapi import APIRouter

router = APIRouter(prefix="/ws", tags=["WebSocket实时通信"])

from .routes import *
