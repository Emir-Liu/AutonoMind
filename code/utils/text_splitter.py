"""文本分块工具模块

提供文本分块策略
"""

from typing import List, Optional
from config import settings
from utils.logger import logger


class TextSplitter:
    """文本分块器"""

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        separators: Optional[List[str]] = None,
    ):
        """初始化分块器

        Args:
            chunk_size: 每块的最大字符数
            chunk_overlap: 块之间的重叠字符数
            separators: 分隔符列表，按优先级排序
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        # 默认分隔符（按优先级）
        self.separators = separators or [
            "\n\n\n",  # 段落分隔
            "\n\n",   # 段落分隔
            "\n",     # 行分隔
            "。",     # 中文句号
            "！",     # 中文感叹号
            "？",     # 中文问号
            ".",      # 英文句号
            "!",      # 英文感叹号
            "?",      # 英文问号
            ";",      # 分号
            "；",     # 中文分号
            ",",      # 逗号
            "，",     # 中文逗号
            " ",      # 空格
            "",       # 无分隔符（最后手段）
        ]

    async def split_text(self, text: str) -> List[str]:
        """分割文本

        Args:
            text: 输入文本

        Returns:
            List[str]: 文本块列表
        """
        if not text:
            return []

        if len(text) <= self.chunk_size:
            return [text]

        chunks = []

        # 使用分隔符分块
        for separator in self.separators:
            splits = text.split(separator)

            # 尝试按此分隔符分块
            chunks = self._merge_chunks(splits)

            # 检查是否所有块都小于最大长度
            if all(len(chunk) <= self.chunk_size for chunk in chunks):
                # 添加重叠
                chunks = self._add_overlap(chunks)
                break

        # 如果使用所有分隔符后仍有超长块，强制分割
        chunks = self._force_split(chunks)

        logger.info(f"Split text into {len(chunks)} chunks")
        return chunks

    def _merge_chunks(self, splits: List[str]) -> List[str]:
        """合并小的分块

        Args:
            splits: 分割后的文本列表

        Returns:
            List[str]: 合并后的文本块
        """
        chunks = []
        current_chunk = ""

        for split in splits:
            if not split.strip():
                continue

            # 检查添加此块后是否超过限制
            if len(current_chunk) + len(split) <= self.chunk_size:
                current_chunk += split
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = split

        if current_chunk:
            chunks.append(current_chunk)

        return chunks

    def _add_overlap(self, chunks: List[str]) -> List[str]:
        """添加块之间的重叠

        Args:
            chunks: 文本块列表

        Returns:
            List[str]: 添加重叠后的文本块
        """
        if not chunks or self.chunk_overlap == 0:
            return chunks

        overlapped = [chunks[0]]

        for i in range(1, len(chunks)):
            prev_chunk = chunks[i - 1]
            current_chunk = chunks[i]

            # 从前一块末尾取重叠部分
            overlap_text = prev_chunk[-self.chunk_overlap:] if len(prev_chunk) > self.chunk_overlap else prev_chunk

            # 添加到当前块开头
            overlapped.append(overlap_text + current_chunk)

        return overlapped

    def _force_split(self, chunks: List[str]) -> List[str]:
        """强制分割超长块

        Args:
            chunks: 文本块列表

        Returns:
            List[str]: 分割后的文本块
        """
        result = []

        for chunk in chunks:
            if len(chunk) <= self.chunk_size:
                result.append(chunk)
            else:
                # 按固定长度分割
                for i in range(0, len(chunk), self.chunk_size - self.chunk_overlap):
                    result.append(chunk[i:i + self.chunk_size])

        return result


class SemanticTextSplitter(TextSplitter):
    """语义分块器（基于段落和句子）"""

    async def split_text(self, text: str) -> List[str]:
        """按语义分割文本

        Args:
            text: 输入文本

        Returns:
            List[str]: 文本块列表
        """
        if not text:
            return []

        # 按段落分割
        paragraphs = text.split("\n\n")

        chunks = []
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue

            if len(paragraph) <= self.chunk_size:
                chunks.append(paragraph)
            else:
                # 段落过长，按句子分割
                sentences = self._split_by_sentences(paragraph)
                chunks.extend(sentences)

        # 添加重叠
        chunks = self._add_overlap(chunks)

        logger.info(f"Split text into {len(chunks)} chunks (semantic)")
        return chunks

    def _split_by_sentences(self, text: str) -> List[str]:
        """按句子分割文本

        Args:
            text: 输入文本

        Returns:
            List[str]: 句子列表
        """
        # 使用正则表达式分割句子
        import re

        # 匹配句号、问号、感叹号
        sentence_pattern = r'(?<=[。！？.!?])\s*'
        sentences = re.split(sentence_pattern, text)

        # 合并过短的句子
        chunks = []
        current_chunk = ""

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            if len(current_chunk) + len(sentence) <= self.chunk_size:
                current_chunk += sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = sentence

        if current_chunk:
            chunks.append(current_chunk)

        return chunks


# 全局分块器实例
text_splitter = TextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
)

semantic_splitter = SemanticTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
)


__all__ = [
    "TextSplitter",
    "SemanticTextSplitter",
    "text_splitter",
    "semantic_splitter",
]
