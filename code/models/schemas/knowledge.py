"""知识库相关的Pydantic模型"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class KnowledgeBase(BaseModel):
    """知识基础模型"""
    title: str = Field(..., min_length=1, max_length=200, description="知识标题")
    content: str = Field(..., min_length=1, description="知识内容")
    file_type: str = Field(..., description="文件类型: text, pdf, doc, image")
    source: Optional[str] = Field(None, max_length=200, description="来源")


class KnowledgeCreate(KnowledgeBase):
    """知识创建模型"""
    pass


class KnowledgeUpdate(BaseModel):
    """知识更新模型"""
    title: Optional[str] = Field(None, max_length=200)
    content: Optional[str] = None
    status: Optional[str] = Field(None, description="状态: active, archived, deleted")


class KnowledgeResponse(KnowledgeBase):
    """知识响应模型"""
    id: int
    user_id: int
    status: str
    embedding_model: str
    embedding_dimension: int
    qdrant_id: str
    chunk_count: int
    reference_count: int
    created_at: datetime
    updated_at: datetime
    archived_at: Optional[datetime]
    metadata: Optional[dict]

    class Config:
        from_attributes = True


class KnowledgeSearchResult(BaseModel):
    """知识检索结果"""
    id: int
    title: str
    content: str
    score: float
    metadata: Optional[dict]


class UploadKnowledgeRequest(BaseModel):
    """上传知识请求"""
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    file_type: str = Field(default="text", description="文件类型")
    source: Optional[str] = None


class DeleteKnowledgeRequest(BaseModel):
    """删除知识请求"""
    knowledge_ids: list[int] = Field(..., min_length=1, description="知识ID列表")


__all__ = [
    "KnowledgeBase",
    "KnowledgeCreate",
    "KnowledgeUpdate",
    "KnowledgeResponse",
    "KnowledgeSearchResult",
    "UploadKnowledgeRequest",
    "DeleteKnowledgeRequest",
]
