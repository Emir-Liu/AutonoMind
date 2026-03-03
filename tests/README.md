# AutonoMind 测试指南

## 概述

本文档说明如何运行 AutonoMind 项目的测试。

## 测试结构

```
tests/
├── __init__.py              # 测试模块初始化
├── conftest.py             # pytest配置和fixtures
├── pytest.ini              # pytest配置文件
├── requirements-test.txt   # 测试依赖
├── unit/                   # 单元测试
│   ├── test_conversational_learning.py  # 对话式学习引擎测试
│   ├── test_embedding_service.py       # 嵌入服务测试
│   ├── test_knowledge_retriever.py     # 知识检索器测试
│   └── test_tool_registry.py          # 工具注册表测试
├── integration/            # 集成测试
│   ├── test_session_api.py            # 会话API测试
│   ├── test_message_api.py            # 消息API测试
│   └── test_knowledge_api.py          # 知识库API测试
└── e2e/                    # 端到端测试
    └── test_full_conversation_flow.py  # 完整对话流程测试
```

## 环境准备

### 1. 安装依赖

```bash
pip install -r tests/requirements-test.txt
```

### 2. 数据库要求

**集成测试和端到端测试需要以下依赖:**

- PostgreSQL 数据库
- Redis 缓存
- Qdrant 向量数据库

**单元测试不需要数据库**, 可以独立运行。

## 运行测试

### 运行所有测试

```bash
# 需要配置数据库环境
pytest tests/ -v
```

### 只运行单元测试

```bash
# 单元测试不需要数据库
pytest tests/unit/ -v
```

### 运行特定测试

```bash
# 运行单个测试文件
pytest tests/unit/test_conversational_learning.py -v

# 运行特定测试类
pytest tests/unit/test_conversational_learning.py::TestConversationalLearningEngine -v

# 运行特定测试方法
pytest tests/unit/test_conversational_learning.py::TestConversationalLearningEngine::test_detect_learning_intent_add -v
```

### 运行特定标记的测试

```bash
# 只运行单元测试
pytest -m unit -v

# 只运行集成测试
pytest -m integration -v

# 只运行端到端测试
pytest -m e2e -v

# 排除慢速测试
pytest -v -m "not slow"
```

## 测试覆盖范围

### 单元测试 (Unit Tests)

测试单个模块和类的功能:

- ✅ **ConversationalLearningEngine**: 对话式学习引擎
  - 学习意图检测 (ADD, CORRECT, SUPPLEMENT, DELETE, MERGE, NONE)
  - 知识提取
  - 冲突检测

- ✅ **EmbeddingService**: 嵌入服务
  - 文本嵌入生成
  - 批量嵌入
  - 文本分块
  - 相似度计算

- ✅ **QdrantVectorStore**: 向量存储
  - 向量插入和删除
  - 向量搜索
  - 过滤条件
  - 相似度阈值

- ✅ **KnowledgeRetriever**: 知识检索器
  - 向量检索
  - 关键词检索
  - 混合检索
  - 重排序

- ✅ **ToolRegistry**: 工具注册表
  - 工具注册和注销
  - 工具执行
  - 参数验证
  - 内置工具

### 集成测试 (Integration Tests)

测试API端点和模块间的交互:

- ✅ **Session API**: 会话管理
  - 创建/获取/删除会话
  - 会话列表
  - 会话分页

- ✅ **Message API**: 消息管理
  - 发送消息
  - 获取历史
  - 多轮对话

- ✅ **Knowledge API**: 知识库管理
  - 添加/删除/更新知识
  - 批量操作
  - 知识检索
  - 文件上传

### 端到端测试 (E2E Tests)

测试完整的用户场景:

- ✅ **完整对话流程**
  - 添加知识 → 创建会话 → 发送消息 → 获取响应
  - 多轮对话
  - 知识检索集成

- ✅ **对话式学习流程**
  - 学习意图识别
  - 知识自动提取
  - 知识库更新

- ✅ **会话隔离**
  - 多用户独立会话
  - 历史记录隔离

## 当前状态

### 已完成的工作

1. ✅ 创建完整的测试目录结构
2. ✅ 编写全面的单元测试用例
3. ✅ 编写API集成测试
4. ✅ 编写端到端测试
5. ✅ 配置pytest环境
6. ✅ 创建测试fixtures和mock

### 已知问题

1. **数据库依赖问题**
   - 集成测试和E2E测试需要配置数据库
   - 单元测试可以独立运行

2. **模块导入问题**
   - 部分模块之间存在循环依赖
   - 需要重构代码结构

3. **未实现的API端点**
   - 部分API端点尚未完全实现
   - 测试中已预留404/500状态码的断言

## 测试最佳实践

### 1. 测试隔离

每个测试应该是独立的,不依赖其他测试:

```python
@pytest.mark.asyncio
async def test_create_session(async_client):
    # 不要依赖其他测试创建的数据
    response = await async_client.post("/api/v1/sessions", json={...})
    assert response.status_code == 200
```

### 2. 使用Mock和Fixture

利用pytest的mock和fixture功能:

```python
@pytest.fixture
def mock_llm_client():
    mock = AsyncMock()
    mock.chat.completions.create = AsyncMock()
    return mock
```

### 3. 清理测试数据

测试完成后清理数据:

```python
@pytest.mark.asyncio
async def test_delete_knowledge(async_client):
    # 创建
    response = await async_client.post("/api/v1/knowledge", json={...})
    knowledge_id = response.json()["data"]["id"]

    # 清理
    await async_client.delete(f"/api/v1/knowledge/{knowledge_id}")
```

### 4. 边界条件测试

测试各种边界情况:

```python
async def test_empty_query():
    """测试空查询"""
    result = await retriever.retrieve(query="", top_k=5)
    assert isinstance(result, list)

async def test_very_long_query():
    """测试超长查询"""
    long_query = "测试" * 1000
    result = await retriever.retrieve(query=long_query, top_k=5)
    assert isinstance(result, list)
```

## 下一步计划

### 短期目标

1. **修复导入问题**
   - 重构模块依赖关系
   - 消除循环导入
   - 简化测试配置

2. **配置测试数据库**
   - 使用Docker容器
   - 或使用SQLite进行测试
   - 确保测试环境隔离

3. **增加测试覆盖率**
   - 目标: 核心模块覆盖率 > 80%
   - 使用pytest-cov生成报告

### 中期目标

1. **性能测试**
   - 响应时间测试
   - 并发测试
   - 负载测试

2. **API文档测试**
   - 自动化API文档验证
   - 使用Postman/Newman

3. **CI/CD集成**
   - GitHub Actions自动化测试
   - 测试报告生成

## 运行特定测试场景

### 快速验证

```bash
# 只运行快速测试
pytest -v -m "not slow"
```

### 完整测试

```bash
# 运行所有测试(需要数据库)
pytest -v --cov=code --cov-report=html
```

### 生成报告

```bash
# 生成HTML测试报告
pytest -v --html=reports/test_report.html
```

## 贡献指南

添加新测试时:

1. 选择合适的测试类型 (unit/integration/e2e)
2. 使用清晰的命名
3. 添加适当的标记 (unit/integration/e2e/slow)
4. 编写测试文档字符串
5. 确保测试独立且可重复

---

**文档版本**: v1.0
**最后更新**: 2026-03-03
