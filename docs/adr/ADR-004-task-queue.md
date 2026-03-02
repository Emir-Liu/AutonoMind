# ADR-004: 任务队列选型 - Celery + Redis

## 状态

已接受

## 背景

AutonoMind 需要一个任务队列来处理长时间运行的任务,如知识向量化、异步 Agent 执行、知识进化等。需要支持任务调度、重试机制、任务监控和分布式部署。

## 决策

选择 **Celery + Redis** 作为任务队列方案。

## 夕选方案

### 方案 A: Celery + Redis
**优点**:
- 成熟稳定,生态丰富
- 支持 AMQP 和 Redis 作为 broker
- 内置重试、定时任务、任务链等功能
- 支持任务监控(Flower)
- 与 Python 生态集成好

**缺点**:
- 配置相对复杂
- 学习曲线有一定陡度
- 依赖较重

### 方案 B: RQ (Redis Queue)
**优点**:
- 轻量级,易于使用
- 专为 Redis 设计
- 配置简单

**缺点**:
- 功能不如 Celery 丰富
- 不支持复杂任务链
- 监控能力有限

### 方案 C: Dramatiq
**优点**:
- 性能高,轻量级
- 支持多种 broker
- API 简洁

**缺点**:
- 生态不如 Celery 成熟
- 监控工具较少
- 社区相对较小

### 方案 D: Arq ( asyncio)
**优点**:
- 原生支持 asyncio
- 性能优秀
- API 现代

**缺点**:
- 功能相对简单
- 生态较新
- 社区较小

## 评估矩阵

| 维度 | Celery+Redis | RQ | Dramatiq | Arq |
|------|--------------|-----|----------|-----|
| 成熟度 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| 易用性 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 功能丰富度 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| 性能 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 监控能力 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| 社区活跃度 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| 异步支持 | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

## 决策理由

1. **成熟稳定**: 生产环境广泛使用,可靠性高
2. **功能丰富**: 支持任务链、分组、定时任务等高级功能
3. **监控完善**: Flower 提供友好的 Web 监控界面
4. **生态集成**: 与 FastAPI、SQLAlchemy 等集成良好
5. **团队经验**: 团队已有 Celery 使用经验
6. **Redis Broker**: Redis 作为 broker 性能优异,部署简单

## 后果

### 正面影响
- 任务管理功能完善,满足复杂场景需求
- 监控和调试方便
- 任务失败自动重试
- 分布式部署支持好

### 负面影响
- 配置相对复杂,学习成本较高
- 依赖较重,增加了系统复杂度
- Celery 4.x 到 5.x 有 breaking changes

### 风险
- Celery 版本升级可能引入兼容性问题
- Redis broker 在大规模场景下可能成为瓶颈

### 缓解措施
- 锁定 Celery 版本,谨慎评估升级
- 监控 Redis 性能,必要时考虑 RabbitMQ
- 编写完整的任务测试用例

## 实施细节

### 核心依赖

```python
celery==5.3.6
redis==5.0.1
flower==2.0.1
```

### 目录结构

```
code/tasks/
├── __init__.py
├── celery_app.py          # Celery 应用配置
├── tasks/                 # 任务定义
│   ├── __init__.py
│   ├── knowledge.py       # 知识相关任务
│   ├── agent.py           # Agent 执行任务
│   └── evolution.py       # 知识进化任务
└── workers/               # Worker 配置
    └── __init__.py
```

### 配置示例

