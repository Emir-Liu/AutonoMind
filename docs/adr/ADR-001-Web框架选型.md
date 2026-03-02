# ADR-001: Web 框架选型 - FastAPI

## 状态

已接受

## 背景

AutonoMind 需要一个高性能的 Python Web 框架来提供 RESTful API 服务,同时需要支持异步处理、自动文档生成和类型安全。

## 决策

选择 **FastAPI** 作为主要 Web 框架。

## 备选方案

### 方案 A: FastAPI
**优点**:
- 基于 Starlette 和 Pydantic,性能优异
- 自动生成 OpenAPI 文档
- 原生支持异步(async/await)
- 类型安全,自动数据验证
- 依赖注入系统,便于测试
- 社区活跃,文档完善

**缺点**:
- 生态不如 Flask 和 Django 成熟
- 相对较新,最佳实践较少

### 方案 B: Flask
**优点**:
- 轻量级,灵活度高
- 生态成熟,插件丰富
- 学习曲线平缓

**缺点**:
- 原生不支持异步(需要扩展)
- 需要手动编写文档
- 数据验证需要额外配置

### 方案 C: Django
**优点**:
- 功能全面,包含 ORM、Admin 等
- 生态最成熟
- 安全性高

**缺点**:
- 重量级,学习曲线陡峭
- 异步支持不完善(3.1+ 才支持)
- 对于 API 开发过于臃肿

### 方案 D: Starlette
**优点**:
- 性能最高
- 轻量级,灵活

**缺点**:
- 功能较少,需要自己构建
- 自动文档生成不如 FastAPI 完善

## 评估矩阵

| 维度 | FastAPI | Flask | Django | Starlette |
|------|---------|-------|--------|-----------|
| 性能 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| 易用性 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| 类型安全 | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| 自动文档 | ⭐⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| 异步支持 | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| 生态成熟度 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| 团队熟悉度 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |

## 决策理由

1. **性能优异**: 基于 Starlette,性能接近 Node.js 和 Go
2. **异步支持**: 原生支持 async/await,适合 I/O 密集型应用
3. **自动文档**: 自动生成 OpenAPI/Swagger 文档,减少维护成本
4. **类型安全**: 基于 Pydantic,自动数据验证和类型检查
5. **依赖注入**: 便于测试和模块解耦
6. **团队经验**: 团队已有 FastAPI 使用经验

## 后果

### 正面影响
- 开发效率高,类型安全减少 Bug
- 自动文档减少维护工作
- 异步处理提升性能
- 代码清晰,易于维护

### 负面影响
- 某些成熟功能需要自己实现(如后台任务管理)
- 社区相对较小,遇到问题可能需要自行解决

### 风险
- FastAPI 框架仍在快速迭代,可能有 breaking changes
- 部分第三方库兼容性可能不如 Flask

### 缓解措施
- 锁定主要依赖版本,定期评估升级
- 选择成熟稳定的第三方库
- 关注 FastAPI Release Notes,及时适配

## 实施细节

### 核心依赖

```python
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3
pydantic-settings==2.1.0
```

### 目录结构

```
code/api/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI 应用入口
│   ├── config.py        # 配置管理
│   ├── dependencies.py  # 依赖注入
│   ├── routers/         # 路由
│   │   ├── __init__.py
│   │   ├── sessions.py
│   │   ├── knowledge.py
│   │   └── tools.py
│   ├── models/          # Pydantic 模型
│   ├── services/        # 业务逻辑
│   └── utils/           # 工具函数
└── tests/
```

### 示例代码

```python
from fastapi import FastAPI, Depends
from pydantic import BaseModel

app = FastAPI(
    title="AutonoMind API",
    description="自主 AI Agent API",
    version="1.0.0"
)

class Query(BaseModel):
    text: str
    session_id: str = None

@app.post("/api/v1/query")
async def query(
    query: Query,
    service: AgentService = Depends(get_agent_service)
):
    result = await service.execute(query.text, query.session_id)
    return {"result": result}
```

## 相关决策

- [ADR-002: 向量数据库选型 - Qdrant](./ADR-002-向量数据库选型.md)
- [ADR-003: LLM框架选型 - LangChain](./ADR-003-LLM框架选型.md)

---

**决策日期**: 2026-03-02
**决策者**: Technical Architect
