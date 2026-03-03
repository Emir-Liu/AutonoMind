"""知识库管理API接口"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict, Any

from api.v1.knowledge.router import router
from utils.database import get_db
from func.knowledge.knowledge_service import KnowledgeService
from func.knowledge.retrieval_service import RetrievalService
from models.schemas.knowledge import (
    KnowledgeCreate,
    KnowledgeUpdate,
    KnowledgeResponse,
    DeleteKnowledgeRequest,
)
from utils.dependencies import get_current_active_user
from utils.logger import logger
from core.embedding import EmbeddingService, QdrantVectorStore


# 获取检索服务实例
async def get_retrieval_service() -> RetrievalService:
    """获取检索服务实例"""
    # TODO: 从依赖注入中获取
    embedding_service = EmbeddingService()
    vector_store = QdrantVectorStore(collection_name="knowledge_base")
    async for db in get_db():
        yield RetrievalService(embedding_service, vector_store, db)


@router.post("/knowledge", response_model=KnowledgeResponse, status_code=status.HTTP_201_CREATED)
async def create_knowledge(
    request: dict = Body(..., description="知识数据"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user),
    retrieval_service: RetrievalService = Depends(get_retrieval_service),
):
    """创建知识

    Args:
        request: 知识数据
        db: 数据库会话
        current_user: 当前用户
        retrieval_service: 检索服务

    Returns:
        KnowledgeResponse: 创建的知识信息
    """
    try:
        # 生成Qdrant ID
        qdrant_id = KnowledgeService.generate_qdrant_id()

        # 创建知识记录
        knowledge = await KnowledgeService.create_knowledge(
            db,
            current_user.id,
            KnowledgeCreate(
                title=request.get("title"),
                content=request.get("content"),
                file_type=request.get("file_type", "text"),
                source=request.get("source"),
            ),
            embedding_model="text-embedding-3-small",
            qdrant_id=qdrant_id,
            chunk_count=1,
        )

        # 生成向量嵌入并存储到Qdrant
        await retrieval_service.add_knowledge_vectors(
            knowledge_id=knowledge.id,
            content=request.get("content", ""),
            metadata={
                "user_id": current_user.id,
                "title": request.get("title"),
                "source": request.get("source"),
            },
        )

        logger.info(f"知识创建成功: ID={knowledge.id}, Qdrant ID={qdrant_id}")
        return knowledge
    except Exception as e:
        logger.error(f"Create knowledge failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Create knowledge failed",
        )


@router.get("/knowledge", response_model=list[KnowledgeResponse])
async def list_knowledge(
    status: Optional[str] = Query(None, description="过滤状态"),
    file_type: Optional[str] = Query(None, description="过滤文件类型"),
    limit: int = Query(50, ge=1, le=100, description="返回数量限制"),
    offset: int = Query(0, ge=0, description="偏移量"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user),
):
    """获取用户的知识列表

    Args:
        status: 过滤状态
        file_type: 过滤文件类型
        limit: 返回数量限制
        offset: 偏移量
        db: 数据库会话
        current_user: 当前用户

    Returns:
        List[KnowledgeResponse]: 知识列表
    """
    try:
        knowledge_list, total = await KnowledgeService.list_knowledge(
            db, current_user.id, status, file_type, limit, offset
        )
        return knowledge_list
    except Exception as e:
        logger.error(f"List knowledge failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="List knowledge failed",
        )


@router.get("/knowledge/{knowledge_id}", response_model=KnowledgeResponse)
async def get_knowledge(
    knowledge_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user),
):
    """获取知识详情

    Args:
        knowledge_id: 知识ID
        db: 数据库会话
        current_user: 当前用户

    Returns:
        KnowledgeResponse: 知识详情
    """
    knowledge = await KnowledgeService.get_knowledge(db, knowledge_id, current_user.id)

    if not knowledge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge not found",
        )

    return knowledge


@router.put("/knowledge/{knowledge_id}", response_model=KnowledgeResponse)
async def update_knowledge(
    knowledge_id: int,
    knowledge_data: KnowledgeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user),
    retrieval_service: RetrievalService = Depends(get_retrieval_service),
):
    """更新知识

    Args:
        knowledge_id: 知识ID
        knowledge_data: 更新数据
        db: 数据库会话
        current_user: 当前用户
        retrieval_service: 检索服务

    Returns:
        KnowledgeResponse: 更新后的知识信息
    """
    try:
        # 获取原知识
        old_knowledge = await KnowledgeService.get_knowledge(db, knowledge_id, current_user.id)
        if not old_knowledge:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Knowledge not found",
            )

        # 更新知识记录
        knowledge = await KnowledgeService.update_knowledge(
            db,
            knowledge_id,
            current_user.id,
            knowledge_data,
        )

        # 如果内容更新,更新向量
        if knowledge_data.content:
            await retrieval_service.update_knowledge_vectors(
                knowledge_id=knowledge_id,
                content=knowledge_data.content,
                metadata={
                    "user_id": current_user.id,
                    "title": knowledge_data.title or old_knowledge.title,
                    "source": old_knowledge.source,
                },
            )

        logger.info(f"知识更新成功: ID={knowledge_id}")
        return knowledge
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Update knowledge failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Update knowledge failed",
        )


@router.delete("/knowledge/{knowledge_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_knowledge(
    knowledge_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user),
    retrieval_service: RetrievalService = Depends(get_retrieval_service),
):
    """删除知识（软删除）

    Args:
        knowledge_id: 知识ID
        db: 数据库会话
        current_user: 当前用户
        retrieval_service: 检索服务
    """
    try:
        # 删除知识记录
        await KnowledgeService.delete_knowledge(db, knowledge_id, current_user.id)
        # 删除向量
        await retrieval_service.delete_knowledge_vectors(knowledge_id)
        logger.info(f"知识删除成功: ID={knowledge_id}")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Delete knowledge failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Delete knowledge failed",
        )


@router.post("/knowledge/batch-delete")
async def batch_delete_knowledge(
    request: DeleteKnowledgeRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user),
    retrieval_service: RetrievalService = Depends(get_retrieval_service),
):
    """批量删除知识

    Args:
        request: 删除请求
        db: 数据库会话
        current_user: 当前用户
        retrieval_service: 检索服务

    Returns:
        dict: {"deleted_count": 删除数量, "failed_count": 失败数量}
    """
    try:
        deleted_count = 0
        failed_count = 0

        for knowledge_id in request.knowledge_ids:
            try:
                await KnowledgeService.delete_knowledge(db, knowledge_id, current_user.id)
                await retrieval_service.delete_knowledge_vectors(knowledge_id)
                deleted_count += 1
            except Exception as e:
                logger.error(f"批量删除知识失败: ID={knowledge_id}, error={e}")
                failed_count += 1

        logger.info(f"批量删除完成: 成功={deleted_count}, 失败={failed_count}")
        return {
            "success": True,
            "deleted_count": deleted_count,
            "failed_count": failed_count,
        }
    except Exception as e:
        logger.error(f"Batch delete knowledge failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Batch delete knowledge failed",
        )


@router.post("/knowledge/search", response_model=Dict[str, Any])
async def search_knowledge(
    query: str = Body(..., embed=True, min_length=1, description="查询文本"),
    top_k: int = Body(10, embed=True, ge=1, le=20, description="返回数量"),
    strategy: str = Body("vector", embed=True, description="检索策略: vector/keyword/hybrid"),
    filters: Optional[Dict[str, Any]] = Body(None, embed=True, description="过滤条件"),
    rerank: bool = Body(True, embed=True, description="是否重排序"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user),
    retrieval_service: RetrievalService = Depends(get_retrieval_service),
):
    """检索知识

    Args:
        query: 查询文本
        top_k: 返回数量
        strategy: 检索策略
        filters: 过滤条件
        rerank: 是否重排序
        db: 数据库会话
        current_user: 当前用户
        retrieval_service: 检索服务

    Returns:
        dict: 检索结果
    """
    try:
        result = await retrieval_service.search_knowledge(
            query=query,
            user_id=current_user.id,
            top_k=top_k,
            strategy=strategy,
            filters=filters,
            rerank=rerank,
        )

        logger.info(f"知识检索完成: query='{query}', results={result['total']}, strategy={strategy}")
        return result
    except Exception as e:
        logger.error(f"Search knowledge failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Search knowledge failed",
        )


@router.get("/knowledge/stats")
async def get_knowledge_stats(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user),
):
    """获取知识统计

    Args:
        db: 数据库会话
        current_user: 当前用户

    Returns:
        dict: 统计信息
    """
    try:
        stats = await KnowledgeService.get_statistics(db, current_user.id)
        return {
            "success": True,
            "data": stats,
        }
    except Exception as e:
        logger.error(f"Get knowledge stats failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Get knowledge stats failed",
        )


# 导入文件上传路由
from .file_routes import *



@router.post("/knowledge/upload")
async def upload_knowledge_file(
    file: UploadFile = File(..., description="上传的文件"),
    title: str = Query(..., description="知识标题"),
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """上传知识文件

    Args:
        file: 上传的文件
        title: 知识标题
        current_user: 当前用户
        db: 数据库会话

    Returns:
        dict: {"message": "上传成功", "knowledge_id": xxx}
    """
    # TODO: 实现文件上传逻辑
    # 1. 验证文件类型和大小
    # 2. 读取文件内容
    # 3. 创建知识记录
    # 4. 生成向量嵌入

    logger.warning("Knowledge file upload not fully implemented yet")
    return {
        "message": "Upload feature not fully implemented",
        "file_name": file.filename,
    }
