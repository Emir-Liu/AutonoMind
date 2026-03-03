"""会话相关的Pydantic模型"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class SessionBase(BaseModel):
    """会话基础模型"""
    title: str = Field(..., min_length=1, max_length=200, description="会话标题")
    agent_id: str = Field(..., description="智能体ID")


class SessionCreate(SessionBase):
    """会话创建模型"""
    pass


class SessionUpdate(BaseModel):
    """会话更新模型"""
    title: Optional[str] = Field(None, max_length=200)
    status: Optional[str] = Field(None, description="状态: active, archived, deleted")


class SessionResponse(SessionBase):
    """会话响应模型"""
    id: int
    user_id: int
    status: str
    message_count: int
    created_at: datetime
    updated_at: datetime
    archived_at: Optional[datetime]
    metadata: Optional[dict]

    class Config:
        from_attributes = True


class MessageBase(BaseModel):
    """消息基础模型"""
    role: str = Field(..., description="角色: user, assistant, system")
    content: str = Field(..., min_length=1, description="消息内容")


class MessageCreate(MessageBase):
    """消息创建模型"""
    pass


class MessageResponse(MessageBase):
    """消息响应模型"""
    id: int
    session_id: int
    prompt_tokens: Optional[int]
    completion_tokens: Optional[int]
    total_tokens: Optional[int]
    execution_time_ms: Optional[int]
    created_at: datetime
    metadata: Optional[dict]

    class Config:
        from_attributes = True


class ConversationRequest(BaseModel):
    """对话请求模型"""
    session_id: Optional[int] = Field(None, description="会话ID，为空时自动创建新会话")
    message: str = Field(..., min_length=1, description="用户消息")
    title: Optional[str] = Field(None, max_length=200, description="新会话标题")
    agent_id: str = Field("default", description="智能体ID")


class ConversationResponse(BaseModel):
    """对话响应模型"""
    session_id: int
    message_id: int
    response: str
    tokens: Optional[dict]
    execution_time_ms: Optional[int]


__all__ = [
    "SessionBase",
    "SessionCreate",
    "SessionUpdate",
    "SessionResponse",
    "MessageBase",
    "MessageCreate",
    "MessageResponse",
    "ConversationRequest",
    "ConversationResponse",
]
