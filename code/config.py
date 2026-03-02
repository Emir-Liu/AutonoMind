"""配置管理模块

使用pydantic-settings管理配置，支持环境变量和配置文件优先级
优先级: 环境变量 > .env文件 > 默认值
"""

from functools import lru_cache
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """全局配置类"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # ========== 应用配置 ==========
    APP_NAME: str = "AutonoMind"
    APP_VERSION: str = "0.1.0"
    APP_DESCRIPTION: str = "自进化AI智能体系统"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # development, staging, production

    # ========== 服务器配置 ==========
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1

    # ========== 数据库配置 ==========
    # PostgreSQL
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_NAME: str = "autonomind"
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 3600

    @property
    def DATABASE_URL(self) -> str:
        """数据库连接URL"""
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # ========== Redis配置 ==========
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0
    REDIS_MAX_CONNECTIONS: int = 50

    @property
    def REDIS_URL(self) -> str:
        """Redis连接URL"""
        auth = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        return f"redis://{auth}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    # ========== Qdrant向量数据库配置 ==========
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_API_KEY: Optional[str] = None
    QDRANT_COLLECTION_PREFIX: str = "autonomind"

    @property
    def QDRANT_URL(self) -> str:
        """Qdrant连接URL"""
        return f"http://{self.QDRANT_HOST}:{self.QDRANT_PORT}"

    # ========== RabbitMQ配置 ==========
    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "guest"
    RABBITMQ_PASSWORD: str = "guest"
    RABBITMQ_VHOST: str = "/"

    @property
    def RABBITMQ_URL(self) -> str:
        """RabbitMQ连接URL"""
        return f"amqp://{self.RABBITMQ_USER}:{self.RABBITMQ_PASSWORD}@{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}/{self.RABBITMQ_VHOST}"

    # ========== MinIO对象存储配置 ==========
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_SECURE: bool = False
    MINIO_BUCKET_PREFIX: str = "autonomind"

    # ========== LLM配置 ==========
    # OpenAI兼容接口
    OPENAI_API_BASE: str = "https://api.openai.com/v1"
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    OPENAI_TEMPERATURE: float = 0.7
    OPENAI_MAX_TOKENS: int = 4096
    OPENAI_TIMEOUT: int = 60
    OPENAI_MAX_RETRIES: int = 3

    # ========== Celery配置 ==========
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    CELERY_TASK_SERIALIZER: str = "json"
    CELERY_RESULT_SERIALIZER: str = "json"
    CELERY_ACCEPT_CONTENT: list[str] = ["json"]
    CELERY_TIMEZONE: str = "Asia/Shanghai"
    CELERY_ENABLE_UTC: bool = True

    # ========== JWT配置 ==========
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ========== 日志配置 ==========
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_DIR: str = "logs"
    LOG_MAX_BYTES: int = 10485760  # 10MB
    LOG_BACKUP_COUNT: int = 10

    # ========== 限流配置 ==========
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000

    # ========== CORS配置 ==========
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8080"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = ["*"]
    CORS_ALLOW_HEADERS: list[str] = ["*"]

    # ========== 文件上传配置 ==========
    UPLOAD_MAX_SIZE: int = 10485760  # 10MB
    UPLOAD_ALLOWED_EXTENSIONS: list[str] = [
        ".txt", ".md", ".pdf", ".doc", ".docx",
        ".jpg", ".jpeg", ".png", ".gif"
    ]

    # ========== 向量嵌入配置 ==========
    EMBEDDING_MODEL: str = "text-embedding-ada-002"
    EMBEDDING_DIMENSION: int = 1536
    EMBEDDING_BATCH_SIZE: int = 100

    # ========== 智能体配置 ==========
    AGENT_MAX_CONVERSATION_LENGTH: int = 50
    AGENT_MAX_CONTEXT_TOKENS: int = 8000
    AGENT_MEMORY_RETENTION_DAYS: int = 30
    AGENT_AUTO_EVOLUTION_ENABLED: bool = True
    AGENT_EVOLUTION_CHECK_INTERVAL_HOURS: int = 24

    # ========== 监控配置 ==========
    METRICS_ENABLED: bool = True
    METRICS_PORT: int = 9090

    # ========== 健康检查配置 ==========
    HEALTH_CHECK_TIMEOUT: int = 5


@lru_cache()
def get_settings() -> Settings:
    """获取配置实例(单例模式)"""
    return Settings()


# 导出配置实例
settings = get_settings()

__all__ = ["Settings", "get_settings", "settings"]
