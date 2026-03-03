"""日志工具模块

提供结构化日志记录功能
"""

import sys
import os
from pathlib import Path
from loguru import logger
from config import settings


def setup_logger() -> None:
    """配置日志系统"""
    # 移除默认处理器
    logger.remove()

    # 确保日志目录存在
    log_dir = Path(settings.LOG_DIR)
    log_dir.mkdir(parents=True, exist_ok=True)

    # 控制台输出
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.LOG_LEVEL,
        colorize=True,
    )

    # 文件输出 - 所有日志
    logger.add(
        log_dir / "autonomind_{time:YYYY-MM-DD}.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=settings.LOG_LEVEL,
        rotation="00:00",  # 每天午夜轮转
        retention="30 days",  # 保留30天
        compression="zip",  # 压缩旧日志
        encoding="utf-8",
    )

    # 文件输出 - 错误日志
    logger.add(
        log_dir / "autonomind_error_{time:YYYY-MM-DD}.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="ERROR",
        rotation="00:00",
        retention="30 days",
        compression="zip",
        encoding="utf-8",
    )


# 初始化日志
setup_logger()

# 导出logger
__all__ = ["logger"]
