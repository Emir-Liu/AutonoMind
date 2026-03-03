"""数据库模型定义

基于SQLAlchemy 2.0异步ORM，实现用户、会话、消息、知识等核心数据模型
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    String, Integer, BigInteger, Text, DateTime, Boolean,
    Float, ForeignKey, Index, JSON, Enum as SQLEnum
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func
import enum


class Base(DeclarativeBase):
    """ORM基类"""

    pass


class UserStatus(str, enum.Enum):
    """用户状态枚举"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    BANNED = "banned"


class User(Base):
    """用户表"""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(100))
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500))
    status: Mapped[UserStatus] = mapped_column(SQLEnum(UserStatus), default=UserStatus.ACTIVE, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # 元数据
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # 关系
    sessions: Mapped[list["Session"]] = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    knowledge_items: Mapped[list["Knowledge"]] = relationship("Knowledge", back_populates="user", cascade="all, delete-orphan")

    # 索引
    __table_args__ = (
        Index('idx_users_status', 'status'),
        Index('idx_users_created_at', 'created_at'),
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"


class Session(Base):
    """会话表"""

    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    agent_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)  # active, archived, deleted

    # 消息统计
    message_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # 元数据
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    archived_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # 会话元数据（JSON格式存储额外信息）
    meta_data: Mapped[Optional[dict]] = mapped_column(JSON)

    # 关系
    user: Mapped["User"] = relationship("User", back_populates="sessions")
    messages: Mapped[list["Message"]] = relationship("Message", back_populates="session", cascade="all, delete-orphan")

    # 索引
    __table_args__ = (
        Index('idx_sessions_user_status', 'user_id', 'status'),
        Index('idx_sessions_agent', 'agent_id'),
        Index('idx_sessions_created_at', 'created_at'),
    )

    def __repr__(self) -> str:
        return f"<Session(id={self.id}, title='{self.title}', user_id={self.user_id})>"


class Message(Base):
    """消息表"""

    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True)

    # 消息内容
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # user, assistant, system
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Token统计
    prompt_tokens: Mapped[Optional[int]] = mapped_column(Integer)
    completion_tokens: Mapped[Optional[int]] = mapped_column(Integer)
    total_tokens: Mapped[Optional[int]] = mapped_column(Integer)

    # 执行统计
    execution_time_ms: Mapped[Optional[int]] = mapped_column(Integer)  # 执行耗时(毫秒)

    # 元数据
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # 消息元数据（JSON格式存储额外信息）
    meta_data: Mapped[Optional[dict]] = mapped_column(JSON)

    # 关系
    session: Mapped["Session"] = relationship("Session", back_populates="messages")

    # 索引
    __table_args__ = (
        Index('idx_messages_session_created', 'session_id', 'created_at'),
        Index('idx_messages_role', 'role'),
    )

    def __repr__(self) -> str:
        return f"<Message(id={self.id}, role='{self.role}', session_id={self.session_id})>"


class KnowledgeStatus(str, enum.Enum):
    """知识状态枚举"""
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"


class Knowledge(Base):
    """知识表"""

    __tablename__ = "knowledge"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # 知识内容
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    file_type: Mapped[str] = mapped_column(String(20), nullable=False)  # text, pdf, doc, image
    source: Mapped[Optional[str]] = mapped_column(String(200))  # 来源URL或文件名
    status: Mapped[KnowledgeStatus] = mapped_column(SQLEnum(KnowledgeStatus), default=KnowledgeStatus.ACTIVE, nullable=False)

    # 向量嵌入
    embedding_model: Mapped[str] = mapped_column(String(50), nullable=False)
    embedding_dimension: Mapped[int] = mapped_column(Integer, nullable=False)
    qdrant_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)  # Qdrant中的向量ID

    # 统计
    chunk_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 分块数量
    reference_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 被引用次数

    # 元数据
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    archived_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # 知识元数据（JSON格式存储额外信息）
    meta_data: Mapped[Optional[dict]] = mapped_column(JSON)

    # 关系
    user: Mapped["User"] = relationship("User", back_populates="knowledge_items")

    # 索引
    __table_args__ = (
        Index('idx_knowledge_user_status', 'user_id', 'status'),
        Index('idx_knowledge_type', 'file_type'),
        Index('idx_knowledge_created_at', 'created_at'),
    )

    def __repr__(self) -> str:
        return f"<Knowledge(id={self.id}, title='{self.title}', user_id={self.user_id})>"


