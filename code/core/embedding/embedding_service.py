"""向量嵌入服务

集成OpenAI Embedding API，实现文本向量化、分块处理
"""

from typing import List, Dict, Any, Optional
from enum import Enum
import re

from openai import AsyncOpenAI

from utils.logger import logger
from config import settings


class EmbeddingModel(str, Enum):
    """嵌入模型枚举"""

    OPENAI_TEXT_EMBEDDING_3_SMALL = "text-embedding-3-small"
    OPENAI_TEXT_EMBEDDING_3_LARGE = "text-embedding-3-large"
    OPENAI_TEXT_EMBEDDING_ADA_002 = "text-embedding-ada-002"


class TextChunk:
    """文本块"""

    def __init__(
        self,
        content: str,
        index: int,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.content = content
        self.index = index
        self.metadata = metadata or {}


class EmbeddingResult:
    """嵌入结果"""

    def __init__(
        self,
        vector: List[float],
        model: str,
        tokens: int,
    ):
        self.vector = vector
        self.model = model
        self.tokens = tokens


class EmbeddingService:
    """向量嵌入服务"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: EmbeddingModel = EmbeddingModel.OPENAI_TEXT_EMBEDDING_3_SMALL,
    ):
        self.model = model
        self.client = AsyncOpenAI(
            api_key=api_key or settings.OPENAI_API_KEY,
            base_url=base_url or settings.OPENAI_API_BASE,
        )
        logger.info(f"初始化Embedding服务, 模型: {self.model}")

    # ========== 文本分块 ==========

    def chunk_text(
        self,
        text: str,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        separator: str = "\n\n",
    ) -> List[TextChunk]:
        """将文本分块

        Args:
            text: 输入文本
            chunk_size: 每块的最大字符数
            chunk_overlap: 块之间的重叠字符数
            separator: 分隔符

        Returns:
            List[TextChunk]: 文本块列表
        """
        if not text or len(text) <= chunk_size:
            return [TextChunk(content=text, index=0)]

        # 按分隔符分割
        chunks_text = text.split(separator)
        chunks: List[TextChunk] = []
        current_chunk = ""
        chunk_index = 0

        for chunk_text in chunks_text:
            # 如果当前块加上新内容超过大小限制
            if len(current_chunk) + len(chunk_text) + len(separator) > chunk_size:
                # 保存当前块
                if current_chunk:
                    chunks.append(
                        TextChunk(
                            content=current_chunk.strip(),
                            index=chunk_index,
                        )
                    )
                    chunk_index += 1

                    # 处理重叠
                    if chunk_overlap > 0 and chunks:
                        current_chunk = (
                            chunks[-1].content[-chunk_overlap:]
                            if len(chunks[-1].content) > chunk_overlap
                            else chunks[-1].content
                        )
                    else:
                        current_chunk = ""
                else:
                    # 单个段落太长，强制分割
                    for i in range(0, len(chunk_text), chunk_size):
                        chunks.append(
                            TextChunk(
                                content=chunk_text[i : i + chunk_size],
                                index=chunk_index,
                            )
                        )
                        chunk_index += 1

            current_chunk += chunk_text + separator

        # 保存最后一个块
        if current_chunk.strip():
            chunks.append(
                TextChunk(
                    content=current_chunk.strip(),
                    index=chunk_index,
                )
            )

        logger.info(f"文本分块完成: {len(chunks)} 块, 总长度: {len(text)}")
        return chunks

    def chunk_text_by_sentences(
        self,
        text: str,
        max_sentences: int = 10,
    ) -> List[TextChunk]:
        """按句子分块

        Args:
            text: 输入文本
            max_sentences: 每块的最大句子数

        Returns:
            List[TextChunk]: 文本块列表
        """
        # 使用正则表达式分割句子
        sentences = re.split(r"(?<=[.!?。！？])\s+", text)
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            return [TextChunk(content=text, index=0)]

        # 将句子组合成块
        chunks: List[TextChunk] = []
        for i in range(0, len(sentences), max_sentences):
            chunk_sentences = sentences[i : i + max_sentences]
            chunk_text = "".join(chunk_sentences)
            chunks.append(TextChunk(content=chunk_text, index=i // max_sentences))

        logger.info(f"按句子分块完成: {len(chunks)} 块")
        return chunks

    # ========== 生成嵌入 ==========

    async def embed_text(
        self,
        text: str,
    ) -> EmbeddingResult:
        """生成文本的向量嵌入

        Args:
            text: 输入文本

        Returns:
            EmbeddingResult: 嵌入结果
        """
        try:
            response = await self.client.embeddings.create(
                model=self.model.value,
                input=text,
            )

            vector = response.data[0].embedding
            tokens = response.usage.total_tokens

            result = EmbeddingResult(
                vector=vector,
                model=self.model.value,
                tokens=tokens,
            )

            logger.debug(f"生成嵌入成功, 长度: {len(vector)}, tokens: {tokens}")
            return result

        except Exception as e:
            logger.error(f"生成嵌入失败: {e}")
            raise

    async def embed_text_batch(
        self,
        texts: List[str],
    ) -> List[EmbeddingResult]:
        """批量生成文本嵌入

        Args:
            texts: 输入文本列表

        Returns:
            List[EmbeddingResult]: 嵌入结果列表
        """
        if not texts:
            return []

        try:
            response = await self.client.embeddings.create(
                model=self.model.value,
                input=texts,
            )

            results = []
            for idx, data in enumerate(response.data):
                results.append(
                    EmbeddingResult(
                        vector=data.embedding,
                        model=self.model.value,
                        tokens=response.usage.total_tokens // len(texts),
                    )
                )

            logger.info(f"批量生成嵌入成功: {len(results)} 条")
            return results

        except Exception as e:
            logger.error(f"批量生成嵌入失败: {e}")
            raise

    async def embed_chunks(
        self,
        chunks: List[TextChunk],
    ) -> List[Dict[str, Any]]:
        """为文本块生成嵌入

        Args:
            chunks: 文本块列表

        Returns:
            List[Dict]: 嵌入结果列表
            [{
                "vector": [...],
                "content": "文本内容",
                "tokens": 100,
                "metadata": {...}
            }]
        """
        texts = [chunk.content for chunk in chunks]

        embedding_results = await self.embed_text_batch(texts)

        results = []
        for idx, (chunk, embed_result) in enumerate(zip(chunks, embedding_results)):
            results.append(
                {
                    "vector": embed_result.vector,
                    "content": chunk.content,
                    "tokens": embed_result.tokens,
                    "metadata": {
                        "chunk_index": chunk.index,
                        **chunk.metadata,
                    },
                }
            )

        logger.info(f"文本块嵌入完成: {len(results)} 块")
        return results

    # ========== 获取嵌入信息 ==========

    def get_vector_dimension(self) -> int:
        """获取向量维度

        Returns:
            int: 向量维度
        """
        dimensions = {
            EmbeddingModel.OPENAI_TEXT_EMBEDDING_3_SMALL: 1536,
            EmbeddingModel.OPENAI_TEXT_EMBEDDING_3_LARGE: 3072,
            EmbeddingModel.OPENAI_TEXT_EMBEDDING_ADA_002: 1536,
        }
        return dimensions.get(self.model, 1536)

    def get_model_name(self) -> str:
        """获取模型名称

        Returns:
            str: 模型名称
        """
        return self.model.value
