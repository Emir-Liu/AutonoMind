"""对话式学习API接口"""

from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional
from datetime import datetime

from api.v1.learning.router import router
from utils.database import get_db
from core.conversational_learning import ConversationLearningEngine
from utils.dependencies import get_current_active_user
from utils.logger import logger
from utils.llm import LLMManager


# 全局学习引擎实例
_learning_engine: Optional[ConversationLearningEngine] = None


def get_learning_engine() -> ConversationLearningEngine:
    """获取学习引擎实例"""
    global _learning_engine
    if _learning_engine is None:
        # TODO: 从依赖注入中获取
        llm_manager = LLMManager()
        async for db in get_db():
            _learning_engine = ConversationLearningEngine(
                db_session=db,
                llm_manager=llm_manager,
            )
            break
    return _learning_engine


@router.post("/learning/detect-intent")
async def detect_learning_intent(
    user_message: str = Body(..., embed=True, min_length=1),
    assistant_message: str = Body(None, embed=True),
    current_user = Depends(get_current_active_user),
    learning_engine: ConversationLearningEngine = Depends(get_learning_engine),
):
    """检测学习意图

    Args:
        user_message: 用户消息
        assistant_message: 助手消息
        current_user: 当前用户
        learning_engine: 学习引擎

    Returns:
        dict: 学习意图
    """
    try:
        intent_result = await learning_engine.detect_learning_intent(
            user_message=user_message,
            assistant_message=assistant_message,
        )

        logger.info(f"学习意图检测: user={current_user.id}, intent={intent_result.intent}")
        return {
            "success": True,
            "data": intent_result.model_dump(),
        }
    except Exception as e:
        logger.error(f"Detect learning intent failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Detect learning intent failed",
        )


@router.post("/learning/extract-knowledge")
async def extract_knowledge(
    user_message: str = Body(..., embed=True, min_length=1),
    assistant_message: str = Body(None, embed=True),
    intent: str = Body("new", embed=True, description="学习意图"),
    current_user = Depends(get_current_active_user),
    learning_engine: ConversationLearningEngine = Depends(get_learning_engine),
):
    """提取知识

    Args:
        user_message: 用户消息
        assistant_message: 助手消息
        intent: 学习意图
        current_user: 当前用户
        learning_engine: 学习引擎

    Returns:
        dict: 提取的知识
    """
    try:
        knowledge = await learning_engine.extract_knowledge(
            user_message=user_message,
            assistant_message=assistant_message,
            intent=intent,
        )

        logger.info(f"知识提取成功: user={current_user.id}, confidence={knowledge.confidence}")
        return {
            "success": True,
            "data": knowledge.model_dump(),
        }
    except Exception as e:
        logger.error(f"Extract knowledge failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Extract knowledge failed",
        )


@router.post("/learning/process")
async def process_learning(
    user_message: str = Body(..., embed=True, min_length=1),
    assistant_message: str = Body(None, embed=True),
    auto_approve: bool = Body(False, embed=True, description="是否自动批准"),
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    learning_engine: ConversationLearningEngine = Depends(get_learning_engine),
):
    """处理学习流程

    Args:
        user_message: 用户消息
        assistant_message: 助手消息
        auto_approve: 是否自动批准
        current_user: 当前用户
        db: 数据库会话
        learning_engine: 学习引擎

    Returns:
        dict: 学习结果
    """
    try:
        result = await learning_engine.process_learning(
            user_message=user_message,
            assistant_message=assistant_message,
            auto_approve=auto_approve,
        )

        logger.info(
            f"学习处理完成: user={current_user.id}, "
            f"intent={result.intent}, approved={result.auto_approved}"
        )
        return {
            "success": True,
            "data": result.model_dump(),
        }
    except Exception as e:
        logger.error(f"Process learning failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Process learning failed",
        )


