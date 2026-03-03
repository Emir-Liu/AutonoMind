"""知识检索核心模块"""

from core.knowledge.interfaces import IKnowledgeRetriever
from core.knowledge.retriever import KnowledgeRetriever, RetrievalStrategy

__all__ = [
    "IKnowledgeRetriever",
    "KnowledgeRetriever",
    "RetrievalStrategy",
]
