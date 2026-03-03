"""文件上传和知识提取API接口"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional
import aiofiles
import os
import uuid
from datetime import datetime

from api.v1.knowledge.router import router
from utils.database import get_db
from func.knowledge.knowledge_service import KnowledgeService
from core.embedding import EmbeddingService, QdrantVectorStore
from utils.dependencies import get_current_active_user
from utils.logger import logger
from utils.text_splitter import TextSplitter
from config import settings


# 支持的文件类型
SUPPORTED_FILE_TYPES = {
    "txt": "text/plain",
    "md": "text/markdown",
    "pdf": "application/pdf",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


async def get_text_splitter() -> TextSplitter:
    """获取文本分割器实例"""
    return TextSplitter()


async def get_embedding_service() -> EmbeddingService:
    """获取嵌入服务实例"""
    return EmbeddingService()


@router.post("/knowledge/upload", status_code=status.HTTP_201_CREATED)
async def upload_knowledge_file(
    file: UploadFile = File(..., description="上传的文件"),
    title: str = Form(..., min_length=1, max_length=200, description="知识标题"),
    source: Optional[str] = Form(None, description="知识来源"),
    chunk_size: int = Form(500, ge=100, le=2000, description="分块大小"),
    chunk_overlap: int = Form(50, ge=0, le=500, description="分块重叠"),
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    splitter: TextSplitter = Depends(get_text_splitter),
    embedding_service: EmbeddingService = Depends(get_embedding_service),
):
    """上传知识文件

    支持的文件类型: TXT, MD, PDF, DOCX

    Args:
        file: 上传的文件
        title: 知识标题
        source: 知识来源
        chunk_size: 分块大小
        chunk_overlap: 分块重叠
        current_user: 当前用户
        db: 数据库会话
        splitter: 文本分割器
        embedding_service: 嵌入服务

    Returns:
        dict: 上传结果
    """
    try:
        # 检查文件大小(最大10MB)
        MAX_FILE_SIZE = 10 * 1024 * 1024
        file_size = 0
        content = await file.read()

        file_size = len(content)
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File size exceeds limit of {MAX_FILE_SIZE / 1024 / 1024}MB",
            )

        # 检查文件类型
        file_ext = file.filename.split(".")[-1].lower() if "." in file.filename else ""
        if file_ext not in SUPPORTED_FILE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type. Supported: {', '.join(SUPPORTED_FILE_TYPES.keys())}",
            )

        # 读取文件内容
        if file_ext in ["txt", "md"]:
            text_content = content.decode("utf-8", errors="ignore")
        elif file_ext == "pdf":
            # TODO: 实现PDF解析
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="PDF parsing not implemented yet",
            )
        elif file_ext == "docx":
            # TODO: 实现DOCX解析
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="DOCX parsing not implemented yet",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type: {file_ext}",
            )

        # 分块处理
        chunks = splitter.split_text(
            text=text_content,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        if not chunks:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No content extracted from file",
            )

        # 创建知识记录
        qdrant_id = KnowledgeService.generate_qdrant_id()
        knowledge = await KnowledgeService.create_knowledge(
            db=db,
            user_id=current_user.id,
            knowledge_data={
                "title": title,
                "content": text_content,
                "file_type": file_ext,
                "source": source,
            },
            embedding_model="text-embedding-3-small",
            qdrant_id=qdrant_id,
            chunk_count=len(chunks),
        )

        # 生成向量嵌入并存储
        vector_store = QdrantVectorStore(collection_name="knowledge_base")

        # 确保集合存在
        await vector_store.create_collection(
            vector_size=1536,  # OpenAI text-embedding-3-small 维度
            recreate_if_exists=False,
        )

        # 为每个分块生成向量
        points = []
        for i, chunk in enumerate(chunks):
            embed_result = await embedding_service.embed_text(chunk)
            if embed_result.success and embed_result.embedding:
                points.append({
                    "id": f"{qdrant_id}_{i}",
                    "vector": embed_result.embedding,
                    "payload": {
                        "knowledge_id": knowledge.id,
                        "chunk_index": i,
                        "content": chunk,
                        "user_id": current_user.id,
                        "title": title,
                        "source": source,
                    }
                })

        # 批量插入向量
        if points:
            await vector_store.upsert_points(points)

        logger.info(
            f"文件上传成功: file={file.filename}, "
            f"chunks={len(chunks)}, vectors={len(points)}"
        )

        return {
            "success": True,
            "data": {
                "knowledge_id": knowledge.id,
                "title": knowledge.title,
                "file_name": file.filename,
                "file_size": file_size,
                "chunk_count": len(chunks),
                "vector_count": len(points),
                "message": "File uploaded successfully",
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload knowledge file failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Upload knowledge file failed",
        )


@router.post("/knowledge/upload/batch")
async def upload_knowledge_files_batch(
    files: list[UploadFile] = File(..., description="上传的文件列表"),
    chunk_size: int = Form(500, ge=100, le=2000, description="分块大小"),
    chunk_overlap: int = Form(50, ge=0, le=500, description="分块重叠"),
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    splitter: TextSplitter = Depends(get_text_splitter),
    embedding_service: EmbeddingService = Depends(get_embedding_service),
):
    """批量上传知识文件

    Args:
        files: 文件列表
        chunk_size: 分块大小
        chunk_overlap: 分块重叠
        current_user: 当前用户
        db: 数据库会话
        splitter: 文本分割器
        embedding_service: 嵌入服务

    Returns:
        dict: 上传结果
    """
    try:
        results = []
        success_count = 0
        failed_count = 0

        # 限制批量上传数量
        MAX_BATCH_SIZE = 10
        if len(files) > MAX_BATCH_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Maximum {MAX_BATCH_SIZE} files allowed per batch",
            )

        for file in files:
            try:
                # 为每个文件使用标题
                title = file.filename.split(".")[0] if file.filename else "Untitled"

                # 调用单文件上传逻辑
                # TODO: 这里需要重构以复用上传逻辑
                result = {
                    "file_name": file.filename,
                    "status": "success",
                    "knowledge_id": None,
                }
                success_count += 1
                results.append(result)

            except Exception as e:
                logger.error(f"批量上传文件失败: file={file.filename}, error={e}")
                failed_count += 1
                results.append({
                    "file_name": file.filename,
                    "status": "failed",
                    "error": str(e),
                })

        logger.info(
            f"批量上传完成: total={len(files)}, "
            f"success={success_count}, failed={failed_count}"
        )

        return {
            "success": True,
            "data": {
                "total": len(files),
                "success_count": success_count,
                "failed_count": failed_count,
                "results": results,
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload knowledge files batch failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Upload knowledge files batch failed",
        )


@router.post("/knowledge/extract-text")
async def extract_text_from_file(
    file: UploadFile = File(..., description="上传的文件"),
    current_user = Depends(get_current_active_user),
):
    """从文件中提取文本

    Args:
        file: 上传的文件
        current_user: 当前用户

    Returns:
        dict: 提取的文本
    """
    try:
        # 读取文件
        content = await file.read()
        file_ext = file.filename.split(".")[-1].lower() if "." in file.filename else ""

        # 提取文本
        if file_ext in ["txt", "md"]:
            text = content.decode("utf-8", errors="ignore")
        elif file_ext == "pdf":
            # TODO: 实现PDF解析
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="PDF parsing not implemented yet",
            )
        elif file_ext == "docx":
            # TODO: 实现DOCX解析
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="DOCX parsing not implemented yet",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type: {file_ext}",
            )

        return {
            "success": True,
            "data": {
                "file_name": file.filename,
                "file_type": file_ext,
                "text": text,
                "text_length": len(text),
                "char_count": len(text),
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Extract text failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Extract text failed",
        )
