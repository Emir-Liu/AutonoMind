# ADR-003: LLM 框架选型 - LangChain

## 状态

已接受

## 背景

AutonoMind 需要一个 LLM 框架来统一接口,支持多种 LLM 提供商(OpenAI、Anthropic、DeepSeek 等),并提供 Agent、工具调用、记忆管理等高级功能。

## 决策

选择 **LangChain** 作为 LLM 框架。

## 备选方案

### 方案 A: LangChain
**优点**:
- 支持 50+ LLM 提供商
- 提供 Agent、工具、记忆等高级抽象
- 生态丰富,社区活跃
- 支持链式调用和自定义组件
- 文档完善,易于上手

**缺点**:
- 抽象层次较高,性能有一定开销
- 版本迭代快,API 变化频繁
- 过度工程化,简单场景使用较重

### 方案 B: 直接调用 LLM API
**优点**:
- 轻量级,性能最优
- 完全可控,无额外抽象
- 依赖最少

**缺点**:
- 需要自己实现 Agent 逻辑
- 切换 LLM 需要修改代码
- 缺少工具和记忆管理功能

### 方案 C: LlamaIndex
**优点**:
- 专注知识检索(RAG)
- 数据连接器丰富
- 检索优化好

**缺点**:
- Agent 能力不如 LangChain
- 工具生态不如 LangChain
- 主要面向 RAG 场景

### 方案 D: Semantic Kernel
**优点**:
- 微软官方支持
- 类型安全(C#)
- Planner 功能强大

**缺点**:
- Python 支持不如 C# 完善
- 生态不如 LangChain
- 学习曲线陡峭

## 评估矩阵

| 维度 | LangChain | 直接 API | LlamaIndex | Semantic Kernel |
|------|-----------|----------|------------|-----------------|
| 易用性 | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| 性能 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 功能丰富度 | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| LLM 支持度 | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Agent 能力 | ⭐⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| 生态成熟度 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| 学习曲线 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |

## 决策理由

1. **多 LLM 支持**: 统一接口支持 OpenAI、Anthropic、DeepSeek 等
2. **Agent 能力**: 内置 Agent 框架,支持 ReAct、Plan-and-Solve 等策略
3. **工具集成**: 提供丰富的工具库和工具调用机制
4. **记忆管理**: 支持短期和长期记忆,适合多轮对话
5. **生态丰富**: 大量集成组件和社区贡献
6. **文档完善**: 官方文档详细,示例丰富

## 后果

### 正面影响
- 快速集成多种 LLM
- Agent 开发效率高
- 工具和记忆管理开箱即用
- 社区支持好,问题解决快

### 负面影响
- 框架有一定学习成本
- 性能相比直接 API 调用有开销
- 版本迭代快,需要跟进更新

### 风险
- LangChain 仍在快速迭代,API 可能有 breaking changes
- 过度依赖 LangChain 可能导致耦合

### 缓解措施
- 锁定 LangChain 版本,定期评估升级
- 使用 LangChain 的抽象层,同时保持自己封装
- 关注 LangChain Release Notes,及时适配

## 实施细节

### 核心依赖

```python
langchain==0.1.10
langchain-community==0.0.20
langchain-openai==0.0.5
langchain-anthropic==0.1.1
```

### 目录结构

```
code/core/
├── llm/
│   ├── __init__.py
│   ├── providers/          # LLM 提供商封装
│   │   ├── __init__.py
│   │   ├── openai.py
│   │   ├── anthropic.py
│   │   └── deepseek.py
│   ├── agents/            # Agent 封装
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── retrieval_agent.py
│   │   └── tool_agent.py
│   ├── tools/             # 工具定义
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── search.py
│   │   └── database.py
│   └── memory/            # 记忆管理
│       ├── __init__.py
│       ├── base.py
│       ├── short_term.py
│       └── long_term.py
```

### 示例代码

#### LLM 提供商配置

```python
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_community.llms import DeepSeek

class LLMProvider:
    @staticmethod
    def get_openai(model: str = "gpt-4", temperature: float = 0.7):
        return ChatOpenAI(
            model=model,
            temperature=temperature,
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            openai_api_base=os.getenv("OPENAI_API_BASE")
        )

    @staticmethod
    def get_anthropic(model: str = "claude-3-sonnet-20240229"):
        return ChatAnthropic(
            model=model,
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
        )

    @staticmethod
    def get_deepseek(model: str = "deepseek-chat"):
        return DeepSeek(
            model=model,
            deepseek_api_key=os.getenv("DEEPSEEK_API_KEY"),
            deepseek_api_base=os.getenv("DEEPSEEK_API_BASE")
        )
```

#### Agent 封装

```python
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate

class RetrievalAgent:
    def __init__(self, llm, retriever):
        self.llm = llm
        self.retriever = retriever

    def create_agent(self):
        prompt = PromptTemplate.from_template(
            """Answer the question based on the context below:
            Context: {context}
            Question: {input}

            Thought: {agent_scratchpad}
            """
        )

        tools = [
            Tool(
                name="Search",
                func=self.retriever.search,
                description="Search the knowledge base"
            )
        ]

        agent = create_react_agent(self.llm, tools, prompt)
        return AgentExecutor(agent=agent, tools=tools, verbose=True)
```

#### 工具定义

```python
from langchain.tools import BaseTool
from typing import Type

class SearchTool(BaseTool):
    name = "search"
    description = "Search the knowledge base for relevant information"

    def _run(self, query: str) -> str:
        # 实现同步搜索
        retriever = KnowledgeRetriever()
        results = retriever.search(query, top_k=5)
        return "\n".join([r.content for r in results])

    async def _arun(self, query: str) -> str:
        # 实现异步搜索
        retriever = KnowledgeRetriever()
        results = await retriever.search(query, top_k=5)
        return "\n".join([r.content for r in results])
```

### 配置管理

```python
from pydantic_settings import BaseSettings

class LLMConfig(BaseSettings):
    provider: str = "openai"
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 2000
    api_key: str
    api_base: str = None

    class Config:
        env_file = ".env"
```

## 相关决策

- [ADR-001: Web框架选型 - FastAPI](./ADR-001-Web框架选型.md)
- [ADR-002: 向量数据库选型 - Qdrant](./ADR-002-向量数据库选型.md)

---

**决策日期**: 2026-03-02
**决策者**: Technical Architect