@router.get("/learning/records")
async def list_learning_records(
    session_id: Optional[int] = Body(None, embed=True, description="会话ID"),
    intent: Optional[str] = Body(None, embed=True, description="学习意图"),
    status: Optional[str] = Body(None, embed=True, description="审核状态"),
    limit: int = Body(50, embed=True, ge=1, le=100),
    offset: int = Body(0, embed=True, ge=0),
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """列出学习记录

    Args:
        session_id: 会话ID
        intent: 学习意图
        status: 审核状态
        limit: 返回数量限制
        offset: 偏移量
        current_user: 当前用户
        db: 数据库会话

    Returns:
        dict: 学习记录列表
    """
    try:
        from models.database import LearningRecord, LearningIntent, ApprovalStatus
        from sqlalchemy import select, func

        # 构建查询
        query = select(LearningRecord).where(
            LearningRecord.user_id == current_user.id,
        )

        if session_id:
            query = query.where(LearningRecord.session_id == session_id)
        if intent:
            query = query.where(LearningRecord.intent == LearningIntent(intent))
        if status:
            query = query.where(LearningRecord.approval_status == ApprovalStatus(status))

        # 获取总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # 获取记录列表
        query = query.order_by(LearningRecord.created_at.desc())
        query = query.limit(limit).offset(offset)
        result = await db.execute(query)
        records = result.scalars().all()

        logger.info(f"列出学习记录: user={current_user.id}, count={total}")
        return {
            "success": True,
            "data": records,
            "total": total,
            "limit": limit,
            "offset": offset,
        }
    except Exception as e:
        logger.error(f"List learning records failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="List learning records failed",
        )


@router.get("/learning/records/{record_id}")
async def get_learning_record(
    record_id: int,
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """获取学习记录详情

    Args:
        record_id: 记录ID
        current_user: 当前用户
        db: 数据库会话

    Returns:
        dict: 学习记录详情
    """
    try:
        from models.database import LearningRecord
        from sqlalchemy import select

        result = await db.execute(
            select(LearningRecord).where(
                LearningRecord.id == record_id,
                LearningRecord.user_id == current_user.id,
            )
        )
        record = result.scalar_one_or_none()

        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Learning record not found",
            )

        return {
            "success": True,
            "data": record,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get learning record failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Get learning record failed",
        )


@router.patch("/learning/records/{record_id}/approve")
async def approve_learning_record(
    record_id: int,
    approved: bool = Body(..., embed=True, description="是否批准"),
    review_comment: Optional[str] = Body(None, embed=True, description="审核意见"),
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    learning_engine: ConversationLearningEngine = Depends(get_learning_engine),
):
    """审核学习记录

    Args:
        record_id: 记录ID
        approved: 是否批准
        review_comment: 审核意见
        current_user: 当前用户
        db: 数据库会话
        learning_engine: 学习引擎

    Returns:
        dict: 审核结果
    """
    try:
        # 获取记录
        from models.database import LearningRecord
        from sqlalchemy import select

        result = await db.execute(
            select(LearningRecord).where(
                LearningRecord.id == record_id,
                LearningRecord.user_id == current_user.id,
            )
        )
        record = result.scalar_one_or_none()

        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Learning record not found",
            )

        # 更新审核状态
        await learning_engine.approve_learning(
            record_id=record_id,
            approved=approved,
            reviewer_id=current_user.id,
            comment=review_comment,
        )

        logger.info(f"学习记录审核: id={record_id}, approved={approved}")
        return {
            "success": True,
            "message": "Learning record approved successfully",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Approve learning record failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Approve learning record failed",
        )


@router.get("/learning/stats")
async def get_learning_stats(
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """获取学习统计

    Args:
        current_user: 当前用户
        db: 数据库会话

    Returns:
        dict: 统计信息
    """
    try:
        from models.database import LearningRecord, LearningIntent, ApprovalStatus
        from sqlalchemy import select, func

        # 总学习次数
        total_result = await db.execute(
            select(func.count()).select_from(
                select(LearningRecord).where(
                    LearningRecord.user_id == current_user.id,
                ).subquery()
            )
        )
        total = total_result.scalar()

        # 按意图统计
        intent_result = await db.execute(
            select(LearningRecord.intent, func.count()).where(
                LearningRecord.user_id == current_user.id,
            ).group_by(LearningRecord.intent)
        )
        by_intent = {str(row[0]): row[1] for row in intent_result.all()}

        # 按状态统计
        status_result = await db.execute(
            select(LearningRecord.approval_status, func.count()).where(
                LearningRecord.user_id == current_user.id,
            ).group_by(LearningRecord.approval_status)
        )
        by_status = {str(row[0]): row[1] for row in status_result.all()}

        # 平均置信度
        avg_result = await db.execute(
            select(func.avg(LearningRecord.confidence)).where(
                LearningRecord.user_id == current_user.id,
            )
        )
        avg_confidence = float(avg_result.scalar() or 0)

        return {
            "success": True,
            "data": {
                "total": total,
                "by_intent": by_intent,
                "by_status": by_status,
                "avg_confidence": avg_confidence,
            },
        }
    except Exception as e:
        logger.error(f"Get learning stats failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Get learning stats failed",
        )
