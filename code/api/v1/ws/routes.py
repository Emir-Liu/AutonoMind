"""WebSocket实时通信接口"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from typing import Dict, Any, Optional
import json
import asyncio
from datetime import datetime

from api.v1.ws.router import router
from utils.logger import logger


class ConnectionManager:
    """WebSocket连接管理器"""

    def __init__(self):
        # active_connections: Dict[str, Dict[str, WebSocket]] = {session_id: {user_id: WebSocket}}
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}

    async def connect(self, websocket: WebSocket, session_id: str, user_id: int):
        """建立连接"""
        await websocket.accept()

        if session_id not in self.active_connections:
            self.active_connections[session_id] = {}

        self.active_connections[session_id][str(user_id)] = websocket
        logger.info(f"WebSocket连接建立: session={session_id}, user={user_id}")

    def disconnect(self, session_id: str, user_id: int):
        """断开连接"""
        if session_id in self.active_connections:
            user_key = str(user_id)
            if user_key in self.active_connections[session_id]:
                del self.active_connections[session_id][user_key]

                # 如果会话没有连接了,删除会话记录
                if not self.active_connections[session_id]:
                    del self.active_connections[session_id]

            logger.info(f"WebSocket连接断开: session={session_id}, user={user_id}")

    async def send_personal_message(
        self,
        message: Dict[str, Any],
        session_id: str,
        user_id: int,
    ):
        """发送个人消息"""
        if session_id in self.active_connections:
            user_key = str(user_id)
            if user_key in self.active_connections[session_id]:
                websocket = self.active_connections[session_id][user_key]
                try:
                    await websocket.send_json(message)
                    logger.debug(f"发送个人消息: session={session_id}, user={user_id}")
                except Exception as e:
                    logger.error(f"发送个人消息失败: {e}")
                    self.disconnect(session_id, user_id)

    async def broadcast_to_session(
        self,
        message: Dict[str, Any],
        session_id: str,
        exclude_user_id: Optional[int] = None,
    ):
        """向会话广播消息"""
        if session_id in self.active_connections:
            disconnected_users = []

            for user_key, websocket in self.active_connections[session_id].items():
                user_id = int(user_key)

                # 排除指定用户
                if exclude_user_id and user_id == exclude_user_id:
                    continue

                try:
                    await websocket.send_json(message)
                except Exception as e:
                    logger.error(f"广播消息失败: user={user_id}, error={e}")
                    disconnected_users.append(user_id)

            # 清理断开的连接
            for user_id in disconnected_users:
                self.disconnect(session_id, user_id)

            logger.debug(f"广播消息到会话: session={session_id}, recipients={len(self.active_connections.get(session_id, {})) - len(disconnected_users)}")

    def get_connection_count(self, session_id: str) -> int:
        """获取会话连接数"""
        return len(self.active_connections.get(session_id, {}))


# 全局连接管理器
manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(..., description="JWT Token"),
    session_id: str = Query(..., description="会话ID"),
):
    """WebSocket实时通信端点

    Args:
        websocket: WebSocket连接
        token: JWT Token
        session_id: 会话ID
    """
    # 验证Token
    try:
        from utils.dependencies import decode_token
        payload = decode_token(token)
        user_id = payload.get("user_id")

        if not user_id:
            await websocket.close(code=4001, reason="Invalid token")
            return

    except Exception as e:
        logger.error(f"WebSocket认证失败: {e}")
        await websocket.close(code=4001, reason="Authentication failed")
        return

    # 建立连接
    await manager.connect(websocket, session_id, user_id)

    try:
        # 发送连接成功消息
        await websocket.send_json({
            "type": "connected",
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": session_id,
            "user_id": user_id,
        })

        # 消息处理循环
        while True:
            # 接收消息
            data = await websocket.receive_text()
            message = json.loads(data)

            # 处理消息
            await handle_websocket_message(websocket, message, session_id, user_id)

    except WebSocketDisconnect:
        manager.disconnect(session_id, user_id)
        logger.info(f"WebSocket正常断开: session={session_id}, user={user_id}")

    except Exception as e:
        logger.error(f"WebSocket错误: {e}", exc_info=True)
        manager.disconnect(session_id, user_id)


async def handle_websocket_message(
    websocket: WebSocket,
    message: Dict[str, Any],
    session_id: str,
    user_id: int,
):
    """处理WebSocket消息

    Args:
        websocket: WebSocket连接
        message: 消息内容
        session_id: 会话ID
        user_id: 用户ID
    """
    message_type = message.get("type")

    if message_type == "ping":
        # 心跳消息
        await websocket.send_json({
            "type": "pong",
            "timestamp": datetime.utcnow().isoformat(),
        })

    elif message_type == "message":
        # 发送消息
        await handle_send_message(websocket, message, session_id, user_id)

    elif message_type == "typing":
        # 正在输入
        await broadcast_typing_status(session_id, user_id, True)

    elif message_type == "typing_stop":
        # 停止输入
        await broadcast_typing_status(session_id, user_id, False)

    else:
        logger.warning(f"未知消息类型: {message_type}")
        await websocket.send_json({
            "type": "error",
            "error": f"Unknown message type: {message_type}",
        })


async def handle_send_message(
    websocket: WebSocket,
    message: Dict[str, Any],
    session_id: str,
    user_id: int,
):
    """处理发送消息

    Args:
        websocket: WebSocket连接
        message: 消息内容
        session_id: 会话ID
        user_id: 用户ID
    """
    try:
        content = message.get("content", "")
        if not content:
            await websocket.send_json({
                "type": "error",
                "error": "Message content is required",
            })
            return

        # TODO: 调用对话服务处理消息
        # 这里需要集成实际的对话处理逻辑

        # 模拟AI响应
        await websocket.send_json({
            "type": "message_start",
            "message_id": f"msg_{datetime.utcnow().timestamp()}",
            "role": "assistant",
        })

        # 模拟流式响应
        response_text = "这是AI的回复..."
        for i in range(len(response_text)):
            await asyncio.sleep(0.05)  # 模拟延迟
            await websocket.send_json({
                "type": "message_delta",
                "content": response_text[i],
            })

        await websocket.send_json({
            "type": "message_end",
            "message_id": f"msg_{datetime.utcnow().timestamp()}",
            "tokens": len(response_text),
        })

    except Exception as e:
        logger.error(f"处理发送消息失败: {e}", exc_info=True)
        await websocket.send_json({
            "type": "error",
            "error": "Failed to process message",
        })


async def broadcast_typing_status(
    session_id: str,
    user_id: int,
    is_typing: bool,
):
    """广播输入状态

    Args:
        session_id: 会话ID
        user_id: 用户ID
        is_typing: 是否正在输入
    """
    await manager.broadcast_to_session(
        message={
            "type": "typing_status",
            "user_id": user_id,
            "is_typing": is_typing,
            "timestamp": datetime.utcnow().isoformat(),
        },
        session_id=session_id,
        exclude_user_id=user_id,
    )


@router.get("/ws/status")
async def get_websocket_status(
    session_id: str = Query(..., description="会话ID"),
):
    """获取WebSocket连接状态

    Args:
        session_id: 会话ID

    Returns:
        dict: 连接状态
    """
    connection_count = manager.get_connection_count(session_id)

    return {
        "success": True,
        "data": {
            "session_id": session_id,
            "connection_count": connection_count,
            "active": connection_count > 0,
        },
    }
