"""向量嵌入工具模块

提供文本向量嵌入生成功能
"""

from typing import List, Optional
from openai import AsyncOpenAI
from config import settings
from utils.logger import logger


class EmbeddingService:
    """向量嵌入服务"""

    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_API_BASE,
            timeout=settings.OPENAI_TIMEOUT,
            max_retries=settings.OPENAI_MAX_RETRIES,
        )
        self.model = settings.EMBEDDING_MODEL
        self.dimension = settings.EMBEDDING_DIMENSION

    async def generate_embedding(
        self,
        text: str,
    ) -> List[float]:
        """生成单个文本的向量嵌入

        Args:
            text: 输入文本

        Returns:
            List[float]: 向量嵌入

        Raises:
            Exception: 嵌入生成失败
        """
        try:
            response = await self.client.embeddings.create(
                model=self.model,
                input=text,
            )

            embedding = response.data[0].embedding
            logger.debug(f"Generated embedding for text (length: {len(text)})")

            return embedding

        except Exception as e:
            logger.error(f"Generate embedding failed: {e}")
            raise

    async def generate_embeddings_batch(
        self,
        texts: List[str],
        batch_size: Optional[int] = None,
    ) -> List[List[float]]:
        """批量生成向量嵌入

        Args:
            texts: 输入文本列表
            batch_size: 批处理大小，默认使用配置值

        Returns:
            List[List[float]]: 向量嵌入列表

        Raises:
            Exception: 嵌入生成失败
        """
        if not texts:
            return []

        batch_size = batch_size or settings.EMBEDDING_BATCH_SIZE
        all_embeddings = []

        # 分批处理
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]

            try:
                response = await self.client.embeddings.create(
                    model=self.model,
                    input=batch,
                )

                # 按顺序提取嵌入
                batch_embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(batch_embeddings)

                logger.debug(f"Generated embeddings for batch {i//batch_size + 1}")

            except Exception as e:
                logger.error(f"Generate embeddings batch failed: {e}")
                raise

        logger.info(f"Generated {len(all_embeddings)} embeddings total")
        return all_embeddings

    async def count_tokens(self, text: str) -> int:
        """计算文本的Token数量

        Args:
            text: 输入文本

        Returns:
            int: Token数量
        """
        try:
            import tiktoken

            encoding = tiktoken.encoding_for_model(self.model)
            return len(encoding.encode(text))

        except Exception:
            # 降级处理：按字符估算
            return len(text) // 4


# 全局嵌入服务实例
embedding_service = EmbeddingService()


__all__ = [
    "EmbeddingService",
    "embedding_service",
]