```python
from celery import Celery
import os

# Celery 应用
celery_app = Celery(
    'autonomind',
    broker=f"redis://{os.getenv('REDIS_HOST', 'localhost')}:{os.getenv('REDIS_PORT', 6379)}/0",
    backend=f"redis://{os.getenv('REDIS_HOST', 'localhost')}:{os.getenv('REDIS_PORT', 6379)}/0",
    include=[
        'tasks.tasks.knowledge',
        'tasks.tasks.agent',
        'tasks.tasks.evolution'
    ]
)

# 配置
celery_app.conf.update(
    # 任务配置
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Shanghai',
    enable_utc=True,

    # 结果过期时间
    result_expires=3600,

    # 重试配置
    task_acks_late=True,
    task_reject_on_worker_lost=True,

    # 并发配置
    worker_prefetch_multiplier=1,
    worker_concurrency=4,

    # 任务路由
    task_routes={
        'tasks.tasks.knowledge.*': {'queue': 'knowledge'},
        'tasks.tasks.agent.*': {'queue': 'agent'},
        'tasks.tasks.evolution.*': {'queue': 'evolution'},
    },

    # 定时任务
    beat_schedule={
        'knowledge-evolution-check': {
            'task': 'tasks.tasks.evolution.check_for_new_knowledge',
            'schedule': 300.0,  # 每5分钟
        },
    },
)
```

### 任务定义示例

```python
from celery import Task
import logging

logger = logging.getLogger(__name__)

class KnowledgeTask(Task):
    """知识相关任务基类"""
    _db = None

    @property
    def db(self):
        if self._db is None:
            self._db = get_db()
        return self._db

@celery_app.task(base=KnowledgeTask, bind=True, max_retries=3)
def vectorize_document(self, document_id: str):
    """向量化文档任务"""
    try:
        logger.info(f"开始向量化文档: {document_id}")

        # 获取文档
        document = self.db.get_document(document_id)
        if not document:
            raise ValueError(f"文档不存在: {document_id}")

        # 分块
        chunks = split_text(document.content)
        logger.info(f"文档分块完成,共 {len(chunks)} 块")

        # 向量化
        embeddings = []
        for chunk in chunks:
            embedding = embed_text(chunk)
            embeddings.append(embedding)

        # 存储到向量库
        vector_db = get_vector_db()
        vector_db.upsert_knowledge(document_id, chunks, embeddings)

        logger.info(f"文档向量化完成: {document_id}")
        return {"status": "success", "chunks_count": len(chunks)}

    except Exception as exc:
        logger.error(f"向量化失败: {document_id}, 错误: {exc}")
        # 重试
        raise self.retry(exc=exc, countdown=60)

@celery_app.task(bind=True, max_retries=3)
def execute_agent(self, session_id: str, query: str):
    """异步执行 Agent"""
    try:
        logger.info(f"开始执行 Agent: session_id={session_id}")

        agent = get_agent(session_id)
        result = agent.execute(query)

        logger.info(f"Agent 执行完成: session_id={session_id}")
        return result

    except Exception as exc:
        logger.error(f"Agent 执行失败: {exc}")
        raise self.retry(exc=exc, countdown=30)
```

### 启动 Worker

```bash
# 启动 worker (所有队列)
celery -A tasks.celery_app worker --loglevel=info

# 启动 worker (指定队列)
celery -A tasks.celery_app worker -Q agent --loglevel=info

# 启动 flower (监控)
celery -A tasks.celery_app flower --port=5555
```

### Docker Compose

```yaml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  celery-worker:
    build: .
    command: celery -A tasks.celery_app worker --loglevel=info
    depends_on:
      - redis
    environment:
      - REDIS_HOST=redis
      - REDIS_PORT=6379

  celery-beat:
    build: .
    command: celery -A tasks.celery_app beat --loglevel=info
    depends_on:
      - redis

  flower:
    build: .
    command: celery -A tasks.celery_app flower --port=5555
    ports:
      - "5555:5555"
    depends_on:
      - redis
```

### 监控和告警

```python
# 使用 Flower 监控
# 访问 http://localhost:5555

# 任务监控指标
- 任务成功率
- 任务平均执行时间
- 任务队列长度
- Worker 状态
```

## 相关决策

- [ADR-001: Web 框架选型 - FastAPI](./ADR-001-web-framework.md)

---

**决策日期**: 2026-03-02
**决策者**: Technical Architect
