"""用户认证API接口"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.agents.router import router
from utils.database import get_db
from func.agents.user_service import UserService
from models.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse, UserUpdate
from utils.dependencies import get_current_active_user
from utils.logger import logger


@router.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """用户注册

    Args:
        user_data: 用户注册信息
        db: 数据库会话

    Returns:
        UserResponse: 创建的用户信息
    """
    try:
        user = await UserService.create_user(db, user_data)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Registration failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed",
        )


@router.post("/auth/login", response_model=TokenResponse)
async def login(
    user_data: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    """用户登录

    Args:
        user_data: 登录信息
        db: 数据库会话

    Returns:
        TokenResponse: 访问Token和刷新Token
    """
    try:
        result = await UserService.login_user(db, user_data.username, user_data.password)
        return TokenResponse(
            access_token=result["access_token"],
            refresh_token=result["refresh_token"],
            token_type=result["token_type"],
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed",
        )


@router.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(
    current_user = Depends(get_current_active_user),
):
    """获取当前用户信息

    Args:
        current_user: 当前登录用户

    Returns:
        UserResponse: 用户信息
    """
    return current_user


@router.put("/auth/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user),
):
    """更新当前用户信息

    Args:
        user_data: 用户更新信息
        db: 数据库会话
        current_user: 当前登录用户

    Returns:
        UserResponse: 更新后的用户信息
    """
    try:
        updated_user = await UserService.update_user(db, current_user.id, user_data)
        return updated_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Update user failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Update failed",
        )


@router.delete("/auth/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_current_user(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user),
):
    """删除当前用户（软删除）

    Args:
        db: 数据库会话
        current_user: 当前登录用户
    """
    try:
        await UserService.delete_user(db, current_user.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Delete user failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Delete failed",
        )
