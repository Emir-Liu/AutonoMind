"""会话管理API接口"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.sessions.router import router
from utils.database import get_db
from func.sessions.session_service import SessionService
from models.schemas.session import (
    SessionCreate,
    SessionUpdate,
    SessionResponse,
    MessageCreate,
    MessageResponse,
    ConversationRequest,
    ConversationResponse,
)
from utils.dependencies import get_current_active_user
from utils.logger import logger


@router.post("/sessions", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    session_data: SessionCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user),
):
    """创建新会话

    Args:
        session_data: 会话数据
        db: 数据库会话
        current_user: 当前用户

    Returns:
        SessionResponse: 创建的会话信息
    """
    try:
        session = await SessionService.create_session(db, current_user.id, session_data)
        return session
    except Exception as e:
        logger.error(f"Create session failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Create session failed",
        )


@router.get("/sessions", response_model=list[SessionResponse])
async def list_sessions(
    status: Optional[str] = Query(None, description="过滤状态"),
    limit: int = Query(50, ge=1, le=100, description="返回数量限制"),
    offset: int = Query(0, ge=0, description="偏移量"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user),
):
    """获取用户的会话列表

    Args:
        status: 过滤状态
        limit: 返回数量限制
        offset: 偏移量
        db: 数据库会话
        current_user: 当前用户

    Returns:
        List[SessionResponse]: 会话列表
    """
    try:
        sessions, _ = await SessionService.list_sessions(
            db, current_user.id, status, limit, offset
        )
        return sessions
    except Exception as e:
        logger.error(f"List sessions failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="List sessions failed",
        )


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user),
):
    """获取会话详情

    Args:
        session_id: 会话ID
        db: 数据库会话
        current_user: 当前用户

    Returns:
        SessionResponse: 会话详情
    """
    session = await SessionService.get_session(db, session_id, current_user.id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    return session


@router.put("/sessions/{session_id}", response_model=SessionResponse)
async def update_session(
    session_id: int,
    session_data: SessionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user),
):
    """更新会话

    Args:
        session_id: 会话ID
        session_data: 更新数据
        db: 数据库会话
        current_user: 当前用户

    Returns:
        SessionResponse: 更新后的会话信息
    """
    try:
        session = await SessionService.update_session(
            db,
            session_id,
            current_user.id,
            title=session_data.title,
            status=session_data.status,
        )
        return session
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Update session failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Update session failed",
        )


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user),
):
    """删除会话（软删除）

    Args:
        session_id: 会话ID
        db: 数据库会话
        current_user: 当前用户
    """
    try:
        await SessionService.delete_session(db, session_id, current_user.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Delete session failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Delete session failed",
        )


@router.get("/sessions/{session_id}/messages", response_model=list[MessageResponse])
async def get_messages(
    session_id: int,
    limit: int = Query(50, ge=1, le=100, description="返回数量限制"),
    offset: int = Query(0, ge=0, description="偏移量"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user),
):
    """获取会话的消息历史

    Args:
        session_id: 会话ID
        limit: 返回数量限制
        offset: 偏移量
        db: 数据库会话
        current_user: 当前用户

    Returns:
        List[MessageResponse]: 消息列表
    """
    # 验证会话权限
    session = await SessionService.get_session(db, session_id, current_user.id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    try:
        messages = await SessionService.get_messages(db, session_id, limit, offset)
        return messages
    except Exception as e:
        logger.error(f"Get messages failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Get messages failed",
        )


@router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(
    request: ConversationRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user),
):
    """创建对话（发送消息）

    Args:
        request: 对话请求
        db: 数据库会话
        current_user: 当前用户

    Returns:
        ConversationResponse: 对话响应
    """
    try:
        from func.agents.conversation_service import ConversationService

        result = await ConversationService.create_conversation(
            db,
            current_user.id,
            request,
        )

        return result

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Create conversation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Create conversation failed",
        )
