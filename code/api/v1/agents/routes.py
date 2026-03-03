"""智能体相关接口"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from api.v1.agents.router import router as agent_router
from utils.database import get_db
from models.database import User
from models.schemas.user import UserResponse
from utils.logger import logger


@agent_router.get("/agents", response_model=list[UserResponse])
async def list_agents(db: AsyncSession = Depends(get_db)):
    """获取所有智能体列表"""
    try:
        result = await db.execute(select(User))
        users = result.scalars().all()
        return users
    except Exception as e:
        logger.error(f"Failed to list agents: {e}")
        raise HTTPException(status_code=500, detail="Failed to list agents")


@agent_router.get("/agents/{agent_id}", response_model=UserResponse)
async def get_agent(agent_id: int, db: AsyncSession = Depends(get_db)):
    """获取智能体详情"""
    try:
        result = await db.execute(select(User).where(User.id == agent_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="Agent not found")
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get agent: {e}")
        raise HTTPException(status_code=500, detail="Failed to get agent")
