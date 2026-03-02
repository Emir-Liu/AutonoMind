# AutonoMind

Autonomous(自主) + Mind(心智/知识库)

AutonoMind 是一个具备**自主决策**、**自我进化**能力的 AI Agent 架构。它能够直接使用大语言模型,根据用户问题自主检索知识库,智能决策是继续检索还是使用工具执行任务,并能够自主维护和更新向量知识库。

## 核心能力

- **智能检索**: 基于问题迭代检索向量知识库
- **自主决策**: 判断继续检索还是使用工具执行
- **知识自维护**: 自主增删改查向量数据库
- **知识进化**: 发现新知识、识别冲突、自主更新
- **LLM 驱动**: 大模型作为决策和推理核心

## 文档

### 架构文档
- [系统架构设计](./docs/architecture/system-architecture.md) - 整体架构、核心模块、技术选型
- [数据模型设计](./docs/data-model.md) - 数据库设计、向量数据库、缓存设计

### 产品文档
- [产品需求文档(PRD)](./docs/product/prd.md) - 功能需求、用户画像、验收标准
- [用户故事](./docs/product/user-stories.md) - 详细的用户故事和验收标准

### 技术文档
- [API 接口文档](./docs/api/api-reference.md) - RESTful API 完整参考
- [技术决策(ADR)](./docs/adr/) - 技术选型决策记录
  - [Web 框架选型 - FastAPI](./docs/adr/ADR-001-web-framework.md)
  - [向量数据库选型 - Qdrant](./docs/adr/ADR-002-vector-database.md)
  - [LLM 框架选型 - LangChain](./docs/adr/ADR-003-llm-framework.md)
  - [任务队列选型 - Celery](./docs/adr/ADR-004-task-queue.md)

## 技术栈

| 组件 | 技术 |
|------|------|
| **Web 框架** | FastAPI |
| **LLM 框架** | LangChain |
| **向量数据库** | Qdrant |
| **关系数据库** | PostgreSQL |
| **缓存** | Redis |
| **任务队列** | Celery + RabbitMQ |
| **对象存储** | MinIO |
| **监控** | Prometheus + Grafana |

## 项目结构

```
AutonoMind/
├── docs/                 # 文档目录
│   ├── architecture/    # 架构文档
│   ├── product/         # 产品文档
│   ├── api/             # API 文档
│   ├── adr/             # 技术决策记录
│   └── data-model.md    # 数据模型设计
├── code/                # 代码目录(待创建)
└── README.md            # 项目说明
```

## 快速开始

### 环境要求

- Python 3.9+
- PostgreSQL 14+
- Redis 7+
- Qdrant 1.7+

### 安装

```bash
# 克隆仓库
git clone https://github.com/your-org/AutonoMind.git
cd AutonoMind

# 安装依赖
pip install -r requirements.txt

# 启动服务
docker-compose up -d
```

## 贡献

欢迎贡献!请查看 [贡献指南](./CONTRIBUTING.md) 了解详情。

## 许可证

MIT License

---

**版本**: v1.0
**更新日期**: 2026-03-02
