"""知识库服务模块

提供知识上传、向量嵌入、检索等业务逻辑
"""

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime
import uuid

from models.database import Knowledge, KnowledgeStatus
from models.schemas.knowledge import KnowledgeCreate, KnowledgeUpdate
from config import settings
from utils.logger import logger


class KnowledgeService:
    """知识库服务类"""

    @staticmethod
    async def create_knowledge(
        db: AsyncSession,
        user_id: int,
        knowledge_data: KnowledgeCreate,
        embedding_model: str,
        qdrant_id: str,
        chunk_count: int = 1,
    ) -> Knowledge:
        """创建知识

        Args:
            db: 数据库会话
            user_id: 用户ID
            knowledge_data: 知识数据
            embedding_model: 嵌入模型
            qdrant_id: Qdrant向量ID
            chunk_count: 分块数量

        Returns:
            Knowledge: 创建的知识对象
        """
        knowledge = Knowledge(
            user_id=user_id,
            title=knowledge_data.title,
            content=knowledge_data.content,
            file_type=knowledge_data.file_type,
            source=knowledge_data.source,
            status=KnowledgeStatus.ACTIVE,
            embedding_model=embedding_model,
            embedding_dimension=settings.EMBEDDING_DIMENSION,
            qdrant_id=qdrant_id,
            chunk_count=chunk_count,
            reference_count=0,
        )

        db.add(knowledge)
        await db.commit()
        await db.refresh(knowledge)

        logger.info(f"Knowledge created: {knowledge.id}")
        return knowledge

    @staticmethod
    async def get_knowledge(
        db: AsyncSession,
        knowledge_id: int,
        user_id: int,
    ) -> Optional[Knowledge]:
        """获取知识

        Args:
            db: 数据库会话
            knowledge_id: 知识ID
            user_id: 用户ID

        Returns:
            Optional[Knowledge]: 知识对象，不存在或无权访问返回None
        """
        result = await db.execute(
            select(Knowledge).where(
                Knowledge.id == knowledge_id,
                Knowledge.user_id == user_id,
                Knowledge.status != KnowledgeStatus.DELETED,
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_knowledge(
        db: AsyncSession,
        user_id: int,
        status: Optional[str] = None,
        file_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[List[Knowledge], int]:
        """列出用户的知识

        Args:
            db: 数据库会话
            user_id: 用户ID
            status: 过滤状态
            file_type: 过滤文件类型
            limit: 返回数量限制
            offset: 偏移量

        Returns:
            tuple: (知识列表, 总数)
        """
        # 构建查询
        query = select(Knowledge).where(
            Knowledge.user_id == user_id,
            Knowledge.status != KnowledgeStatus.DELETED,
        )

        if status:
            query = query.where(Knowledge.status == status)
        if file_type:
            query = query.where(Knowledge.file_type == file_type)

        # 获取总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # 获取知识列表
        query = query.order_by(Knowledge.updated_at.desc())
        query = query.limit(limit).offset(offset)
        result = await db.execute(query)
        knowledge_list = result.scalars().all()

        return list(knowledge_list), total

    @staticmethod
    async def update_knowledge(
        db: AsyncSession,
        knowledge_id: int,
        user_id: int,
        knowledge_data: KnowledgeUpdate,
    ) -> Knowledge:
        """更新知识

        Args:
            db: 数据库会话
            knowledge_id: 知识ID
            user_id: 用户ID
            knowledge_data: 知识更新数据

        Returns:
            Knowledge: 更新后的知识对象

        Raises:
            ValueError: 知识不存在
        """
        knowledge = await KnowledgeService.get_knowledge(db, knowledge_id, user_id)

        if not knowledge:
            raise ValueError(f"Knowledge {knowledge_id} not found")

        if knowledge_data.title is not None:
            knowledge.title = knowledge_data.title
        if knowledge_data.content is not None:
            knowledge.content = knowledge_data.content
        if knowledge_data.status is not None:
            knowledge.status = KnowledgeStatus(knowledge_data.status)
            if knowledge.status == KnowledgeStatus.ARCHIVED:
                knowledge.archived_at = datetime.utcnow()

        knowledge.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(knowledge)

        logger.info(f"Knowledge updated: {knowledge_id}")
        return knowledge

    @staticmethod
    async def delete_knowledge(
        db: AsyncSession,
        knowledge_id: int,
        user_id: int,
    ) -> bool:
        """删除知识（软删除）

        Args:
            db: 数据库会话
            knowledge_id: 知识ID
            user_id: 用户ID

        Returns:
            bool: 删除成功返回True

        Raises:
            ValueError: 知识不存在
        """
        knowledge = await KnowledgeService.get_knowledge(db, knowledge_id, user_id)

        if not knowledge:
            raise ValueError(f"Knowledge {knowledge_id} not found")

        knowledge.status = KnowledgeStatus.DELETED
        knowledge.updated_at = datetime.utcnow()

        await db.commit()

        logger.info(f"Knowledge deleted: {knowledge_id}")
        return True

    @staticmethod
    async def batch_delete_knowledge(
        db: AsyncSession,
        knowledge_ids: List[int],
        user_id: int,
    ) -> int:
        """批量删除知识

        Args:
            db: 数据库会话
            knowledge_ids: 知识ID列表
            user_id: 用户ID

        Returns:
            int: 删除的数量
        """
        count = 0
        for knowledge_id in knowledge_ids:
            try:
                await KnowledgeService.delete_knowledge(db, knowledge_id, user_id)
                count += 1
            except ValueError:
                continue

        logger.info(f"Batch deleted {count} knowledge items")
        return count

    @staticmethod
    async def search_knowledge(
        query_text: str,
        user_id: int,
        top_k: int = 5,
    ) -> List[dict]:
        """检索知识

        TODO: 实现向量检索逻辑

        Args:
            query_text: 查询文本
            user_id: 用户ID
            top_k: 返回数量

        Returns:
            List[dict]: 检索结果列表
        """
        # TODO: 实现实际的向量检索
        # 1. 对查询文本进行嵌入
        # 2. 在Qdrant中搜索相似向量
        # 3. 返回检索结果

        logger.warning("Knowledge search not implemented yet, returning empty results")
        return []

    @staticmethod
    def generate_qdrant_id() -> str:
        """生成Qdrant向量ID

        Returns:
            str: 唯一的向量ID
        """
        return str(uuid.uuid4())

    @staticmethod
    async def get_statistics(
        db: AsyncSession,
        user_id: int,
    ) -> dict:
        """获取知识统计

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            dict: 统计信息
        """
        # 总数统计
        total_result = await db.execute(
            select(func.count()).select_from(
                select(Knowledge).where(
                    Knowledge.user_id == user_id,
                    Knowledge.status != KnowledgeStatus.DELETED,
                ).subquery()
            )
        )
        total = total_result.scalar()

        # 按状态统计
        active_result = await db.execute(
            select(func.count()).select_from(
                select(Knowledge).where(
                    Knowledge.user_id == user_id,
                    Knowledge.status == KnowledgeStatus.ACTIVE,
                ).subquery()
            )
        )
        active = active_result.scalar()

        archived_result = await db.execute(
            select(func.count()).select_from(
                select(Knowledge).where(
                    Knowledge.user_id == user_id,
                    Knowledge.status == KnowledgeStatus.ARCHIVED,
                ).subquery()
            )
        )
        archived = archived_result.scalar()

        # 按文件类型统计
        type_result = await db.execute(
            select(Knowledge.file_type, func.count()).where(
                Knowledge.user_id == user_id,
                Knowledge.status != KnowledgeStatus.DELETED,
            ).group_by(Knowledge.file_type)
        )
        by_type = {row[0]: row[1] for row in type_result.all()}

        # 总引用次数
        ref_result = await db.execute(
            select(func.sum(Knowledge.reference_count)).where(
                Knowledge.user_id == user_id,
                Knowledge.status != KnowledgeStatus.DELETED,
            )
        )
        total_references = ref_result.scalar() or 0

        return {
            "total": total,
            "active": active,
            "archived": archived,
            "by_type": by_type,
            "total_references": total_references,
        }


__all__ = ["KnowledgeService"]