class AgentConfig(Base):
    """智能体配置表"""

    __tablename__ = "agent_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    agent_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

    # LLM配置
    llm_model: Mapped[str] = mapped_column(String(100), nullable=False)
    llm_temperature: Mapped[float] = mapped_column(Float, default=0.7, nullable=False)
    llm_max_tokens: Mapped[int] = mapped_column(Integer, default=4096, nullable=False)

    # 能力配置（JSON格式）
    capabilities: Mapped[dict] = mapped_column(JSON, nullable=False)
    personality: Mapped[Optional[str]] = mapped_column(Text)

    # 元数据
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    def __repr__(self) -> str:
        return f"<AgentConfig(id={self.id}, agent_id='{self.agent_id}', name='{self.name}')>"


class EvolutionRecord(Base):
    """进化记录表"""

    __tablename__ = "evolution_records"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    agent_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    session_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("sessions.id", ondelete="SET NULL"))

    # 进化类型
    evolution_type: Mapped[str] = mapped_column(String(50), nullable=False)  # learning, retrieval, decision, tool

    # 触发原因
    trigger_reason: Mapped[str] = mapped_column(Text, nullable=False)

    # 进化内容（JSON格式）
    changes: Mapped[dict] = mapped_column(JSON, nullable=False)

    # 效果评估
    effect_score: Mapped[Optional[float]] = mapped_column(Float)  # -1.0 到 1.0
    effect_description: Mapped[Optional[str]] = mapped_column(Text)

    # 元数据
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # 索引
    __table_args__ = (
        Index('idx_evolution_agent_type', 'agent_id', 'evolution_type'),
        Index('idx_evolution_created_at', 'created_at'),
    )

    def __repr__(self) -> str:
        return f"<EvolutionRecord(id={self.id}, agent_id='{self.agent_id}', type='{self.evolution_type}')>"


class LearningIntent(str, enum.Enum):
    """学习意图枚举"""
    NEW = "new"
    CORRECT = "correct"
    SUPPLEMENT = "supplement"
    DELETE = "delete"
    MERGE = "merge"


class ApprovalStatus(str, enum.Enum):
    """审核状态枚举"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class LearningRecord(Base):
    """学习记录表"""

    __tablename__ = "learning_records"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    session_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("sessions.id", ondelete="SET NULL"), index=True)

    # 学习意图
    intent: Mapped[LearningIntent] = mapped_column(SQLEnum(LearningIntent), nullable=False)

    # 学习内容
    user_message: Mapped[str] = mapped_column(Text, nullable=False)
    assistant_message: Mapped[Optional[str]] = mapped_column(Text)

    # 提取的知识
    knowledge_title: Mapped[Optional[str]] = mapped_column(String(200))
    knowledge_content: Mapped[Optional[str]] = mapped_column(Text)
    confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # 审核状态
    approval_status: Mapped[ApprovalStatus] = mapped_column(SQLEnum(ApprovalStatus), default=ApprovalStatus.PENDING, nullable=False)

    # 审核信息
    reviewer_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    review_comment: Mapped[Optional[str]] = mapped_column(Text)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # 元数据
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # 学习记录元数据（JSON格式）
    meta_data: Mapped[Optional[dict]] = mapped_column(JSON)

    # 索引
    __table_args__ = (
        Index('idx_learning_user_status', 'user_id', 'approval_status'),
        Index('idx_learning_session', 'session_id'),
        Index('idx_learning_intent', 'intent'),
        Index('idx_learning_created_at', 'created_at'),
    )

    def __repr__(self) -> str:
        return f"<LearningRecord(id={self.id}, intent='{self.intent}', status='{self.approval_status}')>"


class ExecutionLog(Base):
    """执行日志表"""

    __tablename__ = "execution_logs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    message_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("messages.id", ondelete="SET NULL"), index=True)

    # 步骤类型
    step_type: Mapped[str] = mapped_column(String(50), nullable=False)  # retrieve, decide, execute, tool

    # 输入输出（JSON格式）
    input_data: Mapped[Optional[dict]] = mapped_column(JSON)
    output_data: Mapped[Optional[dict]] = mapped_column(JSON)

    # 执行结果
    success: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text)

    # 性能指标
    duration_ms: Mapped[Optional[int]] = mapped_column(Integer)  # 执行耗时(毫秒)

    # 元数据
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # 执行日志元数据（JSON格式）
    meta_data: Mapped[Optional[dict]] = mapped_column(JSON)

    # 索引
    __table_args__ = (
        Index('idx_execution_session', 'session_id', 'created_at'),
        Index('idx_execution_step', 'step_type'),
        Index('idx_execution_message', 'message_id'),
        Index('idx_execution_success', 'success'),
    )

    def __repr__(self) -> str:
        return f"<ExecutionLog(id={self.id}, step='{self.step_type}', success={self.success})>"

